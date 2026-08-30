"""
=============================================================================
Phase 4A.5.1B — Production Period Contract Closure
=============================================================================

Minimal Red Team correction (Grok Red Team Round 3). Proves:

  1. The PRODUCTION selection boundary (select_canonical_fact_production) forces
     explicit period intent and fails closed — no silent earliest-start / YTD.
  2. classify_period() fails closed on stub / transition durations even when the
     length is under a broad upper bound.
  3. Explicit standard QUARTER / YEAR_TO_DATE still select the correct live
     periods for MSFT, AAPL, Realty Income (O), Berkshire (BRK.B).
  4. The market-data identity join contract: price observations bind to
     security_key, not issuer CIK; BRK.A and BRK.B get distinct series.

Does NOT touch frozen d37f654 or the frozen v3 harness. Does NOT expand XBRL
mappings or resolve any carried-forward mapping candidate.

Artifacts: live_validation_results/<UTC-timestamp>_phase4a5_1b.{json,md}
=============================================================================
"""

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from sec_adapter import SECAdapter
from identity_resolver import (
    resolve_security, market_price_join_key, assert_distinct_price_series,
    IdentityJoinError,
)
from xbrl_parser import (
    select_canonical_fact_production, classify_period, PeriodIntentError,
    PeriodGranularity,
)

load_dotenv()

PERIOD_CASES = ["MSFT", "AAPL", "O", "BRK.B"]


# ---------------------------------------------------------------------------
# 1 + 2. production boundary + fail-closed classification (synthetic, deterministic)
# ---------------------------------------------------------------------------
def fail_closed_checks():
    cf_qy = {"facts": {"us-gaap": {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
        {"val": 241832000000, "start": "2025-07-01", "end": "2026-03-31", "accn": "Q", "fp": "Q3", "form": "10-Q"},
        {"val": 82886000000, "start": "2026-01-01", "end": "2026-03-31", "accn": "Q", "fp": "Q3", "form": "10-Q"},
    ]}}}}}
    stub_q1 = {"val": 999, "start": "2026-01-01", "end": "2026-05-27", "accn": "S", "fp": "Q1", "form": "10-Q"}
    stub_nofp = {"val": 1, "start": "2026-01-01", "end": "2026-08-04", "accn": "S", "form": "10-Q"}
    fy_quarter = {"val": 7, "start": "2026-01-01", "end": "2026-03-31", "accn": "K", "fp": "FY"}

    checks = {}

    # omitted intent -> TypeError (required kwarg)
    try:
        select_canonical_fact_production(cf_qy, "revenue", accession="Q", period_end="2026-03-31")
        checks["omitted_intent_rejected"] = False
    except TypeError:
        checks["omitted_intent_rejected"] = True

    # explicit None -> PeriodIntentError
    try:
        select_canonical_fact_production(cf_qy, "revenue", period_granularity=None,
                                         accession="Q", period_end="2026-03-31")
        checks["none_intent_rejected"] = False
    except PeriodIntentError:
        checks["none_intent_rejected"] = True

    # instant field requested as QUARTER -> PeriodIntentError
    try:
        select_canonical_fact_production({"facts": {}}, "cash", period_granularity="QUARTER")
        checks["instant_field_wrong_intent_rejected"] = False
    except PeriodIntentError:
        checks["instant_field_wrong_intent_rejected"] = True

    checks["stub_q1_146d_classifies_empty"] = classify_period(stub_q1) == set()
    checks["stub_nofp_215d_classifies_empty"] = classify_period(stub_nofp) == set()
    checks["fy_tag_with_quarter_duration_classifies_empty"] = classify_period(fy_quarter) == set()

    sel_stub = select_canonical_fact_production(
        {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [stub_q1]}}}}},
        "revenue", period_granularity="YEAR_TO_DATE", accession="S", period_end="2026-05-27")
    checks["stub_not_selected_via_production_boundary"] = sel_stub["status"] == "UNAVAILABLE"

    return {"ok": all(checks.values()), "checks": checks}


# ---------------------------------------------------------------------------
# 3. explicit standard QUARTER / YTD live
# ---------------------------------------------------------------------------
def period_case(symbol, adapter):
    rec = {"symbol": symbol, "ok": False, "notes": []}
    res = resolve_security(symbol, adapter)
    tq = adapter.get_recent_filings(res.cik, "10-Q", 1) if res.cik else []
    if not tq:
        rec["notes"].append("no 10-Q")
        return rec
    accn, end = tq[0]["accessionNumber"], tq[0]["reportDate"]
    cf = adapter.get_company_facts(res.cik)

    q = select_canonical_fact_production(cf, "revenue", period_granularity=PeriodGranularity.QUARTER,
                                         accession=accn, period_end=end)
    y = select_canonical_fact_production(cf, "revenue", period_granularity=PeriodGranularity.YEAR_TO_DATE,
                                         accession=accn, period_end=end)

    def brief(s):
        return {"status": s.get("status"), "concept": s.get("concept"), "value": s.get("raw_value"),
                "period": f"{s.get('period_start')}..{s.get('period_end')}",
                "classification": s.get("period_classification"),
                "boundary": s.get("selection_boundary")}

    qb, yb = brief(q), brief(y)
    q_is_quarter = q.get("status") in ("SELECTED", "CONFLICTED") and "QUARTER" in (q.get("period_classification") or [])
    y_is_ytd = y.get("status") in ("SELECTED", "CONFLICTED") and "YEAR_TO_DATE" in (y.get("period_classification") or [])
    distinct = q.get("period_start") != y.get("period_start")
    not_same_value = (q.get("status") == "CONFLICTED" or y.get("status") == "CONFLICTED"
                      or q.get("raw_value") != y.get("raw_value"))
    rec["ok"] = bool(q_is_quarter and y_is_ytd and distinct and not_same_value)
    rec.update({
        "quarter_10q_accession": accn, "quarter_10q_period_end": end,
        "quarter_selection": qb, "ytd_selection": yb,
        "checks": {
            "quarter_confidently_classified_quarter": q_is_quarter,
            "ytd_confidently_classified_ytd": y_is_ytd,
            "quarter_and_ytd_distinct_periods": distinct,
            "quarter_value_not_ytd_value": not_same_value,
        },
    })
    if q.get("status") == "CONFLICTED":
        rec["notes"].append("quarter revenue CONFLICTED (carried-forward Berkshire conflict, not resolved here)")
    return rec


# ---------------------------------------------------------------------------
# 4. market-data identity join contract
# ---------------------------------------------------------------------------
def identity_join_case(adapter):
    a = resolve_security("BRK.A", adapter)
    b = resolve_security("BRK.B", adapter)
    rep = assert_distinct_price_series("BRK.A", "BRK.B", adapter=adapter)
    checks = {
        "join_key_is_security_key_not_cik": (
            market_price_join_key("BRK.B", adapter) == b.security_key
            and market_price_join_key("BRK.B", adapter) != b.cik
        ),
        "dotted_and_hyphen_ticker_same_key": (
            market_price_join_key("BRK.A", adapter) == market_price_join_key("BRK-A", adapter)
        ),
        "brk_a_brk_b_distinct_security_keys": rep["distinct_security_keys"],
        "brk_a_brk_b_share_one_issuer": rep["shares_issuer"],
        "share_classes_preserved": rep["share_classes"] == {"BRK.A": "A", "BRK.B": "B"},
        "unresolvable_ticker_fails_closed": _fails_closed("NOT_A_REAL_TICKER_XYZ", adapter),
    }
    return {
        "ok": all(checks.values()),
        "security_keys": rep["security_keys"],
        "issuer_keys": rep["issuer_keys"],
        "checks": checks,
    }


def _fails_closed(ticker, adapter):
    try:
        market_price_join_key(ticker, adapter)
        return False
    except IdentityJoinError:
        return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def run():
    adapter = SECAdapter()
    errors = []

    try:
        fc = fail_closed_checks()
    except Exception as e:
        errors.append(f"fail_closed: {e!r}")
        fc = {"ok": False, "error": traceback.format_exc()}

    periods = []
    for sym in PERIOD_CASES:
        try:
            periods.append(period_case(sym, adapter))
        except Exception as e:
            errors.append(f"period {sym}: {e!r}")
            periods.append({"symbol": sym, "ok": False, "error": traceback.format_exc()})

    try:
        idjoin = identity_join_case(adapter)
    except Exception as e:
        errors.append(f"identity_join: {e!r}")
        idjoin = {"ok": False, "error": traceback.format_exc()}

    ok = fc.get("ok") and all(p.get("ok") for p in periods) and idjoin.get("ok") and not errors
    verdict = ("PHASE 4A.5.1B PASS — READY FOR PHASE 4A.5.2 MARKET DATA BENCHMARK"
               if ok else "PHASE 4A.5.1B BLOCKED — MATERIAL ISSUE REMAINS")

    summary = {
        "phase": "4A.5.1B",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_baseline": "d37f654 (untouched)",
        "start_commit": "bc2b3c5",
        "errors": errors,
        "production_fail_closed": fc,
        "explicit_period_cases": periods,
        "market_data_identity_join": idjoin,
        "verdict": verdict,
    }
    art = write_artifacts(summary)
    summary["artifacts"] = art

    print("\n" + "=" * 70)
    print("PHASE 4A.5.1B — PRODUCTION PERIOD CONTRACT CLOSURE")
    print("=" * 70)
    print("\n[1+2] PRODUCTION BOUNDARY + FAIL-CLOSED CLASSIFICATION")
    for k, v in fc.get("checks", {}).items():
        print(f"  {'OK ' if v else 'FAIL'} {k}")
    print("\n[3] EXPLICIT STANDARD QUARTER / YTD (live, via production boundary)")
    for p in periods:
        q = p.get("quarter_selection", {})
        y = p.get("ytd_selection", {})
        print(f"  {p['symbol']:6s} quarter={q.get('value')} ({q.get('period')}) "
              f"ytd={y.get('value')} ({y.get('period')})  {'OK' if p.get('ok') else 'FAIL'}")
        for n in p.get("notes", []):
            print(f"         ! {n}")
    print("\n[4] MARKET-DATA IDENTITY JOIN CONTRACT")
    for k, v in idjoin.get("checks", {}).items():
        print(f"  {'OK ' if v else 'FAIL'} {k}")
    print(f"  BRK.A -> {idjoin.get('security_keys', {}).get('BRK.A')}")
    print(f"  BRK.B -> {idjoin.get('security_keys', {}).get('BRK.B')}")
    print(f"\nArtifacts:\n  JSON: {art['json']}\n  MD:   {art['md']}")
    print(f"\nVERDICT: {verdict}")
    return summary


def write_artifacts(summary, results_dir="live_validation_results"):
    d = Path(results_dir)
    d.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jp = d / f"{ts}_phase4a5_1b.json"
    mp = d / f"{ts}_phase4a5_1b.md"
    jp.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))

    L = ["# Phase 4A.5.1B — Production Period Contract Closure", "",
         f"- Generated (UTC): {summary['generated_utc']}",
         f"- Start commit: {summary['start_commit']} · frozen baseline {summary['frozen_baseline']}",
         f"- Verdict: **{summary['verdict']}**", ""]

    L += ["## 1+2. Production boundary + fail-closed classification", "",
          "| check | result |", "|---|---|"]
    for k, v in summary["production_fail_closed"].get("checks", {}).items():
        L.append(f"| {k} | {'PASS' if v else 'FAIL'} |")
    L.append("")

    L += ["## 3. Explicit standard QUARTER / YTD (live)", "",
          "| symbol | 10-Q | period end | QUARTER | YTD | result |", "|---|---|---|---|---|---|"]
    for p in summary["explicit_period_cases"]:
        q = p.get("quarter_selection", {})
        y = p.get("ytd_selection", {})
        L.append(f"| {p['symbol']} | {p.get('quarter_10q_accession')} | {p.get('quarter_10q_period_end')} | "
                 f"{q.get('status')} {q.get('value')} ({q.get('period')}) | "
                 f"{y.get('status')} {y.get('value')} ({y.get('period')}) | "
                 f"{'PASS' if p.get('ok') else 'FAIL'} |")
    L.append("")
    for p in summary["explicit_period_cases"]:
        for n in p.get("notes", []):
            L.append(f"> {p['symbol']}: {n}")
    L.append("")

    L += ["## 4. Market-data identity join contract", "",
          f"- BRK.A security_key: `{summary['market_data_identity_join'].get('security_keys', {}).get('BRK.A')}`",
          f"- BRK.B security_key: `{summary['market_data_identity_join'].get('security_keys', {}).get('BRK.B')}`",
          f"- shared issuer_key: `{summary['market_data_identity_join'].get('issuer_keys', {}).get('BRK.A')}`",
          "", "| check | result |", "|---|---|"]
    for k, v in summary["market_data_identity_join"].get("checks", {}).items():
        L.append(f"| {k} | {'PASS' if v else 'FAIL'} |")
    L.append("")
    L.append("See `IDENTITY_JOIN_CONTRACT.md` for the binding rule.")
    L.append("")

    if summary["errors"]:
        L += ["## Errors", ""] + [f"- {e}" for e in summary["errors"]] + [""]

    mp.write_text("\n".join(L))
    return {"json": str(jp), "md": str(mp)}


if __name__ == "__main__":
    s = run()
    raise SystemExit(0 if s["verdict"].endswith("MARKET DATA BENCHMARK") else 1)
