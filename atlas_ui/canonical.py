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
    snapshot_id: str = ""

    @property
    def portfolio_snapshot_id(self) -> str:
        """The id a Stage 7 artifact names. Legacy Cycle 0 keeps its original derivation so earlier runs still reconstruct."""
        return self.snapshot_id or f"CYCLE0-{self.doc_sha256[:12]}"

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


def load_snapshot(spec: dict, repo: Path = REPO) -> Cycle0:
    """Load one APPROVED portfolio snapshot named by the authority register and re-validate it against what was approved: the document's SHA-256,
    holding count, unique tickers, declared total and any declared per-holding checks. Any mismatch fails closed. Nothing is adjusted."""
    doc = Path(repo) / spec["doc"]
    if not doc.is_file():
        raise CanonicalError(f"approved portfolio snapshot {spec['snapshot_id']!r}: record missing: {spec['doc']}")
    raw = doc.read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["doc_sha256"]:
        raise CanonicalError(f"approved portfolio snapshot {spec['snapshot_id']!r}: {spec['doc']} differs from the approved bytes (edited after approval)")
    text = raw.decode("utf-8")
    if spec["table_marker"] not in text:
        raise CanonicalError(f"snapshot record lacks its holdings section {spec['table_marker']!r}")
    rows = re.findall(r"\|\s*([A-Z]{1,5})\s*\|\s*\$([\d,]+\.\d{2})\s*\|", text[text.index(spec["table_marker"]):])
    names = [t for t, _ in rows]
    if len(names) != int(spec["holdings"]) or len(set(names)) != len(names):
        raise CanonicalError(f"expected {spec['holdings']} unique holdings, parsed {len(names)}/{len(set(names))}")
    holdings = tuple((t, Decimal(v.replace(",", ""))) for t, v in rows)
    total = sum(v for _, v in holdings)
    if total != Decimal(str(spec["stocks_total"])):
        raise CanonicalError(f"holdings sum {total} != approved {spec['stocks_total']}; not adjusted")
    for t, v in (spec.get("value_checks") or {}).items():
        if dict(holdings).get(t) != Decimal(str(v)):
            raise CanonicalError(f"{t} value does not match the approved {v}")
    defensive = Decimal(str(spec["defensive_approx"]))
    note = spec.get("as_of_note")
    return Cycle0(holdings, total, defensive, total + defensive, f"{spec['as_of']} ({note})" if note else spec["as_of"],
                  str(doc.relative_to(repo)), hashlib.sha256(raw).hexdigest(),
                  label=spec.get("label") or "HUMAN-SUPPLIED BASELINE — APPROXIMATE; not a live account balance", snapshot_id=spec["snapshot_id"])


def current_portfolio(repo: Path = REPO) -> Cycle0:
    """The latest APPROVED portfolio snapshot per the authority register (never a hardcoded date or file). Conflicting or unreadable authority
    records raise CanonicalError: callers fail closed rather than fall back to an older snapshot."""
    from atlas_ui import authority
    try:
        res = authority.resolve(Path(repo) / authority.REGISTER)
    except authority.AuthorityError as exc:
        raise CanonicalError(f"authority register: {exc}")
    spec = res.current_snapshot
    if spec is None:
        raise CanonicalError("no approved portfolio snapshot in the authority register")
    return load_snapshot(spec, repo)


def portfolio_as_of(on, repo: Path = REPO) -> Cycle0:
    """The approved snapshot in force on a date, for reconstructing a past analysis. Superseded snapshots stay loadable."""
    from atlas_ui import authority
    try:
        spec = authority.resolve(Path(repo) / authority.REGISTER).snapshot_as_of(on)
    except authority.AuthorityError as exc:
        raise CanonicalError(f"authority register: {exc}")
    if spec is None:
        raise CanonicalError(f"no approved portfolio snapshot was in force on {on}")
    return load_snapshot(spec, repo)


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
        snapshot_id=c0.portfolio_snapshot_id,
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
