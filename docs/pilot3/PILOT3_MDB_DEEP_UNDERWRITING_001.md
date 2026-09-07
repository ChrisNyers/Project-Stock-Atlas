# PILOT 3 — MDB DEEP UNDERWRITING 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Deep underwriting only. Stage 7 capital comparison has **not** begun.

| | |
|---|---|
| Date | September 7, 2026 |
| Batch | `PILOT3_MANUAL_DISCOVERY_BATCH_002.md` |
| Prior record | `PILOT3_MDB_PRIMARY_EVIDENCE_TRIAGE_001.md` — `PROMOTE_TO_DEEP_UNDERWRITING` |
| Candidate | MDB — MongoDB, Inc. (CIK `0001441816`) |

---

## 1. Preserve the current variant — as hypothesis, not conclusion

> The market may be over-weighting the lack of near-term Atlas growth
> acceleration while underweighting stronger bookings/RPO evidence,
> improving profitability, and management's raised forward expectations.

Carried forward unmodified from triage. Tested, not assumed, below — and
in §4 it is substantially weakened by evidence the triage record did not
have (the multi-quarter RPO trend).

---

## 2. Core question

> Does MDB have a real expectations gap around Atlas growth durability and
> future revenue conversion, or does the current valuation already assume
> enough reacceleration that the apparent variant is not investable?

Answered in §8–§12, not reduced to "9x forward revenue is below some peer
set."

---

## Primary evidence reviewed (new, beyond the triage record)

1. **SEC XBRL company facts** (`data.sec.gov/api/xbrl/companyfacts`,
   CIK `0001441816`) — quarter-by-quarter `RevenueRemainingPerformanceObligation`,
   `OperatingIncomeLoss`, `RevenueFromContractWithCustomerExcludingAssessedTax`,
   `ShareBasedCompensation`, `WeightedAverageNumberOfDilutedSharesOutstanding`,
   and `CommonStockSharesOutstanding`, spanning Q1 FY2026 through Q2 FY2027
   (six consecutive quarters). This is the single most load-bearing new
   evidence source in this record — it replaces single-snapshot YoY
   comparisons with an actual trend line.
2. **10-Q**, quarter ended 2025-07-31 (accession `0001441816-25-000181`) —
   prior-year RPO/cRPO comparable and share count.
3. **10-Q**, quarter ended 2025-10-31 (accession `0001628280-25-054768`) —
   RPO/cRPO.
4. **10-Q**, quarter ended 2026-04-30 (accession `0001628280-26-039150`) —
   RPO/cRPO, customer-concentration statement, buyback authorization,
   competition language.
5. **10-K**, FY2026 (accession `0001628280-26-016799`), including the
   XBRL-rendered **Remaining Performance Obligations note (R69.htm)** —
   year-end RPO and timing split; customer-concentration risk factor;
   general competition risk factors.
6. Earnings releases for **Q4 FY2026** (filed 2026-03-02) and **Q1 FY2027**
   (filed 2026-05-28), used for the Atlas-growth and customer-count trend.

**Evidence gaps, disclosed rather than filled by inference:** no primary
source names a specific large customer or contract behind the RPO
step-change identified in §4; no primary source quantifies AI-workload
consumption on Atlas as a dollar figure or percentage of revenue; no
primary source contains risk-factor language naming PostgreSQL/open-source
alternatives or AI-driven architecture change specifically (only general
cloud-provider and legacy-vendor competition language was found).

---

## 3. Atlas revenue quality

| Quarter | Atlas revenue | Atlas YoY growth |
|---|---|---|
| Q4 FY2026 (Jan 2026) | $502.6M | 29% |
| Q1 FY2027 (Apr 2026) | $512.5M | "more than 29%" |
| Q2 FY2027 (Jul 2026) | $565.9M | 29% |

**Confirmed, primary-sourced: Atlas growth has held at ~29% for three
consecutive fiscal quarters** — the secondary-source characterization from
the triage record is accurate, not overstated. Customer growth alongside
this is broad-based and continuous, not lumpy:

| Quarter | Total customers | Customers >$100K ARR |
|---|---|---|
| Q2 FY2026 | 59,900+ | 2,564 |
| Q3 FY2026 | (not captured) | — |
| Q4 FY2026 | 65,200+ (+2,700 in-quarter) | 2,799 |
| Q1 FY2027 | 67,700+ | 2,895 |
| Q2 FY2027 | 70,600+ | 2,999 |

**Finding:** the ~29% Atlas growth plateau coexists with steady,
incremental, broad-based customer additions (roughly +2,000–3,000 total
customers and +100–150 large ($100K+ ARR) customers every quarter) — this
is **not** a business stalling; it is a large, still-growing base whose
aggregate growth *rate* has stopped increasing. This is most consistent
with "stable but healthy, not obviously reaccelerating" rather than
"structurally slowing" (no absolute customer-count deceleration was found)
or "certain to reaccelerate" (three flat quarters with no confirmed
catalyst named in primary sources). **No inference of reacceleration is
drawn from RPO here** — that is tested on its own in §4 and does not
support one.

---

## 4. RPO / cRPO quality — the load-bearing finding of this record

**Full quarter-by-quarter trend (primary, SEC XBRL, not previously
assembled in the triage record):**

| Quarter end | Total RPO | QoQ | cRPO (calc./disclosed) | cRPO QoQ |
|---|---|---|---|---|
| 2025-04-30 (Q1 FY26) | $774.3M | — | — | — |
| 2025-07-31 (Q2 FY26) | $794.2M | +2.6% | ~$460.6M (58%) | — |
| 2025-10-31 (Q3 FY26) | $994.3M | **+25.2%** | ~$546.9M (55%) | +18.7% |
| 2026-01-31 (Q4 FY26) | $1,472.7M | **+48.1%** | ~$765.8M (52%) | **+40.0%** |
| 2026-04-30 (Q1 FY27) | $1,458.6M | **−1.0%** | ~$773.1M (53%) | +1.0% |
| 2026-07-31 (Q2 FY27) | $1,519.2M | +4.2% | $797.3M (disclosed) | +3.1% |

**This directly answers the work order's central RPO question.** The
"+91% YoY / +73% YoY" headline figures cited at triage are real as a
year-over-year snapshot, but the sequential trend shows they are almost
entirely a **base effect from a step-change concentrated in Q3–Q4 FY2026**
(RPO nearly doubled, +85%, in those two quarters combined) — **not**
evidence of current, ongoing bookings acceleration. In the two quarters
*since* that step-change (Q1 and Q2 FY2027), RPO grew a combined **+3.2%**
and cRPO a combined **+4.1%** — both **slower than the ~29% YoY (≈6.6%
sequential-equivalent) Atlas growth rate they were supposed to be leading
indicators for.**

**No primary source identifies the cause of the Q3–Q4 FY2026 step-change**
(no named large customer or contract was found in the 10-Q/10-K language
reviewed) — this is an unresolved evidence gap. But regardless of cause,
**the bookings-acceleration mechanism the triage-stage variant relied on
has already played out and stopped** — it is not a live, ongoing signal
that current quarters are under-reporting. This is the primary basis on
which this record substantially weakens the discovery-stage variant.

**Answering the work order's specific sub-questions:**
- Duration/broad-based nature: cannot be confirmed either way from primary
  sources (gap).
- Historical reliability of RPO/cRPO as a leading indicator: not tested
  here beyond this one episode; insufficient longer history reviewed to
  generalize.
- Bookings quality vs. revenue quality: **materially different over the
  last two quarters** — bookings (RPO/cRPO) growth has been slower than
  revenue growth, the opposite of what the variant needed to be true.

---

## 5. Profitability quality

| Quarter | GAAP operating income/(loss) | Non-GAAP op margin | SBC | SBC % of revenue |
|---|---|---|---|---|
| Q1 FY2026 | $(53.6)M | — | $132.4M | 24.1% |
| Q2 FY2026 | $(65.3)M | 15% | — | — |
| Q3 FY2026 | $(18.4)M | — | ~$133.6M | 21.3% |
| Q4 FY2026 | ~$0.3M (≈breakeven) | 23% | ~$144.0M | 20.7% |
| Q1 FY2027 | $(24.8)M | 18% | $137.8M | 20.0% |
| Q2 FY2027 | **$28.4M** (first clear positive) | 24% | $148.9M | 19.3% |

**Two genuine, primary-confirmed findings, one positive and one mixed:**

1. **SBC as a percentage of revenue has steadily declined** (24.1%→19.3%
   over five quarters) even as SBC dollars stayed roughly flat — this is
   real operating leverage on the SBC line, not solely a non-GAAP
   presentation effect.
2. **GAAP operating income is noisy, not monotonic** — it went from a
   near-breakeven Q4 FY2026 back to a $(24.8)M loss in Q1 FY2027 before
   turning solidly positive ($28.4M) in Q2 FY2027. **This is the first
   clearly positive GAAP operating quarter in the six-quarter series
   reviewed, not yet a confirmed trend.**

**Share-count / dilution finding:** actual common shares outstanding
*declined* slightly over the period reviewed (81.72M → 80.50M, per the most
recent disclosed balance-sheet-date counts), while weighted-average
*diluted* shares (used for EPS) rose slightly (81.06M → 81.995M) — i.e.,
buybacks (~$100M/quarter against a $1.0B authorization, ~$499.7M remaining
as of Q1 FY2027) are **roughly offsetting, but not clearly outpacing**, new
dilutive issuance from a $148.9M/quarter SBC expense. In dollar terms,
buyback spend ($100M/quarter) is materially **smaller** than the SBC
expense it is nominally offsetting ($148.9M/quarter) — the improving
non-GAAP margin story is real (SBC ratio is falling), but capital return is
not fully cash-neutralizing the economic dilution cost SBC represents.

**Cash/debt:** ≈$2.4B cash and short-term investments, no debt (unchanged
from triage).

---

## 6. Competitive position

Only competition materially bearing on the thesis is retained, per the
work order's instruction not to build a full industry map:

- **Primary-disclosed competitors:** public cloud providers (AWS, GCP,
  Azure) offering native database functionality, and legacy vendors
  (IBM, Microsoft, Oracle). The 10-K notes some competitors "have
  advantages... broader offerings and can bundle competing products with
  hardware or other software offerings."
- **PostgreSQL / open-source alternatives:** **not addressed in any
  primary source reviewed** — a real gap given this is a widely-discussed
  competitive dynamic in the database market generally (CTX/general
  industry knowledge only, not AVGO-style over-reliance on it).
- **AI changing application architecture:** the 10-Q notes, narrowly, that
  "a number of companies launched code assistant tools, which leverage
  generative AI to help developers write and test their code faster" —
  acknowledged as an evolving dynamic, not framed as an existential risk
  to MongoDB's document-database model specifically.
- **Snowflake/Databricks-adjacent competition:** not addressed in primary
  sources reviewed (different workload category — analytics vs.
  operational database — plausibly explaining the absence, not confirmed).

**Retained for the thesis:** general hyperscaler-native database
competition is real and disclosed, but no primary evidence found ties it
specifically to the Atlas growth plateau (§3) or the RPO deceleration (§4)
— those are better explained by scale/base effects than by a named
competitive loss.

---

## 7. AI / application-modernization thesis

**Fact vs. management claim vs. Atlas inference, separated:**

- **FACT:** MongoDB has made product investments in this direction
  (Voyage AI acquisition referenced in the 10-K; a LangChain integration
  partnership announced around Q1 FY2027 for "production-ready AI
  agents"). No dollar or percentage figure for AI-attributable Atlas
  consumption was found in any primary source reviewed.
- **MANAGEMENT CLAIM:** CEO CJ Desai has referenced "AI & digital natives"
  as a source of strength and "momentum" with "AI agents with features such
  as search, vector search and embeddings" (Q4 FY2026 release) and
  "emerging AI opportunities" (Q1 FY2027 release) — consistently
  qualitative, never quantified.
- **ATLAS INFERENCE:** given Atlas growth has been flat at ~29% across the
  same quarters these AI references were made, **it is a reasonable
  inference — not a disclosed fact — that AI-driven consumption is not yet
  large enough to move the aggregate Atlas growth rate**, whatever its
  qualitative narrative value. This inference is flagged as such, not
  presented as confirmed.

**Conclusion:** the AI/application-modernization thesis is currently
**mostly future narrative, not yet demonstrated current economics** — this
directly bears on §11's market-could-be-right case (AI optimism being
"already consensus" without matching disclosed evidence).

---

## 8. Priced-in / expectations test — corrected from the triage record

- **Fresh price (unchanged, see §15):** $368.74.
- **Market capitalization:** $368.74 × ≈82.0M diluted shares ≈ **$30.2B**.
- **Net cash:** ≈$2.4B, no debt → **enterprise value ≈ $27.8B**.
- **EV / FY2027E revenue** (guide midpoint $3.01B): ≈**9.25x**.
- **P/E on FY2027E non-GAAP EPS** (guide midpoint $6.485): ≈**56.9x**.

**Reverse-engineering what has to be true:** holding price flat, solving
for the sustained non-GAAP EPS growth rate needed to compress today's
~57x forward multiple to a more "mature, 25–30%-grower" multiple of
25–30x within three years: $57 ÷ (1+g)³ ≈ 27 → **g ≈ 28% per year, for
three consecutive years.** That would require non-GAAP EPS to compound
from ≈$6.49 today to roughly $13–14 by FY2030 — a large, specific,
multi-year assumption, not a modest one, and one requiring **both**
continued ~25–30%+ revenue growth **and** further margin expansion beyond
the ~20–24% non-GAAP operating margin range seen this year.

**Comparing against the primary-evidence trajectory:** Atlas growth has
been flat, not accelerating, for three quarters; RPO/cRPO growth (the
forward-looking bookings signal) has been running *slower* than revenue
growth for the two most recent quarters, following a step-change that has
already fully played out. **The primary-evidence trajectory does not
currently support the sustained ~28%/year multi-year EPS compounding the
price appears to require** — it supports continued solid, but not
accelerating, growth. This is the same style of correction made to AVGO's
triage-stage valuation framing: **the price is not cheap, and the specific
evidence needed to justify it (accelerating bookings, accelerating Atlas
growth) is the evidence that did not hold up under a longer look.**

---

## 9. Scenario framework (coarse, non-probability-weighted, FY2027–FY2028)

| Assumption | Downside | Base | Upside |
|---|---|---|---|
| Atlas growth | slows to 20–25% | holds ~28–30% | reaccelerates to 33–38% |
| RPO/cRPO conversion | proves partly lumpy; near-term revenue undershoots backlog implication | converts in line with historical recognition timing (~53% within 12 months) | converts faster than modeled, new large deals resume |
| Non-GAAP op margin | stalls near 20–22% | gradual expansion to 24–26% | expands to 28%+ |
| SBC / dilution | SBC % of revenue plateaus, buybacks don't keep pace | SBC % of revenue keeps declining slowly | SBC % of revenue declines faster; buybacks exceed dilution |
| FY2028E revenue (illustrative) | ~$3.3–3.5B | ~$3.8–4.0B | ~$4.3–4.6B |
| FY2028E non-GAAP EPS (illustrative) | ~$6.50–7.50 | ~$8.50–10.00 | ~$11.50–13.50 |
| Applied forward multiple | 20–25x | 28–35x | 35–42x |
| Implied price | **$130–190** | **$240–350** | **$400–570** |

**Key observation:** unlike AVGO, where the Base case bracketed the
current price, **MDB's current price ($368.74) sits above the top of this
record's Base case band and only inside the Upside band** — a further,
independent confirmation of §8's finding that the price already requires
something closer to sustained reacceleration than to a continuation of the
current, flat-Atlas trajectory.

---

## 10. Coarse 12–24 month return range

| Scenario | Implied price | Total return vs. $368.74 |
|---|---|---|
| Downside | $130–190 | **≈ −48% to −65%** |
| Base | $240–350 | **≈ −5% to −35%** |
| Upside | $400–570 | **≈ +8% to +55%** |

MDB pays no dividend; this does not affect the range. **This is a
materially more negatively-skewed range than AVGO's equivalent test** — the
Base case here implies a *decline* from the current price, not a roughly
neutral outcome, because the current price already sits above this
record's Base-case valuation band.

---

## 11. Market-could-be-right case — strengthened materially by this record

- **29% Atlas growth may simply be the real, normalized rate at this
  scale** — three consecutive flat quarters, with no confirmed reaccelerating
  catalyst in primary evidence, is a real pattern, not noise.
- **RPO growth was contract-timing/step-change noise, not a leading
  indicator of acceleration** — this record's own §4 finding, not the
  triage record's framing, is now the best-supported read: the headline
  YoY RPO growth is a stale base effect from a step-change that has already
  fully played out and stopped.
- **Current valuation already assumes meaningful continued growth** — §8's
  reverse-engineering shows ~28%/year sustained EPS growth for three years
  is embedded in today's price; §9's scenario framework shows the current
  price already sits above this record's Base case.
- **SBC meaningfully reduces true economic profitability** — $148.9M/qtr
  SBC against ~$100M/qtr buybacks means capital return is not fully
  cash-offsetting dilution, even though the SBC-to-revenue ratio is
  improving.
- **Competition is real, if not shown to be the specific cause of the
  Atlas plateau** — hyperscaler-native and legacy-vendor competition is
  primary-disclosed; PostgreSQL/open-source competition, while not
  addressed in primary sources, is a well-known industry dynamic.
- **AI/application-modernization optimism is currently narrative, not
  demonstrated economics** — §7 found no quantified AI-consumption
  evidence; a market already skeptical of unquantified AI narratives across
  software broadly has a credible basis for discounting it here too.

**This case is now stronger than at triage, credible enough that a
reasonable investor could decline to fund MDB** — the work order's bar for
this section.

---

## 12. Variant dimension and durability

**Dimension:** primarily **timing and magnitude** — whether the RPO/cRPO
signal cited at triage represented genuine, ongoing magnitude (more
bookings than revenue implies, continuing) or a one-time timing event
(a step-change that already happened and stopped). **This record's finding
is that it was predominantly the latter.**

**Why could this expectations gap persist in a widely followed software
company?** Two candidate explanations were tested:

1. **The market is correctly reading the RPO trend** — professional
   investors and analysts with access to the same sequential XBRL data
   this record used would very plausibly have already identified that
   RPO/cRPO growth decelerated sharply after Q4 FY2026, which would mean
   **there is no gap to persist** — this is the better-supported
   explanation given how directly this record's own sequential-trend
   analysis (available in public filings to any analyst) undercuts the
   triage-stage YoY framing.
2. **The market is anchored to the simple YoY RPO headline** (a real
   number, "+91%") **without doing the same quarter-by-quarter
   reconstruction this record performed**, and is separately anchored to
   the flat 29% Atlas figure without weighing the RPO context at all —
   this is possible, but this record cannot confirm that professional
   market participants (unlike Atlas at the triage stage) failed to do this
   reconstruction; RPO tables are standard, closely-watched SaaS disclosure
   items.

**No strong, evidence-grounded reason for a durable, distinctive gap was
found.** The more defensible reading is that the market's caution about a
flat 29% Atlas rate is not obviously mistaken once the RPO signal — the
main piece of counter-evidence the triage record relied on — is properly
sequenced and found to have already run its course. **The variant is
downgraded** from the triage record's framing.

---

## 13. Falsifiers / revisit triggers

1. **Next Atlas growth print (Q3 FY2027)** — a move meaningfully above 29%
   would revive the reacceleration case; continuation at ~29% for a fourth
   consecutive quarter would further confirm this record's plateau finding.
2. **Next RPO/cRPO print** — renewed strong sequential (not just YoY)
   growth would indicate the Q3–Q4 FY2026 step-change was the start of a
   new pattern rather than a one-off; continued sub-revenue-rate sequential
   growth would confirm this record's finding.
3. **Evidence of RPO conversion** — whether the large Q3–Q4 FY2026 backlog
   actually converts into revenue on the disclosed ~53%-within-12-months
   schedule, or converts more slowly than modeled.
4. **Margin/FCF progression** — whether the Q2 FY2027 GAAP operating-income
   inflection (§5) repeats in Q3, or reverts to loss as it did between Q4
   FY2026 and Q1 FY2027.
5. **SBC / dilution** — whether SBC-as-%-of-revenue continues declining, and
   whether buyback pace increases relative to SBC dollars.
6. **Forward guidance** — whether FY2028 initial guidance (expected with
   Q4 FY2027 results) implies any Atlas-growth reacceleration.
7. **Named large-customer or competitive disclosure** — any primary source
   naming the counterparty or cause behind the Q3–Q4 FY2026 RPO step-change
   would close this record's largest single evidence gap.

No price-target-only trigger is created; §8–§10 already supply the
valuation-based reasoning the work order requires before creating one.

---

## 14. Material underwriting risks

Documentary only — not scored, not a Stage 8 input:

- **Valuation / expectations risk** — primary, per §8–§10; the price
  already requires sustained, not merely continued, growth.
- **RPO lumpiness / stale-signal risk** — the specific mechanism this
  candidate was promoted on (§4).
- **Atlas growth plateau** — three consecutive quarters flat at ~29%, cause
  unconfirmed.
- **SBC / dilution** — large relative to buyback pace, though improving as
  a share of revenue.
- **Competition** — hyperscaler-native and legacy-vendor, primary-disclosed;
  PostgreSQL/open-source and AI-architecture risk, evidence gap.
- **AI-narrative-vs-consumption risk** — qualitative claims outpace
  quantified evidence (§7).
- **GAAP profitability inflection unconfirmed** — one positive quarter
  after a noisy, non-monotonic series (§5).

---

## 15. Fresh-price checkpoint

Re-bound via the Gate B pipeline as of 2026-09-07:

- **Latest completed U.S. session: still 2026-09-04** — 2026-09-07 is Labor
  Day (U.S. market holiday); no new completed session exists since the
  triage record's bind.
- **Price: $368.74, unchanged**, `FRESH`, identity confirmed unambiguous
  (`SEC-CIK:0001441816:MDB`, MIC `XNMS`).
- Price is unchanged from the triage checkpoint — **no valuation work
  required re-running**; §8–§10 above use the same $368.74 input.

---

## 16. Final disposition

> ## `NO_DEMONSTRATED_EDGE`

**Rationale.** The triage-stage variant rested specifically on RPO/cRPO
growing far faster than revenue (+91%/+73% YoY) as evidence the market was
under-weighting real forward momentum. This record's quarter-by-quarter
reconstruction of the same primary disclosure (§4) shows that acceleration
was concentrated entirely in a step-change two-to-three quarters ago and
has since **decelerated to a pace slower than revenue growth itself** — the
specific mechanism the variant depended on has already played out and is
not a live signal. Atlas growth remains genuinely flat at ~29% for a third
consecutive quarter with no confirmed reacceleration catalyst in primary
evidence. The reverse-engineered priced-in test (§8) and scenario framework
(§9) both independently show the current price already sits above what
this record's own Base case would justify — not a name priced for
disappointment, but one priced for sustained multi-year reacceleration the
recent evidence does not currently support.

Real, if modest, positives were found and are recorded fairly: broad-based,
continuing customer growth (§3), an improving SBC-to-revenue ratio and a
first clearly positive GAAP operating quarter (§5), and no debt with a
functioning buyback program. **None of these rises to the level of the
specific, distinctive edge the discovery-stage variant proposed**, and per
standing governance this record does not substitute a new, untested thesis
to rescue the candidate. This is a rejection of the tested variant, not a
statement that MDB is a bad business or that no future variant could exist
if the named falsifiers (§13) resolve favorably.

**Stage 7 has not begun.** No return band, position size, or capital
comparison is constructed by this record.

---

## What this record does not do

No Stage 7 comparison. No Stage 8 decision. No capital allocated. No
architecture change. PATH (`NO_DEMONSTRATED_EDGE`), SPXC
(`SURFACE_WITH_EVIDENCE_GAP`), SOLS (`EVENT_DRIVEN_HOLD`), PCG
(`SURFACE_WITH_EVIDENCE_GAP`), and DOCU (`SURFACE_WITH_EVIDENCE_GAP`) are
unchanged and were not touched by this record. Batch 001 (AVGO, XOM, SMH,
AAPL, JPM, NVDA) is unchanged. XOM is not advanced.

**Capital status: NO REAL PORTFOLIO ACTION.**
