# PILOT 5 — CTVA INDEX-FLOW TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Primary-evidence forced-flow triage only. No fundamental underwriting. No
> capital decision. No Stage 7. No position size, score, or price target.

| | |
|---|---|
| Date | October 1, 2026 (evidence through ~7:10 PM EDT, after the close) |
| Prior state | `SURFACE_FOR_TRIAGE` (`PILOT5_DISCOVERY_SCAN_002_REGISTRATION.md`) |
| Source | `GROK_SCOUT_FORCED_FLOW_DISCOVERY` |
| Question | Does the CTVA S&P 500 → S&P MidCap 400 migration plausibly create a net mechanical imbalance large enough to distort price, separable from the spin adjustment and from fundamentals? |

---

## 1. Canonical identity and original index announcement

- **Corteva, Inc.**, NYSE `CTVA`, SEC CIK `0001755672`, USD, common stock
  (identity per the S&P release and Corteva's SEC filings; ticker and exchange
  unchanged by the spin). GICS Materials.
- **Trading status:** trading normally. First post-distribution session was
  Oct 1, 2026. About 667.2M shares outstanding (one class; unchanged by the
  spin). Aggregator-sourced, not a primary share count.
- **Original announcement:** S&P Dow Jones Indices press release dated
  Oct 1, 2026 ("Vylor Added to the S&P 500; Twilio Set to Join S&P 500;
  Others to Join S&P MidCap 400 and S&P SmallCap 600").

## 2. Confirmed migration dates (from the release's own table)

| Effective | Index | Action | Company |
|---|---|---|---|
| Oct 1, 2026 | S&P 500 | Addition | Vylor (VYLR), Consumer Staples |
| **Oct 6, 2026, prior to the open** | **S&P 500** | **Deletion** | **Corteva (CTVA)** |
| **Oct 6, 2026, prior to the open** | **S&P MidCap 400** | **Addition** | **Corteva (CTVA)** |
| Oct 6, 2026, prior to the open | S&P MidCap 400 | Deletion | Olin (OLN) |
| Oct 6, 2026, prior to the open | S&P SmallCap 600 | Addition / Deletion | Olin in / Qorvo (QRVO) out |
| Oct 6, 2026, prior to the open | S&P 500 / 400 / 600 | Second transaction | Twilio ↑500 (replaces Warner Bros. Discovery, an acquisition), Formfactor ↑400, Workiva ↑600 |

- **Trading window.** "Effective prior to the opening of trading on Tuesday,
  October 6" means index funds trade at the **Monday, October 5 close**. The
  sessions that matter are Fri Oct 2 and Mon Oct 5, with the closing auction
  on Oct 5 being the point of mechanical execution. Oct 6 is the first
  post-migration open.
- **CTVA stays in the S&P 500 through the Oct 5 close**, alongside VYLR. This
  is why S&P 500 funds had no required CTVA sale on Oct 1.
- Release rationale (quoted): "Post spin-off, Corteva will be more
  representative of the mid-cap market space." Vylor takes a Consumer Staples
  GICS classification on Oct 6.
- **Subsequent notices:** none found altering these mechanics as of this
  record. An earlier S&P notice of the CTVA migration was **not located**; the
  first located publication is the Oct 1 release (a secondary article dates
  it ~6:51 PM EDT; the release's own time was not verified). Solactive's notice
  covers only the VYLR addition (ex-date Oct 1) and states no CTVA deletion
  mechanics.
- Caution: one summarizer described Corteva as "removed from the S&P 500 on
  October 1" in an earlier pass. The release's own table and text control.

## 3. Must-sell versus must-buy mechanics

This is a **migration**, not one-directional selling.

| Holder | Required action at the Oct 5 close | Basis |
|---|---|---|
| S&P 500 index-tracking funds (and benchmarked sector/style sub-index funds) | **Sell CTVA** (full deletion) | Documented in the release |
| S&P MidCap 400 index-tracking funds | **Buy CTVA** (addition), partly funded by selling Olin | Documented in the release |
| Funds tracking other benchmarks (Russell, MSCI, CRSP, total-market) | No S&P-driven trade identified; treatment of this spin and any size-segment changes **not verified** | Unverified |

The imbalance is therefore **S&P 500 passive holdings sold minus MidCap 400
passive holdings bought**, both measured in CTVA shares.

## 4. Potential net-flow assessment (estimate, not fact)

**Documented facts used:** ≈667.2M CTVA shares; Oct 1 close $12.57; market cap
≈$8.4B. Aggregate index data (as quoted by Wikipedia from S&P DJI): ≈$13T
tracking the S&P 500 as of Dec 31, 2024, against index market cap >$61.1T as
of Dec 31, 2025; ≈$337B tracking the S&P MidCap 400 as of Dec 31, 2024,
against index market cap >$2.9T as of Dec 31, 2025.

**Estimate (labeled as such).** Ratios of tracking assets to index market
capitalization: S&P 500 ≈ 21% on those numbers, probably 21–25% once dates
match; S&P 400 ≈ 11.6%, call it 11–13%. Applied to CTVA's shares (float
adjustment not verified, assumed near 1):

| | Low | High |
|---|---|---|
| S&P 500 passive sale | ≈140M sh | ≈167M sh |
| MidCap 400 passive purchase | ≈73M sh | ≈87M sh |
| **Net passive sale** | **≈53M sh** | **≈93M sh** |
| As % of shares outstanding | ≈8% | ≈14% |
| Dollar value at $12.57 | ≈$0.67B | ≈$1.17B |

**This is not a forced-share count.** It is a bracket built from aggregate
ratios with mismatched dates, a float assumption, and no fund-level holdings
data. The **sign** (net sale) is better supported than the magnitude,
because S&P 500 passive ownership runs well above mid-cap passive ownership.
The magnitude could easily be ±50%. No precise forced-seller number is
manufactured.

## 5. Liquidity and float context

- Oct 1 volume ≈ **88.0M shares** (≈13.2% of shares outstanding), against an
  average volume of ≈4.45M (Yahoo; averaging period not stated). Oct 1 is the
  mechanical repricing and repositioning day and is not a clean baseline.
- The bracketed net sale equals **≈12–21 days of average volume** and **≈60–105%
  of Oct 1's volume**.
- Natural counterparties: MidCap 400 index funds (the documented buyers),
  active mid-cap and crop-protection/chemicals managers, event-driven and
  index-arbitrage desks (who have had at most the Oct 2 and Oct 5 sessions if
  the Oct 1 release was first notice), and dividend/value holders.

## 6. Correct treatment of ex-spin pricing

**CTVA's −83.8% on Oct 1 is a mechanical corporate-action adjustment, not an
economic collapse.** The $77.65 prior close was a cum-distribution price for
a share carrying the right to one VYLR share.

| Basis | Value |
|---|---|
| CTVA prior close, cum-distribution | $77.65 |
| VYLR Oct 1 close (uncertified) | $68.26 |
| Implied residual reference for CTVA (77.65 − 68.26) | **$9.39** (reconciliation basis, not a target or fair value) |
| CTVA Oct 1 close | $12.57, **≈34% above** the residual reference |
| One CTVA + one VYLR at the close | **$80.83, +4.1%** versus $77.65 |
| S&P 500 Oct 1 | +0.19% (secondary report) |

The earlier **$12.75 intraday CTVA observation is not used** as a completed
session price. Oct 1 session (Yahoo and StockAnalysis agree): open 14.44 (=
the day's high), low 11.84, close **12.57**, volume ≈87.94–88.0M, after-hours
≈12.48. Any historical CTVA price series must be adjusted for the
distribution before use; vendors' unadjusted "−83.8%" is not an economic
return.

## 7. Fundamental-change assessment

Scout flagged four items. Verification:

| Scout item | What primary/near-primary sources show | Economic weight |
|---|---|---|
| PFAS settlement | Chemours 8-K (Sept 10, 2026): **$455M** aggregate, 15-year payout; Chemours 50%, DuPont and Corteva share the other 50% (Corteva ≈25% ≈ **$114M** nominal). Announced **Sept 10, not Oct 1**. | Small against ≈$8.4B equity. Not a new Oct 1 event. |
| Credit rating | S&P Global Ratings: **A− → BBB+**, Sept 17, 2026, outlook stable; cited narrower scale and diversification after the spin. (Via an Investing.com summary; S&P's own report was not read.) | A real, disclosed change that was pre-spin and already known. |
| State AG lawsuit | Actually a **settlement**, not a new suit. FTC release (Sept 28, 2026): $35M to state plaintiffs, 10-year ban on loyalty/share-based rebate programs across all post-patent actives; stipulated order awaits court approval. Arkansas settled separately (Aug 2026, secondary). | $35M is immaterial. The conduct remedy is the real economic item (price/rebate flexibility vs generics), **not quantified**. |
| Crop-protection pricing pressure | Follows from the FTC remedy. No dollar impact found. | Unquantified. |

Other facts, from a secondary summary: S&P cites pro forma 2025
crop-protection EBITDA of **$1.35B**, a target debt/EBITDA not above 2.0x, and
retained PFAS, crop-protection, and underfunded-pension liabilities. The same
summary says seed was "34% of pre-separation EBITDA", which does **not**
reconcile with the frozen Seed EBITDA of $2.636B, so I do not rely on it.
CTVA's post-spin debt and equity-value bridge was **not** assembled.

**Separation of the three effects.** (1) The mechanical adjustment explains
the entire −83.8%. (2) Index-related trading has not yet occurred at its
documented point, the Oct 5 close. (3) Fundamental items are all dated Sept
10–28, before the spin, and were in the $77.65 cum price. None shows
Oct 1 deterioration. On the combined position CTVA+VYLR **rose**. So
fundamentals do not independently explain any index-window weakness that
may appear, and whether CTVA is cheap or expensive on fundamentals is **not
assessed here**.

## 8. Completed-session evidence

Only **one** post-spin session exists (Oct 1). **Missing, precisely:** the
Oct 2 session; the Oct 5 session including the closing auction and
imbalance; the Oct 6 open and following sessions. Price evidence is
**uncertified** (no `TWELVEDATA_API_KEY`; Gate B blocked for CTVA and VYLR
alike). No closing-auction evidence exists and none is claimed. Sector or
peer comparisons (Materials, crop-protection names) were not retrieved.

## 9. Recognition and timing

- The mechanism is **structurally known**: S&P publishes its spin-off and
  migration methodology and its size ranges, and a $8.4B post-spin company
  sits at the low end of the MidCap 400's stated $1.5B–$33.6B range. An
  index-arbitrage desk could reasonably have expected a migration, but no
  earlier S&P notice was found.
- The Oct 1 volume (≈20x average) shows heavy repositioning already, so some
  of the mechanical supply may have been absorbed. Whether it was cannot be
  determined from one session.
- Early relative to the announcement is not early relative to specialist
  recognition. Atlas has no evidence it is early relative to either.

## 10. Strongest market-could-be-right case

CTVA may simply be a lower-quality stub whose fair value is below the Oct 1
price: a crop-protection-only business with a downgraded rating, a 10-year
FTC conduct remedy that exposes branded products to generics, retained PFAS
and pension liabilities, and pro forma 2025 crop-protection EBITDA of
only $1.35B (secondary source). CTVA also already trades ≈34% above its
VYLR-implied residual, so an index-fund sale that pulls it down toward the
residual could be a correction, not a dislocation. Combined holder value
rose on Oct 1. Passive sales of 8–14% of shares could also be fully absorbed
by the documented MidCap 400 buyers and arbs with no visible price effect, as
index-deletion effects are often small and short-lived.

## 11. Cheapest falsification result

> After adjusting for the Vylor distribution and the documented fundamental
> developments, is there a plausible net mechanical imbalance large enough to
> create temporary mispricing?

**Not falsified.** The bracketed net passive sale (≈8–14% of shares, ≈12–21
days of volume) is not economically immaterial; fundamental items do not
explain it; and its pricing effect cannot be assessed until the Oct 2 and
Oct 5 sessions exist. It would be falsified by: a showing that the net sale
is near zero once actual fund holdings are used; Oct 5 closing-auction and
Oct 6 data showing full absorption with no dislocation; or fundamentals
that fully explain a residual decline. **The hook is weakened by the
unknown anticipation, the mismatched-date inputs, and the dirty
fundamentals, but survives triage.**

## 12. Best-expression observation

CTVA is the **direct** subject of the migration and the only
**S&P 500 → MidCap 400 down-migration** in the release's table. The rest of
the cascade differs in kind: Warner Bros. Discovery leaves the S&P 500
because it is being acquired (a merger exit, not an index-driven sale);
Twilio, Formfactor, and Workiva are up-migrations (buy-dominated); Olin
moves 400 → 600 and Qorvo leaves on its acquisition. I did not size or research
those securities. **No trade selected; no candidate created.** Whether the
CTVA stub is the right security to own versus VYLR or nothing is a
valuation question reserved for underwriting.

## 13. What Atlas added beyond Scout

- Confirmed from the S&P release's own table that CTVA remains in the S&P
  500 through the **Oct 5 close**, so the forced trade is on **Oct 5**, not
  Oct 1; Scout's window was right but its mechanics were not stated.
- Reframed the hook from "forced selling" to **migration**: S&P 500 sellers
  versus MidCap 400 buyers, with a net sale **bracket** and its limits.
- Showed the −83.8% is a corporate-action artifact, and built a post-spin
  reference basis ($9.39 residual; combined +4.1%).
- Corrected Scout's "state AG lawsuit": a Sept 28 **settlement** with a
  $35M payment and a pending court order. Corrected the PFAS timing: Sept
  10, with Corteva's share ≈$114M nominal. Flagged that one article blames
  the Oct 1 move on PFAS, which is auto-generated and wrong.
- Identified the missing observations (Oct 2, Oct 5 auction) rather than
  inferring them.
- Carried the Vylor lesson forward: the index outcome was unknown there and
  went against the thesis; here it is documented in primary text.

## 14. Final disposition

> ## `PROMOTE_TO_FUNDAMENTAL_UNDERWRITING`

**Meaning, and only this:** the mechanism is confirmed from a primary source
with exact dates, a plausible net passive sale exists that is not
economically immaterial, and the known fundamental items do not
independently explain it. A valuation framework and a pass/fail
threshold should be written **before** the Oct 5 close, as with Vylor. It does
**not** mean buy, does not mean Stage 7, and is not a finding of
dislocation: **no price evidence of dislocation exists yet.** Promotion is not
based on the fact that index funds must trade; it is based on a documented
mechanism, a bracketed imbalance, and fundamentals that do not obviously
absorb it. If underwriting finds the dirty fundamentals dominate valuation,
the correct outcome is `NO_DEMONSTRATED_FORCED_FLOW_EDGE`, consistent with
the Crasus and MSGR lesson.

## 15. CBRS

Registered as surfaced only. **Untouched and unresearched.**

## 16. Frozen-record isolation

Unchanged: Vylor triage, underwriting, and price-test records; Crasus; MSG
Rangers; Pilot 4 records; the frozen control layer; the facade. No code,
test, or configuration changed.

## What this record does not do

No CTVA fundamental underwriting or valuation. No Stage 7 or Stage 8. No
capital decision, position size, score, or price target. No CBRS research.
No new data provider or architecture. No second discovery scan.

**Capital status: NO REAL PORTFOLIO ACTION.**
