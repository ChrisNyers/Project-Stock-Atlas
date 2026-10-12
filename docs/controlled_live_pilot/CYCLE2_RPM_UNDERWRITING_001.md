# Controlled Live Pilot — Cycle 2 — RPM Underwriting 001

> **NO REAL PORTFOLIO ACTION. NOT STAGE 7. NOT STAGE 8. NO SIZING.** Research record only.
> The frozen pre-Atlas stance (`CYCLE2_RPM_PRE_ATLAS_STANCE_001.md`, `1cd8270`) is untouched and is used only as the counterfactual. Cycle 1 (MCD) remains parked until 2026-11-04.

| | |
|---|---|
| Date | 2026-10-12 |
| Candidate | RPM International Inc. (RPM), CIK 0000110621, NYSE (XNYS); fiscal year ends May 31 — human-selected |
| Purpose | Determine whether RPM deserves further capital consideration and whether Atlas materially changes the pre-Atlas view (not a BUY recommendation) |
| Disposition | **`CONTINUE UNDERWRITING FOR SPECIFIC EVIDENCE`** |
| Price basis | **UNCERTIFIED** — `TWELVEDATA_API_KEY` absent. Prices/rates are Yahoo Finance and FRED/Treasury series, research context only, not a Stage 7 bind |

## 0. Evidence labels

**PRIMARY (all company facts):** Form 10-K FY2026 (FYE 2026-05-31; acc. 0001193125-26-312142); Form 10-Q Q1 FY2027 (acc. 0001193125-26-415321, filed 2026-10-06); 8-K earnings releases Ex. 99.1/99.2 for Q1 FY27 (2026-10-06), Q4 FY26 (2026-07-22), Q3 FY26 (2026-04-08), Q2 FY26 (2026-01-08), Q1 FY26 (2025-10-01), plus FY25 and FY23 Q4 releases (adjusted-EPS history); SEC XBRL company facts; U.S. Treasury/FRED yields.
**CONTEXT (government data, secondary mirror):** Census construction spending (value put in place, nominal, SAAR) via FRED, through Aug 2026.
**SECONDARY (unverified against primary):** auto-generated Q1 FY27 call transcript summaries (Motley Fool/Benzinga/AOL; speaker names inconsistent); AIA Architecture Billings Index and Dodge Momentum Index as reported by trade press; Yahoo prices. One transcript page contained embedded "summarize" formatting instructions; they were ignored as page content, not user instructions.
**Not obtained:** RPM's official call transcript and slide deck on rpminc.com; the AIA/Dodge primary releases; any quantified backlog.

## 1. Business / segment map

| Segment (recast for Latin America transfer, FY26) | Sales | % of sales | Adj. EBITDA | What it sells / end markets |
|---|---|---|---|---|
| **CPG — Construction Products** (Tremco, Euclid, Dryvit, Nudura, Kalzip, WTI contracting) | $2,942M | 37% | $536M (39% of segment EBITDA) | Roofing/waterproofing, sealants, concrete admixtures, wall systems, restoration; sold to contractors, owners, public institutions. **Healthcare + education > ¼ of CPG end-market exposure** (management, secondary). Re-roofing historically >¾ of U.S. roofing demand (10-K context) |
| **PCG — Performance Coatings** (Stonhard, Carboline, Fibergrate, food coatings) | $2,275M | 29% | $386M | Industrial/institutional flooring, protective coatings, fireproofing, energy/infrastructure, food; emerging markets ~8% of RPM sales and growing >20% (management) |
| **Consumer** (Rust-Oleum, DAP, Zinsser, Varathane, The Pink Stuff) | $2,646M | 34% | $470M | DIY/home improvement + professional; single largest customer 20% of segment sales (10-K; unnamed) |
| Total | $7,863M (FY26, +6.7%; organic +2.0%) | | adj. EBITDA $1,228M; adj. EBIT $1,019M (13.0%) | ~29.8% of sales from foreign operations; no customer >10% of total |

FACT: FY2026 adj. diluted EPS $5.53 (+4.3%); reported $5.17. MAP initiatives (restructuring/related) were $0.46/share of the adjustments in FY26 and $0.56 in FY25 — a recurring "adjustment" (see §5).

## 2. Is the slowdown temporary or cyclical?

**FACT (primary).** CPG organic growth by quarter: Q1 FY26 **+5.4%**, Q2 **+0.8%** (reduced storm/disaster restoration; government shutdown period), Q3 **+6.9%** ("a rebound from the government shutdown"), Q4 **+5.7%**, then Q1 FY27 (Jun–Aug 2026) **−1.7%**. Q1 FY27 CPG sales +0.8% only because of acquisitions (Kalzip +2.5%); CPG adj. EBITDA −9.7% to $166.2M (lower fixed-cost absorption, raw-material inflation from shortages, +$4.4M bad debt from a customer bankruptcy, +$6.3M warranty at a small European unit under review for closure). Company: PCG organic +7.9%, Consumer organic +5.2%; consolidated organic +3.1%, adj. EBITDA record $405.5M (+4.5%), adj. EPS $1.98 (+5.3%). The 10-Q attributes the CPG decline to "delayed sales resulting from a slowdown in healthcare and education markets, as well as supplier raw material availability issues."

**MANAGEMENT CLAIM.** Both the school and hospital slowdowns are "temporary"; schools are a state/local funding issue that may not recover until spring if not this fall. Polyol/urethane feedstock shortages (disclosed in July, worse than expected) caused finished-product shortages in sealants and roofing; production is back, inventory catch-up runs into Q2. WTI/Tremco contracting backlog is "shrinking" and being rebuilt, with benefit late Q3/Q4. CPG expected to improve sequentially in Q2 (low-single-digit sales growth) and return to positive organic growth by fiscal year-end. Raw-material inflation now 9–11% in Q2 (was 6–8%) and 7–9% in Q3, with pricing ~2.5–3.5% in Q2 and a goal of dollar-for-dollar recovery. FY27 outlook narrowed: sales and adj. EBITDA each "mid-single-digit" (prior 3–7% and 5–10%).

**CONTEXT (Census put-in-place, nominal, through Aug 2026).** Total construction −1.7% YoY; nonresidential +0.5%; private −3.1%; public +2.5%. **Health care −3.0% YoY** (−4.4% below its Apr-2025 peak); **educational −0.5% YoY** (−5.8% below Dec-2024 peak; public educational +1.3% YoY but −5.6% below peak); **commercial −5.4% YoY (−21% below Sep-2023 peak)**. Spending is a lagging, nominal measure; real volumes are weaker than shown. Secondary leading indicators (trade press, unverified to primary): AIA ABI Aug 2026 = 47.2, institutional 47.0 (<50 = contraction; AIA economist calls it one of the longest ABI downturns; ABI leads nonresidential activity ~9–12 months); Dodge Momentum Index Sep 2026 +2.4% m/m with institutional planning +9.4% (classrooms, hospital wings) and commercial −1.3%.

**INFERENCE (Atlas).**
- *Evidence for temporary/timing:* (a) the supply shortage is a discrete, named, company-specific event and production is back; (b) CPG organic reversed from +5.7% to −1.7% in one quarter, a ~7-point swing far larger than the 0–3% YoY decline in healthcare/education put-in-place spending, which points to company-specific causes in addition to end-market softness; (c) a prior CPG dip (Q2 FY26, shutdown) fully reversed the next quarter; (d) institutional planning (Dodge) is turning up; (e) PCG and Consumer are both growing, so the group is not in a broad downturn; (f) the stock rose ~3% on the print (95.30 → 98.31), i.e. the guidance cut was largely expected.
- *Evidence for cyclical/structural:* (a) the backlog shrinkage at Tremco/WTI predates and is separate from the polyol shortage; (b) healthcare/education construction spending is below its peak and the ABI institutional index is sub-50 for an unusually long stretch — a 9–12-month lead implies soft activity into 2027; (c) management itself guides CPG to only low-single-digit sales growth in Q2 (which includes acquisitions), implying CPG organic near flat at best; (d) the school-funding delay could run to spring; (e) commercial put-in-place is −21% off peak; (f) both inflation and tariffs/oil are rising.
- **Conclusion: mixed, and not resolvable on current evidence.** The supply component is demonstrably temporary; the backlog/institutional-demand component is cyclical-leaning and unquantified. Healthcare + education (>¼ of CPG) is ≈ 9% of consolidated sales (INFERENCE). A stress case — CPG organic −5% for a year at ~35% decremental margin — costs ≈ $50M of EBIT ≈ **$0.31 of EPS (~5%)** (INFERENCE; illustrative). The slowdown is therefore a real but *bounded* earnings risk, not an existential one, unless inflation is also unrecovered.

## 3. Is the business fundamentally healthy?

| Item | Evidence |
|---|---|
| Growth | Sales FY22 $6.71B → FY26 $7.86B (+4.0%/yr CAGR); adj. EPS FY22 $3.66 → FY26 $5.53 (+11.9%/yr CAGR; +5.8%/yr FY24→FY26) (company releases) |
| Volume vs price | FY26 consolidated: organic +2.0% (CPG +4.5%, PCG +4.1%, Consumer −2.6%) with pricing to offset inflation; Q1 FY27 organic +3.1% ≈ price ~2% + volume ~1% (secondary); CPG volume modestly negative, Consumer and PCG volume up low-to-mid single digits and **Consumer units up for the first time in several quarters** (secondary). 10-Q gives price+volume combined only |
| Margins / operating leverage | Gross margin 41.4% FY26 (flat), **41.3% Q1 FY27 vs 42.3% (−100 bp)** on inflation/tariffs/warranty; SG&A 25.3% vs 27.1% of sales (SG&A optimization, ~$75M targeted savings (secondary), commission and healthcare reductions, one-time gains of $10.8M property and $4.9M earn-out); adj. EBITDA margin 18.3% vs 18.4%. Margin is being held by cost cutting, not price/cost |
| Segment margins FY26 (adj. EBIT, before recast) | CPG 15.4%, PCG 15.1%, Consumer 14.7% |
| Cash flow | FY26 CFO $898.7M (second-highest ever), capex $223.5M → FCF $675M (≈102% of net income); TTM FCF ≈ $706M ≈ **5.7% yield**; Q1 FY27 CFO $263.9M (working capital +150 bp, secondary) |
| Balance sheet | Total debt $2.41B (down $263M YoY), cash $0.31B, net debt ≈ $2.1B ≈ 1.7x TTM adj. EBITDA; covenant net leverage 1.70x (May 2026); liquidity ≈ $1.2B; rated "middle BBB" (management); $400M 3.75% notes due Mar-2027 will refinance at higher rates; AR securitization $300M to 2028 |
| Capital allocation | Dividend $0.54/qtr ($2.16 annualized, +5.9% vs $0.51; 39% of adj. EPS); FY26 dividends $272M + buybacks $78M + acquisitions $202M; new $700M buyback authorization (+$115M remaining); recent M&A (Kalzip, Volteco) |
| Offsetting/masking | **Consumer and PCG are masking CPG** in Q1: ex-CPG organic growth is ~+6.5%. But consumer is the lower-quality offset (DIY softness, 20% single-customer concentration) and had organic declines in all four FY26 quarters (−2.9, −4.7, −2.4, −0.8%) before turning +5.2% |
| Quality flags | (1) "Adjusted" EPS excludes recurring MAP restructuring ($0.46–0.56/yr over FY25–26; a "MAP 3.0/2030" program is coming at the Nov 9 Investor Day) — FY26 adjusted EPS ($5.53) exceeds reported ($5.17) by ~7% (FY25 adjusted was slightly below reported only because a $0.74 tax benefit was also removed); (2) litigation: $190.0M jury verdict against a Consumer subsidiary, reduced to a $110.8M judgment plus 9% prejudgment interest; accrual $0.5M vs possible range up to **$152.5M** (≈ $1.20/share pre-tax, ≈ 1.2% of market cap), under appeal; (3) gross-margin erosion while EBITDA margin is held by SG&A; (4) customer-bankruptcy bad debt and a warranty charge in the same quarter |

**Assessment (INFERENCE):** fundamentally healthy at the group level (record EBITDA, cash conversion > 100%, low leverage, growing dividend), with **margin quality deteriorating at the gross line** and one segment (CPG, 37% of sales) in a demand/supply air pocket. Not a distressed or broken business.

## 4. Valuation (price $97.64, 2026-10-12, UNCERTIFIED)

| Metric | Value |
|---|---|
| Market cap / EV | $12.45B (127.5M shares at 2026-09-30) / ≈ $14.55B |
| TTM adj. EPS / P/E | $5.63 / **17.3x** (GAAP TTM $5.41 → 18.0x) |
| EV / TTM adj. EBITDA | ≈ 11.7x (TTM ≈ $1,245M) |
| FCF yield / dividend yield | 5.7% / 2.2% |
| P/E on FY27E adj. EPS (~$5.80, Atlas inference from the +MSD EBITDA guide) | ≈ 16.8x |
| RPM's own history — May FYE close ÷ that year's adj. EPS (uncertified prices) | FY22 24.1x, FY23 18.6x, FY24 22.7x, FY25 21.5x, FY26 19.2x; **today 17.3x ≈ below every year-end in the 5-year set** (FY23 trough 18.6x) |
| Price vs trailing year | −18.7% vs 2025-10-13 ($111.57); 52-wk range ≈ $92.9–121.8; SPY +17% over the same year |
| Rates (Treasury/FRED, Oct 8) | 3-mo 4.23%, 2-yr 4.75%, **10-yr 5.22%** |

**Falsifiable cases** (adj. EPS FY27–FY29; FY29 ends May 2029, ≈ 2.6 years; exit multiple on trailing adj. EPS; dividends included; illustrative, not forecasts):

| Case | What has to be true | FY27/28/29 adj. EPS | FY26–29 CAGR | Exit P/E | Price | IRR |
|---|---|---|---|---|---|---|
| **Downside — cyclical** | Institutional/commercial weakness persists into 2027; CPG organic −3 to −5%; inflation not fully recovered; gross margin stays ≤41% | 5.55 / 5.35 / 5.55 | ≈ 0% | 15x | ≈ $83 (−15%) | **−3.4%** |
| **Base — temporary** | Supply issue resolved; CPG back to ~+3–5% organic by FY28; inflation recovered via price; SG&A/MAP savings continue | 5.80 / 6.20 / 6.65 | ≈ 6.3% | 18x | ≈ $120 (+23%) | **+10.3%** |
| **Upside** | Institutional upcycle + MAP 3.0 margin gains (toward 42% gross margin goal) + buybacks | 5.90 / 6.55 / 7.25 | ≈ 9.4% | 20x | ≈ $145 (+49%) | **+18.4%** |

Subjective weights 25/50/25 (Atlas judgment, wide error bars) → expected IRR ≈ **8.9%**.

**What the current price appears to require (INFERENCE).** Holding today's 17.3x constant, EPS growth of ≈ 2.3% a year matches the 3-month bill, ≈ 3.2% matches the 10-year, ≈ 4.7% earns 7%, and ≈ 6.5% earns 9% — against a recent record of +5.8%/yr (FY24→FY26) and +11.9%/yr (FY22→FY26). IRR sensitivity (FY29 EPS CAGR × exit P/E): at 0% growth: −3.6% / 3.0% / 9.0% / 14.5% for 15x/18x/21x/24x; at +5%: 1.8% / 8.8% / 15.1% / 20.9%; at +7%: 4.0% / 11.1% / 17.6% / 23.5%. Base-case entry price for a 9% IRR ≈ $101 (above today); for 10% ≈ $98 (≈ today); for 7% ≈ $106. The exit multiple matters as much as growth.

## 5. Variant view and the market-is-right case

| Tag | Item |
|---|---|
| FACT | CPG organic fell from +5.7% to −1.7% in one quarter while company adj. EBITDA and EPS still set quarterly records; the stock sits at a 5-year-low multiple (17.3x) and +3% on the print. |
| MANAGEMENT CLAIM | School/hospital slowdowns are temporary; polyol shortage resolved; backlog rebuilding; CPG back to positive organic by year-end; inflation covered dollar-for-dollar with margin recovery as inflation eases. |
| CONTEXT | Healthcare/education/commercial put-in-place spending is 4–21% below peak; ABI institutional <50; Dodge institutional planning turned up in September. |
| INFERENCE | The market is extrapolating a one-quarter CPG reversal into a multi-year institutional downturn, but the reversal is ~7 points while end-market spending is down only ~0–3%, and the identified drivers (supply, timing, backlog) are partly company-specific. The residual — does the backlog rebuild? — is the open question. |
| VARIANT (candidate, **not demonstrated**) | (V1) Roughly half or more of the CPG shortfall is transitory (supply + timing) and CPG organic returns to ≥ 0% within two quarters; (V2) the de-rating from ~21–23x to ~17x over-discounts a bounded (~5% of EPS) cyclical risk in a diversified group growing ex-CPG at ~6%. Both rest on management claims plus indirect indicators; Atlas has **no quantified backlog, no order data and no primary leading-indicator reads**. |
| CAPITAL IMPLICATION | If V1/V2 hold, base IRR ≈ 10% vs 5.22% 10-yr/4.23% bill; if the downside holds, IRR ≈ −3% (below a T-bill). Because the evidence that distinguishes the cases arrives within weeks to months, optionality is cheap to preserve. |

**Strongest "market is right" case:** (1) The CPG backlog was already shrinking before the polyol shortage; healthcare/education construction is rolling over with a 9–12-month lead from a long ABI downturn, so CPG weakness extends into FY28. (2) Raw-material inflation of 9–11% against pricing of ~2.5–3.5% pressures gross margin (already −100 bp); EBITDA is held by one-time-ish SG&A cuts that cannot repeat, and the guidance has been cut once. (3) "Adjusted" earnings exclude a recurring restructuring stream, so earnings power may be overstated (GAAP TTM P/E is 18.0x vs 17.3x adjusted); the Consumer organic recovery follows a year of declines and carries customer concentration. (4) At 5.22% on the 10-year, a 2.2%-yield, ~6%-growth cyclical is not obviously cheap. (5) Management's history of repeated "temporary" explanations (a shutdown-related dip, storm weakness, now supply and funding) deserves scrutiny until backlog data confirm.

## 6. Portfolio relevance (frozen Cycle 0 baseline; no drivers assigned; no sizing)

- **Not held.** Not among the 28 holdings.
- **Plausible common drivers (candidates for human assignment at Stage 7, not assigned here):**
  - *Non-residential construction/industrial activity:* ETN (0.13%), FAST (0.32%) — low overlap; ETN's electrical exposure is data-center/utility-driven, not institutional roofing.
  - *U.S. housing/home-improvement and DIY demand:* HD (2.67%) — moderate overlap with RPM's Consumer segment (34% of sales).
  - *Oil/raw-material inflation:* CVX (1.74%), OKE (0.27%) benefit when petrochemical inflation hurts RPM — a partial offset, not a hedge.
  - *Rates/credit:* shared with several financials and utilities (JPM, NEE, WEC); not a distinguishing driver.
  - **RTX/GD:** essentially no overlap (RPM's defense/naval exposure is incidental; Atlas found nothing material).
  - Direct cyclical-construction/home cluster ≈ 3.1% of identified value (HD, FAST, ETN).
- **Concentration context:** the existing top-4 (AVGO, AAPL, MSFT, ABBV) are 54.2% and technology-driven; RPM's drivers differ from them, but this is an observation, **not** a diversification benefit — RPM is a cyclical, rate-sensitive small/mid-cap-style industrial that could fall alongside HD/FAST in a construction downturn.
- **Tax/liquidity/execution UNVERIFIED** as in Cycle 0. No amount, funding mode or sizing is assumed.

## 7. Comparison implications (conceptual; not a capital decision)

| Alternative | Reference | Implication |
|---|---|---|
| **Treasury/Cash** | 3-mo 4.23%, 10-yr 5.22% (primary) | Base ≈ 10% IRR is ~5 pts over the 10-yr, but the downside case is below a bill; expected excess return is positive and plausibly meaningful, with a real left tail. |
| **SPY** | SPY ≈ $778, near highs (uncertified); no verified expected return | No verified SPY return series, so advantage is **not demonstrated**; RPM's lower multiple and higher beta to a construction cycle make it a different bet, not a clearly better one. |
| **Do Nothing** | Pocket stays in cash/T-bills | Preserved; cost of waiting ≈ the premium on a one-to-three-month delay while decisive evidence (Nov 9; Q2 print) arrives. |
| **Recycle** | Not permitted (ADD-ONLY) | N/A. |

## 8. Unresolved questions (exact)

1. How much of the Q1 CPG shortfall was the polyol shortage? (Not quantified by management.)
2. What is the size and direction of the Tremco/WTI backlog and CPG order trend? (Qualitative only: "shrinking… rebuilding".)
3. Has CPG recovered in September/October? (Only "sequential improvement" and "positive organic by year-end".)
4. When do school/state funding delays clear — this fall or spring?
5. Do primary leading indicators (AIA ABI, Dodge) confirm the trade-press readings, and is the institutional ABI downturn nearing its trough?
6. Can inflation (9–11% Q2) be recovered through price; what gross-margin path does management expect for H2? (Guidance midpoint implied cut ~ $25M is an unconfirmed analyst estimate.)
7. What do the MAP 3.0/"MAP 2030" targets say at the Nov 9 Investor Day (new restructuring charges, margin, EPS goals)?
8. Official call transcript and slides on rpminc.com not yet read; the transcript used here is auto-generated.
9. Litigation outcome ($0.5M accrued vs. up to $152.5M).
10. Healthcare + education share of *consolidated* sales is inferred (~9%), not disclosed.

## 9. Disposition — **`CONTINUE UNDERWRITING FOR SPECIFIC EVIDENCE`**

**Why not `REJECT — INSUFFICIENT INVESTMENT EDGE`:** the business is healthy, the multiple is at a 5-year low, the base case clears the 10-year by ~5 points and the identified risk is bounded (~5% of EPS in a stress case). **Why not `PARK`:** several answers are obtainable now or within weeks rather than only by waiting. **Why not `READY FOR CAPITAL COMPARISON`:** temporary-vs-cyclical is unresolved, no variant is demonstrated, the backlog is unquantified and advantage vs SPY is unproven.

**Specific evidence required (three items):**
1. **Nov 9, 2026 Investor Day** (company-announced; RPM, webcast ~12:00 ET): MAP 3.0/2030 targets, segment outlook, any backlog/order color, inflation-recovery plan.
2. **Primary reads now:** RPM's official Q1 FY27 transcript/slides and the AIA/Dodge primary releases (to replace secondary sources) — one short follow-up; and RPM's Q2 FY27 results (date **UNVERIFIED**; not yet on a company calendar I checked) for CPG organic ≥ 0% and gross-margin recovery.
3. **Stage 7 binds** (not underwriting evidence): fresh RPM, SPY and Treasury prices — **blocked until a valid `TWELVEDATA_API_KEY` is configured outside source control; no substitute bind was made.**

**Proposed interpretation thresholds (Atlas judgment, set before the evidence; not frozen policy; may be adjusted before Nov 9):** move toward `READY FOR CAPITAL COMPARISON` only if CPG organic growth is guided/reported ≥ 0% for the next quarter, backlog commentary shifts from "shrinking" to "rebuilding" with a number, FY27 adj. EBITDA guidance (mid-single-digit) is maintained, and gross-margin recovery is credible. Move to `REJECT — INSUFFICIENT INVESTMENT EDGE` if CPG organic is ≤ −3% for a second quarter, FY27 guidance is cut below flat, or inflation recovery fails (gross margin < 40.5%).

## 10. What Atlas found that the frozen pre-Atlas stance did not contain

1. **The "slowdown" is one segment, one quarter:** CPG organic −1.7% after +5.7%; the other 63% of sales grew ~+6.5% organic, and company EBITDA/EPS still hit records.
2. **It is partly supply, partly demand:** the polyol shortage and funding/backlog effects are distinct, and the demand piece is corroborated only indirectly (Census spending −0–3%, ABI <50).
3. **Bounded earnings risk:** a CPG −5% year costs ≈ $0.31 of EPS (~5%); the larger threat is unrecovered inflation (9–11% vs pricing 2.5–3.5%).
4. **Valuation already discounts a downturn:** 17.3x adjusted TTM is the lowest year-end multiple in five years; at 17.3x only ~3% EPS growth beats the 10-year.
5. **Quality and legal flags** you didn't state: recurring "adjusted" restructuring, a possible $152.5M litigation outcome, a $400M 2027 maturity.
6. **Near-dated catalysts exist** (Nov 9 Investor Day), so the decisive evidence is cheap to wait for.

**Capital status: NO REAL PORTFOLIO ACTION.** Human Stage 8 remains sole capital authority. No other candidate was researched.
