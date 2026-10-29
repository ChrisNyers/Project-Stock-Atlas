"""Probe: can a direct facade caller defeat the run-age/session safeguard by choosing created_at?"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
sys.path.insert(0, "tests")
from atlas_ui import demo
from atlas_ui.__main__ import build
from atlas_ui.service import Stage7Service
from capital_decision_facade import ControlFailure, FundedFreshnessEvidence
from live_price_binding import bind_price_snapshot
from live_session_calendar import latest_completed_session
from stock_atlas.models import FreshnessStatus, MarketReferenceSnapshot, RevisitTriggers
from test_atlas_ui import NOW, good_req

now = datetime.now(timezone.utc)
run_at = now - timedelta(days=8)
app = build(True, Path(tempfile.mkdtemp()))
svc = Stage7Service(app.ws, provider_factory=lambda: demo.FixtureProvider(clock=lambda: run_at), identity_fn=lambda t: demo.DEMO_KEY,
                    allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: True)
e = svc.run(good_req(tsy_ref_date=run_at.date().isoformat(), revisit_date=(now + timedelta(days=200)).date().isoformat()), run_at)
run, versions, _ = svc.load_run(e["run_id"])
fake_created = run_at + timedelta(minutes=1)      # the caller simply states a created_at near the run
snap = bind_price_snapshot(demo.FixtureProvider(clock=lambda: run_at), "DEMOCO", expected_security_key=demo.DEMO_KEY,
                           attestation=latest_completed_session(run_at)).snapshot
tre = MarketReferenceSnapshot("UST-13W", 0.039, datetime.fromisoformat(run_at.date().isoformat() + "T00:00:00+00:00"),
                              "HUMAN-ATTESTED U.S. Treasury par curve — not independently verified by Atlas", FreshnessStatus.FRESH, "USD")
try:
    rec = app.ws.facade.record_final_decision(
        run, record_id="BACKDATED", human_stage8_action="INITIATE", human_rationale="direct call, created_at chosen by caller",
        alternatives_considered=("SPY", "Treasury/Cash", "Do Nothing"), input_versions=versions, created_at=fake_created,
        portfolio_snapshot_id="X", dominant_drivers=("fixture driver",), starter_cap_weight=0.02,
        revisit_triggers=RevisitTriggers("p", fake_created + timedelta(days=90)),
        funded_freshness=FundedFreshnessEvidence(fresh_price=snap, treasury_reattested=tre))
    print(f"ACCEPTED an 8-day-old run (real now {now:%Y-%m-%d %H:%MZ}, run {run_at:%Y-%m-%d}) — ledger rows: {len(app.svc.ledger_rows())}, record created_at={rec.created_at}")
except ControlFailure as exc:
    print("REJECTED:", exc)
