"""FROZEN_CONTROL_CHANGE_003 — an ordinary caller cannot choose the clock the facade uses for a funded decision.

The 1683f98 guard accepted any replaced clock whenever ``"pytest" in sys.modules``; a plain script that imported pytest and assigned
``facade._now = ...`` got a stale paper INITIATE recorded. These tests (a) run the reviewer's route in a SUBPROCESS outside the pytest runner,
(b) try the same routes in-process against the REAL public entry point (these tests deliberately do not use the ``facade_clock`` fixture),
(c) prove with a negative mutation that these tests would catch a regression, and (d) check the removed machinery stays removed.
Every rejection asserts the decision ledger is byte-identical. Fixture data; paper only; nothing live.
"""
import ast
import inspect
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest

import capital_decision_facade as cdf
from capital_decision_facade import CapitalDecisionFacade, ControlFailure
from stock_atlas.models import RevisitTriggers
from test_integration_facade import NOW, _eligible_run, _facade, _input_versions, funded_evidence

ROOT = Path(__file__).resolve().parent.parent
PROBE = ROOT / "atlas_ui" / "evidence" / "probe_standalone_clock_replacement.py"


def ledger_bytes(facade) -> bytes:
    p = Path(facade.store.path)
    return p.read_bytes() if p.exists() else b""


def call(entry, facade, run, tmp, *, action="INITIATE", evidence="default", created_at=NOW, record_id="CLK"):
    """A funded request that is internally consistent with the Sept-2 fixture world (the only thing wrong with it is the real date)."""
    return entry(
        run, record_id=record_id, human_stage8_action=action, human_rationale="paper decision",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"), input_versions=_input_versions(tmp),
        created_at=created_at, portfolio_snapshot_id="INTEGRATION", dominant_drivers=("enterprise IT",),
        revisit_triggers=RevisitTriggers("±25% price", created_at + timedelta(days=90)), starter_cap_weight=0.10,
        funded_freshness=funded_evidence() if evidence == "default" else evidence)


def attempt(facade, run, tmp, entry=None, **kw):
    """-> (accepted, ledger_unchanged). Uses the facade's real public entry unless a different one is supplied."""
    entry = entry or facade.record_final_decision
    before = ledger_bytes(facade)
    try:
        call(entry, facade, run, tmp, **kw)
        accepted = True
    except ControlFailure:
        accepted = False
    return accepted, ledger_bytes(facade) == before


@pytest.fixture
def setup(tmp_path):
    facade = _facade(tmp_path)
    return facade, _eligible_run(facade), tmp_path


def assert_refused(facade, run, tmp, **kw):
    accepted, unchanged = attempt(facade, run, tmp, **kw)
    assert not accepted and unchanged and facade.verify_ledger()
    assert not list(facade.artifact_dir.glob("*.funded_freshness.json"))  # not even the audit artifact of a funded check


# ---- (a) outside the pytest runner: the reviewer's reproduction ------------------------------------------------------------
def test_standalone_script_outside_the_pytest_runner_cannot_choose_the_clock():
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST")}
    r = subprocess.run([sys.executable, str(PROBE)], capture_output=True, text=True, env=env, cwd=ROOT, timeout=120)
    out = r.stdout
    assert "pytest imported: True" in out, out  # the probe imports pytest on purpose
    ordinary = [l for l in out.splitlines() if l.split() and l.split()[0] in ("ACCEPTED", "REJECTED") and "RESIDUAL" not in l]
    assert len(ordinary) == 5, out
    assert all(l.startswith("REJECTED") and "ledger_rows=0 ledger_unchanged=True" in l for l in ordinary), out
    assert "SUMMARY ordinary routes: ALL REFUSED" in out and r.returncode == 0, out + r.stderr


# ---- (b) the same routes in-process, against the REAL public entry ------------------------------------------------------------------
def test_replacing_an_instance_clock_has_no_effect(setup):
    facade, run, tmp = setup
    facade._now = lambda: NOW
    assert_refused(facade, run, tmp)


def test_patching_the_class_clock_has_no_effect(setup, monkeypatch):
    facade, run, tmp = setup
    monkeypatch.setattr(CapitalDecisionFacade, "_now", lambda self: NOW, raising=False)
    assert_refused(facade, run, tmp)


def test_a_subclass_defining_a_clock_has_no_effect(tmp_path):
    class Sneaky(CapitalDecisionFacade):
        def _now(self):
            return NOW

        def _trusted_now(self):
            return NOW

    facade = Sneaky(ledger_path=tmp_path / "d.jsonl", artifact_dir=tmp_path / "artifacts")
    assert_refused(facade, _eligible_run(facade), tmp_path)


def test_patching_the_modules_datetime_name_has_no_effect(setup, monkeypatch):
    from datetime import datetime

    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW

    facade, run, tmp = setup
    monkeypatch.setattr(cdf, "datetime", FakeDatetime)
    assert_refused(facade, run, tmp)


def test_having_pytest_loaded_grants_nothing(setup):
    facade, run, tmp = setup
    assert "pytest" in sys.modules  # we are running under it, and an honest stale call is still refused
    assert_refused(facade, run, tmp)


def test_stale_run_with_a_consistent_created_at_is_still_refused(setup):
    facade, run, tmp = setup
    assert_refused(facade, run, tmp, created_at=NOW + timedelta(days=8), evidence=funded_evidence(now=NOW + timedelta(days=8)))


def test_every_funded_action_is_refused_not_just_initiate(setup):
    facade, run, tmp = setup
    for i, action in enumerate(("INITIATE", "ADD")):
        assert_refused(facade, run, tmp, action=action, record_id=f"A-{i}")


def test_non_actions_remain_recordable_through_the_real_entry(setup):
    facade, run, tmp = setup
    for i, action in enumerate(("HOLD CASH", "DO NOTHING")):
        accepted, _ = attempt(facade, run, tmp, action=action, evidence=None, record_id=f"NA-{i}")
        assert accepted
    assert facade.verify_ledger()


# ---- (c) negative mutation: these tests do detect a replaceable clock ----------------------------------------------------------------
def test_negative_mutation_a_replaceable_clock_is_accepted_by_the_attempt_helper(setup):
    """If production code ever read ``self._now()`` again, ``attempt`` (and so every test above) would report ACCEPTED."""
    facade, run, tmp = setup
    facade._now = lambda: NOW

    def mutated_entry(stage7_run, **kwargs):  # the 1683f98 shape: the clock is whatever the instance says it is
        return facade._record_final_decision_at(stage7_run, now=facade._now(), **kwargs)

    accepted, unchanged = attempt(facade, run, tmp, entry=mutated_entry)
    assert accepted and not unchanged, "the helper must be able to see a clock bypass; otherwise the tests above prove nothing"
    # ...while the real entry, on a fresh facade with the same tampering, refuses
    f2 = _facade(tmp / "second")
    f2._now = lambda: NOW
    assert_refused(f2, _eligible_run(f2), tmp / "second")


# ---- (d) the removed machinery stays removed ------------------------------------------------------------------------------------------
def test_no_clock_parameter_or_clock_method_exists_on_the_public_surface():
    for name in dir(CapitalDecisionFacade):
        if not name.startswith("__"):
            params = set(inspect.signature(getattr(CapitalDecisionFacade, name)).parameters) if callable(getattr(CapitalDecisionFacade, name)) else set()
            if not name.startswith("_"):
                assert not ({"clock", "now", "utc_now", "trusted_now", "time_source"} & params), (name, params)
    for gone in ("_now", "_trusted_now"):
        assert not hasattr(CapitalDecisionFacade, gone), gone
    assert not hasattr(cdf, "_ORIGINAL_NOW")


def test_facade_source_has_no_test_runner_or_replaced_clock_logic():
    src = inspect.getsource(cdf)
    for forbidden in ("pytest", "sys.modules", "_ORIGINAL_NOW", "_trusted_now", "import sys"):
        assert forbidden not in src, forbidden
    assert "self._now" not in src and "def _now" not in src


def test_only_tests_and_evidence_probes_reference_the_private_time_entry():
    allowed_dirs = {"tests", "evidence", ".venv", ".git", "deliverables", "__pycache__"}
    offenders = []
    for path in ROOT.rglob("*.py"):
        parts = set(path.relative_to(ROOT).parts)
        if parts & allowed_dirs or path.name == "capital_decision_facade.py":
            continue
        if any(isinstance(n, ast.Attribute) and n.attr == "_record_final_decision_at" or isinstance(n, ast.Name) and n.id == "_record_final_decision_at"
               for n in ast.walk(ast.parse(path.read_text(encoding="utf-8")))):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_sealed_clock_is_real_utc_system_time():
    from datetime import datetime, timezone
    t = cdf._BACKEND_UTC_NOW()
    assert t.utcoffset() == timedelta(0) and abs(t - datetime.now(timezone.utc)) < timedelta(seconds=5)


def test_a_non_utc_or_naive_time_into_the_private_implementation_fails_closed(setup):
    from datetime import datetime, timezone
    facade, run, tmp = setup
    for bad in (datetime(2026, 9, 2, 21, 0), NOW.astimezone(timezone(timedelta(hours=2)))):
        before = ledger_bytes(facade)
        with pytest.raises(ControlFailure, match="UTC"):
            call(lambda r, **kw: facade._record_final_decision_at(r, now=bad, **kw), facade, run, tmp)
        assert ledger_bytes(facade) == before
