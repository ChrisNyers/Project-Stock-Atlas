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

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

from stock_atlas import ControlFailure, DecisionStore, Stage7Run, run_stage7_pipeline
from stock_atlas.models import (
    CandidateUnderwriting,
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
    "FUNDING_ACTIONS",
    "STAGE7_ELIGIBLE",
]

#: The only Stage 7 status that may back a funding action.
STAGE7_ELIGIBLE = "ELIGIBLE FOR STAGE 8"

#: Actions that move capital and therefore require a passing Stage 7 bundle.
FUNDING_ACTIONS = frozenset({"INITIATE", "ADD"})


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
    ) -> DecisionRecord:
        """Persist a final human Stage 8 capital decision.

        The Stage 7 facts written to the ledger are read from the frozen run,
        never from caller-supplied arguments. ``DecisionStore.append`` then
        independently re-verifies the retained artifact before writing.
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

        position = getattr(result, "position", None)
        record = DecisionRecord(
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
        )
        return self._store.append(record)

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
