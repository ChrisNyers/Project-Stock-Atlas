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

## Governance Classification

This section **consolidates** decisions already accepted and acted on
elsewhere in this document and in the Decision Log — it creates no new
governance layer, no new document, and no new architecture. Its purpose
is to state plainly, in one place, which rules are permanent, which are
controls currently under test within a specific pilot, and which are
unproven hypotheses for a possible future pilot. Where a rule is already
stated in full elsewhere in this plan, it is cross-referenced here rather
than restated.

### Permanent Governance

- **Human capital allocation authority** — Stage 7 emits no
  `PortfolioAction`; Stage 8 is human; human allocation authority is
  unchanged. See "Architecture (frozen)," immediately below.
- **Fail-closed evidence discipline** — a provider may never be the
  authority on whether its own observation is fresh; ambiguity fails
  closed rather than resolving in the direction of a trade. See the Gate
  B live-price-binding record and the control-layer merge record
  referenced throughout this plan.
- **Provenance over privilege** — source state is logged, never treated
  as underwriting privilege. First stated in Pilot 3 (`preserve
  provenance, remove privilege`) and applied identically to every
  discovery source since (Agent World, the manual-discovery bridge,
  Scout).
- **Immutable frozen records** — completed Pilot 1 and Pilot 2 records,
  closed Pilot 3 company records, and prior Decision Log entries are not
  rewritten once committed. Corrections are appended, never substituted.
- **Live-alternatives / real-decision-time-data requirement** — see "Live
  Capital," below: no real-capital step proceeds on stale or
  provider-self-reported freshness.
- **Discovery Source Neutrality.** Stock Atlas is multi-source by design.
  No discovery source — including Grok Scout or Agent World — may own
  Atlas's workflow, canonical state, validation standards, ranking,
  sizing, or capital-allocation authority. Every discovery source submits
  candidates into the same Atlas validation process, with no
  underwriting advantage over any other source. Atlas must remain fully
  operable if any individual source disappears. **Core test before
  adding anything source-specific to core architecture: would this
  change still improve Atlas if that source disappeared tomorrow? If
  not, it does not belong in core architecture.**
- **Mandatory Scout Feedback Governance.** The direction of learning is
  fixed: Scout surfaces candidates → Atlas tests them against primary
  evidence → Atlas's findings feed back to improve Scout's future
  surfacing. **Atlas never changes its validation standards to
  accommodate Scout.** Scout-improvement feedback should emphasize
  change rather than names, tentative expectations gaps, second-order or
  non-price discovery, the cheapest falsification test, the strongest
  contradictory fact found, why the market might be wrong, and lessons
  from prior failed hooks and false positives (e.g., NHP's and UCB's
  Batch 003 triages). Scout may not rank, size, allocate, self-promote a
  candidate to a later Atlas stage, or alter Atlas's standards.
- **One-New-Information-Family-Per-Pilot Guardrail.** Default: introduce
  no more than one new information family per pilot, unless prior
  evidence clearly earns more. Before adding a lane, ask: (1) does it
  surface opportunities Atlas would otherwise miss; (2) does it improve
  timing or decision quality; (3) is its incremental value worth the
  added complexity? If the answer to any is not clearly yes, do not add
  it.
- **Experiment-First Rule for new discovery / information lanes.** Every
  new lane begins as an experiment, not a permanent feature. It is
  tested for unique discovery value, timing value, variant-quality
  improvement, risk-control improvement, false-positive/false-negative
  impact, and the role it is actually best suited for. It is retained
  only if it materially improves decision quality relative to the
  complexity it adds — this is the same evidence-earned-complexity
  discipline the two guardrails above exist to enforce.

### Pilot Controls (under test, scoped to a specific pilot — not automatically permanent)

- **Pilot 3 Hook Reconstruction at Triage**
  (`PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`) and **Priced-In One-Liner**
  (`PILOT3_PRICED_IN_ONE_LINER`) — see `pilot3/PILOT3_BATCH_003_CHARTER.md`
  and the Pilot 3 section below. Adopted prospectively for Batch 003
  only; not applied retroactively; not yet evaluated for permanence.
- **Current shadow-sentiment treatment** — sentiment observations, where
  encountered, are recorded separately and never used to promote, block,
  fund, or score a candidate. In force for Pilot 3; formal sentiment
  testing remains a roadmap hypothesis, below, not a committed pilot.
- **Batch-specific stop conditions** — e.g., "do not triage SAIA or TCS,"
  "do not start Batch 004" — apply to the work order that issued them,
  not as standing architecture.

### Roadmap Hypotheses (unproven; may change based on evidence; never binding architecture until promoted)

- Forced-flow / source-ownership testing — see "Future Pilot Candidates,"
  below (source-blind capital allocation across Chris/Karen, an outside
  investor, research, or the existing basket).
- Formal sentiment / news / trend testing — see "Parked / Future
  Research," below.
- Capital-cycle / capacity testing; credit-equity divergence; statistical
  / ML testing — not yet scoped to any active pilot.
- Late-Pilot-4 CX / Claude Design work — not yet scoped.

**Consolidation note:** this section restates no substantive rule
differently from where it was first accepted — it only classifies
permanence and cross-references. Nothing above changes human capital
authority, the frozen-record rule, or any completed Pilot 1/2/3 record.

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

> ### Status: **CLOSED — `CLOSE_PILOT3_ADVANCE_TO_PILOT5`** (see
> `pilot3/PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md`)
>
> **Numbering note:** the next experiment is **Pilot 5**, not Pilot 4.
> `docs/pilot4/` already holds a separate, complete, frozen pilot
> (September 2, 2026 — the COST/PH/AMGN incumbent-substitution test and
> its "two-bar rule"), unrelated to forced-flow/ownership-dislocation
> discovery. An earlier draft of this closeout mislabeled the new
> experiment "Pilot 4"; corrected here — numbering only, no substantive
> change. The frozen Pilot 4 materials are untouched.

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

MDB's deep underwriting (`pilot3/PILOT3_MDB_DEEP_UNDERWRITING_001.md`)
returned `NO_DEMONSTRATED_EDGE`: the triage-stage variant relied on
RPO/cRPO growing far faster than revenue (+91%/+73% YoY), but a
quarter-by-quarter reconstruction of the same primary disclosure showed
that acceleration was a step-change concentrated in Q3–Q4 FY2026 that has
since decelerated to a pace slower than revenue growth — the specific
mechanism the variant relied on had already played out. Atlas growth
remains flat at ~29% for a third consecutive quarter, and a
reverse-engineered priced-in test showed the current price already
requires sustained, not merely continued, multi-year growth.

DOCU's primary-evidence triage
(`pilot3/PILOT3_DOCU_PRIMARY_EVIDENCE_TRIAGE_001.md`) returned
`PROMOTE_TO_DEEP_UNDERWRITING`: IAM's share of ARR has risen every quarter
measured (2.3%→10.8%→12.6%→15.1%), with the pace itself accelerating,
corroborated by monotonically improving GAAP margins, a declining
SBC-to-revenue ratio, and a genuine, accelerating reduction in actual share
count. The open question for deep underwriting is whether this converts
into a higher consolidated growth rate rather than continuing to offset
core e-signature maturity (total revenue has held flat at 8–9% YoY for
five consecutive quarters). A Gate-B `FRESH` price bind could not be
obtained (market open at decision time; Gate B correctly returned `STALE`)
— an unvalidated reference price was used with explicit caveats, and a
certified bind should be captured before deep underwriting relies on a
specific valuation figure.

DOCU's deep underwriting (`pilot3/PILOT3_DOCU_DEEP_UNDERWRITING_001.md`)
returned `BLOCKED_BY_MATERIAL_UNCERTAINTY`: durable, multi-quarter
capital-allocation and margin quality survived (buybacks executed at an
average ~$47/share versus a ~$66 reference price; monotonically improving
GAAP margin across six quarters), but a coarse core-versus-IAM ARR
growth-bridge calculation (Atlas-derived from two disclosed annual data
points) found core ARR was approximately flat to slightly declining in
FY2026 — IAM accounts for essentially all net growth, and reaching a
materially higher blended growth regime would require IAM's own
(likely-decelerating) growth rate to re-accelerate, which current guidance
does not support. No Gate-B-certified `FRESH` price could be obtained
(market open at decision time; the binder has no capability to bind a
specific historical close, reported as a limitation rather than engineered
around).

XOM's relative-dislocation resolution
(`pilot3/PILOT3_XOM_RELATIVE_DISLOCATION_RESOLUTION_001.md`) returned
`NO_DEMONSTRATED_EDGE` once the required completed-session evidence
existed: over the observation window (2026-09-04 baseline through
2026-09-10, the latest completed session), XOM led both CVX and XLE on
every session, with the gap widening rather than narrowing — the
pre-registered lag never materialized. Per the governing work order's own
instruction, this is recorded as a successful Pilot 3 discovery-system
outcome (Agent World correctly surfaced a coherent hypothesis; Atlas's
discipline of waiting for completed-session evidence rather than
front-running it is what let this be resolved cleanly).

AAPL's post-event variant test
(`pilot3/PILOT3_AAPL_POST_EVENT_VARIANT_TEST_001.md`) returned
`EVIDENCE_GAP` following the September 9, 2026 event: the $1,999 iPhone
Duo starting price undercut pre-event analyst consensus ($2,099–$2,500+),
a genuine new piece of information, and the market has already begun a
real, still-developing repricing (+3.27% through the latest completed
session, delayed by one session rather than an instant same-day pop). The
evidence needed to judge whether that repricing is proportionate to the
actual economic magnitude does not yet exist (preorders begin Oct 16,
2026) — held at `EVIDENCE_GAP`, not promoted on narrative alone.

SPXC's primary-evidence triage
(`pilot3/PILOT3_SPXC_PRIMARY_EVIDENCE_TRIAGE_001.md`) returned
`PROMOTE_TO_DEEP_UNDERWRITING`: Q2 2026 organic growth (16.9% company-wide)
accounted for roughly 74% of total reported growth (22.9%), HVAC segment
margin pressure had a specific, disclosed, plausibly temporary attribution
(capacity-expansion startup costs, tariffs) while Detection & Measurement
margin expanded 610bps, and FY2026 guidance was raised meaningfully across
revenue, EBITDA, and EPS. The market's own initial post-print selloff
fully reversed within a week, but the stock then gave back the entire
recovery over the following five to six weeks for reasons no evidence
gathered explains — named explicitly as the central open question for
deep underwriting.

SPXC's deep underwriting (`pilot3/PILOT3_SPXC_DEEP_UNDERWRITING_001.md`)
returned `BLOCKED_BY_MATERIAL_UNCERTAINTY`: real, multi-quarter-confirmed
quality was found (accelerating HVAC organic growth corroborated by a
$919M/+59% backlog, a well-quantified data-center demand driver, a
durable three-quarter D&M margin-expansion trend offsetting HVAC pressure
at the consolidated level, an immediately accretive high-margin
acquisition, and 1.4x pro forma leverage below management's own target
floor), but HVAC segment margin worsened for a second consecutive quarter
rather than troughing, and the triage-stage unexplained price decline was
not resolved. Both open questions have a specific, dated resolution point
(Q3 2026 earnings, ~late October).

PCG's primary-evidence triage
(`pilot3/PILOT3_PCG_PRIMARY_EVIDENCE_TRIAGE_001.md`) returned
`NO_DEMONSTRATED_EDGE`: real earnings growth and a reduced near-term
financing need were confirmed, but the strategic review discloses no
value-creating optionality on evidence gathered (only a capital-plan
deferral and a withdrawn multi-year outlook), and the wildfire-liability
framework was shown by primary evidence to be a live, structurally
unresolved risk — a cross-utility contagion charge (driven by a
competitor's loss) already hit Q1 2026 results, and California's SB 492
left the core strict-liability-plus-subrogation framework intact. The
market's post-announcement rebound partially reversed rather than
continuing to recover, and the ~8x forward P/E is consistent with a
durable, not temporary, discount.

SOLS's post-merger primary-evidence triage
(`pilot3/PILOT3_SOLS_POST_MERGER_PRIMARY_EVIDENCE_TRIAGE_001.md`) returned
`PROMOTE_TO_DEEP_UNDERWRITING`: broad-based double-digit organic growth
across every segment (Nuclear +27%, Healthcare Packaging +24%, Electronic
Materials +15%, Refrigerants +13%), a real and monetizing HFO/IP position
(a European patent upheld against multiple challengers; an active
licensing relationship), low leverage (1.3x), and a durable (not
reversed) positive market reaction to the August 27 merger termination
corroborate the candidate variant. A 218bps EBITDA-margin decline despite
11% revenue growth, and an unexplained ~28% gap to the
pre-merger-announcement price level, were named as the central open
questions for deep underwriting.

A follow-on work order first required a mandatory integrity check on the
committed SOLS triage record (a claim that it attributed HSR merger
filing fees to PG&E); primary-source re-verification confirmed the
record never made that attribution and its actual language was accurate
(`Parent` = Solstice itself), so no correction to the promotion thesis
was required and deep underwriting proceeded
(`pilot3/PILOT3_SOLS_DEEP_UNDERWRITING_001.md`), closing
**`BLOCKED_BY_MATERIAL_UNCERTAINTY`**. Verified against primary sources
rather than the earnings release's own non-GAAP framing, the real EBITDA
margin decline was roughly double the headlined figure (417–508bps vs.
218bps) and traced precisely to the Refrigerants & Applied Solutions
segment, where margin compression **worsened, not improved**, from
−527bps (Q1 2026) to −648bps (Q2 2026) — the same segment carrying the
growth and HFO/IP narrative. A new, material spin-off-related
interest-expense burden and a higher GAAP-basis capex growth rate (+54%
vs. the company's own +35% non-GAAP figure) were also identified. Growth,
backlog, and the IP position remained real and uncontradicted, so the
record did not close `NO_DEMONSTRATED_EDGE`, but the load-bearing margin
question resolved less favorably under scrutiny, so it was not advanced
either.

A Red Team review of Pilot 3's discovery-to-triage process
(`pilot3/PILOT3_BATCH_003_CHARTER.md`) returned
**`CONTINUE_WITH_NARROW_FIX`**: discovery is producing plausible,
falsifiable ideas and underwriting is successfully rejecting false
positives (zero Stage 7 survivors across twelve candidates is not itself
treated as a failure), but discovery over-samples post-event/familiar-
theme setups, and some candidates receive substantial work before the
original hook is cheaply disproven. Two, and only two, narrow process
fixes were adopted, **prospective only, beginning with Batch 003** — no
prior record is rewritten: **`PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`**
(when a hook depends on acceleration, margin change, bookings/RPO,
mix, or FCF improvement, triage must reconstruct that metric across the
last 4 reporting periods, sequential and YoY, before the full variant is
written — and must stop or block if the hook has already peaked, reversed,
or flattened, absent an independent source of edge) and
**`PILOT3_PRICED_IN_ONE_LINER`** (before advancing to deep underwriting,
triage must state "for this to be mispriced, the market must currently be
assuming ______" — if it cannot be stated credibly, no clear variant has
been demonstrated). Batch 003 is chartered to test a different discovery
pond (capital-allocation/balance-sheet change, neglected/lower-attention
securities, competitor/industry read-through, quiet regulatory/structural
change — not post-earnings selloffs, mega-cap themes, or generic AI
exposure), targeting 4–6 candidates.

**Batch 003 registration** (`pilot3/PILOT3_BATCH_003_REGISTRATION.md`),
source `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` (as-of 2026-09-12): five
candidates registered — NHP, UCB, NNBR, SAIA, and TCS (TSX) — with
canonical identity verified for each, including two real ticker
collisions resolved explicitly (UCB vs. Belgian pharmaceutical UCB SA;
TCS vs. Tata Consultancy Services and a German-venue Axon Enterprise
listing, resolved to Tecsys Inc., TSX, without researching the company
further, per instruction). Only NHP received primary-evidence triage.
Scout's characterization of NHP as the "best research-use-of-time
candidate" was explicitly disregarded as a ranking input.

**NHP's primary-evidence triage** (`pilot3/PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`),
the first record governed by the two new narrow fixes, returned
`NO_DEMONSTRATED_EDGE`: the discovery hook (an outpatient-medical
portfolio sale paying down debt beyond the sold properties' own
collateral, plus a full preferred-stock redemption, improving the
capital stack for common shareholders) was tested via the mandatory
4-period hook reconstruction and found directly contradicted, not merely
unresolved — a ~156%-dilutive common equity raise ($531.3M gross, closed
April 23, 2026), not the asset sale or preferred redemption, was the
primary-sourced driver of the year's leverage improvement (9.6x→4.9x net
leverage), and Normalized FFO per diluted share fell 18.2% year-over-year
in the same quarter. The market's own reaction to the September 10
first-tranche closing was negative, not positive. Treated as a
successful discovery-system outcome — the narrow fixes killed a
plausible-sounding hook cheaply, before a full variant was written.

**UCB's primary-evidence triage**
(`pilot3/PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_001.md`), the second record
governed by the two narrow fixes, returned `NO_DEMONSTRATED_EDGE`: the
discovery hook (Navitas exit + HTM-to-AFS securities repositioning +
debt paydown + expanded buyback collectively improving earnings quality
and risk profile more than the market credits) was tested against
management's own EPS walkforward, which showed the Navitas-exit
(−$0.07/quarter) and securities-reset reinvestment (+$0.06/quarter)
pieces net to roughly zero — the touted overall EPS improvement came
instead from an unrelated small acquisition (Peach State, +$0.02) and
unguided future "core bank growth" (+$0.02–0.04), neither named in the
hook. The credit-risk-reduction half of the hook (Navitas responsible
for ~50% of total net charge-offs) was well corroborated, but the
market's reaction to the September 8 announcement was flat-to-mildly-
negative, and post-restructuring valuation (~1.5–1.65x tangible book,
~11–12x P/E, ~13% ROTCE) was unremarkable for a well-capitalized
regional bank. Treated as a second successful discovery-system outcome
for the new narrow-fix discipline.

**NNBR's primary-evidence triage**
(`pilot3/PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_001.md`), the third record
governed by the two narrow fixes, returned
**`PROMOTE_TO_DEEP_UNDERWRITING`** — the first Batch 003 candidate to
survive triage. Unlike NHP and UCB, the mandatory hook reconstruction did
not kill the operating thesis: revenue growth accelerated for three
consecutive quarters (−8.5%→−1.7%→+12.1%→+19.3% YoY), EBITDA margin
expanded to 13.9% in the most recent quarter, new-business-wins guidance
was raised at every update for a year (to a $90–110M FY2026 midpoint of
$100M), Data Center & Electric Grid revenue (~$80M TTM) was confirmed as
fact, and the auto/non-auto sales-mix shift (65%/35% in 2023 to 40%/60%
by Q2 2026) is real and substantially already executed. A capital-
structure reconciliation was named **thesis-blocking**: whether the
"9,850 shares of Series D exchanged" figure represented the bulk of the
preferred cleanup or left most of it intact.

**Resolved by addendum to the same record**
(`pilot3/PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_001.md`): the actual Series
D Exchange Agreement (a 10-Q exhibit, not press-release shorthand) shows
a separate, previously unlocated 36,750-share **cash** redemption
occurred concurrently with the 9,850-share stock exchange — together
retiring **71.7%** of the 65,000-share pre-transaction Series D balance
(reconciling cleanly to the earnings release's "~$89 million paid off"
figure), not the ~15% the worst-case reading implied. The remaining
18,400 shares (~28.3%, ~$34.6M) carry a temporarily reduced 10.0% rate
through August 2027 and a confirmed $5.0 million discount if fully
redeemed by December 31, 2026. Common dilution from the private
placement and exchange combined is confirmed at ~57.1%; the exchange
ratio itself retired preferred at roughly fair-to-premium value, not a
discount. Uncertainty classification updated to
**`RESOLVED_SUPPORTS_THESIS`**; progression decision
**`PROCEED_TO_DEEP_UNDERWRITING`** — deep underwriting itself had not
begun as of that record.

**NNBR deep underwriting**
(`pilot3/PILOT3_NNBR_DEEP_UNDERWRITING_001.md`) closed
**`BLOCKED_BY_MATERIAL_UNCERTAINTY`**. The operating transition proved
broader and more economically significant than triage established:
three separately-guided growth programs (Data Center & Electric Grid
~$80M TTM/goal $120M, Defense & Electronics ~$60M TTM/goal $90M, Medical
Products ~$15M TTM/goal $40M) totaling ~30% of revenue, not the
~15-16% data-center-only estimate triage had; a ~5x segment operating-
margin gap (Power Solutions 15.1% vs. Mobile Solutions 3.0%, FY2025)
quantifying the mix shift as economically transformative, not merely
descriptive; and a favorable, evidence-based reconciliation of the
preferred-cleanup trade (a coarse estimate that the retired 71.7% of
Series D, left compounding, could plausibly have grown past $150M within
3-4 years). The disposition is blocked on one specific, named,
evidence-gatherable gap: capex has not, in any of the eight quarters
reconstructed, approached the guided $35-40M annual run-rate needed to
build capacity for the win pipeline, and free cash flow (this record's
own calculation) was positive in exactly one of the last nine quarters
reconstructed. Growth and a favorable capital-structure resolution were
both found real but were explicitly not treated as sufficient on their
own, per instruction.

**SAIA primary-evidence triage**
(`pilot3/PILOT3_SAIA_PRIMARY_EVIDENCE_TRIAGE_001.md`) closed
**`NO_DEMONSTRATED_EDGE`** — the first Batch 003 candidate governed by a
**read-through** discovery type (Old Dominion Freight Line's August LTL
pricing data as a signal for Saia's Q3 setup), and the pilot's core test
of whether competitor read-throughs validly transfer economic
information. The read-through failed the mandatory cheapest-
falsification test on four grounds: Saia's own Q3 operating-ratio
guidance (100bps sequential degradation, already better than the
150-200bps historical norm) was public more than a month before the
hook; Saia discloses its own monthly shipment/tonnage data via SEC
filing, filed the same calendar day as ODFL's release; ODFL's cited
ex-fuel pricing metric sat inside a stable, year-long range rather than
representing new information; and the cost items most likely to drive
Saia's actual Q3 outcome (new-terminal drag, stacked wage increases,
purchased-transportation costs up 47.3% YoY) are Saia-specific and
unrelated to ODFL's pricing environment. Direct market-reaction evidence
confirmed this: Saia rose on the day both companies released their own
data while ODFL did not, indicating the market's reaction traced to
Saia's own disclosures, not the read-through. Classified
`READ_THROUGH_PARTIAL` — a genuine but non-transferable industry
pricing-discipline signal — as a Pilot 3 learning observation.

**TCS primary-evidence triage**
(`pilot3/PILOT3_TCS_PRIMARY_EVIDENCE_TRIAGE_001.md`) closed
**`NO_DEMONSTRATED_EDGE`** — the fifth and final Batch 003 candidate,
completing the batch. Every headline fact in Scout's `NEGLECTED /
INSTALLED_BASE_EXPANSION` hook (revenue, SaaS revenue/growth, Elite SaaS
growth, ARR, RPO, Adjusted EBITDA, raised FY2027 guidance, NCIB,
dividend) verified precisely against primary sources — a notably
different starting point than NHP, UCB, or SAIA — and the aggregate
installed-base-expansion mechanism strengthened under the mandatory hook
reconstruction: Elite SaaS ARR net retention reached 111% (LTM),
climbing from ~102% several quarters earlier, and Elite ARR growth
itself accelerated to 24% YoY beneath a merely-stable blended total-SaaS
figure (masked by shrinking non-Elite attrition). Promotion failed on a
different dimension than a broken hook: Scout's specifically named
customer expansions (Prisma Health, UT Southwestern, a cancer center)
could not be corroborated in any primary Tecsys disclosure reviewed;
FY2027 guidance was raised the same day (September 10, 2026) as the
hook's underlying Q1 results, meaning the evidence is already reflected
in management's own forward guidance; and the market's own reaction
(~+11% over the following days, concentrated in one high-volume session)
indicated the story had already begun to be priced by the evidence date.
Gate B could not be attempted for this security at all — `XTSE` is not a
MIC supported by the live session calendar, and the configured
TwelveData plan does not cover TSX-listed names — disclosed plainly as a
genuine data-availability limitation rather than worked around; a
coarse valuation was built instead from the company's own disclosed
market capitalization and uncertified secondary price data, labeled as
such throughout. Classified `NEGLECT_PARTIAL` (six sell-side analysts
cover the name, but trading liquidity is genuinely thin) as a Pilot 3
learning observation.

**Pilot 3 formal closeout**
(`pilot3/PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md`) recorded, following
two Red Team reviews. **Verdict: `CLOSE_PILOT3_ADVANCE_TO_PILOT5`. No
further Pilot 3 batch will be created.** Pilot 3 proved: broader
discovery mechanisms beyond headline/event setups; improved Scout
opportunity quality without source privilege; Hook Reconstruction can
cheaply falsify weak hooks (NHP, UCB, SAIA) without mechanically
rejecting all candidates (NNBR, TCS both strengthened under
reconstruction); the Priced-In One-Liner improves expectations-gap
discipline; Atlas can distinguish company improvement from common-share
value creation and productive from thesis-blocking uncertainty (both
demonstrated within the single NNBR record); competitor read-through
requires a valid economic transmission mechanism (SAIA); real business
mechanisms may already be reflected in price (TCS); research intensity
can be allocated selectively; and Atlas repeatedly added
decision-relevant information beyond the original discovery hook.
**Recorded explicitly, not softened**: no Pilot 3 candidate reached
Stage 7; discovery has not yet demonstrated repeatable investable alpha
or repeatable discovery before market recognition; false-negative
calibration remains unproven; opportunity half-life remains poorly
understood; Atlas has not yet demonstrated the originally surfaced
security is consistently the best expression of a valid thesis. All
Pilot 3 company records remain frozen exactly as committed: PATH, MDB,
XOM, PCG, NHP, UCB, SAIA, and TCS closed at `NO_DEMONSTRATED_EDGE`;
DOCU, SPXC, SOLS, and NNBR closed at `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AAPL `EVIDENCE_GAP`; JPM `CALENDAR_HOLD`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; SMH `REFERENCE_PEER_TAPE`; NVDA
`REFERENCE_ONLY`. No Batch 003 or prior candidate is authorized to
advance further without an explicit new work order. **Current active
next action: none — Pilot 3 is closed; Pilot 5 (below) is chartered but
no Pilot 5 candidate has been created.**

---

## Pilot 5 — FORCED_FLOW / OWNERSHIP_DISLOCATION

> ### Status: **ACTIVE — DISCOVERY SCAN 001 FULLY TRIAGED AND RED-TEAM
> CHECKPOINTED. VYLR FUNDAMENTALLY UNDERWRITTEN
> (`READY_FOR_WI_PRICE_TEST`, pre-WI trading); CRASUS
> (`NO_DEMONSTRATED_FORCED_FLOW_EDGE`); MSGR
> (`NO_DEMONSTRATED_FORCED_FLOW_EDGE`). Scan 002:
> `WAIT_FOR_VYLOR_REGULAR_WAY_PRICE_TEST` (updated 2026-09-24 event;
> supersedes the earlier `WAIT_FOR_VYLOR_WI_PRICE_TEST` — WI market
> canceled, see Trading-Trigger Update below). Update 2026-10-01: Vylor regular-way price test
> complete — `NO_DEMONSTRATED_INVESTABLE_DISLOCATION`; trigger satisfied;
> Scan 002 not started (needs explicit work order).**
> **Update 2026-10-01 (later): Discovery Scan 002 registered (CTVA, CBRS);
> CTVA triaged `PROMOTE_TO_FUNDAMENTAL_UNDERWRITING`; CBRS surfaced only.
> Update 2026-10-01 (evening): CTVA underwritten pre-event —
> `READY_FOR_POST_INDEX_EVENT_PRICE_TEST`.**

**Discovery Scan 001** (`pilot5/PILOT5_DISCOVERY_SCAN_001_REGISTRATION.md`),
source `GROK_SCOUT_FORCED_FLOW_DISCOVERY`: three situations registered
without ranking (Scout's own "best research-use-of-time" claim for VYLR
explicitly disregarded, per Discovery Source Neutrality) — VYLR
(Corteva → Vylor spin-off shareholder/index mismatch), 646A/Crasus
(Resonac → Crasus cross-border mismatch), MSGR (MSG Sports → Rangers
shareholder-preference mismatch). **All three situations have now
received forced-flow triage — Discovery Scan 001 is fully closed.**

**VYLR forced-flow triage**
(`pilot5/PILOT5_VYLR_FORCED_FLOW_TRIAGE_001.md`) closed
**`PROMOTE_TO_FUNDAMENTAL_UNDERWRITING`** — Pilot 5's first candidate.
Confirmed Corteva (CTVA) is an S&P 500 constituent; located and quoted
Vylor's own primary-sourced (Form 10-12B/A) risk-factor language that
index funds "may be required to sell Vylor common stock" if not
included in tracked indices at spin-off; confirmed the corporate-action
mechanics (WI trading beginning the session before the record date,
regular-way beginning on the distribution date) directly from the
primary information statement, with the specific dates themselves
(record date ~Sept 24, 2026; distribution ~Oct 1, 2026; 1:1 ratio;
ticker VYLR) flagged as secondary-sourced and not yet SEC-confirmed as
of the evidence date. The mandatory cheapest-falsification test found
none of its four kill conditions satisfied (no index-inclusion
announcement exists in either direction; institutional ownership is
high; the mandate-mismatch mechanism is structural, not speculative;
supply-vs-liquidity could not be shown trivial because VYLR liquidity
does not yet exist). The fundamental-separation check was clean:
Corteva's most recent guidance was raised, not cut, with the Seed
segment's H1 2026 operating EBITDA up 11% YoY. A precise, primary-
sourced quantification of the constrained-versus-discretionary holder
split could not be achieved with free/public tooling — disclosed as a
genuine evidence gap, not filled by inference — and, together with the
still-unannounced index-inclusion decision, is named as the specific
focus for the next stage of work, mirroring how NNBR's Series D
uncertainty was named and carried forward in Pilot 3 rather than
treated as an automatic block.

**VYLR pre-WI fundamental underwriting**
(`pilot5/PILOT5_VYLR_PRE_WI_FUNDAMENTAL_UNDERWRITING_001.md`) closed
**`READY_FOR_WI_PRICE_TEST`** — not a buy signal, not Stage 7; it means
Vylor's fundamentals are attractive/understandable enough to compare
actual WI/regular-way pricing against a prepared valuation framework
once trading begins. The prior triage's 65-135M-share constrained-
supply estimate was explicitly re-labeled `EXPLORATORY_CONTEXT_ONLY`,
not a decision fact. Built a full pro forma capital structure from the
primary Form 10-12B/A (downloaded and locally text-extracted at 22.1MB):
≈$5.48 billion of new debt, of which ≈$3.56 billion funds a cash
distribution to New Corteva (a debt-funded recapitalization, not
organic growth capital) versus only ≈$2.44 billion of genuinely
structural long-term debt; confirmed no retained Corteva ownership
stake and a small (~$82M) retained pension obligation. Reconstructed
5-period Seed-segment economics (FY2023-FY2025, H1 2025, H1 2026)
showing price-led revenue growth (+3% price in both FY2024 and FY2025),
expanding gross margin (47.4%→53.8%) and EBITDA margin (22.4%→26.6%),
and rising R&D intensity (8.8%→9.9% of revenue) — margin expansion
achieved without cutting R&D. Found Seed grew through a 2023-2024
period when total Corteva revenue declined, suggesting relative
cyclical resilience. Identified the Pioneer® brand's stated #1 U.S.
corn/soybean position and confirmed Pioneer Hi-Bred International as
Vylor's key subsidiary. Named the single largest unresolved variable
(standalone dis-synergy/stranded costs, acknowledged by the issuer but
not yet quantified) as the cheapest fact that could most change the
picture. Classified fundamental quality `SOLID_CYCLICAL_BUSINESS` and
built a labeled, non-target valuation sensitivity map (downside/base/
strong-execution scenarios) plus a required-return attractiveness
threshold, explicitly distinguishing this from a price target or Stage
7 decision.

**Crasus (646A) forced-flow triage**
(`pilot5/PILOT5_CRASUS_646A_FORCED_FLOW_TRIAGE_001.md`) closed
**`NO_DEMONSTRATED_FORCED_FLOW_EDGE`**. Confirmed the full spin-off
mechanics from Resonac's own primary IR documents (>80% of Crasus
Chemical Inc. distributed to Resonac Holdings shareholders at a 1:1
ratio, Resonac retaining <20%, listing Sept 29 and distribution Oct 1,
2026, a direct listing raising no new capital). Found the transaction
is a **tax-qualified partial spin-off under Japanese law** — Japanese
shareholders face no deemed-dividend taxation, refuting the
domestic-tax-driven forced-selling narrative for the majority of the
holder base. Identified the Nikkei 225's own July 2025 methodology
revision (temporary index inclusion from the ex-rights date, mechanical
removal the business day after listing — Crasus specifically confirmed
by Nikkei Inc.'s own reporting to be included on its Sept 29 listing
date and removed Sept 30) as the most concrete confirmed forced-seller
mechanism, though its magnitude could not be quantified pre-listing and
TOPIX treatment remained an unresolved evidence gap. The
fundamental-separation check — more consequential here than at Vylor,
as anticipated by the sourcing design's own caution about basic-
petrochemical cyclicality — found a genuine, current, issuer-
acknowledged headwind: Crasus's own May 2026 release disclosed
operating profit fell 51% YoY (¥8.6B→¥4.2B, 2024→2025), ROE/ROIC each
roughly halved, and 2026 guidance was explicitly placed "under review"
due to a Middle East-linked naphtha-supply disruption, against a
backdrop of Japan's ethylene industry hitting record-low utilization
(68.6%/67.3%) in early 2026. This independently explains potential
post-listing weakness without requiring any ownership-dislocation
story, and two of the cheapest-falsification test's five kill
conditions were affirmatively satisfied by primary evidence. The
required Pilot 5 comparative-learning exercise found Vylor cleaner on
every axis (more identifiable constrained seller, cleaner fundamental
separation, earlier discovery relative to price discovery) — a useful,
honest contrast rather than a forced symmetry between the two
candidates.

**MSG Rangers (MSGR) forced-flow triage**
(`pilot5/PILOT5_MSGR_FORCED_FLOW_TRIAGE_001.md`) closed
**`NO_DEMONSTRATED_FORCED_FLOW_EDGE`**. Confirmed the current
transaction status directly from MSGS Spinco, Inc.'s (CIK `0002132873`)
primary Form 10-12B/A, Amendment No. 1 (Sept 3, 2026): 1-for-2
distribution ratio and MSGR/MSGK tickers matched Scout exactly, while
board approval, league approval, a final tax opinion, and Form 10
effectiveness all remain unsatisfied conditions with record/
distribution dates still genuinely blank. The issuer's own
selling-pressure risk-factor language — quoted verbatim from the
primary filing — was found to be explicitly preference-framed ("not
interested in holding"), not compulsion-framed, distinguishing it from
Vylor's compulsion-framed index-fund language. Atlas identified a real,
previously-unstated mechanism beyond Scout's own framing: MSGR would
likely fail the S&P SmallCap 600's positive-earnings screen for
independent index addition, given its own disclosed net losses in both
FY2025 and FY2026 — a materially weaker dynamic than Vylor's or
Crasus's index-removal mechanisms, since it describes a stub never
being added rather than a holding being forced out. The
fundamental-separation check found a genuine confound of its own kind:
two consecutive years of operating and net losses, profitability
explicitly conditioned by the issuer on "an extended playoff run," and
an already-realized 18% cut to Rangers local media revenue traced to
related-party MSG Networks' 2025 debt restructuring. The
franchise-value-vs-public-equity test found the widely-reported
Knicks/Rangers sum-of-the-parts valuation gap (~29% discount) real but
not established to accrue cleanly to minority MSGR holders, given the
Dolan Family Group's permanent Class B voting control and the absence
of any sale catalyst. The three-way Pilot 5 comparison found each
non-promoted situation failed for a different reason — Crasus on
fundamentals, MSGR on mechanism purity and prior thesis recognition —
a useful, non-redundant finding preserved without softening.

**Discovery Scan 001 is now fully triaged — all three surfaced
situations carry a recorded Atlas disposition.**

**Sourcing design**: `pilot5/PILOT5_FORCED_FLOW_SOURCING_DESIGN.md`
defines where and how to look (three search lenses — shareholder
mismatch/distributed securities, mechanical benchmark/mandate flow,
holder-specific forced selling — quality before category diversity;
primary public source classes; 14 initial opportunity questions across
constraint/size/timing/economics/recognition/expression/falsification;
a judgment-based, non-scored flow-magnitude comparison; the Scout search
posture; and the human/manual sourcing role). **No candidates were
created; no Batch 001 was started; no architecture was added.**

**Numbering note:** this is Pilot 5, not Pilot 4 — `docs/pilot4/`
already holds a separate, complete, frozen, unrelated pilot (September
2, 2026, COST/PH/AMGN incumbent-substitution test). See the numbering
note in the Pilot 3 status block above.

Full charter in `pilot3/PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md`
§10-§19. Under the standing One-New-Information-Family-Per-Pilot
Guardrail, Pilot 5 tests one new, experimental discovery family:
**`FORCED_FLOW / OWNERSHIP_DISLOCATION`** (index inclusion/exclusion,
spin-off selling, mandate-driven selling, forced deleveraging, holder
transition, fund/redemption pressure, lockup effects, tax-related
selling, other non-fundamental ownership or flow pressure — no
permanent taxonomy established).

**Primary learning objective:** Can forced-flow / ownership dislocation
uncover a security whose price is temporarily disconnected from
underlying economics, early enough that Atlas can validate the
opportunity and reach Stage 7 capital comparison without lowering
evidence or variant standards?

**Carried forward from Pilot 3, unchanged:** Hook Reconstruction at
Triage and the Priced-In One-Liner (no expansion, no new generic triage
gate). **Carried forward as research questions only, no new
architecture:** the quiet-change question (what economically important
change is occurring before it becomes the headline?); the original-
source-vs-echo question (existing provenance discipline remains
sufficient — no new provenance system); the best-expression question
(is the surfaced security the best way to capture the thesis, versus
another company, supplier/customer/competitor, sector/factor beta, SPY,
commodities, Treasury/Cash, or Do Nothing? — no optimizer); the
recognition/half-life question (before/during/after recognition — a
temporary Pilot 5 learning observation, not a permanent canonical
field). Sentiment remains `SHADOW_ONLY` — no formal sentiment
implementation. Beta (including SPY) remains a live, legitimate capital
alternative — no separate beta engine. Infrastructure restraint carried
forward explicitly: no XTSE support, second market-data vendor,
sentiment provider, valuation engine, ownership-data infrastructure, or
ML/statistical tooling unless an actual decision problem earns it.

**Discovery Scan 001 Red Team checkpoint** (record only, September 15,
2026 — full detail in
`pilot5/PILOT5_DISCOVERY_SCAN_001_REGISTRATION.md`'s "Red Team
Checkpoint" section): reviewed all three closed dispositions without
reopening any of them.

- **Vylor** — preserved `READY_FOR_WI_PRICE_TEST`. Conclusion: Vylor
  remains the clean live Pilot 5 test fixture, but the forced-flow
  mechanism should **not** yet be described as demonstrated — the
  issuer's index-selling language plus CTVA's confirmed S&P 500
  membership establish a plausible structural constraint, not a
  measured forced book. Exact constrained supply remains unknown.
  Vylor was discovered early relative to trading, but not necessarily
  early relative to specialist recognition. WI trading is the next
  falsification point.
- **Crasus** — preserved `NO_DEMONSTRATED_FORCED_FLOW_EDGE`. Learning:
  the tax-selling thesis was materially weakened by confirmed Japan
  tax treatment; fundamental deterioration independently explains
  potential weakness; dirty fundamental cases are poor forced-flow
  tests unless a dated mechanical constraint is unusually strong.
- **MSG Rangers** — preserved `NO_DEMONSTRATED_FORCED_FLOW_EDGE`.
  Learning: issuer-described selling pressure was primarily preference,
  not compulsion; preference mismatch should not be treated as forced
  flow; natural specialist buyers and an already-known sum-of-the-parts
  framing weaken the dislocation thesis.

**Scan 001 learning**: the scan clarified the **rejection rules** of
forced-flow discovery more than it demonstrated a profitable
dislocation. Carried forward as **research questions only, no
permanent fields or scoring**: who must transact under a rule they do
not control? By when? Can the likely supply be bounded? Who is able
and motivated to absorb it? Are the fundamentals quiet enough that the
tape could plausibly reflect ownership pressure rather than operating
deterioration?

**Flow quantification**: exact forced-share counts are not required
for initial triage, but a meaningful bound on potential supply relative
to liquidity becomes necessary before Atlas can claim a forced-flow
edge or progress toward capital comparison. **No flow score is
created.**

**Timing**: early relative to first trading is not the same as early
relative to specialist recognition. **No timing engine or permanent
field.**

**Scan 002: `WAIT_FOR_VYLOR_WI_PRICE_TEST`.** Scan 002 does not begin
before the Vylor WI test unless a material event invalidates the
current experiment. Current Red Team hypothesis for when Scan 002
eventually begins: preferentially test genuinely different mechanisms
— index deletion/reconstitution; fund liquidation or concentrated-
holder forced exit; lockup/post-reorganization holder mismatch. **These
remain future search directions only — no candidates created now.**

**Scout feedback: `SCOUT_UPDATE_EARNED`.** Three Pilot 5 lessons earned
a Scout instruction refinement: (1) distinguish must-sell-in-a-defined-
window from may-want-to-sell; (2) do not infer tax-driven selling
without confirming the actual tax treatment; (3) flag material
fundamental deterioration at the discovery hook rather than framing it
as a forced-flow opportunity. **The broader Scout operating
instructions are not rewritten.**

No architecture change. No candidates created. Scan 002 not started.
Vylor, Crasus, and MSGR company records unmodified by this checkpoint.

---

### Pilot 5 — Vylor Trading-Trigger Update (September 24, 2026; append-only)

**Superseding corporate-action event (September 24, 2026).** Primary/issuer
evidence indicates: Vylor's Form 10 registration became effective; the
previously expected VYLR when-issued (WI) trading period will not occur;
there will be no Corteva ex-distribution market before the separation;
Vylor regular-way NYSE trading under `VYLR` is expected to begin
**October 1, 2026**; and the Vylor distribution is also expected on
October 1, 2026. This supersedes the earlier expected September 25–30
WI-trading schedule. **The earlier WI schedule is preserved above and in
the frozen Vylor records as the historical audit trail; it is not
rewritten.**

**Vylor.** Historical frozen underwriting disposition remains
`READY_FOR_WI_PRICE_TEST` (unmodified). **Current active next trigger:
`WAIT_FOR_VYLOR_REGULAR_WAY_PRICE_TEST`.** No capital decision has
occurred. No Stage 7 has begun.

**Pilot 5 implication.** The cancellation of the when-issued market
removes the planned pre-distribution price-discovery test. The first
observable ownership-transfer / price-dislocation test will occur in
regular-way VYLR trading beginning on or after October 1, 2026. The
absence of WI trading may make the October 1 ownership-transfer test
cleaner, because inherited holders cannot reposition through a prior WI
market. This does **not** increase or decrease the probability or
magnitude of forced selling; it changes only the observable test window.

**Discovery-clock implication.** Atlas identified and fundamentally
underwrote Vylor before trading began, and there will now be no WI
observation period. Specialist investors have nevertheless had months
of public spin information. "Before regular-way trading" must therefore
not be confused with "before specialist recognition," and the absence of
WI trading is **not** evidence of edge.

**Scan 002: `WAIT_FOR_VYLOR_REGULAR_WAY_PRICE_TEST`** (supersedes
`WAIT_FOR_VYLOR_WI_PRICE_TEST`). Scan 002 does not begin before the
Vylor regular-way price test unless a material invalidating event
occurs. The future-search directions above are unchanged and remain
search directions only.

**Unchanged dispositions:** Crasus `NO_DEMONSTRATED_FORCED_FLOW_EDGE`;
MSG Rangers `NO_DEMONSTRATED_FORCED_FLOW_EDGE`.

**Not done by this update:** no Vylor valuation work, no price test, no
Scan 002, no new securities researched, no candidates created, no
architecture change, no Scout scan. Vylor triage/underwriting, Crasus,
and MSGR records, Pilot 4 records, the frozen control layer, and the
facade are unmodified.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — Vylor October 1 Regular-Way Price Test (2026-10-01; append-only)

**Result:** `NO_DEMONSTRATED_INVESTABLE_DISLOCATION` (record:
`pilot5/PILOT5_VYLR_REGULAR_WAY_PRICE_TEST_001.md`). The Vylor regular-way
price test is complete; the trigger `WAIT_FOR_VYLOR_REGULAR_WAY_PRICE_TEST`
is satisfied.

- **Event confirmed:** distribution completed Oct 1, 2026 (1:1); NYSE `VYLR`.
  Shares outstanding ≈667M (derived, not primary-confirmed). Debt-exchange
  offers expired Sept 30 with ≈$1.44B tendered; final settlement and
  post-close capitalization not located.
- **Price evidence is UNCERTIFIED.** `TWELVEDATA_API_KEY` (and Alpaca/Tiingo)
  absent; Gate B binding is BLOCKED for VYLR. Public aggregators agree:
  open 66.00, low 65.00, high ≈75, close 68.26, volume ≈15.0M.
- **Against the frozen map:** market cap ≈$45.5B; EV ≈$46.9B (≈17.8x
  FY2025 EBITDA on the frozen structural net-debt convention). Close was
  ≈5% above the top of the strong-execution band ($57–65) and ≈2.4–2.7x the
  downside band ($25–28). The §17 entry threshold was never approached
  (session low $65.00). Scenario B (valuation remains rich).
- **Forced-flow:** not demonstrated. Vylor was added to the S&P 500 on Oct 1
  replacing Corteva, so the index mechanism the triage left unresolved
  resolved against the thesis. Volume ≈2.2% of shares outstanding. The
  65–135M estimate remains exploratory context only.
- **Untested:** sector/benchmark mismatch selling (GICS Materials → Consumer
  Staples effective Oct 6; other indexes), standalone costs, dilution.
- **Observation, not a candidate:** Corteva moves S&P 500 → S&P MidCap 400
  before the Oct 6 open. Not researched; no candidate created.
- **Scan 002** is not started; it requires an explicit new work order.
- Vylor triage/underwriting, Crasus, MSGR, Pilot 4, control layer, and
  facade records are unmodified. **No Stage 7. No capital decision.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — Discovery Scan 002 Registration + CTVA Triage (2026-10-01; append-only)

**Discovery Scan 002 registered** (`pilot5/PILOT5_DISCOVERY_SCAN_002_REGISTRATION.md`),
source `GROK_SCOUT_FORCED_FLOW_DISCOVERY`, without ranking: **CTVA** (index
migration) and **CBRS** (IPO lockup / float eligibility; **surfaced only —
not researched or triaged**). Scan 001 dispositions unchanged (VYLR
`NO_DEMONSTRATED_INVESTABLE_DISLOCATION`; Crasus and MSGR
`NO_DEMONSTRATED_FORCED_FLOW_EDGE`).

**CTVA triage** (`pilot5/PILOT5_CTVA_INDEX_FLOW_TRIAGE_001.md`):
**`PROMOTE_TO_FUNDAMENTAL_UNDERWRITING`** — mechanism only; no price evidence
of dislocation yet.

- **Mechanics (S&P DJI release, Oct 1, 2026):** CTVA is deleted from the S&P
  500 and added to the S&P MidCap 400 effective prior to the Oct 6 open
  (executed at the **Oct 5 close**); CTVA remains in the S&P 500 until then.
  Vylor was added to the S&P 500 on Oct 1.
- **Migration, not one-way selling:** S&P 500 passive funds sell, MidCap 400
  passive funds buy. Estimated net passive sale ≈53–93M shares (≈8–14% of
  ≈667M; ≈12–21 days of average volume). **An estimate from aggregate
  ratios, not a forced-share count**; the sign is better supported than the
  magnitude.
- **Ex-spin pricing:** CTVA's −83.8% on Oct 1 is mechanical. Against a
  residual reference ($77.65 − VYLR $68.26 = $9.39), CTVA's $12.57 close was
  ≈34% above, and one CTVA + one VYLR rose 4.1%. The earlier $12.75
  intraday figure was not used.
- **Fundamentals (Scout flags verified):** PFAS $455M (Sept 10; Corteva ≈25%);
  S&P A− → BBB+ (Sept 17); the "state AG lawsuit" is a Sept 28 FTC/states
  **settlement** ($35M, 10-year loyalty-program remedy, court approval
  pending); pricing pressure unquantified. All pre-date the spin; none
  independently explains an index-window decline.
- **Missing observations:** Oct 2 session; Oct 5 session and closing auction;
  Oct 6 open. Price evidence uncertified (Gate B blocked).
- No deep underwriting performed, no Stage 7, no capital decision. Frozen
  records unmodified.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — CTVA Pre-Event Fundamental Underwriting (2026-10-01; append-only)

**CTVA pre-event fundamental underwriting**
(`pilot5/PILOT5_CTVA_PRE_EVENT_FUNDAMENTAL_UNDERWRITING_001.md`):
**`READY_FOR_POST_INDEX_EVENT_PRICE_TEST`** — a framework fixed before the
Oct 5 close, not a finding of dislocation, not a buy recommendation, not
Stage 7.

- **Correction to the Scan 002 triage (append-only; triage record not
  rewritten):** "all items pre-date the spin" holds for the four Scout flags
  but not for the **Oct 1 Indiana-led state-court fraudulent-transfer suit**
  (Corteva, Vylor, EIDP; ~$39–40B asset-transfer allegation, "tens of
  billions" PFAS claim, unwinding/TRO relief; TRO hearing Oct 2). Allegations
  only; Corteva calls them speculative. The earlier California-led federal
  TRO was denied. Vylor is also a defendant.
- **$9.39 residual not used.** Valuation built from CTVA's own evidence:
  FY2025 Crop Protection segment EBITDA $1,350M (stand-alone ≈ $1.2B);
  primary pro forma balance sheet (cash $3,058M; debt $1,013M; pension
  $1,215M; 667.2M shares).
- **Frozen sensitivities (unweighted, ex-new-tail):** downside ≈ $10.4–12.0;
  base ≈ $15.9–18.7; strong ≈ $23.0–26.3 per share. The Oct 1 close of
  $12.57 (uncertified, known at writing — disclosed) sits just above the
  downside band.
- **Case-specific threshold for continued investigation:** certified price at
  or below ≈ $10.4 (≈17% below the Oct 1 close) with no unboundable-tail
  event; each $1B of incremental liability ≈ −$1.50/share; each −$100M EBITDA
  ≈ −$1.05 to −$1.61/share.
- **Flow bracket is fragile:** ≈25–95M shares depending on passive-share
  assumptions; not a forced-flow number.
- **Invalidation triggers, observable evidence, cheapest falsification and
  missing evidence recorded before the Oct 5 close.** Price data uncertified
  (Gate B blocked). CBRS surfaced only. No Stage 7, no capital decision.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — CTVA October 2 Legal Checkpoint (2026-10-01; append-only)

**CTVA October 2 legal checkpoint — status
`LEGAL_OUTCOME_PENDING_VERIFICATION`** (checked Thu Oct 1, 2026, ~7:30 PM EDT).

- **The hearing has not yet occurred.** Marion Superior Court 1 set the TRO
  hearing for 9 a.m. Fri Oct 2 (Indiana Lawyer, Oct 1). At the time of this
  checkpoint it is about 13½ hours away, so **no order, docket entry, or
  hearing outcome exists to verify.** The complaint and docket were not
  retrievable (no authoritative court record; Oregon and Maryland AG releases
  and Corteva's Oct 1 8-K and press release say nothing on a hearing result).
- **Not an outcome:** the Indiana action is a filed complaint plus a
  **requested** TRO/preliminary injunction (freeze assets; bar dividends and
  buybacks; bar Vylor from selling or pledging seed assets; unwind the
  separation). These are allegations and requests, not orders.
- **Conflation guard:** search summaries state that "the court denied a
  TRO." That refers to the **separate federal D.S.C. denial of California's
  motion on Sept 30**, which cleared the Oct 1 separation; it is **not** an
  Indiana ruling. It is not counted.
- **New issuer disclosure:** Corteva's Oct 1 8-K (Item 8.01, press release)
  contains only generic "legal proceedings may be instituted" risk language;
  no lawsuit, TRO, or PFAS statement. No other relevant filing located.
- **Comparison with the frozen invalidation conditions:** no adverse TRO or
  injunction, dividend/buyback restriction, or new quantified liability is
  **established** by any authoritative source, and none is **ruled out**.
  Silence is not treated as favorable. Index-transition mechanics
  (CTVA S&P 500 deletion and MidCap 400 addition effective before the Oct 6
  open, executed at the Oct 5 close) are unchanged by any located notice.
- **Preserved without modification:** underwriting commit `529286a`, its
  assumptions, sensitivity ranges, and the ≈$10.40 further-review threshold.
  No Oct 2 or Oct 5 market observation was made. **Next step:** re-run this
  checkpoint after the hearing, before the Oct 5 test.
- No Stage 7, no capital decision, no new discovery scan, no CBRS research.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — CTVA October 5 Legal Re-check (2026-10-05; append-only)

**CTVA October 5 legal re-check (interim, ~2:10 PM EDT Mon Oct 5) — status
`LEGAL_OUTCOME_PENDING_VERIFICATION`.** The Oct 5 index-flow observation was
**not** performed: the session had not closed when this was written, and the
price test was not run.

- **No authoritative record of the Oct 2 hearing outcome was found.** Checked:
  the filed complaint (primary), Indiana, Oregon, Maryland and Vermont AG
  releases, Corteva's and Vylor's Oct 1 8-Ks and Corteva's EDGAR 8-K list,
  and trade/legal press (Indiana Lawyer, IBJ, Agri-Pulse, Insurance Journal,
  Hoosier Ag Today [blocked]). Every source either predates the hearing or
  repeats that it was scheduled. No order, docket entry, continuance notice,
  or issuer disclosure about it surfaced. **Silence is not treated as a
  denial or as a favorable outcome.** Corteva's EDGAR list showed no 8-K after
  Oct 1.
- **Primary document obtained:** complaint filed **Oct 1, 2026, 10:48 AM**,
  Cause No. **49D01-2610-CE-054574**, Marion Superior Court 1, Indiana
  Commercial Court; plaintiffs Indiana, Guam and 14 states; defendants
  EIDP, Corteva, Vylor. **Prayer (requested relief only):** avoid the Vylor
  transfers to the extent needed to satisfy plaintiffs' claims; declare Vylor
  must satisfy claims against Old DuPont/Corteva; TRO/preliminary/permanent
  injunctions barring Old DuPont and Corteva from disposing of proceeds "for
  less than reasonably equivalent value," **including distributions to
  shareholders**, and barring Vylor from distributing, transferring,
  capitalizing or disposing of transferred property; constructive trust.
  These are **requests and allegations, not orders.** The complaint values
  the retained crop-protection business at ≈$14B and alleges PFAS liabilities
  "well into the tens of billions"; it states the $4B Chemours/DuPont/Corteva
  PFAS cost-sharing is "nearing exhaustion" and that Corteva bears 29% of
  the $2B contributed by it and New DuPont. Plaintiffs' figures, not Atlas
  facts.
- **Conflation guard:** press repeating "court denied TRO" refers to the
  federal D.S.C. denial (Sept 29–30), not the Indiana hearing.
- **Frozen invalidation conditions:** no adverse order is established, and
  none is ruled out, so the price test is **not** shown to remain eligible
  and **not** shown to be blocked. Underwriting `529286a`, ranges, and the
  ≈$10.40 threshold are unchanged. Index mechanics unchanged (CTVA S&P 500
  deletion and MidCap 400 addition effective before the Oct 6 open, executed
  at the Oct 5 close).
- **Next:** after the Oct 5 close, re-check for an Indiana order, then run
  the index-flow observation. No Stage 7, no capital decision, CBRS
  untouched.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — CTVA October 5 Index-Event Price Test (2026-10-05; append-only)

**CTVA October 5 index-event price test**
(`pilot5/PILOT5_CTVA_OCT5_INDEX_EVENT_PRICE_TEST_001.md`):
**`NO_DEMONSTRATED_INVESTABLE_DISLOCATION`.**

- **Legal:** `LEGAL_OUTCOME_PENDING_VERIFICATION`. No authoritative record of
  the Oct 2 Indiana TRO hearing outcome exists in any source checked; no
  invalidating order established; silence not read as favorable. Corteva's
  Oct 5 8-K (separation completion) places PFAS MOU liabilities with
  RemainCo/Corteva, as underwritten. Requested relief remains requests.
- **Oct 5 (uncertified, aggregator):** O 11.81 / H 12.63 / L 11.74 / C
  **12.39** (+3.9%); volume ≈183M shares (≈27% of shares, ≈26x average).
  Oct 2: −5.2% on 78.7M shares against rising markets. No closing-auction
  data available.
- **Versus frozen map (`529286a`, unchanged):** close 19% above the ≈$10.40
  threshold, 3% above the downside band; session low $11.74 was 12.9% above
  the threshold. Price rose into the close; weakness came before the event.
- **Flow:** observed — exceptional volume, price up at the close;
  inferred, not verified — much volume is index crossing, Oct 2 weakness may
  be anticipation. Net-sale direction remains plausible but unconfirmed; the
  25–95M bracket was not certified.
- **Learning:** a documented index migration is not a dislocation; dirty
  fundamentals plus a live legal tail make a poor forced-flow test.
- No Stage 7, no capital decision, CBRS untouched.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

### Pilot 5 — Post-CTVA Checkpoint Review (2026-10-05; append-only)

**Post-CTVA Pilot 5 checkpoint review (2026-10-05; record-only).** No CBRS
research, no Scan 003, no Stage 7, no capital decision, no architecture,
scoring, field, or governance change.

| Case | Mechanism tested | Cheapest falsification | Disposition | What weakened or killed it |
|---|---|---|---|---|
| VYLR | Spin-off: S&P 500 funds mismatched to a new stub | Is there an identifiable pool compelled not to hold VYLR? | `NO_DEMONSTRATED_INVESTABLE_DISLOCATION` | S&P added VYLR to the S&P 500 on Oct 1, removing the index mechanism; volume ≈2% of shares; price closed above the frozen strong band |
| Crasus (646A) | Cross-border spin: tax, sector, Nikkei 225 removal | Is a large, non-fundamental seller pool constrained? | `NO_DEMONSTRATED_FORCED_FLOW_EDGE` | Japan tax treatment refuted the dominant mechanism; fundamentals independently explained weakness; the Nikkei removal was real but unquantified |
| MSGR | Holder-preference mismatch; possible S&P non-addition | Is there a compelled holder pool? | `NO_DEMONSTRATED_FORCED_FLOW_EDGE` | Issuer language was preference, not compulsion; natural buyers existed; stand-alone losses explained weakness |
| CTVA | S&P 500 → MidCap 400 migration, executed Oct 5 close | Is the net mechanical imbalance large enough to misprice? | `NO_DEMONSTRATED_INVESTABLE_DISLOCATION` | Mechanism confirmed and volume ≈26x average, but price rose into the close and never approached the ≈$10.40 threshold; weakness came before the event |

**Repeated patterns the evidence supports:** (1) *must-sell weaker than first
assumed* (Crasus, MSGR, VYLR: tax, preference, and index treatment each
softened on primary text); (2) *natural buyers or offsetting flow* (MSGR
specialists; CTVA's MidCap 400 buyers); (3) *mechanism existed without an
investable dislocation* (CTVA; VYLR priced above the strong band); (4)
*fundamentals contaminated the flow thesis* (Crasus, MSGR, CTVA's legal tail);
(5) *event already recognized or anticipated* (MSGR; CTVA's pre-event
weakness). *Price never reached an independent value threshold* applies to the
two cases that were price-tested (VYLR, CTVA). Not supported: a claim that
discovery arrived too late. No larger taxonomy is asserted.

**CBRS (Scout one-liner only: IPO lockup / float-eligibility expansion).**
Different in kind in three ways: lockup expiry is a *dated window*; the
forced party, if any, is an *eligible* seller, not a compelled one; float
expansion could create *index-driven buying* rather than selling. But it
looks weakest where earlier cases failed: eligibility to sell is not
compelled selling (the MSGR and Crasus failure); a scheduled public date
invites the anticipation seen in CTVA; and no forced-seller population is
identifiable from the description. The new question it could ask (does
scheduled supply or float-driven demand misprice a name after a public date?)
is better preserved as a research question than spent on a triage.

**Disposition: `CLOSE_PILOT5_INSUFFICIENT_EVIDENCE_OF_REPEATABLE_EDGE`.**
Recorded as the checkpoint decision; a formal pilot closeout, if wanted, is a
separate work order, and the Pilot 5 status banner is not rewritten here.
CBRS stays `SURFACE_FOR_TRIAGE`, untouched. **Proved:** Atlas can find
documented mechanical events early and reject weak ones quickly with primary
evidence. **Not proved:** that any forced-flow case yields an investable
edge. Only VYLR and CTVA received post-event price tests; Crasus and MSGR
closed at triage with no post-event price observation; prices were uncertified;
no closing-auction data; no post-event drift beyond Oct 5 was measured.

**Learnings.** (1) Documented is not priced: mechanisms were confirmed and the
price effect was absent or spent. (2) "Must sell" usually turned into "may
sell" once primary text arrived. (3) Pre-registered thresholds and fail-fast
triage produced honest negatives; early relative to trading is not early
relative to recognition. **Improved in Atlas:** discovery-source neutrality
and Scout feedback, the triage kill-condition questions, ex-spin price
basis, pre-event baseline freezing, and separating legal tails. **Forced flow:**
lower-priority opportunistic family; no active scanning; a case enters triage
only if surfaced with a documented compelled seller, a dated window, a
boundable supply, and clean fundamentals. A learning assessment, not a
permanent rule.

**Question worth preserving:** for a strictly one-directional, dated
forced-flow event with fund-level holdings data and clean fundamentals, how
large and how persistent is the price effect from event day through about ten
sessions, net of pre-event drift? (Pilot 5 never measured this window.)

**Capital status: NO REAL PORTFOLIO ACTION.**

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
