"""Append Addendum 003 to the MCD underwriting record, generated from the committed result artifact (no number is hand-copied). Run once."""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
art = REPO / "atlas_ui/evidence/mcd_r1_r2/MCD_R1_R2_result.json"
doc = REPO / "docs/controlled_live_pilot/CYCLE1_MCD_UNDERWRITING_001.md"
sha = hashlib.sha256(art.read_bytes()).hexdigest()
r = json.loads(art.read_text())
pc = lambda x, d=1: f"{100 * x:+.{d}f}%"
w = r["benchmarks"]["windows"]
full = next(v for k, v in w.items() if k.startswith("full"))
sc = r["scenarios"]["named"]
bear, base, bull, rec = (sc[n] for n in list(sc)[:4])
rv = r["reverse_valuation"]
imp = rv["implied_cagr"]
pe_set = rv["inputs"]["label_ASSUMPTION"]["exit_pe_set"]
refpts = r["scenarios"]["eps_cagr_reference_points"]
t, h, pcx, pf = r["treasury_evaluation"], r["history"], r["price_context"], r["adjustment_convention"]["diagnostics"]
y = t["latest_yields_pct"]
cur = "current (P0 / FY2025 EPS)"
if any(f"[{sha[:16]}" in ln or sha in ln for ln in doc.read_text().splitlines()):
    raise SystemExit("Addendum 003 for this artifact is already in the record")


def win(k, label):
    v = w[k]
    a = v["annualized"]
    return (f"| {label} | {v['start_used']} → {v['end_used']} | {pc(v['mcd_total_return'])} | {pc(v['spy_total_return'])} | {pc(v['cash_3mo_par_proxy'])} | {v['mcd_minus_spy_pts']:+.1f} | "
            f"{v['mcd_minus_cash_pts']:+.1f} | " + (f"{pc(a['mcd'])} / {pc(a['spy'])} / {pc(a['cash'])}" if isinstance(a, dict) else "n/a (<1 year)") + " |")


rows = "\n".join([win("since 2026-10-07 (underwriting reference date)", "since 2026-10-07"), win("1 year", "1 year"), win("3 years", "3 years"), win("5 years", "5 years"),
                  win("10 years", "10 years"), win(next(k for k in w if k.startswith("full")), "full history")])
hk = list(imp)
rvrows = "\n".join(f"| {label} | {pc(imp[k]['hurdle'])} | " + " | ".join(pc(imp[k]["implied_eps_cagr_by_exit_pe"][c]) for c in (cur, "observed minimum", "observed median")) + " |"
                   for k, label in zip(hk, ("Cash (3-month par yield)", "5-year Treasury", "10-year Treasury", "SPY, trailing 10-year total return (history)", "SPY, total return since 2006-12-13 (history)")))
grid = r["scenarios"]["grid_irr"]
gcols = list(next(iter(grid.values())))
gridrows = "\n".join(f"| {g} | " + " | ".join(pc(grid[g][c]) for c in gcols) + " |" for g in grid)
dv = r["dividend_cross_check"]["years"]
max08 = max(abs(v["difference"]) / v["sec_declared"] for k, v in dv.items() if int(k) >= 2008)
d07 = abs(dv["2007"]["difference"]) / dv["2007"]["sec_declared"]
gap = lambda k: 100 * abs(pf[k]["candidate_price_return"] - pf[k]["unadjusted_total_return_with_reinvested_dividends"])
spy_note = f"SPY 10y {pc(pf['SPY_10y']['candidate_price_return'], 0)} vs {pc(pf['SPY_10y']['unadjusted_total_return_with_reinvested_dividends'], 0)}"
txt = f'''

---

## Addendum 003 — R1/R2 research run: reverse valuation, reference cases and benchmark comparison (2026-10-29; append-only)

*What this is.* New, measured evidence on the questions this record left open (a certified price; matched SPY and Treasury/cash comparisons; reverse valuation). It is **descriptive research, not a capital verdict**: MCD stays **PARKED until 2026-11-04**, no stance was written, no allocation is implied, and nothing here promotes it. Facts, market data, assumptions and outputs are labelled; gaps are listed.
Inputs and arithmetic: `atlas_ui/evidence/mcd_r1_r2/` (`fetch_inputs.py`, `run_mcd_r1_r2.py`, the result `MCD_R1_R2_result.json` sha256 `{sha}`, the retained U.S. Treasury CSVs); formulas: `atlas_ui/valuation.py` (unit-tested). Recorded in the candidate ledger as seven evidence entries, five open questions, one linked observation and assessment v2 (`DRAFT_BY_RECORDER`).

### 1. Data integrity (checked before any conclusion)
| Check | Result |
|---|---|
| Provider close on 2026-10-28 vs the Gate B bind | ${pcx['close_at_cutoff']:.2f} = $250.50 (equal). The provider's 2026-10-29 bar is an unfinished intraday bar and is excluded. |
| Adjustment convention (prevents double counting) | `adjust=all` is a **dividend-adjusted** series, `adjust=none` raw closes. The adjusted series' return equals raw-close return with reinvested dividends to within {max(gap(k) for k in pf):.1f} percentage points in every window tested (MCD 10y {pc(pf['MCD_10y']['candidate_price_return'], 0)} vs {pc(pf['MCD_10y']['unadjusted_total_return_with_reinvested_dividends'], 0)}; {spy_note}). **Dividends are never added to the adjusted series** (doing so would overstate MCD's 5-year return by {100 * pf['MCD_5y']['double_counting_error_if_dividends_were_added_to_the_candidate']:.0f} points). |
| Dividends endpoint | **Not on TwelveData's free plan (HTTP 403)**; the earlier benchmark note saying otherwise is wrong. Dividends were inferred from the adjusted/unadjusted ratio and tie to the SEC's declared per-share dividends within {100 * max08:.1f}% in every fiscal year 2008–2025 ({100 * d07:.1f}% in FY2007, the first year). |
| SPY | Same provider method; verified structurally, **not** against a primary distribution record (gap). |
| Treasury | The keyless official CSV reproduces **every** hand-attested value in this record and the RPM record (3-month, 2-year, 10-year on 2026-10-06 and 2026-10-08); latest observation 2026-10-28 (0 days stale); no non-numeric cells. |
| Year-end trailing P/E | Recomputed from provider closes and SEC EPS: 2021–2025 = 26.7x, 31.6x, 25.6x, 25.5x, 25.6x, identical to the table in §3 above (which used uncertified Yahoo closes). |
| The earlier price | The 2026-10-07 reference price was $232.24 (uncertified); the provider's close is **$230.88**. The earlier observation's “+7.9%” becomes **{pc(pcx['price_change_since_2026-10-07'])}** on certified prices. |

### 2. Measured: MCD against SPY and cash (total return; same dates; history, not a forecast)
| Window | Dates used | MCD | SPY | Cash (3-mo par) | MCD−SPY (pts) | MCD−cash (pts) | Annualized MCD / SPY / cash |
|---|---|---|---|---|---|---|---|
{rows}

MCD lagged SPY in every window from one to ten years (one year: MCD {pc(w['1 year']['mcd_total_return'])} vs SPY {pc(w['1 year']['spy_total_return'])}) and trailed cash over one, three and five years; over the full common history it led SPY ({pc(full['annualized']['mcd'])} vs {pc(full['annualized']['spy'])} a year). Price is {pc(pcx['below_52w_high'])} from the 52-week high close (${pcx['52w_high_close']['close']:.2f}, {pcx['52w_high_close']['date']}); worst peak-to-trough in the last year {pc(pcx['max_drawdown_last_year'])}. Relative performance is regime-dependent; this is not evidence of an edge in either direction.

### 3. Reverse valuation: what the price requires (INFERENCE; arithmetic on stated inputs)
Inputs. FACT: price ${pcx['close_at_cutoff']:.2f}, FY2025 diluted EPS $11.95 (SEC 10-K), FCF/share ${rv['inputs']['label_FACT']['fcf_per_share_fy2025']:.2f}. MARKET DATA: dividend run-rate $7.44/yr (underwriting record; inferred tie-out ${rv['inputs']['label_MARKET_DATA']['dps_run_rate_latest_quarter_x4_inferred_tie_out']:.2f}). ASSUMPTION: exit on 2030-12-31, dividends scale with EPS. Constant EPS growth from FY2025 needed to earn each hurdle, by exit multiple:

| Hurdle | Hurdle rate | Multiple unchanged ({pe_set[cur]:.1f}x) | Observed minimum ({pe_set['observed minimum']:.1f}x) | 12-year median ({pe_set['observed median']:.1f}x) |
|---|---|---|---|---|
{rvrows}

Reading: with the multiple unchanged the price needs only about {pc(imp[hk[0]]['implied_eps_cagr_by_exit_pe'][cur])} to {pc(imp[hk[2]]['implied_eps_cagr_by_exit_pe'][cur])} a year of EPS growth to match cash and Treasuries, about {pc(imp[hk[4]]['implied_eps_cagr_by_exit_pe'][cur])} to match SPY's full-history return and about {pc(imp[hk[3]]['implied_eps_cagr_by_exit_pe'][cur])} to match SPY's last ten years. EPS growth was {pc(refpts['latest_2y_FY2023_FY2025'])} a year over FY2023–FY2025, the median observed five-year window is {pc(refpts['five_year_windows']['median'])} (range {pc(refpts['five_year_windows']['min'])} to {pc(refpts['five_year_windows']['max'])}) and the ten-year CAGR is {pc(refpts['ten_year_FY2015_FY2025'])}. Free-cash-flow view: at required returns of 8% / 9% / 10% the price implies perpetual FCF growth of {pc(rv['perpetual_growth_view']['required_return_8pct'])} / {pc(rv['perpetual_growth_view']['required_return_9pct'])} / {pc(rv['perpetual_growth_view']['required_return_10pct'])}. (A negative number under a higher exit multiple means the multiple alone would carry the return.)

### 4. Reference cases (NOT forecasts, NOT probabilities; no expected value)
Each input is an observed reference point from MCD's own history; BASE is the middle reference case, **not the likeliest outcome**. Annual IRR from ${pcx['close_at_cutoff']:.2f} to 2030-12-31.

| Case | EPS growth | Exit multiple | FY2030 EPS | Exit price | IRR | vs cash ({y['3 Mo']['yield']}%) | vs SPY 10y history ({pc(w['10 years']['annualized']['spy'])}) | vs SPY full history ({pc(full['annualized']['spy'])}) |
|---|---|---|---|---|---|---|---|---|
| BEAR: latest 2-year growth persists; lowest observed year-end P/E | {pc(bear['eps_cagr'])} | {bear['exit_pe']:.1f}x | ${bear['eps_fy2030']:.2f} | ${bear['exit_price']:.0f} | **{pc(bear['irr'])}** | {bear['minus_cash_pts']:+.1f} pts | {bear['minus_spy_10y_history_pts']:+.1f} pts | {bear['minus_spy_full_history_pts']:+.1f} pts |
| BASE: only growth normalizes (median 5-year window); multiple unchanged | {pc(base['eps_cagr'])} | {base['exit_pe']:.1f}x | ${base['eps_fy2030']:.2f} | ${base['exit_price']:.0f} | **{pc(base['irr'])}** | {base['minus_cash_pts']:+.1f} pts | {base['minus_spy_10y_history_pts']:+.1f} pts | {base['minus_spy_full_history_pts']:+.1f} pts |
| BULL: growth normalizes and the multiple reverts to the 12-year median | {pc(bull['eps_cagr'])} | {bull['exit_pe']:.1f}x | ${bull['eps_fy2030']:.2f} | ${bull['exit_price']:.0f} | **{pc(bull['irr'])}** | {bull['minus_cash_pts']:+.1f} pts | {bull['minus_spy_10y_history_pts']:+.1f} pts | {bull['minus_spy_full_history_pts']:+.1f} pts |

**What changed since this record's own base case (5% EPS growth, 19x exit, an Atlas judgment):** at the 2026-10-07 close the same assumptions earn {pc(rec['irr_at_2026-10-07_close_230.88'])}; at the 2026-10-28 price they earn {pc(rec['irr_at_2026-10-28_price_250.50'])}. The +8.5% move alone removed {100 * (rec['irr_at_2026-10-07_close_230.88'] - rec['irr_at_2026-10-28_price_250.50']):.1f} points of prospective return.

IRR grid (rows: EPS growth from FY2025; columns: exit P/E):

| EPS growth | {" | ".join(gcols)} |
|---|{"---|" * len(gcols)}
{gridrows}

### 5. What this does and does not establish
- **Established (measured):** the price needs little growth to beat cash and Treasuries but a great deal to beat SPY's recent record; the bear case ({pc(bear['irr'])}) is below cash ({y['3 Mo']['yield']}%); the spread between cases (about {100 * (bull['irr'] - bear['irr']):.0f} points) is mostly the growth regime (recent {pc(refpts['latest_2y_FY2023_FY2025'])} vs long-run {pc(refpts['five_year_windows']['median'])}) plus the multiple; the Oct-7→Oct-28 rally made every case less attractive.
- **Not established:** that the long-run growth regime returns (the only evidence for it is management's Investor-Day claims, already recorded as MANAGEMENT CLAIM), any advantage over SPY, or any probability. **No edge is demonstrated.** The question is now sharply testable on **2026-11-04** (Q3 results; the pre-registered thresholds above still apply) and, later, by the retained reference cases (R4: compare outcomes with these recorded IRRs, SPY and cash, assumptions unchanged).
- **Gaps (also recorded as open questions):** no forward EPS, guidance schedule or partnering phasing is evidenced; scenarios start from FY2025 EPS ($11.95), below the TTM $12.31 in §3; dividends inferred (the paid endpoint is unavailable); SPY adjustment verified structurally only; cash is a par-yield proxy, not a fund return; taxes and costs not modeled.

### 6. Treasury source evaluation (R2.1): evaluated, NOT integrated
Source: U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates, CSV (home.treasury.gov), keyless, one read-only GET per year; {t['rows']} daily rows {t['first_date']} → {t['last_date']}; PRIMARY if integrated. Findings: complete and numeric; reproduces all six hand-attested values; fresh to the cutoff; the only daily moves over 50 bp in the 3-month or 10-year series are six, all in 2007–2009 (stress periods; real, not data errors). **Schema drift:** the CSV gained columns over time (11 in 2015, 14 from 2025), so a parser must select columns by name. **Not verified by software:** the site's terms of use.
Governance approvals needed **before any integration** (none is assumed): (1) the human's explicit approval of a new data source (standing rule: no new provider without authorization); (2) confirmation of the terms of use; (3) because a funded Stage 8 requires a human re-attested Treasury reference (frozen-control change 001), an automated source may only *inform or pre-fill* that attestation unless a frozen-control change record is separately authorized; (4) a staleness policy (a last observation older than N days is UNKNOWN); (5) a retention decision (public data; the CSVs are retained here with SHA-256). Until then the Treasury inputs in this addendum are an evaluation artifact, not a Stock Atlas data feed.

**Capital status: NO REAL PORTFOLIO ACTION.**
'''
doc.write_text(doc.read_text().rstrip("\n") + txt)
print(len(txt.splitlines()), "lines appended; artifact", sha[:16])
