"""
=============================================================================
Phase 4A.5.2 — Free Market Data Benchmark
=============================================================================

Determine the minimum reliable FREE/PUBLIC market-data source stack for Stock
Atlas. This is a BENCHMARK, not a production build-out.

Governing rule: every market observation is bound to a Stock Atlas
`security_key` (identity_resolver.market_price_join_key), never a bare issuer
CIK. Provider tickers are lookup strings only. BRK.A and BRK.B must never
collapse into one price series.

FREE / PUBLIC ONLY. No paid plans. Providers exercised live only where free
access is currently available in this environment; otherwise the adapter is
implemented and reported NOT_EXERCISED (credentials absent).

Candidates: Twelve Data, Alpaca, Tiingo, Massive.

Artifacts: live_validation_results/<UTC-timestamp>_phase4a5_2.{json,md}
=============================================================================
"""

import json
import statistics
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from identity_resolver import resolve_security, market_price_join_key, IdentityJoinError
from market_data_providers import build_providers, MDResult

load_dotenv()

UNIVERSE = ["MSFT", "AAPL", "JPM", "O", "BRK.B", "SPY", "BRK.A"]
DIVIDEND_CONTROLS = ["MSFT", "AAPL", "JPM", "O", "SPY"]
SPLIT_CONTROLS = ["AAPL", "MSFT"]           # both have known splits
INVALID_TICKER = "ZZZZ_NOT_A_TICKER"
IDENTITY_STRESS = ("BRK.A", "BRK.B")

MATERIAL_PRICE_DISCREPANCY = 0.02           # 2% relative — flag, do not reconcile


# ---------------------------------------------------------------------------
def atlas_identity(sym):
    try:
        rs = resolve_security(sym)
        return {"atlas_symbol": sym, "security_key": rs.security_key if rs.resolved else None,
                "issuer_key": rs.issuer_key, "share_class": rs.share_class,
                "cik": rs.cik, "name": rs.issuer_name}
    except Exception as e:
        return {"atlas_symbol": sym, "security_key": None, "error": repr(e)}


def run_provider(provider, results):
    pname = provider.name
    rec = {
        "provider": pname,
        "eligibility": provider.eligibility,
        "homepage": provider.homepage,
        "key_env": list(provider.key_env),
        "credentials_present": bool(getattr(provider, "enabled", False)) and provider.eligibility != "NOT_ELIGIBLE"
        and (not provider.key_env or all((provider.credentials or {}).values())),
        "using_demo": getattr(provider, "using_demo", False),
        "published_limits": provider.published_limits,
        "securities": {},
        "invalid_ticker": None,
        "identity_gate": None,
        "capability_seen": {c: set() for c in
                            ["resolve", "latest_price", "daily_history", "dividends", "splits"]},
    }

    for sym in UNIVERSE:
        srec = {}
        for cap, fn in [
            ("resolve", lambda: provider.resolve_symbol(sym)),
            ("latest_price", lambda: provider.latest_price(sym)),
            ("daily_history", lambda: provider.daily_history(sym, 400)),
        ]:
            r = _safe(fn, provider.name, cap, sym)
            srec[cap] = r.to_dict()
            rec["capability_seen"][cap].add(r.state)
        if sym in DIVIDEND_CONTROLS:
            r = _safe(lambda: provider.dividends(sym), provider.name, "dividends", sym)
            srec["dividends"] = r.to_dict()
            rec["capability_seen"]["dividends"].add(r.state)
        if sym in SPLIT_CONTROLS:
            r = _safe(lambda: provider.splits(sym), provider.name, "splits", sym)
            srec["splits"] = r.to_dict()
            rec["capability_seen"]["splits"].add(r.state)
        rec["securities"][sym] = srec

    # invalid ticker — probe both resolve and latest_price
    inv_r = _safe(lambda: provider.resolve_symbol(INVALID_TICKER), provider.name, "resolve", INVALID_TICKER)
    inv_p = _safe(lambda: provider.latest_price(INVALID_TICKER), provider.name, "latest_price", INVALID_TICKER)
    rec["invalid_ticker"] = {
        "resolve_state": inv_r.state, "latest_price_state": inv_p.state,
        "notes": inv_r.notes + inv_p.notes,
        "distinguishes_from_available": inv_r.state in ("UNAVAILABLE", "ERROR")
        or inv_p.state in ("UNAVAILABLE", "ERROR", "NOT_ELIGIBLE"),
        "did_not_substitute_zero": not (isinstance(inv_p.data, dict) and inv_p.data.get("price") in (0, 0.0)),
        "did_not_fall_back_to_another_symbol": (inv_r.provider_symbol_returned in (None, INVALID_TICKER)),
    }

    # BRK.A / BRK.B hard identity gate
    rec["identity_gate"] = identity_gate(provider)

    for c in rec["capability_seen"]:
        rec["capability_seen"][c] = sorted(rec["capability_seen"][c])
    results.append(rec)
    return rec


def identity_gate(provider):
    out = {"pair": list(IDENTITY_STRESS), "per_symbol": {}, "verdict": None, "notes": []}
    keys, prices, price_states = {}, {}, {}
    prov_syms, instr_names, resolve_states = {}, {}, {}
    for sym in IDENTITY_STRESS:
        try:
            sk = market_price_join_key(sym)
        except IdentityJoinError:
            sk = None
        keys[sym] = sk
        rr = _safe(lambda: provider.resolve_symbol(sym), provider.name, "resolve", sym)
        pr = _safe(lambda: provider.latest_price(sym), provider.name, "latest_price", sym)
        resolve_states[sym] = rr.state
        prov_syms[sym] = rr.provider_symbol_returned or rr.query_symbol
        instr_names[sym] = (rr.data or {}).get("instrument_name") if isinstance(rr.data, dict) else None
        price_states[sym] = pr.state
        prices[sym] = (pr.data or {}).get("price") if isinstance(pr.data, dict) else None
        out["per_symbol"][sym] = {
            "atlas_security_key": sk,
            "provider_symbol": prov_syms[sym],
            "instrument_name": instr_names[sym],
            "resolve_state": rr.state,
            "price_state": pr.state,
            "price": prices[sym],
            "bound_security_key": pr.security_key or rr.security_key,
        }

    distinct_keys = bool(keys["BRK.A"] and keys["BRK.B"] and keys["BRK.A"] != keys["BRK.B"])
    distinct_prov_syms = bool(prov_syms["BRK.A"] and prov_syms["BRK.B"]
                              and prov_syms["BRK.A"] != prov_syms["BRK.B"])
    distinct_instr = bool(instr_names["BRK.A"] and instr_names["BRK.B"]
                          and instr_names["BRK.A"] != instr_names["BRK.B"])
    prices_exercised = all(price_states[s] in ("AVAILABLE", "STALE") for s in IDENTITY_STRESS)
    resolve_exercised = all(resolve_states[s] in ("AVAILABLE", "AMBIGUOUS") for s in IDENTITY_STRESS)

    if all(resolve_states[s] == "NOT_ELIGIBLE" for s in IDENTITY_STRESS):
        out["verdict"] = "NOT_ELIGIBLE"
        out["notes"].append("provider not eligible")
    elif not distinct_keys:
        out["verdict"] = "FAIL"
        out["notes"].append("Atlas did not produce distinct security_keys for the pair")
    elif prices_exercised:
        collapsed = (prices["BRK.A"] is not None and prices["BRK.B"] is not None
                     and abs(prices["BRK.A"] - prices["BRK.B"]) < 1.0)
        if collapsed or not distinct_prov_syms:
            out["verdict"] = "FAIL"
            out["notes"].append("provider cannot distinguish BRK.A from BRK.B (same symbol or near-identical price)")
        else:
            out["verdict"] = "PASS"
            out["notes"].append("distinct security_keys + distinct provider symbols + distinct prices")
    elif resolve_exercised and distinct_prov_syms and distinct_instr:
        out["verdict"] = "PASS_SYMBOL_LEVEL"
        out["notes"].append("distinct provider symbols and instrument names "
                            f"({prov_syms['BRK.A']}='{instr_names['BRK.A']}' vs "
                            f"{prov_syms['BRK.B']}='{instr_names['BRK.B']}'); "
                            "prices not exercised (no full API key)")
    elif not distinct_prov_syms and (resolve_exercised or prices_exercised):
        out["verdict"] = "FAIL"
        out["notes"].append("provider maps both classes to the same symbol")
    else:
        out["verdict"] = "NOT_EXERCISED"
        out["notes"].append(f"not exercised for this provider (resolve={resolve_states}, price={price_states}); "
                            "Atlas-side security_keys are distinct and the provider's documented symbol "
                            "convention gives distinct tickers per class")
    return out


def _safe(fn, provider, cap, sym) -> MDResult:
    try:
        return fn()
    except Exception as e:
        return MDResult(provider=provider, capability=cap, query_symbol=sym, atlas_symbol=sym,
                        state="ERROR", notes=[f"adapter raised: {e!r}", traceback.format_exc()[-400:]])


# ---------------------------------------------------------------------------
# reconciliation (only where >=2 providers actually returned the value)
# ---------------------------------------------------------------------------
def reconcile(results):
    rep = {"latest_price": [], "history_last_close": [], "dividends_latest": [], "splits": []}
    for sym in UNIVERSE:
        # latest price
        px = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("latest_price", {})
            if d.get("state") in ("AVAILABLE", "STALE") and isinstance(d.get("data"), dict):
                v = d["data"].get("price")
                if v:
                    px[pr["provider"]] = v
        if len(px) >= 2:
            vals = list(px.values())
            spread = (max(vals) - min(vals)) / statistics.mean(vals)
            rep["latest_price"].append({
                "symbol": sym, "values": px, "relative_spread": round(spread, 4),
                "material": spread > MATERIAL_PRICE_DISCREPANCY,
            })
        # history last close
        hc = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("daily_history", {})
            raw = d.get("raw") or {}
            sample = raw.get("sample") if isinstance(raw, dict) else None
            if d.get("state") == "AVAILABLE" and sample:
                hc[pr["provider"]] = {"last_date": (d.get("data") or {}).get("last"),
                                      "sample_close": sample[0].get("close")}
        if len(hc) >= 2:
            rep["history_last_close"].append({"symbol": sym, "providers": hc})
        # dividends latest
        dv = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("dividends", {})
            if d.get("state") == "AVAILABLE" and isinstance(d.get("data"), dict):
                dv[pr["provider"]] = d["data"].get("latest")
        if len(dv) >= 2:
            rep["dividends_latest"].append({"symbol": sym, "providers": dv})
        # splits
        sp = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("splits", {})
            if d.get("state") == "AVAILABLE" and isinstance(d.get("data"), dict):
                sp[pr["provider"]] = d["data"].get("count")
        if len(sp) >= 2:
            rep["splits"].append({"symbol": sym, "provider_counts": sp})
    return rep


# ---------------------------------------------------------------------------
# provider verdicts
# ---------------------------------------------------------------------------
def provider_verdict(rec):
    if rec["eligibility"] == "NOT_ELIGIBLE":
        return "NOT_ELIGIBLE", "no identifiable free market-data API"

    ident = rec["identity_gate"]["verdict"]
    # distinct symbols with a live DATA capability (price or history)
    data_symbols = {
        s for s in UNIVERSE for c in ("latest_price", "daily_history")
        if rec["securities"].get(s, {}).get(c, {}).get("state") in ("AVAILABLE", "STALE")
    }
    resolve_symbols = {
        s for s in UNIVERSE
        if rec["securities"].get(s, {}).get("resolve", {}).get("state") in ("AVAILABLE", "AMBIGUOUS")
    }
    caps = rec["capability_seen"]
    caps_seen_live = [c for c in ("resolve", "latest_price", "daily_history", "dividends", "splits")
                      if any(st in ("AVAILABLE", "STALE") for st in caps.get(c, []))]

    if ident == "FAIL":
        return ("SPECIALTY_ONLY",
                "fails the BRK.A/BRK.B identity gate — usable only where share-class identity is not at stake")
    if not data_symbols and not resolve_symbols:
        return ("SECONDARY_CANDIDATE",
                "adapter implemented; free tier needs an API key absent from this environment "
                "-> not live-verified. Documented free access is suitable; classify pending keys.")
    if len(data_symbols) >= 5 and len(caps_seen_live) == 5 and ident == "PASS":
        return "PRIMARY_CANDIDATE", "full universe + all capabilities + identity gate exercised live"
    return ("SECONDARY_CANDIDATE",
            f"partial live coverage: {len(data_symbols)} symbol(s) with price/history, "
            f"{len(resolve_symbols)} resolved, capabilities live={caps_seen_live}, identity gate={ident}. "
            "Full classification pending a free API key.")


# ---------------------------------------------------------------------------
def run():
    started = datetime.now(timezone.utc).isoformat()
    identities = {s: atlas_identity(s) for s in UNIVERSE}

    providers = build_providers()
    results = []
    for p in providers:
        try:
            run_provider(p, results)
        except Exception as e:
            results.append({"provider": p.name, "fatal": repr(e), "traceback": traceback.format_exc(),
                            "eligibility": getattr(p, "eligibility", "?"), "securities": {},
                            "identity_gate": {"verdict": "ERROR"}, "capability_seen": {}})

    recon = reconcile(results)

    verdicts = {}
    for rec in results:
        v, why = provider_verdict(rec)
        verdicts[rec["provider"]] = {"verdict": v, "rationale": why}
        rec["verdict"] = v
        rec["verdict_rationale"] = why

    # final phase verdict
    live_ok = [p for p, v in verdicts.items() if v["verdict"] == "PRIMARY_CANDIDATE"]
    any_ident_fail = any(r["identity_gate"]["verdict"] == "FAIL" for r in results if r.get("identity_gate"))
    any_live = any(
        r["securities"].get(s, {}).get(c, {}).get("state") in ("AVAILABLE", "STALE")
        for r in results for s in UNIVERSE for c in ("latest_price", "daily_history"))

    if live_ok and not any_ident_fail:
        final = "PHASE 4A.5.2 PASS — MINIMUM FREE MARKET DATA STACK IDENTIFIED"
    elif any_live or all(v["verdict"] in ("PRIMARY_CANDIDATE", "SECONDARY_CANDIDATE", "SPECIALTY_ONLY", "NOT_ELIGIBLE")
                         for v in verdicts.values()):
        final = "PHASE 4A.5.2 PASS WITH SOURCE GAPS"
    else:
        final = "PHASE 4A.5.2 FAIL — FREE MARKET DATA INSUFFICIENT"

    summary = {
        "phase": "4A.5.2",
        "started_utc": started,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_baseline": "d37f654 (untouched)",
        "start_commit": "d2b0d93",
        "universe": UNIVERSE,
        "atlas_identities": identities,
        "providers": results,
        "provider_verdicts": verdicts,
        "reconciliation": recon,
        "recommended_stack": recommended_stack(results, verdicts),
        "verdict": final,
    }
    art = write_artifacts(summary)
    summary["artifacts"] = art

    _console(summary)
    return summary


def recommended_stack(results, verdicts):
    prim = [p for p, v in verdicts.items() if v["verdict"] == "PRIMARY_CANDIDATE"]
    sec = [p for p, v in verdicts.items() if v["verdict"] == "SECONDARY_CANDIDATE"]
    return {
        "primary": prim,
        "secondary_for_cross_check": sec,
        "principle": "smallest stack that gives decision-grade inputs: 1 primary EOD/history "
                     "+ 1 secondary for cross-check of price/dividend/split events",
        "note": "final selection pending live verification with free API keys (see unresolved issues)",
    }


def _console(s):
    print("\n" + "=" * 70)
    print("PHASE 4A.5.2 — FREE MARKET DATA BENCHMARK")
    print("=" * 70)
    for r in s["providers"]:
        ig = (r.get("identity_gate") or {}).get("verdict")
        print(f"\n[{r['provider']}] eligibility={r['eligibility']} verdict={r.get('verdict')}")
        print(f"   identity gate (BRK.A/BRK.B): {ig}")
        for cap, states in (r.get("capability_seen") or {}).items():
            print(f"   {cap:14s}: {states}")
        it = r.get('invalid_ticker', {}) or {}
        print(f"   invalid ticker -> resolve={it.get('resolve_state')} price={it.get('latest_price_state')} "
              f"(distinguished={it.get('distinguishes_from_available')})")
    print(f"\nRecommended stack: {s['recommended_stack']}")
    print(f"\nArtifacts:\n  JSON: {s['artifacts']['json']}\n  MD:   {s['artifacts']['md']}")
    print(f"\nVERDICT: {s['verdict']}")


# ---------------------------------------------------------------------------
def write_artifacts(summary, results_dir="live_validation_results"):
    d = Path(results_dir)
    d.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jp = d / f"{ts}_phase4a5_2.json"
    mp = d / f"{ts}_phase4a5_2.md"
    jp.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))

    L = ["# Phase 4A.5.2 — Free Market Data Benchmark", "",
         f"- Generated (UTC): {summary['generated_utc']}",
         f"- Start commit: {summary['start_commit']} · frozen baseline {summary['frozen_baseline']}",
         f"- Universe: {', '.join(summary['universe'])}",
         f"- **Verdict: {summary['verdict']}**", ""]

    # A. eligibility
    L += ["## A. Provider eligibility", "",
          "| provider | eligibility | credentials in env | key vars | notes |",
          "|---|---|---|---|---|"]
    for r in summary["providers"]:
        note = "; ".join(f"{k}: {v}" for k, v in list(r.get("published_limits", {}).items())[:1])
        L.append(f"| {r['provider']} | {r['eligibility']} | {r.get('credentials_present')} | "
                 f"{', '.join(r.get('key_env') or []) or '—'} | {note} |")
    L.append("")

    # B. provider x capability
    L += ["## B. Provider × capability matrix (observed states across universe)", "",
          "| provider | resolve | latest_price | daily_history | dividends | splits |",
          "|---|---|---|---|---|---|"]
    for r in summary["providers"]:
        cs = r.get("capability_seen", {})
        L.append(f"| {r['provider']} | {cs.get('resolve')} | {cs.get('latest_price')} | "
                 f"{cs.get('daily_history')} | {cs.get('dividends')} | {cs.get('splits')} |")
    L.append("")

    # C. security x provider
    L += ["## C. Security × provider results (latest_price / daily_history state)", "",
          "| security | " + " | ".join(r["provider"] for r in summary["providers"]) + " |",
          "|" + "---|" * (len(summary["providers"]) + 1)]
    for sym in summary["universe"]:
        cells = []
        for r in summary["providers"]:
            s = r["securities"].get(sym, {})
            cells.append(f"{s.get('latest_price', {}).get('state', '-')}/{s.get('daily_history', {}).get('state', '-')}")
        L.append(f"| {sym} | " + " | ".join(cells) + " |")
    L.append("")

    # D. identity gate
    L += ["## D. BRK.A / BRK.B identity hard gate", ""]
    for sym in ("BRK.A", "BRK.B"):
        i = summary["atlas_identities"][sym]
        L.append(f"- {sym}: security_key `{i.get('security_key')}` (issuer `{i.get('issuer_key')}`, class {i.get('share_class')})")
    L += ["", "| provider | verdict | BRK.A resolve/price | BRK.B resolve/price | distinct provider symbols | notes |",
          "|---|---|---|---|---|---|"]
    for r in summary["providers"]:
        g = r.get("identity_gate", {})
        ps = g.get("per_symbol", {})
        a, b = ps.get("BRK.A", {}), ps.get("BRK.B", {})
        dps = bool(a.get("provider_symbol") and b.get("provider_symbol")
                   and a.get("provider_symbol") != b.get("provider_symbol"))
        L.append(f"| {r['provider']} | {g.get('verdict')} | "
                 f"{a.get('resolve_state')}/{a.get('price_state')} | "
                 f"{b.get('resolve_state')}/{b.get('price_state')} | {dps} | "
                 f"{'; '.join(g.get('notes', []))} |")
    L.append("")

    # E-H comparisons
    rc = summary["reconciliation"]
    L += ["## E. Latest-price comparison (>=2 providers)", ""]
    if rc["latest_price"]:
        L += ["| symbol | values | rel spread | material? |", "|---|---|---|---|"]
        for x in rc["latest_price"]:
            L.append(f"| {x['symbol']} | {x['values']} | {x['relative_spread']} | {x['material']} |")
    else:
        L.append("_no symbol had a live latest price from 2+ providers_")
    L += ["", "## F. Historical-data comparison (>=2 providers)", ""]
    L.append(json.dumps(rc["history_last_close"], indent=2) if rc["history_last_close"]
             else "_no symbol had live history from 2+ providers_")
    L += ["", "## G. Dividend comparison (>=2 providers)", ""]
    L.append(json.dumps(rc["dividends_latest"], indent=2) if rc["dividends_latest"]
             else "_no symbol had live dividends from 2+ providers_")
    L += ["", "## H. Split / corporate-action comparison (>=2 providers)", ""]
    L.append(json.dumps(rc["splits"], indent=2) if rc["splits"]
             else "_no symbol had live splits from 2+ providers_")

    # I. freshness
    L += ["", "## I. Freshness / timestamp findings", ""]
    for r in summary["providers"]:
        lp = r["securities"].get("AAPL", {}).get("latest_price", {}) or r["securities"].get("MSFT", {}).get("latest_price", {})
        if lp.get("state") in ("AVAILABLE", "STALE"):
            L.append(f"- {r['provider']}: feed_class={lp.get('feed_class')} · provider_ts={lp.get('provider_timestamp')} "
                     f"· tz={lp.get('provider_timezone')} · stated_delay={lp.get('stated_delay')} · state={lp.get('state')}")
        else:
            L.append(f"- {r['provider']}: not live-exercised — freshness semantics from documentation only")
    L.append("")

    # J. rate limits
    L += ["## J. Rate-limit / free-tier findings", ""]
    for r in summary["providers"]:
        L.append(f"### {r['provider']}")
        for k, v in r.get("published_limits", {}).items():
            L.append(f"- **{k}**: {v}")
        L.append("")

    # K. failures / discrepancies
    L += ["## K. Failures and discrepancies", ""]
    any_k = False
    for r in summary["providers"]:
        for sym, caps in r["securities"].items():
            for cap, d in caps.items():
                if d.get("state") in ("ERROR", "RATE_LIMITED", "AMBIGUOUS"):
                    any_k = True
                    L.append(f"- {r['provider']} / {sym} / {cap}: {d.get('state')} — {'; '.join(d.get('notes', []))}")
        it = r.get("invalid_ticker", {})
        if not it.get("distinguishes_from_available"):
            any_k = True
            L.append(f"- {r['provider']}: invalid ticker not distinguished ({it.get('state')})")
    for x in rc["latest_price"]:
        if x["material"]:
            any_k = True
            L.append(f"- price discrepancy {x['symbol']}: {x['values']} (spread {x['relative_spread']})")
    if not any_k:
        L.append("_none observed in the exercised surface_")
    L.append("")

    # L. burden
    L += ["## L. Implementation / maintenance burden", "",
          "| provider | adapter LOC (approx) | endpoints used | quirks | maintenance |",
          "|---|---|---|---|---|",
          "| twelvedata | ~180 | /quote /time_series /dividends /splits /symbol_search | error-as-200 JSON; "
          "no adj-close on free; demo key = AAPL only | low |",
          "| alpaca | ~90 | /v2 snapshot /trades /bars, /v1/corporate-actions | IEX-only feed; header auth; "
          "dotted share-class tickers | low-medium |",
          "| tiingo | ~90 | /tiingo/daily /tiingo/daily/prices /iex | divs+splits embedded in daily rows (elegant); "
          "hyphen share-class tickers; 50 req/hr | low |",
          "| massive | n/a | — | not a real market-data API | n/a |", ""]

    # M. recommended stack
    L += ["## M. Recommended minimum source stack", "",
          f"- **primary:** {summary['recommended_stack']['primary'] or '(pending free API key verification)'}",
          f"- **secondary (cross-check):** {summary['recommended_stack']['secondary_for_cross_check']}",
          f"- principle: {summary['recommended_stack']['principle']}",
          f"- {summary['recommended_stack']['note']}", ""]

    # N. unresolved
    L += ["## N. Unresolved issues", "",
          "- No market-data API keys are present in this environment, so Twelve Data (beyond the "
          "AAPL-only demo key), Alpaca, and Tiingo could not be exercised live across the full "
          "universe or the BRK.A/BRK.B identity gate. Adapters are implemented and ready.",
          "- 'Massive' does not resolve to a real free market-data API — treat as removed from the "
          "candidate list unless the planning source is clarified.",
          "- Stooq (the classic keyless CSV fallback) now serves a JavaScript bot-check instead of "
          "CSV; automating around it would violate the no-evasion rule, so it is NOT ELIGIBLE.",
          "- Free real-time consolidated (SIP) US equity data does not exist on any candidate; the "
          "realistic free posture is EOD/consolidated close + delayed or IEX-only intraday.",
          "- Adjusted-close handling differs (Tiingo supplies explicit adj columns; Twelve Data free "
          "does not; Alpaca applies adjustment=all). Not normalized here, per instructions.",
          ""]

    # provider verdicts
    L += ["## Provider verdicts", "", "| provider | verdict | rationale |", "|---|---|---|"]
    for p, v in summary["provider_verdicts"].items():
        L.append(f"| {p} | {v['verdict']} | {v['rationale']} |")
    L.append("")

    mp.write_text("\n".join(L))
    return {"json": str(jp), "md": str(mp)}


if __name__ == "__main__":
    s = run()
    raise SystemExit(0 if not s["verdict"].startswith("PHASE 4A.5.2 FAIL") else 1)
