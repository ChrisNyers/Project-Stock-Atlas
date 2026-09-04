# Stock Atlas — Master Project Plan

Authoritative status record. Updated as gates close; prior entries are not
rewritten.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## Governing Mission

> **Stock Atlas exists to make money by finding, validating, and capturing
> genuine investment edge and alpha through disciplined capital allocation.**

Process quality, controls, pilots, research depth, and software architecture
are **supporting mechanisms, not the objective.**

Read every status below against that mission. A green test suite is not
progress toward it; evidence of edge is.

---

## Architecture (frozen)

```
Discovery → Underwriting → Stage 7 Capital Comparison → Fresh-Price Check
         → Human Stage 8 → Decision Record → Revisit
```

Stage 7 compares and emits no `PortfolioAction`. Stage 8 is human. Human
allocation authority is unchanged.

---

## Phases 1–4 / Core Foundation

> ### Status: **COMPLETE / FROZEN WHERE GOVERNED**

Includes:

- Methodology v1.0
- Calibration / Investor Policy
- Governing system specification
- Portfolio and concentration controls
- Evidence and provenance controls
- Security Decision / Portfolio Action separation
- Sequential next-dollar allocation
- Fresh-price control
- Free/public-first data architecture
- Code Red Team / frozen control layer
- Gate B live-data binding

**Do not reopen these layers** unless a future pilot exposes a material
decision defect.

### Commit lineage

| Layer | Status | Commit |
|---|---|---|
| Phase 4A.5.0 baseline | COMPLETE / FROZEN | `d37f654` |
| Phases 4A.5.1 – 4A.5.2A (SEC, identity, period, market data) | COMPLETE | `59911d2` |
| Pilots 1–4 manual methodology + doctrine | COMPLETE | `bf03986` |
| v0.2 control-layer merge + capital-decision facade | ACCEPTED (Final Code Red Team) | `8dba996` |
| Gate B live data binding (B1–B5) | CLOSED — awaiting Gate B Red Team review | `4c71d06` |
| Stage 8 allocation-rationale fields | COMPLETE | `22f7077` |
| Records-scope clarification | COMPLETE | `acfd446` |

Governing suite: **245 passed.** All 10 v0.2 control-layer files remain
byte-identical to the Red-Team-accepted archive.

> **Gate B note for the reviewer — market-hours test defect, control not at
> fault.** Two Gate B B1 tests asserted `FRESH` unconditionally. Run during an
> open session (2026-09-04 17:24 UTC) they failed, because the calendar
> correctly attested 2026-09-03 as the latest *completed* session while the
> provider stamped the in-progress 2026-09-04 — so the binder marked the
> observation `STALE` and refused it. **That refusal is the B3 rule working.**
> The tests now assert the correct behaviour in both market states and pass
> mid-session. The frozen Gate B review target `4c71d06` is unchanged; this is
> a forward test-harness fix, and the original 31/31 evidence was gathered
> after the close.

---

## Control Validation Dry Run

> ### Status: **COMPLETE**

**Nomenclature note.** This exercise was previously referred to as
*"Pilot 2 Dry Run."* For project-plan clarity it is renamed here to
**CONTROL VALIDATION DRY RUN**. It was a control/system validation exercise —
**it is not the current Pilot 2 learning experiment.**

Historical underlying records and artifacts remain unchanged, including
everything under `docs/pilot2/` (the ACN / RMD / TROW / VICI / ORCL
differentiation loop, with RMD funded on paper). This is nomenclature cleanup
only; no record was edited.

> **Directory caution.** The historical artifacts live in `docs/pilot2/` under
> their original `PILOT2_*` filenames. The new Pilot 2 (Variant Edge) writes to
> `docs/pilot2_variant_edge/` so the two are never confused. Paths are
> historical fact and are not renamed.

---

## Pilot 1 — COMPLETE

**Purpose:** test whether Stock Atlas could run an end-to-end decision process
and legitimately **refuse to deploy capital.**

**Canonical Stage 8 decision:** September 1, 2026 — **$50,000 paper capital →
Treasury/Cash Sleeve.** Record:
[`pilot1/PILOT1_STAGE8_HUMAN_DECISION_001.md`](pilot1/PILOT1_STAGE8_HUMAN_DECISION_001.md).

> ### Status: `FROZEN / COMPLETE`

### Principal learning

Stock Atlas demonstrated **process coherence** and the ability to let cash beat
equity candidates.

> **It did not demonstrate investment edge.**

Against the governing mission, that is the finding that matters.

---

## Post-Pilot-1 Calibration — COMPLETE

**September 3, 2026 paper allocation. Separate from canonical Pilot 1.**

| Asset | Allocation |
|---|---:|
| Tencent | $25,000 |
| VEON | $10,000 |
| SPY | $10,000 |
| 1-Year Treasury | $5,000 |
| **Total** | **$50,000** |

### Learning

The allocation was described by Chris as **"Taking a stab in the dark."** This
exposed the gap between **underwriting quality** and **explicit allocation
reasoning.**

### Resulting accepted control

> `ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`

Implemented inside `FINAL_CAPITAL_DECISION` as human-authored fields. **No
optimizer, score, ranking engine, or automated sizing system was added.**

> ### Status: **COMPLETE**

Scope: see `PILOT1_DECISION_RECORD_SCOPE_CLARIFICATION` in the
[Decision Log](STOCK_ATLAS_DECISION_LOG.md). Neither this nor the September 1
decision supersedes the other.

---

## Pilot 2 — VARIANT EDGE & INTENTIONAL ALLOCATION

> ### Status: **CHARTER / BASKET DESIGN**

**This is the next active pilot.** Charter:
[`pilot2_variant_edge/PILOT2_VARIANT_EDGE_CHARTER_001.md`](pilot2_variant_edge/PILOT2_VARIANT_EDGE_CHARTER_001.md).

### Primary hypothesis

Can Stock Atlas identify a **falsifiable variant view** and use that edge claim
to support an intentional human allocation *or refusal* versus competing
securities, SPY, Treasury/Cash, and Do Nothing?

Pilot 2 must distinguish:

> **attractive under Atlas assumptions** — from — **genuine potential
> mispricing / edge**

### Parameters

| | |
|---|---|
| Capital | $50,000 paper/shadow, live market data |
| Basket | 10 securities + SPY + Treasury/Cash + Do Nothing |
| Basket freeze | **Must be frozen before underwriting starts** |
| Basket construction | A **discrimination set**, not simply ten attractive stocks |
| Sentiment | **SHADOW ONLY** — no effect on promotion, underwriting, Stage 7, Stage 8, or allocation |
| Portfolio context | Existing lightweight snapshot / overlap / capacity / common-driver controls where useful. **No portfolio optimizer.** |
| Architecture | **FROZEN** |

**Pilot 2 is a learning experiment, not a feature sprint.**

---

## Future Pilot Candidates — NOT ACTIVE

**Do not assign numbers yet.** Future pilot questions are selected from actual
learning, not from a predefined roadmap.

One strong parked candidate:

> **Can Stock Atlas preserve source provenance while eliminating source
> privilege?**

This would test whether ideas originating from Chris/Karen, an outside
investor, research, the existing basket, or another source receive capital
based on **evidence and portfolio fit** rather than familiarity or who supplied
the idea. The concept is already captured in earlier Stock Atlas research and
remains available for a later learning cycle. **It is not mixed into Pilot 2.**

Other future tests remain uncommitted until Pilot 2 teaches us what matters
next.

---

## Parked / Future Research

Kept **outside** the active build:

- Monetary-debasement / required-return hypothesis
- Secular adoption curves
- Agentic-economy value-accrual map
- Sentiment as a possible production input
- Watchman
- Scout
- Additional automation / agents
- Paid / commercial data sources

**These are hypotheses, not roadmap commitments.** Promote only when evidence
shows they could improve the ability to find and capture alpha.

---

## Live Capital

> ### Status: **NOT YET AUTHORIZED AS THE NEXT PROJECT STEP**

Before meaningful real-capital deployment, all of the following must be
present:

- Real portfolio snapshot
- Actual exposure / capacity controls
- Real funding pocket
- Complete Stage 8 rationale fields
- Human Stage 8 authority
- Current decision-time data

Whether Pilot 2 completion is sufficient to move to a controlled live sleeve
**will be decided after Pilot 2, based on its evidence.**

Gate B remains open pending its Red Team review (`4c71d06`); the ELIGIBLE
branch has never been exercised on live data.

---

## Immediate Next Actions

| # | Action | State |
|---|---|---|
| 1 | Freeze this cleaned Master Project Plan | **DONE** — this document |
| 2 | Create Pilot 2 Charter | **DONE** — charter drafted |
| 3 | Select and freeze 10-name discrimination basket | **BLOCKED — awaiting human selection** |
| 4 | Do not underwrite before basket freeze | enforced by the charter's freeze gate |
| 5 | Execute Pilot 2 | not started |
| 6 | Stage 8 paper allocation | not started |
| 7 | Pilot 2 Health Review | not started |
| 8 | Red Team | not started |
| 9 | Decide what worked, failed, or is missing | not started |
| 10 | Build nothing unless the learning earns it | standing rule |

**Current active task: PILOT 2 CHARTER + 10-NAME DISCRIMINATION BASKET.**

Action 3 is a human investment judgement. Atlas does not select the basket —
doing so would be inventing investment conclusions and would contaminate the
very hypothesis Pilot 2 exists to test. The charter specifies what the
discrimination set must *do*; the names come from Chris.
