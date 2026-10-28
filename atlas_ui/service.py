"""Server-side adapters between the UI and the EXISTING frozen engine.

Nothing here computes Stage 7 eligibility or creates a PortfolioAction. Stage 7
runs only through ``CapitalDecisionFacade.run_stage7``; Stage 8 persists only
through ``CapitalDecisionFacade.record_final_decision``. This module's job is to
(1) assemble inputs from canonical records and human-typed fields, (2) bind
price/session through the Gate B code path, (3) retain hashed input artifacts and
an index of runs, (4) rehydrate a retained run and re-verify it before Stage 8.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from capital_decision_facade import CapitalDecisionFacade, ControlFailure, FUNDING_ACTIONS
from live_price_binding import LiveBindingError, bind_price_snapshot
from live_session_calendar import SessionCalendarError, latest_completed_session
from stock_atlas.freeze import canonical_json_bytes, freeze_payload, verify_frozen_ref_file
from stock_atlas.models import (
    AlternativeType, BlockFlag, CandidateUnderwriting, CapacityStatus, ComparisonAlternative, ETFOverlap,
    FreshnessStatus, FundingMode, FrozenInputRef, InputVersions, MarketReferenceSnapshot, OverlapStatus,
    PositionClassification, PositionProposal, ReturnBand, RevisitTriggers, SecurityDecision,
    Stage7CandidateResult, TypedUncertainty, UnderwritingGateStatus, VerificationStatus,
)
from stock_atlas.pipeline import Stage7Run
from stock_atlas.portfolio import build_position_proposal

from operating_mvp import ledger

from . import canonical

REPO = canonical.REPO
BASELINE_COMMIT = "4c71d06afe0853389beb4a77ec2708656c3fc708"
STAGE7_VERSION = "stage7-control-v0.2"
PAPER_ACTIONS = ("INITIATE", "ADD", "HOLD CASH", "DO NOTHING")


class Blocked(Exception):
    """A prerequisite is missing; the exact reason is shown to the human. Nothing was written."""


class Rejected(Exception):
    """The backend refused a Stage 8 request. ``rows_before == rows_after`` is the zero-row proof."""

    def __init__(self, message: str, rows_before: int, rows_after: int):
        super().__init__(message)
        self.rows_before, self.rows_after = rows_before, rows_after


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _lines(text: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in (text or "").splitlines() if x.strip())


def _f(v, name: str) -> float:
    try:
        x = float(str(v).strip().replace("%", "")) if v not in (None, "") else None
    except ValueError:
        raise Blocked(f"{name} must be a number")
    if x is None:
        raise Blocked(f"{name} is required")
    return x


def _band(lo, hi, horizon, name: str) -> ReturnBand:
    a, b = _f(lo, f"{name} low"), _f(hi, f"{name} high")
    if abs(a) > 1 or abs(b) > 1:  # accept 3 or 0.03 -> annualized decimals; refuse nonsense
        a, b = a / 100.0, b / 100.0
    if a > b:
        raise Blocked(f"{name}: low exceeds high")
    return ReturnBand(a, b, float(horizon))


@dataclass
class Workspace:
    """Where one mode keeps its records. Canonical and demo never share paths."""
    root: Path
    mode: str  # "CANONICAL" | "DEMO"
    candidate_ledger: Path | None = None  # canonical mode shares operating_mvp's ledger: one store, not a copy
    facade: CapitalDecisionFacade = field(init=False)

    def __post_init__(self):
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.candidate_ledger = Path(self.candidate_ledger or self.root / "candidate_ledger.jsonl")
        self.facade = CapitalDecisionFacade(self.root / "decisions.jsonl", self.root / "artifacts")
        (self.root / "inputs").mkdir(exist_ok=True)

    @property
    def index_path(self) -> Path:
        return self.root / "runs_index.jsonl"


class Stage7Service:
    def __init__(self, ws: Workspace, *, provider_factory: Callable[[], object],
                 identity_fn: Callable[[str], str], allowed_providers: set[str],
                 key_present: Callable[[], bool], mic: str = "XNYS"):
        self.ws, self._pf, self._identity = ws, provider_factory, identity_fn
        self.allowed_providers, self._key_present, self.mic = allowed_providers, key_present, mic

    # ---------------------------------------------------------------- market (Gate B)
    def bind_price(self, ticker: str, now: datetime):
        """Reuse the verified Gate B path. Raises Blocked with the exact canonical reason."""
        if not self._key_present():
            raise Blocked("TWELVEDATA_API_KEY is absent — live price binding is BLOCKED; no price was shown "
                          "or inferred")
        try:
            key = self._identity(ticker)
            att = latest_completed_session(now, mic=self.mic)
            ev = bind_price_snapshot(self._pf(), ticker, expected_security_key=key, attestation=att,
                                     expected_mic=self.mic)
        except (LiveBindingError, SessionCalendarError, ControlFailure) as exc:
            raise Blocked(f"Gate B binding stopped: {exc}") from exc
        except Exception as exc:  # identity resolution / provider failure: fail closed, no detail leaked
            raise Blocked(f"market data unavailable: {type(exc).__name__}") from exc
        if ev.snapshot.provider not in self.allowed_providers:
            raise Blocked(f"price provider {ev.snapshot.provider!r} is not permitted in {self.ws.mode} mode")
        return ev

    # ---------------------------------------------------------------- Stage 7
    def run(self, req: dict, now: datetime) -> dict:
        ticker = (req.get("ticker") or "").strip().upper()
        if not ticker:
            raise Blocked("ticker is required")
        cid = (req.get("candidate_id") or ticker).strip()
        cand = ledger.replay(self.ws.candidate_ledger).get(cid)
        if cand is None:
            raise Blocked(f"unknown candidate {cid!r}")
        if cand["state"] != "READY_FOR_CAPITAL_COMPARISON":
            raise Blocked(f"{cid} is {cand['state']}"
                          + (f" until {cand['parked_until']}" if cand["parked_until"] else "")
                          + "; Stage 7 starts only for a candidate a human moved to READY_FOR_CAPITAL_COMPARISON")
        c0 = canonical.load_cycle0()
        ev = self.bind_price(ticker, now)  # nothing is retained unless binding succeeds
        key = ev.snapshot.security_key

        horizon = _f(req.get("horizon_years") or 5, "horizon")
        cand_band = _band(req.get("ret_low"), req.get("ret_high"), horizon, "candidate return band")
        req_band = _band(req.get("req_low"), req.get("req_high"), horizon, "required-return band")
        spy_band = _band(req.get("spy_low"), req.get("spy_high"), horizon, "SPY/beta band")
        tsy_band = _band(req.get("tsy_low"), req.get("tsy_high"), horizon, "Treasury/Cash band")
        tsy_ref_as_of = datetime.fromisoformat(req.get("tsy_ref_date", "").strip() + "T00:00:00+00:00") \
            if req.get("tsy_ref_date", "").strip() else None
        if tsy_ref_as_of is None:
            raise Blocked("Treasury reference date is required (primary source: home.treasury.gov)")
        age_h = (now - tsy_ref_as_of).total_seconds() / 3600
        tsy_fresh = FreshnessStatus.FRESH if 0 <= age_h <= 96 else FreshnessStatus.STALE

        unc = []
        for line in _lines(req.get("uncertainties", "")):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 3 or parts[2].upper() not in ("YES", "NO"):
                raise Blocked("each uncertainty must be 'TYPE | description | YES/NO(blocking)'")
            unc.append(TypedUncertainty(parts[0], parts[1], BlockFlag(parts[2].upper())))
        revisit_at = req.get("revisit_date", "").strip()
        if not revisit_at:
            raise Blocked("revisit time trigger date is required")
        revisit = RevisitTriggers(req.get("revisit_price", "").strip(),
                                  datetime.fromisoformat(revisit_at + "T00:00:00+00:00"),
                                  req.get("revisit_thesis", "").strip() or None)
        gate = UnderwritingGateStatus(req.get("gate", "UNVERIFIED").strip().upper())
        underwriting = CandidateUnderwriting(
            security_key=key, ticker=ticker, security_decision=SecurityDecision(req.get("decision", "BUY").upper()),
            price_snapshot=ev.snapshot, observable_regime=req.get("regime", "").strip(),
            observable_regime_evidence=_lines(req.get("regime_evidence", "")),
            atlas_variant=req.get("variant", "").strip(), variant_evidence=_lines(req.get("variant_evidence", "")),
            return_band=cand_band, return_band_basis=_lines(req.get("band_basis", "")),
            required_return_band=req_band, underwriting_gate_status=gate, uncertainties=tuple(unc),
            dominant_drivers=_lines(req.get("drivers", "")), revisit_triggers=revisit,
            underwriting_provenance=_lines(req.get("provenance", "")),
        )
        attested = {k: VerificationStatus(req.get(k, "UNVERIFIED").upper()) for k in ("tax", "liquidity", "execution")}
        increment = _f(req.get("increment"), "increment dollars")
        snapshot = canonical.build_portfolio_snapshot(
            c0, as_of=now, funding_amount=_f(req.get("pocket") or canonical.FUNDING_POCKET_MAX, "pocket"),
            tax=attested["tax"], liquidity=attested["liquidity"], execution=attested["execution"])
        cur_w = c0.weight(ticker)
        position = build_position_proposal(
            snapshot, current_weight=cur_w, increment_dollars=increment,
            classification=PositionClassification(
                (req.get("classification") or ("ADD" if cur_w > 0 else "STARTER")).strip().upper()),
            capacity_status=CapacityStatus(req.get("capacity", "UNVERIFIED").upper()),
            remaining_capacity=(_f(req["remaining_capacity"], "remaining capacity")
                                if req.get("remaining_capacity", "").strip() else None),
            funding_source="new outside capital", funding_mode=FundingMode.EXTERNAL_NEW_CAPITAL)
        alts = (
            ComparisonAlternative(AlternativeType.BETA, "SPY", spy_band, security_key="ETF:SPY",
                                  overlap=ETFOverlap("SPY", key, OverlapStatus.UNMEASURED),
                                  notes=_lines(req.get("spy_notes", ""))),
            ComparisonAlternative(
                AlternativeType.TREASURY_CASH, "Treasury/Cash", tsy_band,
                market_reference=MarketReferenceSnapshot(
                    req.get("tsy_ref_key", "UST-PAR").strip() or "UST-PAR", _f(req.get("tsy_ref_value"), "Treasury reference value"),
                    tsy_ref_as_of, "U.S. Treasury par curve (human-entered)", tsy_fresh, "USD"),
                duration_match_status=VerificationStatus(req.get("tsy_duration", "UNVERIFIED").upper()),
                notes=_lines(req.get("tsy_notes", ""))),
            ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing"),
        )
        accept = req.get("accept_unverified") in ("1", "on", True)
        run_id = f"S7-{ticker}-{now:%Y%m%dT%H%M%SZ}"
        d = self.ws.root / "inputs" / run_id
        in_ref = lambda name, ver, payload: freeze_payload(payload, version=ver, destination=d / f"{name}.json")
        refs = InputVersions(
            portfolio_snapshot=in_ref("portfolio_snapshot", "cycle0-baseline", {
                "baseline_doc": c0.doc_path, "baseline_doc_sha256": c0.doc_sha256, "as_of": c0.as_of,
                "identified_value": str(c0.identified_value), "holdings": [(t, str(v)) for t, v in c0.holdings],
                "defensive_approx": str(c0.defensive_approx), "label": c0.label, "snapshot": snapshot}),
            scenario_model=in_ref("scenario_model", "human-scenario-v1", {"request": {k: v for k, v in req.items()}}),
            exposure_map=in_ref("exposure_map", "exposure-v1", {
                "candidate_drivers": underwriting.dominant_drivers, "holding_drivers": "UNASSIGNED (human-authored at Stage 7)",
                "etf_overlap": "UNMEASURED — no portfolio-fit credit", "current_weight": cur_w}),
            evidence_set=in_ref("evidence_set", "evidence-v1", {
                "price_binding": ev.to_dict(), "underwriting_provenance": underwriting.underwriting_provenance,
                "variant_evidence": underwriting.variant_evidence, "regime_evidence": underwriting.observable_regime_evidence}),
            control_contract=in_ref("control_contract", STAGE7_VERSION, self._contract()),
        )
        run = self.ws.facade.run_stage7(
            underwriting, snapshot, position, alts, now, artifact_name=run_id,
            human_accepts_unverified_constraints=accept, known_latest_session_date=ev.attestation.session_date)
        entry = {
            "run_id": run_id, "created_at": now.isoformat(), "mode": self.ws.mode, "ticker": ticker,
            "candidate_id": req.get("candidate_id", ticker), "security_key": key, "status": run.result.status,
            "baseline_doc_sha256": c0.doc_sha256, "increment_dollars": increment,
            "stage7": _ref_dict(run.artifact_ref), "inputs": {k: _ref_dict(getattr(refs, k)) for k in refs.__dataclass_fields__},
        }
        _append_index(self.ws.index_path, entry)
        return entry

    def _contract(self) -> dict:
        files = [REPO / "capital_decision_facade.py", REPO / "allocation_rationale.py",
                 *sorted((REPO / "stock_atlas").glob("*.py"))]
        try:
            head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,
                                  timeout=5).stdout.strip()
        except Exception:
            head = "UNKNOWN"
        return {"accepted_baseline": BASELINE_COMMIT, "repo_head": head,
                "control_files_sha256": {f.relative_to(REPO).as_posix(): _sha(f) for f in files}}

    # ---------------------------------------------------------------- retained runs
    def list_runs(self) -> list[dict]:
        out = []
        for e in read_index(self.ws.index_path):
            ok, why = self.verify_entry(e)
            out.append({**e, "verified": ok, "verify_note": why})
        return out

    def verify_entry(self, e: dict) -> tuple[bool, str]:
        try:
            refs = [FrozenInputRef(**e["stage7"])] + [FrozenInputRef(**v) for v in e["inputs"].values()]
        except Exception:
            return False, "malformed index entry"
        for r in refs:
            if not verify_frozen_ref_file(r):
                return False, f"retained artifact missing or hash-mismatched: {r.artifact_path}"
        return True, "all retained artifacts match their recorded SHA-256"

    def load_run(self, run_id: str) -> tuple[Stage7Run, InputVersions, dict]:
        """Rehydrate a retained Stage 7 run and prove it reproduces its recorded hash."""
        entry = next((e for e in read_index(self.ws.index_path) if e["run_id"] == run_id), None)
        if entry is None:
            raise Blocked(f"no retained Stage 7 run {run_id!r}")
        ok, why = self.verify_entry(entry)
        if not ok:
            raise Blocked(f"NOT VERIFIED: {why}")
        ref = FrozenInputRef(**entry["stage7"])
        data = json.loads(Path(ref.artifact_path).read_text(encoding="utf-8"))
        r = data["result"]
        p = r.get("position")
        pos = None if p is None else PositionProposal(
            p["current_weight"], p["proposed_increment_weight"], p["proposed_increment_dollars"],
            p["post_trade_portfolio_value"], p["post_trade_weight"], PositionClassification(p["classification"]),
            CapacityStatus(p["capacity_status"]), p["remaining_capacity"], p["funding_source"],
            FundingMode(p["funding_mode"]), tuple(p["sensitivity_weights"]))
        result = Stage7CandidateResult(
            r["security_key"], r["ticker"], r["status"], tuple(r["reasons"]), pos,
            VerificationStatus(r["constraint_state"]),
            OverlapStatus(r["overlap_status"]) if r.get("overlap_status") else None, r["comparison_header"])
        bundle = {"decision_time": data["decision_time"], "result": result, "rendered_text": data["rendered_text"]}
        if hashlib.sha256(canonical_json_bytes(bundle)).hexdigest() != ref.sha256:
            raise Blocked("NOT VERIFIED: rehydrated Stage 7 result does not reproduce its frozen hash")
        run = Stage7Run(result=result, rendered_text=data["rendered_text"], artifact_ref=ref)
        versions = InputVersions(**{k: FrozenInputRef(**v) for k, v in entry["inputs"].items()})
        return run, versions, entry

    # ---------------------------------------------------------------- Stage 8 (paper only)
    def ledger_rows(self) -> list[dict]:
        p = self.ws.facade.store.path
        if not Path(p).exists():
            return []
        return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]

    def record_stage8(self, run_id: str, form: dict, now: datetime) -> dict:
        rows_before = len(self.ledger_rows())

        def reject(msg):
            raise Rejected(msg, rows_before, len(self.ledger_rows()))

        try:
            run, versions, entry = self.load_run(run_id)
        except Blocked as exc:
            reject(str(exc))
        action = (form.get("action") or "").strip().upper()
        if action not in PAPER_ACTIONS:
            reject(f"action {action!r} is not available in this paper-only UI; legal: {', '.join(PAPER_ACTIONS)}")
        if form.get("confirm") not in ("1", "on"):
            reject("explicit paper-only confirmation is required")
        if not (form.get("rationale") or "").strip():
            reject("human rationale is required")
        if any(r["record"]["record_id"] == f"S8-{run_id}" for r in self.ledger_rows()):
            reject("a final decision already exists for this retained run; a change needs a fresh Stage 7 run "
                   "linked by prior_record_id")
        # Backend re-check of the retained run (the facade/store re-verify independently).
        if action in FUNDING_ACTIONS:
            if run.result.status != "ELIGIBLE FOR STAGE 8":
                reject(f"{action} requires Stage 7 status 'ELIGIBLE FOR STAGE 8'; retained run says {run.result.status!r}")
            if run.result.constraint_state != VerificationStatus.VERIFIED:
                reject("tax, liquidity and execution constraints are not all VERIFIED; funded action fails closed")
        req = json.loads(Path(entry["inputs"]["scenario_model"]["artifact_path"]).read_text())["request"]
        drivers = _lines(req.get("drivers", ""))
        revisit = RevisitTriggers(req.get("revisit_price", ""), datetime.fromisoformat(req["revisit_date"] + "T00:00:00+00:00"),
                                  req.get("revisit_thesis") or None)
        funded = action in FUNDING_ACTIONS
        try:
            rec = self.ws.facade.record_final_decision(
                run, record_id=f"S8-{run_id}", human_stage8_action=action,
                human_rationale=form["rationale"].strip(),
                alternatives_considered=("SPY/beta", "Treasury/Cash", "Do Nothing", entry["ticker"]),
                input_versions=versions, created_at=now, portfolio_snapshot_id=f"CYCLE0-{entry['baseline_doc_sha256'][:12]}",
                dominant_drivers=drivers if funded else (), revisit_triggers=revisit if funded else None,
                starter_cap_weight=canonical.STARTER_CAP_WEIGHT if funded else None,
                cluster_note=(form.get("cluster_note") or "").strip() or None,
                prior_record_id=(form.get("prior_record_id") or "").strip() or None,
                why_this_vs_alternatives=(form.get("why_vs") or "").strip() or None,
                why_this_size=(form.get("why_size") or "").strip() or None,
                allocation_wrong_if=(form.get("wrong_if") or "").strip() or None,
                why_not_this_increment=(form.get("why_not") or "").strip() or None)
        except ControlFailure as exc:
            reject(f"backend refused: {exc}")
        rows_after = self.ledger_rows()
        return {"record_id": rec.record_id, "action": action, "record_hash": rec.record_hash,
                "rows_before": rows_before, "rows_after": len(rows_after),
                "entry_hash": rows_after[-1]["entry_hash"], "ledger_verified": self.ws.facade.verify_ledger(),
                "paper_only": True}


def _ref_dict(r: FrozenInputRef) -> dict:
    return {"version": r.version, "sha256": r.sha256, "artifact_path": r.artifact_path}


def read_index(path: Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _append_index(path: Path, entry: dict) -> None:
    with open(path, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0, 2)
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
