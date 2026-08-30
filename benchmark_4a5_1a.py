"""
=============================================================================
Phase 4A.5.1A — Identity & Period Closure
=============================================================================

Closes the three architectural gaps from Phase 4A.5.1 that could make Atlas
select the wrong financial period, confuse issuer identity with security
identity, or route a security through the wrong filing regime.

Proves, against live SEC data:

  1. PERIOD GRANULARITY
     select_canonical_fact(period_granularity="QUARTER") never returns a
     year-to-date duration, and "YEAR_TO_DATE" never returns the quarter.
     Checked on MSFT, AAPL, Realty Income (O), Berkshire (BRK.B).

  2. ISSUER vs SECURITY IDENTITY
     identity_resolver.resolve_security keeps issuer (CIK) and security
     (ticker / share class) distinct. BRK.A != BRK.B, same issuer, no
     share-class collapse.

  3. ENTITY ARCHETYPE / FILING REGIME
     entity_classification routes all six Phase 4A.5.1 controls with no
     benchmark-specific if/else. SPY -> investment-company regime.

Does NOT touch the frozen baseline commit d37f654, does NOT expand XBRL
mappings, does NOT resolve any carried-forward mapping candidate.

Artifacts: live_validation_results/<UTC-timestamp>_phase4a5_1a.{json,md}
=============================================================================
"""

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from sec_adapter import SECAdapter
from entity_classification import classify_entity, filing_regime_for, discover_filing_regime
from identity_resolver import resolve_security, same_issuer, distinct_securities
from xbrl_parser import select_canonical_fact, duration_granularity, PeriodGranularity

load_dotenv()

# Phase 4A.5.1 control universe (same six securities).
UNIVERSE = ["MSFT", "AAPL", "JPM", "O", "BRK.B", "SPY"]

EXPECTED_ARCHETYPE = {
    "MSFT": "OPERATING_COMPANY",
    "AAPL": "OPERATING_COMPANY",
    "JPM": "FINANCIAL_BANK",
    "O": "REIT",
    "BRK.B": "INSURANCE",
    "SPY": "INVESTMENT_COMPANY_ETF",
}

# Live observed quarter vs YTD revenue for the latest 10-Q (Phase 4A.5.1 data,
# re-verified each run — these are expectations for the report, not inputs).
PERIOD_CASES = ["MSFT", "AAPL", "O", "BRK.B"]


# ---------------------------------------------------------------------------
# 1. period granularity
# ---------------------------------------------------------------------------
def _revenue_duration_facts(company_facts, accn, end):
    from xbrl_parser import XBRL_CONCEPT_MAPPINGS
    ug = (company_facts or {}).get("facts", {}).get("us-gaap", {})
    fam = [c.split(":", 1)[-1] for c in XBRL_CONCEPT_MAPPINGS["revenue"]]
    rows = []
    for concept in fam:
        cd = ug.get(concept)
        if not cd:
            continue
        for unit, flist in cd.get("units", {}).items():
            for f in flist:
                if f.get("accn") != accn or f.get("end") != end or not f.get("start"):
                    continue
                rows.append({
                    "concept": f"us-gaap:{concept}", "unit": unit,
                    "start": f["start"], "end": f["end"],
                    "days": (datetime.fromisoformat(f["end"]) - datetime.fromisoformat(f["start"])).days,
                    "granularity": duration_granularity(f["start"], f["end"]),
                    "fp": f.get("fp"), "frame": f.get("frame"), "value": f.get("val"),
                })
    rows.sort(key=lambda r: (r["start"], r["concept"]))
    return rows


def period_granularity_case(symbol, adapter):
    rec = {"symbol": symbol, "ok": False, "notes": []}
    res = resolve_security(symbol, adapter)
    if not res.resolved:
        rec["notes"].append("identity not resolved")
        return rec
    tq = adapter.get_recent_filings(res.cik, "10-Q", 1)
    if not tq:
        rec["notes"].append("no 10-Q")
        return rec
    q = tq[0]
    accn, end = q["accessionNumber"], q["reportDate"]
    cf = adapter.get_company_facts(res.cik)
    facts = _revenue_duration_facts(cf, accn, end)

    quarter = select_canonical_fact(cf, "revenue", accession=accn, period_end=end,
                                    period_granularity=PeriodGranularity.QUARTER)
    ytd = select_canonical_fact(cf, "revenue", accession=accn, period_end=end,
                                period_granularity=PeriodGranularity.YEAR_TO_DATE)
    legacy = select_canonical_fact(cf, "revenue", accession=accn, period_end=end,
                                   period_type="duration")

    def _brief(sel):
        return {
            "status": sel.get("status"),
            "concept": sel.get("concept"),
            "value": sel.get("raw_value"),
            "period": f"{sel.get('period_start')}..{sel.get('period_end')}",
            "granularity": sel.get("period_granularity"),
            "conflict": sel.get("conflict"),
        }

    q_b, y_b, l_b = _brief(quarter), _brief(ytd), _brief(legacy)

    # PASS conditions:
    #  - a QUARTER fact exists and classifies QUARTER (days <= ~quarter)
    #  - a YEAR_TO_DATE fact exists and classifies YTD
    #  - the two selections are different periods (quarter is NOT the YTD span)
    q_is_quarter = quarter.get("status") in ("SELECTED", "CONFLICTED") and quarter.get("period_granularity") == "QUARTER"
    y_is_ytd = ytd.get("status") in ("SELECTED", "CONFLICTED") and ytd.get("period_granularity") == "YEAR_TO_DATE"
    distinct_period = quarter.get("period_start") != ytd.get("period_start")
    quarter_not_ytd_value = (
        quarter.get("status") == "CONFLICTED"  # Berkshire: value itself is a carried-forward conflict
        or ytd.get("status") == "CONFLICTED"
        or quarter.get("raw_value") != ytd.get("raw_value")
    )

    rec["ok"] = bool(q_is_quarter and y_is_ytd and distinct_period and quarter_not_ytd_value)
    rec.update({
        "quarter_10q_accession": accn,
        "quarter_10q_period_end": end,
        "revenue_duration_facts": facts,
        "quarter_selection": q_b,
        "ytd_selection": y_b,
        "legacy_period_end_only_selection": l_b,
        "legacy_would_have_returned_ytd": (l_b["granularity"] == "YEAR_TO_DATE"),
        "checks": {
            "quarter_request_returns_quarter": q_is_quarter,
            "ytd_request_returns_ytd": y_is_ytd,
            "quarter_and_ytd_are_distinct_periods": distinct_period,
            "quarter_value_is_not_the_ytd_value": quarter_not_ytd_value,
        },
    })
    if quarter.get("status") == "CONFLICTED":
        rec["notes"].append("quarter revenue is CONFLICTED across approved concepts "
                            "(carried-forward Berkshire revenue conflict — not resolved here)")
    return rec


# ---------------------------------------------------------------------------
# 2. issuer vs security identity
# ---------------------------------------------------------------------------
def identity_case(adapter):
    a = resolve_security("BRK.A", adapter)
    b = resolve_security("BRK.B", adapter)
    checks = {
        "both_resolved": a.resolved and b.resolved,
        "brk_a_ne_brk_b_security_key": distinct_securities(a, b),
        "brk_a_ne_brk_b_ticker": a.sec_ticker != b.sec_ticker,
        "brk_a_ne_brk_b_share_class": a.share_class != b.share_class and bool(a.share_class) and bool(b.share_class),
        "same_issuer_cik": a.cik == b.cik,
        "same_issuer_key": same_issuer(a, b),
        "share_class_not_collapsed": a.share_class == "A" and b.share_class == "B",
        "both_list_each_other_as_siblings": (
            {s["sec_ticker"] for s in a.sibling_securities} == {"BRK-A", "BRK-B"}
            and {s["sec_ticker"] for s in b.sibling_securities} == {"BRK-A", "BRK-B"}
        ),
        "market_data_adapter_gets_exact_ticker": a.sec_ticker == "BRK-A" and b.sec_ticker == "BRK-B",
    }
    # control: a single-class issuer has no share class and one sibling
    msft = resolve_security("MSFT", adapter)
    checks["single_class_issuer_has_no_share_class"] = msft.resolved and msft.share_class is None
    return {
        "ok": all(checks.values()),
        "brk_a": a.to_dict(),
        "brk_b": b.to_dict(),
        "msft_control": {"share_class": msft.share_class, "security_type": msft.security_type,
                         "issuer_tickers": msft.issuer_tickers},
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# 3. entity archetype / filing regime routing
# ---------------------------------------------------------------------------
def routing_case(symbol, adapter):
    res = resolve_security(symbol, adapter)
    rec = {
        "symbol": symbol,
        "cik": res.cik,
        "issuer_name": res.issuer_name,
        "entity_type": res.entity_type,
        "sic": res.sic,
        "archetype": res.entity_archetype,
        "archetype_reason": res.archetype_reason,
        "filing_regime": res.filing_regime,
        "expected_archetype": EXPECTED_ARCHETYPE.get(symbol),
    }
    if res.resolved and res.cik:
        reg = discover_filing_regime(classify_entity(adapter.get_company_submissions(res.cik))[0], adapter, res.cik)
        pf = reg.get("primary_filing") or {}
        rec["regime_primary_form"] = pf.get("form")
        rec["regime_primary_accession"] = pf.get("accessionNumber")
        rec["annual_forms"] = reg.get("annual_forms")
    rec["ok"] = (
        res.entity_archetype == EXPECTED_ARCHETYPE.get(symbol)
        and res.filing_regime in ("SEC_CORPORATE", "SEC_INVESTMENT_COMPANY")
    )
    if symbol == "SPY":
        rec["ok"] = rec["ok"] and res.filing_regime == "SEC_INVESTMENT_COMPANY" and rec.get("regime_primary_form") in (
            "N-CEN", "N-CSR", "24F-2NT", "485BPOS")
    return rec


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def run():
    adapter = SECAdapter()
    errors = []

    routing = []
    for sym in UNIVERSE:
        try:
            routing.append(routing_case(sym, adapter))
        except Exception as e:
            errors.append(f"routing {sym}: {e!r}")
            routing.append({"symbol": sym, "ok": False, "error": traceback.format_exc()})

    try:
        identity = identity_case(adapter)
    except Exception as e:
        errors.append(f"identity: {e!r}")
        identity = {"ok": False, "error": traceback.format_exc()}

    period = []
    for sym in PERIOD_CASES:
        try:
            period.append(period_granularity_case(sym, adapter))
        except Exception as e:
            errors.append(f"period {sym}: {e!r}")
            period.append({"symbol": sym, "ok": False, "error": traceback.format_exc()})

    routing_ok = all(r.get("ok") for r in routing)
    identity_ok = bool(identity.get("ok"))
    period_ok = all(p.get("ok") for p in period)
    no_errors = not errors

    verdict = (
        "PHASE 4A.5.1A PASS — READY FOR MARKET DATA BENCHMARK"
        if (routing_ok and identity_ok and period_ok and no_errors)
        else "PHASE 4A.5.1A BLOCKED — ARCHITECTURAL ISSUE REMAINS"
    )

    summary = {
        "phase": "4A.5.1A",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_baseline": "d37f654 (untouched)",
        "start_commit": "24955be",
        "errors": errors,
        "routing": routing,
        "identity": identity,
        "period_granularity": period,
        "checks": {
            "entity_archetype_routing_all_six": routing_ok,
            "issuer_vs_security_identity": identity_ok,
            "period_granularity_quarter_never_ytd": period_ok,
            "no_unhandled_errors": no_errors,
        },
        "verdict": verdict,
    }
    art = write_artifacts(summary)
    summary["artifacts"] = art

    print("\n" + "=" * 70)
    print("PHASE 4A.5.1A — IDENTITY & PERIOD CLOSURE")
    print("=" * 70)
    print("\n[1] ENTITY / ARCHETYPE ROUTING")
    for r in routing:
        print(f"  {r['symbol']:6s} {str(r.get('archetype')):24s} regime={r.get('filing_regime'):24s} "
              f"expected={r.get('expected_archetype'):24s} {'OK' if r.get('ok') else 'FAIL'}")
    print("\n[2] ISSUER vs SECURITY IDENTITY (BRK.A / BRK.B)")
    for k, v in identity.get("checks", {}).items():
        print(f"  {'OK ' if v else 'FAIL'} {k}")
    print("\n[3] PERIOD GRANULARITY (latest 10-Q: QUARTER vs YEAR_TO_DATE)")
    for p in period:
        q = p.get("quarter_selection", {})
        y = p.get("ytd_selection", {})
        print(f"  {p['symbol']:6s} quarter={q.get('value')} ({q.get('period')}) "
              f"ytd={y.get('value')} ({y.get('period')})  {'OK' if p.get('ok') else 'FAIL'}")
        for n in p.get("notes", []):
            print(f"         ! {n}")
    print(f"\nArtifacts:\n  JSON: {art['json']}\n  MD:   {art['md']}")
    print(f"\nVERDICT: {verdict}")
    return summary


def write_artifacts(summary, results_dir="live_validation_results"):
    d = Path(results_dir)
    d.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jp = d / f"{ts}_phase4a5_1a.json"
    mp = d / f"{ts}_phase4a5_1a.md"
    jp.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))

    L = ["# Phase 4A.5.1A — Identity & Period Closure", "",
         f"- Generated (UTC): {summary['generated_utc']}",
         f"- Start commit: {summary['start_commit']} · frozen baseline {summary['frozen_baseline']}",
         f"- Verdict: **{summary['verdict']}**", ""]

    L += ["## 1. Entity / archetype routing (all six controls)", "",
          "| symbol | CIK | entityType | SIC | archetype | expected | filing regime | primary form | result |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in summary["routing"]:
        L.append(f"| {r['symbol']} | {r.get('cik')} | {r.get('entity_type')} | {r.get('sic')} | "
                 f"{r.get('archetype')} | {r.get('expected_archetype')} | {r.get('filing_regime')} | "
                 f"{r.get('regime_primary_form')} | {'PASS' if r.get('ok') else 'FAIL'} |")
    L.append("")

    L += ["## 2. Issuer vs security identity — BRK.A / BRK.B", ""]
    idc = summary["identity"]
    a, b = idc.get("brk_a", {}), idc.get("brk_b", {})
    L += [f"- BRK.A: ticker `{a.get('sec_ticker')}` · share_class `{a.get('share_class')}` · "
          f"security_key `{a.get('security_key')}` · type {a.get('security_type')}",
          f"- BRK.B: ticker `{b.get('sec_ticker')}` · share_class `{b.get('share_class')}` · "
          f"security_key `{b.get('security_key')}` · type {b.get('security_type')}",
          f"- shared issuer_key: `{a.get('issuer_key')}` (CIK {a.get('cik')})",
          f"- MSFT control (single class): share_class={idc.get('msft_control', {}).get('share_class')}, "
          f"issuer_tickers={idc.get('msft_control', {}).get('issuer_tickers')}", ""]
    L += ["| check | result |", "|---|---|"]
    for k, v in idc.get("checks", {}).items():
        L.append(f"| {k} | {'PASS' if v else 'FAIL'} |")
    L.append("")

    L += ["## 3. Period granularity — QUARTER must never return YTD", ""]
    for p in summary["period_granularity"]:
        L += [f"### {p['symbol']} — latest 10-Q {p.get('quarter_10q_accession')} "
              f"(period end {p.get('quarter_10q_period_end')})",
              "",
              f"- QUARTER request -> {p.get('quarter_selection', {}).get('status')} "
              f"{p.get('quarter_selection', {}).get('value')} "
              f"({p.get('quarter_selection', {}).get('period')}, "
              f"{p.get('quarter_selection', {}).get('granularity')})",
              f"- YEAR_TO_DATE request -> {p.get('ytd_selection', {}).get('status')} "
              f"{p.get('ytd_selection', {}).get('value')} "
              f"({p.get('ytd_selection', {}).get('period')}, "
              f"{p.get('ytd_selection', {}).get('granularity')})",
              f"- legacy (period_end only) would have returned -> "
              f"{p.get('legacy_period_end_only_selection', {}).get('value')} "
              f"({p.get('legacy_period_end_only_selection', {}).get('granularity')})",
              f"- result: **{'PASS' if p.get('ok') else 'FAIL'}**", ""]
        L += ["| concept | period | days | granularity | fp | frame | value |",
              "|---|---|---|---|---|---|---|"]
        for f in p.get("revenue_duration_facts", []):
            L.append(f"| {f['concept']} | {f['start']}..{f['end']} | {f['days']} | {f['granularity']} | "
                     f"{f['fp']} | {f['frame']} | {f['value']} |")
        L.append("")
        for n in p.get("notes", []):
            L.append(f"> note: {n}")
        L.append("")

    if summary["errors"]:
        L += ["## Errors", ""] + [f"- {e}" for e in summary["errors"]] + [""]

    mp.write_text("\n".join(L))
    return {"json": str(jp), "md": str(mp)}


if __name__ == "__main__":
    s = run()
    raise SystemExit(0 if s["verdict"].endswith("READY FOR MARKET DATA BENCHMARK") else 1)
