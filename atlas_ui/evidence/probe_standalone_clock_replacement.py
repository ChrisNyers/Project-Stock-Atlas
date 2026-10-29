"""Probe (FROZEN_CONTROL_CHANGE_003): can an ORDINARY standalone Python process (no pytest runner) control the facade clock?

Reproduces independent-review finding 1 on 1683f98 and is re-run after the fix. Each vector uses a fresh facade and a real, hashed,
ELIGIBLE Stage 7 run dated 2026-09-02 (fixture, paper only, temp directory) and then asks for a funded INITIATE. The real wall clock is
today, so a correct backend must refuse every vector (the run is far older than 96 h) and leave the ledger byte-identical.

Run:  python atlas_ui/evidence/probe_standalone_clock_replacement.py     (NOT under pytest)
"""
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest  # noqa: F401  — deliberately imported: the 1683f98 guard treated "pytest in sys.modules" as permission to swap the clock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1]), str(HERE.parents[1] / "tests")]

import capital_decision_facade as cdf  # noqa: E402
from capital_decision_facade import CapitalDecisionFacade, ControlFailure  # noqa: E402
from stock_atlas.models import RevisitTriggers  # noqa: E402
from test_integration_facade import NOW, _eligible_run, _facade, _input_versions, funded_evidence  # noqa: E402

assert "PYTEST_CURRENT_TEST" not in __import__("os").environ, "run this probe outside the pytest runner"


class _FakeDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW


def attempt(label, tamper, *, private_entry=False, factory=None):
    tmp = Path(tempfile.mkdtemp())
    facade = (factory or _facade)(tmp)
    run = _eligible_run(facade)
    try:
        restore = tamper(facade)
    except AttributeError:
        print(f"N/A       (does not exist at this commit)  {label}")
        return "N/A"
    before = Path(facade.store.path).read_bytes() if Path(facade.store.path).exists() else b""
    call = (lambda *a, **k: facade._record_final_decision_at(*a, now=NOW, **k)) if private_entry else facade.record_final_decision
    try:
        call(
            run, record_id="PROBE", human_stage8_action="INITIATE", human_rationale="standalone clock replacement probe",
            alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"), input_versions=_input_versions(tmp),
            created_at=NOW, portfolio_snapshot_id="PROBE", dominant_drivers=("fixture",),
            revisit_triggers=RevisitTriggers("p", NOW + timedelta(days=90)), starter_cap_weight=0.10,
            funded_freshness=funded_evidence())
        verdict = "ACCEPTED"
    except ControlFailure as exc:
        verdict = "REJECTED"
        label += f"  [{str(exc)[:70]}]"
    after = Path(facade.store.path).read_bytes() if Path(facade.store.path).exists() else b""
    rows = after.count(b"\n")
    print(f"{verdict:9s} ledger_rows={rows} ledger_unchanged={after == before}  {label}")
    restore()
    return verdict


def v_instance(f):
    f._now = lambda: NOW
    return lambda: None


def v_class(f):
    orig = CapitalDecisionFacade.__dict__.get("_now")
    CapitalDecisionFacade._now = lambda self: NOW
    return lambda: setattr(CapitalDecisionFacade, "_now", orig) if orig else delattr(CapitalDecisionFacade, "_now")


def v_subclass(f):
    return lambda: None  # the tamper is the subclass itself (see factory below)


def v_private_entry(f):
    f._record_final_decision_at  # AttributeError if absent  # noqa: B018
    return lambda: None


def v_overwrite_sealed_clock(f):
    cdf._BACKEND_UTC_NOW  # AttributeError if absent  # noqa: B018
    orig = cdf._BACKEND_UTC_NOW
    cdf._BACKEND_UTC_NOW = lambda: NOW
    return lambda: setattr(cdf, "_BACKEND_UTC_NOW", orig)


def v_module_datetime(f):
    orig = cdf.datetime
    cdf.datetime = _FakeDatetime
    return lambda: setattr(cdf, "datetime", orig)


if __name__ == "__main__":
    print(f"real wall clock {datetime.now(timezone.utc):%Y-%m-%d %H:%MZ}; fixture run dated {NOW:%Y-%m-%d %H:%MZ}; pytest imported: {'pytest' in sys.modules}")
    class Sneaky(CapitalDecisionFacade):
        def _now(self):
            return NOW

    sneaky = lambda tmp: Sneaky(ledger_path=tmp / "decisions.jsonl", artifact_dir=tmp / "artifacts")
    print("-- ordinary routes: every one must be REJECTED --")
    results = [
        attempt("replace instance facade._now", v_instance),
        attempt("replace class CapitalDecisionFacade._now", v_class),
        attempt("subclass defining _now", v_subclass, factory=sneaky),
        attempt("replace capital_decision_facade.datetime", v_module_datetime),
        attempt("pytest imported, nothing replaced, honest stale call", lambda f: (lambda: None)),
    ]
    print("-- documented RESIDUAL (editing the control from inside the process; see FROZEN_CONTROL_CHANGE_003 section 4) --")
    residual = [
        attempt("RESIDUAL a: call private _record_final_decision_at(now=...) directly", v_private_entry, private_entry=True),
        attempt("RESIDUAL b: overwrite module _BACKEND_UTC_NOW", v_overwrite_sealed_clock),
    ]
    bad = [r for r in results if r == "ACCEPTED"]
    print("SUMMARY ordinary routes:", "ALL REFUSED" if not bad else f"{len(bad)} ACCEPTED A STALE FUNDED INITIATE")
    print("SUMMARY residual (not claimed closed):", ", ".join(residual))
    sys.exit(1 if bad else 0)
