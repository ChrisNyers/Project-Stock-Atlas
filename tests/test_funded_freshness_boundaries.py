"""Workstream A (backend completion package): calendar/age boundaries of the funded-freshness safeguard, plus the
reproduced Material finding as a STRICT xfail (it flips to a failure the moment the safeguard is fixed, forcing this test
to be promoted to a normal test). No frozen control is modified here. Fixture data; paper only.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from capital_decision_facade import ControlFailure
from test_funded_freshness_facade import fund, ledger_bytes, rejects
from test_integration_facade import NOW, _eligible_run, _facade, funded_evidence

CLOSE_SEP3 = datetime(2026, 9, 3, 20, 0, tzinfo=timezone.utc)  # XNYS regular close on 2026-09-03 (EDT)


@pytest.fixture
def setup(tmp_path):
    facade = _facade(tmp_path)
    return facade, _eligible_run(facade), tmp_path


def test_decision_one_second_before_the_next_close_still_stands_on_the_priced_session(setup):
    facade, run, tmp = setup
    t = CLOSE_SEP3 - timedelta(seconds=1)
    rec = fund(facade, run, tmp, created_at=t, evidence=funded_evidence(now=NOW), record_id="BOUND-BEFORE")
    assert rec.human_stage8_action.value == "INITIATE" and facade.verify_ledger()


def test_decision_exactly_at_the_next_close_requires_a_rerun(setup):
    facade, run, tmp = setup
    rejects(facade, run, tmp, "STALE price", created_at=CLOSE_SEP3, evidence=funded_evidence(now=NOW))


def test_negative_age_boundary_is_sixty_seconds(setup):
    facade, run, tmp = setup
    ok = fund(facade, run, tmp, created_at=NOW - timedelta(seconds=60), record_id="NEG-OK")
    assert ok.record_id == "NEG-OK"
    facade2 = _facade(tmp / "second")
    run2 = _eligible_run(facade2, name="stage7-neg")
    rejects(facade2, run2, tmp / "second", "STALE Stage 7 run", created_at=NOW - timedelta(seconds=61))


def test_all_rejections_above_left_the_ledger_intact(setup):
    facade, run, tmp = setup
    before = ledger_bytes(facade)
    with pytest.raises(ControlFailure):
        fund(facade, run, tmp, created_at=CLOSE_SEP3, evidence=funded_evidence(now=NOW))
    assert ledger_bytes(facade) == before and facade.verify_ledger()


@pytest.mark.xfail(strict=True, reason="REPRODUCED MATERIAL FINDING (see FROZEN_CONTROL_CHANGE_002_PROPOSED.md): the facade measures run "
                   "age and session against the CALLER-SUPPLIED created_at, so a direct caller who states a created_at near the run "
                   "defeats the staleness safeguard. Real wall-clock now is ~2026-10; the fixture run is 2026-09-02.")
def test_a_direct_caller_cannot_backdate_created_at_to_defeat_the_staleness_safeguard(setup):
    facade, run, tmp = setup
    # created_at == the run's own time, evidence copied from the run: identical to what a careless script would do.
    with pytest.raises(ControlFailure):
        fund(facade, run, tmp, created_at=NOW, record_id="BACKDATED")
