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
