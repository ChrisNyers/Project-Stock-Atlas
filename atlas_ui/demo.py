"""DEMO mode: a fixture price provider and an isolated workspace.

Everything produced here is labelled FIXTURE and lives in a separate directory.
The canonical service refuses any provider not in its allow-list, so a fixture
price can never back a canonical Stage 7 run. Demo output is NOT evidence.
"""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from live_session_calendar import latest_completed_session
from operating_mvp import ledger

DEMO_TICKER = "DEMOCO"
DEMO_KEY = "DEMO-FIXTURE:0000000:DEMOCO"
DEMO_PROVIDER = "FIXTURE-DEMO"


class _R:
    def __init__(self, d):
        self._d = d

    def to_dict(self):
        return self._d


class FixtureProvider:
    """Offline stand-in shaped like the TwelveData adapter. Always labelled FIXTURE-DEMO."""

    def __init__(self, clock=lambda: datetime.now(timezone.utc), price: float = 100.0, mic: str = "XNYS",
                 provider: str = DEMO_PROVIDER, currency: str = "USD", quote_offset_s: int = 0, name: str = "Demo Co (fixture)",
                 key: str = DEMO_KEY):
        self._clock, self._price, self._mic = clock, price, mic
        self._provider, self._currency, self._offset, self._name, self._key = provider, currency, quote_offset_s, name, key

    def resolve_symbol(self, symbol):
        return _R({"state": "AVAILABLE", "security_key": self._key})

    def latest_price(self, symbol):
        att = latest_completed_session(self._clock(), mic=self._mic)
        return _R({"state": "AVAILABLE", "security_key": self._key, "provider": self._provider,
                   "data": {"price": self._price, "mic_code": self._mic, "is_market_open": False},
                   "raw": {"currency": self._currency, "mic_code": self._mic, "datetime": att.session_date.isoformat(),
                           "last_quote_at": int(att.session_close_utc.timestamp()) + self._offset, "name": self._name}})


def seed_demo_workspace(root: Path, canonical_ledger: Path) -> Path:
    """Copy the canonical candidate ledger and add one fixture candidate at READY_FOR_CAPITAL_COMPARISON."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    dest = root / "candidate_ledger.jsonl"
    if not dest.exists():
        shutil.copyfile(canonical_ledger, dest)
        ledger.surface(dest, name="Demo Co (fixture)", ticker=DEMO_TICKER, source="OTHER",
                       source_detail="DEMO fixture candidate — not a real company",
                       why_surfaced="Fixture used to exercise the Stage 7 / Stage 8 UI flow end to end.",
                       investment_question="Does the demo fixture clear the comparison gates? (not real)")
        ledger.freeze_stance(dest, candidate_id=DEMO_TICKER, stance_text="NEUTRAL — demo fixture, no view.")
        ledger.change_state(dest, candidate_id=DEMO_TICKER, to_state="QUICK_TEST", reason="demo")
        ledger.record_falsification(dest, candidate_id=DEMO_TICKER, test="demo fixture test", result="SURVIVED",
                                    grade="UNCERTIFIED", source_ref="FIXTURE")
        ledger.change_state(dest, candidate_id=DEMO_TICKER, to_state="UNDERWRITING", reason="demo")
        ledger.change_state(dest, candidate_id=DEMO_TICKER, to_state="READY_FOR_CAPITAL_COMPARISON", reason="demo")
    return dest
