# Stock Atlas — Decision Log

Architecture decisions, appended only. Entries are never edited; a superseded
decision gets a new entry that names the one it replaces.

---

## `ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`

| | |
|---|---|
| Date | 2026-09-03 |
| Status | **ACCEPTED** |
| Context | Pilot 1 Red Team closeout |

### Decision

Stage 8 allocation reasoning is captured through **human-authored fields within
the existing final capital decision record**. No separate allocation engine,
scoring model, ranking layer, or optimizer is introduced.

### Reason

Pilot 1 demonstrated strong research and process coherence but **insufficient
explicit linkage between the evidence and the human dollar split**. The gap was
in what got recorded, not in the machinery — so the fix belongs in the record,
not in a new engine.

### What was added

Five fields on the `FINAL_CAPITAL_DECISION` object:

- `why_this_vs_alternatives` — why own this instead of the live alternatives
- `why_this_size` — why approximately this position size (qualitative)
- `allocation_wrong_if` — what observable evidence would weaken it
- `allocation_rationale_status` — `RATIONALE_COMPLETE` or `EXPLORATORY_LOW_RATIONALE`
- `why_not_this_increment` — for a finalist that received no capital

### Consequences

- Funded paper lines missing rationale are **preserved** and flagged
  `EXPLORATORY_LOW_RATIONALE`. Nothing is backfilled.
- A future controlled live-capital pilot requires all three funded-line fields
  before a funded `INITIATE`/`ADD` is decision-ready.
- Unfunded finalists are **never** auto-classified as rejected, and no ranking
  may be inferred from any field.
- Human allocation authority is unchanged. Rationale text cannot alter a dollar
  amount or a position weight.

### Implementation note

`AllocationDecisionRecord` **subclasses** the control layer's `DecisionRecord`
rather than modifying it, so `stock_atlas/` remains byte-identical to the
Red-Team-accepted archive. The added fields still flow into the record hash and
the append-only ledger, because `canonical_payload` serialises via `asdict()`
and `append` re-hashes via `dataclasses.replace()`.

### Explicitly not built

Allocation score · conviction score · sentiment score · sizing formula ·
optimization routine · ranking layer · automated recommendation · probability
engine · new Stage 8 module · second capital-allocation model.

---

## `PILOT1_DECISION_RECORD_SCOPE_CLARIFICATION`

| | |
|---|---|
| Date | 2026-09-03 |
| Status | **ACCEPTED** |
| Context | Records-scope clarification following Pilot 1 closeout |

### Decision

The **September 1 Treasury/Cash decision is the canonical Pilot 1 Stage 8
record.** The September 3 allocation is a **separate post-Pilot-1 paper
calibration decision.** Neither supersedes the other.

### Reason

The two decisions used different dates, different opportunity universes, and
different purposes. Preserving this distinction prevents hindsight
contamination and incorrect Pilot 1 outcome attribution.

### The two records

| | Canonical Pilot 1 Stage 8 | Post-Pilot-1 calibration |
|---|---|---|
| Date | September 1, 2026 | September 3, 2026 |
| Universe | Frozen Pilot 1 33-stock discovery process / resulting Opportunity Set | HBR / Tencent / VEON / CRM plus SPY / Treasury / Do Nothing |
| Decision | $50,000 → Treasury/Cash Sleeve | Tencent $25k · VEON $10k · SPY $10k · 1-Yr Treasury $5k |
| Artifact | `pilot1/PILOT1_STAGE8_HUMAN_DECISION_001.md` | `pilot1/PILOT1_SEPT3_ALLOCATION_RECORD_001.md` |
| Authority | **Authoritative Pilot 1 Stage 8 decision** | Calibration exercise only |

`PILOT1_STAGE8_HUMAN_DECISION_001.md` is not superseded, rewritten, or
reconciled with the September 3 decision.

### Filename provenance note

`PILOT1_SEPT3_ALLOCATION_RECORD_001.md` was initially labeled within Pilot 1
during closeout. Historical review established that the underlying September 3
allocation was a separate post-Pilot-1 paper decision using a different
opportunity universe. **The artifact remains unchanged for provenance**, but it
must not be interpreted as superseding or replacing the September 1 Pilot 1
Stage 8 decision.

Its filename and path therefore under-describe its scope by accident of
sequencing. Renaming it would destroy provenance; this entry is the correction
of record. The artifact's own "Relationship to
`PILOT1_STAGE8_HUMAN_DECISION_001.md`" section predates this clarification and
is superseded **by this entry only** — the artifact text itself stays as
committed.

### Why the September 3 decision still matters

It exposed the Stage 8 rationale gap that produced
`ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`. It remains a valid historical test
case for missing-rationale behaviour, `EXPLORATORY_LOW_RATIONALE`, absence of
synthetic rationale, and human allocation authority — but it is not the
canonical Pilot 1 Stage 8 decision, and test fixtures name it accordingly
(`POST_PILOT1_SEPT3_ALLOCATION`).

### Scope

Records-scope clarification only. Not an architecture reopening. Pilot 1
remains `FROZEN / COMPLETE`.

---

## `PILOT2_BASKET_FROZEN`

| | |
|---|---|
| Date | 2026-09-04 |
| Status | **ACCEPTED** |
| Context | Pilot 2 — Variant Edge & Intentional Allocation |

### Decision

The Pilot 2 discrimination basket is **pre-registered and frozen** before any
underwriting begins:

`FIS` · `FISV` · `MELI` · `JD` · `ADBE` · `SNOW` · `WCC` · `GLNG` · `NTR` ·
`CVS`

plus **SPY**, **Treasury/Cash** and **Do Nothing** as live alternatives.

Basket status: **`FROZEN / PRE-REGISTERED`**. No additions, substitutions,
removals or rebalancing without an explicit documented scope change.

### Reason

Pre-registration is what makes the Pilot 2 result interpretable. A basket that
can move during the pilot cannot falsify anything: a favourable outcome would
be indistinguishable from selection drift. Freezing first means a later
reviewer can tell whether Atlas discriminated among the candidates it was
given, rather than among the candidates that survived.

The names are a **human input**. Atlas did not select them — a basket chosen by
the system under test cannot test that system.

### Consequences

- These securities are **test inputs**, not recommendations, endorsements,
  rankings or preliminary investment conclusions.
- No security begins preferred, promoted, eligible, underwritten or funded.
  List order is transcription order and carries no priority.
- A technical issue is evaluated against the **existing frozen architecture**
  first. Architecture is never expanded merely to preserve a candidate.
- A genuine operational blocker requiring substitution must be **surfaced and
  stopped on**, not silently resolved.

### Governing rule recorded with the freeze

> People and agents may surface ideas. Atlas must prove a variant before an
> idea can compete for capital. Humans allocate — including to cash, beta, or
> nothing.
>
> **Surface does not mean promote. Modeled return does not prove edge.**

---

## `PILOT2_NASDAQ_SESSION_BINDING_EXTENSION`

| | |
|---|---|
| Date | 2026-09-04 |
| Status | **ACCEPTED** |
| Context | Pilot 2 execution readiness — frozen basket venue resolution |

### Decision

Five frozen Pilot 2 names require Nasdaq session attestation:

| Ticker | Provider-resolved MIC |
|---|---|
| `FISV` | `XNMS` (Nasdaq Global Market) |
| `MELI` | `XNGS` (Nasdaq Global Select) |
| `JD` | `XNGS` |
| `ADBE` | `XNGS` |
| `GLNG` | `XNGS` |

**Replacing those securities would materially alter the pre-registered
discrimination basket.** Deliberate Nasdaq session-calendar support is
therefore the **narrower and more faithful response.**

**This is venue coverage, not an architecture redesign.** Unsupported
exchanges remain fail-closed.

### What was added

`live_session_calendar.SUPPORTED_MICS` gains exactly two entries, scoped to
the MICs the frozen basket actually produced:

```
"XNGS": "XNAS"
"XNMS": "XNAS"
```

Both are bound to `exchange_calendars.get_calendar("XNAS")`, requested **by
name** — not by reusing the `XNYS` lookup already made for NYSE names.

### A constraint surfaced during implementation

`exchange_calendars==4.13.2` documents `XNAS` (and `NASDAQ`, `ARCX`, `XASE`,
`BATS`, `OOTC`) as aliases resolving to the **same underlying schedule object**
as `XNYS` (`calendar_utils._default_calendar_aliases`). There is no
independently-coded Nasdaq calendar in this pinned library.

This was surfaced to the human before implementation, since it appeared to
conflict with "do not silently map a Nasdaq MIC to the NYSE calendar." The
resolution: the alias reflects a real fact, not a shortcut — NYSE and Nasdaq
are both regulated U.S. equity markets observing SIFMA-coordinated market
holidays and identical 9:30 a.m.–4:00 p.m. ET regular sessions, so the
trading-day/session-hour data genuinely is the same. What makes the binding
**deliberate rather than silent** is that `XNGS`/`XNMS` request the `XNAS`
calendar **by their own name**, are attested as bound to a Nasdaq venue in
their own `SessionAttestation.exchange` field, and are never satisfied by a
caller that only asked for `XNYS`. No second calendar library was added.

### Consequences

- Supported NYSE behaviour is unchanged (regression-tested).
- `FISV`, `MELI`, `JD`, `ADBE`, `GLNG` now bind through the Nasdaq calendar,
  with genuine completed-session, intraday-refusal, holiday and early-close
  semantics (day-after-Thanksgiving 2026 verified as a real 1:00 p.m. ET
  close).
- Any other MIC — `XLON`, `XHKG`, `ARCX`, `BATS`, `XASE`, the bare string
  `"NASDAQ"`, or anything else outside the four supported entries — still
  fails closed. No generic "all U.S. exchanges" fallback was created.
- All 10 frozen Pilot 2 basket names verified, live, to resolve to an
  explicitly supported MIC.

### Explicitly not done

No basket change. No security substitution. No underwriting. No investment
conclusion generated. No second market-data vendor. No second calendar
library. No completed-session control loosened.

---

## `PILOT2_STAGE8_BINDING_READINESS`

| | |
|---|---|
| Date | 2026-09-04 |
| Status | **ACCEPTED** |
| Context | Closing two decision-time binding blockers before Pilot 2 Stage 8 |

### Decision

Two known decision-time binding issues are closed, both by the same narrow
principle already used for the Nasdaq extension — never by weakening
identity or freshness controls.

**1. SPY / `ARCX`.** `exchange_calendars==4.13.2` documents `ARCX` (NYSE Arca,
SPY's primary MIC) as an alias resolving to the same underlying schedule
object as `XNYS` — structurally identical to how `XNAS` was already handled
for the Nasdaq basket names. `SUPPORTED_MICS` gains exactly one entry,
`"ARCX": "ARCX"`, requested by its own name. SPY now binds live, FRESH,
through the full Gate B pipeline.

**Correction to the prior entry.** `PILOT2_NASDAQ_SESSION_BINDING_EXTENSION`
(above) listed `ARCX` among the MICs that "still fail closed." That was
accurate when written — SPY had not yet been bound live. It is not rewritten,
per the append-only rule; this entry is the correction of record. `ARCX` is
now supported, deliberately and narrowly, for exactly the reason stated here.

**2. JD identity integrity.** `JD` is a genuine bare-ticker collision:
TwelveData's `symbol_search` reports `AMBIGUOUS` across JD.com's Nasdaq ADR,
JD Sports Fashion plc (LSE, unrelated issuer), and a Buenos Aires depositary
receipt. Atlas's own identity resolution was never ambiguous — SEC CIK
`0001549802` unambiguously identifies JD.com — but `bind_price_snapshot`
previously refused to proceed past the provider's `AMBIGUOUS` state at all,
correctly, rather than trusting a ticker-only match.

`live_price_binding.py` gains `_disambiguate_via_known_mic`, invoked only
when `resolve_symbol` reports `AMBIGUOUS`: it re-queries the provider with
`mic_code` supplied explicitly (Atlas already knows JD.com trades on `XNGS`,
from the venue-readiness work), rather than trusting the provider's
undocumented bare-ticker default. Two independent signals must agree before
anything is trusted — the MIC-qualified query itself, and `resolve_symbol`'s
own separately-fetched `quote_confirmed` field — and TwelveData's `mic_code`
parameter was empirically confirmed to be a genuine, respected filter (a
mismatched MIC returns HTTP 404, not a silent substitution) before this was
built on. A missing `expected_mic`, a failed query, or disagreement between
the two signals all fail closed; nothing here weakens the existing B2
class-substitution guard, which still governs every unambiguous name
unchanged.

### Why this is not "ticker-only matching"

The distinction is the query itself, not just a post-hoc check. A bare
`symbol=JD` query asks the provider to guess and trusts its guess. A
`symbol=JD&mic_code=XNGS` query tells the provider which instrument to
return, using a MIC Atlas already established independently (SEC CIK
resolution, done once, unambiguous on Atlas's side from the start). The
ambiguity being resolved is in the *provider's* bare-ticker default, not in
Atlas's own identity of the security.

### Consequences

- SPY, FIS, MELI, JD, and Treasury/Cash can now all reach a decision-time
  price/session bind without an unresolved identity or venue-control defect.
- The adversarial case (JD Sports Fashion's own venue, `XLON`) is refused at
  the calendar layer — it was never an authorized MIC — before any price bind
  is even attempted.
- A MIC-qualified query to a supported calendar where JD.com does not
  actually list (`XNMS`, tested directly) is refused with a 404, proving the
  unrelated security cannot satisfy the bind merely because the calendar
  itself is authorized.
- `SUPPORTED_MICS` is now `{XNYS, NYSE, XNGS, XNMS, ARCX}` — scoped to exactly
  the frozen basket's venues plus the required Stage 7 alternative's venue,
  nothing broader.

### Explicitly not done

No Stage 7 state changed. No return assumption changed. No basket change. No
new market-data vendor. No generic "all U.S. exchanges" fallback. No
weakening of the B2 identity guard for any name that already resolves
unambiguously.

---

## `STAGE8_KEY_RISKS_CONSIDERED`

| | |
|---|---|
| Date | 2026-09-07 |
| Status | **ACCEPTED** |
| Context | Pilot 2, Cycle 2 Stage 8 decision record |

### Decision

A new field, `key_risks_considered`, is added to the Stage 8 decision-record
vocabulary. It captures the material risks explicitly reviewed by the human
decision-maker at Stage 8: human-reviewed, concise, no scoring, no fixed
number of risks, no required categories, and **may be blank** when the human
did not explicitly review risks — absence is valid evidence, not a defect to
correct.

**This field supplements the Allocation Bridge. It does not replace**
`why_this_vs_alternatives`, `why_this_size` or `allocation_wrong_if`, and
**does not alter** the existing derived allocation-rationale status. Re-run
with the same three arguments `derive_allocation_rationale_status` already
took, the result is identical with or without `key_risks_considered` present
— the function was never given a fourth argument to change its answer.

### Why this is a lightweight record improvement, not a new subsystem

`key_risks_considered` is documentary. It is not scored, not weighted, not
fed into any comparison, and does not gate Stage 7 or Stage 8 eligibility. No
risk engine, ranking, weighting system, probability model, or fixed risk
taxonomy was introduced. It exists so a later Loop B or Loop C can ask which
identified risks mattered, which did not, and what was missed — a record for
future comparison, not a live control.

### First application — Cycle 2

FIS's two previously-recorded risk considerations (leverage from ~$7.7B of
new Issuer Solutions debt and the 2.8x deleveraging target; underlying growth
weakness despite raised FCF guidance) are formally captured as FIS's
`key_risks_considered` in `PILOT2_STAGE8_HUMAN_DECISION_002.md`. No risk was
added beyond what was already explicitly human-reviewed. JD, SPY,
Treasury/Cash and Do Nothing all carry an empty `key_risks_considered` for
Cycle 2 — none was invented to populate the field.

### Loop interpretation, clarified alongside this change

- **Loop A** asks what Atlas changed in the decision *process*. During
  paper/shadow testing, Loop A does **not** require mathematically
  intentional sizing — a genuinely intentional decision (Cycle 2) and a
  randomized one (Cycle 1) are both legitimate Loop A findings.
- **Allocation-rationale status** asks whether the required human-authored
  fields are complete. This is a **separate control** from Loop A — Cycle 2
  is Loop A = YES (intentional) while still `EXPLORATORY_LOW_RATIONALE` for
  both funded lines (the Allocation Bridge was not formally completed). One
  is not evidence for the other.
- **Loop B**, when a trigger fires, compares new evidence against: the
  original thesis, the original variant, `key_risks_considered`, and any
  newly discovered risks. It does not rewrite the original Stage 8 record.
- **Loop C**, at the stated horizon, evaluates what Atlas believed, which
  risks were identified, what actually happened, which risks mattered, which
  did not, what important risk was missed, and performance versus the
  contemporaneous alternatives — **never graded solely on price return.**

### Testing-mode allocation clarification (recorded alongside this change)

> Paper/shadow allocations may be random or exploratory by design. Random
> sizing during system testing is not evidence that the allocation layer is
> weak or that intentional allocation failed. Live-capital allocation
> discipline may become more deliberate or structured later based on pilot
> and outcome evidence. Do not pre-build a sizing engine or formula before
> that evidence exists.

This prevents a future Loop A review from mistaking a deliberately random
test allocation (Cycle 1) for a process defect.

### Historical integrity

Applies prospectively. Cycle 1 (`PILOT2_STAGE8_HUMAN_DECISION_001.md`) is
**not** modified to backfill `key_risks_considered` — it was randomized, no
risk review was recorded at the time, and the frozen record is not rewritten
to add one now.

### Explicitly not done

No risk engine. No risk score. No risk ranking or weighting system. No
probability model. No fixed risk taxonomy or required category list. No new
decision layer. No change to the allocation-rationale-status derivation. No
edit to any already-frozen record.

---

## `PILOT3_AGENT_WORLD_DISCOVERY_DISPOSITIONS`

| | |
|---|---|
| Date | 2026-09-07 |
| Status | **ACCEPTED** |
| Context | Pilot 3, Agent World Batch 001 |

### Decision

Five discovery-stage disposition states are adopted for candidates surfaced
by an external discovery source (Agent World, the first named instance):
`SURFACE_WITH_EVIDENCE_GAP`, `REFERENCE_PEER_TAPE`,
`ADVANCE_TO_PRIMARY_EVIDENCE_TRIAGE`, `CALENDAR_HOLD`, `REFERENCE_ONLY`. Each
is a discovery-stage label only — none authorizes underwriting, funding, or
capital action by itself, consistent with Discovery Contract v0.1's "Discovery
allocates attention, not capital."

The governing principle, extending `PILOT3_RECORD_001.md`'s source-blind
capital-allocation finding to a new named source:

> **Preserve provenance. Remove privilege.**

Source state (Agent World's `WATCH` / `CALENDAR` / `MAP_ONLY`) is logged as
provenance. It is never treated as underwriting privilege: no candidate is
advanced because of where it came from, and none is penalized for that reason
either. Treatment is driven by the same evidence, typed uncertainty,
alternatives and portfolio-fit standard as every other Stock Atlas candidate.

### Why this is not a scoring system

No numeric or ordinal score attaches to Agent World or to any candidate
because of its source. The disposition states are qualitative labels
describing *what evidence exists so far*, not a ranking of source quality or
idea quality. A lightweight discovery log accumulates, over time, whether
Agent World surfaced ideas Atlas would otherwise have missed that survived
underwriting — but that log records outcomes, not a score.

### Consequences

- XOM, evidence-dependent, is held at `SURFACE_WITH_EVIDENCE_GAP` rather than
  underwritten ahead of the completed-session evidence its own thesis
  requires.
- AAPL and JPM, both calendar-dependent, are held rather than underwritten
  ahead of their respective events.
- SMH and NVDA are reference-only; strong sector sentiment alone does not
  promote them.
- AVGO alone advanced to primary-evidence triage in Batch 001, and that
  triage — not its Agent World provenance — produced its
  `PROMOTE_TO_DEEP_UNDERWRITING` result.

### Explicitly not done

No agent score. No source score. No ranking. No discovery-quality algorithm.
No change to Discovery Contract v0.1, Stage 7, or Stage 8. No rewrite of
`PILOT3_RECORD_001.md`, or of any Pilot 1 or Pilot 2 record.

---

## PILOT3_AVGO_DEEP_UNDERWRITING_RESULT (2026-09-07)

**Record:** `docs/pilot3/PILOT3_AVGO_DEEP_UNDERWRITING_001.md`

AVGO's deep underwriting, following its triage-stage promotion, returned
`BLOCKED_BY_MATERIAL_UNCERTAINTY` rather than `ADVANCE_TO_FINAL_CAPITAL_COMPARISON`
or `NO_DEMONSTRATED_EDGE`.

**What survived:** genuine business quality — a $164.6B non-cancellable
revenue backlog (RPO) including a newly signed long-term custom-AI-
accelerator contract, free cash flow not flattered by one-time items, and a
balance sheet with ample flexibility (>20x interest coverage from FCF alone)
to withstand a significant AI-growth disappointment.

**What did not survive:** the triage-stage variant that the market was
under-weighting an under-appreciated acceleration. A corrected consensus/
priced-in test (reverse-engineering FY2027 non-GAAP EPS implied by the
triage record's own cited forward-multiple range, rather than relying on a
sector-median P/E comparison) showed the current price already requires
something close to continued strong execution — not a Downside-priced
bargain. A variant-durability test found no strong evidence-grounded reason
a distinctive, persistent gap should exist in one of the most widely
followed semiconductor names, three trading sessions after the market
priced the same guidance data.

**Why `BLOCKED_BY_MATERIAL_UNCERTAINTY` rather than a clean call:** several
named, closeable evidence gaps are load-bearing and unresolved — non-AI
semiconductor trend, whether AI-specific customer concentration is rising
(the disclosed company-wide top-5 figure was flat at ≈40% across FY2024 and
FY2025 despite AI's rise to 56% of Q3 FY2026 revenue — an unexplained
tension, not resolved by inference in either direction), Infrastructure
Software/VMware integration detail, and the identity of the new large
AI-accelerator counterparty. None of these could be resolved from the
primary sources retrievable through available tooling (the 10-Q/10-K MD&A
sections were too large for the fetch tool to return intact).

**Consequence:** Stage 7 has not begun for AVGO. Named falsifiers/revisit
triggers (Q4 FY2026 results, Q1 FY2027 guidance, customer-concentration
disclosure in the next 10-K/10-Q, MD&A retrieval) are recorded as the path
to resolving this block — not a new methodology, a new variant, or a second
deep-underwriting pass on the same evidence.

**Batch 001 controls unchanged:** XOM `SURFACE_WITH_EVIDENCE_GAP`, SMH
`REFERENCE_PEER_TAPE`, AAPL `CALENDAR_HOLD`, JPM `CALENDAR_HOLD`, NVDA
`REFERENCE_ONLY`. AVGO's disposition is not used to promote any
semiconductor peer.

**Explicitly not done:** no Stage 7 comparison, no Stage 8 decision, no
capital allocated, no second Agent World batch, no advance of XOM or any
other Batch 001 candidate.

---

## PILOT3_MANUAL_DISCOVERY_BATCH_002_RESULT (2026-09-07)

**Records:** `docs/pilot3/PILOT3_MANUAL_DISCOVERY_BATCH_002.md`,
`docs/pilot3/PILOT3_PATH_PRIMARY_EVIDENCE_TRIAGE_001.md`,
`docs/pilot3/PILOT3_MDB_PRIMARY_EVIDENCE_TRIAGE_001.md`

Manual Discovery Batch 002 registers six candidates under a new source
provenance, `MANUAL_DISCOVERY_BRIDGE`, used because Agent World is not yet
fully operational. This is a temporary bridge, not an architecture change:
manual candidates receive no underwriting advantage or disadvantage versus
Agent World or any other source, per the same governing principle used in
Batch 001 — **preserve provenance, remove privilege.**

**PATH and MDB** received full primary-evidence triage; SPXC, SOLS, PCG,
and DOCU were registered with an initial discovery state only and were not
triaged.

**PATH → `NO_DEMONSTRATED_EDGE`.** The discovery-stage variant (market
overreacting to near-term ARR/growth mechanics) did not survive: the
company's own Q3 FY2027 guide, verified against a primary prior-year
comparable, implies revenue growth roughly halving (13% actual in Q2 to an
implied ~7–8% YoY), and net-new ARR fell in absolute dollars across the two
most recent primary data points ($59M → $37M). A reverse-engineered
valuation (≈3.4x EV/ARR) showed the market has already substantially
repriced the name for weaker growth, not ignored real evidence of cash
generation. No alternative variant was substituted to rescue the candidate.

**MDB → `PROMOTE_TO_DEEP_UNDERWRITING`.** The discovery-stage variant
(market over-weighting a flat, narrow Atlas growth figure) was corroborated
by primary forward-bookings evidence — remaining performance obligations
+91% YoY and current RPO +73% YoY, both filed the same day as the earnings
release, far outpacing the 29–30% revenue/Atlas growth rate the market
reacted to — and a direct CFO attribution that the raised full-year guide
was "mainly due to Atlas." The market-could-be-right case (a three-quarter
flat Atlas pattern, possible RPO concentration in large lumpy deals, heavy
SBC diluting non-GAAP profitability) is real and unresolved, and the
reverse-engineered valuation (≈9.2x forward revenue, ≈57x forward non-GAAP
EPS) is full rather than cheap — both are named as open questions for deep
underwriting, not resolved here.

**AVGO lesson applied explicitly:** both candidates arrived with a similar
surface pattern (beat/raise plus a selloff). They reached opposite
dispositions because the underlying primary evidence differed — a real,
guided negative fact for PATH versus a real, corroborating positive fact
for MDB — not because of a templated beat/selloff/multiple rule.

**Batch 001 unchanged:** AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM
`SURFACE_WITH_EVIDENCE_GAP`, SMH `REFERENCE_PEER_TAPE`, AAPL/JPM
`CALENDAR_HOLD`, NVDA `REFERENCE_ONLY`.

**Explicitly not done:** no deep underwriting for MDB, no triage of SPXC/
SOLS/PCG/DOCU, no Stage 7 or Stage 8, no capital allocated, no advance of
XOM, no Batch 003.

---

## PILOT3_MDB_DEEP_UNDERWRITING_RESULT (2026-09-07)

**Record:** `docs/pilot3/PILOT3_MDB_DEEP_UNDERWRITING_001.md`

MDB's deep underwriting, following its triage-stage promotion, returned
`NO_DEMONSTRATED_EDGE`.

**What the triage variant relied on:** RPO +91% YoY and cRPO +73% YoY,
both far outpacing the 29–30% revenue/Atlas growth rate, taken as evidence
of forward bookings momentum the market was under-weighting.

**What deep underwriting found:** reconstructing the same primary
disclosure (SEC XBRL `RevenueRemainingPerformanceObligation`) on a
quarter-by-quarter basis rather than a single YoY snapshot showed the
apparent acceleration was a step-change concentrated almost entirely in
Q3–Q4 FY2026 (RPO nearly doubled, +85%, across those two quarters
combined). In the two quarters since, RPO grew a combined +3.2% and cRPO
+4.1% — both slower than the ~29% YoY Atlas growth rate they were supposed
to be leading. The specific mechanism the promoted variant depended on had
already played out and stopped; no primary source names the cause of the
step-change (an unresolved evidence gap, not filled by inference in either
direction).

**Corroborating findings:** Atlas growth confirmed flat at ~29% for a third
consecutive fiscal quarter (Q4 FY2026, Q1 FY2027, Q2 FY2027, all
primary-sourced). A reverse-engineered priced-in test showed today's ~57x
forward non-GAAP P/E requires roughly 28%/year sustained EPS growth for
three years to normalize to a mature-grower multiple — a demanding,
specific assumption the flat-Atlas/decelerated-RPO trajectory does not
currently support. A coarse scenario framework placed the current price
above the Base case band, inside only the Upside band — the opposite
pattern from AVGO, where the Base case bracketed the price.

**Genuine positives recorded fairly, not sufficient to sustain the
variant:** broad-based, continuing customer growth (unaffected by the RPO
lumpiness); a declining SBC-as-percentage-of-revenue trend (24%→19% over
five quarters); a first clearly positive GAAP operating-income quarter
after a noisy, non-monotonic series; no debt; an active buyback program
(though buyback dollars remain smaller than the SBC expense they partially
offset).

**Consequence:** Stage 7 has not begun for MDB. No alternative thesis was
substituted to rescue the candidate, per standing governance. Named
falsifiers/revisit triggers (next Atlas print, next RPO/cRPO print, RPO
conversion evidence, margin-inflection confirmation) are recorded as the
path to reopening this candidate if evidence changes — not a new
methodology or a second deep-underwriting pass on the same evidence.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, SPXC
`SURFACE_WITH_EVIDENCE_GAP`, SOLS `EVENT_DRIVEN_HOLD`, PCG
`SURFACE_WITH_EVIDENCE_GAP`, DOCU `SURFACE_WITH_EVIDENCE_GAP`. Batch 001
(AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `SURFACE_WITH_EVIDENCE_GAP`,
SMH `REFERENCE_PEER_TAPE`, AAPL/JPM `CALENDAR_HOLD`, NVDA
`REFERENCE_ONLY`) is unchanged.

**Explicitly not done:** no Stage 7 comparison, no Stage 8 decision, no
capital allocated, no triage of SPXC/SOLS/PCG/DOCU, no advance of XOM, no
Batch 003.

---

## PILOT3_DOCU_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_DOCU_PRIMARY_EVIDENCE_TRIAGE_001.md`

DOCU's primary-evidence triage returned `PROMOTE_TO_DEEP_UNDERWRITING`,
applying the explicit lesson from the MDB deep underwriting: rather than
trust a single YoY snapshot, IAM's share of total ARR was reconstructed
across five consecutive fiscal quarters (2.3% at FY2025 year-end →10.8%
→12.6%→15.1% through Q2 FY2027), with the quarter-over-quarter point gain
itself accelerating through the most recent quarter — a live, still-building
trend, unlike MDB's RPO, which had already peaked and decelerated below the
revenue growth rate.

**Corroborating findings:** GAAP operating margin improved every quarter
measured (7.9%→13.4%); SBC declined as a percentage of revenue every
quarter (~20.0%→17.0%); actual common shares outstanding fell 6.4% over
four quarters with the pace accelerating, and buyback dollars now clearly
exceed SBC dollars (unlike MDB) — genuine, not merely dilution-offsetting,
per-share value creation.

**The unresolved, load-bearing question:** total company revenue growth has
held flat at 8–9% YoY for five consecutive quarters despite IAM's near-
sevenfold rise in ARR share — consistent with IAM currently offsetting core
e-signature maturity rather than lifting the consolidated growth rate. This
is recorded as genuinely unresolved (not refuted, unlike PATH's and MDB's
specific mechanisms), checkable within 1-2 quarters as IAM approaches its
own guided 18-19%-of-ARR exit rate, and is the explicit focus for deep
underwriting.

**Valuation note:** a Gate-B `FRESH` completed-session price bind could not
be obtained (the U.S. market was open at decision time; the provider
returned an in-progress intraday observation rather than the prior
completed session's close, and Gate B correctly returned `STALE` per its
fail-closed design). Per standing governance, this was not forced or
substituted — an unvalidated reference price was used for the coarse
priced-in test, explicitly labeled as such, with the instruction that a
certified bind be captured before deep underwriting or Stage 7 relies on a
specific valuation figure. That coarse math (≈3.3x forward revenue, ≈14x
forward non-GAAP EPS, ≈9.6% FCF yield) suggests DOCU's price does not
already assume the growth outcome the variant depends on — a materially
different pattern from AVGO, PATH, and MDB in this pilot, where reverse-
engineering showed the price already assumed continued strong execution.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, SPXC `SURFACE_WITH_EVIDENCE_GAP`, SOLS
`EVENT_DRIVEN_HOLD`, PCG `SURFACE_WITH_EVIDENCE_GAP`. Batch 001 (AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `SURFACE_WITH_EVIDENCE_GAP`, SMH
`REFERENCE_PEER_TAPE`, AAPL/JPM `CALENDAR_HOLD`, NVDA `REFERENCE_ONLY`) is
unchanged.

**Process note:** the work order for this triage arrived truncated (cut off
mid-sentence in its market-reaction instruction, before any disposition
menu or stop condition was given). The triage was completed using the
disposition vocabulary and template already established for PATH and MDB
rather than pausing to ask, since the pattern was unambiguous from
precedent; this is flagged in the triage record itself for the user to
correct if different scope was intended.

**Explicitly not done:** no deep underwriting for DOCU, no triage of SPXC/
SOLS/PCG, no Stage 7 or Stage 8, no capital allocated, no advance of XOM,
no Batch 003.

---

## PILOT3_DOCU_DEEP_UNDERWRITING_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_DOCU_DEEP_UNDERWRITING_001.md`

DOCU's deep underwriting, following its triage-stage promotion, returned
`BLOCKED_BY_MATERIAL_UNCERTAINTY`.

**What survived:** durable, multi-quarter capital-allocation and margin
quality — GAAP operating margin improved monotonically across six
consecutive quarters (7.9%→13.4%), SBC-as-percent-of-revenue declined for
five straight quarters, and buybacks were executed at an average price
(~$47/share, from the 10-Q's repurchase table) meaningfully below the
~$66 reference price used in this record — disciplined, value-accretive
capital return, not mechanical dilution-offsetting.

**What did not survive intact:** the growth-inflection half of the
variant. A coarse but directly-derived growth-bridge calculation (using
only two company-disclosed data points -- FY2026's 8.0% total ARR growth
and IAM's ARR share at FY2025/FY2026 year-end) found core (ex-IAM) ARR was
approximately flat to slightly declining (~-1.4%) over FY2026 -- IAM
accounts for essentially all of the company's net ARR growth. Reaching a
materially higher blended growth regime would require IAM's own growth
rate (estimated at ~407% YoY off a small FY2026 base, implying ~56-60%
YoY at its current larger size) to re-accelerate toward ~83%, which the
company's own Q4 FY2027 ARR-share guide (implying a moderating, not
accelerating, pace of further gains) does not support.

**A distinction the record treats as central:** IAM's rising point-of-ARR-
share gain (+1.8pt then +2.5pt sequentially) is not the same thing as an
accelerating IAM dollar growth rate -- a constant or declining growth-rate
spread produces a larger point gain each quarter purely from IAM's
increasing size. This nuance materially tempers the triage-stage framing.

**Valuation:** no Gate-B-certified `FRESH` price could be obtained -- the
market was open at decision time, and the sanctioned binder
(`bind_price_snapshot`) has no capability to bind against a specific
historical completed-session close, only the current live quote. This is
reported as a binder capability limitation, not engineered around; no new
binding path was added. The unvalidated reference price carried forward
from triage (~$66) was found, via reverse-engineering, to roughly match
rather than clearly beat this record's own Base case -- removing the
valuation cushion that might otherwise have offset the unresolved growth
question.

**Why `BLOCKED_BY_MATERIAL_UNCERTAINTY` rather than a clean call:** real,
durable business and capital-allocation quality argues against
`NO_DEMONSTRATED_EDGE`; an unresolved, load-bearing growth question with no
current valuation cushion argues against `ADVANCE_TO_FINAL_CAPITAL_COMPARISON`.
The question is closeable by near-term evidence (next 1-2 quarters' ARR
prints; FY2027 year-end total ARR disclosure, which would let the §4
growth-bridge calculation be re-run) rather than requiring new methodology.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, SPXC `SURFACE_WITH_EVIDENCE_GAP`, SOLS
`EVENT_DRIVEN_HOLD`, PCG `SURFACE_WITH_EVIDENCE_GAP`. Batch 001 (AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `SURFACE_WITH_EVIDENCE_GAP`, SMH
`REFERENCE_PEER_TAPE`, AAPL/JPM `CALENDAR_HOLD`, NVDA `REFERENCE_ONLY`) is
unchanged.

**Explicitly not done:** no Stage 7 comparison, no Stage 8 decision, no
capital allocated, no triage of SPXC/SOLS/PCG, no advance of XOM, no
Batch 003.

---

## PILOT3_XOM_RELATIVE_DISLOCATION_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_XOM_RELATIVE_DISLOCATION_RESOLUTION_001.md`

XOM's registered evidence gap (`SURFACE_WITH_EVIDENCE_GAP`, held since
Batch 001 registration pending the required first completed U.S. session
following a weekend geopolitical/oil-supply escalation) was resolved once
that evidence existed. The pre-registered discovery question -- unchanged
after seeing the outcome, per standing discipline -- was: does XOM
materially lag the change in oil economics after the market has had an
opportunity to price the new information?

**Completed-session evidence (2026-09-04 baseline through 2026-09-10,
latest completed session):** XOM +3.61% cumulative, CVX +1.99%, XLE +1.36%.
XOM led both peers on every single completed session in the window, and
the gap widened (not narrowed) by the final session. USO (a provider-
sourced WTI-tracking proxy, used because the current provider stack has no
primary WTI/Brent series -- a disclosed infrastructure gap, not routed
around) rose +11.57% over the same window; all three equities
under-reacted to the commodity move relative to itself, uniformly and as
expected for integrated-major economics -- not as an XOM-specific lag.

**Finding:** the pre-registered lag never materialized. There was no
relative dislocation for a candidate variant to explain. Secondary
evidence reviewed (ceasefire-negotiation coverage, a partial pullback in
the oil proxy on the following, uncertified session) further supports a
temporary-event-trade reading over a durable one, reinforcing rather than
being needed to reach the disposition.

**Disposition: `NO_DEMONSTRATED_EDGE`.** Per the governing work order's own
explicit instruction, this is recorded as a successful Pilot 3
discovery-system outcome, not a failed candidate: Agent World surfaced a
coherent, evidence-testable hypothesis at the moment the news broke, and
Atlas's discipline of waiting for completed-session evidence rather than
front-running it is what allowed the hypothesis to be cleanly falsified
rather than acted on prematurely.

**Fresh-price note:** Gate B's `bind_price_snapshot` correctly returned
`STALE` for the live intraday quote (market open at decision time) for the
same disclosed reason found in the DOCU deep underwriting -- the binder has
no capability to bind a specific historical completed-session close. Per
this work order's explicit instruction not to use intraday prices, the
already-attested 2026-09-10 completed-session close was used directly; no
new binding capability was added.

**Batch 001/002 controls unchanged:** AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`,
SMH `REFERENCE_PEER_TAPE`, AAPL/JPM `CALENDAR_HOLD`, NVDA `REFERENCE_ONLY`;
PATH `NO_DEMONSTRATED_EDGE`, MDB `NO_DEMONSTRATED_EDGE`, DOCU
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, SPXC `SURFACE_WITH_EVIDENCE_GAP`, SOLS
`EVENT_DRIVEN_HOLD`, PCG `SURFACE_WITH_EVIDENCE_GAP`.

**Explicitly not done:** no deep underwriting of XOM, no triage of
SPXC/SOLS/PCG, no Stage 7 or Stage 8, no capital allocated, no Batch 003.

---

## PILOT3_AAPL_POST_EVENT_VARIANT_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_AAPL_POST_EVENT_VARIANT_TEST_001.md`

AAPL's `CALENDAR_HOLD` (held pending the September 9, 2026 product event)
was resolved via post-event primary-evidence triage. Following the
established discipline of not evaluating whether products are interesting
but whether the event created an investable variant, this record separated
EXPECTED-BEFORE-EVENT from NEW-AT-EVENT: the foldable iPhone Duo's
existence, the iPhone 18 Pro/Pro Max's incremental spec/price changes, and
the AI-enhanced Siri feature set were all broadly anticipated and are not
new information. One genuine, well-corroborated new fact emerged: the
$1,999 iPhone Duo starting price undercut every cited pre-event analyst
estimate (JPMorgan $1,999 floor, BofA $2,099, IDC $2,500+).

**Market-reaction evidence, checked directly (same discipline as the XOM
relative-dislocation record) rather than assumed:** AAPL was roughly flat
on the event day itself (Sept 9, -0.28%), then moved +3.56% the following
completed session (Sept 10) once analyst notes digesting the pricing
surprise were published -- a delayed, not instant, reaction that continued
(uncertified) into the next session rather than reversing.

**Why `EVIDENCE_GAP` rather than a clean promote/reject:** a real new fact
and a real, still-developing market reaction rule out `NO_DEMONSTRATED_EDGE`.
But whether that reaction is proportionate to, short of, or already ahead
of the actual economic magnitude cannot be assessed -- iPhone Duo preorders
do not begin until October 16, 2026, so no real demand signal, company
guidance, or stabilized analyst consensus yet exists. This is treated as
the same category of state as XOM's pre-resolution hold (decisive evidence
not yet in existence, on a short, concrete, dated horizon) rather than
`BLOCKED_BY_MATERIAL_UNCERTAINTY` (substantial evidence reviewed and found
genuinely irresolvable, as with AVGO and DOCU).

**Process note:** the work order for this triage arrived truncated (cut off
mid-sentence in its economic-impact instruction, before any falsifier,
disposition menu, or stop condition was given). It was completed using the
disposition vocabulary and template already established for PATH, MDB, and
DOCU rather than pausing to ask, since the pattern was unambiguous from the
work order's own "post-event primary-evidence triage" framing; flagged in
the triage record itself for correction if different scope was intended.

**Batch 001/002 controls unchanged:** AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`,
XOM `NO_DEMONSTRATED_EDGE`, SMH `REFERENCE_PEER_TAPE`, JPM `CALENDAR_HOLD`,
NVDA `REFERENCE_ONLY`; PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, DOCU `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SPXC
`SURFACE_WITH_EVIDENCE_GAP`, SOLS `EVENT_DRIVEN_HOLD`, PCG
`SURFACE_WITH_EVIDENCE_GAP`.

**Explicitly not done:** no deep underwriting of AAPL, no triage of
SPXC/SOLS/PCG, no advance of JPM, no Stage 7 or Stage 8, no capital
allocated, no new registration batch.

---

## PILOT3_SPXC_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_SPXC_PRIMARY_EVIDENCE_TRIAGE_001.md`

SPXC's primary-evidence triage returned `PROMOTE_TO_DEEP_UNDERWRITING`.
The discovery-stage question -- is the market over-penalizing near-term
margin pressure while underweighting durable growth, or correctly
repricing lower-quality growth -- was tested against Q2 2026 primary
evidence.

**Corroborating findings:** organic growth (16.9% company-wide) accounted
for roughly 74% of total reported growth (22.9%) -- not acquisition-
manufactured. HVAC segment margin fell 260bps for two specific, disclosed,
directly testable reasons (capacity-expansion startup costs, tariffs),
while Detection & Measurement margin expanded 610bps on favorable mix --
a mixed, not uniformly deteriorating, margin picture. FY2026 guidance was
raised meaningfully across revenue (+4.8% at the midpoint), adjusted
EBITDA (+5.3%), and adjusted EPS (+5.7%). Leverage remains low (~1.5x pro
forma gross) despite five acquisitions across two recent periods.

**Market-reaction evidence, checked directly:** the initial post-print
selloff (-14.4% over two sessions) fully reversed within the following two
sessions, exceeding the pre-print level -- evidence the market's own
first-pass reaction largely accepted the temporary-margin-pressure
explanation. However, the stock then gave back the entire recovery over
the following five to six weeks, returning to essentially the same trough
by September, for reasons no primary or secondary evidence gathered in
this record explains. This is disclosed as a genuine, unresolved gap and
named explicitly as the central open question for deep underwriting, not
papered over or used to block promotion given the strength of the
underlying fundamental evidence.

**Valuation note:** a coarse checkpoint (~22x P/E, ~16x EV/EBITDA on the
raised guidance) found the stock full, not statistically cheap, tempering
the promotion without rejecting it. A Gate-B `FRESH` bind could not be
obtained (market open at decision time); the already-attested 2026-09-10
completed-session close was used directly, consistent with the XOM and
AAPL precedent -- no new binding capability was added.

**Process note:** the work order for this triage arrived truncated (cut
off mid-sentence in its organic-vs-acquired-growth instruction, before any
market-could-be-right, falsifier, valuation, disposition menu, or stop
condition was given). It was completed using the disposition vocabulary
and template established for PATH, MDB, and DOCU rather than pausing to
ask; flagged in the triage record itself for correction if different scope
was intended.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, DOCU `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SOLS
`EVENT_DRIVEN_HOLD`, PCG `SURFACE_WITH_EVIDENCE_GAP`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `NO_DEMONSTRATED_EDGE`, SMH
`REFERENCE_PEER_TAPE`, AAPL `EVIDENCE_GAP`, JPM `CALENDAR_HOLD`, NVDA
`REFERENCE_ONLY`.

**Explicitly not done:** no deep underwriting of SPXC, no triage of
SOLS/PCG, no Stage 7 or Stage 8, no capital allocated, no Batch 003.

---

## PILOT3_SPXC_DEEP_UNDERWRITING_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_SPXC_DEEP_UNDERWRITING_001.md`

SPXC's deep underwriting, following its triage-stage promotion, returned
`BLOCKED_BY_MATERIAL_UNCERTAINTY`.

**What survived and strengthened:** reconstructing organic growth and
margins across four quarters (Q3 2025 through Q2 2026), not one, found a
real, accelerating HVAC organic-growth trend (9.0%->9.6%->18.9%)
corroborated by a $919M backlog (+59% organically YoY) explicitly
attributed by management to data-center demand; a well-quantified secular
driver (2026 data-center revenue guide raised from $350M to $430M, +115%
YoY, full-production capacity target raised to $1.1B); a durable,
three-consecutive-quarter Detection & Measurement margin-expansion trend
(25.2%->27.0%->28.9%) that has offset HVAC's pressure at the consolidated
EBITDA-margin level (which has stayed roughly stable, 21.5%-23.0%, rather
than declining); an immediately accretive, high-margin (mid-40s% EBITDA
margin) Neptronic acquisition contributing $0.05-0.06 EPS in five months
of 2026 ownership; FCF that doubled YoY despite (not because of) a large
working-capital investment funding growth; and 1.4x pro forma leverage,
below management's own 1.5-2.5x target floor.

**What remained unresolved:** reconstructing the HVAC margin trend across
the same four quarters found it worsening for two consecutive quarters
(+50bps, then -40bps, then -260bps), not troughing -- the opposite
direction from management's "Q4 better than Q3" claim, which is
directional, not yet evidenced. Management's own guidance raise was
confirmed to NOT assume HVAC margin recovery (a credibility-supporting,
conservative posture), but this also means no company-quantified recovery
timeline exists to test against. The triage-stage finding of an
unexplained five-to-six-week price decline back to the post-earnings
trough was not resolved by this deeper review either -- no new negative
catalyst was found, but none was ruled out.

**Why `BLOCKED_BY_MATERIAL_UNCERTAINTY` rather than a clean call:** real,
now multi-quarter-confirmed business quality argues against
`NO_DEMONSTRATED_EDGE`; a worsening (not troughing) margin trend and an
unexplained price decline, per the record's own governing instruction not
to assume the selloff itself creates edge, argue against
`ADVANCE_TO_FINAL_CAPITAL_COMPARISON`. Both open questions have a
specific, dated, near-term resolution point (Q3 2026 earnings, expected
~late October) rather than requiring new methodology.

**Valuation note:** a fresh, Gate-B-certified price ($191.73, 2026-09-11)
was obtained after the U.S. market's close -- a genuine improvement over
the triage record's checkpoint, which had to rely on the prior completed
session because the market was still open at that record's preparation
time. The price moved modestly (+2.6%) and did not change the record's
scenario or return-range conclusions.

**Process note:** the work order arrived truncated (cut off mid-sentence in
its balance-sheet-flexibility instruction, before any scenario framework,
return range, disposition menu, or stop condition was given). It was
completed using the template established for AVGO, MDB, and DOCU deep
underwriting; flagged in the record for correction if different scope was
intended.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, DOCU `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SOLS
`EVENT_DRIVEN_HOLD`, PCG `SURFACE_WITH_EVIDENCE_GAP`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `NO_DEMONSTRATED_EDGE`, SMH
`REFERENCE_PEER_TAPE`, AAPL `EVIDENCE_GAP`, JPM `CALENDAR_HOLD`, NVDA
`REFERENCE_ONLY`.

**Explicitly not done:** no Stage 7 comparison, no Stage 8 decision, no
capital allocated, no triage of SOLS/PCG, no Batch 003.

---

## PILOT3_PCG_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_PCG_PRIMARY_EVIDENCE_TRIAGE_001.md`

PCG's primary-evidence triage returned `NO_DEMONSTRATED_EDGE`. The
discovery-stage question -- is the market over-penalizing wildfire and
financing uncertainty despite improving earnings, reduced borrowing needs,
and a potentially value-relevant strategic review -- was tested against
primary evidence with an explicit instruction not to minimize tail risk.

**What was confirmed:** real core-earnings growth (Q2 2026 core EPS +29%
YoY, GAAP EPS +37.5% YoY), reaffirmed FY2026 guidance, ~$2B lower 2027
borrowing need, and no anticipated equity issuance through 2030.

**What was not corroborated:** the strategic review, examined directly per
the instruction not to infer undisclosed options, discloses no specific
value-creating structural alternative on any source reviewed -- only a
capital-plan deferral and a withdrawn multi-year outlook. The deferred
2027 capex was found to be growth-oriented (housing and renewable-energy
interconnection work), not discretionary, tempering the "value-preserving"
reading.

**The central, load-bearing finding:** the wildfire-liability framework,
examined without minimizing tail risk, is live and already
partially-materializing rather than a market-overweighted hypothetical.
PG&E's own 10-Q discloses a $78M accelerated Wildfire Fund amortization
charge in Q1 2026 driven specifically by a competitor's loss (SCE's $1.3
billion Eaton-fire-related loss) -- direct, primary evidence of a
cross-utility contagion mechanism within the shared AB 1054 Wildfire Fund
pool. Separately, at least $699M in recorded wildfire-related regulatory-
recovery receivables (Dixie Fire, Mosquito Fire) remain subject to CPUC
prudency-standard disallowance risk. California's SB 492, the legislative
reform PG&E had been counting on, was found (via well-corroborated
secondary reporting) to have preserved insurer subrogation and strict
liability -- leaving the core legal exposure that makes wildfire liability
severe for California utilities intact.

**Market reaction, checked directly rather than assumed:** the stock fell
roughly 28% peak-to-trough around the September 2 announcement, partially
rebounded, then gave back most of that rebound over the following week --
remaining ~25% below its pre-decline level at the latest completed
session. This persistent, non-reversing pattern was read as evidence
against a knee-jerk overreaction, not treated as proof of edge in either
direction.

**Valuation:** a Gate-B-certified fresh price ($13.80, 2026-09-11)
implies roughly 8x forward P/E on FY2026/FY2027 core EPS guidance --
a deep discount to typical regulated-utility multiples, read as consistent
with a durable, evidence-grounded discount rather than an exploitable
temporary mispricing.

**Disposition rationale:** the tested variant's growth/financing
components survived, but its strategic-review and wildfire-liability
components did not -- this is a rejection of the specific tested variant,
not a permanent judgment that PG&E can never present an investable case.
Named falsifiers (a concretely value-creating strategic-review outcome, or
a durable legislative liability-reform fix) are recorded as the path to
revisiting this, not a new methodology.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, DOCU `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SPXC
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, SOLS `EVENT_DRIVEN_HOLD`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `NO_DEMONSTRATED_EDGE`, SMH
`REFERENCE_PEER_TAPE`, AAPL `EVIDENCE_GAP`, JPM `CALENDAR_HOLD` (not
advanced ahead of the September 16 FOMC decision), NVDA `REFERENCE_ONLY`.

**Explicitly not done:** no deep underwriting of PCG, no triage of SOLS,
no advance of JPM, no Stage 7 or Stage 8, no capital allocated, no
Batch 003.

---

## PILOT3_SOLS_POST_MERGER_TRIAGE_RESULT (2026-09-11)

**Record:** `docs/pilot3/PILOT3_SOLS_POST_MERGER_PRIMARY_EVIDENCE_TRIAGE_001.md`

SOLS's post-merger primary-evidence triage returned
`PROMOTE_TO_DEEP_UNDERWRITING`, resolving `EVENT_DRIVEN_HOLD` now that the
proposed Element Solutions merger has been mutually terminated (no fee
owed by either party) alongside a first-ever $500M buyback authorization
and reaffirmed FY2026 guidance.

**Corroborating findings:** Q2 2026 organic growth was broad-based across
every segment (Nuclear +27%, Healthcare Packaging +24%, Electronic
Materials +15%, Refrigerants +13%), not a single hot-segment story;
guidance was raised meaningfully at Q2 earnings and reaffirmed at
termination; net leverage is low (1.3x) with real balance-sheet capacity;
and the HFO/refrigerant IP position is real and currently monetizing, not
merely narrative -- a key European patent (HFO-1234yf process) was upheld
against multiple challengers, and a licensing relationship with Hudson
Technologies generates real revenue from the patent estate. Market
reaction to the termination, checked directly (+12.8% the next session,
consistent with a reported ~15% after-hours pop), has held for roughly two
weeks rather than reversing -- a materially different, more durable
pattern than this pilot found for PCG.

**Unresolved, named for deep underwriting:** adjusted EBITDA margin fell
218bps YoY even as revenue grew 11% and guidance was raised twice, with no
management explanation found in evidence reviewed -- a real, unexplained
profitability tension, not papered over. Separately, the current price
(~$61.55) remains roughly 28% below the pre-merger-announcement level
(~$85) even after the positive resolution; no evidence gathered explains
whether this reflects unrecovered standalone value or a justified
re-rating. The company's very short standalone operating history (a
recent Honeywell spinoff) limits how much trend-reconstruction this
triage could perform.

**Why `PROMOTE_TO_DEEP_UNDERWRITING` rather than a more cautious call:** no
primary evidence found directly refutes the candidate variant (unlike this
pilot's PATH or PCG findings) -- the open questions are unresolved, not
negative findings, and are specifically named as the deep-underwriting
focus rather than resolved by inference, consistent with how AVGO, MDB,
DOCU, and SPXC were promoted at triage with comparable named open
questions.

**Batch 002/001 controls unchanged:** PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, DOCU `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SPXC
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, PCG `NO_DEMONSTRATED_EDGE`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`, XOM `NO_DEMONSTRATED_EDGE`, SMH
`REFERENCE_PEER_TAPE`, AAPL `EVIDENCE_GAP`, JPM `CALENDAR_HOLD` (not
advanced ahead of the September 16 FOMC decision), NVDA `REFERENCE_ONLY`.

**Explicitly not done:** no deep underwriting of SOLS, no advance of JPM,
no Stage 7 or Stage 8, no capital allocated, no Batch 003.

## PILOT3_SOLS_INTEGRITY_CHECK_AND_DEEP_UNDERWRITING_RESULT (2026-09-11)

**Integrity check (prerequisite):** a work order asserted the committed
SOLS triage record attributed HSR merger-filing-fee responsibility to
PG&E. Direct re-verification of both the committed record's own text and
the primary source (termination agreement exhibit `tm2620579d9_ex10-1.htm`)
found this premise did not match the record: PG&E is not named anywhere
in it; the clause reads "Parent remains responsible for all filing
fees..."; "Parent" is defined in the agreement as Solstice Advanced
Materials Inc. itself. No correction was required; an addendum
documenting the check (not a rewrite) was appended to
`PILOT3_SOLS_POST_MERGER_PRIMARY_EVIDENCE_TRIAGE_001.md`. No effect on
the triage disposition. Deep underwriting proceeded per the work order's
own instruction that an immaterial/non-existent correction does not
block continuation.

**Deep underwriting result:** `pilot3/PILOT3_SOLS_DEEP_UNDERWRITING_001.md`
closed **`BLOCKED_BY_MATERIAL_UNCERTAINTY`**.

Reconstructed standalone operating history using SEC XBRL company facts
plus the FY2025 10-K and Q1/Q2 2026 10-Qs, explicitly separating pre-spin
carve-out results (Honeywell segment, spin-off completed October 30,
2025, confirmed primary source) from post-spin standalone results.
Revenue growth genuinely accelerated versus Solstice's own FY2023–FY2025
trend (~3%/year) to ~10–11%/year standalone in 2026, corroborated by
growing backlog (RevenueRemainingPerformanceObligation $2.8B→$3.2B over
three quarters).

The margin question — named as the central open item at triage — was
resolved with materially more precision and less favorably than the
218bps headline suggested. The earnings release's own "218bps decline"
compared 2026 actual Adjusted EBITDA against a non-GAAP "Adjusted
Standalone EBITDA" pro forma base for Q2 2025 ($283M); verified against
the audited 10-Q segment footnote's actual as-reported comparative figure
($304M), the real decline was 417bps (Q2) and 508bps (Q1) — roughly
double. Segment-level decomposition (newly obtained from each 10-Q's
segment reconciliation note) found this driven by two separable forces:
(1) rising standalone corporate/unallocated costs, real but decelerating
sharply (+168bps drag Q1 → +25bps Q2, consistent with anniversarying the
spin-off) and (2) Refrigerants & Applied Solutions segment margin
compression, real and **worsening** (−527bps Q1 → −648bps Q2) — sitting
directly inside the segment carrying the growth and HFO/IP narrative,
with no disclosed cause. A new, material interest-expense burden
($2–3M/quarter pre-spin to $23–53M post-spin, from the ~$2B debt issued
at separation) and a higher GAAP-basis capex growth rate (+54% per the
cash-flow statement vs. the company's own +35% non-GAAP figure) were also
identified and reconciled precisely. Zero shares repurchased under the
$500M buyback authorization was reconfirmed via three independent sources
(10-Q equity rollforward, XBRL `TreasuryStockSharesAcquired`=0, absence
of any subsequent 8-K). The HFO/IP position was reconfirmed as real and
reasonably durable (primary-sourced "at least into the mid-2030s"
horizon; one patent challenge already defeated at the EPO), and a
previously undisclosed $4.685B bridge-financing commitment for the
abandoned Element Solutions deal was found to have been fully removed by
the termination, with no residual obligation.

A reverse-engineered priced-in test (not peer-multiple-based) found
FY2026 guidance requires H2 2026 Adjusted EBITDA of only ~$496–516M —
essentially flat to H1's $539M — meaning current guidance does not
require the RAS margin problem to be fixed by year-end, only that it not
worsen further. Since RAS margin worsened, not improved, across the only
two comparable quarters that exist, this is treated as a live, unresolved
test rather than a formality.

Because growth, backlog, and IP evidence remained real and uncontradicted
throughout, `NO_DEMONSTRATED_EDGE` was not supported. Because the
specific, named, load-bearing uncertainty from triage resolved less
favorably (not favorably) under primary-source scrutiny,
`ADVANCE_TO_FINAL_CAPITAL_COMPARISON` was not supported either. The most
direct, evidence-gatherable revisit trigger is Q3 2026 RAS segment margin
(10-Q due ~late October/early November 2026).

**Confirmed unchanged:** PATH/MDB/PCG `NO_DEMONSTRATED_EDGE`; DOCU/SPXC
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
XOM `NO_DEMONSTRATED_EDGE`; AAPL `EVIDENCE_GAP`; JPM `CALENDAR_HOLD` (not
advanced ahead of the September 16 FOMC decision); SMH
`REFERENCE_PEER_TAPE`; NVDA `REFERENCE_ONLY`. No Batch 003 candidate
registered. No Stage 7, no Stage 8, no capital allocated, no control-layer
or facade change.

**Capital status: NO REAL PORTFOLIO ACTION.**

## PILOT3_NARROW_DISCOVERY_FIX_AND_BATCH003_CHARTER_RESULT (2026-09-12)

**Red Team verdict:** `CONTINUE_WITH_NARROW_FIX`. Pilot 3 discovery is
producing plausible, falsifiable ideas and underwriting is successfully
rejecting false positives; zero Stage 7 survivors across twelve Batch
001/002 candidates is not treated as a failure by itself. Two specific
weaknesses are named: discovery over-samples post-event/familiar-theme
setups, and some candidates receive substantial work before the original
hook is cheaply disproven. No other finding is adopted as a process
change.

**Decision `PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`:** when a discovery
hook depends materially on acceleration, margin change, bookings/RPO,
segment/product mix, FCF improvement, or new-product penetration, triage
must first reconstruct that metric across the last 4 reporting periods
(sequential and YoY trend, one mix line if relevant) before the full
candidate variant is written. If the hook has already peaked, reversed,
or flattened materially, triage must stop or block unless an independent
source of edge remains. No historical-data engine is built — a
human-readable, four-period check using the same primary-source tools
already used throughout this pilot.

**Decision `PILOT3_PRICED_IN_ONE_LINER`:** before any candidate advances
from triage to deep underwriting, triage must state: "for this to be
mispriced, the market must currently be assuming ______." If this cannot
be stated credibly from evidence gathered, no clear variant has been
demonstrated, and the candidate does not advance on that basis alone. No
pricing engine is built — a one-sentence variant-clarity gate.

**Both fixes are prospective only, beginning with Batch 003.** No prior
Pilot 3 record (AVGO, PATH, MDB, SPXC, SOLS, PCG, DOCU, XOM, AAPL, JPM,
SMH, NVDA, or the underlying `PILOT3_RECORD_001.md`) is modified,
annotated, or reopened.

**Batch 003 charter recorded** (`pilot3/PILOT3_BATCH_003_CHARTER.md`):
targets a different discovery pond — capital-allocation/balance-sheet
change, neglected/lower-attention securities, competitor/industry
read-through, and quiet regulatory/structural change — explicitly
avoiding post-earnings selloffs, mega-cap thematic names, "beat and raise
but stock fell," one-line cheapness, and generic AI exposure. Target size
4–6 candidates, quality over quantity, no market-cap rule. A required
per-candidate discovery-record template is defined (source, hook,
economic rationale, 4-period reconstruction where applicable, priced-in
one-liner, tentative variant, market-could-be-right alternative, cheapest
falsification test, evidence gap, initial disposition —
`SURFACE_FOR_TRIAGE` / `SURFACE_WITH_EVIDENCE_GAP` / `IGNORE` only, no
funding or ranking). Cheap-falsification discipline is restated as a
general principle (kill weak hooks sooner; deep-underwrite only
survivors). A false-negative-awareness learning note is recorded for a
future Loop C / outcome-learning process (not built now). Shadow
sentiment is restated as unchanged: recorded separately if observed,
never used to promote/block/fund, no sentiment score.

**Current interpretation recorded:** Pilot 3 is demonstrating strong
false-positive control but has not yet demonstrated repeatable discovery
of missed investable alpha. Batch 003 tests whether a more diverse,
under-the-surface discovery source can produce a candidate that survives
to Stage 7 without weakening underwriting standards — the underwriting
bar itself is unchanged by this charter.

**Batch 003 remains unpopulated** — no candidate created, sourced, or
registered by this record. No prior record modified. No scoring, ranking,
sentiment-promotion, or new discovery/pricing engine built. No Stage 7,
no Stage 8, no advance of JPM or AAPL, no change to the control layer,
facade, or core architecture.

**Capital status: NO REAL PORTFOLIO ACTION.**

## PILOT3_BATCH003_REGISTRATION_AND_NHP_TRIAGE_RESULT (2026-09-12)

**Batch 003 registered** (`pilot3/PILOT3_BATCH_003_REGISTRATION.md`),
source `GROK_SCOUT_UNDER_SURFACE_DISCOVERY`, as-of 2026-09-12: NHP
(National Healthcare Properties, Inc., CIK 0001561032, Nasdaq Global
Market MIC XNMS), UCB (United Community Banks, Inc., CIK 0000857855,
NYSE MIC XNYS), NNBR (NN, Inc., CIK 0000918541, Nasdaq MIC XNGS), SAIA
(Saia, Inc., CIK 0001177702, Nasdaq MIC XNGS), and TCS (Tecsys Inc.,
Toronto Stock Exchange, MIC XTSE — not SEC-registered, not researched
beyond identity per instruction). Two real ticker collisions were
identified and resolved explicitly rather than assumed: UCB also names a
Belgian pharmaceutical company (UCB SA, Euronext Brussels) and a stale
former-ticker artifact (UCBI, Nasdaq); TCS also names Tata Consultancy
Services (India) and, on certain German venues, Axon Enterprise. Scout's
characterization of NHP as the "best research-use-of-time candidate" was
explicitly disregarded as a ranking input. Only NHP was triaged in this
record; UCB, NNBR, SAIA, and TCS remain registered at
`SURFACE_FOR_TRIAGE` only.

**NHP primary-evidence triage** (`pilot3/PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`)
— the first record governed by the two Batch 003 narrow fixes — returned
**`NO_DEMONSTRATED_EDGE`**. The discovery hook (OMF portfolio-sale
proceeds reducing debt beyond the sold properties' own collateral, plus
a full preferred-stock redemption, improving the capital stack for
common shareholders) was tested via the mandatory `PILOT3_HOOK_
RECONSTRUCTION_AT_TRIAGE` 4/5-period reconstruction of FFO/share,
Normalized FFO/share, and net leverage across Q2 2025 through Q2 2026.
The reconstruction found net leverage improved sharply (9.6x to 4.9x)
and Normalized FFO per diluted share fell 18.2% year-over-year, both in
the same quarter (Q2 2026) — before either the OMF sale or the preferred
redemptions had actually occurred. Independent XBRL verification found
the true driver: a ~156%-dilutive common equity offering (44,275,000
Class A shares, ~$531.3M gross proceeds, closed April 23, 2026), not the
asset sale or preferred redemption, funded the revolver paydown and
produced the leverage improvement, while mechanically explaining the
per-share FFO decline. The `PILOT3_PRICED_IN_ONE_LINER` gate was applied
and could be stated credibly, but the stated one-liner's premise was not
supported by the evidence gathered. Direct completed-session price
review found the market's reaction to the September 10 first-tranche
closing was negative (-1.87% over two sessions), not positive, and that
the bulk of the leverage-improvement news had already been rewarded in
an August 5-7 rally (+11.2%) five weeks before Scout's discovery date.
Closed `NO_DEMONSTRATED_EDGE`, framed as a successful discovery-system
outcome: the narrow fixes killed a plausible-sounding hook cheaply, on
primary evidence, before a full deep-underwriting variant was written
around it.

**Confirmed unchanged:** PATH/MDB/XOM/PCG `NO_DEMONSTRATED_EDGE`;
DOCU/SPXC/SOLS `BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AAPL `EVIDENCE_GAP`; JPM
`CALENDAR_HOLD` (not advanced); SMH `REFERENCE_PEER_TAPE`; NVDA
`REFERENCE_ONLY`. No deep underwriting of NHP. No triage of UCB, NNBR,
SAIA, or TCS. No research of TCS. No Stage 7, no Stage 8, no capital
allocated, no control-layer or facade change.

**Capital status: NO REAL PORTFOLIO ACTION.**

## PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-14)

**UCB primary-evidence triage** (`pilot3/PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_001.md`)
— the second record governed by the two Batch 003 narrow fixes — returned
**`NO_DEMONSTRATED_EDGE`**. Canonical identity re-confirmed (United
Community Banks, Inc., NYSE, MIC XNYS, CIK 0000857855); the prior
collision resolution against UCB SA (Belgian pharmaceutical) and the
stale UCBI ticker artifact held with no new ambiguity.

The discovery hook (Navitas exit, HTM-to-AFS securities repositioning,
debt paydown, and expanded buyback collectively improving earnings
quality and risk profile more than the market credits) was tested via
`PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`: a clean 4-quarter reconstruction
(Q3 2025-Q2 2026) of NIM, loan yield, deposit cost, CET1, tangible book
value per share, operating EPS, and operating ROTCE, followed by
management's own EPS restructuring bridge from the September 8 investor
presentation. The bridge showed the Navitas-exit (-$0.07/quarter) and
securities-reset reinvestment (+$0.06/quarter) pieces -- the two pieces
that are actually Scout's hook -- net to roughly zero (-$0.01/quarter),
failing the cheapest-falsification test explicitly specified in the work
order. The touted overall EPS improvement ($0.74 to $0.78 baseline) was
driven instead by an unrelated small acquisition (Peach State
Bancshares, +$0.02/quarter, ~2-3% of UCB's balance sheet, explicitly
isolated per instruction) and unguided future "core bank growth"
(+$0.02-0.04/quarter, management-dependent, not contractual) -- neither
named in Scout's hook.

The tangible-book-value bridge found a real, immediate ~$1.95/share
(~8.4%) TBV hit (Q2 2026 $23.31 to Q3 2026E pro forma ~$21.36), erasing
roughly three quarters of the steady TBV growth shown in the
reconstruction; no company-disclosed earnback period exists, and this
record's own coarse, explicitly-labeled illustration (~1 year, using
total company earnings, not the restructuring's own roughly-zero
contribution) is not treated as proof the transaction pays for its own
damage. The credit-risk-reduction half of the hook was well corroborated
by primary evidence: Navitas accounted for roughly 50% of total net
charge-offs despite being a minority of the loan book, and a ~$38
million ALLL release accompanied the sale.

Applying `PILOT3_PRICED_IN_ONE_LINER`, a credible one-liner could be
stated but relied on the same unguided growth assumption the bridge
could not verify. Direct completed-session price review found the
market's reaction to the September 8 announcement was flat-to-mildly-
negative (-0.98% from the pre-announcement close through the latest
completed session), not a rally -- no evidence the market is
under-crediting an improvement. A reverse-engineered valuation
checkpoint (~1.51x P/TBV pre-restructuring, ~1.65x pro forma -- mechanically
richer, not cheaper, immediately after the TBV cut; ~11-12x P/E; ~2.8%
dividend yield; ~13% ROTCE; 13%+ CET1 throughout) was unremarkable for a
well-capitalized regional bank. A same-day Gate B bind correctly
returned STALE (market open at decision time); per instruction this was
not forced, and the last confirmed completed-session close ($35.29,
2026-09-11) was used instead with the limitation stated plainly.

Closed `NO_DEMONSTRATED_EDGE`, framed as a second successful
discovery-system outcome for the narrow-fix discipline: the hook
reconstruction and priced-in one-liner tested a plausible, well-
evidenced, multi-part restructuring hook against management's own
numbers and found the specific "earnings quality" claim does not survive
its own bridge, before any deep-underwriting variant was built around
it.

**Confirmed unchanged:** NHP `NO_DEMONSTRATED_EDGE`; NNBR, SAIA, TCS
remain registered only (`SURFACE_FOR_TRIAGE`), not triaged; PATH/MDB/XOM/PCG
`NO_DEMONSTRATED_EDGE`; DOCU/SPXC/SOLS `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`; AAPL `EVIDENCE_GAP`; JPM
`CALENDAR_HOLD` (not advanced); SMH `REFERENCE_PEER_TAPE`; NVDA
`REFERENCE_ONLY`. No deep underwriting of UCB. No triage of NNBR, SAIA,
or TCS. No Batch 004. No Stage 7, no Stage 8, no capital allocated, no
control-layer or facade change.

**Capital status: NO REAL PORTFOLIO ACTION.**
