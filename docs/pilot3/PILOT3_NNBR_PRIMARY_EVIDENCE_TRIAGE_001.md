# PILOT 3 — NNBR PRIMARY-EVIDENCE TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Third Batch 003 candidate to receive primary-evidence triage, and the
> third record governed by the two narrow fixes
> (`pilot3/PILOT3_BATCH_003_CHARTER.md`).

| | |
|---|---|
| Date | September 14, 2026 |
| Batch | `PILOT3_BATCH_003_REGISTRATION.md` |
| Candidate | NNBR — NN, Inc. |
| Source | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY`, as-of 2026-09-12 |
| Prior state | `SURFACE_FOR_TRIAGE` |

---

## 1. Canonical identity — verified, no ambiguity

- **Issuer:** NN, Inc., **Nasdaq Global Select Market**, ticker **NNBR**,
  **MIC `XNGS`**, SEC CIK `0000918541` — confirmed directly against SEC
  EDGAR company submissions and independently against the provider's
  `symbol_search` (a single, unambiguous U.S. common-stock match, plus a
  secondary IEX quote of the same instrument — not a collision).
- **Security type:** common stock (SIC 3540, Metalworking Machinery &
  Equipment).
- **No ambiguity found or fail-closed condition triggered.**

---

## 2. Discovery hook — restated, treated as tentative

> NNBR may be undergoing an underappreciated business-mix shift as new
> programs in data-center liquid cooling, defense, and medical precision
> manufacturing ramp alongside preferred-equity cleanup and growth-
> capacity investment.

Per instruction, **"data center," "AI," "new business wins," and
capacity additions are not credited as edge by themselves** — each is
tested against primary evidence below.

---

## 3. Primary evidence reviewed

- **8-K filed 2026-09-09** (accession `0000918541-26-000087`, exhibit
  `nn-form8xk2026x09x10inve.htm`, an investor presentation used at the
  Lake Street Capital Markets Investor Conference).
- **8-K filed 2026-08-05** (accession `0000918541-26-000065`, exhibits
  `pressrelease2026-q2.htm` and an earnings presentation) — Q2 2026
  results, referencing the post-quarter refinancing.
- **8-K filed 2026-07-01** (accession `0001104659-26-079868`) — the
  actual $75.0 million common-stock private placement (Items 1.01, 3.02).
- **10-Q for Q2 2026** (accession `0000918541-26-000064`) — Series D
  preferred-stock footnote and subsequent-events disclosure.
- **Earnings-release exhibits for Q1 2026, Q4/FY2025, and Q3 2025**
  (accessions `0000918541-26-000034`, `0000918541-26-000007`,
  `0000918541-25-000149`) — used for the Fix 1 4-period reconstruction.
- **SEC XBRL company facts** (CIK `0000918541`) — common shares
  outstanding, long-term debt, cash, operating cash flow, capex.
- **Equity price series** (TwelveData), 2026-07-20 through 2026-09-14 —
  checked directly.

**Evidence gap, disclosed up front:** the FY2025 10-K's own Series D
preferred-stock footnote (Item 8, notes to financial statements) could
not be retrieved in full through the fetch tooling used — a filing-size
limitation this pilot has hit before with large 10-Ks. This record relies
instead on the Q2 2026 10-Q's comparative disclosure and the earnings
release/8-K language for the preferred-structure figures in §4, and
**flags rather than papers over** the resulting reconciliation gaps.

---

## 4. Refinancing / preferred cleanup — reconstructed, only partially reconciled

**The transaction was executed in two, dated steps, not one:**

1. **July 1–2, 2026 — $75.0 million common stock private placement:**
   **24,509,804 new shares** at **$3.06/share** (a discount to the
   prevailing ~$3.4–3.5 price seen in the weeks that followed),
   **~$70.4 million net proceeds** after a ~6.0% placement-agent fee.
   Registration rights required resale registration within 45 days
   (fulfilled via the S-3/424B3 filed July 13/21, 2026).
2. **August 5, 2026 — Series D Preferred Stock redemption and
   exchange:** **9,850 shares of Series D Preferred Stock** redeemed/
   exchanged, in part for **5,500,000 newly issued common shares**, "the
   Exchange" explicitly **conditioned on the concurrent consummation of
   the Redemption" — i.e., a combined cash-and-stock transaction, not a
   pure stock swap. Separately, the Q2 2026 earnings release states
   **"approximately $89 million of the preferred stock"** was "paid off."

**Series D structure, as disclosed (Q2 2026 10-Q, pre-transaction):**
initial liquidation preference **$1,000/share**; initial dividend rate
**10.0%**, stepping up **+2.5%/year** (reaching **14.5%** by March 2026);
PIK election available through April 2027, with a further step-up to
**12.0%** if cash dividends are not paid; **carrying value $122.1
million**, of which **$75.5 million is accumulated unpaid/deemed
dividends** — meaning the preferred's compounding cost has already
roughly **doubled** its effective value well above the original $1,000/
share face.

**This record's reconciliation, and where it breaks down:** the $122.1M
carrying value is consistent with **65,000 shares outstanding**
pre-transaction at an effective accreted value of roughly **~$1,880/
share** (65,000 × ~$1,880 ≈ $122.2M) — **not** the "65 shares" figure
that appeared in one fetched extraction, which this record treats as a
scale/units error in that extraction rather than fact. On that basis,
**the 9,850 shares specifically identified as exchanged represent only
about 15% of the pre-transaction Series D balance** — implying **roughly
55,150 shares (~85%) may remain outstanding**, still accruing the 14.5%+
compounding coupon, **unless a separate, larger cash-redemption tranche
not captured by the "9,850 shares" figure accounts for the bulk of the
"$89 million paid off."** **This record could not fully reconcile the
$89M headline figure against the 9,850-share exchange figure from the
primary sources reviewed** — a genuine, load-bearing, disclosed evidence
gap, not resolved by inference.

**No warrants** to preferred holders or placement agents were found in
connection with either transaction. Pre-existing, unrelated warrants
(2019 and 2023 vintages) were mostly exercised or cancelled during H1
2026 and are not part of this transaction.

**Net share-count effect, confirmed via XBRL:** common shares outstanding
were **52.574 million at June 30, 2026** (pre-transaction). Adding the
24.510M private-placement shares and the 5.5M preferred-exchange shares
gives a pro forma **~82.58 million shares — a ~57% increase** in share
count from these two actions combined. **This is a very large dilution
event, materially larger in percentage terms than Scout's hook framing
("preferred-equity cleanup") suggests on its own.**

**Answering the work order's question directly: this record cannot
confirm the transaction materially improved common-equity economics
rather than merely pushing a difficult capital structure forward.** Real
progress occurred (some preferred cleared; new capital came from equity
rather than more debt), but a large share of dilution has already been
absorbed by common holders, and the fraction of the punitive,
compounding Series D coupon actually eliminated **could not be
confirmed** from evidence gathered — this is the single most important
open question this record identifies (see §19).

---

## 5. Narrow Fix 1 — hook reconstruction (5 reporting periods)

| Metric | Q3 2025 | Q4 2025 | Q1 2026 | Q2 2026 | Sept 9, 2026 update |
|---|---|---|---|---|---|
| Revenue | $103.9M | $104.7M | $118.5M | **$128.7M** | — |
| Revenue YoY | **−8.5%** | **−1.7%** | **+12.1%** | **+19.3%** | — |
| Adjusted EBITDA | $12.4M | $12.9M | $14.1M | **$17.9M** | — |
| EBITDA margin | 11.9% | 12.3% | 11.9% | **13.9%** | — |
| New-business-wins guide (FY2026) | — | $70–80M (initial) | $80–90M | $80–100M | **$90–110M** |
| Data Center & Electric Grid revenue | — | — | — | **~$80M TTM** | ~$80M TTM (reaffirmed) |
| Capex (quarterly) | $11.1M (9mo cumulative) | $12.9M (FY cumulative) | $3.3M | $5.2M (implied, $8.5M 6mo) | guided "$35–40M" (annual) |

**What the reconstruction shows, plainly:**

1. **Revenue growth has accelerated for three straight quarters**
   (−8.5%→−1.7%→+12.1%→+19.3%) — a real, monotonic, primary-sourced
   trend, not a single good quarter.
2. **EBITDA margin expanded meaningfully in the most recent quarter**
   (11.9%→13.9%), though the three prior quarters were roughly flat
   (11.9%–12.3%) — the margin story is newer and less established than
   the revenue-growth story.
3. **New-business-wins guidance has been raised at every single update
   in the last year** ($70–80M → $80–90M → $80–100M → $90–110M) — a
   genuine, repeated, not one-off, positive revision pattern.
4. **Data Center & Electric Grid revenue (~$80M TTM) is confirmed as
   fact**, not merely cited by Scout — directly verified in the
   September 9 investor presentation.
5. **The auto/non-auto mix shift is real and substantially executed
   already, not merely promised:** the same presentation states the
   sales mix moved from **"Auto 65% / Non-Auto 35%" in 2023** to **"Auto
   40% / Non-Auto 60%" by Q2 2026** — a large, already-realized
   diversification, not an aspiration.
6. **Per instruction, this record does not substitute the cumulative
   new-business-wins award figure for recognized revenue** — the
   guidance figures above are management's own forward award/booking
   metric, tested for conversion quality separately in §6.

**Per Fix 1's rule:** the hook's core operating claims (growth
acceleration, margin improvement, mix shift, data-center revenue) **do
not disappear or reverse under reconstruction — they strengthen.** This
is a materially different outcome than this record found for NHP or UCB.
The **capital-structure** half of the hook (§4) is the piece that does
not reconstruct cleanly.

---

## 6. New-business-wins economics — tested, not accepted at face value

- Scout's cited figures (2026 midpoint ~$100M, up from ~$90M) are
  **confirmed, precisely**: the Aug 5 release guided $80–100M (mid $90M,
  "29% growth over 2025 at the midpoint"); the Sept 9 update raised this
  to $90–110M (mid $100M).
- **This is management's own annual new-business-win award metric — an
  awarded/booked program value, not recognized revenue** — the sources
  reviewed do not disaggregate it into contractual/near-certain versus
  aspirational conversion, and **do not disclose a specific conversion
  timeline, cancellability terms, or customer-funded tooling
  requirements.** **This is a genuine evidence gap.** Per instruction,
  **this record does not assume 100% conversion** — the wins figure is
  treated as a forward-looking award pipeline, not booked revenue, and
  its eventual conversion is exactly the kind of question the falsifier
  (§17) is built to test.

---

## 7. Data-center / liquid-cooling economics

- **~$80 million TTM (Q2 2026) Data Center & Electric Grid revenue** —
  confirmed, primary-sourced, real, current revenue, not a projection.
- **"~$120 million" is explicitly labeled a "near-term goal" in the
  investor presentation, not formal guidance** — a meaningful
  distinction this record preserves rather than blurs; it carries less
  certainty than the $90–110M new-business-wins range, which is
  presented as guidance.
- **~60 new CNC machine centers in NN's Wuxi plant, explicitly tied to
  "Southeast Asia AI Data Center supply chains"** — confirmed, a real,
  disclosed capacity commitment, not merely a narrative claim.
- **Customer concentration, gross-margin profile specific to this
  sub-segment, working-capital requirements, and whether Wuxi capacity is
  dedicated or fungible with other end markets: not disclosed** in
  sources reviewed — genuine evidence gaps.

**Answering the work order's core question directly:** at ~$80M TTM
against total Q2 2026 annualized revenue of ~$515M (4×$128.7M), Data
Center & Electric Grid is currently **an attractive, real, but still
modest-sized sub-segment (roughly 15–16% of the annualized total) — not
yet large enough on its own to transform consolidated economics**, though
it is a genuine, disproportionate contributor to the growth
**acceleration** shown in §5, alongside the broader mix shift.

---

## 8. Legacy business drag — load-bearing, answered directly

- **The auto/non-auto mix shift (§5) is the single strongest piece of
  evidence that faster-growing end markets are creating net company
  growth, not merely offsetting a shrinking legacy base:** total revenue
  itself has accelerated from −8.5% to +19.3% YoY over four quarters
  **while** the auto share of the mix fell from 65% (2023) to 40% (Q2
  2026) — this is only mathematically possible if non-auto revenue grew
  fast enough to both replace lost/flat auto revenue **and** drive
  positive, accelerating **total** company growth.
- **Automotive-specific revenue trend, China-specific revenue exposure,
  industrial end-market detail, and customer concentration are not
  separately quantified** in the sources reviewed beyond the aggregate
  mix percentages — a genuine evidence gap on the "how much is legacy
  still dragging" question, even though the aggregate arithmetic
  supports a "net growth," not "mere offset," conclusion.

**Answering the work order's question directly: on the evidence
gathered, faster-growing end markets are creating real net company
growth**, not merely offsetting legacy weakness — this is the strongest,
most directly falsifiable piece of corroboration this record found for
Scout's hook.

---

## 9. Capex and capacity economics

- **Guided capex: "$35–40 million"** annually, described as "capex
  averaging 30 cents per annual sales-rate dollar" — i.e., management's
  own framing ties capex directly to the revenue run-rate, not to a
  fixed dollar target independent of growth.
- **Maintenance-versus-growth split, expected utilization, expected
  incremental revenue/EBITDA from the new capacity, and payback period:
  not disclosed** in sources reviewed — a genuine, load-bearing evidence
  gap. **Per instruction, this record does not award credit for capacity
  merely because it exists** — the Wuxi CNC additions and the $35–40M
  capex guide are recorded as facts, not credited as value-creating
  without disclosed return evidence.
- **Cross-check against actual spend:** H1 2026 capex was $8.5M
  (Q1 $3.3M + Q2 ~$5.2M) — annualizing to roughly $17M, well **below**
  the $35–40M full-year guide, implying a significant back-half-loaded
  ramp that has not yet occurred and is not yet evidenced in actuals.

---

## 10. Cash flow quality

- **Operating cash flow swung sharply**: Q1 2026 **used** $8.6M; the
  six-month 2026 cumulative figure is **+$11.8M**, implying **Q2 2026
  alone generated approximately +$20.4M** — a large, real, positive swing
  in the same quarter revenue and EBITDA accelerated.
- **FY2025 operating cash flow was only $5.7M** for the full year, with
  $12.9M of capex — i.e., **free cash flow was negative for all of
  2025** on a straightforward OCF-minus-capex basis.
- **Interest expense, preferred dividends paid/accrued, and lease
  obligations are not separately reconciled** against the OCF figures
  above in sources reviewed — a genuine evidence gap that limits how
  confidently this record can answer "can the business fund the growth
  program while reducing balance-sheet risk" on a fully-loaded basis.

**Answering the work order's question directly: cash-flow quality has
genuinely improved in the most recent quarter, but the base the company
is improving from was weak (negative FCF for all of 2025)** — this
record treats the Q2 2026 swing as a real, positive, single-quarter data
point, not yet a confirmed trend.

---

## 11. Preferred-equity overhang — answered with the reconciliation gap named plainly

Per §4, **this record cannot state with confidence how much of the
Series D overhang remains** after the August transaction — the two
headline figures available ("9,850 shares exchanged" and "~$89 million
paid off") do not cleanly reconcile against each other or against the
pre-transaction $122.1M/65,000-share base without an assumption this
record is not willing to make without better evidence.

**If the 9,850-share figure is the complete picture,** roughly 85% of
the Series D balance (by share count) remains outstanding, continuing to
accrue a 14.5%+ compounding coupon — in which case **clearing the
preferred is only partially done**, and continues to consume future cash
flow and dilution capacity rather than being resolved.

**If the $89 million figure reflects a much larger cash redemption not
separately itemized in the sources reviewed,** the cleanup could be
substantially more complete than the share-count arithmetic alone
suggests.

**This record does not resolve which is closer to correct — this is the
single most important open question identified in this triage, and is
classified accordingly in §19.**

---

## 12. Cheapest falsification test

> Are the new-business wins converting quickly enough, at sufficiently
> attractive economics, to outweigh legacy-business drag and the capital
> required to fund the ramp?

**Partially supported, not clearly "no," but not fully confirmable
either.** The revenue/EBITDA/mix-shift evidence (§5, §8) supports "yes"
on the operating side — growth is real, accelerating, and net of legacy
drag. But **"the capital required to fund the ramp" includes both the
capex program (§9, not yet evidenced at its guided run-rate) and the
~57% share dilution already incurred (§4)** — and this record cannot
confirm the operating improvement's per-share benefit exceeds the
dilution's per-share cost without resolving the preferred-overhang
question in §11. **Per instruction, since the answer is genuinely mixed
rather than a clean "no," this record does not close the file here — it
treats the unresolved capital-structure reconciliation as the specific
task for deep underwriting**, consistent with how this pilot has handled
similarly genuine, evidence-gatherable splits before (AVGO, DOCU, SPXC,
SOLS).

---

## 13. Narrow Fix 2 — priced-in one-liner

> For NNBR to be mispriced positively, the market must currently be
> assuming that the ~57% share dilution from the private placement and
> preferred exchange — combined with a Series D overhang that may remain
> substantially intact — more than offsets the genuine, accelerating
> revenue and EBITDA momentum and the already-executed mix shift, when in
> fact the dilution-adjusted per-share economics are better than the
> market currently reflects.

**This sentence can be stated credibly** — real, quantified dilution and
real, quantified operating momentum both exist to hang it on — so Fix 2
does not veto this record. **Unlike NHP and UCB, this record's own
evidence does not clearly refute this one-liner** — the operating side
of the ledger is genuinely strong, and the capital-structure side is
genuinely unresolved rather than affirmatively negative. This is exactly
the profile Fix 2 is meant to let through to deep underwriting, not
screen out.

---

## 14. Valuation checkpoint — coarse, explicitly not falsely precise

**Fresh-price bind attempted first, per instruction.** A same-day
(2026-09-14) Gate B bind was attempted and correctly returned `STALE`:
the market was open at decision time, so no new completed session
existed beyond the prior one to certify.

```
security_key: SEC-CIK:0000918541:NNBR
mic: XNGS
attempted decision time: 2026-09-14 (market open) -> STALE, not forced
last confirmed completed-session close: $3.58, session 2026-09-11
52-week range (raw observation, context only): $1.10 - $4.48
```

Per instruction, this record does not force an intraday bind — the last
independently-confirmed completed-session close ($3.58) is used below
with this limitation stated plainly.

- **Reference price:** **$3.58** (last confirmed completed-session
  close, 2026-09-11).
- **52-week range:** $1.10–$4.48 — the stock is already **up
  roughly 220%** from its 52-week low, and specifically **up ~24% over
  two weeks** following the August 5 earnings/refinancing announcement
  before giving back about half that move.
- **Pro forma shares outstanding** (post both dilutive actions, per §4):
  **~82.6 million.** **Market capitalization at the reference price:
  ~$296 million.**
- **Net debt / EV: this record does not compute a single precise
  figure** — the $89M "paid off" preferred figure's cash-versus-stock
  composition (§4, §11) is not resolved cleanly enough to state a
  confident post-transaction net-debt number. Using the pre-transaction
  Q2 2026 balance sheet only (total debt ~$166.7M, cash $16.45M, net
  debt ~$150.3M) against Q2 2026's annualized Adjusted EBITDA run-rate
  ($17.9M × 4 = $71.6M): **a coarse, labeled EV/EBITDA of roughly 6x**
  (EV ≈ $296M + $150M ≈ $446M ÷ $71.6M ≈ 6.2x) — **this is an
  illustration, not a precise or company-confirmed figure**, given the
  unresolved net-debt reconciliation.
- **FCF yield:** not meaningfully computable given negative FY2025 FCF
  and only one quarter of strongly positive OCF (§10).

**Answering the work order's question directly:** the current price
already embeds **substantial** credit for the growth story — the stock's
220% rise off its 52-week low and its sharp reaction to the August
news are themselves evidence the market has not been asleep at the
wheel. **This record does not use cheapness (a coarse ~6x EV/EBITDA) by
itself as evidence of edge**, per instruction — that multiple is
consistent with, not obviously cheaper than, a company carrying real
dilution and capital-structure uncertainty alongside real growth.

---

## 15. Market reaction — checked directly, not assumed

| Date | Close | Note |
|---|---|---|
| 2026-07-31 | $3.31 | Before the Aug 5 earnings/refinancing news |
| 2026-08-05 | $3.90 | Earnings + refinancing day |
| 2026-08-06 | $3.87 | Volume spiked to ~14x average (13.9M shares) |
| 2026-08-17 | **$4.11** | Peak — **+24.2%** from July 31 |
| 2026-08-31 | $3.43 | Giving back most of the gain |
| 2026-09-08 | $3.74 | Day before the investor-conference presentation |
| 2026-09-09 | $3.68 | Investor-conference day — down, not up |
| 2026-09-11 | $3.58 | Latest completed session — down further |

**The market reacted strongly and positively to the August 5 news**
(+24% over two weeks) — a real, substantial re-rating, not a muted
response. It has since **given back roughly half that move**, and the
**September 9 investor presentation (raised new-business-wins guidance,
confirmed data-center figures) did not trigger a fresh rally — the stock
fell over the following two sessions.** Per instruction, this record
does not treat the earlier positive move as proof of edge, nor read too
much into the more recent pullback — but the pattern (strong initial
re-rating, partial reversal, no reaction to incrementally positive
follow-up disclosure) is consistent with **a market that has already
absorbed much, though perhaps not all, of this story**, echoing what
this pilot found at NHP and UCB.

---

## 16. Market-could-be-right case

- **New-business-wins figures are an awarded/booked metric, not
  recognized revenue** (§6) — a reasonable investor could discount them
  heavily pending disclosed conversion evidence.
- **The Series D overhang may remain ~85% intact** (§11) — a reasonable
  investor could conclude the "preferred cleanup" is more symbolic than
  substantive, with a large, expensive, compounding claim still standing
  ahead of common equity.
- **~57% dilution has already occurred** — a reasonable investor could
  argue any operating improvement must first overcome this before common
  per-share value genuinely improves, and this record cannot yet confirm
  it does.
- **The $120M data-center figure is explicitly a "goal," not guidance**
  — a reasonable investor could treat it as aspirational until formalized.
- **Capex actuals are running well below the guided $35–40M annual
  rate** — a reasonable investor could question whether the back-half
  ramp implied by guidance will actually occur.
- **FY2025 free cash flow was negative**, and only one quarter of strong
  OCF exists — a reasonable investor could want more than one data point
  before crediting a durable cash-generation improvement.
- **The stock is already up 220% from its 52-week low and reacted
  sharply to the initial good news** — a reasonable investor could
  conclude the market has not under-reacted to this story at all.

**This case is credible, built entirely from this record's own findings,
and is not a strawman.**

---

## 17. Tentative variant — refined, not rejected

> NNBR may be moving from a legacy precision-components profile toward a
> higher-growth, higher-margin mix led by data-center, defense, and
> medical programs, while capital-structure cleanup and capacity
> additions allow those wins to translate into materially better
> per-share economics than the market currently expects.

**Refined, not rejected.** The **operating** half of this variant
(mix shift, growth acceleration, margin expansion) is well corroborated
and, per §5, actually **strengthens** under reconstruction. The
**capital-structure** half ("cleanup... allow[ing] wins to translate
into materially better per-share economics") is the part this record
cannot yet confirm — the dilution is large and confirmed; the extent of
genuine preferred-overhang relief is not. **The variant survives as a
live, evidence-gatherable question, not as a settled conclusion in
either direction.**

---

## 18. What Atlas added beyond the original Scout hook

- **Quantified the actual dilution** (~57% combined share-count increase
  from the private placement and preferred exchange) — a cost dimension
  Scout's "preferred-equity cleanup" framing did not surface.
- **Identified a specific, load-bearing reconciliation gap** between the
  "9,850 shares exchanged" and "~$89 million paid off" figures, implying
  the Series D overhang may remain roughly 85% intact — a materially
  more cautious read than "cleanup" implies on its face.
- **Distinguished "goal" from "guidance"** for the $120M data-center
  figure, and confirmed the $80M TTM figure as fact rather than
  projection.
- **Confirmed the auto/non-auto mix shift as already substantially
  executed** (65/35→40/60), not merely underway — a stronger, more
  concrete finding than Scout's "ramp alongside" framing implied.
- **Found capex actuals running well below the guided annual rate**,
  implying a back-half ramp not yet evidenced.
- **Checked the actual market reaction directly** and found a
  substantial initial re-rating (+24%) that has partially reversed, with
  no fresh reaction to the September investor-day update — evidence the
  market has already engaged with, not ignored, this story.

**Per instruction, this record does not force a finding beyond what the
evidence supports** — the net effect of these additions is to leave the
operating thesis stronger and more concrete, and the capital-structure
thesis more uncertain, than Scout's original hook presented either.

---

## 19. Uncertainty classification

> **`THESIS_BLOCKING_UNCERTAINTY`**

The unresolved reconciliation between the Series D preferred's
pre-transaction balance (65,000 shares / $122.1M carrying value) and the
August transaction's disclosed figures (9,850 shares exchanged / "~$89
million paid off") is classified as thesis-blocking, not merely a
potential source of edge, **because the entire promotion thesis — that
capital-structure cleanup lets genuine operating improvement translate
into better per-share economics — depends on knowing how much of the
preferred's compounding, dilutive claim actually remains.** If the
overhang is substantially resolved, the operating momentum found in
§5–§8 would likely support promotion; if ~85% remains, as the share-count
arithmetic implies, continued heavy dilution and coupon accrual could
absorb most or all of the per-share benefit the operating improvement
would otherwise create. **This is a Pilot 3 learning observation about
this record, not a permanent architecture field or a score.**

---

## 20. Final triage disposition

> ## `PROMOTE_TO_DEEP_UNDERWRITING`

Unlike NHP and UCB, this record's mandatory hook reconstruction (Fix 1)
did **not** kill or neutralize Scout's operating thesis — revenue growth
accelerated for three consecutive quarters, EBITDA margin expanded in
the most recent quarter, new-business-wins guidance has been raised at
every update for a year, the data-center revenue figure is confirmed
fact, and the auto/non-auto mix shift is real and substantially already
executed, not aspirational. The priced-in one-liner (Fix 2) can be
stated credibly and is not contradicted by evidence gathered. What
remains unresolved — the true extent of Series D preferred relief, the
resulting genuine dilution-adjusted per-share economics, whether the
$120M data-center figure becomes guidance, and whether capex converts to
revenue at the rate implied by the still-unrealized back-half ramp — are
exactly the kind of load-bearing, evidence-gatherable questions deep
underwriting exists to resolve, not reasons to close the file here.

**Deep underwriting has not begun.** No return band, position size, or
capital comparison is constructed by this record.

---

## 21. Confirmation — other Batch 003 candidates and all prior states unchanged

NHP remains `NO_DEMONSTRATED_EDGE`
(`PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`). UCB remains
`NO_DEMONSTRATED_EDGE`
(`PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_001.md`). SAIA and TCS remain
registered only (`SURFACE_FOR_TRIAGE`) — **not triaged by this record**,
per instruction. All other Pilot 3 states are unchanged: PATH, MDB, XOM,
PCG `NO_DEMONSTRATED_EDGE`; DOCU, SPXC, SOLS
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AAPL `EVIDENCE_GAP`; JPM `CALENDAR_HOLD` (not advanced); SMH
`REFERENCE_PEER_TAPE`; NVDA `REFERENCE_ONLY`.

---

## 22. Shadow sentiment

No sentiment observations were encountered or used in this record. Had
any arisen, they would have been labeled `SHADOW` and excluded from the
disposition, per the Batch 003 charter.

---

## What this record does not do

No deep underwriting of NNBR. No triage of SAIA or TCS. No Stage 7 or
Stage 8. No capital allocated. No scoring, ranking, or new engine. No
advance of JPM or AAPL. No Batch 004.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## Addendum — Series D reconciliation resolved (2026-09-15)

**This record is frozen above this line. Nothing above is rewritten.
This addendum only appends a resolution finding**, per the historical-
integrity/append-only discipline this pilot has followed since the SOLS
record (`PILOT3_SOLS_POST_MERGER_PRIMARY_EVIDENCE_TRIAGE_001.md`
addendum).

**Primary source located and reviewed:** the actual Series D Preferred
Stock **Exchange Agreement**, filed as an exhibit to the Q2 2026 10-Q
(`nn-exchangeagreement.htm`, accession `0000918541-26-000064`) — the
legal document itself, not press-release shorthand, per instruction.

### The reconciliation, resolved plainly

- **Pre-transaction:** Holder (identified in the agreement as **NHTV
  Nevada Holdings LP**) held **65,000 shares** of Series D Preferred
  Stock — confirmed directly from the agreement's own recital, matching
  this record's own carrying-value cross-check (§4, above).
- **The Exchange:** **9,850 shares** exchanged for **5,500,000** newly
  issued common shares — as previously found.
- **The Redemption (the piece this record could not previously locate):**
  a **separate, concurrent cash redemption of 36,750 additional Series D
  shares**, exercised via a Notice of Redemption under the original
  Certificate of Designation (filed March 22, 2021). The exact per-share
  cash redemption price is not stated in the Exchange Agreement itself
  (it resides in the Certificate of Designation formula, not re-derived
  here) — a residual, minor, non-blocking evidence gap.
- **Remaining after both actions:** **65,000 − 9,850 − 36,750 = 18,400
  shares** — confirmed arithmetic, directly from the agreement.
- **Independent cross-check, primary-sourced:** NN, Inc.'s special-
  meeting proxy statement (DEF 14A, filed 2026-08-28, accession
  `0000918541-26-000083`) states **"As of August 5, 2026, we had
  90,000,000 authorized shares of common stock of which 82,580,864
  shares were issued and outstanding."** Working forward from the
  pre-transaction base (52,574,000 shares at June 30, 2026, per XBRL)
  plus the 24,509,804-share private placement plus the 5,500,000
  Series D exchange shares reconciles to 82,583,804 — within a few
  thousand shares of the proxy's own 82,580,864 figure (the small
  residual is consistent with ordinary RSU vesting/withholding activity
  in the interim, not a sign of any additional, unaccounted-for Series D
  issuance). **This independently confirms no Series D shares beyond the
  9,850/5.5M exchange were converted into common stock by August 5,
  2026** — the 36,750-share piece was genuinely a cash redemption, not a
  second, hidden stock conversion this record had missed.
- **The same proxy explicitly states:** *"We do not currently have any
  definitive agreements or arrangements to issue any of the [additional
  authorized] shares"* — directly refuting this record's earlier
  speculative hypothesis that the proxy's requested doubling of
  authorized shares (90M→180M) was earmarked for a further, pending
  Series D conversion. **That hypothesis is retracted**; the share-
  authorization increase is generic capital-raising/M&A flexibility
  language, unconnected to Series D.

### The "$89 million paid off" figure — reconciled, not merely asserted

Using this record's own carrying-value-per-share estimate (§4:
$122.1M ÷ 65,000 shares ≈ **$1,878.5/share** average accreted value),
**46,600 shares addressed (9,850 exchanged + 36,750 redeemed) × ~$1,878.5
≈ $87.5 million** — within roughly $1.5 million of the earnings
release's "**approximately $89 million**" headline. **This is a clean,
credible reconciliation**, not a forced one: the earnings release's
figure describes the combined liquidation-preference-plus-accrued-
dividend value of both the Exchange and the Redemption together, not
just one piece of it.

### The December 31, 2026 discount — confirmed, precisely

Section 5.4 of the Exchange Agreement provides that if the Company
achieves a **"Final Redemption"** of the entire remaining Series D
balance **by December 31, 2026**, the aggregate redemption price payable
is **reduced by $5.0 million (not below zero)** — this is the discount
the original work order asked this record to verify, now confirmed
directly from the primary legal document.

### The remaining 18,400 shares — real, temporarily lighter burden

Section 5.3 of the Exchange Agreement sets a **"Rate Adjustment
Period"** running from the August 5, 2026 closing date through its first
anniversary (August 2027): during this window, **both the cash and PIK
dividend rates on the remaining shares are reduced to 10.0% per
annum** (down from the pre-transaction 14.5%+ and rising trajectory).
After the Rate Adjustment Period, rates **revert to 15.0% and 17.0% per
annum** respectively, with a further **+2.5%/year step-up beginning
March 22, 2028** if the balance is still outstanding. **No shareholder
vote or Nasdaq approval was required for this transaction** — the
agreement states this explicitly — confirming the special-meeting proxy
(above) is unrelated to Series D.

### Common-equity economics — recalculated on resolved facts

- **New shares created:** 24,509,804 (private placement) + 5,500,000
  (Series D exchange) = **30,009,804**, against a pre-transaction base
  of 52,574,000 — **≈57.1% dilution**, confirmed, matching this record's
  original estimate exactly.
- **Preferred obligation eliminated:** 46,600 of 65,000 shares —
  **≈71.7%** of the pre-transaction Series D balance, its full 14.5%+
  compounding coupon extinguished on the retired portion. **This is
  materially more complete than this record's original, appropriately
  cautious ~15% reading** — the worst-case interpretation named in the
  original triage did not materialize.
- **Preferred obligation remaining:** 18,400 shares (~28.3%), carrying
  value roughly **$34.6 million** (18,400 × ~$1,878.5), temporarily
  accruing at the reduced 10.0% rate (~$3.5 million/year) through August
  2027, reverting to 15–17% (~$5.2–5.9 million/year) thereafter absent
  further redemption — with a real, quantified $5.0 million incentive to
  eliminate it entirely by year-end 2026.
- **Was this economically attractive for today's common holders, or
  merely a shift in difficulty? Answered directly, not by leverage
  improvement alone:** the exchange ratio (9,850 preferred shares for
  5,500,000 common shares) implies each preferred share was valued at
  roughly **558 common shares** — at the $3.06 private-placement price,
  ≈$1,707/share; at the $3.90 closing price on the Exchange's effective
  date, ≈$2,176/share — **both at or above** the ~$1,878.5/share average
  carrying value used above. **This record does not find that common
  holders received a bargain in the exchange ratio itself** — the
  preferred was retired at roughly fair value to a premium, not at a
  discount, funded by real, substantial (57.1%) dilution. **The genuine
  economic benefit is not "cheap retirement," it is de-risking**:
  replacing an escalating, compounding, senior-to-common claim with
  fixed, already-issued, pari passu common shares removes a structurally
  worsening overhang in exchange for a one-time, now-capped dilution —
  a real trade-off, not a one-sided win, and not evaluated here merely
  on whether leverage or CET1-style metrics improved.

### Updated uncertainty classification

> ## `RESOLVED_SUPPORTS_THESIS`

The factual ambiguity is fully resolved via the primary Exchange
Agreement and independently cross-checked via the special-meeting proxy's
share-count disclosure. The resolved facts are **more favorable to the
promotion thesis than the unresolved ambiguity implied**: 71.7% of the
punitive, compounding preferred balance is confirmed retired (not the
feared ~15%), the residual 28.3% carries a temporarily reduced coupon and
a concrete, dated ($5.0M) incentive for full elimination by year-end, and
no hidden, additional dilutive conversion exists beyond what was already
known. This does not mean the transaction was cheap for common — it was
not — but it means the specific, named blocking question (how much of
the preferred overhang genuinely remains, and on what terms) no longer
blocks proceeding.

### NNBR progression decision

> ## `PROCEED_TO_DEEP_UNDERWRITING`

Per instruction, deep underwriting itself is **not** performed by this
addendum. The resolved Series D economics (§ above), the confirmed
57.1% dilution, the remaining $34.6M/18,400-share balance and its
December 31, 2026 discount incentive, and the exchange-ratio finding
(retirement at fair-to-premium value, not a discount) are named as the
specific, load-bearing inputs the next work order's deep-underwriting
stage must carry forward and weigh against the operating momentum this
record already found intact (§5–§8, above).

**Capital status: NO REAL PORTFOLIO ACTION.**
