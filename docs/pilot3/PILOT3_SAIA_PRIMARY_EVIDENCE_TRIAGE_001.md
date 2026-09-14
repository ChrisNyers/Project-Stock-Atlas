# PILOT 3 — SAIA PRIMARY-EVIDENCE TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Fourth Batch 003 candidate to receive primary-evidence triage, and the
> first governed specifically by a **read-through** discovery type
> (`READ_THROUGH`) — the core Pilot 3 learning test this record targets
> is whether a competitor's disclosure validly transfers economic
> information to the candidate.

| | |
|---|---|
| Date | September 14, 2026 |
| Batch | `PILOT3_BATCH_003_REGISTRATION.md` |
| Candidate | SAIA — Saia, Inc. |
| Discovery type | `READ_THROUGH` (Old Dominion Freight Line → Saia) |
| Source | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` |
| Prior state | `SURFACE_FOR_TRIAGE` |

---

## 1. Canonical identity — verified, no ambiguity

- **Issuer:** Saia, Inc., **Nasdaq Global Select Market**, ticker
  **SAIA**, **MIC `XNGS`**, SEC CIK `0001177702` — confirmed directly
  against SEC EDGAR company submissions (`tickers: ['SAIA']`,
  `exchanges: ['Nasdaq']`).
- **Security type:** common stock (SIC "Trucking (No Local)").
- **No collision or fail-closed condition found** — "SAIA" is not, in
  this record's search, a meaningfully ambiguous ticker on any major
  venue.
- **Read-through counterparty, also verified:** Old Dominion Freight
  Line, Inc., ticker **ODFL**, SEC CIK `0000878927`, Nasdaq.

---

## 2. Discovery hook — restated, treated as tentative

> Old Dominion Freight Line's August LTL data may indicate that industry
> pricing remains firmer than the market expects, potentially making
> Saia's previously guided Q3 operating-ratio pressure less severe than
> feared.

Per instruction, **ODFL economics are not assumed to transfer directly
to SAIA** — §6 below is built specifically to test this.

---

## 3. Primary evidence reviewed

**Saia:**
- Q2 2026 earnings release (8-K, accession `0001193125-26-324937`,
  exhibit `saia-ex99_1.htm`, filed 2026-07-30).
- Q2 2026 earnings-call transcript, **issuer-filed** as an 8-K exhibit
  (accession `0001193125-26-335131`, exhibit `saia-ex99_1.htm`, filed
  2026-08-05) — treated as primary evidence per instruction, since it is
  SEC-filed by the issuer, not a third-party summary.
- Q2 2026 10-Q (accession `0001193125-26-326240`).
- **September 3, 2026 8-K** (accession `0001193125-26-381050`, exhibit
  `saia-ex99_1.htm`) — **Saia's own July and August 2026 shipment/
  tonnage data**, filed the same calendar day as ODFL's comparable
  release. This is a primary, company-specific data point Scout's hook
  did not reference and this record treats as load-bearing (§6, §13).
- Q3 2025, Q4 2025, and Q1 2026 earnings releases (accessions
  `0001193125-25-257441`, `0001193125-26-043714`, `0001193125-26-194062`)
  — used for the Fix 1 4-period reconstruction.
- SEC XBRL company facts (CIK `0001177702`) — net income, diluted EPS,
  shares outstanding, D&A, operating income, debt, cash.

**Old Dominion Freight Line (ODFL):**
- **September 3, 2026 8-K** (accession `0000878927-26-000025`, exhibit
  `odfl-ex99_1.htm`) — the August 2026 operating-statistics release
  Scout's hook is built on.
- Q2 2026, Q1 2026, Q4/FY2025, and Q3 2025 earnings releases (accessions
  `0000878927-26-000021`, `-26-000009`, `0001193125-26-036791`,
  `0001193125-25-255040`) — used for the comparative reconstruction.

**Equity price series** (TwelveData), SAIA and ODFL, 2026-07-27 through
2026-09-14 — checked directly.

**Evidence gap, disclosed up front:** ODFL's own Q3-2026-to-date
operating ratio, and any ODFL management commentary specific to Q3
margin expectations, were not found in the September 3 release (it is a
volume/pricing statistics release only, not an earnings call) — this
record does not infer ODFL's own Q3 margin trajectory beyond what its
own historical OR trend (§5) shows.

---

## 4. SAIA's actual Q3 setup — what management told the market, verbatim

**Source: the issuer-filed Q2 2026 earnings-call transcript
(2026-07-30), not a secondary summary, per instruction.**

- **Q3 operating ratio:** CFO Matt Batteh: **"we think we can be around
  100 basis points of sequential degradation"** Q2→Q3, versus a
  **historical norm of "150 to 200 basis points"** Q2-to-Q3
  deterioration. CEO Fritz Holzgrefe reiterated this explicitly: **"Our
  normal Q2 to Q3 OR typically gets 150 to 200 basis points worse. This
  year, we're highlighting 100."** Applied to Q2 2026's 86.9% OR, this
  implies **guided Q3 2026 OR of roughly 87.9%**, this record's own
  arithmetic.
- **Volume expectations:** "we're projecting **normal shipment
  seasonality**, Q2 to Q3."
- **Wage inflation:** two increases embedded — October 2025 and **July
  1, 2026** — each "generally about a point" of OR impact; the July
  increase compounds off a higher base than the October one.
- **Purchased transportation:** **"increased by 47.3% year-over-year and
  represented 8.9% of total revenue"** in Q2 2026, attributed to "higher
  volumes, our disciplined approach to headcount, and significantly
  higher diesel fuel costs" — i.e., **a real, large, already-disclosed
  cost headwind**, not a future risk.
- **Terminal/network costs:** newer (2023-2024-vintage) terminals
  **"operated in the low-90s"** operating ratio, **"improved nearly 300
  basis points"** YoY — i.e., a real, quantified, still-above-average-OR
  drag that is **improving but has not yet matured** to the company
  average (86.9% Q2 2026).
- **Depreciation:** $64.2 million in Q2 2026 (vs. $62.5M Q2 2025) — a
  modest, not dramatic, increase.
- **Startup costs:** not separately quantified in dollars in sources
  reviewed; qualitatively described via the new-terminal OR drag above.
- **Full-year 2026 OR guidance:** "we still feel like we can get to the
  **100 basis points of OR improvement** [year-over-year]... we'll see
  what the back half deals us" — with the caveat that a prior, higher
  (200bps) improvement scenario "included some pretty solid mid-single-
  digit shipment growth for the full year," which **shipment growth (as
  opposed to tonnage growth) has not yet reached** (§5).

**Answering the work order's first question directly: SAIA's own,
already-public Q3 setup, as stated on July 30, 2026 — more than a month
before Scout's ODFL-based hook — was already framed as better than
typical seasonality (100bps vs. a 150-200bps historical norm), not as a
"feared severe" deterioration requiring an external read-through to
soften.** This is the first, and one of the most important, findings
this record makes (developed further in §9 and §12).

---

## 5. Narrow Fix 1 — hook reconstruction (4+ comparable periods, SAIA and ODFL)

### SAIA

| Metric | Q3'25 | Q4'25 | Q1'26 | Q2'26 | Jul'26 | Aug'26 |
|---|---|---|---|---|---|---|
| Revenue | $839.6M | $790.0M | $806.2M | $956.5M | — | — |
| Revenue YoY | −0.3% | +0.1% | +2.4% | +17.1% | — | — |
| Operating ratio | 85.9% | 91.9%\* | 91.7% | 86.9% | — | — |
| Shipments/day YoY | −1.9% | −0.5% | +1.0% | +4.4% | +0.8% | +1.1% |
| Tonnage/day YoY | −1.5% | −1.5% | −2.1% | +8.4% | +7.8% | +8.7% |
| Weight/shipment (lbs) | 1,355 | 1,348 | 1,380 | 1,448 | — | — |
| Revenue/shipment | $349.07 | $352.27 | $357.93 | $393.56 | — | — |
| Rev/shipment ex-fuel | $294.35 | $297.57 | $297.11 | $303.12 | — | — |
| Revenue/cwt | $25.76 | $26.13 | $25.93 | $27.18 | — | — |
| **Revenue/cwt ex-fuel** | $21.72 (−0.1%) | $22.07 (+0.5%) | $21.52 (+1.9%) | **$20.94 (−2.2%)** | — | — |
| Terminal count | 213 | ~215 | — | 218 (5 opened in Q2) | — | — |

\* Q4 2025 OR included a disclosed $4.7M one-off self-insurance/claims
charge from prior-year accidents — a real, named, non-recurring item
this record does not treat as part of the underlying trend.

**Distinguishing price/yield, volume, mix, and fuel, per instruction:**
management's own words in the Q2 2026 call are explicit and are used
directly rather than this record's own inference: **"Yield, excluding
fuel surcharge, decreased by 2.2%, primarily reflecting a 3.9% increase
in weight per shipment"** — i.e., the headline ex-fuel yield decline is
a **mix effect** (heavier average shipments structurally price lower
per hundredweight), not a price cut. Management's own **mix-adjusted
"core yield"** figure: **"core yield, excluding fuel surcharge, was up
about 3% compared to prior year"** after adjusting for weight,
length-of-haul, and a named Los Angeles-region customer exit. **GRI:** a
**7.1% general rate increase implemented in early July 2026**, with
"pretty good acceptance" reported. **Contract renewals: "10.7% for both
June and for the quarter."**

**What this reconstruction shows:** SAIA's tonnage growth has
**accelerated dramatically and monotonically** for three straight
periods (Q1'26 −2.1% → Q2'26 +8.4% → Jul +7.8% → Aug +8.7%), while its
**shipment count growth has been far more modest** (+1.0% → +4.4% →
+0.8% → +1.1%) — meaning **almost all of the tonnage acceleration is a
weight-per-shipment/mix effect** (heavier, likely more industrial
freight), not a shipment-count (customer/order) acceleration. This
single fact is the mechanical explanation for both the headline
ex-fuel-yield decline **and** the disconnect between "record tonnage"
optics and a still-elevated, only-modestly-improving operating ratio.

### ODFL (comparable metrics, same periods)

| Metric | Q3'25 | Q4'25 | Q1'26 | Q2'26 | Aug'26 (QTD) |
|---|---|---|---|---|---|
| Revenue YoY | −4.3% | −5.7% | −2.9% | +10.4% | — |
| Operating ratio | 74.3% | 76.7% | 76.2% | 70.1% | — |
| LTL tons/day YoY | −9.0% | −10.7% | −7.7% | −4.1% | −0.9% |
| LTL shipments/day YoY | −7.9% | −9.7% | −7.9% | −5.7% | −2.4% |
| Revenue/cwt YoY | +4.7% | +5.6% | +5.7% | +15.2%\* | +11.3%\* |
| **Revenue/cwt ex-fuel YoY** | +4.7% | +4.9% | +4.4% | +5.5% | +4.8% |

\* Q2/Aug's larger headline revenue/cwt YoY figures reflect fuel
surcharge swings, not a change in underlying pricing — the ex-fuel line
is the comparable series and is **remarkably stable, in a narrow
4.4%–5.5% band, across all five periods.**

**What the ODFL reconstruction shows, and why it matters for the
read-through test (§6):** ODFL's **core, ex-fuel pricing power has not
meaningfully accelerated** — August's 4.8% sits squarely inside the
year-long 4.4%–5.5% range, **not a new positive surprise on price**.
What **has** changed is **volume**: ODFL's tons/day decline has eased
steadily from −10.7% (Q4'25) to −9.0%, −7.7%, −4.1%, and −0.9% (August
alone) — **ODFL's "August news" is really a volume-stabilization story,
not a pricing-acceleration story**, a distinction Scout's hook framing
("industry pricing remains firmer") does not make and this record
treats as a material correction to the hook as stated.

---

## 6. Competitor read-through validity — the core Pilot 3 learning test

**Structural differences tested directly, with evidence:**

- **Volume/mix trajectory is the opposite of transferable.** Over the
  same five periods, **ODFL's shipment volume has been shrinking
  throughout (−9.7% to −2.4%)** while **SAIA's has been growing and
  accelerating (−1.9% to +4.4% to +1.1%)**, and SAIA's **tonnage** growth
  (+8.7% in August) is an order of magnitude larger than ODFL's tonnage
  decline is closing. **These two companies are in opposite phases of
  the volume cycle right now** — ODFL deliberately shedding lower-margin
  freight to hold price (a well-documented, long-running ODFL strategy),
  SAIA aggressively adding network capacity (33 terminals since 2022,
  5 more in Q2 2026 alone, "~25% door count growth") and taking on
  volume, including materially heavier, likely lower-cwt-yield,
  shipments.
- **Network density and maturity differ sharply.** ODFL's network is
  long-established and premium-positioned (70.1% Q2 2026 OR — among the
  best in the industry). SAIA's is mid-maturation: its newest terminal
  cohorts run **"low-90s"** OR, a full ~20 points worse than ODFL's, and
  "by no means at maturity" per its own CEO.
- **Customer mix differs**, evidenced concretely: SAIA specifically
  named and exited unprofitable Los Angeles-region customers during the
  reconstruction window ("we exited those customers... the headwind...
  we finally lapped that... in June"), a company-specific mix event with
  no ODFL analog in sources reviewed.
- **Pricing strategy differs in emphasis, not necessarily in underlying
  strength.** ODFL's ex-fuel yield (4.4%-5.5%, stable) and SAIA's own
  management-stated **mix-adjusted core yield (~3%)** and **contract
  renewal pricing (10.7%)** are **directionally similar and both
  real** — this is the one place where a genuine, if modest, common
  industry-pricing-discipline signal exists across both carriers.

**Answering the work order's question directly: ODFL is a
directionally-informative but quantitatively weak read-through for
SAIA.** The *qualitative* claim that LTL pricing discipline persists is
corroborated by both companies' own data (SAIA's contract renewals and
GRI acceptance are at least as strong a piece of evidence for this as
anything in ODFL's release). But the *specific* claim in Scout's hook —
that ODFL's **August print** carries incremental information about
whether **SAIA's Q3 operating-ratio pressure will be less severe than
feared** — does not hold up: ODFL's August pricing metric was **not
actually new information** (it sits inside a year-long stable range),
and the two companies' volume/mix trajectories are moving in **opposite
directions** for structurally different reasons (deliberate volume
shedding vs. aggressive capacity-led volume growth), which limits how
much any single ODFL data point can say about SAIA's specific Q3
mechanics (§8's terminal drag, wage step-ups, and purchased-
transportation inflation). **The read-through is not structurally
invalid on its face, but it is materially weaker than Scout's framing
implies** — this record does not stop here (per §6's own instruction,
only "if the read-through is structurally weak, stop" — this record
treats "weak but not fatally invalid" as warranting continuation through
the falsification test, §9, rather than an automatic stop).

---

## 7. ODFL August evidence — verified and distinguished

**Scout's implied figures, verified directly from the primary source
(ODFL's own September 3, 2026 8-K exhibit):**

- **Revenue per day: +12.4%** YoY (August 2026).
- **LTL tons per day: −0.9%** YoY.
- **LTL shipments per day: −2.4%** YoY.
- **Weight per shipment: +1.7%** YoY.
- **LTL revenue/cwt (QTD, i.e., July+August combined): +11.3%.**
- **LTL revenue/cwt excluding fuel (QTD): +4.8%.**
- **CEO commentary:** "Old Dominion produced solid revenue growth for
  July and August, with underlying demand trends remaining relatively
  consistent as the quarter has progressed," attributing the
  "improvement" to "the strength and consistency of our industry-leading
  service."

**Distinguishing stronger industry pricing from ODFL-specific pricing
power, per instruction:** as established in §5, ODFL's **ex-fuel** yield
of 4.8% is **not a step-change** from its own trailing four-quarter
range (4.4%-5.5%) — it is **consistent with, not incremental to, ODFL's
already-known pricing power.** What is modestly new is the **volume**
trend: **tons/day −0.9% is ODFL's best (least-negative) reading in the
five periods reconstructed**, and shipments/day −2.4% is similarly its
best reading. **This record characterizes the August release as
evidence of ODFL's own volume trend improving, layered on an
already-known, stable ODFL pricing power — not as evidence of a new,
industry-wide pricing inflection.**

---

## 8. SAIA network-expansion economics — load-bearing, answered directly

- **Terminals:** "approximately $1 billion in real estate investments"
  since 2022, **33 terminals added**, 25+ relocated/expanded, **"~25%"**
  operational door-count growth; **5 new terminals opened in Q2 2026
  alone**; 218 terminals total as of Q2 2026 (up from 213 at Q3 2025).
- **Startup costs / utilization / maturation curve:** newer (2023-2024)
  terminal cohorts run **"low-90s"** OR, improving **~300bps YoY** but
  explicitly **"by no means at maturity."** No specific dollar startup-
  cost figure or utilization percentage is disclosed in sources
  reviewed — a genuine, disclosed evidence gap.
- **Revenue ramp:** qualitatively confirmed ("shipments grew in both
  legacy and ramping facilities," Q1 2026 release) but not quantified by
  cohort in dollars.
- **Incremental depreciation:** modest and gradual ($62.5M→$64.2M Q2
  YoY) — not, on its own, a large driver of the OR gap.
- **Labor burden:** two wage increases (Oct 2025, July 2026), each
  "about a point" of OR — a real, quantified, already-embedded cost.
- **Effect on operating ratio:** the combination of (a) new-terminal
  drag (low-90s vs. 86.9% company average), (b) two stacked wage
  increases (~2pts combined potential OR impact), and (c) purchased
  transportation up 47.3% YoY (8.9% of revenue) **are the specific,
  quantified cost items management itself cites as working against the
  OR** — none of which are affected by, or informed by, ODFL's pricing
  data.

**Answering the work order's question directly, and directly: yes —
SAIA could experience genuinely strong, even accelerating, industry
pricing and still miss margin expectations, because its own network-
investment and cost-inflation items (new-terminal drag, stacked wage
increases, sharply higher purchased-transportation costs) are large,
already-disclosed, and structurally independent of whatever ODFL's
pricing data shows.** This is the single most important reason the
read-through, even if directionally real, is not sufficient on its own
to change the probability of SAIA's Q3 outcome.

---

## 9. Cheapest falsification test — run first, as instructed

> After adjusting for network mix, fuel, and SAIA-specific expansion
> costs, does ODFL's August pricing evidence materially improve the
> probability that SAIA's Q3 operating ratio will be better than the
> market expects?

**No — not materially.** Four independent reasons converge on this
answer:

1. **SAIA's own Q3 guidance (100bps sequential degradation, better than
   the 150-200bps historical norm) was already public on July 30,
   2026** — more than a month before Scout's ODFL-based hook (dated
   2026-09-12 registration, ODFL data dated 2026-09-03). **The
   "better-than-feared" framing already existed in SAIA's own words**,
   independent of ODFL.
2. **SAIA discloses its own monthly shipment/tonnage data via SEC
   filing**, filed the **same calendar day** as ODFL's August release
   (both dated Sept 3, 2026). The market does not need an ODFL
   read-through to learn about SAIA's own Q3-to-date volume trends — it
   has SAIA's own primary data directly.
3. **ODFL's ex-fuel pricing metric is not new information** (§7) — it
   sits inside a stable, year-long range, so it cannot be said to be
   revealing an unexpected industry-wide pricing acceleration that the
   market had not already had a full year of comparable evidence for.
4. **The specific cost items most likely to determine whether SAIA's Q3
   OR beats or misses its own 100bps guide (new-terminal drag, wage
   step-ups, purchased-transportation inflation) are SAIA-specific and
   unaffected by ODFL's pricing environment** (§8).

**Per instruction: since the answer is no, the read-through hook, as
specifically framed by Scout (ODFL's August data → SAIA's Q3 setup),
fails the cheapest-falsification test.** This record does not stop
outright (the work order's remaining sections are completed for the
learning record and to avoid concealing corroborating detail), but this
result is the primary driver of the final disposition (§20).

---

## 10. Volume versus price

**Industry conditions, reconstructed from both companies' own evidence,
reflect improving volume with historically stable (not accelerating)
pricing at ODFL, and strongly improving volume (via network-driven mix
shift toward heavier freight) with modest, mix-adjusted core pricing
gains at SAIA** — not a single, uniform "weak volume/strong price" or
"improving volume/strong price" story across the industry. **This is
itself evidence against treating ODFL's release as a clean, transferable
signal**: the two carriers' volume stories are diverging for
company-specific reasons (deliberate share-shedding vs. deliberate
capacity-led share gain), even while both report broadly similar,
modest, stable core pricing power.

**Answering the work order's question directly: pricing strength alone
is not shown to be economically sufficient to overcome SAIA's specific,
quantified volume/cost pressures** (new-terminal OR drag, wage
step-ups, purchased-transportation inflation) — **yield improvement is
explicitly not treated as earnings improvement**, per instruction; the
Q2 2026 OR improvement (87.8%→86.9%, a modest 90bps YoY gain) came
despite, not because of, the ex-fuel yield print, which was headline-
negative.

---

## 11. Earnings sensitivity — coarse, no false precision

- **100bps of operating ratio, applied to Q2 2026 revenue ($956.5M):**
  **≈$9.6 million** of pre-tax operating income, a genuinely material
  but not overwhelming swing relative to Q2 2026 operating income of
  **$125.2 million** (XBRL) — roughly **±7-8%** of quarterly operating
  income per 100bps of OR.
- **Applied to the guided ~100bps Q3 sequential degradation itself:**
  the gap between the company's own guided scenario and the "normal
  seasonal" 150-200bps scenario is **50-100bps**, or **roughly
  $4.8-9.6 million** of quarterly operating income — this is the
  approximate economic size of the very question Scout's hook is asking
  about ("will Q3 be even better than SAIA's own already-better-than-
  normal guide?").
- **Volume sensitivity:** SAIA's own tonnage growth (accelerating to
  +8.7% YoY in August) is overwhelmingly a **mix** effect (heavier
  shipments), not a shipment-count effect (+1.1%) — meaning a
  meaningful part of any "volume upside" is not the kind of volume
  growth (more shipments, more customers) that most directly supports
  margin at scale; it is weight-per-shipment growth, which this record's
  own reconstruction (§5) shows depresses the ex-fuel cwt yield metric
  mechanically.

**Answering the work order's purpose directly: the read-through, even
taken at face value, would be economically meaningful if true (the
50-100bps gap is worth several million dollars per quarter) — but §9
already found the read-through does not meaningfully raise the
probability of that upside occurring**, so the earnings sensitivity
here quantifies the size of a question this record cannot answer more
confidently because of ODFL's data specifically.

---

## 12. Narrow Fix 2 — priced-in one-liner

> For SAIA to be mispriced positively on this specific hook, the market
> must currently be assuming that SAIA's Q3 operating ratio will land
> at, or worse than, the already-better-than-normal 100bps-sequential-
> degradation guidance the company itself gave on July 30 — i.e., that
> the market has not yet credited the possibility of a further,
> ODFL-signaled upside surprise beyond what management itself already
> guided.

**This sentence can be stated, but this record finds it is not credibly
supported by the evidence gathered.** Per §9, SAIA's own Q3 guidance was
already framed as better-than-normal-seasonality over a month before the
Scout hook, and the market has already had access to SAIA's own July and
August volume data (filed the same day as ODFL's release, §13) — **there
is no clear, evidence-based reason to believe the market is anchored to
a more pessimistic Q3 scenario than SAIA's own already-public guidance,
purely because it has not yet "found" ODFL's data.** Per instruction, **a
one-liner that cannot be stated credibly means this record does not
promote** on this basis.

---

## 13. Market reaction — checked directly, not assumed

| Date | SAIA close | ODFL close | Note |
|---|---|---|---|
| 2026-07-27 | $419.92 | $226.77 | Before Q2 earnings (both report same week) |
| 2026-07-29 | $394.44 | $222.79 | ODFL earnings day (−4.3% vs 7/28's $226.28... wait, ODFL reported 7/29) |
| 2026-07-30 | $350.63 | $212.47 | SAIA earnings day — SAIA fell **−11.1%** same-day |
| 2026-07-31 | $347.63 | $212.14 | SAIA continued down |
| 2026-09-01 | $331.62 | $187.01 | Pre-release lows |
| 2026-09-02 | $332.04 | $187.61 | Day before the dual Sept 3 release |
| **2026-09-03** | **$345.81** | **$185.75** | **Both companies' own July/August data released — SAIA rose +4.2%; ODFL fell slightly** |
| 2026-09-04 | $357.94 | $185.87 | SAIA continued up (+7.8% cumulative from 9/2); ODFL flat |
| 2026-09-08 to 09-11 | $346-355 | $180-187 | SAIA gave back roughly half its Sept 3-4 gain |
| 2026-09-14 (intraday, not certified) | $351.51 | — | Context only |

**Two distinct, direct, primary-sourced findings:**

1. **SAIA's Q2 earnings itself (July 30) triggered a sharp, immediate,
   negative reaction (−11.1% same-day, continuing to roughly −17% off
   the pre-earnings high within days)** — despite a headline OR
   *improvement* (87.8%→86.9%) — consistent with this record's own
   finding that the market focused on the cost items (wage step-ups,
   +47.3% purchased transportation, still-immature new terminals) more
   than the revenue/tonnage growth headline.
2. **On September 3, 2026 — the day both SAIA's own July/August data and
   ODFL's August data were released — SAIA rose while ODFL did not.**
   This is direct evidence that **the market's positive reaction is
   better explained by SAIA's own disclosed data (strong tonnage growth)
   than by ODFL's release** — if the market were reacting to ODFL's
   pricing signal as a read-through for the sector, ODFL's own stock
   would be expected to react positively too; it did not (it was flat to
   slightly down on its own release day and the two following days).

**Answering the work order's question directly: yes, the market appears
to have already used the available primary data (predominantly SAIA's
own, not ODFL's) to reprice SAIA on September 3-4, and that reaction has
since partially faded** — this is consistent with, and reinforces, this
record's §9 finding that the discovery, as specifically framed around
ODFL, is economically too late and mechanically not the right
explanation for what the market actually did.

---

## 14. Valuation checkpoint — coarse, explicitly not falsely precise

**Fresh-price bind attempted first, per instruction.** A same-day
(2026-09-14) Gate B bind was attempted and correctly returned `STALE`
(the market was open at decision time):

```
security_key: SEC-CIK:0001177702:SAIA
mic: XNGS
attempted decision time: 2026-09-14 (market open) -> STALE, not forced
last confirmed completed-session close: $351.05, session 2026-09-11
52-week range (raw observation, context only): $249.32 - $494.71
```

- **Reference price:** **$351.05** (last confirmed completed-session
  close, 2026-09-11) — the stock is **down ~29% from its 52-week high**
  ($494.71) and **up ~41% from its 52-week low** ($249.32).
- **TTM net income** (Q3'25 $86.316M + Q4'25 $47.519M [FY2025
  $255.036M minus 9-month $207.517M] + Q1'26 $49.869M + Q2'26 $94.260M)
  = **≈$277.96M**; diluted shares ≈26.67M (Q2 2026, XBRL) → **TTM
  diluted EPS ≈$10.42** → **coarse P/E ≈33.7x.**
- **TTM operating income** (Q3'25 $118.610M + Q4'25 $64.023M + Q1'26
  $66.806M + Q2'26 $125.212M) = **≈$374.65M**; **TTM D&A** (Q3'25
  $64.037M + Q4'25 $62.947M + Q1'26 $62.190M + Q2'26 $64.181M) =
  **≈$253.36M** → **coarse TTM EBITDA ≈$628.0M.**
- **Balance sheet, confirmed via XBRL: essentially net-debt-free** —
  long-term debt has fallen from $307M (Jun 2025) to $100M (Jun 2026)
  while cash has risen from $18.8M to $84.0M, for **net debt of roughly
  $16M** — a real, positive, primary-sourced balance-sheet trend this
  record notes as a genuine strength, independent of the read-through
  question.
- **Market cap** at the reference price (≈26.67M shares × $351.05)
  ≈**$9.36 billion**; **EV** ≈**$9.38 billion**; **coarse EV/EBITDA
  ≈14.9x.**

**Answering the work order's question directly: today's price already
embeds a demanding, growth-multiple valuation (≈34x TTM earnings,
≈15x TTM EBITDA) for a trucking company — not a depressed, "priced for
Q3 disappointment" multiple.** This is itself evidence against the
premise that the market is under-crediting SAIA's prospects and simply
waiting on an ODFL-style catalyst — a company already priced at a
growth multiple, that just fell double digits on its own earnings print
over cost concerns, is a harder case for "the market hasn't caught up
yet" than a cheaply-priced, unloved name would be. **Per instruction,
this record does not use the peer discount/premium relationship (SAIA
trades at a premium to ODFL on trailing multiples in some conventional
framings) as evidence of edge on its own.**

---

## 15. Market-could-be-right case

- **The read-through itself is weak** (§6, §9) — a reasonable investor
  could simply not credit ODFL's data as meaningfully informative about
  SAIA's specific Q3 setup at all.
- **SAIA's network investments are a real, ongoing margin drag** — new
  terminals running "low-90s" OR, "by no means at maturity," is a
  multi-year, not multi-quarter, maturation process; a reasonable
  investor could expect this drag to persist well beyond Q3 2026.
- **Tonnage strength is substantially a mix effect** (heavier shipments,
  not more shipments) — a reasonable investor could see this as lower-
  quality growth than a shipment-count acceleration would represent, and
  could reasonably expect it to continue pressuring the ex-fuel cwt
  yield optic even if underlying "core" pricing (per management's own
  adjusted figure) is genuinely positive.
- **Wage costs and purchased-transportation costs are large, real, and
  already disclosed** (two stacked wage increases; purchased
  transportation +47.3% YoY, now 8.9% of revenue) — a reasonable
  investor could conclude these more than offset any incremental
  ODFL-signaled pricing tailwind.
- **The Los Angeles-region customer exit and other mix effects mean some
  of SAIA's "core yield" strength is arguably a comparison-base
  effect** (lapping a self-inflicted headwind) rather than fresh pricing
  power.
- **The market's own behavior on July 30 is itself strong evidence for
  this case** — SAIA fell over 11% the day it reported results that
  included record tonnage and a YoY OR improvement, indicating the
  market was, if anything, **more focused on the cost/margin risks
  this record identifies than reassured by the growth headline.**
- **Valuation already reflects a premium growth multiple** (≈34x TTM
  P/E, ≈15x TTM EV/EBITDA) — a reasonable investor could argue there is
  little room for a modest, ODFL-inferred upside surprise to move a
  stock already priced for a robust growth-and-margin-recovery
  narrative.

**This case is credible, built entirely from this record's own findings,
and is not a strawman.**

---

## 16. Tentative variant — tested and weakened

> The market may be overestimating the severity or duration of SAIA's
> margin pressure if industry pricing remains disciplined while network
> investments mature and incremental terminals begin contributing
> revenue.

**Weakened, not rejected outright, but not promotable as framed around
the ODFL read-through.** The "network investments mature and begin
contributing" half of this variant is **real and evidenced** (the
300bps YoY improvement in new-terminal OR, management's own "they've got
room to go" framing) — but this is a **SAIA-specific, multi-year
maturation story**, independent of and not meaningfully accelerated by
ODFL's August data. The "industry pricing remains disciplined" half is
**also real** (SAIA's own contract-renewal and GRI data, corroborated
directionally by ODFL's stable core yield) but **was already known to
the market before the Scout hook's dating** (SAIA's GRI and contract-
renewal figures were disclosed on the same July 30 call as the Q3
guidance itself). **The specific causal claim the hook requires — that
ODFL's August print is the thing making the market underestimate SAIA's
Q3 setup — is not supported.** The variant, if it exists at all, rests
on SAIA's own terminal-maturation trajectory playing out over multiple
quarters, not on a near-term, ODFL-triggered repricing catalyst.

---

## 17. What Atlas added beyond the original Scout hook

- **Found that SAIA discloses its own monthly shipment/tonnage data**,
  filed via SEC 8-K the **same day** as ODFL's August release — a
  primary, company-specific data source Scout's ODFL-centric hook did
  not reference, and one that better explains the actual market reaction
  than the read-through does.
- **Established, from ODFL's own four-quarter trend, that its August
  ex-fuel pricing print was not new information** (it sits inside a
  stable, year-long 4.4%-5.5% range) — reframing "industry pricing
  remains firmer than expected" into "ODFL's already-known pricing power
  persists, and its volume decline is easing" — a materially different
  and more precise characterization than Scout's hook.
- **Quantified, from SAIA's own issuer-filed earnings-call transcript,
  the specific, already-disclosed cost items** (two stacked wage
  increases, +47.3% YoY purchased transportation, "low-90s"-OR new
  terminals) that are structurally independent of ODFL's pricing
  environment and are the more likely determinants of SAIA's actual Q3
  outcome.
- **Found that SAIA's own Q3 guidance (100bps sequential degradation)
  was already framed as better-than-normal-seasonality over a month
  before the Scout hook's dating** — directly testing, and substantially
  undermining, the hook's implicit premise that the market is anchored
  to a more severe expectation.
- **Directly reconciled the mechanical driver of SAIA's headline
  ex-fuel-yield decline** (a 3.9% weight-per-shipment/mix effect, per
  management's own words) versus its management-stated ~3% mix-adjusted
  core yield — a distinction neither Scout's hook nor a surface reading
  of the headline number would surface.
- **Checked the actual, dated market reaction to both companies' own
  September 3 releases** and found a divergence (SAIA up, ODFL flat-to-
  down) that is itself primary evidence the market's move was driven by
  SAIA's own data, not by an ODFL read-through — directly answering the
  work order's core learning question with dated, falsifiable evidence
  rather than assumption.

---

## 18. Read-through learning classification

> **`READ_THROUGH_PARTIAL`**

A genuine, if modest, common signal of LTL industry pricing discipline
is corroborated across both companies' own primary evidence (SAIA's
contract renewals and GRI acceptance; ODFL's stable ex-fuel yield), but
the *specific* claim that ODFL's August print carries material
incremental information about SAIA's Q3 setup does not hold up — ODFL's
pricing data was not new, the two companies' volume/mix trajectories are
moving in opposite directions for company-specific reasons, and SAIA's
own, already-public data (Q3 guidance and its own July/August shipment
release) is both more current and more determinative. **This is a Pilot
3 learning observation only, not a permanent scoring field.**

---

## 19. Uncertainty classification

> **`POTENTIAL_SOURCE_OF_EDGE`**

Whether SAIA's new-terminal cohorts mature toward the company average OR
fast enough, in the next several quarters, to let its genuine network-
expansion-driven volume growth translate into margin improvement is
classified as a potential source of edge, not thesis-blocking, for this
record's narrow purpose — because it is a real, quantified, improving
(not deteriorating) trend (§8) that this record simply lacks enough
periods of further evidence to resolve, not a trend already working
against the candidate. **This is a Pilot 3 learning observation about
this record, not a permanent architecture field or a score.**

---

## 20. Final disposition

> ## `NO_DEMONSTRATED_EDGE`

The specific discovery mechanism Scout proposed — that ODFL's August
2026 pricing data provides an information edge suggesting SAIA's Q3
operating-ratio pressure will be less severe than the market expects —
**fails the mandatory cheapest-falsification test (§9)** on four
independent, primary-sourced grounds: SAIA's own Q3 guidance was already
publicly framed as better-than-normal-seasonality more than a month
before the hook; SAIA discloses its own monthly volume data
contemporaneously with ODFL's release, making the read-through largely
redundant; ODFL's cited pricing metric was not actually new information
relative to its own trailing year; and the specific cost items most
likely to determine SAIA's actual Q3 outcome (new-terminal drag, wage
step-ups, purchased-transportation inflation) are SAIA-specific and
unrelated to ODFL's pricing environment. The priced-in one-liner (§12)
cannot be stated credibly against this evidence. Direct market-reaction
evidence (§13) shows the market's own September 3 repricing of SAIA is
better explained by SAIA's own disclosed data than by ODFL's. **This is
not a finding that SAIA is a weak business** — tonnage growth, network
expansion, and a strengthening balance sheet (net debt of roughly $16M)
are all real and evidenced — but **this specific, competitor-read-
through discovery hook does not survive primary-evidence testing**,
consistent with how this pilot has treated hooks that do not survive
mandatory reconstruction at NHP and UCB.

**No deep underwriting of SAIA is performed by this record.**

---

## 21. Confirmation — other Batch 003 candidates and all prior states unchanged

NHP remains `NO_DEMONSTRATED_EDGE`
(`PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`). UCB remains
`NO_DEMONSTRATED_EDGE`
(`PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_001.md`). NNBR remains
`BLOCKED_BY_MATERIAL_UNCERTAINTY`
(`PILOT3_NNBR_DEEP_UNDERWRITING_001.md`). **TCS is untouched by this
record** — not triaged, not researched, remaining `SURFACE_FOR_TRIAGE`,
per instruction. All other Pilot 3 states are unchanged: PATH, MDB, XOM,
PCG `NO_DEMONSTRATED_EDGE`; DOCU, SPXC, SOLS
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AAPL `EVIDENCE_GAP`; JPM `CALENDAR_HOLD`; SMH `REFERENCE_PEER_TAPE`;
NVDA `REFERENCE_ONLY`.

---

## 22. Shadow sentiment

No sentiment observations were encountered or used in this record. Had
any arisen, they would have been labeled `SHADOW` and excluded from the
disposition, per the Batch 003 charter.

---

## What this record does not do

No deep underwriting of SAIA. No triage or research of TCS. No Stage 7
or Stage 8. No capital allocated. No scoring, ranking, or new engine. No
advance of JPM or AAPL. No Batch 004.

**Capital status: NO REAL PORTFOLIO ACTION.**
