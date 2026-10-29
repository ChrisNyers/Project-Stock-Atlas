"""Shared test support.

``facade_clock`` pins the time the facade uses for funded-decision freshness (FROZEN_CONTROL_CHANGE_003). The production class has no clock
method, parameter or test-runner exemption: ``record_final_decision`` reads a sealed backend clock. For deterministic tests this fixture
replaces the TEST-SIDE binding of ``record_final_decision`` with a function that calls the private ``_record_final_decision_at(..., now=<pinned>)``.
That is the only place in the repository, apart from ``atlas_ui/evidence`` probes, that does so.
"""
import inspect
from datetime import datetime, timezone

import pytest

from capital_decision_facade import CapitalDecisionFacade


class FacadeClock:
    def __init__(self):
        self.t = None

    def set(self, dt):
        self.t = dt

    def __call__(self):
        return self.t or datetime.now(timezone.utc)


@pytest.fixture
def facade_clock(monkeypatch):
    clock = FacadeClock()

    def pinned(self, stage7_run, **kwargs):
        return self._record_final_decision_at(stage7_run, now=clock(), **kwargs)

    pinned.__signature__ = inspect.signature(CapitalDecisionFacade.record_final_decision)  # signature tests still see the real public contract
    monkeypatch.setattr(CapitalDecisionFacade, "record_final_decision", pinned)
    return clock
