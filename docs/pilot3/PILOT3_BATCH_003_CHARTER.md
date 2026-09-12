# PILOT 3 — NARROW DISCOVERY FIX + BATCH 003 CHARTER

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> This record adopts two narrow, evidence-earned process fixes and charters
> Batch 003. **It does not create any Batch 003 candidate.** It does not
> modify, rewrite, or supersede any prior Pilot 3 record — Batch 001 and
> Batch 002 (AVGO, PATH, MDB, SPXC, SOLS, PCG, DOCU, XOM, AAPL, JPM, SMH,
> NVDA) remain frozen exactly as closed.

| | |
|---|---|
| Date | September 12, 2026 |
| Pilot | Pilot 3 — Opportunity Discovery Shadow Test |
| Scope | Discovery-process governance only; no architecture change |

---

## 1. Red Team verdict

> ## `CONTINUE_WITH_NARROW_FIX`

**Reason, as given:** Pilot 3 discovery is producing plausible,
falsifiable ideas, and underwriting is successfully rejecting false
positives — twelve candidates processed across Batch 001 and Batch 002
with five promotions, three blocks, and four rejections/holds, each on
differentiated primary evidence (see the Batch 001/002 discovery logs).
**Zero Stage 7 survivors is not, by itself, treated as a failure** —
it is treated as evidence the underwriting stage has real teeth.

**However, two specific weaknesses are named, and only these two:**

1. Discovery is over-sampling post-event / familiar-theme setups (beat-
   and-raise-but-sold-off, mega-cap thematic exposure, post-earnings
   selloffs).
2. Some candidates receive substantial deep-underwriting work before the
   original discovery hook is cheaply disproven — the hook itself is not
   tested first, at low cost, before a full variant is written.

**No other finding from this review is adopted as a process change.** No
scoring, ranking, sentiment-promotion, or discovery-quality engine is
introduced.

---

## 2. Narrow Fix 1 — Hook Reconstruction at triage

**Decision identifier: `PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`**

**Rule, effective prospectively beginning with Batch 003:**

When a discovery hook depends materially on any of —

- acceleration,
- margin change,
- bookings / RPO,
- product / segment mix,
- FCF improvement,
- new-product penetration —

— then **primary-evidence triage must first reconstruct that specific
metric across the last 4 reporting periods** before the full candidate
variant is written up. The reconstruction must show:

- the last 4 reporting periods of the relevant metric;
- the sequential (quarter-over-quarter) trend, where meaningful;
- the year-over-year trend, where meaningful;
- one mix line, if the hook depends on segment/product mix.

**If that 4-period reconstruction shows the hook has already peaked,
reversed, or flattened materially, triage must stop or block the
candidate unless another, independent source of edge remains** — the
full candidate variant is not written up around a hook the cheapest
available evidence has already weakened or killed.

**Explicitly not built:** no historical-data engine, no automated
sequential-reconstruction tool, no scoring of trend quality. This is a
four-period, human-readable check performed with the same primary-source
tools (XBRL company facts, direct filing review) already used throughout
this pilot — the same discipline this pilot already applied ad hoc at
MDB, DOCU, SPXC, and SOLS, now made a **required, first, cheap** step at
triage rather than something reached only during deep underwriting.

---

## 3. Narrow Fix 2 — Priced-in one-liner

**Decision identifier: `PILOT3_PRICED_IN_ONE_LINER`**

**Rule, effective prospectively beginning with Batch 003:**

Before any candidate advances from triage to deep underwriting, triage
must state one sentence in this exact form:

> For this to be mispriced, the market must currently be assuming
> ______.

Illustrative fills (not a fixed list): growth remains permanently below
X; margin recovery does not occur; new-segment growth cannot offset core
decline; the current commodity shock is temporary; acquisition economics
do not improve normalized FCF.

**If this sentence cannot be stated credibly from evidence already
gathered, no clear variant has yet been demonstrated**, and the candidate
does not advance to deep underwriting on that basis alone — it is held at
triage (`SURFACE_WITH_EVIDENCE_GAP`) or closed `NO_DEMONSTRATED_EDGE`,
per the existing triage disposition vocabulary; this fix adds a
**gate**, not a new disposition state.

**Explicitly not built:** no pricing engine, no valuation model, no
automated consensus-scrape. This is a one-sentence variant-clarity test
written by the same evidence-gathering process already used throughout
this pilot.

---

## 4. Prospective application only

**Both fixes apply beginning with Batch 003 candidates only.** No prior
Pilot 3 record is rewritten, annotated, or reopened as a result of this
charter — AVGO, PATH, MDB, SPXC, SOLS, PCG, DOCU, XOM, AAPL, JPM, SMH, and
NVDA remain exactly as closed in their own frozen records. This charter
does not retroactively find any prior record deficient; it changes the
process for what comes next.

---

## 5. Batch 003 discovery objective

Batch 003 tests a **different discovery pond** than Batch 001/002. It
should **not** center on:

- post-earnings selloffs;
- famous mega-cap thematic names;
- "beat and raise but stock fell";
- one-line cheapness;
- generic AI exposure.

**Preferred discovery-hook categories** (not all four need to be
represented; none is forced):

**A. Capital-allocation / balance-sheet change** — unexpected buyback,
debt paydown, dividend initiation/change, asset sale, spin-off,
deleveraging, refinancing, working-capital shift, major capex change.

**B. Neglected / lower-attention security** — lighter coverage, less
crowded narrative, primary evidence plausibly under-synthesized by the
market. **No market-cap rule is imposed.**

**C. Competitor / industry read-through** — one firm's disclosure implies
something material for another before it reports. Preferred form: *"Company
A disclosed ______, which may imply ______ for Company B, while Company
B's price / estimates do not appear to reflect it."*

**D. Quiet regulatory / structural change** — a public-policy, regulatory,
procurement, industry-structure, or supply-chain change with economics
not yet fully reflected in price.

---

## 6. Batch 003 size

**Target: 4–6 candidates maximum.** Quality over quantity — candidates
are not added merely to fill the batch.

**Batch 003 remains unpopulated as of this charter.** No candidate is
registered, sourced, or named by this record.

---

## 7. Required Batch 003 discovery record (template — to be used when Batch 003 is actually populated)

For each surfaced candidate, capture:

1. company / ticker;
2. source provenance;
3. discovery hook;
4. why this may matter economically;
5. 4-period hook reconstruction, if applicable (Fix 1);
6. priced-in one-liner (Fix 2);
7. candidate variant — tentative;
8. credible market-could-be-right alternative;
9. cheapest falsification test;
10. evidence gap;
11. initial disposition — exactly one of: `SURFACE_FOR_TRIAGE`,
    `SURFACE_WITH_EVIDENCE_GAP`, `IGNORE`.

**No funding, no ranking, no score at this stage.**

---

## 8. Cheap-falsification discipline

For every candidate, ask first: **what is the cheapest piece of evidence
that could kill this idea?** Run that check before lengthy research,
wherever feasible. Examples: last 4 quarters; one primary filing; peer
price reaction; balance-sheet reconciliation; segment bridge; management
guidance comparison; consensus-expectations check.

**The objective is not shallower research. The objective is: kill weak
hooks sooner; deep-underwrite only survivors.** This discipline and Fix 1
are complementary, not redundant — Fix 1 is the specific, mandatory
instance of this discipline for metric-dependent hooks.

---

## 9. False-negative awareness — a learning note, not a system

**Recorded for the Pilot 3 health process, not built now:** Atlas must
eventually examine whether rejected candidates were rejected for the
right reason. A future Loop C / outcome-learning process should examine:

- false positives (promoted candidates that should have been rejected);
- false negatives (rejected candidates that later succeeded for the exact
  thesis Atlas dismissed);
- whether the *reasoning*, not just the outcome, was sound.

**This is a learning note, not outcome tracking, not a scoring system.**
Nothing is built or scheduled by this charter to implement it now.

---

## 10. Shadow sentiment

**Unchanged, restated for Batch 003:** sentiment is not added to
candidate promotion, blocking, or funding logic. If sentiment
observations happen to be available during Batch 003 discovery, they are
recorded separately, labeled `SHADOW`, and never used to promote, block,
or fund a candidate, and no sentiment score is created. **Formal
sentiment testing remains a later, separate pilot question.**

---

## 11. Pilot 3 — current interpretation

> Pilot 3 is demonstrating strong false-positive control but has not yet
> demonstrated repeatable discovery of missed investable alpha.

**Batch 003 therefore tests:** whether a more diverse, under-the-surface
discovery source (§5, categories A–D) can produce a candidate that
survives to Stage 7 **without weakening underwriting standards.** The two
narrow fixes (§2, §3) are process improvements to *discovery triage
efficiency*, not a loosening of the underwriting bar that has produced
zero Stage 7 survivors so far — that bar is unchanged by this charter.

---

## 12. What this record does not do

No Batch 003 candidate is created, sourced, or registered. No prior
Pilot 3 record is modified. No scoring, ranking, sentiment-promotion, or
new discovery engine is built. No historical-data engine or pricing
engine is built. No Stage 7 or Stage 8 action. No advance of JPM or AAPL.
No change to the control layer, the facade, or core architecture.

**Capital status: NO REAL PORTFOLIO ACTION.**
