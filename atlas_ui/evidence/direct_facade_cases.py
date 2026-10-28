"""Replay the DIRECT-FACADE funded-decision bypass cases (no UI guard involved).

Run against any checkout:  PYTHONPATH=<checkout> python direct_facade_cases.py
Prints, per case, whether the canonical backend ACCEPTED a funded INITIATE (a ledger row was written) or REJECTED it.
Fixture provider, isolated temp workspaces, paper only.
"""
import inspect
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
from atlas_ui import demo
from atlas_ui.__main__ import build
from atlas_ui.service import Stage7Service
from capital_decision_facade import CapitalDecisionFacade, ControlFailure
from stock_atlas.models import MarketReferenceSnapshot, RevisitTriggers
from test_atlas_ui import NOW, good_req

NEW_API = "funded_freshness" in inspect.signature(CapitalDecisionFacade.record_final_decision).parameters


def fresh_evidence(price, now, run_entry_req, key=demo.DEMO_KEY):
    from live_price_binding import bind_price_snapshot
    from live_session_calendar import latest_completed_session
    ev = bind_price_snapshot(demo.FixtureProvider(price=price, clock=lambda: now), "DEMOCO", expected_security_key=key,
                             attestation=latest_completed_session(now))
    return ev.snapshot


def scenario(label, run_at, decide_at, fresh_price=None, omit_evidence=False):
    root = Path(tempfile.mkdtemp(prefix="direct_facade_"))
    app = build(True, root)
    clock = [run_at]
    svc = Stage7Service(app.ws, provider_factory=lambda: demo.FixtureProvider(clock=lambda: clock[0]),
                        identity_fn=lambda t: demo.DEMO_KEY, allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: True)
    req = good_req(tsy_ref_date=run_at.date().isoformat(), revisit_date=(NOW + timedelta(days=200)).date().isoformat())
    e = svc.run(req, run_at)
    run, versions, _ = svc.load_run(e["run_id"])
    kw = {}
    if NEW_API and not omit_evidence:
        from capital_decision_facade import FundedFreshnessEvidence
        snap = fresh_evidence(fresh_price if fresh_price is not None else 100.0, decide_at, req)
        kw["funded_freshness"] = FundedFreshnessEvidence(
            fresh_price=snap, treasury_reattested=MarketReferenceSnapshot(
                "UST-13W", 0.039, datetime.fromisoformat(run_at.date().isoformat() + "T00:00:00+00:00"),
                "HUMAN-ATTESTED U.S. Treasury par curve — not independently verified by Atlas", run.result and
                __import__("stock_atlas.models", fromlist=["FreshnessStatus"]).FreshnessStatus.FRESH, "USD"))
    try:
        rec = app.ws.facade.record_final_decision(
            run, record_id="DIRECT", human_stage8_action="INITIATE", human_rationale="direct facade call (no UI)",
            alternatives_considered=("SPY", "Treasury/Cash", "Do Nothing"), input_versions=versions, created_at=decide_at,
            portfolio_snapshot_id="X", dominant_drivers=("fixture driver",), starter_cap_weight=0.02,
            revisit_triggers=RevisitTriggers("p", decide_at + timedelta(days=90)), **kw)
        outcome = f"ACCEPTED — ledger rows: {len(app.svc.ledger_rows())}"
    except ControlFailure as exc:
        outcome = f"REJECTED — ledger rows: {len(app.svc.ledger_rows())} — {str(exc)[:150]}"
    print(f"[{'NEW' if NEW_API else 'OLD'} facade] {label}\n    -> {outcome}")


if __name__ == "__main__":
    scenario("8-day-old eligible Stage 7 run", NOW - timedelta(days=8), NOW)
    scenario("same-session run, evidence argument OMITTED", NOW, NOW, omit_evidence=True)
    scenario("same-session run, fresh price moved $100 -> $130", NOW, NOW, fresh_price=130.0)
    scenario("same-session run, unchanged evidence (control case)", NOW, NOW)
