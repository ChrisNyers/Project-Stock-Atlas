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

> ### Status: **STAGE 8 IN PROGRESS — TWO DECISION CYCLES RECORDED**

Basket frozen September 4, 2026 as `FROZEN / PRE-REGISTERED` (charter §18–21):
FIS · FISV · MELI · JD · ADBE · SNOW · WCC · GLNG · NTR · CVS, plus SPY,
Treasury/Cash and Do Nothing as live alternatives. No additions, substitutions,
removals or rebalancing without an explicit documented scope change.

Test inputs only — not recommendations, rankings, or preliminary conclusions.
No security begins preferred, promoted, eligible, underwritten or funded.

**Venue readiness:** all 10 frozen basket names verified live to an explicitly
supported MIC (5 NYSE, 5 Nasdaq across `XNGS`/`XNMS`) after a narrow Nasdaq
session-calendar extension — `PILOT2_NASDAQ_SESSION_BINDING_EXTENSION` in the
[Decision Log](STOCK_ATLAS_DECISION_LOG.md); detail in charter §22–23.

Discovery, promotion-check, deep underwriting and Stage 7 have all run: FIS
and JD reached `ELIGIBLE_FOR_STAGE8`; MELI was refused as
`NO_DEMONSTRATED_EDGE` on a well-evidenced cautionary variant; GLNG remains
`BLOCKED_BY_MATERIAL_UNCERTAINTY`. Two independent Stage 8 paper/shadow
decision cycles are recorded — Cycle 1 (randomized, LOW confidence, Loop A
= NO) and Cycle 2 (intentional, MEDIUM confidence, Loop A = YES) — each
preserved separately in `docs/pilot2_variant_edge/`, neither rewriting the
other.

**Testing-mode allocation clarification** (accepted operating rule, see
`STAGE8_KEY_RISKS_CONSIDERED` in the [Decision Log](STOCK_ATLAS_DECISION_LOG.md)):
paper/shadow allocations may be random or exploratory by design. Random
sizing during system testing is **not** evidence that the allocation layer is
weak or that intentional allocation failed. Live-capital allocation
discipline may become more deliberate or structured later, based on pilot and
outcome evidence — no sizing engine or formula is pre-built ahead of that
evidence.

**This is the active pilot.** Charter:
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

## Pilot 3 — OPPORTUNITY DISCOVERY SHADOW TEST

> ### Status: **ACTIVE — BATCH 001 IN PROGRESS**

Builds on the compact historical record
[`pilot3/PILOT3_RECORD_001.md`](pilot3/PILOT3_RECORD_001.md) (2026-09-02, not
modified, not superseded), which demonstrated source-blind capital allocation
in one controlled paper case. Pilot 3 now tests the same core question
against a new, named external discovery source, **Agent World**:

> Can an opportunity-discovery layer surface worthwhile ideas Atlas likely
> would otherwise have missed, and do those ideas survive the existing Atlas
> underwriting process?

**Not a test of idea volume.** No agent score, source score, ranking, or
discovery-quality algorithm exists or is planned. Governing principle:
**preserve provenance, remove privilege** — source state is logged, never
treated as underwriting privilege.

**Batch 001** (`pilot3/PILOT3_AGENT_WORLD_BATCH_001.md`): six candidates
registered — XOM (`SURFACE_WITH_EVIDENCE_GAP`, awaiting first completed U.S.
session following a geopolitical/oil move), SMH (`REFERENCE_PEER_TAPE`),
AVGO (`ADVANCE_TO_PRIMARY_EVIDENCE_TRIAGE`), AAPL and JPM
(`CALENDAR_HOLD`), NVDA (`REFERENCE_ONLY`). AVGO's primary-evidence triage
(`pilot3/PILOT3_AVGO_PRIMARY_EVIDENCE_TRIAGE_001.md`) returned
`PROMOTE_TO_DEEP_UNDERWRITING`. AVGO's deep underwriting
(`pilot3/PILOT3_AVGO_DEEP_UNDERWRITING_001.md`) returned
`BLOCKED_BY_MATERIAL_UNCERTAINTY`: real business quality (RPO backlog,
FCF quality, balance-sheet flexibility) survived, but the triage-stage
mispricing variant did not — a corrected consensus/priced-in test showed
the price already requires continued strong execution, and named evidence
gaps (non-AI trend, AI-specific customer concentration, software/VMware
detail) remain unresolved. Stage 7 has not begun.

**Manual Discovery Batch 002** (`pilot3/PILOT3_MANUAL_DISCOVERY_BATCH_002.md`),
source `MANUAL_DISCOVERY_BRIDGE` — a temporary bridge while Agent World is
not yet fully operational, carrying no underwriting privilege over Agent
World candidates. Six candidates registered (PATH, MDB, SPXC, SOLS, PCG,
DOCU); only PATH and MDB received primary-evidence triage.
`pilot3/PILOT3_PATH_PRIMARY_EVIDENCE_TRIAGE_001.md` returned
`NO_DEMONSTRATED_EDGE` (the discovery variant was contradicted by a
primary, guided revenue-growth deceleration, roughly halving 13%→7–8% YoY,
and by a valuation already repriced for weaker growth).
`pilot3/PILOT3_MDB_PRIMARY_EVIDENCE_TRIAGE_001.md` returned
`PROMOTE_TO_DEEP_UNDERWRITING` (the discovery variant was corroborated by
primary RPO/cRPO acceleration of +91%/+73% YoY, far outpacing the 29–30%
revenue/Atlas growth the market reacted to, and a direct management
attribution). SPXC, SOLS, PCG, and DOCU remain registered but untriaged.

**Current active next action:** Manual Discovery Batch 002 — PATH and MDB
primary-evidence triage; XOM awaiting next completed U.S. session. AVGO
remains closed at `BLOCKED_BY_MATERIAL_UNCERTAINTY`, pending its named
falsifiers/revisit triggers.

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
| 3 | Select and freeze 10-name discrimination basket | **DONE** — frozen 2026-09-04 |
| 4 | Do not underwrite before basket freeze | **SATISFIED** — freeze recorded before any underwriting |
| 5 | Execute Pilot 2 | **NEXT** |
| 6 | Stage 8 paper allocation | not started |
| 7 | Pilot 2 Health Review | not started |
| 8 | Red Team | not started |
| 9 | Decide what worked, failed, or is missing | not started |
| 10 | Build nothing unless the learning earns it | standing rule |

**Current active task: EXECUTE PILOT 2 — underwriting against the frozen
basket, not yet begun.**

Action 3 was a human investment judgement, as it had to be. Atlas did not
select the basket — doing so would have invented investment conclusions and
contaminated the very hypothesis Pilot 2 exists to test. The charter specified
what the discrimination set must *do*; the names came from Chris.
