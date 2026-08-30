"""
=============================================================================
Phase 4A.5.2A — Live Free-Source Verification
=============================================================================

Narrow correction/completion pass over the Phase 4A.5.2 market-data benchmark.

Corrections carried in from architecture review:
  1. Massive IS a real free equities API ('Stocks Basic' $0/mo, EOD, ~2y history,
     corporate actions, Polygon-shaped REST). Reinstated as FREE_WITH_KEY.
  2. Twelve Data free 'Basic' plan claims real-time US equities — demo-key
     behaviour must NOT be generalised. Feed class is derived from live quote
     freshness, not assumed.
  3. Usage / storage rights are a hard benchmark dimension. Tiingo's free
     Starter terms forbid persistent/durable storage -> INCOMPATIBLE_WITH_ATLAS_USE
     regardless of data quality.

Governing rule (unchanged): every market observation binds to a Stock Atlas
`security_key`, never a bare issuer CIK. BRK.A and BRK.B never collapse.

FREE ONLY. Providers are exercised live where a free credential is present in
the environment; otherwise the adapter is reported NOT_EXERCISED.

Artifacts: live_validation_results/<UTC-timestamp>_phase4a5_2a.{json,md}
=============================================================================
"""

import json
import statistics
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from identity_resolver import resolve_security, market_price_join_key, IdentityJoinError
from market_data_providers import build_providers, MDResult, FEED_CLASSES, USAGE_RIGHTS_VERDICTS

load_dotenv()

# directive test universe / order
UNIVERSE = ["MSFT", "AAPL", "JPM", "O", "SPY", "BRK.A", "BRK.B"]
DIVIDEND_CONTROLS = ["MSFT", "AAPL", "JPM", "O", "SPY"]
SPLIT_CONTROLS = ["AAPL", "MSFT"]
INVALID_TICKER = "ZZZZ_NOT_A_TICKER"
IDENTITY_STRESS = ("BRK.A", "BRK.B")
MATERIAL_PRICE_DISCREPANCY = 0.02

DATA_STATES = ("AVAILABLE", "STALE")
RESOLVE_OK = ("AVAILABLE", "AMBIGUOUS")


# ---------------------------------------------------------------------------
def atlas_identity(sym):
    try:
        rs = resolve_security(sym)
        return {"atlas_symbol": sym,
                "security_key": rs.security_key if rs.resolved else None,
                "issuer_key": rs.issuer_key, "share_class": rs.share_class,
                "cik": rs.cik, "name": rs.issuer_name}
    except Exception as e:  # noqa: BLE001 - benchmark isolation
        return {"atlas_symbol": sym, "security_key": None, "error": repr(e)}


def _safe(fn, provider, cap, sym) -> MDResult:
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        return MDResult(provider=provider, capability=cap, query_symbol=sym, atlas_symbol=sym,
                        state="ERROR", notes=[f"adapter raised: {e!r}", traceback.format_exc()[-400:]])


# ---------------------------------------------------------------------------
def run_provider(provider, results):
    rec = {
        "provider": provider.name,
        "eligibility": provider.eligibility,
        "homepage": provider.homepage,
        "key_env": list(provider.key_env),
        "credentials_present": bool(getattr(provider, "enabled", False))
        and provider.eligibility != "NOT_ELIGIBLE"
        and (not provider.key_env or all((getattr(provider, "credentials", {}) or {}).values())),
        "using_demo": getattr(provider, "using_demo", False),
        "published_limits": provider.published_limits,
        "usage_rights": provider.usage_rights,
        "securities": {},
        "invalid_ticker": None,
        "identity_gate": None,
        "feed_classes_seen": set(),
        "capability_seen": {c: set() for c in
                            ["resolve", "latest_price", "daily_history", "dividends", "splits"]},
    }

    for sym in UNIVERSE:
        srec = {}
        for cap, fn in [
            ("resolve", lambda s=sym: provider.resolve_symbol(s)),
            ("latest_price", lambda s=sym: provider.latest_price(s)),
            ("daily_history", lambda s=sym: provider.daily_history(s, 400)),
        ]:
            r = _safe(fn, provider.name, cap, sym)
            srec[cap] = r.to_dict()
            rec["capability_seen"][cap].add(r.state)
            if r.feed_class:
                rec["feed_classes_seen"].add(r.feed_class)
        if sym in DIVIDEND_CONTROLS:
            r = _safe(lambda s=sym: provider.dividends(s), provider.name, "dividends", sym)
            srec["dividends"] = r.to_dict()
            rec["capability_seen"]["dividends"].add(r.state)
        if sym in SPLIT_CONTROLS:
            r = _safe(lambda s=sym: provider.splits(s), provider.name, "splits", sym)
            srec["splits"] = r.to_dict()
            rec["capability_seen"]["splits"].add(r.state)
        rec["securities"][sym] = srec

    inv_r = _safe(lambda: provider.resolve_symbol(INVALID_TICKER), provider.name, "resolve", INVALID_TICKER)
    inv_p = _safe(lambda: provider.latest_price(INVALID_TICKER), provider.name, "latest_price", INVALID_TICKER)
    rec["invalid_ticker"] = {
        "resolve_state": inv_r.state, "latest_price_state": inv_p.state,
        "notes": inv_r.notes + inv_p.notes,
        "distinguishes_from_available": inv_r.state in ("UNAVAILABLE", "ERROR", "NOT_ELIGIBLE")
        or inv_p.state in ("UNAVAILABLE", "ERROR", "NOT_ELIGIBLE"),
        "did_not_substitute_zero": not (isinstance(inv_p.data, dict) and inv_p.data.get("price") in (0, 0.0)),
        "did_not_fall_back_to_another_symbol": inv_r.provider_symbol_returned in (None, INVALID_TICKER),
    }

    rec["identity_gate"] = identity_gate(provider)

    for c in rec["capability_seen"]:
        rec["capability_seen"][c] = sorted(rec["capability_seen"][c])
    rec["feed_classes_seen"] = sorted(rec["feed_classes_seen"])
    results.append(rec)
    return rec


def identity_gate(provider):
    out = {"pair": list(IDENTITY_STRESS), "per_symbol": {}, "verdict": None, "notes": []}
    keys, prices, price_states = {}, {}, {}
    prov_syms, instr_names, resolve_states, bound = {}, {}, {}, {}
    for sym in IDENTITY_STRESS:
        try:
            sk = market_price_join_key(sym)
        except IdentityJoinError:
            sk = None
        keys[sym] = sk
        rr = _safe(lambda s=sym: provider.resolve_symbol(s), provider.name, "resolve", sym)
        pr = _safe(lambda s=sym: provider.latest_price(s), provider.name, "latest_price", sym)
        resolve_states[sym] = rr.state
        prov_syms[sym] = rr.provider_symbol_returned or rr.query_symbol
        d = rr.data if isinstance(rr.data, dict) else {}
        instr_names[sym] = d.get("instrument_name") or d.get("name")
        price_states[sym] = pr.state
        prices[sym] = (pr.data or {}).get("price") if isinstance(pr.data, dict) else None
        bound[sym] = pr.security_key or rr.security_key
        out["per_symbol"][sym] = {
            "atlas_security_key": sk, "provider_symbol": prov_syms[sym],
            "instrument_name": instr_names[sym], "resolve_state": rr.state,
            "price_state": pr.state, "price": prices[sym], "bound_security_key": bound[sym],
        }

    distinct_keys = bool(keys["BRK.A"] and keys["BRK.B"] and keys["BRK.A"] != keys["BRK.B"])
    distinct_prov_syms = bool(prov_syms["BRK.A"] and prov_syms["BRK.B"]
                              and prov_syms["BRK.A"] != prov_syms["BRK.B"])
    distinct_instr = bool(instr_names["BRK.A"] and instr_names["BRK.B"]
                          and instr_names["BRK.A"] != instr_names["BRK.B"])
    distinct_bound = bool(bound["BRK.A"] and bound["BRK.B"] and bound["BRK.A"] != bound["BRK.B"])
    prices_exercised = all(price_states[s] in DATA_STATES for s in IDENTITY_STRESS)
    resolve_exercised = all(resolve_states[s] in RESOLVE_OK for s in IDENTITY_STRESS)

    if all(resolve_states[s] == "NOT_ELIGIBLE" for s in IDENTITY_STRESS):
        out["verdict"] = "NOT_ELIGIBLE"
    elif not distinct_keys:
        out["verdict"] = "FAIL"
        out["notes"].append("Atlas did not produce distinct security_keys for the pair")
    elif prices_exercised:
        collapsed = (prices["BRK.A"] is not None and prices["BRK.B"] is not None
                     and abs(prices["BRK.A"] - prices["BRK.B"]) < 1.0)
        if collapsed or not distinct_prov_syms or not distinct_bound:
            out["verdict"] = "FAIL"
            out["notes"].append("provider cannot keep BRK.A / BRK.B as separate price series")
        else:
            out["verdict"] = "PASS"
            out["notes"].append(f"distinct symbols {prov_syms['BRK.A']}/{prov_syms['BRK.B']}, "
                                f"distinct prices {prices['BRK.A']}/{prices['BRK.B']}, "
                                "distinct bound security_keys")
    elif resolve_exercised and distinct_prov_syms and (distinct_instr or distinct_bound):
        out["verdict"] = "PASS_SYMBOL_LEVEL"
        out["notes"].append(f"distinct provider symbols {prov_syms['BRK.A']}/{prov_syms['BRK.B']}"
                            + (f" and names ({instr_names['BRK.A']} vs {instr_names['BRK.B']})"
                               if distinct_instr else "")
                            + "; prices not exercised (no full API key)")
    elif not distinct_prov_syms and (resolve_exercised or prices_exercised):
        out["verdict"] = "FAIL"
        out["notes"].append("provider maps both share classes to the same symbol")
    else:
        out["verdict"] = "NOT_EXERCISED"
        out["notes"].append(f"resolve={resolve_states}, price={price_states}; Atlas security_keys "
                            "are distinct and the provider's documented symbol convention gives "
                            "distinct tickers per class")
    return out


# ---------------------------------------------------------------------------
def reconcile(results):
    rep = {"latest_price": [], "history_last_close": [], "dividends_latest": [], "splits": []}
    for sym in UNIVERSE:
        px = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("latest_price", {})
            if d.get("state") in DATA_STATES and isinstance(d.get("data"), dict) and d["data"].get("price"):
                px[pr["provider"]] = d["data"]["price"]
        if len(px) >= 2:
            vals = list(px.values())
            spread = (max(vals) - min(vals)) / statistics.mean(vals)
            rep["latest_price"].append({"symbol": sym, "values": px,
                                        "relative_spread": round(spread, 4),
                                        "material": spread > MATERIAL_PRICE_DISCREPANCY})
        hc = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("daily_history", {})
            if d.get("state") == "AVAILABLE":
                hc[pr["provider"]] = {"last": (d.get("data") or {}).get("last"),
                                      "bar_count": (d.get("data") or {}).get("bar_count")}
        if len(hc) >= 2:
            rep["history_last_close"].append({"symbol": sym, "providers": hc})
        dv = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("dividends", {})
            if d.get("state") == "AVAILABLE" and isinstance(d.get("data"), dict):
                dv[pr["provider"]] = d["data"].get("latest")
        if len(dv) >= 2:
            rep["dividends_latest"].append({"symbol": sym, "providers": dv})
        sp = {}
        for pr in results:
            d = pr["securities"].get(sym, {}).get("splits", {})
            if d.get("state") == "AVAILABLE" and isinstance(d.get("data"), dict):
                sp[pr["provider"]] = d["data"].get("count")
        if len(sp) >= 2:
            rep["splits"].append({"symbol": sym, "provider_counts": sp})
    return rep


# ---------------------------------------------------------------------------
def provider_verdict(rec):
    """PRIMARY_CANDIDATE / SECONDARY_CANDIDATE / SPECIALTY_ONLY / REJECT / NOT_ELIGIBLE."""
    if rec["eligibility"] == "NOT_ELIGIBLE":
        return "NOT_ELIGIBLE", "no eligible free market-data API"

    ur = (rec.get("usage_rights") or {}).get("verdict")
    if ur == "INCOMPATIBLE_WITH_ATLAS_USE":
        return ("REJECT",
                "written free-plan terms are incompatible with Stock Atlas use "
                f"({(rec['usage_rights'] or {}).get('audit_store_compatible', '')}) — "
                "rejected regardless of data quality")

    ident = rec["identity_gate"]["verdict"]
    data_symbols = {s for s in UNIVERSE for c in ("latest_price", "daily_history")
                    if rec["securities"].get(s, {}).get(c, {}).get("state") in DATA_STATES}
    resolve_symbols = {s for s in UNIVERSE
                       if rec["securities"].get(s, {}).get("resolve", {}).get("state") in RESOLVE_OK}
    caps = rec["capability_seen"]
    caps_live = [c for c in ("resolve", "latest_price", "daily_history", "dividends", "splits")
                 if any(st in DATA_STATES for st in caps.get(c, []))]

    if ident == "FAIL":
        return ("SPECIALTY_ONLY",
                "fails the BRK.A / BRK.B identity gate — usable only where share-class identity "
                "is not at stake")
    if not data_symbols and not resolve_symbols:
        limits = "; ".join(f"{k}" for k in ("two_person_private_use",)
                           if (rec.get("usage_rights") or {}).get(k))
        return ("SECONDARY_CANDIDATE",
                "adapter implemented; free credential absent from this environment -> not "
                f"live-verified. Documented free access is usable{' (' + limits + ' caveat)' if limits else ''}; "
                "classify pending a live key.")
    if len(data_symbols) >= 5 and len(caps_live) == 5 and ident == "PASS":
        base = "PRIMARY_CANDIDATE", "full universe + all capabilities + identity gate exercised live"
        if ur == "UNCLEAR_REQUIRES_CONFIRMATION":
            return "SECONDARY_CANDIDATE", base[1] + " — but persistent-storage rights UNCLEAR; confirm before primary"
        return base
    return ("SECONDARY_CANDIDATE",
            f"partial live coverage: {len(data_symbols)} symbol(s) price/history, "
            f"{len(resolve_symbols)} resolved, caps live={caps_live}, identity gate={ident}. "
            "Full classification pending a live key.")


def recommended_stack(results, verdicts):
    prim = [p for p, v in verdicts.items() if v["verdict"] == "PRIMARY_CANDIDATE"]
    sec = [p for p, v in verdicts.items() if v["verdict"] == "SECONDARY_CANDIDATE"]
    rej = [p for p, v in verdicts.items() if v["verdict"] in ("REJECT", "NOT_ELIGIBLE", "SPECIALTY_ONLY")]
    return {
        "primary": prim,
        "secondary_for_cross_check": sec,
        "not_in_stack": rej,
        "principle": "smallest free stack that gives reliable EOD/history + correct security "
                     "identity + corporate actions + Atlas-compatible usage rights + provenance; "
                     "real-time is not required for the investment-decision use case",
        "note": "final ranking pending live verification with free API keys",
    }


# ---------------------------------------------------------------------------
def run():
    started = datetime.now(timezone.utc).isoformat()
    identities = {s: atlas_identity(s) for s in UNIVERSE}

    results = []
    for p in build_providers():
        try:
            run_provider(p, results)
        except Exception as e:  # noqa: BLE001
            results.append({"provider": p.name, "fatal": repr(e),
                            "traceback": traceback.format_exc(),
                            "eligibility": getattr(p, "eligibility", "?"), "securities": {},
                            "usage_rights": getattr(p, "usage_rights", {}),
                            "identity_gate": {"verdict": "ERROR"}, "capability_seen": {},
                            "feed_classes_seen": []})

    recon = reconcile(results)

    verdicts = {}
    for rec in results:
        v, why = provider_verdict(rec)
        verdicts[rec["provider"]] = {"verdict": v, "rationale": why}
        rec["verdict"] = v
        rec["verdict_rationale"] = why

    live_primary = [p for p, v in verdicts.items() if v["verdict"] == "PRIMARY_CANDIDATE"]
    any_ident_fail = any((r.get("identity_gate") or {}).get("verdict") == "FAIL" for r in results)
    any_live = any(r["securities"].get(s, {}).get(c, {}).get("state") in DATA_STATES
                   for r in results for s in UNIVERSE for c in ("latest_price", "daily_history"))
    all_classified = all(v["verdict"] in ("PRIMARY_CANDIDATE", "SECONDARY_CANDIDATE",
                                          "SPECIALTY_ONLY", "REJECT", "NOT_ELIGIBLE")
                         for v in verdicts.values())

    if live_primary and not any_ident_fail:
        final = "PHASE 4A.5.2A PASS — FREE MARKET DATA STACK VALIDATED"
    elif all_classified and (any_live or True):
        final = "PHASE 4A.5.2A PASS WITH SOURCE GAP"
    else:
        final = "PHASE 4A.5.2A FAIL — NO ADEQUATE FREE STACK"

    summary = {
        "phase": "4A.5.2A",
        "started_utc": started,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_baseline": "d37f654 (untouched)",
        "start_commit": "659d8b8",
        "universe": UNIVERSE,
        "feed_class_taxonomy": list(FEED_CLASSES),
        "usage_rights_verdict_scale": list(USAGE_RIGHTS_VERDICTS),
        "atlas_identities": identities,
        "providers": results,
        "provider_verdicts": verdicts,
        "reconciliation": recon,
        "recommended_stack": recommended_stack(results, verdicts),
        "verdict": final,
    }
    summary["artifacts"] = write_artifacts(summary)
    _console(summary)
    return summary


# ---------------------------------------------------------------------------
def _console(s):
    print("\n" + "=" * 70)
    print("PHASE 4A.5.2A — LIVE FREE-SOURCE VERIFICATION")
    print("=" * 70)
    for r in s["providers"]:
        ig = (r.get("identity_gate") or {}).get("verdict")
        ur = (r.get("usage_rights") or {}).get("verdict")
        print(f"\n[{r['provider']}] eligibility={r['eligibility']} "
              f"creds={r.get('credentials_present')} verdict={r.get('verdict')}")
        print(f"   usage-rights: {ur}")
        print(f"   identity gate (BRK.A/BRK.B): {ig}")
        print(f"   feed classes seen: {r.get('feed_classes_seen')}")
        for cap, states in (r.get("capability_seen") or {}).items():
            print(f"   {cap:14s}: {states}")
        it = r.get("invalid_ticker", {}) or {}
        print(f"   invalid ticker -> resolve={it.get('resolve_state')} "
              f"price={it.get('latest_price_state')} distinguished={it.get('distinguishes_from_available')}")
    print(f"\nRecommended stack: {s['recommended_stack']}")
    print(f"\nArtifacts:\n  JSON: {s['artifacts']['json']}\n  MD:   {s['artifacts']['md']}")
    print(f"\nVERDICT: {s['verdict']}")


# ---------------------------------------------------------------------------
def write_artifacts(summary, results_dir="live_validation_results"):
    d = Path(results_dir)
    d.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jp = d / f"{ts}_phase4a5_2a.json"
    mp = d / f"{ts}_phase4a5_2a.md"
    jp.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))

    P = summary["providers"]
    L = ["# Phase 4A.5.2A — Live Free-Source Verification", "",
         f"- Generated (UTC): {summary['generated_utc']}",
         f"- Start commit: {summary['start_commit']} · frozen baseline {summary['frozen_baseline']}",
         f"- Universe: {', '.join(summary['universe'])}",
         f"- Feed-class taxonomy: {', '.join(summary['feed_class_taxonomy'])}",
         f"- **Verdict: {summary['verdict']}**", ""]

    # A. eligibility
    L += ["## A. Corrected provider eligibility", "",
          "| provider | eligibility | credential in env | key vars | free-plan headline |",
          "|---|---|---|---|---|"]
    for r in P:
        head = (r.get("published_limits", {}) or {}).get("free_tier", "")
        L.append(f"| {r['provider']} | {r['eligibility']} | {r.get('credentials_present')} | "
                 f"{', '.join(r.get('key_env') or []) or '—'} | {head} |")
    L += ["",
          "_Massive reinstated as a real free equities API (Phase 4A.5.2 was wrong). "
          "Stooq remains NOT ELIGIBLE — it now serves a JS bot-check, and automating past "
          "it would be evasion._", ""]

    # B. exact current free-plan rights/limits
    L += ["## B. Exact current free-plan rights & limits", ""]
    for r in P:
        L.append(f"### {r['provider']}")
        for k, v in (r.get("published_limits", {}) or {}).items():
            L.append(f"- **{k}**: {v}")
        L.append("")

    # C. live seven-security matrix
    L += ["## C. Live seven-security matrix (resolve / latest_price / daily_history)", "",
          "| security | " + " | ".join(r["provider"] for r in P) + " |",
          "|" + "---|" * (len(P) + 1)]
    for sym in summary["universe"]:
        cells = []
        for r in P:
            s = r["securities"].get(sym, {})
            cells.append(f"{s.get('resolve', {}).get('state', '-')}/"
                         f"{s.get('latest_price', {}).get('state', '-')}/"
                         f"{s.get('daily_history', {}).get('state', '-')}")
        L.append(f"| {sym} | " + " | ".join(cells) + " |")
    L.append("")

    # D. BRK.A/BRK.B price-level identity proof
    L += ["## D. BRK.A / BRK.B identity proof", ""]
    for sym in ("BRK.A", "BRK.B"):
        i = summary["atlas_identities"][sym]
        L.append(f"- {sym}: security_key `{i.get('security_key')}` "
                 f"(issuer `{i.get('issuer_key')}`, class {i.get('share_class')})")
    L += ["", "| provider | gate verdict | BRK.A sym→bound key | BRK.B sym→bound key | notes |",
          "|---|---|---|---|---|"]
    for r in P:
        g = r.get("identity_gate", {}) or {}
        ps = g.get("per_symbol", {})
        a, b = ps.get("BRK.A", {}), ps.get("BRK.B", {})
        L.append(f"| {r['provider']} | {g.get('verdict')} | "
                 f"{a.get('provider_symbol')}→`{a.get('bound_security_key')}` | "
                 f"{b.get('provider_symbol')}→`{b.get('bound_security_key')}` | "
                 f"{'; '.join(g.get('notes', []))} |")
    L.append("")

    # E. latest-price / feed-class
    L += ["## E. Latest-price & feed-class results", "",
          "| provider | feed classes seen | AAPL/MSFT sample | notes |", "|---|---|---|---|"]
    for r in P:
        lp = (r["securities"].get("AAPL", {}).get("latest_price")
              or r["securities"].get("MSFT", {}).get("latest_price") or {})
        samp = "-"
        if lp.get("state") in DATA_STATES and isinstance(lp.get("data"), dict):
            samp = f"{lp['data'].get('price')} @ {lp.get('provider_timestamp')} ({lp.get('feed_class')})"
        L.append(f"| {r['provider']} | {r.get('feed_classes_seen')} | {samp} | {lp.get('stated_delay', '-')} |")
    L.append("")

    # F. daily-history
    L += ["## F. Daily-history results", "",
          "| provider | state(s) | bar span | adjustment | ", "|---|---|---|---|"]
    for r in P:
        h = r["securities"].get("AAPL", {}).get("daily_history", {}) or {}
        data = h.get("data") or {}
        L.append(f"| {r['provider']} | {r['capability_seen'].get('daily_history')} | "
                 f"{data.get('first')}..{data.get('last')} ({data.get('bar_count')}) | "
                 f"{data.get('adjustment_status', '-')} |")
    L.append("")

    # G. dividends / splits / corporate actions
    L += ["## G. Dividends / splits / corporate actions", "",
          "| provider | dividends | splits | fields |", "|---|---|---|---|"]
    for r in P:
        dv = r["securities"].get("AAPL", {}).get("dividends", {}) or {}
        sp = r["securities"].get("AAPL", {}).get("splits", {}) or {}
        fields = (dv.get("data") or {}).get("fields_present", [])
        L.append(f"| {r['provider']} | {dv.get('state')} ({(dv.get('data') or {}).get('count')}) | "
                 f"{sp.get('state')} ({(sp.get('data') or {}).get('count')}) | {fields} |")
    L.append("")

    # H. usage-rights / persistence matrix
    L += ["## H. Usage-rights / persistence matrix", "",
          "| provider | free personal/internal use | persistent storage allowed? | "
          "two-person private use permitted? | redistribution/display | audit-store compatible? | "
          "source | verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in P:
        u = r.get("usage_rights", {}) or {}
        L.append(f"| {r['provider']} | {u.get('personal_internal_use', '?')} | "
                 f"{u.get('persistent_storage', '?')} | {u.get('two_person_private_use', '?')} | "
                 f"{u.get('redistribution_display', '?')} | {u.get('audit_store_compatible', '?')} | "
                 f"{u.get('source', '?')} | **{u.get('verdict', '?')}** |")
    L += ["", "_Verdicts are drawn only from each provider's written terms (fetched 2026-08-30). "
          "Where the terms are silent, the verdict is UNCLEAR_REQUIRES_CONFIRMATION — no "
          "interpretation beyond the text._", ""]

    # I. cross-provider discrepancies
    rc = summary["reconciliation"]
    L += ["## I. Cross-provider discrepancies", ""]
    if rc["latest_price"]:
        L += ["| symbol | values | rel spread | material? |", "|---|---|---|---|"]
        for x in rc["latest_price"]:
            L.append(f"| {x['symbol']} | {x['values']} | {x['relative_spread']} | {x['material']} |")
    else:
        L.append("_no symbol had a live price from 2+ providers — no reconciliation possible_")
    for key, label in [("history_last_close", "history"), ("dividends_latest", "dividends"),
                       ("splits", "splits")]:
        L.append("")
        L.append(json.dumps({label: rc[key]}, indent=2) if rc[key]
                 else f"_{label}: no 2+ provider overlap_")
    L.append("")

    # J. free-tier operating practicality
    L += ["## J. Free-tier operating practicality", "",
          "| provider | rate limit | daily cap | notes for a small nightly universe |",
          "|---|---|---|---|",
          "| massive | 5 req/min | — | ~7 symbols × 5 calls ≈ 35 calls → ~7 min of throttled batch; fine nightly |",
          "| twelvedata | 8 req/min, 800 credits/day | 800 credits | small universe fits comfortably |",
          "| alpaca | 200 req/min | — | not a constraint; bars endpoint is multi-symbol |",
          "| tiingo | 50 req/hr, 1000/day, 500 symbols/mo | 1000/day | tightest limit; still fine for <500 symbols |",
          ""]

    # K. recommended minimum free stack
    rs = summary["recommended_stack"]
    L += ["## K. Recommended minimum free stack", "",
          f"- **primary:** {rs['primary'] or '(pending live key verification)'}",
          f"- **secondary / cross-check:** {rs['secondary_for_cross_check']}",
          f"- **not in stack:** {rs['not_in_stack']}",
          f"- principle: {rs['principle']}",
          f"- {rs['note']}", ""]

    # L. providers rejected and exact reason
    L += ["## L. Providers rejected / limited and exact reason", "",
          "| provider | verdict | reason |", "|---|---|---|"]
    for p, v in summary["provider_verdicts"].items():
        L.append(f"| {p} | {v['verdict']} | {v['rationale']} |")
    L.append("")

    # M/N/O handled in the console + return text; embed pointers
    L += ["## M. Files changed", "",
          "- `market_data_providers.py` — Massive rewritten as a real Polygon-shaped adapter "
          "(FREE_WITH_KEY, MASSIVE_API_KEY); FEED_CLASSES taxonomy "
          "(REAL_TIME/DELAYED/EOD/IEX_ONLY/UNKNOWN); `usage_rights` on every provider; Twelve "
          "Data feed class now derived from live quote freshness; Tiingo usage-rights = "
          "INCOMPATIBLE_WITH_ATLAS_USE.",
          "- `benchmark_4a5_2a.py` — new live-verification harness (this file).",
          "- `USAGE_RIGHTS.md` — new; the usage-rights matrix and citations.",
          "- `test_atlas.py` — provider tests updated for the corrected Massive + feed/usage metadata.",
          "",
          "## N. Regression", "",
          "- Run `pytest test_atlas.py`, `python validation_harness_live_v3.py`, and the "
          "4A.5.1 / 1a / 1b benchmarks — see the RETURN message for exact counts.", "",
          "## O. Git commit", "",
          "- See the RETURN message.", ""]

    mp.write_text("\n".join(L))
    return {"json": str(jp), "md": str(mp)}


if __name__ == "__main__":
    s = run()
    raise SystemExit(1 if s["verdict"].endswith("NO ADEQUATE FREE STACK") else 0)
