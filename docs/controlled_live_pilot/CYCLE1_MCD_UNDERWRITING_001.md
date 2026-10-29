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

---

## Addendum 002 — Official Investor Day "Select Slides" review (2026-10-07; append-only)

Scope: answer only the seven unresolved primary-source questions. Source: the
official 22-slide PDF *2026 Investor Day Select Slides* (company IR site,
`corporate.mcdonalds.com`, ~14 MB; fetched with the user's permission and read
in the browser pane — **no copy is stored in the repo**). Most slides are
charts/graphics, so they were read visually as well as by text extraction. The
slides are a **selection**, not the full deck; the Investor Day webcast replay
was **not** reviewed. Frozen valuation cases, thresholds and the pre-Atlas
stance are unchanged.

| Question | Answer from the slides |
|---|---|
| Year-by-year rent-relief schedule? | **No.** Slide 10 shows only two totals: **~$5B for 2027–2030** and **~$8.5B through 2036**. |
| Split between rent relief and capital support? | **No stated split.** Slide 10 footnote: support "will be through a mix of rent relief and capital support. The mix and level of support will vary by market and be flexible and targeted to the realities franchisees face locally." |
| Corporate capital timing by year? | **No.** Slide 15: capex **2027E–2030E ~$3.0B annually**, **plus cumulative ~$1.5B–$2B capital partnering** to accelerate NEXT deployment (a four-year cumulative range, not annual); FX as of 9/23/2026. |
| Remodel timing / counts? | **No counts, no timing schedule.** Slide 8: incremental investment **~$800K per U.S. restaurant, ~$650–700K IOM**, "investments will be phased over time." Slide 13 gives **new-unit** growth (nearly 4.5% in 2027E, 3.5–3.0% 2028E–2030E; "more than 550 combined U.S. and IOM gross openings annually through to 2030") — not remodels. (The 2026E bar is cropped in my render; not read.) |
| 2027–28 operating-income or EPS framework? | **No.** The only EPS language is qualitative (slide 21: deliver durable comparable sales growth, "support strong EPS growth", reinforce position as a high-quality long-term compounder). No EPS or operating-income dollars or growth rate for any year. |
| Bridge from the 2030 margin target to earnings growth? | **No numeric bridge.** Slide 18: adjusted operating margin **46.9% (2025)**, **mid-to-high 40s (2026E)**, **low-to-mid 50s (2030E)**. Component levers are shown separately without a quantified contribution each: refranchising **~95% (2026) → ~98% (2028E)** (slide 16); G&A **~2.2% (2026E) → ~1.9% (2030E)** of Systemwide sales (slide 17); non-comp sales **~2.5% (2026E, 2027E) moderating to ~2% by 2030** (slide 12); FCF conversion **low-to-mid 80s (2026E) → mid-to-high 80s (2030E)** (slide 19). |
| Anything making the ≥4% EPS-growth threshold testable? | **No.** With no EPS/OI framework, no annual partnering schedule and no quantified bridge, the 2027–28 EPS-growth condition cannot be tested from the slides. It stays open. |

**FACT (primary, slides):** ~250 bps gross restaurant-level efficiency ≈ ~$100K gross annual cash flow for an average U.S. restaurant, with the note that "a portion" will be reinvested in NEXT initiatives but "the majority will benefit the restaurant's bottom line over time" (slide 7); average unit volumes $4M+ (U.S.) / $4.5M+ (IOM) and average franchisee cash flow ~$500K (U.S.) / ~$400K (IOM) (slide 6); **payback ~4 years for franchisees after partnering and ~5–6 years for McDonald's on Restaurant NEXT investments** (slide 11); commitment to the current investment-grade rating and to return excess FCF through dividends and repurchases "over time" (slide 20). The **~5–6-year corporate payback** is new primary evidence not stated in the earlier release or transcript: the program is a mid-single-digit-year, not a quick, return for the parent.

**MANAGEMENT CLAIM:** all of the above targets are forward-looking company estimates. The ~10-year P&L amortization of rent relief, and "support strong EPS growth" quantification, remain **transcript-only/unquantified** — they do **not** appear on the slides.

**INFERENCE (still inference):** the arithmetic that rent relief ≈ ~$5B − ~$1.5–2B ≈ ~$3.0–3.5B through 2030 assumes all non-capital partnering is rent relief. The slide's own footnote (mix and level vary by market, flexible) means the split could differ, so this is softer than previously stated; it is not a published figure. No annual P&L or cash schedule is inferred.

**Effect on prior assumptions:** none invalidated. The slides contain no number that contradicts the valuation cases (5% base EPS CAGR, 19x exit) or the thresholds. The one qualitative addition — a ~5–6-year corporate payback — is consistent with, and slightly reinforces, the "cash cost precedes benefit" risk in §6; it is not used to change any case.

**Thresholds preserved unchanged (pre-registered judgment thresholds, not permanent methodology):** Promotion evidence — Q3 U.S. comp ≥ −1.0%; evidence of U.S. comps turning positive in September/Q4; FY2026 outlook unchanged; partnering economics consistent with roughly ≥4% EPS growth in 2027–28. Negative evidence — Q3 U.S. comp < −2.0%, or a material FY2026 outlook cut.

**Disposition: unchanged — `CONTINUE_UNDERWRITING_FOR_SPECIFIC_EVIDENCE`. MCD is PARKED until the officially scheduled Q3 2026 earnings release/call on 2026-11-04** (official IR calendar). No Stage 7, no Stage 8, no new candidate, no sizing. **Capital status: NO REAL PORTFOLIO ACTION.**

---

## Addendum 003 — R1/R2 research run: reverse valuation, reference cases and benchmark comparison (2026-10-29; append-only)

*What this is.* New, measured evidence on the questions this record left open (a certified price; matched SPY and Treasury/cash comparisons; reverse valuation). It is **descriptive research, not a capital verdict**: MCD stays **PARKED until 2026-11-04**, no stance was written, no allocation is implied, and nothing here promotes it. Facts, market data, assumptions and outputs are labelled; gaps are listed.
Inputs and arithmetic: `atlas_ui/evidence/mcd_r1_r2/` (`fetch_inputs.py`, `run_mcd_r1_r2.py`, the result `MCD_R1_R2_result.json` sha256 `ebb2a2d5c0848993cff30a56d51ef4eb27aba5fd72951f67e5690918817b853e`, the retained U.S. Treasury CSVs); formulas: `atlas_ui/valuation.py` (unit-tested). Recorded in the candidate ledger as seven evidence entries, five open questions, one linked observation and assessment v2 (`DRAFT_BY_RECORDER`).

### 1. Data integrity (checked before any conclusion)
| Check | Result |
|---|---|
| Provider close on 2026-10-28 vs the Gate B bind | $250.50 = $250.50 (equal). The provider's 2026-10-29 bar is an unfinished intraday bar and is excluded. |
| Adjustment convention (prevents double counting) | `adjust=all` is a **dividend-adjusted** series, `adjust=none` raw closes. The adjusted series' return equals raw-close return with reinvested dividends to within 0.3 percentage points in every window tested (MCD 10y +184% vs +184%; SPY 10y +325% vs +326%). **Dividends are never added to the adjusted series** (doing so would overstate MCD's 5-year return by 15 points). |
| Dividends endpoint | **Not on TwelveData's free plan (HTTP 403)**; the earlier benchmark note saying otherwise is wrong. Dividends were inferred from the adjusted/unadjusted ratio and tie to the SEC's declared per-share dividends within 0.9% in every fiscal year 2008–2025 (2.5% in FY2007, the first year). |
| SPY | Same provider method; verified structurally, **not** against a primary distribution record (gap). |
| Treasury | The keyless official CSV reproduces **every** hand-attested value in this record and the RPM record (3-month, 2-year, 10-year on 2026-10-06 and 2026-10-08); latest observation 2026-10-28 (0 days stale); no non-numeric cells. |
| Year-end trailing P/E | Recomputed from provider closes and SEC EPS: 2021–2025 = 26.7x, 31.6x, 25.6x, 25.5x, 25.6x, identical to the table in §3 above (which used uncertified Yahoo closes). |
| The earlier price | The 2026-10-07 reference price was $232.24 (uncertified); the provider's close is **$230.88**. The earlier observation's “+7.9%” becomes **+8.5%** on certified prices. |

### 2. Measured: MCD against SPY and cash (total return; same dates; history, not a forecast)
| Window | Dates used | MCD | SPY | Cash (3-mo par) | MCD−SPY (pts) | MCD−cash (pts) | Annualized MCD / SPY / cash |
|---|---|---|---|---|---|---|---|
| since 2026-10-07 | 2026-10-07 → 2026-10-28 | +8.5% | -0.6% | +0.2% | +9.1 | +8.3 | n/a (<1 year) |
| 1 year | 2025-10-28 → 2026-10-28 | -16.2% | +13.6% | +3.9% | -29.8 | -20.1 | -16.2% / +13.6% / +3.9% |
| 3 years | 2023-10-27 → 2026-10-28 | +5.3% | +95.0% | +14.5% | -89.7 | -9.2 | +1.7% / +24.9% / +4.6% |
| 5 years | 2021-10-28 → 2026-10-28 | +14.6% | +80.1% | +22.0% | -65.6 | -7.5 | +2.8% / +12.5% / +4.1% |
| 10 years | 2016-10-28 → 2026-10-28 | +183.7% | +325.2% | +28.9% | -141.5 | +154.8 | +11.0% / +15.6% / +2.6% |
| full history | 2006-12-13 → 2026-10-28 | +887.1% | +679.2% | +38.2% | +207.9 | +848.9 | +12.2% / +10.9% / +1.6% |

MCD lagged SPY in every window from one to ten years (one year: MCD -16.2% vs SPY +13.6%) and trailed cash over one, three and five years; over the full common history it led SPY (+12.2% vs +10.9% a year). Price is -26.6% from the 52-week high close ($341.06, 2026-02-27); worst peak-to-trough in the last year -32.3%. Relative performance is regime-dependent; this is not evidence of an edge in either direction.

### 3. Reverse valuation: what the price requires (INFERENCE; arithmetic on stated inputs)
Inputs. FACT: price $250.50, FY2025 diluted EPS $11.95 (SEC 10-K), FCF/share $10.03. MARKET DATA: dividend run-rate $7.44/yr (underwriting record; inferred tie-out $7.39). ASSUMPTION: exit on 2030-12-31, dividends scale with EPS. Constant EPS growth from FY2025 needed to earn each hurdle, by exit multiple:

| Hurdle | Hurdle rate | Multiple unchanged (21.0x) | Observed minimum (19.4x) | 12-year median (25.5x) |
|---|---|---|---|---|
| Cash (3-month par yield) | +4.2% | +0.9% | +2.3% | -2.7% |
| 5-year Treasury | +4.8% | +1.4% | +2.8% | -2.2% |
| 10-year Treasury | +5.0% | +1.6% | +3.0% | -2.0% |
| SPY, trailing 10-year total return (history) | +15.6% | +9.8% | +11.4% | +5.9% |
| SPY, total return since 2006-12-13 (history) | +10.9% | +6.2% | +7.6% | +2.4% |

Reading: with the multiple unchanged the price needs only about +0.9% to +1.6% a year of EPS growth to match cash and Treasuries, about +6.2% to match SPY's full-history return and about +9.8% to match SPY's last ten years. EPS growth was +1.7% a year over FY2023–FY2025, the median observed five-year window is +8.9% (range +5.5% to +13.6%) and the ten-year CAGR is +9.6%. Free-cash-flow view: at required returns of 8% / 9% / 10% the price implies perpetual FCF growth of +3.8% / +4.8% / +5.8%. (A negative number under a higher exit multiple means the multiple alone would carry the return.)

### 4. Reference cases (NOT forecasts, NOT probabilities; no expected value)
Each input is an observed reference point from MCD's own history; BASE is the middle reference case, **not the likeliest outcome**. Annual IRR from $250.50 to 2030-12-31.

| Case | EPS growth | Exit multiple | FY2030 EPS | Exit price | IRR | vs cash (4.18%) | vs SPY 10y history (+15.6%) | vs SPY full history (+10.9%) |
|---|---|---|---|---|---|---|---|---|
| BEAR: latest 2-year growth persists; lowest observed year-end P/E | +1.7% | 19.4x | $12.98 | $252 | **+3.4%** | -0.8 pts | -12.2 pts | -7.5 pts |
| BASE: only growth normalizes (median 5-year window); multiple unchanged | +8.9% | 21.0x | $18.32 | $384 | **+14.4%** | +10.2 pts | -1.2 pts | +3.5 pts |
| BULL: growth normalizes and the multiple reverts to the 12-year median | +8.9% | 25.5x | $18.32 | $467 | **+19.5%** | +15.4 pts | +4.0 pts | +8.7 pts |

**What changed since this record's own base case (5% EPS growth, 19x exit, an Atlas judgment):** at the 2026-10-07 close the same assumptions earn +9.1%; at the 2026-10-28 price they earn +7.0%. The +8.5% move alone removed 2.1 points of prospective return.

IRR grid (rows: EPS growth from FY2025; columns: exit P/E):

| EPS growth | 16x | 18x | 20x | 22x | 24x | 26x |
|---|---|---|---|---|---|---|
| 0% | -3.0% | -0.4% | +2.0% | +4.2% | +6.2% | +8.2% |
| 2% | -0.6% | +2.1% | +4.5% | +6.7% | +8.8% | +10.8% |
| 4% | +1.8% | +4.5% | +7.0% | +9.3% | +11.4% | +13.5% |
| 6% | +4.2% | +7.0% | +9.5% | +11.9% | +14.1% | +16.1% |
| 8% | +6.6% | +9.4% | +12.0% | +14.4% | +16.7% | +18.8% |
| 10% | +9.0% | +11.9% | +14.6% | +17.0% | +19.3% | +21.5% |

### 5. What this does and does not establish
- **Established (measured):** the price needs little growth to beat cash and Treasuries but a great deal to beat SPY's recent record; the bear case (+3.4%) is below cash (4.18%); the spread between cases (about 16 points) is mostly the growth regime (recent +1.7% vs long-run +8.9%) plus the multiple; the Oct-7→Oct-28 rally made every case less attractive.
- **Not established:** that the long-run growth regime returns (the only evidence for it is management's Investor-Day claims, already recorded as MANAGEMENT CLAIM), any advantage over SPY, or any probability. **No edge is demonstrated.** The question is now sharply testable on **2026-11-04** (Q3 results; the pre-registered thresholds above still apply) and, later, by the retained reference cases (R4: compare outcomes with these recorded IRRs, SPY and cash, assumptions unchanged).
- **Gaps (also recorded as open questions):** no forward EPS, guidance schedule or partnering phasing is evidenced; scenarios start from FY2025 EPS ($11.95), below the TTM $12.31 in §3; dividends inferred (the paid endpoint is unavailable); SPY adjustment verified structurally only; cash is a par-yield proxy, not a fund return; taxes and costs not modeled.

### 6. Treasury source evaluation (R2.1): evaluated, NOT integrated
Source: U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates, CSV (home.treasury.gov), keyless, one read-only GET per year; 5211 daily rows 2006-01-03 → 2026-10-28; PRIMARY if integrated. Findings: complete and numeric; reproduces all six hand-attested values; fresh to the cutoff; the only daily moves over 50 bp in the 3-month or 10-year series are six, all in 2007–2009 (stress periods; real, not data errors). **Schema drift:** the CSV gained columns over time (11 in 2015, 14 from 2025), so a parser must select columns by name. **Not verified by software:** the site's terms of use.
Governance approvals needed **before any integration** (none is assumed): (1) the human's explicit approval of a new data source (standing rule: no new provider without authorization); (2) confirmation of the terms of use; (3) because a funded Stage 8 requires a human re-attested Treasury reference (frozen-control change 001), an automated source may only *inform or pre-fill* that attestation unless a frozen-control change record is separately authorized; (4) a staleness policy (a last observation older than N days is UNKNOWN); (5) a retention decision (public data; the CSVs are retained here with SHA-256). Until then the Treasury inputs in this addendum are an evaluation artifact, not a Stock Atlas data feed.

**Capital status: NO REAL PORTFOLIO ACTION.**
