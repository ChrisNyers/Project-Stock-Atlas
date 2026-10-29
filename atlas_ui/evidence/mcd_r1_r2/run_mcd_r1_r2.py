"""MCD research run (R1 reverse valuation + scenarios, R2 SPY and Treasury/cash benchmarks), from the cached inputs.

    .venv/bin/python atlas_ui/evidence/mcd_r1_r2/fetch_inputs.py        # once (network; needs TWELVEDATA_API_KEY and SEC_USER_AGENT in .env)
    .venv/bin/python atlas_ui/evidence/mcd_r1_r2/run_mcd_r1_r2.py       # offline; writes MCD_R1_R2_result.json next to this file

Every number is tagged FACT (primary source), MARKET DATA (provider, secondary), ASSUMPTION or OUTPUT (arithmetic on the others), and gaps are listed.
Scenarios are mechanical: their inputs are the OBSERVED minimum / median / maximum of the company's own history. They are not forecasts, not
probabilities, not a recommendation. The result stores derived numbers and input hashes only (no raw provider series).
"""
import csv
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from atlas_ui import research, valuation as V  # noqa: E402

HERE = Path(__file__).resolve().parent
CACHE = REPO / "atlas_cache" / "mcd_r1_r2"
CUTOFF = date(2026, 10, 28)             # latest COMPLETED XNYS session at the Gate B bind; the provider's 2026-10-29 bar is an unfinished intraday bar
EXIT = date(2030, 12, 31)               # exit date used by every scenario (FY2030 EPS x exit multiple)
BASE_FY = 2025
CIK, KEY = "0000063908", "SEC-CIK:0000063908:MCD"
UNDERWRITING_REFERENCE = {"date": "2026-10-06", "3 Mo": 4.21, "2 Yr": 4.79, "10 Yr": 5.27}      # as written in CYCLE1_MCD_UNDERWRITING_001 §3 (human-attested then)
RPM_REFERENCE = {"date": "2026-10-08", "3 Mo": 4.23, "2 Yr": 4.75, "10 Yr": 5.22}               # as written in CYCLE2_RPM_UNDERWRITING_001


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def series(name: str) -> dict[date, float]:
    js = json.loads((CACHE / f"{name}.json").read_text())
    return {date.fromisoformat(v["datetime"]): float(v["close"]) for v in js["values"] if date.fromisoformat(v["datetime"]) <= CUTOFF}


def treasury() -> tuple[dict[str, list[tuple[date, float]]], dict]:
    cols: dict[str, list[tuple[date, float]]] = {}
    schema, rows, bad = {}, 0, []
    for f in sorted(HERE.glob("treasury_par_yield_curve_*.csv")):
        rd = csv.DictReader(f.read_text().splitlines())
        schema[f.stem[-4:]] = rd.fieldnames[1:]
        for r in rd:
            m, d, y = r["Date"].split("/")
            dt = date(int(y), int(m), int(d))
            rows += 1
            for c, v in r.items():
                if c == "Date":
                    continue
                if v in ("", None):
                    continue
                try:
                    cols.setdefault(c, []).append((dt, float(v)))
                except ValueError:
                    bad.append((str(dt), c, v))
    for c in cols:
        cols[c].sort()
    return cols, {"rows": rows, "non_numeric": bad, "schema_by_year": schema}


def main():
    now = datetime.now(timezone.utc)
    out: dict = {"generated_at": now.isoformat(timespec="seconds"), "cutoff_session": CUTOFF.isoformat(), "labels": "FACT | MARKET DATA | ASSUMPTION | OUTPUT | GAP"}
    gaps: list[str] = []

    # ---------------------------------------------------------------- inputs and their hashes
    out["inputs"] = {"twelvedata_cached_responses_sha256": {p.name: sha(p) for p in sorted(CACHE.glob("*.json"))},
                     "treasury_csv_sha256": {p.name: sha(p) for p in sorted(HERE.glob("treasury_par_yield_curve_*.csv"))},
                     "note": "TwelveData raw responses stay in the git-ignored atlas_cache/ (provider storage terms); only hashes and derived numbers are committed."}
    mcd_u, mcd_a, spy_u, spy_a = series("MCD_ts_none"), series("MCD_ts_all"), series("SPY_ts_none"), series("SPY_ts_all")
    out["market_data"] = {"grade": "SECONDARY (provider, independent exchange calendar fixes the session)", "mcd_close_at_cutoff": mcd_u[CUTOFF],
                          "gate_b_bound_price_2026-10-28": 250.5, "equals_gate_b_bind": abs(mcd_u[CUTOFF] - 250.5) < 1e-6,
                          "mcd_first_bar": min(mcd_u).isoformat(), "spy_first_bar": min(spy_u).isoformat(),
                          "excluded": "the provider's 2026-10-29 bar is an unfinished intraday bar (partial volume) and is not used"}

    # ---------------------------------------------------------------- adjustment convention (prevents double counting)
    divs_mcd, divs_spy = V.infer_dividends(mcd_u, mcd_a), V.infer_dividends(spy_u, spy_a)
    conv = {}
    for nm, u, a, dv in (("MCD", mcd_u, mcd_a, divs_mcd), ("SPY", spy_u, spy_a, divs_spy)):
        for yrs in (1, 5, 10):
            s = date(CUTOFF.year - yrs, CUTOFF.month, CUTOFF.day)
            d = V.adjustment_diagnostic(u, a, dv, s, CUTOFF, tolerance=0.01)
            conv[f"{nm}_{yrs}y"] = {k: d[k] for k in ("verdict", "candidate_price_return", "unadjusted_price_return", "unadjusted_total_return_with_reinvested_dividends",
                                                       "double_counting_error_if_dividends_were_added_to_the_candidate")}
    out["adjustment_convention"] = {
        "finding": "TwelveData adjust=all returns a DIVIDEND-ADJUSTED series (and adjust=none the raw closes). Total return = the adjusted series' price return; never add dividends to it.",
        "dividends_endpoint": "NOT available on the free plan (HTTP 403); dividends are inferred from the adjusted/unadjusted ratio steps and checked against the SEC's per-share dividend facts below.",
        "diagnostics": conv, "dividend_events_inferred": {"MCD": len(divs_mcd), "SPY": len(divs_spy)}}

    # ---------------------------------------------------------------- SEC facts: EPS history, dividends per share (primary)
    facts = json.loads((CACHE / "MCD_companyfacts.json").read_text())
    out["inputs"]["sec_company_facts_sha256"] = sha(CACHE / "MCD_companyfacts.json")
    snap = research.build_snapshot(facts, ticker="MCD", security_key=KEY, cik=CIK, decision_time=now, n_years=12)
    eps, eps_prov = {}, {}
    for end, p in sorted(snap["periods"].items()):
        f = p.get("diluted_eps") or {}
        if f.get("value") is not None:
            eps[int(end[:4])] = float(f["value"])
            eps_prov[int(end[:4])] = {"period_end": end, "eps": float(f["value"]), "accession": f.get("accession"), "filed": f.get("filed")}
    gaps += [g for g in snap["gaps"] if "diluted" in g.lower() or "eps" in g.lower()]
    sec_dps = {}
    for fct in (((facts.get("facts") or {}).get("us-gaap") or {}).get("CommonStockDividendsPerShareDeclared", {}).get("units", {}).get("USD/shares", [])):
        if str(fct.get("form", "")).startswith("10-K") and fct.get("fp") == "FY" and fct.get("start") and fct.get("end"):
            if 350 <= (date.fromisoformat(fct["end"]) - date.fromisoformat(fct["start"])).days <= 380:
                sec_dps[int(fct["end"][:4])] = float(fct["val"])
    out["facts"] = {"grade": "PRIMARY (SEC XBRL company facts; annual 10-K diluted EPS, approved concept, explicit period)", "eps_by_fiscal_year": eps_prov,
                    "dividends_per_share_declared_by_fiscal_year": sec_dps, "fcf_fy2025": snap["derived_inference"][f"{BASE_FY}-12-31"].get("free_cash_flow"),
                    "weighted_diluted_shares_fy2025_millions": snap["periods"][f"{BASE_FY}-12-31"]["weighted_average_diluted_shares"]["value"] if "weighted_average_diluted_shares" in snap["periods"][f"{BASE_FY}-12-31"] else None}
    # check: inferred dividends by calendar year vs the SEC's declared per-share dividends
    by_year = {}
    for d, amt in divs_mcd.items():
        by_year[d.year] = by_year.get(d.year, 0.0) + amt
    out["dividend_cross_check"] = {"grade": "inferred (secondary) vs declared (primary)",
                                   "years": {str(y): {"inferred_from_ratio_steps": round(by_year.get(y, 0.0), 3), "sec_declared": sec_dps.get(y),
                                                      "difference": (round(by_year.get(y, 0.0) - sec_dps[y], 3) if y in sec_dps else None)} for y in sorted(set(by_year) & set(sec_dps))}}

    # ---------------------------------------------------------------- Treasury (keyless primary source) evaluation + yields
    cols, tq = treasury()
    at = lambda c, d: V.on_or_before({x: y for x, y in cols[c]}, d)
    yields_cut = {c: at(c, CUTOFF) for c in ("3 Mo", "2 Yr", "5 Yr", "10 Yr")}
    repro = {}
    for ref in (UNDERWRITING_REFERENCE, RPM_REFERENCE):
        d = date.fromisoformat(ref["date"])
        got = {c: dict(cols[c]).get(d) for c in ("3 Mo", "2 Yr", "10 Yr")}
        repro[ref["date"]] = {"recorded_in_underwriting": {c: ref[c] for c in ("3 Mo", "2 Yr", "10 Yr")}, "treasury_csv": got,
                              "all_match": all(got[c] == ref[c] for c in got)}
    allrows = sorted({d for c in cols for d, _ in cols[c]})
    jumps = [(str(b), c, round(dict(cols[c])[b] - dict(cols[c])[a], 2)) for c in ("3 Mo", "10 Yr") for a, b in zip(sorted(dict(cols[c])), sorted(dict(cols[c]))[1:]) if abs(dict(cols[c])[b] - dict(cols[c])[a]) > 0.5]
    out["treasury_evaluation"] = {
        "source": "U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates, CSV download (home.treasury.gov); keyless, read-only, one GET per calendar year",
        "grade_if_integrated": "PRIMARY", "years_retained": sorted(tq["schema_by_year"]), "rows": tq["rows"], "first_date": str(allrows[0]), "last_date": str(allrows[-1]),
        "days_between_last_observation_and_cutoff": (CUTOFF - allrows[-1]).days, "non_numeric_cells": tq["non_numeric"],
        "daily_moves_over_50bp_in_3Mo_or_10Yr": jumps[:10],
        "schema_changes": {y: tq["schema_by_year"][y] for y in sorted(tq["schema_by_year"]) if y in ("2015", "2018", "2022", "2025", "2026")},
        "reproduces_values_previously_recorded_by_the_human_attestation": repro,
        "latest_yields_pct": {c: {"date": str(v[0]), "yield": v[1]} for c, v in yields_cut.items()}}

    # ---------------------------------------------------------------- benchmark comparison (matched windows)
    stance_date = date(2026, 10, 7)
    wins = {"since 2026-10-07 (underwriting reference date)": stance_date, "1 year": date(CUTOFF.year - 1, 10, 28), "3 years": date(CUTOFF.year - 3, 10, 28),
            "5 years": date(CUTOFF.year - 5, 10, 28), "10 years": date(CUTOFF.year - 10, 10, 28), "full common history (since " + min(mcd_u).isoformat() + ")": min(mcd_u)}
    bench = {}
    for label, s in wins.items():
        m, sp = V.total_return(mcd_a, {}, s, CUTOFF), V.total_return(spy_a, {}, s, CUTOFF)           # adjusted series: dividends already inside; none added
        mp = V.total_return(mcd_u, {}, s, CUTOFF)
        cash = V.cash_accrual(cols["3 Mo"], date.fromisoformat(m["start_used"]), CUTOFF) if m else None      # the SAME start date as the price series
        if not (m and sp and cash):
            bench[label] = {"status": "UNAVAILABLE: window not covered by every series (nothing extrapolated)"}
            continue
        ann = lambda x: x["annualized_total_return"] if "annualized_total_return" in x else x["annualized"]
        bench[label] = {"start_used": m["start_used"], "end_used": m["end_used"], "days": m["days"],
                        "mcd_price_return": mp["price_return"], "mcd_total_return": m["total_return"], "spy_total_return": sp["total_return"], "cash_3mo_par_proxy": cash["total_return"],
                        "mcd_minus_spy_pts": 100 * (m["total_return"] - sp["total_return"]), "mcd_minus_cash_pts": 100 * (m["total_return"] - cash["total_return"]),
                        "annualized": {"mcd": ann(m), "spy": ann(sp), "cash": cash["annualized"]} if m["days"] >= 365 else "not annualized (window under one year)"}
    out["benchmarks"] = {"method": "TOTAL return = the dividend-adjusted (adjust=all) series' price return, same dates for every series; SPY and MCD from one provider; cash = 3-month par yield compounded (proxy, not a T-bill fund)",
                         "grade": "SECONDARY (market data); cash proxy PRIMARY (Treasury)", "windows": bench}
    ann_of = lambda w, k: bench[w]["annualized"][k] if isinstance(bench.get(w, {}).get("annualized"), dict) else None
    spy10, spy5 = ann_of("10 years", "spy"), ann_of("5 years", "spy")
    full_key = next(k for k in bench if k.startswith("full common history"))
    spy_full = ann_of(full_key, "spy")

    # ---------------------------------------------------------------- price context
    last_year = [(d, c) for d, c in sorted(mcd_u.items()) if d > date(CUTOFF.year - 1, CUTOFF.month, CUTOFF.day)]
    hi = max(last_year, key=lambda x: x[1])
    peak, mdd = 0.0, 0.0
    for _, c in last_year:
        peak = max(peak, c)
        mdd = min(mdd, c / peak - 1.0)
    out["price_context"] = {"close_at_cutoff": mcd_u[CUTOFF], "52w_high_close": {"date": hi[0].isoformat(), "close": hi[1]}, "below_52w_high": mcd_u[CUTOFF] / hi[1] - 1.0, "max_drawdown_last_year": mdd,
                            "close_2026-10-07": mcd_u.get(date(2026, 10, 7)), "price_change_since_2026-10-07": mcd_u[CUTOFF] / mcd_u[date(2026, 10, 7)] - 1.0,
                            "earlier_observation_used_uncertified_yahoo_close_232_24": "the provider's 2026-10-07 close differs; see price_change_since_2026-10-07"}

    # ---------------------------------------------------------------- history: year-end trailing P/E and EPS growth
    fye = {}
    for y in sorted(eps):
        px = V.on_or_before(mcd_u, date(y, 12, 31))
        if px and px[0] >= date(y, 12, 24):
            fye[y] = {"fiscal_year_end_close": px[1], "close_date": px[0].isoformat(), "eps": eps[y], "trailing_pe": px[1] / eps[y]}
    pes = [v["trailing_pe"] for v in fye.values()]
    c3, c5 = V.rolling_cagrs(eps, 3), V.rolling_cagrs(eps, 5)
    out["history"] = {"grade": "PRIMARY EPS (SEC) / SECONDARY price", "year_end_trailing_pe": fye, "pe_summary": V.quantile_summary(pes),
                      "eps_cagr_3y_by_end_year": c3, "eps_cagr_5y_by_end_year": c5, "eps_cagr_3y_summary": V.quantile_summary(list(c3.values())),
                      "eps_cagr_5y_summary": V.quantile_summary(list(c5.values())),
                      "note_underwriting_record_year_end_pe_2021_2025": "26.7x, 31.6x, 25.6x, 25.5x, 25.6x (SEC EPS / uncertified Yahoo closes) — compare with trailing_pe above"}

    # ---------------------------------------------------------------- reverse valuation
    p0, eps0 = mcd_u[CUTOFF], eps[BASE_FY]
    ds = sorted(divs_mcd)
    last_q = divs_mcd[ds[-1]]
    ttm = sum(a for d, a in divs_mcd.items() if d > date(CUTOFF.year - 1, CUTOFF.month, CUTOFF.day) and d <= CUTOFF)
    dps_inferred = round(last_q * 4, 2)
    dps_run = 7.44        # annualized current dividend, $1.86 x 4, from the underwriting record (primary 10-Q/8-K); the inferred run-rate is the tie-out

    base = dict(price0=p0, as_of=CUTOFF, eps_base=eps0, base_fy=BASE_FY, exit_date=EXIT, dps_run_rate=dps_run)
    fcf0, sh = out["facts"]["fcf_fy2025"], out["facts"]["weighted_diluted_shares_fy2025_millions"]
    fcf_ps = fcf0 / (sh * 1e6) if fcf0 and sh else None
    hurdles = {"cash (3-month par yield, 2026-10-28)": yields_cut["3 Mo"][1] / 100, "5-year Treasury par yield, 2026-10-28": yields_cut["5 Yr"][1] / 100,
               "10-year Treasury par yield, 2026-10-28": yields_cut["10 Yr"][1] / 100}
    if spy10 is not None:
        hurdles["SPY trailing 10-year annualized total return (HISTORY, not a forecast)"] = spy10
    if spy_full is not None:
        hurdles["SPY annualized total return since " + min(spy_u).isoformat() + " (HISTORY, not a forecast)"] = spy_full
    pe_set = {"current (P0 / FY2025 EPS)": p0 / eps0, "observed minimum": min(pes), "observed median": V.quantile_summary(pes)["median"], "observed maximum": max(pes)}
    rv = {}
    for hn, h in hurdles.items():
        rv[hn] = {"hurdle": h, "implied_eps_cagr_by_exit_pe": {pn: V.implied_cagr(target_irr=h, exit_pe=pv, **base) for pn, pv in pe_set.items()}}
    out["reverse_valuation"] = {
        "question": "At the bound price, what EPS growth (FY2025 -> FY2030, constant) is needed to earn each hurdle, for each exit multiple?",
        "inputs": {"label_FACT": {"price_p0_2026-10-28": p0, "eps_fy2025_diluted_sec": eps0, "fcf_per_share_fy2025": fcf_ps}, "label_MARKET_DATA": {"dps_run_rate_used_from_underwriting_record_primary": dps_run, "dps_run_rate_latest_quarter_x4_inferred_tie_out": dps_inferred, "dps_ttm_inferred": round(ttm, 3), "underwriting_record_run_rate": 7.44},
                   "label_ASSUMPTION": {"exit_date": EXIT.isoformat(), "constant_payout_ratio": "DPS scales with EPS", "exit_pe_set": pe_set}},
        "implied_cagr": rv,
        "perpetual_growth_view": {f"required_return_{int(r * 100)}pct": V.implied_perpetual_growth(fcf_per_share=fcf_ps, price=p0, required_return=r) for r in (0.08, 0.09, 0.10)} if fcf_ps else None}

    # ---------------------------------------------------------------- reference scenarios (each input is an OBSERVED reference point, labelled; none is a forecast)
    g_recent = (eps[BASE_FY] / eps[BASE_FY - 2]) ** 0.5 - 1.0                      # FY2023 -> FY2025
    g5 = V.quantile_summary(list(c5.values()))
    pe_now, pe_min, pe_med = p0 / eps0, min(pes), V.quantile_summary(pes)["median"]
    cash_h, ust5_h = hurdles["cash (3-month par yield, 2026-10-28)"], hurdles["5-year Treasury par yield, 2026-10-28"]
    refs = {
        "BEAR — the recent regime persists: EPS growth = the latest 2-year CAGR (FY2023-FY2025); exit multiple = the lowest year-end P/E observed in 12 years": (g_recent, pe_min),
        "BASE — only growth normalizes: EPS growth = the median of the observed 5-year EPS CAGR windows; exit multiple = today's multiple, unchanged": (g5["median"], pe_now),
        "BULL — growth normalizes AND the multiple reverts: median 5-year EPS growth; exit multiple = the 12-year median year-end P/E": (g5["median"], pe_med)}
    sc = {}
    for nm, (g, pe) in refs.items():
        irr = V.scenario_irr(cagr=g, exit_pe=pe, **base)
        sc[nm] = {"eps_cagr": g, "exit_pe": pe, "irr": irr, "eps_fy2030": eps0 * (1 + g) ** (EXIT.year - BASE_FY), "exit_price": pe * eps0 * (1 + g) ** (EXIT.year - BASE_FY),
                  "minus_cash_pts": 100 * (irr - cash_h), "minus_5y_treasury_pts": 100 * (irr - ust5_h),
                  "minus_spy_10y_history_pts": (100 * (irr - spy10)) if spy10 is not None else None, "minus_spy_full_history_pts": (100 * (irr - spy_full)) if spy_full is not None else None}
    # the record's own base case (a 2026-10-07 judgment: 5% EPS growth, 19x exit), recomputed at today's certified price: what the +8.5% move did to it
    rec_now = V.scenario_irr(cagr=0.05, exit_pe=19.0, **base)
    rec_then = V.scenario_irr(**{**base, "price0": 230.88, "as_of": date(2026, 10, 7)}, cagr=0.05, exit_pe=19.0)
    sc["REFERENCE — the 2026-10-07 underwriting base case (5% EPS growth, 19x exit; an Atlas judgment, not history)"] = {
        "eps_cagr": 0.05, "exit_pe": 19.0, "irr_at_2026-10-28_price_250.50": rec_now, "irr_at_2026-10-07_close_230.88": rec_then,
        "note": "same assumptions, same exit date; only the entry price moved. (The record itself reported about 8.9% from a different horizon and an uncertified $232.24.)"}
    grid_g, grid_pe = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10], [16.0, 18.0, 20.0, 22.0, 24.0, 26.0]
    out["scenarios"] = {"construction": "each case takes its two inputs from a named OBSERVED reference point (the company's own recent and long-run EPS growth; its own year-end P/E range), because the key uncertainty is which growth regime applies. NOT forecasts, NOT probabilities, no expected value; read the grid. BASE is the middle reference case, NOT the most likely outcome.",
                        "eps_cagr_reference_points": {"latest_2y_FY2023_FY2025": g_recent, "five_year_windows": g5, "ten_year_FY2015_FY2025": (eps[2025] / eps[2015]) ** 0.1 - 1.0 if 2015 in eps else None},
                        "named": sc, "grid_irr": {f"{int(g * 100)}%": {f"{int(pe)}x": V.scenario_irr(cagr=g, exit_pe=pe, **base) for pe in grid_pe} for g in grid_g},
                        "exit_date": EXIT.isoformat(), "base_eps_fy2025": eps0}

    gaps += ["Dividend amounts are inferred from the provider's adjusted/unadjusted ratio (the /dividends endpoint needs a paid plan); checked against SEC declared per-share dividends only for fiscal years where that fact exists.",
             "SPY has no primary dividend record in this repository: its adjustment is verified structurally (the same provider method as MCD, which ties to SEC), not against a State Street distribution record.",
             "No forward EPS, consensus, guidance schedule or NEXT partnering phasing is evidenced: the scenarios use the company's own past growth, which is not a forecast; the 2026-11-04 Q3 results are not yet available.",
             "TTM EPS ($12.31) in the underwriting record comes from a 10-Q and is not re-derived here; the scenarios start from the FY2025 annual XBRL EPS ($11.95), which is lower.",
             "Cash is a 3-month par-yield proxy (bond-equivalent, compounded by days/365), not a T-bill fund or money-market return; Treasury yields are par yields, not total returns of Treasury securities.",
             "A buyer's taxes, transaction costs and the dividend's tax treatment are not modeled."]
    out["gaps"] = gaps
    f = HERE / "MCD_R1_R2_result.json"
    f.write_text(json.dumps(out, indent=1, default=str))
    print(f"wrote {f.relative_to(REPO)} sha256={sha(f)}")
    return out


if __name__ == "__main__":
    main()
