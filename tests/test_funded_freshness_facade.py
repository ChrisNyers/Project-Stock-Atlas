"""FROZEN_CONTROL_CHANGE_001 — the canonical facade itself refuses a funded decision on stale or changed evidence.

Direct-facade tests (no UI, no atlas_ui guard) over the real facade/DecisionStore, plus the UI path with its own guard
disabled, to show the backend is the control. Every rejection asserts the decision ledger is byte-identical.
HOLD CASH / DO NOTHING stay recordable. Fixture data; paper only.
"""
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from capital_decision_facade import (CapitalDecisionFacade, ControlFailure, FundedFreshnessEvidence,
                                     MAX_STAGE7_RUN_AGE_HOURS)
from stock_atlas.freeze import freeze_payload, verify_frozen_ref_file
from stock_atlas.models import FreshnessStatus, MarketReferenceSnapshot, RevisitTriggers
from stock_atlas.pipeline import Stage7Run
from test_integration_facade import (NOW, _eligible_run, _facade, _input_versions, _price, funded_evidence)


def ledger_bytes(facade) -> bytes:
    p = Path(facade.store.path)
    return p.read_bytes() if p.exists() else b""


_CLOCK = {}


@pytest.fixture(autouse=True)
def _clock(facade_clock, request):
    _CLOCK["c"] = facade_clock
    # UI-path tests run on the real clock (the UI passes its own real "now"); fixture tests pin the fixture time.
    facade_clock.set(None if request.node.name.startswith("test_ui_") else NOW)


def fund(facade, run, tmp_path, *, action="INITIATE", evidence="default", created_at=NOW, record_id="F-1", now="same", **kw):
    """`now` is the TRUSTED backend time; by default an honest caller whose created_at equals it."""
    _CLOCK["c"].set(created_at if now == "same" else now)
    ev = funded_evidence() if evidence == "default" else evidence
    return facade.record_final_decision(
        run, record_id=record_id, human_stage8_action=action, human_rationale="paper decision",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"), input_versions=_input_versions(tmp_path),
        created_at=created_at, portfolio_snapshot_id="INTEGRATION", dominant_drivers=("enterprise IT",),
        revisit_triggers=RevisitTriggers("±25% price", created_at + timedelta(days=90)), starter_cap_weight=0.10,
        funded_freshness=ev, **kw)


def rejects(facade, run, tmp_path, match, **kw):
    before = ledger_bytes(facade)
    with pytest.raises(ControlFailure, match=match):
        fund(facade, run, tmp_path, **kw)
    assert ledger_bytes(facade) == before and facade.verify_ledger()


@pytest.fixture
def setup(tmp_path):
    facade = _facade(tmp_path)
    return facade, _eligible_run(facade), tmp_path


# ---- omission can never bypass --------------------------------------------------------------
@pytest.mark.parametrize("action", ["INITIATE", "ADD"])
@pytest.mark.parametrize("bad", [None, {}, "fresh", 42, object()])
def test_funded_action_without_valid_evidence_is_refused(setup, action, bad):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "requires FundedFreshnessEvidence", action=action, evidence=bad)


def test_the_parameter_is_optional_only_in_signature_not_in_effect(setup):
    import inspect
    facade, run, tmp = setup
    assert inspect.signature(CapitalDecisionFacade.record_final_decision).parameters["funded_freshness"].default is None
    before = ledger_bytes(facade)
    with pytest.raises(ControlFailure):
        facade.record_final_decision(run, record_id="OMIT", human_stage8_action="INITIATE", human_rationale="x",
                                     alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
                                     input_versions=_input_versions(tmp), created_at=NOW, portfolio_snapshot_id="I",
                                     dominant_drivers=("enterprise IT",), revisit_triggers=RevisitTriggers("p", NOW + timedelta(days=90)),
                                     starter_cap_weight=0.10)
    assert ledger_bytes(facade) == before


# ---- stale ---------------------------------------------------------------------------------------
def test_old_run_is_refused_by_the_facade_alone(setup):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "STALE", created_at=NOW + timedelta(hours=MAX_STAGE7_RUN_AGE_HOURS + 1), evidence=funded_evidence(now=NOW + timedelta(hours=97)))
    rejects(facade, run, tmp, "STALE", created_at=NOW + timedelta(days=8))


def test_decision_before_the_run_is_refused(setup):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "STALE Stage 7 run", created_at=NOW - timedelta(minutes=5))


def test_a_newer_completed_session_forces_a_rerun_even_inside_the_age_window(setup):
    facade, run, tmp = setup
    later = NOW + timedelta(hours=24)  # next XNYS close (2026-09-03 20:00Z) has passed; age 24h < 96h
    rejects(facade, run, tmp, "STALE price", created_at=later, evidence=funded_evidence(now=later))


# ---- changed ---------------------------------------------------------------------------------------
@pytest.mark.parametrize("over,needle", [
    ({"price": 130.0}, "price: Stage 7 100.0 vs now 130.0"),
    ({"price": 100.01}, "price"),
    ({"provider": "OTHER"}, "provider"),
    ({"quoted_instrument": "ELIG Class B (XNYS)"}, "quoted_instrument"),
    ({"price_as_of": datetime(2026, 9, 2, 20, 1, tzinfo=timezone.utc)}, "price_as_of"),
    ({"quoted_security_key": "SEC:OTHER"}, "quoted_security_key"),
    ({"ticker": "OTHR"}, "ticker"),
    ({"adjusted": True}, "adjusted"),
    ({"currency": "EUR"}, "currency"),
])
def test_changed_price_evidence_is_refused(setup, over, needle):
    facade, run, tmp = setup
    rejects(facade, run, tmp, needle, evidence=FundedFreshnessEvidence(
        fresh_price=replace(funded_evidence().fresh_price, **over), treasury_reattested=funded_evidence().treasury_reattested))


def test_stale_labelled_fresh_price_is_refused(setup):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "not FRESH", evidence=FundedFreshnessEvidence(
        fresh_price=replace(funded_evidence().fresh_price, freshness_status=FreshnessStatus.STALE),
        treasury_reattested=funded_evidence().treasury_reattested))


@pytest.mark.parametrize("over", [{"value": 0.041}, {"value": 0.0390001}, {"reference_key": "UST-26W"}, {"provider": "other"},
                                  {"as_of": NOW - timedelta(days=1)}, {"currency": "EUR"}])
def test_changed_treasury_reattestation_is_refused(setup, over):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "Treasury reference re-attestation differs", evidence=FundedFreshnessEvidence(
        fresh_price=funded_evidence().fresh_price, treasury_reattested=replace(funded_evidence().treasury_reattested, **over)))


def test_stale_labelled_treasury_reattestation_is_refused(setup):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "Treasury reference is outside", evidence=FundedFreshnessEvidence(
        fresh_price=funded_evidence().fresh_price,
        treasury_reattested=replace(funded_evidence().treasury_reattested, freshness_status=FreshnessStatus.STALE)))


# ---- old format / non-USD / no exchange: fail closed -------------------------------------------------------
def crafted(facade, tmp, mutate):
    """An ELIGIBLE run whose retained artifact is rewritten (and re-hashed) with a modified or absent price_basis."""
    run = _eligible_run(facade, name="stage7-crafted")
    data = json.loads(Path(run.artifact_ref.artifact_path).read_text())
    mutate(data)
    ref = freeze_payload(data, version="stage7-control-v0.2", destination=tmp / "crafted" / "s7.json")
    return Stage7Run(result=run.result, rendered_text=run.rendered_text, artifact_ref=ref)


def test_older_format_artifact_cannot_fund_but_can_hold_cash(tmp_path):
    facade = _facade(tmp_path)
    old = crafted(facade, tmp_path, lambda d: d.pop("price_basis"))
    rejects(facade, old, tmp_path, "no frozen price basis")
    rec = fund(facade, old, tmp_path, action="HOLD CASH", evidence=None, record_id="OLD-HOLD")
    assert rec.human_stage8_action.value == "HOLD CASH"


def test_non_usd_and_missing_or_unsupported_exchange_fail_closed(tmp_path):
    facade = _facade(tmp_path)
    rejects(facade, crafted(facade, tmp_path / "a", lambda d: d["price_basis"]["price_snapshot"].update(currency="EUR")), tmp_path, "Non-USD")
    rejects(facade, crafted(facade, tmp_path / "b", lambda d: d["price_basis"]["price_snapshot"].update(quoted_instrument="ELIG")), tmp_path, "names no exchange")
    rejects(facade, crafted(facade, tmp_path / "c", lambda d: d["price_basis"]["price_snapshot"].update(quoted_instrument="ELIG (ZZZZ)")), tmp_path, "Session authority")
    rejects(facade, crafted(facade, tmp_path / "d", lambda d: d["price_basis"].pop("treasury_reference")), tmp_path, "no Treasury reference")


def test_tampered_stage7_artifact_cannot_fund(setup):
    facade, run, tmp = setup
    p = Path(run.artifact_ref.artifact_path)
    p.write_text(p.read_text().replace('"price":100.0', '"price":90.0'))
    rejects(facade, run, tmp, "hash-mismatched")


# ---- success keeps its proof -------------------------------------------------------------------------------------
def test_unchanged_evidence_is_accepted_and_the_checked_evidence_is_retained(setup):
    facade, run, tmp = setup
    rec = fund(facade, run, tmp)
    assert rec.human_stage8_action.value == "INITIATE" and facade.verify_ledger()
    art = facade.artifact_dir / "F-1.funded_freshness.json"
    from stock_atlas.models import FrozenInputRef
    data = json.loads(art.read_text())
    assert data["stage7_sha256"] == run.artifact_ref.sha256 and data["session_authority"]["mic"] == "XNYS"
    assert data["frozen_price_basis"]["price_snapshot"]["price"] == data["fresh_price"]["price"] == 100.0


def test_rejection_leaves_no_retained_check_artifact(setup):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "price", evidence=funded_evidence(price=130.0))
    assert not list(facade.artifact_dir.glob("*.funded_freshness.json"))


# ---- non-actions stay available ------------------------------------------------------------------------------------
@pytest.mark.parametrize("action", ["HOLD CASH", "DO NOTHING"])
@pytest.mark.parametrize("when", [NOW, NOW + timedelta(days=8)])
def test_hold_cash_and_do_nothing_need_no_evidence_even_for_a_stale_run(setup, action, when):
    facade, run, tmp = setup
    rec = fund(facade, run, tmp, action=action, evidence=None, created_at=when, record_id=f"NA-{action}-{when:%d}")
    assert rec.human_stage8_action.value == action and facade.verify_ledger()


# ---- UI-funded path: the backend refuses even if the UI guard is bypassed ------------------------------------------------
from atlas_ui import demo
from atlas_ui.__main__ import build
from atlas_ui.service import Rejected
from test_atlas_ui import NOW as UI_NOW, good_req, s8


def test_ui_funded_path_is_refused_by_the_backend_when_the_ui_guard_is_disabled(tmp_path, monkeypatch):
    app = build(True, tmp_path / "ui")
    e = app.svc.run(good_req(), UI_NOW)
    changed = demo.FixtureProvider(price=130.0)

    def forged_gate(entry, form, now, reject):  # a UI that skipped its own checks and handed the backend a changed bind
        from live_price_binding import bind_price_snapshot
        from live_session_calendar import latest_completed_session
        snap = bind_price_snapshot(changed, "DEMOCO", expected_security_key=demo.DEMO_KEY, attestation=latest_completed_session(now)).snapshot
        t = MarketReferenceSnapshot("UST-13W", 0.039, datetime.fromisoformat(UI_NOW.date().isoformat() + "T00:00:00+00:00"),
                                    "HUMAN-ATTESTED U.S. Treasury par curve — not independently verified by Atlas", FreshnessStatus.FRESH, "USD")
        return FundedFreshnessEvidence(fresh_price=snap, treasury_reattested=t)

    monkeypatch.setattr(app.svc, "_fresh_price_gate", forged_gate)
    before = Path(app.ws.facade.store.path).read_bytes() if Path(app.ws.facade.store.path).exists() else b""
    with pytest.raises(Rejected, match="backend refused.*does not reproduce the frozen Stage 7 evidence") as ei:
        app.svc.record_stage8(e["run_id"], s8(), UI_NOW)
    assert (ei.value.rows_before, ei.value.rows_after) == (0, 0) and app.svc.ledger_rows() == []
    assert app.svc.record_stage8(e["run_id"], s8(action="HOLD CASH"), UI_NOW)["rows_after"] == 1


def test_ui_funded_unchanged_path_still_works_end_to_end(tmp_path):
    app = build(True, tmp_path / "ui")
    e = app.svc.run(good_req(), UI_NOW)
    out = app.svc.record_stage8(e["run_id"], s8(), UI_NOW)
    assert out["rows_after"] == 1 and (app.ws.facade.artifact_dir / f"S8-{e['run_id']}.funded_freshness.json").exists()
