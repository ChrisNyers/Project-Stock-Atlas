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
import math
import os
import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from capital_decision_facade import CapitalDecisionFacade, ControlFailure, FUNDING_ACTIONS, FundedFreshnessEvidence
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

from . import authority, canonical

REPO = canonical.REPO
_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
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


def _num(v, name: str) -> float:
    text = str(v if v is not None else "").strip().replace(",", "")
    if text.endswith("%"):
        text = text[:-1].strip()
    if not text:
        raise Blocked(f"{name} is required")
    try:
        x = float(text)
    except ValueError:
        raise Blocked(f"{name} must be a number")
    if not math.isfinite(x):
        raise Blocked(f"{name} must be a finite number")
    return x


def _f(v, name: str) -> float:
    """A plain number (dollars, years). Never reinterpreted."""
    return _num(v, name)


def _pct(v, name: str) -> float:
    """UI percentage -> decimal. ONE unit, no guessing: '1' is 1% (0.01), '0.5' is 0.5% (0.005)."""
    x = _num(v, name)
    if not -100.0 <= x <= 100.0:
        raise Blocked(f"{name}: {x:g}% is outside the accepted -100%..100% range")
    return x / 100.0


def _band(lo, hi, horizon, name: str) -> ReturnBand:
    a, b = _pct(lo, f"{name} low"), _pct(hi, f"{name} high")
    if a > b:
        raise Blocked(f"{name}: low exceeds high")
    return ReturnBand(a, b, float(horizon))


@dataclass
class Workspace:
    """Where one mode keeps its records. Canonical and demo never share paths."""
    root: Path
    mode: str  # "CANONICAL" | "DEMO"
    candidate_ledger: Path | None = None  # canonical mode shares operating_mvp's ledger: one store, not a copy
    register: Path | None = None          # the approval register that governs candidate status; the repository's when the shared ledger is used
    facade: CapitalDecisionFacade = field(init=False)

    def __post_init__(self):
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.candidate_ledger = Path(self.candidate_ledger or self.root / "candidate_ledger.jsonl")
        shared = self.candidate_ledger.resolve() == Path(ledger.DEFAULT_LEDGER).resolve()
        self.register = Path(self.register or (authority.REPO / authority.REGISTER if shared else self.root / "authority_register.jsonl"))
        self.facade = CapitalDecisionFacade(self.root / "decisions.jsonl", self.root / "artifacts")
        (self.root / "inputs").mkdir(exist_ok=True)

    def candidates(self) -> dict[str, dict]:
        """Candidate status AS THE AUTHORITY REGISTER APPROVES IT. The one place a server-side gate reads candidate state: a ledger change the register
        has not approved (a promotion included) is listed under ``pending`` and never followed. If the records cannot be resolved the gate is closed."""
        try:
            return authority.resolve_candidates(authority.resolve(self.register), self.candidate_ledger)
        except (authority.AuthorityError, ledger.LedgerError, OSError, ValueError) as exc:
            raise Blocked(f"candidate status cannot be established: the authority records did not resolve ({exc}); failing closed, nothing was written")

    @staticmethod
    def capital_gate(cid: str, cand: dict | None) -> str | None:
        """None when the candidate may go to capital comparison, else the exact reason. Both server-side entry points use this one rule:
        the APPROVED status must be READY_FOR_CAPITAL_COMPARISON and no ledger status change may be awaiting approval. An unapproved promotion
        never opens the gate; an unapproved change of any kind closes it until the register and the ledger agree (fail closed)."""
        if cand is None:
            return f"unknown candidate {cid!r}"
        msg = f"{cid} is {cand['state']}" + (f" until {cand['parked_until']}" if cand["parked_until"] else "")
        if cand["pending"]:
            last = cand["pending"][-1]
            return (msg + f"; ledger status change(s) {[p['seq'] for p in cand['pending']]} (latest: {last['to_state']}) are NOT approved in the authority register and are not followed, "
                    "and capital comparison stays closed until the register and the ledger agree")
        if cand["state"] != "READY_FOR_CAPITAL_COMPARISON":
            return msg + "; Stage 7 starts only for a candidate a human moved to READY_FOR_CAPITAL_COMPARISON and the authority register approved"
        return None

    @property
    def index_path(self) -> Path:
        return self.root / "runs_index.jsonl"

    def ref(self, d: dict) -> FrozenInputRef:
        """Rebuild a frozen reference from a run-index entry, located INSIDE this workspace.

        New entries hold ``artifact_rel`` (e.g. ``artifacts/<run>.json``), relative to the workspace root, so a copied or extracted workspace
        resolves its own files. Entries written earlier hold the writing machine's absolute ``artifact_path``; the index is append-only and is not
        rewritten, so only the tail from ``artifacts/`` or ``inputs/`` is used. The SHA-256, not the path, binds the content; every other shape
        (absolute, ``..``, wrong directory, symlink, escape) is refused.
        """
        rel = d.get("artifact_rel")
        if rel is None:
            parts = re.split(r"[\\/]", str(d.get("artifact_path", "")))
            idx = max((i for i, x in enumerate(parts) if x in ("artifacts", "inputs")), default=None)
            rel = "/".join(parts[idx:]) if idx is not None else ""
        segs = rel.split("/") if isinstance(rel, str) else []
        if not (2 <= len(segs) <= 3 and segs[0] in ("artifacts", "inputs") and segs[-1].endswith(".json")
                and all(_SEGMENT.match(x) for x in segs)):
            raise Blocked(f"unsafe retained-artifact reference {rel!r}; refused")
        path = self.root.joinpath(*segs)
        for i in range(1, len(segs) + 1):
            if self.root.joinpath(*segs[:i]).is_symlink():
                raise Blocked(f"retained artifact {rel} passes through a symbolic link; refused")
        if self.root.resolve() not in path.resolve().parents:
            raise Blocked(f"retained artifact {rel} resolves outside the workspace; refused")
        return FrozenInputRef(version=d["version"], sha256=d["sha256"], artifact_path=str(path))


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
    @staticmethod
    def _new_run_id(ticker: str, now: datetime) -> str:
        # microseconds + random suffix: two submissions can never share an id
        return f"S7-{ticker}-{now:%Y%m%dT%H%M%S%fZ}-{uuid.uuid4().hex[:8]}"

    def run(self, req: dict, now: datetime) -> dict:
        # --- identity: candidate -> recorded ticker -> bound security. Never trust a client pairing.
        cid = (req.get("candidate_id") or "").strip()
        cand = self.ws.candidates().get(cid)
        if cand is None:
            raise Blocked(f"unknown candidate {cid!r}")
        ticker = (cand.get("ticker") or "").strip().upper()
        if not ticker:
            raise Blocked(f"{cid} has no recorded ticker; the security identity cannot be established")
        claimed = (req.get("ticker") or "").strip().upper()
        if claimed and claimed != ticker:
            raise Blocked(f"ticker mismatch: candidate {cid} is recorded as {ticker}, request named {claimed}")
        why = self.ws.capital_gate(cid, cand)
        if why:
            raise Blocked(why)

        # --- explicit human inputs only: nothing is defaulted into a bullish or fresh state
        decision = (req.get("decision") or "").strip().upper()
        if decision not in {d.value for d in SecurityDecision}:
            raise Blocked("security decision must be chosen explicitly (nothing is inferred, BUY is never a default)")
        if not (req.get("decision_basis") or "").strip():
            raise Blocked("security decision requires its evidence basis (reference the underwriting record)")
        horizon = _f(req.get("horizon_years"), "horizon years")
        cand_band = _band(req.get("ret_low"), req.get("ret_high"), horizon, "candidate return band")
        req_band = _band(req.get("req_low"), req.get("req_high"), horizon, "required-return band")
        spy_band = _band(req.get("spy_low"), req.get("spy_high"), horizon, "SPY/beta band")
        tsy_band = _band(req.get("tsy_low"), req.get("tsy_high"), horizon, "Treasury/Cash band")
        increment = _f(req.get("increment"), "increment dollars")
        remaining = _pct(req["remaining_capacity"], "remaining capacity") if (req.get("remaining_capacity") or "").strip() else None

        # --- Treasury reference: a typed rate is a human attestation, never "verified fresh"
        tsy_value = _pct(req.get("tsy_ref_value"), "Treasury reference yield")
        tsy_src = (req.get("tsy_source_ref") or "").strip()
        if not tsy_src:
            raise Blocked("Treasury reference requires its source reference (e.g. the home.treasury.gov page and date)")
        if req.get("tsy_attest") not in ("1", "on"):
            raise Blocked("Treasury reference requires explicit human attestation that it was retrieved from the "
                          "primary source; Atlas does not verify a typed rate and a recent date is not verification")
        try:
            tsy_ref_as_of = datetime.fromisoformat((req.get("tsy_ref_date") or "").strip() + "T00:00:00+00:00")
        except ValueError:
            raise Blocked("Treasury reference date must be YYYY-MM-DD")
        age_h = (now - tsy_ref_as_of).total_seconds() / 3600
        if age_h < -24:
            raise Blocked("Treasury reference date is in the future")
        tsy_fresh = FreshnessStatus.FRESH if age_h <= 96 else FreshnessStatus.STALE

        # --- baseline: valuation date is the frozen record's, not the decision time
        c0 = canonical.current_portfolio()
        baseline_age = (now - c0.effective_at).days
        if req.get("baseline_ack") not in ("1", "on"):
            raise Blocked(f"acknowledge that the portfolio baseline is dated {c0.as_of} ({baseline_age} days old), "
                          "holdings are not live, and the denominator is approximate")

        ev = self.bind_price(ticker, now)  # nothing is retained unless binding succeeds
        key = ev.snapshot.security_key
        if ev.snapshot.ticker != ticker:
            raise Blocked(f"bound price ticker {ev.snapshot.ticker!r} does not match candidate ticker {ticker!r}")

        unc = []
        for line in _lines(req.get("uncertainties", "")):
            parts = [x.strip() for x in line.split("|")]
            if len(parts) != 3 or parts[2].upper() not in ("YES", "NO"):
                raise Blocked("each uncertainty must be 'TYPE | description | YES/NO(blocking)'")
            unc.append(TypedUncertainty(parts[0], parts[1], BlockFlag(parts[2].upper())))
        revisit_at = (req.get("revisit_date") or "").strip()
        if not revisit_at:
            raise Blocked("revisit time trigger date is required")
        revisit = RevisitTriggers((req.get("revisit_price") or "").strip(),
                                  datetime.fromisoformat(revisit_at + "T00:00:00+00:00"),
                                  (req.get("revisit_thesis") or "").strip() or None)
        gate = UnderwritingGateStatus((req.get("gate") or "UNVERIFIED").strip().upper())
        provenance = _lines(req.get("provenance", "")) + (f"security decision basis: {req['decision_basis'].strip()}",)
        underwriting = CandidateUnderwriting(
            security_key=key, ticker=ticker, security_decision=SecurityDecision(decision),
            price_snapshot=ev.snapshot, observable_regime=(req.get("regime") or "").strip(),
            observable_regime_evidence=_lines(req.get("regime_evidence", "")),
            atlas_variant=(req.get("variant") or "").strip(), variant_evidence=_lines(req.get("variant_evidence", "")),
            return_band=cand_band, return_band_basis=_lines(req.get("band_basis", "")),
            required_return_band=req_band, underwriting_gate_status=gate, uncertainties=tuple(unc),
            dominant_drivers=_lines(req.get("drivers", "")), revisit_triggers=revisit,
            underwriting_provenance=provenance,
        )
        attested = {k: VerificationStatus((req.get(k) or "UNVERIFIED").upper()) for k in ("tax", "liquidity", "execution")}
        snapshot = canonical.build_portfolio_snapshot(
            c0, as_of=c0.effective_at, funding_amount=_f(req.get("pocket") or canonical.FUNDING_POCKET_MAX, "pocket"),
            tax=attested["tax"], liquidity=attested["liquidity"], execution=attested["execution"])
        cur_w = c0.weight(ticker)
        position = build_position_proposal(
            snapshot, current_weight=cur_w, increment_dollars=increment,
            classification=PositionClassification(
                (req.get("classification") or ("ADD" if cur_w > 0 else "STARTER")).strip().upper()),
            capacity_status=CapacityStatus((req.get("capacity") or "UNVERIFIED").upper()),
            remaining_capacity=remaining,
            funding_source="new outside capital", funding_mode=FundingMode.EXTERNAL_NEW_CAPITAL)
        alts = (
            ComparisonAlternative(AlternativeType.BETA, "SPY", spy_band, security_key="ETF:SPY",
                                  overlap=ETFOverlap("SPY", key, OverlapStatus.UNMEASURED),
                                  notes=_lines(req.get("spy_notes", ""))),
            ComparisonAlternative(
                AlternativeType.TREASURY_CASH, "Treasury/Cash", tsy_band,
                market_reference=MarketReferenceSnapshot(
                    (req.get("tsy_ref_key") or "UST-PAR").strip() or "UST-PAR", tsy_value, tsy_ref_as_of,
                    "HUMAN-ATTESTED U.S. Treasury par curve — not independently verified by Atlas", tsy_fresh, "USD"),
                duration_match_status=VerificationStatus((req.get("tsy_duration") or "UNVERIFIED").upper()),
                notes=_lines(req.get("tsy_notes", ""))),
            ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing"),
        )
        accept = req.get("accept_unverified") in ("1", "on", True)

        # --- unique id, fail before ANY write if it could collide
        run_id = self._new_run_id(ticker, now)
        d = self.ws.root / "inputs" / run_id
        dest = self.ws.facade.artifact_dir / f"{run_id}.json"
        if any(e["run_id"] == run_id for e in read_index(self.ws.index_path)) or d.exists() or dest.exists():
            raise Blocked(f"run id {run_id} already exists; nothing was written")
        in_ref = lambda name, ver, payload: freeze_payload(payload, version=ver, destination=d / f"{name}.json")
        refs = InputVersions(
            portfolio_snapshot=in_ref("portfolio_snapshot", c0.snapshot_id and "snapshot-" + c0.snapshot_id or "cycle0-baseline", {
                "baseline_doc": c0.doc_path, "baseline_doc_sha256": c0.doc_sha256,
                "baseline_effective_at": c0.effective_at, "baseline_as_of_label": c0.as_of,
                "evaluated_at": now, "baseline_age_days": baseline_age,
                "valuation_uncertainty": f"stocks exact per human record; defensive ≈ ${c0.defensive_approx:,.0f} approximate, so the "
                                         "identified denominator and every weight are approximate",
                "identified_value": str(c0.identified_value), "holdings": [(t, str(v)) for t, v in c0.holdings],
                "defensive_approx": str(c0.defensive_approx), "label": c0.label, "snapshot": snapshot}),
            scenario_model=in_ref("scenario_model", "human-scenario-v2", {"request": {k: v for k, v in req.items()},
                                                                           "ticker": ticker, "units": "percent fields are % (1 = 1%)"}),
            exposure_map=in_ref("exposure_map", "exposure-v1", {
                "candidate_drivers": underwriting.dominant_drivers, "holding_drivers": "UNASSIGNED (human-authored at Stage 7)",
                "etf_overlap": "UNMEASURED — no portfolio-fit credit", "current_weight": cur_w}),
            evidence_set=in_ref("evidence_set", "evidence-v2", {
                "price_binding": ev.to_dict(), "underwriting_provenance": underwriting.underwriting_provenance,
                "variant_evidence": underwriting.variant_evidence, "regime_evidence": underwriting.observable_regime_evidence,
                "treasury_evidence": {"yield_decimal": tsy_value, "as_of": tsy_ref_as_of, "source_ref": tsy_src,
                                      "human_attested": True, "verification": "UNVERIFIED_BY_ATLAS",
                                      "freshness_label_basis": "typed date within 96h of decision time; NOT source verification"}}),
            control_contract=in_ref("control_contract", STAGE7_VERSION, self._contract()),
        )
        run = self.ws.facade.run_stage7(
            underwriting, snapshot, position, alts, now, artifact_name=run_id,
            human_accepts_unverified_constraints=accept, known_latest_session_date=ev.attestation.session_date)
        entry = {
            "run_id": run_id, "created_at": now.isoformat(), "mode": self.ws.mode, "ticker": ticker,
            "candidate_id": cid, "security_key": key, "status": run.result.status,
            "baseline_doc_sha256": c0.doc_sha256, "portfolio_snapshot_id": c0.portfolio_snapshot_id, "baseline_as_of": c0.as_of, "increment_dollars": increment,
            "priced_session": ev.attestation.session_date.isoformat(),
            "stage7": _ref_dict(run.artifact_ref, self.ws.root),
            "inputs": {k: _ref_dict(getattr(refs, k), self.ws.root) for k in refs.__dataclass_fields__},
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
            refs = [self.ws.ref(e["stage7"])] + [self.ws.ref(v) for v in e["inputs"].values()]
        except Blocked as exc:
            return False, str(exc)
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
        ref = self.ws.ref(entry["stage7"])
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
        if "price_basis" in data:  # FROZEN_CONTROL_CHANGE_001 artifacts; older ones simply lack it (and cannot fund)
            bundle["price_basis"] = data["price_basis"]
        if hashlib.sha256(canonical_json_bytes(bundle)).hexdigest() != ref.sha256:
            raise Blocked("NOT VERIFIED: rehydrated Stage 7 result does not reproduce its frozen hash")
        run = Stage7Run(result=result, rendered_text=data["rendered_text"], artifact_ref=ref)
        versions = InputVersions(**{k: self.ws.ref(v) for k, v in entry["inputs"].items()})
        return run, versions, entry

    # ---------------------------------------------------------------- fresh-price checkpoint
    # Adapter policy (pending your approval, see REMEDIATION_REPORT): an upper bound on how old a retained run's
    # HUMAN-ATTESTED inputs may be at funding time. It reuses the frozen 96h reference-data window; the primary
    # freshness controls are session equality and exact price equality below.
    MAX_RUN_AGE_HOURS = 96.0
    # Frozen Stage 7 PriceSnapshot fields that must be reproduced EXACTLY by the fresh Gate B bind. No tolerance.
    PRICE_IDENTITY_FIELDS = ("security_key", "quoted_security_key", "quoted_instrument", "ticker", "currency", "provider",
                             "price", "price_as_of", "price_session_date", "latest_completed_session_date",
                             "market_session_status", "adjusted", "price_mode", "freshness_status")

    def _fresh_price_gate(self, entry: dict, form: dict, now: datetime, reject) -> FundedFreshnessEvidence:
        """Existing process: Stage 7 -> FRESH-PRICE CHECK -> Human Stage 8.

        The facade/store verify a retained run's hash but never its age or whether the market moved, so a funded
        action must pass this checkpoint. Any failure means "re-run Stage 7"; old return ranges are never reused
        against a changed market. Non-actions are exempt. A failure leaves the decision ledger untouched.
        """
        try:
            cand = self.ws.candidates().get(entry["candidate_id"])
        except Blocked as exc:
            reject(str(exc))
        why = self.ws.capital_gate(entry["candidate_id"], cand)
        if why:
            reject("funded action refused: " + why)
        age_h = (now - datetime.fromisoformat(entry["created_at"])).total_seconds() / 3600
        if age_h < -0.02 or age_h > self.MAX_RUN_AGE_HOURS:
            reject(f"STALE Stage 7 run: {age_h:.1f}h old (limit {self.MAX_RUN_AGE_HOURS:g}h); re-run Stage 7 with fresh inputs")
        try:
            att = latest_completed_session(now, mic=self.mic)
        except SessionCalendarError as exc:
            reject(f"fresh-price check failed: {exc}")
        if att.session_date.isoformat() != entry["priced_session"]:
            reject(f"STALE price: Stage 7 priced the {entry['priced_session']} session but the latest completed "
                   f"{self.mic} session is {att.session_date}; re-run Stage 7")

        # --- compare a fresh Gate B bind with the FROZEN Stage 7 evidence, field by field
        evd = json.loads(Path(self.ws.ref(entry["inputs"]["evidence_set"]).artifact_path).read_text(encoding="utf-8"))
        frozen = evd["price_binding"]["price_binding"]
        frozen_att = evd["price_binding"]["session_attestation"]
        try:
            ev = self.bind_price(entry["ticker"], now)
        except Blocked as exc:
            reject(f"fresh-price check failed: {exc}")
        fresh = ev.to_dict()["price_binding"]
        s_fresh = ev.snapshot
        changed = [f"{k}: Stage 7 {frozen.get(k)!r} vs now {fresh.get(k)!r}" for k in self.PRICE_IDENTITY_FIELDS
                   if frozen.get(k) != fresh.get(k)]
        for k in ("exchange", "calendar_name", "session_date"):
            if frozen_att.get(k) != ev.attestation.to_dict().get(k):
                changed.append(f"session attestation {k}: Stage 7 {frozen_att.get(k)!r} vs now {ev.attestation.to_dict().get(k)!r}")
        if frozen.get("currency") != "USD":
            changed.append("non-USD price: FX/reference re-binding is not supported by this UI")
        if changed:
            reject("fresh-price check does NOT reproduce the frozen Stage 7 price evidence (" + "; ".join(changed)
                   + "). The return ranges rest on the old price: re-run Stage 7; nothing was reused")

        # --- Treasury reference: the human re-attests it today; any change or age beyond the window means re-run
        frozen_t = evd["treasury_evidence"]
        try:
            new_val = _pct(form.get("tsy_ref_value"), "Treasury reference yield (re-attested)")
        except Blocked as exc:
            reject(f"funded action requires Treasury re-attestation at Stage 8: {exc}")
        if form.get("tsy_attest") not in ("1", "on") or not (form.get("tsy_source_ref") or "").strip():
            reject("funded action requires the Treasury reference to be re-attested at Stage 8 (value, date, source, attestation)")
        try:
            new_asof = datetime.fromisoformat((form.get("tsy_ref_date") or "").strip() + "T00:00:00+00:00")
        except ValueError:
            reject("Treasury re-attestation date must be YYYY-MM-DD")
        if (now - new_asof).total_seconds() / 3600 > self.MAX_RUN_AGE_HOURS or (new_asof - now).total_seconds() > 86400:
            reject("Treasury re-attestation is older than the 96h reference window (or future-dated); re-run Stage 7")
        if abs(new_val - float(frozen_t["yield_decimal"])) > 1e-12 or new_asof.isoformat() != datetime.fromisoformat(frozen_t["as_of"]).isoformat():
            reject(f"Treasury reference changed since Stage 7 (frozen {float(frozen_t['yield_decimal']) * 100:g}% as of {frozen_t['as_of'][:10]}, "
                   f"re-attested {new_val * 100:g}% as of {new_asof.date()}); re-run Stage 7")
        with open(self.ws.root / "stage8_price_checks.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"run_id": entry["run_id"], "checked_at": now.isoformat(), "session": att.session_date.isoformat(),
                                 "frozen_price_binding": frozen, "fresh_price_binding": fresh,
                                 "treasury_reattested": {"yield_decimal": new_val, "as_of": new_asof.isoformat(),
                                                         "source_ref": form["tsy_source_ref"].strip(), "human_attested": True},
                                 "result": "REPRODUCED"}, default=str) + "\n")
        basis_t = json.loads(Path(self.ws.ref(entry["stage7"]).artifact_path).read_text(encoding="utf-8"))["price_basis"]["treasury_reference"]
        return FundedFreshnessEvidence(
            fresh_price=s_fresh,
            treasury_reattested=MarketReferenceSnapshot(basis_t["reference_key"], new_val, new_asof, basis_t["provider"],
                                                        FreshnessStatus.FRESH, basis_t["currency"]))

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
        req = json.loads(Path(self.ws.ref(entry["inputs"]["scenario_model"]).artifact_path).read_text())["request"]
        drivers = _lines(req.get("drivers", ""))
        revisit = RevisitTriggers(req.get("revisit_price", ""), datetime.fromisoformat(req["revisit_date"] + "T00:00:00+00:00"),
                                  req.get("revisit_thesis") or None)
        funded = action in FUNDING_ACTIONS
        evidence = self._fresh_price_gate(entry, form, now, reject) if funded else None
        try:
            rec = self.ws.facade.record_final_decision(
                run, record_id=f"S8-{run_id}", human_stage8_action=action,
                human_rationale=form["rationale"].strip(),
                alternatives_considered=("SPY/beta", "Treasury/Cash", "Do Nothing", entry["ticker"]),
                input_versions=versions, created_at=now, portfolio_snapshot_id=entry.get("portfolio_snapshot_id") or f"CYCLE0-{entry['baseline_doc_sha256'][:12]}",
                dominant_drivers=drivers if funded else (), revisit_triggers=revisit if funded else None,
                starter_cap_weight=canonical.STARTER_CAP_WEIGHT if funded else None,
                cluster_note=(form.get("cluster_note") or "").strip() or None,
                prior_record_id=(form.get("prior_record_id") or "").strip() or None,
                why_this_vs_alternatives=(form.get("why_vs") or "").strip() or None,
                why_this_size=(form.get("why_size") or "").strip() or None,
                allocation_wrong_if=(form.get("wrong_if") or "").strip() or None,
                why_not_this_increment=(form.get("why_not") or "").strip() or None,
                funded_freshness=evidence)
        except ControlFailure as exc:
            reject(f"backend refused: {exc}")
        rows_after = self.ledger_rows()
        return {"record_id": rec.record_id, "action": action, "record_hash": rec.record_hash,
                "rows_before": rows_before, "rows_after": len(rows_after),
                "entry_hash": rows_after[-1]["entry_hash"], "ledger_verified": self.ws.facade.verify_ledger(),
                "paper_only": True}


def _ref_dict(r: FrozenInputRef, root: Path) -> dict:
    """Index form of a frozen reference: workspace-relative, never an absolute path of the machine that wrote it."""
    rel = Path(r.artifact_path).resolve().relative_to(Path(root).resolve()).as_posix()
    return {"version": r.version, "sha256": r.sha256, "artifact_rel": rel}


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
