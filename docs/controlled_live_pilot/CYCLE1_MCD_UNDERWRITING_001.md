# Controlled Live Pilot — Cycle 1 — MCD Underwriting 001

> **NO REAL PORTFOLIO ACTION. NOT STAGE 7. NOT STAGE 8.** Research record only.
> The frozen pre-Atlas stance (`CYCLE1_MCD_PRE_ATLAS_STANCE_001.md`, `0a923e2`)
> is untouched and was treated only as the counterfactual.

| | |
|---|---|
| Date | 2026-10-07 |
| Candidate | McDonald's Corporation (MCD), CIK 0000063908, NYSE (XNYS) — human-selected |
| Objective | Does MCD currently present a sufficiently attractive case to advance toward Stage 7? |
| Disposition | **`CONTINUE_UNDERWRITING_FOR_SPECIFIC_EVIDENCE`** |
| Price basis | **UNCERTIFIED** — `TWELVEDATA_API_KEY` is absent; price/rate series are from Yahoo Finance and are research context only, not a Stage 7 bind |

## 0. Evidence labels

**PRIMARY (used for every business fact):** SEC Form 10-K FY2025 (acc. 0000063908-26-000035, filed 2026-02-24); Form 10-Q Q2 2026 (acc. 0000063908-26-000073, filed 2026-08-07); Form 8-K 2026-09-23 Ex. 99.1 Investor Day release (acc. 0000063908-26-000076); SEC XBRL company facts; U.S. Treasury daily par yield curve (via home.treasury.gov and FRED, 2026-10-05/06).
**SECONDARY / CONTEXT (labeled where used):** third-party transcript of the 2026-09-23 Investor Day (stockanalysis.com — not checked against audio); press coverage (Fortune, Star-Advertiser, Quiver, IBTimes) for stock reaction, analyst targets and Q2 call quotes; Yahoo Finance prices (uncertified).
**Discarded:** one search snippet giving a 4.5% 10-year yield (contradicted by Treasury primary data: 5.27%); an undated S&P 500 forward P/E (20.6x) — kept only as an unverified context number; a 2025 Restaurant Dive article (wrong year); peer forward multiples (inconsistent dates/sources, not used quantitatively).

## 1. Cheapest falsification (run first)

| # | Case-killer tested | Result | Verdict |
|---|---|---|---|
| F1 | **Valuation is stretched** (Chris's stated concern) | Price ≈ $232.24 (uncertified). TTM GAAP EPS $12.31 → **18.9x** (2026E ≈ $12.60 → 18.4x). Year-end trailing P/E on SEC EPS: 2023 25.6x, 2024 25.5x, 2025 25.6x. Stock is **−32% from its 52-week high ($341.75)** and −24% over a year while SPY is +16%. TTM FCF yield 4.7%; dividend yield 3.2%. | **Does not kill.** Multiple has de-rated ~26% from its 2023–25 level; "fully priced" is not what the data show today. |
| F2 | **Business deterioration at the parent** | H1 2026: revenue +6% (+3% cc), operating income +7% (+4% cc), EPS +6% (+3% cc); Systemwide sales +8% (+5% cc); op margin 46.2%. But U.S. comps +0.8% in Q2 on **negative guest counts**; management guides Q3 U.S. comps "slightly negative" (secondary transcript). | **Does not kill, but is the swing variable.** Weakness is at the U.S. franchisee/consumer layer, not yet in parent earnings. |
| F3 | **Balance sheet / capital-return fragility** | Debt $39.9B (97% fixed, 4.0% avg rate), cash $0.8B; net debt/EBITDA ≈ 2.6x (ex-leases); OI/interest ≈ 7.9x; BBB+/Baa1; CFO/debt 26%; shareholders' equity −$1.8B (buyback artifact). FY2025 dividends $5.1B + buybacks $2.1B ≈ FCF $7.2B. | **Does not kill.** Leveraged by design, covered. Little slack for a heavier partnering burden plus buybacks. |
| F4 | **Return vs alternatives is clearly inferior** | Treasury (primary): 3-mo 4.21%, 2-yr 4.79%, **10-yr 5.27%**. Constant-multiple math: MCD beats the 10-yr only if EPS CAGR ≳1.5%, earns 7% only if ≳3.25%. Scenario IRR range −2.7% to +15.4% (§4). | **Does not kill, but no clear edge.** Expected excess return over rates is positive but moderate; versus SPY it is not demonstrated (§8). |

No single fact killed the case, so underwriting continued — but only on the decision-relevant issues.

## 2. Business / economic underwriting (decision-relevant only)

**Revenue and earnings engine (FACT, 10-K/10-Q).** ~95% franchised (44,016 of 46,028 restaurants at 2026-06-30). Parent earns rent + royalty on franchisee sales (franchised margins $6.1B in the U.S. alone, 2025) plus a small company-operated margin. FY2025: revenue $26.9B, operating income $12.4B (margin 46.1%; 46.9% ex-charges), net income $8.56B, diluted EPS $11.95, Systemwide sales $139.4B (+5% cc), CFO $10.55B, capex $3.37B, **FCF $7.19B (84% of net income)**, ROIC 20.3% (down from 25.2% in 2023, 21.8% in 2024). Operating income split 2025: U.S. $5.8B (47%), International Operated Markets $6.4B (51%), IDL & Corporate $0.2B (2%).

**Same-store sales / traffic / pricing (FACT).** Global comps 2025 +3.1% (U.S. +2.1% "benefiting from average check growth"); Q2 2026 global +1.3% (U.S. +0.8% — "positive check growth… partly offset by negative comparable guest counts"; IOM +1.5%; IDL +1.9% with China negative, France negative in IOM). U.S. is a check/mix story, not a traffic story. **MANAGEMENT CLAIM (secondary press, Q2 call):** loyalty-customer visit loss ≈ two-thirds of the traffic shortfall; "we don't have a strategy problem, we simply didn't execute"; the U.S. operations head was replaced. **MANAGEMENT CLAIM (Investor Day, secondary transcript):** flat industry traffic and elevated inflation expected to persist; Q3 U.S. comps "slightly negative", September positive.

**Franchisee health (MGMT CLAIM, secondary transcript; unverified).** U.S. AUVs "north of $4M" with ~$500K operating cash flow per restaurant; U.S. franchisee system cash flow "up nearly 50%" vs 2019. Atlas has no independent franchisee-margin series — this is the least-verified link in the thesis and the reason for the $8.5B support program.

**Unit growth / development (FACT + MGMT CLAIM).** 2026 guide: ~2,600 openings, ~2,100 net adds, ~2.5% contribution to Systemwide sales, 50,000 units targeted for 2028; restaurants +4.3% YoY at 2026-06-30. Investor Day: nearly 2.5% contribution in 2027 easing to ~2% by 2030; net unit growth "nearly 4.5%" in 2027 (secondary transcript). Roughly 1,800 of 2026 openings are funded by licensees/affiliates (capital-light).

**Margins and FCF (FACT / MGMT CLAIM).** 2026 guide: op margin mid-to-high 40s; FCF conversion low-to-mid 80s; capex $3.7–3.9B; tax 21–23%; interest +4–6%; SG&A ≈2.2% of Systemwide sales. **New 2030 targets (8-K Ex. 99.1):** op margin low-to-mid 50s; G&A ≈1.9% of Systemwide sales; FCF conversion mid-to-high 80s; capex ≈$3B baseline per year plus $1.5–2B cumulative partnering capital (2027–30). **INFERENCE:** most of the margin step is mix, not new profit dollars — management (secondary transcript) attributes it to comps, G&A leverage and franchised mix rising from ~95% to ~98% by 2028. A refranchised store removes low-margin revenue; the margin % can rise while operating-income dollars grow far less. **Valuation should key off dollars/EPS, not the margin %.**

**Debt / capital allocation (FACT / MGMT CLAIM).** Policy: invest first, prioritize the dividend, buy back with remaining FCF. Dividend $1.86/qtr ($7.44 annualized), 50th consecutive annual increase; payout target 50–60% of EPS (secondary) — now ≈59% of 2026E EPS, i.e. the top of the range, so dividend growth ≈ EPS growth. Buybacks fell from $3.9B (2022) to $2.1B (2025); H1 2026 $1.25B. Diluted shares 750M (2020) → 711M (Q2 2026), ≈ −0.9%/yr. Management commits to maintaining the investment-grade rating (secondary).

**NEXT program economics (FACT + INFERENCE).** ~$8.5B of franchisee "partnering" through 2036, ~$5B by 2030, as rent relief plus capital support; ~$800K incremental investment per U.S. restaurant; claimed ~250 bps gross restaurant efficiency ≈ $100K/yr cash flow per U.S. restaurant, ~4-year franchisee payback after partnering. **INFERENCE:** rent relief through 2030 ≈ $5B − $1.5–2B capital ≈ $3.0–3.5B; management says it is amortized over ~10 years (secondary), so incremental P&L drag by 2030 is on the order of $0.3B/yr (~2.5% of FY2025 operating income) before 2031–36 spending — manageable but not zero, and the year-by-year schedule is **not in the primary release**. Cash outflow is front-loaded relative to P&L.

**Competitive position / brand durability (CONTEXT).** Scale (46K restaurants, ~29K drive-thrus, ~220M 90-day loyalty actives, $40B loyalty Systemwide sales TTM, +20%) is a real, verifiable advantage in a flat-traffic industry; real-estate ownership under conventional franchises supports the rent stream. Evidence the brand is losing relative share is **not** in hand beyond negative U.S. guest counts; the company itself targets chicken/beverage share gains (+1.5pp each by 2030).

**Material operating risks (primary risk factors + CONTEXT).** U.S. low-/middle-income consumer weakness; value-war margin give-back; franchisee profitability and willingness to invest; execution of a large remodel/AI (ArchIQ) program; China and France softness; FX (H1 EPS had a +$0.17 FX tailwind — H1 EPS growth is +3% in constant currency); commodity/labor inflation; refranchising mix risk; leadership change in the U.S.

## 3. Valuation basis (as of 2026-10-07; price UNCERTIFIED)

| Metric | Value | Basis |
|---|---|---|
| Price | $232.24 | Yahoo close 2026-10-07 (uncertified) |
| Shares / market cap | 707.6M / $164.3B | 10-Q cover (2026-06-30) |
| Net debt / EV | $39.0B / $203.4B | 10-Q balance sheet; leases ($14.7B) excluded, largely sub-leased to franchisees |
| TTM GAAP EPS / P/E | $12.31 / **18.9x** | FY25 + H1'26 − H1'25 (GAAP incl. ~$0.2/yr restructuring) |
| 2026E EPS / P/E | ≈$12.60 / ≈18.4x | Atlas estimate: H1 actual + H2 at ~+5% — **INFERENCE** |
| TTM EBITDA / EV/EBITDA | $15.1B / 13.5x | OI + D&A |
| TTM FCF / yield | $7.76B ($10.97/sh) / **4.7%** | CFO − capex, TTM (working-capital flattered); 2026E ≈ $7.3B / 4.5% at 82% conversion |
| Dividend yield | 3.2% | $7.44 ÷ $232.24 |
| Year-end trailing P/E, 2021–2025 | 26.7x, 31.6x, 25.6x, 25.5x, 25.6x | SEC GAAP EPS ÷ Yahoo year-end close (uncertified) |
| Treasury | 3-mo 4.21%, 2-yr 4.79%, 10-yr 5.27% | Treasury par curve 2026-10-06 (primary) |
| Analyst context (secondary) | avg target ≈ $299; post-Investor-Day cuts: MS $297, Baird $250, Oppenheimer $295, Melius $230 (Sell) | Press; not used as thesis |

**Trailing EPS history (SEC):** 2022 $8.33, 2023 $11.56, 2024 $11.39, 2025 $11.95, TTM $12.31 — the 2023→TTM CAGR is only **≈2.5%** (≈1.7% 2023→2025), including FX help. A 5% base case therefore requires *acceleration* from recent history.

## 4. Valuation cases (FY2030 EPS × exit multiple, plus dividends; ~4.2-year horizon; illustrative, not forecasts)

| Case | EPS CAGR from 2026E | Exit P/E | 2030 EPS | Price 2030 | Total-return IRR | Operating story |
|---|---|---|---|---|---|---|
| Severe | 0% | 14x | $12.60 | ~$176 | **−2.7%** | U.S. traffic erosion persists; partnering drag and higher interest absorb unit/G&A gains |
| Downside | 2% | 16x | $13.64 | ~$218 | **+2.0%** | Recent-history growth, no recovery, multiple stays compressed |
| **Base** | **5%** | **19x** | $15.32 | ~$291 | **+8.9%** | ~4% revenue/OI growth + G&A leverage + ~1% net buyback − interest/rent-relief drag; multiple unchanged |
| Strong execution | 8% | 22x | $17.14 | ~$377 | **+15.4%** | U.S. traffic recovers, efficiency flows through, multiple re-rates part-way to 25x |

Subjective probability weights 10/20/45/25 (Atlas judgment, wide error bars) give an expected IRR ≈ **8.0%**.

**IRR sensitivity (EPS CAGR rows × exit P/E columns):**

| EPS CAGR | 16x | 19x | 22x | 25x |
|---|---|---|---|---|
| 0% | 0.1% | 3.9% | 7.3% | 10.4% |
| 2% | 2.0% | 5.9% | 9.4% | 12.5% |
| 3.5% | 3.4% | 7.4% | 10.9% | 14.1% |
| 5% | 4.9% | 8.9% | 12.4% | 15.7% |
| 6.5% | 6.3% | 10.3% | 14.0% | 17.2% |
| 8% | 7.7% | 11.8% | 15.5% | 18.8% |

**What the current price appears to require (INFERENCE).** Holding today's 18.9x constant, MCD needs EPS CAGR ≈0.25% to match the 3-mo bill, ≈1.5% to match the 10-yr, ≈3.25% to earn 7%, ≈5.5% to earn 9%. The price therefore does **not** embed heroic growth; it embeds a de-rated, low-growth outcome. The valuation is no longer the binding constraint — the exit multiple and U.S. traffic are. In the base case the entry price for a 9% IRR is ≈$231 (≈ today), for 10% ≈$223, for 7% ≈$249.

## 5. Variant question

*What would Atlas have to believe that the market does not already appear to believe?*

| Tag | Item |
|---|---|
| FACT | The multiple has fallen from ~25.6x to ~18.9x while parent EPS kept growing (+6% H1; +3% cc). Parent earnings are ~95% franchise-fee driven and have not yet reflected U.S. traffic weakness beyond a +0.8% comp. |
| MANAGEMENT CLAIM | U.S. softness is an execution miss (value communication, digital promos), not a strategy flaw; September U.S. comps positive; NEXT yields ~250 bps restaurant efficiency, ~4-year franchisee payback; unit growth ~2.5% of sales growth; G&A to 1.9%; FCF conversion mid-to-high 80s by 2030. |
| CONTEXT | Industry traffic is flat (per management); the 10-year Treasury at 5.27% sets a high hurdle; the stock sold off on the Investor Day (≈−4.8% close-to-close on 9/23 per Yahoo, uncertified; new 52-week lows) on near-term cash cost and no demonstrated U.S. fix. |
| INFERENCE | The market is pricing the NEXT partnering as a transfer from shareholders to franchisees ahead of proof of payback, and pricing U.S. traffic weakness as persistent. Because the price needs only ~1.5–3.5% EPS growth to beat rates, the *pessimism is already largely in the price*; upside requires growth plus stabilization of the multiple. |
| VARIANT (candidate, **not demonstrated**) | (V1) Parent EPS can compound ≥5% through 2030 *despite* flat U.S. traffic, via ~2.5% unit-growth contribution, G&A leverage, and buybacks, with rent relief a ~2.5%-of-OI drag; and (V2) the de-rating from ~25x to ~19x over-extrapolates a U.S. execution lapse. Neither is yet evidenced beyond H1 results and management claims; V1's EPS-growth path is not in the primary release; V2 is a judgment about mean reversion, which Atlas does not treat as evidence. |
| CAPITAL IMPLICATION | If V1/V2 hold, MCD offers a base IRR ≈9% (5% EPS growth, 19x) vs 5.27% (10-yr) and 4.21% (3-mo); if not, the left tail (≤2% IRR) is *below* a T-bill. Atlas cannot yet show MCD's expected advantage over SPY is meaningful (§8). |

## 6. Key risks / the market-could-be-right case

1. **U.S. consumer/traffic structural erosion:** low-income traffic loss plus a value war that returns price to guests faster than costs fall; U.S. comps already ≈ check/mix only.
2. **Franchisee squeeze:** if franchisees cannot fund ~$800K/restaurant, the parent funds more of it (the $8.5B could grow) or remodel adoption slips, delaying the 250 bps benefit.
3. **Cash cost precedes benefit:** capex steps up (2026: $3.7–3.9B vs $3.4B), partnering cash is front-loaded, buybacks are the residual — less share shrink than the history implies; leverage tolerance is limited by the investment-grade commitment.
4. **Quality of the margin target:** the "low-to-mid 50%" is mostly mix; no EPS algorithm was given in the primary release.
5. **FX flattered 2026:** H1 EPS +6% reported vs +3% constant currency; the dollar can reverse.
6. **Rates:** a 5.27% 10-year caps the multiple of a 3.2%-yield, 3–5%-growth equity; the multiple can fall further (16x case).
7. **International drags:** China, France; IOM carries 51% of operating income.
8. **Management/credibility:** public admission of an execution miss and a U.S. leadership change.

**Market-could-be-right case:** EPS growth stays near the recent ~2.5% as U.S. traffic keeps falling and partnering costs rise; at 16–19x the stock then earns ≈2–6%, i.e. at or below the 10-year and well below SPY's likely return, with a 25–30% drawdown path already visible in the last year.

## 7. Portfolio-fit observations (from frozen Cycle 0; no drivers assigned — human-authored later)

- **Not a holding; no duplicate.** MCD is a new name; no ETF holdings (effective = direct).
- **Concentration relief, not addition:** the existing top-4 (AVGO 20.82%, AAPL 14.68%, MSFT 9.65%, ABBV 9.03%) are 54.2% of identified value; MCD is a non-tech consumer franchise and would modestly dilute tech/mega-cap concentration (observation only; no trims under ADD-ONLY).
- **Possible common drivers (candidate, for human assignment at Stage 7):** U.S. consumer spending (COST 4.57%, HD 2.67%, KMB 1.43% ≈ 8.7% combined); long-duration "yield-proxy"/rate sensitivity (WEC, NEE, KMB, ABBV, PAYX). A $10K MCD position (≈1.46%) would raise the consumer-spending cluster to ≈10.1%; below the 20% common-driver TARGET ceiling under any plausible assignment.
- **Sizing arithmetic only (no sizing recommendation):** $10,000 = 1.46% (STARTER band 1–2%; ~43 shares; ≈$320/yr dividends); ≈$13,957 is the 2% STARTER ceiling; **$15,000 = 2.19% exceeds STARTER (PARTIAL)** and must not be treated as a STARTER. Both fit the $25–50K T+1 pocket. Name-level capacity is far from binding (TARGET ≤8%).
- **Tax/liquidity/execution remain UNVERIFIED** and would block persistence of a funded decision until attested at Stage 7/8. MCD is highly liquid (market cap $164B).

## 8. Comparison implications (not a capital decision)

| Alternative | Reference | Implication for the next dollar |
|---|---|---|
| **Treasury/Cash** | 3-mo 4.21%; 10-yr 5.27% (primary) | Risk-free hurdle is high. MCD base ≈8.9% IRR (+3.6 pts over 10-yr, +4.7 pts over bills) but with ≤2% outcomes in 30% of weighted mass and a ~−24% to −32% drawdown history. Expected excess return positive but not large for the risk. |
| **SPY / broad beta** | SPY ≈ $776 (uncertified), near its 52-week high; S&P forward P/E unverified (an undated source says ~20.6x) | No verified SPY expected-return series. MCD's base (≈9%) is **comparable to**, not demonstrably above, plausible index returns; MCD's 18.4x forward multiple is not obviously cheaper than the index. **Advantage vs SPY: NOT DEMONSTRATED.** |
| **Do Nothing** | $25–50K outside capital sits in cash/T-bills at ≈4.2% | Do Nothing is preserved and loses only the ~4–5 pts expected premium. No time-decay pressure on the decision; the dated evidence in §9 arrives within weeks. |
| **Recycle** | Not permitted (ADD-ONLY) | N/A |

## 9. Disposition — **`CONTINUE_UNDERWRITING_FOR_SPECIFIC_EVIDENCE`**

**Why not `PROMOTE_TO_STAGE7`:** the case is reasonable (de-rated multiple, durable franchise cash flows, base IRR ≈9%), but Atlas has not demonstrated a variant: V1 (≥5% EPS CAGR through flat traffic) rests on management claims and a primary release with no EPS/OI algorithm or partnering phasing; V2 is mean-reversion judgment; and advantage vs SPY is unproven. **Why not `NO_DEMONSTRATED_INVESTABLE_EDGE`:** no case-killer in §1 held, and cheap, dated evidence can still move the answer. **Why not `BLOCKED_BY_MATERIAL_UNCERTAINTY`:** the open items are identifiable and resolvable, not structural.

**Specific evidence still required (exactly three):**

1. **Q3 2026 results** (date reported as 2026-10-28 by a secondary source — **confirm on the IR calendar/8-K**): U.S. comp and guest-count trend vs the "slightly negative" guidance, whether September/Q4 U.S. comps are positive, whether FY2026 outlook (op margin mid-to-high 40s, FCF conversion low-to-mid 80s, capex $3.7–3.9B) is unchanged.
2. **NEXT partnering schedule and 2027–2028 earnings framework** from the primary Investor Day materials (slides/webcast/10-Q): year-by-year rent relief vs capital support and its P&L/cash phasing, and any 2027 operating-income or EPS expectation. The 8-K release does not contain it.
3. **Stage 7 binds (not underwriting evidence; required before any capital comparison):** fresh MCD price, SPY, and Treasury/Cash reference through the certified path — **blocked until a valid `TWELVEDATA_API_KEY` is configured outside source control. No substitute live bind was made.**

**Proposed pre-registered interpretation thresholds (Atlas research judgment, set before the evidence; Chris may adjust before 10-28; they do not alter frozen policy or the pre-Atlas stance):**

- Eligible to move to **`PROMOTE_TO_STAGE7`** only if: Q3 U.S. comp ≥ −1.0% **and** management reports U.S. comps turning positive in September/Q4 **and** FY2026 outlook is unchanged **and** the partnering schedule is consistent with 2027–28 EPS growth ≥ ~4%.
- Moves to **`NO_DEMONSTRATED_INVESTABLE_EDGE`** if: Q3 U.S. comp < −2.0%, or any of the FY2026 outlook items is cut, or the partnering schedule implies flat 2027–28 operating income.
- Otherwise remains `CONTINUE_UNDERWRITING_FOR_SPECIFIC_EVIDENCE` and no purchase is considered.
- Price is *not* a trigger in this record: the base-case entry prices (≈$249 / $231 / $223 for 7% / 9% / 10% IRR) are information, and the fresh price is bound at Stage 7.

## 10. What Atlas found that the frozen pre-Atlas stance did not contain

1. **The stated concern is largely out of date at today's price.** "Quality already fully reflected" was a 2023–25 problem (25.5–25.6x year-end P/E); at $232 the trailing P/E is 18.9x, −32% from the 52-week high. Valuation is no longer the binding constraint.
2. **The binding constraints are different:** (a) U.S. traffic and whether EPS growth can accelerate above the recent ~2.5% (FX-aided) trend; (b) a 5.27% 10-year/4.21% bill hurdle; (c) no demonstrated advantage over SPY.
3. **New primary facts Chris did not state:** the Sept 23 Investor Day (≈$8.5B franchisee partnering; 2030 margin/FCF/G&A targets; capex step-up), the margin target being largely mix-driven, Q2 U.S. guest counts negative with management guiding Q3 slightly negative, a U.S. leadership change, and a near-term dated evidence event (Q3 print).
4. **The $10–15K idea needs one correction:** only $10K–$13,957 is STARTER; $15K is PARTIAL.
5. **The decision is not urgent.** Do Nothing/T-bills cost little to hold for three weeks; waiting for the Q3 print is cheap.

**Capital status: NO REAL PORTFOLIO ACTION.** Human Stage 8 remains sole capital authority. Cycle 1 candidate: MCD. No other candidate was researched.

---

## Addendum 001 — Targeted primary-source evidence check (2026-10-07; append-only)

Scope: narrow check requested after the disposition. The valuation cases, the
frozen pre-Atlas stance (`0a923e2`) and the registered thresholds are unchanged.

**Sources checked:** SEC EDGAR filing list for CIK 0000063908 (latest 8-K = 2026-09-23, Items 7.01/9.01, release only; no slide, transcript or schedule exhibit; no later 8-K); official IR page *Events & Presentations* (lists "Investor Day Press Release" and "2026 Investor Day Select Slides (14 MB)"); official IR events calendar (`mcdonalds2017tf.q4web.com/events-calendar`); the Q2 2026 10-Q.

**FACT (primary — 8-K Ex. 99.1, 10-Q):**
- ~$8.5B total NEXT partnering support through 2036, ~$5B through 2030, "through a combination of rent relief and capital support." Capex 2027–30: ~$3B/yr baseline plus $1.5–2B *cumulative* partnering capital. ~250 bps gross restaurant-level efficiency ≈ ~$100K/yr cash flow per average U.S. restaurant; ~4-year franchisee payback after partnering. Targets: op margin low-to-mid 50% by 2030, G&A ~1.9% of Systemwide sales, FCF conversion mid-to-high 80%, unit contribution ~2.5% (2027) → ~2% (2030).
- **Not published in any SEC filing or the press release:** a year-by-year rent-relief schedule; the rent-relief vs capital split; corporate capital contribution timing by year; remodel/restaurant-investment timing or counts; any operating-income or EPS expectation; any 2027–28 earnings framework; any explicit bridge from the 2030 margin target to earnings-dollar growth.
- 10-Q: "Accelerating the Organization" restructuring runs through 2027 ($795M incurred since 2023; ~$250M expected in 2026) — a GAAP-EPS item, not a NEXT item.

**MANAGEMENT CLAIM (secondary transcript, unverified against the primary slides/webcast):** rent relief/capital amortized in the P&L over ~10 years; margin path driven by comps, G&A to 1.9%, and franchised mix ~95% → ~98% by 2028; no EPS algorithm stated; Q3 U.S. comps "slightly negative".

**INFERENCE (unchanged, still labeled):** rent relief through 2030 ≈ $3.0–3.5B (= $5B − $1.5–2B capital) and ~2.5% of FY2025 operating income by 2030 if amortized over ~10 years. No schedule was published and none is inferred here.

**Not read:** the official *2026 Investor Day Select Slides* PDF. Access from this session returned a file-download response, so the file was not retrieved; downloading it requires explicit user permission. The slides may or may not contain the items above — **UNKNOWN until read**.

**Q3 2026 earnings date (official IR calendar):** *McDonald's Q3 2026 Earnings Conference Call — 11/04/26* (listed as "Upcoming, Quarterly Earnings"). This **supersedes** the October 28 date in §9, which came from a secondary source and is **not** supported by the official calendar. No SEC filing announces the date; the IR calendar entry is the official source. Time of day not captured.

**Effect on prior assumptions:** (1) the Q3 evidence date moves from 10-28 (unverified) to 11-04 (official IR calendar); (2) no valuation case, probability weight, threshold or disposition changes; (3) threshold item "partnering economics consistent with ≥~4% EPS growth in 2027–28" is currently **untestable** on primary evidence (no published framework) — it remains open, not met.

**Thresholds preserved unchanged (pre-registered judgment thresholds, not permanent methodology):** Promotion evidence — Q3 U.S. comp ≥ −1.0%; evidence of U.S. comps turning positive in September/Q4; FY2026 outlook unchanged; partnering economics consistent with roughly ≥4% EPS growth in 2027–28. Negative evidence — Q3 U.S. comp < −2.0%, or a material FY2026 outlook cut.

**Disposition: unchanged — `CONTINUE_UNDERWRITING_FOR_SPECIFIC_EVIDENCE`.** No Stage 7, no Stage 8, no new candidate. **Capital status: NO REAL PORTFOLIO ACTION.**
