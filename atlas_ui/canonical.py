"""Canonical pilot state, read from the frozen repo records (never from the browser).

The Cycle 0 baseline is parsed from the frozen document
``docs/controlled_live_pilot/CYCLE0_BASELINE_001.md`` (Correction 002 table) and
re-validated on every load; any mismatch fails closed. A hash of the document is
carried so downstream artifacts can name the exact baseline they used.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from stock_atlas.models import FundingPocket, Holding, PortfolioSnapshot, VerificationStatus

REPO = Path(__file__).resolve().parent.parent
BASELINE_DOC = REPO / "docs" / "controlled_live_pilot" / "CYCLE0_BASELINE_001.md"

EXPECTED_STOCKS_TOTAL = Decimal("624905.93")
DEFENSIVE_APPROX = Decimal("59000")  # T-bills + money market, "≈" per the frozen record
EXPECTED_NAMES = 28
FUNDING_POCKET_MAX = 50_000.0
FUNDING_POCKET_MIN = 25_000.0
STARTER_CAP_WEIGHT = 0.02  # frozen Investor Policy: STARTER 1–2% of post-trade portfolio


class CanonicalError(Exception):
    pass


@dataclass(frozen=True)
class Cycle0:
    holdings: tuple[tuple[str, Decimal], ...]
    stocks_total: Decimal
    defensive_approx: Decimal
    identified_value: Decimal
    as_of: str
    doc_path: str
    doc_sha256: str
    label: str = "HUMAN-SUPPLIED BASELINE — APPROXIMATE (defensive ≈ $59,000); not a live account balance"

    @property
    def effective_at(self) -> datetime:
        """When the human-supplied valuation applies (the frozen record's date) — NOT the decision time."""
        return datetime.fromisoformat(self.as_of[:10] + "T00:00:00+00:00")

    def weight(self, ticker: str) -> float:
        for t, v in self.holdings:
            if t == ticker.upper():
                return float(v / self.identified_value)
        return 0.0


def load_cycle0(doc: Path = BASELINE_DOC) -> Cycle0:
    doc = Path(doc)
    if not doc.is_file():
        raise CanonicalError(f"canonical Cycle 0 record missing: {doc}")
    raw = doc.read_bytes()
    text = raw.decode("utf-8")
    marker = "## Correction 002"
    if marker not in text:
        raise CanonicalError("Cycle 0 record lacks Correction 002 (28 holding values)")
    section = text[text.index(marker):]
    rows = re.findall(r"\|\s*([A-Z]{1,5})\s*\|\s*\$([\d,]+\.\d{2})\s*\|", section)
    names = [t for t, _ in rows]
    if len(names) != EXPECTED_NAMES or len(set(names)) != EXPECTED_NAMES:
        raise CanonicalError(f"expected {EXPECTED_NAMES} unique holdings, parsed {len(names)}/{len(set(names))}")
    holdings = tuple((t, Decimal(v.replace(",", ""))) for t, v in rows)
    total = sum(v for _, v in holdings)
    if total != EXPECTED_STOCKS_TOTAL:
        raise CanonicalError(f"holdings sum {total} != frozen {EXPECTED_STOCKS_TOTAL}; not adjusted")
    if dict(holdings).get("WSO") != Decimal("2247.24"):
        raise CanonicalError("WSO value does not match the frozen 8 x $280.905 = $2,247.24")
    return Cycle0(holdings, total, DEFENSIVE_APPROX, total + DEFENSIVE_APPROX, "2026-10-07 (Correction 002)",
                  str(doc.relative_to(REPO)) if doc.is_relative_to(REPO) else str(doc),
                  hashlib.sha256(raw).hexdigest())


def build_portfolio_snapshot(c0: Cycle0, *, as_of: datetime, funding_amount: float = FUNDING_POCKET_MAX,
                             tax: VerificationStatus = VerificationStatus.UNVERIFIED,
                             liquidity: VerificationStatus = VerificationStatus.UNVERIFIED,
                             execution: VerificationStatus = VerificationStatus.UNVERIFIED) -> PortfolioSnapshot:
    """Existing frozen contract, built from the canonical record. UNVERIFIED stays UNVERIFIED."""
    if not FUNDING_POCKET_MIN <= funding_amount <= FUNDING_POCKET_MAX:
        raise CanonicalError("funding pocket is $25,000–$50,000 under the frozen baseline")
    ident = float(c0.identified_value)
    holdings = tuple(
        Holding(f"UNBOUND-TICKER:{t}", t, float(v), float(v) / ident, "taxable brokerage", "taxable")
        for t, v in c0.holdings
    )
    return PortfolioSnapshot(
        snapshot_id=f"CYCLE0-{c0.doc_sha256[:12]}",
        as_of=as_of,
        total_value=ident,
        holdings=holdings,
        funding_pocket=FundingPocket(
            account="new outside capital", account_type="taxable", amount=float(funding_amount),
            t_plus_1_deployable=True, constraints_supplied=True,
            tax_status=tax, liquidity_status=liquidity, execution_status=execution),
        trims_permitted=False,
        add_only_policy=True,
    )
