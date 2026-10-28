"""Single authorized capital-decision path for Project Stock Atlas.

This module is the ONLY sanctioned way for the production stack to (a) run a
Stage 7 capital comparison and (b) persist a final capital DecisionRecord.

Architecture
------------
The legacy top-level modules (``models``, ``database``, ``sec_adapter``,
``xbrl_parser``, ``market_data_providers``, ``identity_resolver``, ...) form the
data / ingestion domain. They produce evidence. They have no capital-decision
writer of their own and must not acquire one: nothing in that layer may create
a ``PortfolioAction`` or append a ``DecisionRecord``.

The ``stock_atlas`` package is the validated fail-closed control layer for
capital decisions. Its namespace is deliberately separate; in particular
``stock_atlas.models`` (capital-decision control model) is NOT the legacy
top-level ``models`` (data/ingestion-domain model), and the two are never
merged.

    ingestion/evidence (legacy top level)
                 |
                 v
    CapitalDecisionFacade.run_stage7()     -> stock_atlas.run_stage7_pipeline
                 |                            (comparison only; no PortfolioAction)
                 v
            Stage7Run  (frozen, hashed, retained on disk)
                 |
                 v
    CapitalDecisionFacade.record_final_decision()  -> DecisionStore.append
                                                      (Stage 7 binding enforced)

Fencing guarantees
------------------
1. ``run_stage7`` always retains the Stage 7 artifact. ``artifact_destination``
   cannot be omitted or set to ``None``, so a comparison can never be made that
   is unable to back a later final record (closes the M-06 shape at the facade).
2. ``record_final_decision`` accepts only a ``Stage7Run`` instance produced by
   the control-layer pipeline. A caller cannot hand in a dict, a stub, or a
   hand-built record claiming Stage 7 ran.
3. The status, security key, position classification and post-trade weight
   written to the ledger are taken FROM the frozen Stage 7 result, not from
   caller-supplied arguments. A caller cannot assert a status the comparison
   did not produce.
4. Persistence goes through ``DecisionStore.append``, which independently
   re-verifies the retained artifact and enforces the C-01 Stage 7 binding,
   M-01 VERIFIED constraints, M-03 driver cluster, M-04 STARTER history and
   M-06 artifact retention. The facade never bypasses it.
5. ``INITIATE``/``ADD`` additionally require the frozen Stage 7 status to be
   exactly ``ELIGIBLE FOR STAGE 8``; ``HOLD_CASH`` and ``DO_NOTHING`` remain
   legal after any Stage 7 outcome, including ELIGIBLE.

Capital status: NO REAL PORTFOLIO ACTION. This module records human paper
decisions. It contains no execution API, no broker connectivity, no optimizer,
no ranking, and no scoring.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

from allocation_rationale import (
    AllocationDecisionRecord,
    derive_allocation_rationale_status,
)
from live_session_calendar import SessionCalendarError, latest_completed_session
from stock_atlas import ControlFailure, DecisionStore, Stage7Run, run_stage7_pipeline
from stock_atlas.freeze import canonical_json_bytes, freeze_payload, verify_frozen_ref_file
from stock_atlas.models import (
    CandidateUnderwriting,
    FreshnessStatus,
    MarketReferenceSnapshot,
    PriceSnapshot,
    ComparisonAlternative,
    DecisionRecord,
    InputVersions,
    PortfolioAction,
    PortfolioSnapshot,
    PositionProposal,
    ReviewEventType,
    RevisitTriggers,
)

__all__ = [
    "CapitalDecisionFacade",
    "ControlFailure",
    "FundedFreshnessEvidence",
    "MAX_STAGE7_RUN_AGE_HOURS",
    "FUNDING_ACTIONS",
    "STAGE7_ELIGIBLE",
]

#: The only Stage 7 status that may back a funding action.
STAGE7_ELIGIBLE = "ELIGIBLE FOR STAGE 8"

#: Actions that move capital and therefore require a passing Stage 7 bundle.
FUNDING_ACTIONS = frozenset({"INITIATE", "ADD"})

#: Provisional paper-pilot bound (FROZEN_CONTROL_CHANGE_001). Subordinate to session authority and exact
#: evidence consistency: it can only make a funded decision stricter, never admit one they reject.
MAX_STAGE7_RUN_AGE_HOURS = 96.0


@dataclass(frozen=True)
class FundedFreshnessEvidence:
    """What a funded Stage 8 must show, at decision time, about the evidence Stage 7 used.

    ``fresh_price`` is a newly bound ``PriceSnapshot`` for the same security. ``treasury_reattested`` is the
    human's re-confirmation of the Treasury reference. Both must reproduce the frozen Stage 7 evidence exactly.
    """

    fresh_price: PriceSnapshot
    treasury_reattested: MarketReferenceSnapshot


def _jsonable_dict(obj) -> dict:
    return json.loads(canonical_json_bytes(obj))


@dataclass(frozen=True)
class FacadeConfig:
    """Where the single authorized path keeps its ledger and artifacts."""

    ledger_path: Path
    artifact_dir: Path


class CapitalDecisionFacade:
    """The single authorized capital-decision path.

    Every capital comparison and every final capital record in production must
    go through one instance of this class. Direct construction of a
    ``DecisionRecord`` followed by a raw ``DecisionStore.append`` is still
    blocked by the control layer's own binding, but it is not an authorized
    production path and integration tests assert that it cannot yield a funded
    decision without a genuine retained Stage 7 bundle.
    """

    def __init__(self, ledger_path: str | Path, artifact_dir: str | Path) -> None:
        self._config = FacadeConfig(
            ledger_path=Path(ledger_path),
            artifact_dir=Path(artifact_dir),
        )
        self._config.artifact_dir.mkdir(parents=True, exist_ok=True)
        self._store = DecisionStore(self._config.ledger_path)

    # -- properties ----------------------------------------------------------

    @property
    def store(self) -> DecisionStore:
        """Read access to the append-only ledger (verification, history)."""
        return self._store

    @property
    def artifact_dir(self) -> Path:
        return self._config.artifact_dir

    # -- Stage 7 -------------------------------------------------------------

    def run_stage7(
        self,
        underwriting: CandidateUnderwriting,
        portfolio: PortfolioSnapshot,
        position: PositionProposal | None,
        alternatives: Sequence[ComparisonAlternative],
        decision_time: datetime,
        *,
        artifact_name: str,
        human_accepts_unverified_constraints: bool = False,
        known_latest_session_date: date | None = None,
        max_reference_age_hours: float = 96.0,
    ) -> Stage7Run:
        """Run the canonical Stage 7 comparison and retain its frozen bundle.

        Stage 7 compares. It emits no PortfolioAction and authorizes nothing.
        The artifact is always written to disk so a later final record can prove
        the comparison actually ran and re-verify its exact state.
        """
        if not artifact_name or not artifact_name.strip():
            raise ControlFailure("Stage 7 requires an artifact_name so the bundle is retained")
        destination = self._config.artifact_dir / f"{artifact_name.strip()}.json"
        run = run_stage7_pipeline(
            underwriting,
            portfolio,
            position,
            alternatives,
            decision_time,
            human_accepts_unverified_constraints=human_accepts_unverified_constraints,
            known_latest_session_date=known_latest_session_date,
            max_reference_age_hours=max_reference_age_hours,
            artifact_destination=destination,
        )
        if not run.artifact_ref.artifact_path:
            raise ControlFailure("Stage 7 bundle was not retained; refusing to continue")
        return run

    # -- final persistence ---------------------------------------------------

    def record_final_decision(
        self,
        stage7_run: Stage7Run,
        *,
        record_id: str,
        human_stage8_action: str | PortfolioAction,
        human_rationale: str,
        alternatives_considered: Sequence[str],
        input_versions: InputVersions,
        created_at: datetime,
        portfolio_snapshot_id: str,
        dominant_drivers: Sequence[str] = (),
        revisit_triggers: RevisitTriggers | None = None,
        starter_cap_weight: float | None = None,
        cluster_note: str | None = None,
        prior_record_id: str | None = None,
        why_this_vs_alternatives: str | None = None,
        why_this_size: str | None = None,
        allocation_wrong_if: str | None = None,
        why_not_this_increment: str | None = None,
        funded_freshness: FundedFreshnessEvidence | None = None,
    ) -> DecisionRecord:
        """Persist a final human Stage 8 capital decision.

        The Stage 7 facts written to the ledger are read from the frozen run,
        never from caller-supplied arguments. ``DecisionStore.append`` then
        independently re-verifies the retained artifact before writing.

        The four allocation-rationale arguments are human-authored text. They
        are recorded verbatim and never generated, inferred or backfilled. They
        do not affect the dollar amount, the position weight, or any Stage 7
        output; ``allocation_rationale_status`` is derived solely from which of
        the three funded-line fields the human supplied.
        """
        if not isinstance(stage7_run, Stage7Run):
            raise ControlFailure(
                "record_final_decision requires a Stage7Run produced by run_stage7; "
                "a claimed or hand-built Stage 7 result is not accepted"
            )

        result = stage7_run.result
        action = _as_portfolio_action(human_stage8_action)

        # Funding actions are bound to a genuinely passing comparison.
        if action.value in FUNDING_ACTIONS and result.status != STAGE7_ELIGIBLE:
            raise ControlFailure(
                f"{action.value} requires Stage 7 status {STAGE7_ELIGIBLE!r}; "
                f"frozen bundle says {result.status!r}"
            )

        if action.value in FUNDING_ACTIONS:
            # Mandatory: omitting the evidence can never bypass verification (FROZEN_CONTROL_CHANGE_001).
            self._verify_funded_freshness(stage7_run, funded_freshness, created_at, record_id)

        position = getattr(result, "position", None)
        # Derived from field PRESENCE only — never from content, never generated.
        rationale_status = derive_allocation_rationale_status(
            action, why_this_vs_alternatives, why_this_size, allocation_wrong_if
        )
        record = AllocationDecisionRecord(
            record_id=record_id,
            created_at=created_at,
            review_event_type=ReviewEventType.FINAL_CAPITAL_DECISION,
            portfolio_snapshot_id=portfolio_snapshot_id,
            # Stage 7 facts come from the frozen run, not the caller.
            stage7_status=result.status,
            stage7_reasons=tuple(result.reasons),
            stage7_artifact=stage7_run.artifact_ref,
            candidate_security_key=result.security_key,
            constraint_state=result.constraint_state,
            position_classification=getattr(position, "classification", None),
            post_trade_weight=getattr(position, "post_trade_weight", None),
            # Human Stage 8 inputs.
            human_stage8_action=action,
            human_rationale=human_rationale,
            alternatives_considered=tuple(alternatives_considered),
            dominant_drivers=tuple(dominant_drivers),
            revisit_triggers=revisit_triggers,
            starter_cap_weight=starter_cap_weight,
            cluster_note=cluster_note,
            input_versions=input_versions,
            prior_record_id=prior_record_id,
            # Human-authored allocation rationale, recorded verbatim.
            why_this_vs_alternatives=why_this_vs_alternatives,
            why_this_size=why_this_size,
            allocation_wrong_if=allocation_wrong_if,
            allocation_rationale_status=rationale_status,
            why_not_this_increment=why_not_this_increment,
        )
        return self._store.append(record)

    # -- funded-decision freshness (mandatory for INITIATE / ADD) -----------

    def _verify_funded_freshness(
        self,
        stage7_run: Stage7Run,
        evidence: FundedFreshnessEvidence | None,
        created_at: datetime,
        record_id: str,
    ) -> None:
        """Fail closed unless the funded action still stands on the evidence Stage 7 froze. Writes nothing on failure."""
        if not isinstance(evidence, FundedFreshnessEvidence):
            raise ControlFailure(
                "INITIATE/ADD requires FundedFreshnessEvidence (fresh price bind and Treasury re-attestation); "
                "omitting it cannot bypass verification"
            )
        ref = stage7_run.artifact_ref
        if not verify_frozen_ref_file(ref):
            raise ControlFailure("Frozen Stage 7 artifact is missing or hash-mismatched")
        try:
            payload = json.loads(Path(ref.artifact_path).read_text(encoding="utf-8"))
        except Exception as exc:
            raise ControlFailure("Frozen Stage 7 artifact cannot be parsed") from exc
        basis = payload.get("price_basis")
        if not isinstance(basis, dict) or not isinstance(basis.get("price_snapshot"), dict):
            raise ControlFailure(
                "Stage 7 artifact carries no frozen price basis (older format); re-run Stage 7 before a funded action"
            )
        frozen_price = basis["price_snapshot"]
        created = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)

        # 1. run age (provisional, subordinate)
        decided = datetime.fromisoformat(str(payload["decision_time"]))
        decided = decided if decided.tzinfo else decided.replace(tzinfo=timezone.utc)
        age = created - decided
        if age < timedelta(seconds=-60) or age > timedelta(hours=MAX_STAGE7_RUN_AGE_HOURS):
            raise ControlFailure(
                f"STALE Stage 7 run: {age.total_seconds() / 3600:.1f}h old (limit {MAX_STAGE7_RUN_AGE_HOURS:g}h); re-run Stage 7"
            )

        # 2. USD-only scope
        if str(frozen_price.get("currency")) != "USD":
            raise ControlFailure("Non-USD Stage 7 run: FX/reference re-binding is out of scope; fails closed")

        # 3. independent session authority (never the provider)
        instrument = str(frozen_price.get("quoted_instrument") or "")
        mic = instrument[instrument.rfind("(") + 1:instrument.rfind(")")].strip().upper() if "(" in instrument and instrument.endswith(")") else ""
        if not mic:
            raise ControlFailure("Frozen price evidence names no exchange (MIC); session freshness cannot be established")
        try:
            latest = latest_completed_session(created, mic=mic).session_date.isoformat()
        except (SessionCalendarError, ControlFailure) as exc:
            raise ControlFailure(f"Session authority could not be established for {mic}: {exc}") from exc
        fresh = evidence.fresh_price
        sessions = {str(frozen_price.get("latest_completed_session_date")), fresh.latest_completed_session_date.isoformat(),
                    fresh.price_session_date.isoformat(), latest}
        if len(sessions) != 1:
            raise ControlFailure(
                f"STALE price: Stage 7 priced {frozen_price.get('latest_completed_session_date')}, fresh evidence says "
                f"{fresh.price_session_date}, latest completed {mic} session is {latest}; re-run Stage 7"
            )

        # 4. exact evidence consistency, no tolerance
        if fresh.freshness_status != FreshnessStatus.FRESH:
            raise ControlFailure("Fresh price evidence is not FRESH")
        fresh_d = _jsonable_dict(fresh)
        diffs = [f"{k}: Stage 7 {frozen_price.get(k)!r} vs now {fresh_d.get(k)!r}" for k in sorted(set(frozen_price) | set(fresh_d))
                 if frozen_price.get(k) != fresh_d.get(k)]
        if diffs:
            raise ControlFailure("Fresh price evidence does not reproduce the frozen Stage 7 evidence ("
                                 + "; ".join(diffs) + "); re-run Stage 7")

        # 5. Treasury reference: re-attested value must equal the frozen reference and be inside the reference window
        frozen_t = basis.get("treasury_reference")
        if not isinstance(frozen_t, dict):
            raise ControlFailure("Stage 7 froze no Treasury reference; a funded action fails closed")
        t = evidence.treasury_reattested
        t_d = _jsonable_dict(t)
        same = all(frozen_t.get(k) == t_d.get(k) for k in ("reference_key", "value", "as_of", "provider", "currency"))
        if not same:
            raise ControlFailure("Treasury reference re-attestation differs from the frozen Stage 7 reference; re-run Stage 7")
        t_asof = t.as_of if t.as_of.tzinfo else t.as_of.replace(tzinfo=timezone.utc)
        if t.freshness_status != FreshnessStatus.FRESH or (created - t_asof) > timedelta(hours=MAX_STAGE7_RUN_AGE_HOURS) \
                or (t_asof - created) > timedelta(seconds=60):
            raise ControlFailure("Treasury reference is outside the reference window at decision time; re-run Stage 7")

        # Retain exactly what was checked (written only after every check passed; same-content rewrites are idempotent).
        freeze_payload(
            {"record_id": record_id, "stage7_sha256": ref.sha256, "checked_at": created, "frozen_price_basis": basis,
             "fresh_price": fresh, "treasury_reattested": t, "session_authority": {"mic": mic, "latest_completed_session": latest}},
            version="funded-freshness-v1",
            destination=self._config.artifact_dir / f"{record_id}.funded_freshness.json",
        )

    # -- audit ---------------------------------------------------------------

    def verify_ledger(self) -> bool:
        return self._store.verify_integrity()

    def ledger_manifest_hash(self) -> str:
        return self._store.manifest_hash()


def _as_portfolio_action(action: str | PortfolioAction) -> PortfolioAction:
    """Resolve a Stage 8 action to the control-layer enum, fail-closed.

    Accepts the enum itself, its value ("HOLD CASH"), or its name ("HOLD_CASH").
    """
    if isinstance(action, PortfolioAction):
        return action
    text = str(action).strip().upper()
    try:
        return PortfolioAction(text)
    except ValueError:
        pass
    try:
        return PortfolioAction[text.replace(" ", "_")]
    except KeyError as exc:
        raise ControlFailure(f"Unknown human Stage 8 action: {action!r}") from exc


def assert_no_legacy_capital_writer() -> None:
    """Fail loudly if the data/ingestion layer ever grows a capital writer.

    The legacy top-level modules are evidence producers. If any of them starts
    importing the capital-decision persistence surface, the single-path
    guarantee is broken and this raises.
    """
    import importlib

    legacy_modules = (
        "models",
        "database",
        "formulas",
        "entity_classification",
        "identity_resolver",
        "point_in_time",
        "sec_adapter",
        "xbrl_parser",
        "market_data_providers",
        "market_macro_adapters",
        "freeze_and_registry",
    )
    offenders = []
    for name in legacy_modules:
        module = importlib.import_module(name)
        for attr in ("DecisionStore", "PortfolioAction", "DecisionRecord", "run_stage7_pipeline"):
            if hasattr(module, attr):
                offenders.append(f"{name}.{attr}")
    if offenders:
        raise ControlFailure(
            "Legacy data/ingestion modules must not expose capital-decision "
            f"surfaces; found: {', '.join(sorted(offenders))}"
        )
