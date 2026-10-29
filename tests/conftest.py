"""Shared test support.

``facade_clock`` substitutes the facade's PRIVATE ``_now`` method for deterministic tests (FROZEN_CONTROL_CHANGE_002).
Production code has no clock parameter; the facade itself refuses a replaced clock when the pytest runner is not loaded.
"""
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
    monkeypatch.setattr(CapitalDecisionFacade, "_now", lambda self: clock())
    return clock
