"""FROZEN_CONTROL_CHANGE_002 — the facade's funded-decision freshness uses a TRUSTED backend UTC clock only.

`fund(..., now=<trusted time>, created_at=<what the caller claims>)` separates the two. Every rejection leaves the decision
ledger byte-identical. Fixture data; paper only.
"""
import inspect
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from capital_decision_facade import CapitalDecisionFacade, ControlFailure
from test_funded_freshness_facade import _clock, fund, ledger_bytes, rejects  # noqa: F401
from test_integration_facade import NOW, _eligible_run, _facade, funded_evidence


@pytest.fixture
def setup(tmp_path):
    facade = _facade(tmp_path)
    return facade, _eligible_run(facade), tmp_path


def refused(facade, run, tmp, match, **kw):
    before = ledger_bytes(facade)
    with pytest.raises(ControlFailure, match=match):
        fund(facade, run, tmp, **kw)
    assert ledger_bytes(facade) == before and facade.verify_ledger()


# ---- the caller's created_at never sets the time used for freshness ------------------------------------------
def test_eight_day_old_run_with_a_backdated_created_at_is_refused_with_zero_writes(setup):
    facade, run, tmp = setup
    late = NOW + timedelta(days=8)  # the real time of the decision
    # (a) caller backdates created_at to the run's time -> inconsistent with the trusted clock
    refused(facade, run, tmp, "trusted backend clock", created_at=NOW + timedelta(minutes=1), now=late)
    # (b) caller is honest about created_at -> the run is simply stale
    refused(facade, run, tmp, "STALE", created_at=late, now=late, evidence=funded_evidence(now=late))
    assert not list(facade.artifact_dir.glob("*.funded_freshness.json"))


def test_a_caller_created_at_cannot_rescue_a_newer_session_or_stale_treasury(setup):
    facade, run, tmp = setup
    next_day = NOW + timedelta(hours=24)   # a newer XNYS session has completed; run age is only 24h
    refused(facade, run, tmp, "trusted backend clock", created_at=NOW, now=next_day)
    refused(facade, run, tmp, "STALE price", created_at=next_day, now=next_day, evidence=funded_evidence(now=next_day))


def test_legitimate_fresh_decision_and_non_actions_still_work(setup):
    facade, run, tmp = setup
    assert fund(facade, run, tmp, record_id="OK-FUND").human_stage8_action.value == "INITIATE"
    for i, action in enumerate(("HOLD CASH", "DO NOTHING")):
        for when in (NOW, NOW + timedelta(days=8)):
            # non-actions need no evidence and no clock agreement, even with a wildly different trusted time
            rec = fund(facade, run, tmp, action=action, evidence=None, created_at=NOW, now=when, record_id=f"NA-{i}-{when:%d}")
            assert rec.human_stage8_action.value == action
    assert facade.verify_ledger()


# ---- the five-minute tolerance: consistency check, both directions ---------------------------------------------------
@pytest.mark.parametrize("delta_s,ok", [(0, True), (299, True), (-299, True), (300, True), (-300, True), (301, False), (-301, False), (3600, False), (-3600, False)])
def test_created_at_must_agree_with_the_trusted_clock_within_five_minutes_either_way(setup, delta_s, ok):
    facade, run, tmp = setup
    created = NOW + timedelta(seconds=delta_s)
    if ok:
        assert fund(facade, run, tmp, created_at=created, now=NOW, record_id="TOL").record_id == "TOL"
    else:
        refused(facade, run, tmp, "trusted backend clock", created_at=created, now=NOW)


def test_tolerance_is_not_a_freshness_input_a_consistent_timestamp_on_a_stale_run_is_still_stale(setup):
    facade, run, tmp = setup
    t = NOW + timedelta(days=5)
    refused(facade, run, tmp, "STALE", created_at=t, now=t, evidence=funded_evidence(now=t))


# ---- no public clock parameter; replaced clock fails closed outside a test run ---------------------------------------------
def test_there_is_no_public_way_to_choose_now():
    for fn in (CapitalDecisionFacade.__init__, CapitalDecisionFacade.record_final_decision, CapitalDecisionFacade.run_stage7):
        names = set(inspect.signature(fn).parameters)
        assert not ({"clock", "now", "utc_now", "trusted_now", "time_source"} & names), (fn.__name__, names)


def test_instance_subclass_and_class_clock_overrides_fail_closed_outside_pytest(setup, monkeypatch):
    facade, run, tmp = setup
    monkeypatch.delitem(sys.modules, "pytest")  # simulate a production process: the test runner is not loaded
    # the autouse fixture already replaced the class method -> detected
    refused(facade, run, tmp, "clock has been replaced", created_at=NOW)
    monkeypatch.undo()


def test_instance_attribute_override_is_detected(tmp_path, monkeypatch):
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    facade._now = lambda: NOW  # an ordinary caller trying to choose "now" on the instance
    monkeypatch.delitem(sys.modules, "pytest")
    with pytest.raises(ControlFailure, match="clock has been replaced"):
        fund(facade, run, tmp_path)


def test_subclass_override_is_detected(tmp_path, monkeypatch):
    class Sneaky(CapitalDecisionFacade):
        def _now(self):
            return NOW

    facade = Sneaky(ledger_path=tmp_path / "d.jsonl", artifact_dir=tmp_path / "artifacts")
    run = _eligible_run(facade)
    monkeypatch.delitem(sys.modules, "pytest")
    with pytest.raises(ControlFailure, match="clock has been replaced"):
        fund(facade, run, tmp_path)
    assert not (tmp_path / "d.jsonl").exists() or facade.verify_ledger()


def test_naive_or_non_utc_clock_fails_closed(setup, facade_clock):
    facade, run, tmp = setup
    refused(facade, run, tmp, "UTC", created_at=NOW, now=datetime(2026, 9, 2, 21, 0))  # naive
    refused(facade, run, tmp, "UTC", created_at=NOW, now=NOW.astimezone(timezone(timedelta(hours=2))))


def test_unreplaced_default_clock_is_the_real_system_time(tmp_path):
    f = _facade(tmp_path)
    assert type(f)._now is CapitalDecisionFacade._now  # (patched by the autouse fixture during tests; the real one is exercised below)
    real = datetime.now(timezone.utc)
    from capital_decision_facade import _ORIGINAL_NOW
    assert abs(_ORIGINAL_NOW(f) - real) < timedelta(seconds=5) and _ORIGINAL_NOW(f).utcoffset() == timedelta(0)


def test_checked_evidence_records_the_trusted_time_and_the_claimed_created_at(setup):
    facade, run, tmp = setup
    import json
    fund(facade, run, tmp, created_at=NOW + timedelta(minutes=2), now=NOW, record_id="REC")
    d = json.loads((facade.artifact_dir / "REC.funded_freshness.json").read_text())
    assert d["checked_at"].startswith("2026-09-02T21:00:00") and d["created_at"].startswith("2026-09-02T21:02:00")
