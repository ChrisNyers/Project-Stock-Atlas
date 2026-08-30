"""
Issuer vs. security identity resolution.

Phase 4A.5.1A: a CIK identifies an ISSUER, not a security. Berkshire Hathaway
(CIK 1067983) has two listed common-share classes — BRK-A and BRK-B — that must
stay distinct securities while sharing one issuer. This module resolves a ticker
into a structured identity that keeps the two levels separate:

    issuer   -> CIK, name, entity archetype, filing regime
    security -> exact SEC ticker, share class, security_key

It is a *resolver*, not a Security Master redesign: it produces identity records
(dataclasses / dicts). Persisting them via SecurityIdentityORM is the caller's
choice — `to_orm_kwargs()` maps the fields straight onto the existing columns
without collapsing the share class.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional

from sec_adapter import SECAdapter
from entity_classification import classify_entity, filing_regime_for


ISSUER_KEY_PREFIX = "SEC-CIK"


def share_class_from_ticker(sec_ticker: Optional[str]) -> Optional[str]:
    """Derive a share-class / series label from an SEC ticker.

    SEC writes share classes and preferred series with a hyphen: "BRK-A" -> "A",
    "BRK-B" -> "B", "JPM-PC" -> "PC". A plain ticker ("MSFT") has no suffix and
    represents the issuer's single common line -> None.
    """
    if not sec_ticker or "-" not in sec_ticker:
        return None
    suffix = sec_ticker.split("-", 1)[1].strip().upper()
    return suffix or None


def _security_key(cik: Optional[str], sec_ticker: Optional[str]) -> Optional[str]:
    if not cik or not sec_ticker:
        return None
    return f"{ISSUER_KEY_PREFIX}:{cik}:{sec_ticker.upper()}"


def _issuer_key(cik: Optional[str]) -> Optional[str]:
    return f"{ISSUER_KEY_PREFIX}:{cik}" if cik else None


def _security_type(archetype: str, share_class: Optional[str]) -> str:
    if archetype == "INVESTMENT_COMPANY_ETF":
        return "FUND_OR_ETF"
    if share_class and len(share_class) == 1:
        return f"COMMON_STOCK_CLASS_{share_class}"
    if share_class:
        return f"PREFERRED_SERIES_{share_class}"
    return "COMMON_STOCK"


@dataclass
class ResolvedSecurity:
    query_ticker: str
    resolved: bool = False

    # security level
    sec_ticker: Optional[str] = None
    security_key: Optional[str] = None
    share_class: Optional[str] = None
    security_type: Optional[str] = None

    # issuer level
    cik: Optional[str] = None
    issuer_key: Optional[str] = None
    issuer_name: Optional[str] = None
    entity_type: Optional[str] = None
    sic: Optional[str] = None
    sic_description: Optional[str] = None
    fiscal_year_end: Optional[str] = None
    entity_archetype: Optional[str] = None
    archetype_reason: Optional[str] = None
    filing_regime: Optional[str] = None

    # sibling securities on the same issuer CIK
    issuer_tickers: List[str] = field(default_factory=list)
    sibling_securities: List[dict] = field(default_factory=list)
    exchanges: List[str] = field(default_factory=list)

    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_orm_kwargs(self) -> dict:
        """Kwargs for SecurityIdentityORM(**kwargs) — issuer and security stay
        distinct: issuer_id is the CIK-scoped issuer key, security_id is the
        ticker-scoped security key, and share_class is preserved."""
        return {
            "security_id": self.security_key,
            "issuer_id": self.issuer_key,
            "company_name": self.issuer_name,
            "ticker": self.sec_ticker,
            "exchange": (self.exchanges or [None])[0],
            "security_type": self.security_type,
            "share_class": self.share_class,
            "cik": self.cik,
            "fiscal_year_end": self.fiscal_year_end,
        }


def resolve_security(ticker: str, adapter: Optional[SECAdapter] = None) -> ResolvedSecurity:
    """Resolve a ticker into a two-level (issuer / security) identity."""
    adapter = adapter or SECAdapter()
    out = ResolvedSecurity(query_ticker=ticker)

    row = adapter.resolve_ticker(ticker)
    if not row:
        out.notes.append("ticker not found in SEC company_tickers.json")
        return out

    out.sec_ticker = row["sec_ticker"]
    out.cik = row["cik"]
    out.issuer_key = _issuer_key(out.cik)
    out.security_key = _security_key(out.cik, out.sec_ticker)
    out.share_class = share_class_from_ticker(out.sec_ticker)

    subs = adapter.get_company_submissions(out.cik)
    if not subs:
        out.notes.append("submissions unavailable; issuer/security keys still resolved")
        out.security_type = _security_type("", out.share_class)
        out.resolved = True
        return out

    out.issuer_name = subs.get("name")
    out.entity_type = subs.get("entityType")
    out.sic = str(subs.get("sic") or "") or None
    out.sic_description = subs.get("sicDescription")
    out.fiscal_year_end = subs.get("fiscalYearEnd")
    out.exchanges = subs.get("exchanges", []) or []

    archetype, reason = classify_entity(subs)
    out.entity_archetype = archetype.value
    out.archetype_reason = reason
    out.filing_regime = filing_regime_for(archetype).value
    out.security_type = _security_type(archetype.value, out.share_class)

    # sibling securities: every ticker row that maps to this issuer CIK
    sib_rows = adapter.tickers_for_cik(out.cik)
    out.issuer_tickers = sorted({r["sec_ticker"] for r in sib_rows if r.get("sec_ticker")})
    if not out.issuer_tickers and subs.get("tickers"):
        out.issuer_tickers = sorted(set(subs["tickers"]))
    for st in out.issuer_tickers:
        out.sibling_securities.append({
            "sec_ticker": st,
            "share_class": share_class_from_ticker(st),
            "security_key": _security_key(out.cik, st),
            "is_query": st.upper() == (out.sec_ticker or "").upper(),
        })

    out.resolved = True
    return out


def same_issuer(a: ResolvedSecurity, b: ResolvedSecurity) -> bool:
    return bool(a.issuer_key and a.issuer_key == b.issuer_key)


def distinct_securities(a: ResolvedSecurity, b: ResolvedSecurity) -> bool:
    return bool(a.security_key and b.security_key and a.security_key != b.security_key)
