"""Primary-source research adapter: SEC company facts -> point-in-time evidence in the EXISTING discovery ledger.

Reuses ``sec_adapter`` (fetch), ``identity_resolver`` (security key distinct from issuer key), ``xbrl_parser``
(canonical concepts and period selection) and ``operating_mvp.ledger`` (evidence ledger). It adds no data source, no
database, no forecast and no score. A fact enters the ledger only if an approved concept selects it for an explicit period;
anything missing or conflicting becomes an UNRESOLVED question — never an imputed value. Facts filed after ``decision_time``
are excluded (no look-ahead).
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from operating_mvp import ledger
from stock_atlas.freeze import freeze_payload
from xbrl_parser import XBRL_CONCEPT_MAPPINGS, PeriodIntentError, classify_period, select_canonical_fact_production

DURATION_FIELDS = ("revenue", "operating_income", "net_income", "diluted_eps", "cash_from_operations", "capex",
                   "dividends", "share_repurchases", "weighted_average_diluted_shares")
INSTANT_FIELDS = ("cash", "short_term_debt", "long_term_debt", "shareholders_equity")
LABEL = {"revenue": "Revenue", "operating_income": "Operating income", "net_income": "Net income", "diluted_eps": "Diluted EPS",
         "cash_from_operations": "Cash from operations", "capex": "Capital expenditures", "dividends": "Dividends paid",
         "share_repurchases": "Share repurchases", "weighted_average_diluted_shares": "Weighted diluted shares",
         "cash": "Cash", "short_term_debt": "Short-term debt", "long_term_debt": "Long-term debt", "shareholders_equity": "Shareholders' equity"}


class ResearchError(Exception):
    pass


def _filed(fact: dict) -> date | None:
    try:
        return date.fromisoformat(fact.get("filed") or "")
    except ValueError:
        return None


def annual_period_ends(facts: dict, decision_date: date, n: int = 3) -> list[str]:
    """Latest ``n`` fiscal-year ends that an ANNUAL 10-K revenue fact reported and that were filed by ``decision_date``."""
    ends: set[str] = set()
    root = (facts or {}).get("facts", {})
    for cid in XBRL_CONCEPT_MAPPINGS["revenue"]:
        tax, _, name = cid.partition(":")
        for flist in ((root.get(tax, {}).get(name) or {}).get("units") or {}).values():
            for f in flist if isinstance(flist, list) else []:
                fd = _filed(f)
                if f.get("val") is None or not str(f.get("form", "")).startswith("10-K") or fd is None or fd > decision_date:
                    continue
                if "ANNUAL" in {str(x) for x in classify_period(f)}:
                    ends.add(f["end"])
    return sorted(ends, reverse=True)[:n]


def _select(facts, field, end, decision_date):
    gran = "INSTANT" if field in INSTANT_FIELDS else "ANNUAL"
    try:
        r = select_canonical_fact_production(facts, field, period_granularity=gran, period_end=end)
    except PeriodIntentError as exc:  # fail closed: surfaced, not hidden
        return {"status": "UNAVAILABLE", "error": str(exc)}
    if r.get("status") == "SELECTED" and (_filed(r) is None or _filed(r) > decision_date):
        return {"status": "UNAVAILABLE", "error": f"fact first filed {r.get('filed')}, after the decision date {decision_date}"}
    return r


def _url(cik: str, accession: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"


def derive(periods: dict[str, dict]) -> dict:
    """Plain arithmetic on SELECTED facts only (labelled INFERENCE, inputs shown). Missing input -> the metric is omitted."""
    out = {}
    ends = sorted(periods, reverse=True)
    v = lambda e, f: (periods[e].get(f) or {}).get("value")
    for i, e in enumerate(ends):
        m = {}
        rev, oi, ni = v(e, "revenue"), v(e, "operating_income"), v(e, "net_income")
        cfo, cap = v(e, "cash_from_operations"), v(e, "capex")
        if rev and oi is not None:
            m["operating_margin"] = oi / rev
        if rev and ni is not None:
            m["net_margin"] = ni / rev
        if cfo is not None and cap is not None:
            m["free_cash_flow"] = cfo - abs(cap)
            if rev:
                m["fcf_margin"] = m["free_cash_flow"] / rev
            if ni:
                m["fcf_conversion_of_net_income"] = m["free_cash_flow"] / ni
        div, rep = v(e, "dividends"), v(e, "share_repurchases")
        if "free_cash_flow" in m and m["free_cash_flow"] > 0 and div is not None and rep is not None:
            m["shareholder_returns_over_fcf"] = (abs(div) + abs(rep)) / m["free_cash_flow"]
        c, ltd, std = v(e, "cash"), v(e, "long_term_debt"), v(e, "short_term_debt")
        if c is not None and ltd is not None and std is not None:  # never impute a missing leg as zero
            m["net_debt"] = ltd + std - c
        if i + 1 < len(ends):
            p = ends[i + 1]
            for f, k in (("revenue", "revenue_growth"), ("diluted_eps", "eps_growth"), ("weighted_average_diluted_shares", "diluted_share_change")):
                a, b = v(e, f), v(p, f)
                if a is not None and b:
                    m[k] = a / b - 1
        out[e] = m
    return out


def _share_scale(eps, shares, net_income):
    """SEC filers sometimes tag share counts in thousands/millions. Accept a scale only if EPS x shares reproduces net income
    within 5%; otherwise the share count is not trusted (None) and share-based ratios are omitted rather than guessed."""
    if not (eps and shares and net_income):
        return None
    for scale in (1, 1e3, 1e6):
        if abs(eps * shares * scale / net_income - 1) <= 0.05:
            return scale
    return None


def price_relative(price: float, latest: dict, metrics: dict) -> dict:
    """Arithmetic only; each ratio states its inputs and caveats. No return band, no target, no score."""
    out = {}
    eps = (latest.get("diluted_eps") or {}).get("value")
    sh = (latest.get("weighted_average_diluted_shares") or {}).get("value")
    ni = (latest.get("net_income") or {}).get("value")
    if eps and eps > 0:
        out["pe_on_latest_fy_diluted_eps"] = price / eps
        out["earnings_yield"] = eps / price
    fcf = metrics.get("free_cash_flow")
    scale = _share_scale(eps, sh, ni)
    if fcf is not None and sh and scale:
        out["fcf_yield_on_weighted_diluted_shares"] = (fcf / (sh * scale)) / price
        out["caveat_fcf_yield"] = ("uses weighted-average diluted shares" + (f" (filing tagged them in units of {scale:,.0f}; scale verified: EPS x shares ~ net income)" if scale != 1 else "")
                                   + ", not period-end shares; capex taken as an absolute outflow")
    elif fcf is not None:
        out["fcf_yield_status"] = "OMITTED — share count scale could not be verified against EPS x net income (or an input is missing/conflicted)"
    return out


def build_snapshot(facts: dict, *, ticker: str, security_key: str, cik: str, decision_time: datetime, n_years: int = 3) -> dict:
    d = decision_time.date()
    ends = annual_period_ends(facts, d, n_years)
    if not ends:
        raise ResearchError(f"no ANNUAL 10-K revenue fact filed by {d} for {ticker}; nothing can be established")
    periods: dict[str, dict] = {}
    gaps: list[str] = []
    for e in ends:
        row = {}
        for f in (*DURATION_FIELDS, *INSTANT_FIELDS):
            r = _select(facts, f, e, d)
            if r["status"] == "SELECTED":
                row[f] = {"value": r["normalized_value"], "unit": r["unit"], "concept": r["concept"], "form": r["form"], "accession": r["accession"],
                          "filed": r["filed"], "period_start": r.get("period_start"), "period_end": r["period_end"],
                          "granularity": r["period_granularity"], "source_url": _url(cik, r["accession"])}
            elif r["status"] == "CONFLICTED":
                row[f] = {"status": "CONFLICTED", "candidates": r.get("candidates")}
                gaps.append(f"{LABEL[f]} for fiscal period ending {e} is CONFLICTED between approved concepts; no value chosen")
            else:
                gaps.append(f"{LABEL[f]} for fiscal period ending {e} is UNVERIFIED: no approved SEC fact selected ({r.get('error') or 'unavailable'})")
        periods[e] = row
    metrics = derive({e: {f: x for f, x in row.items() if "value" in x} for e, row in periods.items()})
    return {"ticker": ticker, "security_key": security_key, "issuer_cik": cik, "decision_time": decision_time.isoformat(),
            "source": "SEC EDGAR company facts (data.sec.gov), approved XBRL concept families", "periods": periods,
            "derived_inference": metrics, "gaps": gaps, "units_note": "USD as reported; EPS in USD/share; shares as reported"}


def write_evidence(ledger_path: Path, candidate_id: str, snap: dict, today: date | None = None) -> dict:
    """SELECTED facts -> PRIMARY FACT evidence (known-at = filing date); gaps -> UNRESOLVED. Idempotent via a marker in the text."""
    today = today or date.today()
    c = ledger.replay(ledger_path)[candidate_id]
    have = " ".join(i["text"] for i in c["evidence"]) + " " + " ".join(u["question"] for u in c["unresolved"])
    added = skipped = 0
    for e in sorted(snap["periods"], reverse=True):
        for f, x in snap["periods"][e].items():
            if "value" not in x:
                continue
            marker = f"[SEC {x['accession']} {x['concept']} {x['period_start'] or ''}..{x['period_end']}]"
            if marker in have:
                skipped += 1
                continue
            unit = x["unit"]
            val = (f"${x['value'] / 1e9:,.2f}B" if unit == "USD" and abs(x["value"]) >= 1e8 else
                   f"{x['value']:,.2f} {unit}" if unit != "shares" else f"{x['value'] / 1e6:,.1f}M shares")
            ledger.add_evidence(ledger_path, candidate_id=candidate_id, tag="FACT", direction="NEUTRAL", grade="PRIMARY",
                                text=f"{LABEL[f]} FY ending {x['period_end']}: {val} ({x['form']}, {x['granularity']}, {x['unit']}) {marker}",
                                source_ref=x["source_url"], known_at=x["filed"], effective_date=today)
            added += 1
    gaps = 0
    for g in snap["gaps"]:
        if g not in have:
            ledger.add_unresolved(ledger_path, candidate_id=candidate_id, question=g, effective_date=today)
            gaps += 1
    return {"evidence_added": added, "evidence_already_present": skipped, "gaps_recorded": gaps}


def research_candidate(ledger_path: Path, candidate_id: str, out_dir: Path, *, decision_time: datetime | None = None,
                       adapter=None, facts: dict | None = None, price_evidence: dict | None = None) -> dict:
    """End to end for one candidate. ``facts`` / ``adapter`` are injectable so tests can run offline."""
    from identity_resolver import resolve_security
    from sec_adapter import SECAdapter
    cand = ledger.replay(ledger_path).get(candidate_id)
    if cand is None:
        raise ResearchError(f"unknown candidate {candidate_id!r}")
    ticker = (cand.get("ticker") or "").upper()
    if not ticker:
        raise ResearchError(f"{candidate_id} has no recorded ticker; security identity cannot be established")
    decision_time = decision_time or datetime.now(timezone.utc)
    adapter = adapter or SECAdapter()
    res = resolve_security(ticker, adapter)
    if not res.resolved or not res.security_key or not res.issuer_key:
        raise ResearchError(f"{ticker} did not resolve to a security/issuer identity; fail closed")
    cik = res.issuer_key.split(":")[-1]
    facts = facts if facts is not None else adapter.get_company_facts(cik)
    if not facts:
        raise ResearchError(f"SEC company facts unavailable for CIK {cik}; nothing recorded")
    if str(int(facts.get("cik", 0))) != str(int(cik)):
        raise ResearchError("SEC company facts CIK does not match the resolved issuer; fail closed")
    snap = build_snapshot(facts, ticker=ticker, security_key=res.security_key, cik=cik, decision_time=decision_time)
    latest_end = max(snap["periods"])
    if price_evidence:
        pb = price_evidence["price_binding"]
        if pb["security_key"] != res.security_key:
            raise ResearchError("price evidence security does not match the resolved security; refusing to combine")
        snap["price_evidence"] = price_evidence
        snap["price_relative_inference"] = price_relative(pb["price"], snap["periods"][latest_end], snap["derived_inference"][latest_end])
        snap["price_relative_inference"]["inputs"] = {"price": pb["price"], "price_session": pb["price_session_date"], "fy_end": latest_end}
    else:
        snap["price_relative_inference"] = {"status": "BLOCKED — no bound price evidence supplied; no price-relative ratio computed"}
    out_dir = Path(out_dir)
    ref = freeze_payload(snap, version="research-snapshot-v1", destination=out_dir / f"{ticker}-{decision_time:%Y%m%dT%H%M%S%fZ}.json")
    rec = write_evidence(ledger_path, candidate_id, snap, decision_time.date())
    entry = {"candidate_id": candidate_id, "ticker": ticker, "security_key": res.security_key, "latest_fy_end": latest_end,
             "snapshot": {"sha256": ref.sha256, "artifact_path": ref.artifact_path}, "recorded_at": decision_time.isoformat(), **rec}
    with open(out_dir / "research_index.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def latest_snapshot(out_dir: Path, candidate_id: str) -> dict | None:
    """Newest retained snapshot for a candidate, only if its file still matches its recorded SHA-256."""
    import hashlib
    idx = Path(out_dir) / "research_index.jsonl"
    if not idx.exists():
        return None
    rows = [json.loads(l) for l in idx.read_text().splitlines() if l.strip() and json.loads(l)["candidate_id"] == candidate_id]
    for row in reversed(rows):
        p = Path(row["snapshot"]["artifact_path"])
        if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == row["snapshot"]["sha256"]:
            return {**row, "data": json.loads(p.read_text())}
    return None
