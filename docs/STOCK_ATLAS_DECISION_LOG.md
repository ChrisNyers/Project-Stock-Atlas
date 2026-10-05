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

## PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-14)

**NNBR primary-evidence triage** (`pilot3/PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_001.md`)
— the third record governed by the two Batch 003 narrow fixes — returned
**`PROMOTE_TO_DEEP_UNDERWRITING`**, the first Batch 003 candidate to
survive triage. Canonical identity confirmed without ambiguity (NN, Inc.,
Nasdaq Global Select, MIC XNGS, CIK 0000918541).

Applying `PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`, reconstructed revenue,
Adjusted EBITDA, EBITDA margin, new-business-wins guidance, capex, and
Data Center & Electric Grid revenue across five reporting points (Q3
2025 through the September 9, 2026 investor-conference update). Unlike
NHP and UCB, the reconstruction did not kill the operating thesis: it
strengthened it. Revenue growth accelerated for three consecutive
quarters (-8.5% to -1.7% to +12.1% to +19.3% YoY); Adjusted EBITDA margin
expanded to 13.9% in Q2 2026; new-business-wins guidance was raised at
every quarterly update over a year ($70-80M initial to $80-90M to
$80-100M to $90-110M, midpoint now $100M); Data Center & Electric Grid
revenue (~$80M TTM) and ~60 new CNC machine centers at the Wuxi plant
for AI data-center supply chains were both confirmed as fact from the
primary investor presentation; and the auto/non-auto sales mix shift
(65%/35% in 2023 to 40%/60% by Q2 2026) was confirmed as already
substantially executed, not merely underway -- the strongest single
piece of evidence that faster-growing end markets are producing net
company growth rather than merely offsetting legacy weakness.

The refinancing/preferred-cleanup half of the hook did not reconstruct
as cleanly. A $75.0 million common-stock private placement (24,509,804
shares at $3.06/share, closed July 1-2, 2026) funded a Series D
Preferred Stock redemption/exchange (9,850 shares exchanged for
5,500,000 new common shares, closed August 5, 2026, with the Q2 2026
earnings release separately stating "approximately $89 million of the
preferred stock" was paid off). The record could not reconcile the
9,850-share figure against the pre-transaction Series D balance
(65,000 shares outstanding, $122.1 million carrying value including
$75.5 million of accumulated/deemed dividends, at a 14.5% compounding
coupon after step-ups from an initial 10%) and the "$89 million paid
off" headline -- implying, if the 9,850-share figure is the complete
picture, that roughly 85% of the Series D overhang (by share count) may
remain outstanding and still compounding. Combined common shares
outstanding increased by roughly 57% (52.574 million pre-transaction to
approximately 82.6 million pro forma) from the private placement and
preferred exchange together.

Applying `PILOT3_PRICED_IN_ONE_LINER`, a credible one-liner was stated
and -- unlike NHP and UCB -- was not contradicted by the evidence
gathered: the operating momentum is real and the capital-structure
question remains genuinely open rather than resolved unfavorably. A
same-day Gate B bind correctly returned STALE (market open at decision
time) and was not forced; the last confirmed completed-session close
($3.58, 2026-09-11) was used for a coarse, explicitly-labeled valuation
checkpoint (~6x EV/EBITDA, ~$296M market cap post-dilution). Direct
completed-session price review found a strong (+24% over two weeks)
positive reaction to the August 5 news that has since partially reversed
(-13% off the peak), with no fresh rally on the September 9
investor-conference update -- evidence the market has already engaged
with, not ignored, the story, without proving it has been fully priced.

The unresolved Series D reconciliation was classified `THESIS_BLOCKING_
UNCERTAINTY`, not `POTENTIAL_SOURCE_OF_EDGE`: the entire promotion thesis
depends on knowing how much of the preferred's dilutive, compounding
claim actually remains, since continued heavy dilution and coupon
accrual could absorb most or all of the confirmed operating improvement's
per-share benefit. Closed `PROMOTE_TO_DEEP_UNDERWRITING`, with the
preferred-structure reconciliation named as the central deep-underwriting
task.

**Confirmed unchanged:** NHP `NO_DEMONSTRATED_EDGE`; UCB
`NO_DEMONSTRATED_EDGE`; SAIA and TCS remain registered only
(`SURFACE_FOR_TRIAGE`), not triaged; PATH/MDB/XOM/PCG
`NO_DEMONSTRATED_EDGE`; DOCU/SPXC/SOLS `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`; AAPL `EVIDENCE_GAP`; JPM
`CALENDAR_HOLD` (not advanced); SMH `REFERENCE_PEER_TAPE`; NVDA
`REFERENCE_ONLY`. No deep underwriting of NNBR. No triage of SAIA or
TCS. No Batch 004. No Stage 7, no Stage 8, no capital allocated, no
control-layer or facade change.

**Capital status: NO REAL PORTFOLIO ACTION.**

## PILOT3_NNBR_SERIES_D_RECONCILIATION_RESULT (2026-09-15)

**Resolved the `THESIS_BLOCKING_UNCERTAINTY` identified in the committed
NNBR triage record** (`pilot3/PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_001.md`),
by addendum to that same record, per the append-only historical-
integrity discipline established for SOLS.

**Primary evidence located:** the actual Series D Preferred Stock
Exchange Agreement, filed as an exhibit to the Q2 2026 10-Q
(`nn-exchangeagreement.htm`), rather than relying on press-release
shorthand. Cross-checked independently against NN, Inc.'s special-
meeting proxy statement (DEF 14A, filed 2026-08-28), which discloses
82,580,864 total shares outstanding as of August 5, 2026.

**Reconciliation, resolved:** pre-transaction Series D balance was
65,000 shares (Holder: NHTV Nevada Holdings LP). The August 5, 2026
transaction comprised two concurrent, conditioned pieces: (1) an
Exchange of 9,850 shares for 5,500,000 new common shares (previously
known), and (2) a separate, previously unlocated cash Redemption of
36,750 additional shares exercised under the original Certificate of
Designation. Together, 46,600 of 65,000 shares (71.7%) were retired,
reconciling cleanly (within ~$1.5M) to the earnings release's "~$89
million paid off" headline using this record's own ~$1,878.5/share
average carrying-value estimate. The remaining 18,400 shares (~28.3%,
~$34.6 million carrying value) are confirmed to carry a temporarily
reduced 10.0% dividend rate through August 2027 (Exchange Agreement
Section 5.3), reverting to 15.0%/17.0% thereafter with a further 2.5%/
year step-up from March 2028, and a confirmed $5.0 million discount to
the aggregate redemption price (Section 5.4) if the Company achieves a
"Final Redemption" of the full remaining balance by December 31, 2026 --
the discount the original triage record's governing work order asked to
be verified. No shareholder vote or Nasdaq approval was required for the
transaction, and the proxy statement explicitly disclaims any definitive
arrangement to issue its proposed additional authorized shares for
Series D purposes -- a speculative hypothesis in this record's own
diligence process that is accordingly retracted.

**Common-equity economics:** confirmed ~57.1% dilution from the private
placement and exchange combined (30,009,804 new shares against a
52,574,000-share pre-transaction base), reconciling to the proxy's own
82,580,864 share count within ordinary RSU-activity rounding. The
exchange ratio (9,850 preferred shares for 5,500,000 common shares)
values each preferred share at or above its own carrying value (roughly
$1,707-2,176/share against a ~$1,878.5/share carrying-value estimate,
depending on reference price) -- common holders did not receive a
discount in the exchange itself. The transaction is characterized as a
genuine de-risking trade (an escalating, compounding, senior-to-common
claim substantially retired in exchange for fixed, already-issued,
pari passu common dilution), not a cheap one, per the work order's
explicit instruction not to answer based on leverage improvement alone.

**Uncertainty classification:** `RESOLVED_SUPPORTS_THESIS` -- the
resolved facts (71.7% retired, not the feared ~15%; a real, dated
discount incentive for full cleanup; no hidden additional dilution) are
more favorable than the unresolved ambiguity implied, though the
transaction was not without real cost to common.

**Progression decision:** `PROCEED_TO_DEEP_UNDERWRITING`. Deep
underwriting itself was not performed by this record; the resolved
Series D economics, the confirmed dilution, and the exchange-ratio
finding are named as load-bearing inputs for that future work order.

**Confirmed unchanged:** NHP and UCB remain `NO_DEMONSTRATED_EDGE`; SAIA
and TCS remain registered only (`SURFACE_FOR_TRIAGE`), not triaged;
PATH/MDB/XOM/PCG `NO_DEMONSTRATED_EDGE`; DOCU/SPXC/SOLS
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AAPL `EVIDENCE_GAP`; JPM `CALENDAR_HOLD` (not advanced); SMH
`REFERENCE_PEER_TAPE`; NVDA `REFERENCE_ONLY`. No deep underwriting of
NNBR performed. No triage of SAIA or TCS. No Batch 004.

**Capital status: NO REAL PORTFOLIO ACTION.**

## PILOT3_GOVERNANCE_CONSOLIDATION_RESULT (2026-09-15)

**Consolidated, not expanded, governance** into the existing Master
Project Plan via a new "Governance Classification" section placed
immediately after the Governing Mission. No new governance document was
created; no new architecture was introduced; nothing in this
consolidation changes human capital allocation authority (Stage 7 emits
no `PortfolioAction`; Stage 8 remains human) or any completed Pilot 1,
Pilot 2, or Pilot 3 record.

**Four previously accepted governance rules consolidated into Permanent
Governance, in full, for the first time as standing, named rules** (they
had been applied in practice -- e.g., "preserve provenance, remove
privilege" since Pilot 3's inception, Scout's ranking claims already
being disregarded in the NHP and UCB triage records -- but not
previously stated as a consolidated, named set):

- **Discovery Source Neutrality** -- no discovery source, including Grok
  Scout or Agent World, may own Atlas's workflow, canonical state,
  validation standards, ranking, sizing, or capital-allocation authority;
  every source submits into the same validation process; Atlas must
  remain fully operable if any single source disappears; core test:
  would a proposed change still improve Atlas if that source vanished
  tomorrow?
- **Mandatory Scout Feedback Governance** -- learning flows one
  direction only (Scout surfaces, Atlas tests, Atlas's findings improve
  Scout's future surfacing); Atlas never relaxes its validation standards
  to accommodate Scout; Scout feedback should emphasize change over
  names, tentative expectations gaps, second-order/non-price discovery,
  cheapest falsification, the strongest contradictory fact, why the
  market might be wrong, and lessons from prior false positives; Scout
  may not rank, size, allocate, self-promote, or alter Atlas's standards.
- **One-New-Information-Family-Per-Pilot Guardrail** -- no more than one
  new information family introduced per pilot by default, gated by
  whether it surfaces otherwise-missed opportunities, improves timing or
  decision quality, and is worth its added complexity.
- **Experiment-First Rule for new discovery/information lanes** -- every
  new lane begins as an experiment tested for unique discovery value,
  timing value, variant-quality improvement, risk-control improvement,
  and false-positive/false-negative impact, and is retained only if it
  materially improves decision quality relative to its complexity.

**Governance Classification structure added** to the Master Project
Plan, cross-referencing rather than duplicating existing language:

- **Permanent Governance:** human capital allocation authority
  (Architecture, frozen), fail-closed evidence discipline (Gate B /
  control-layer records), provenance over privilege (Pilot 3, since
  inception), immutable frozen records, the live-alternatives/real-
  decision-time-data requirement (Live Capital section), plus the four
  rules above.
- **Pilot Controls (under test, not automatically permanent):** Pilot 3
  Hook Reconstruction at Triage and Priced-In One-Liner
  (`PILOT3_BATCH_003_CHARTER.md`), current shadow-sentiment treatment,
  batch-specific stop conditions.
- **Roadmap Hypotheses (unproven, evidence-gated, never binding until
  promoted):** forced-flow/source-ownership testing (cross-referencing
  the existing "Future Pilot Candidates" section), formal sentiment/news/
  trend testing, capital-cycle/capacity testing, credit-equity
  divergence, statistical/ML testing, late-Pilot-4 CX/Claude Design work
  (cross-referencing "Parked / Future Research").

**No new standalone governance document was created.** The consolidation
lives entirely within the existing Master Project Plan (a single new
section) and this single Decision Log entry -- not four separate entries
for the four rules, per instruction. No frozen Pilot 1, Pilot 2, or
completed Pilot 3 company record was modified.

**Capital status: NO REAL PORTFOLIO ACTION.**

## PILOT3_NNBR_DEEP_UNDERWRITING_RESULT (2026-09-14)

**Candidate:** NNBR — NN, Inc. (`PILOT3_NNBR_DEEP_UNDERWRITING_001.md`).
**Prior state:** `PROMOTE_TO_DEEP_UNDERWRITING`, Series D uncertainty
`RESOLVED_SUPPORTS_THESIS`, progression `PROCEED_TO_DEEP_UNDERWRITING`
(`PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_001.md` addendum).

**Result: `BLOCKED_BY_MATERIAL_UNCERTAINTY`.** Eight-quarter operating
reconstruction (Q3 2024–Q2 2026, primary-sourced earnings-release 8-Ks
and XBRL) confirmed and broadened the triage findings: three separately
guided growth programs — Data Center & Electric Grid (~$80M TTM, $120M
near-term goal), Defense & Electronics (~$60M TTM, $90M goal), Medical
Products (~$15M TTM, $40M goal) — combine to ~$155M TTM, ~30% of
revenue, versus the ~15-16% data-center-only estimate available at
triage. A newly reconstructed segment split (Power Solutions vs. Mobile
Solutions) found a ~5x FY2025 operating-margin gap (15.1% vs. 3.0%),
quantifying the mix shift as economically transformative rather than
merely descriptive. The resolved Series D trade was evaluated on
dilution-earnback terms, not leverage improvement alone: restoring
pre-dilution per-share Adjusted EBITDA (~$1.09/share) on the diluted
82.58M-share base requires TTM Adjusted EBITDA to rise from ~$57.3M to
~$90.0M (+~$32.7M, matching the ~57% dilution mathematically); a coarse,
labeled counterfactual estimated the retired 71.7% of Series D, left
compounding at 14.5%+, could plausibly have exceeded $150M within 3-4
years, supporting the transaction as a credible de-risking trade.

**The specific, named blocking uncertainty:** capex has not approached
the guided $35-40M annual run-rate in any of the eight quarters
reconstructed (H1 2026 annualizes to ~$17.1M), and free cash flow (this
record's own OCF-minus-capex calculation, disclosed as differing
somewhat from the company's own non-GAAP FCF figure) was positive in
only one of the last nine quarters reconstructed. This capacity/cash-
flow gap is the load-bearing precondition for converting the ~$90-110M
FY2026 win-pipeline guidance into the incremental EBITDA the dilution-
earnback math requires — not yet evidenced in actuals. Growth and a
favorable capital-structure resolution were both confirmed real and
explicitly not treated as sufficient on their own, per instruction.
Market-reaction evidence (no rally on the incrementally positive
September 9 disclosure) was found consistent with, not contradictory
to, this blocked disposition.

**No Stage 7 or Stage 8 action.** NHP, UCB remain `NO_DEMONSTRATED_EDGE`;
SAIA, TCS remain `SURFACE_FOR_TRIAGE`, not triaged; no Batch 004 started.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT3_SAIA_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-14)

**Candidate:** SAIA — Saia, Inc. (`PILOT3_SAIA_PRIMARY_EVIDENCE_TRIAGE_001.md`).
**Discovery type:** `READ_THROUGH` (Old Dominion Freight Line → Saia) —
the first Batch 003 candidate testing this pilot's core competitor-
read-through learning question directly.

**Result: `NO_DEMONSTRATED_EDGE`.** Scout's hook (ODFL's September 3,
2026 August LTL operating-statistics release signaling firmer industry
pricing, softening Saia's guided Q3 operating-ratio pressure) was tested
against primary evidence from both companies: Saia's Q2 2026 earnings
release, its issuer-filed earnings-call transcript (treated as primary
evidence per instruction), its own July/August 2026 shipment-and-tonnage
data (filed via 8-K the same calendar day as ODFL's release), four
prior quarters of both companies' operating metrics, and ODFL's own
four-quarter comparative trend.

**The cheapest-falsification test (run first, per instruction) found
no**, on four independent grounds: (1) Saia's own Q3 guidance — "around
100 basis points of sequential degradation," already better than its
own stated 150-200bps historical norm — was public on July 30, 2026,
over a month before the Scout hook; (2) Saia discloses its own monthly
volume data via SEC filing, filed the same day as ODFL's release,
making the read-through largely redundant for the volume question; (3)
ODFL's cited ex-fuel revenue/cwt (+4.8% August QTD) sat inside its own
stable, year-long 4.4%-5.5% range — not new information, and its
"August news" was more a volume-stabilization story (tons/day easing
from -10.7% to -0.9% over four quarters) than a pricing-acceleration
one; (4) the specific cost items most likely to determine Saia's actual
Q3 outcome — new-terminal drag ("low-90s" OR on 2023-2024 cohorts),
two stacked wage increases, and purchased-transportation costs up
47.3% YoY — are Saia-specific and structurally unrelated to ODFL's
pricing environment. The two companies' volume trajectories were found
to be moving in opposite directions for company-specific reasons (ODFL
deliberately shedding volume to hold price; Saia aggressively adding
network capacity and taking on heavier, lower-cwt-yield freight),
limiting quantitative transfer even though a qualitative industry
pricing-discipline signal is real and corroborated by Saia's own
contract-renewal (10.7%) and GRI (7.1%) data.

**Market-reaction evidence directly tested the read-through's practical
relevance**: on September 3, 2026 — when both companies released their
own data — Saia's stock rose (+4.2%, extending to +7.8% over two
sessions) while ODFL's did not, indicating the market's own repricing
traces to Saia's disclosed data, not to an ODFL-driven read-through.
Saia had separately fallen ~11% on its own July 30 earnings day despite
a headline year-over-year operating-ratio improvement, consistent with
the market weighing the same cost items this record identifies.

**Read-through classification: `READ_THROUGH_PARTIAL`** — a genuine
industry pricing-discipline signal exists but does not transfer with
the specificity Scout's hook required, a Pilot 3 learning observation,
not a permanent scoring field.

**No deep underwriting of SAIA.** NHP, UCB remain `NO_DEMONSTRATED_EDGE`;
NNBR remains `BLOCKED_BY_MATERIAL_UNCERTAINTY`; TCS remains
`SURFACE_FOR_TRIAGE`, not triaged or researched. No Batch 004 started.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT3_TCS_PRIMARY_EVIDENCE_TRIAGE_RESULT (2026-09-14)

**Candidate:** TCS — Tecsys Inc. (`PILOT3_TCS_PRIMARY_EVIDENCE_TRIAGE_001.md`).
**Discovery type:** `NEGLECTED / INSTALLED_BASE_EXPANSION`. Fifth and
final Batch 003 candidate — **Batch 003 discovery/triage is now
complete.**

**Result: `NO_DEMONSTRATED_EDGE`.** Every headline fact in Scout's hook
(total revenue ~C$50.0M, SaaS revenue ~C$22.7M, total SaaS growth ~18%,
Elite SaaS growth ~24%, ARR ~C$93.7M, RPO ~C$259.2M, Adjusted EBITDA
~C$6.9M, FY2027 Elite SaaS guidance raised to 21-23%, NCIB activity,
C$0.09 dividend) was verified precisely against primary sources
(Q1 FY2027 earnings release, interim financial statements and MD&A,
investor presentation, Note 7 remaining-performance-obligation
disclosure) — a materially different starting point than NHP, UCB, or
SAIA, whose hooks required significant reframing. The aggregate
installed-base-expansion mechanism strengthened under the mandatory
hook reconstruction: Elite SaaS ARR net retention reached 111% (LTM),
climbing from ~102% several quarters earlier, and Elite ARR growth
itself accelerated from ~18.6% to 24% YoY, masked in the blended
total-SaaS figure by shrinking non-Elite legacy attrition.

**Promotion failed on a different dimension than a broken hook.**
Scout's specifically named customer expansions (Prisma Health, UT
Southwestern, a cancer center) could not be corroborated in any primary
Tecsys disclosure reviewed. FY2027 guidance (Elite SaaS growth, total
SaaS growth, total revenue growth, and Adjusted EBITDA margin, all
raised) was announced the same day (September 10, 2026) as the hook's
underlying Q1 results, meaning management had already incorporated the
installed-base-expansion evidence into its own forward guidance before
this triage began. The market's own reaction (~+11% cumulative over the
following days, concentrated in one high-volume session on T+1)
indicated the story had already begun to be priced, not overlooked, by
the evidence date. The cheapest-falsification test came back split:
strong on margin/cash-conversion improvement (Adjusted EBITDA margin
roughly doubled YoY for the same quarter; operating cash flow swung
~C$9.7M favorably), weak on "not already captured in guidance."

**A secondary, genuine negative finding**: Professional Services
Backlog fell 37-38% YoY, with management explicitly guiding to a near-
term professional-services revenue decline in Q2 FY2027 — a real,
disclosed headwind the original hook did not surface. Note 7 also
showed nearly half of SaaS RPO does not convert to revenue until Fiscal
2029 or later, qualifying the "RPO growth" half of the hook without
contradicting it (RPO is confirmed SaaS-only, not conflated with
services backlog).

**Gate B could not be attempted for this security at all** — `XTSE` is
not a MIC supported by the live session calendar, and the configured
TwelveData plan does not cover TSX-listed names. This was disclosed
plainly as a genuine data-availability limitation, not worked around; a
coarse valuation checkpoint was instead built from the company's own
disclosed market capitalization (C$482M as of July 31, 2026) and
clearly-labeled uncertified secondary price data, showing a full,
growth-company multiple (~17.6x EV/EBITDA, ~4.45x EV/ARR), not a
depressed one.

**Neglect classification: `NEGLECT_PARTIAL`** — six sell-side analysts
cover the name (not conventionally "neglected"), but trading liquidity
is genuinely thin (a few hundred to a few thousand shares/day on
non-event days), a real mechanism by which price discovery could still
lag available information. **Uncertainty classification:
`POTENTIAL_SOURCE_OF_EDGE`** — whether the expansion mechanism continues
accelerating beyond the just-raised guidance is evidence-gatherable, not
currently working against the thesis.

**No deep underwriting of TCS.** NHP, UCB, SAIA remain
`NO_DEMONSTRATED_EDGE`; NNBR remains `BLOCKED_BY_MATERIAL_UNCERTAINTY`.
No Batch 003 candidate advances further without an explicit new work
order. No Batch 004 started.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT3_FORMAL_CLOSEOUT_AND_PILOT4_TRANSITION_RESULT (2026-09-14)

**Record:** `pilot3/PILOT3_CLOSEOUT_AND_PILOT4_TRANSITION.md`.
**Verdict: `CLOSE_PILOT3_ADVANCE_TO_PILOT4`**, following two Red Team
reviews. Pilot 3 is complete; no further Pilot 3 batch will be created.
No frozen Pilot 3 company record is rewritten.

**What Pilot 3 proved** (recorded in full in the closeout record):
broader discovery mechanisms beyond headline/event setups; improved
Scout opportunity quality without source privilege; Hook Reconstruction
can cheaply falsify weak hooks (NHP's hidden dilutive raise, UCB's
near-zero-net EPS bridge, SAIA's redundant read-through) without
mechanically rejecting all candidates (NNBR's operating hook and TCS's
installed-base mechanism both strengthened under reconstruction); the
Priced-In One-Liner improves expectations-gap discipline (passed at
NNBR, failed at SAIA and TCS); Atlas can distinguish company
improvement from common-share value creation and productive from
thesis-blocking uncertainty, both demonstrated within the single NNBR
deep-underwriting record; competitor read-through requires a valid
economic transmission mechanism (SAIA, the pilot's core read-through
learning test); real business mechanisms may already be reflected in
expectations and price (TCS, guidance raised and market already reacted
on the same evidence); research intensity can be allocated selectively
(NHP/UCB/SAIA closed at triage without deep underwriting); Atlas
repeatedly added decision-relevant information beyond the original
discovery hook in every closed record.

**What Pilot 3 did not prove, recorded explicitly and not softened:** no
Pilot 3 candidate reached Stage 7 capital comparison; discovery has not
yet demonstrated repeatable investable alpha; Atlas has not yet
demonstrated repeatable discovery before market recognition;
false-negative calibration remains unproven; opportunity half-life
remains poorly understood; Atlas has not yet demonstrated the
originally surfaced security is consistently the best expression of a
valid thesis.

**The two narrow fixes (Hook Reconstruction at Triage; Priced-In
One-Liner) are carried forward unchanged** — no expansion, no
additional generic triage gate.

**Pilot 4 chartered, not active.** New information family under the
standing One-New-Information-Family-Per-Pilot Guardrail:
`FORCED_FLOW / OWNERSHIP_DISLOCATION` (experimental only, no permanent
taxonomy). Primary learning objective: can forced-flow/ownership
dislocation uncover a security whose price is temporarily disconnected
from underlying economics, early enough for Atlas to validate the
opportunity and reach Stage 7 without lowering evidence or variant
standards? Four research questions carried forward with no new
architecture: quiet-change, original-source-vs-echo (existing
provenance discipline sufficient, no new system), best-expression (no
optimizer), and recognition/half-life (temporary learning observation,
no permanent field). Sentiment remains `SHADOW_ONLY`, no formal
implementation. Beta/SPY remain a live capital alternative, no separate
engine. Scout closeout feedback recorded (prefer changes not yet
obvious stories; identify original source; surface why the market might
be wrong; consider whether the surfaced ticker is the best expression;
bring the strongest contradictory fact — no Scout ranking or capital
authority). Roadmap hypotheses (capital-cycle/capacity, formal
sentiment/news/trend testing, credit-vs-equity divergence, statistical/
ML learning, late-Pilot-4 CX/Claude Design work) preserved, not
activated. Infrastructure restraint recorded: no XTSE support, second
market-data vendor, sentiment provider, valuation engine, ownership-data
infrastructure, or ML/statistical tooling unless an actual decision
problem earns it.

**No Pilot 4 candidate created. No forced-flow research begun. No new
architecture, fields, engines, scoring, governance, or workflow layers
added.** Master Project Plan updated: Pilot 3 status set to `CLOSED`;
new Pilot 4 section added (`CHARTERED, NOT ACTIVE`). No architecture
document created — the closeout lives in a Pilot 3 record, consistent
with this pilot's existing document pattern (e.g., the Batch 003
charter).

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT3_TO_PILOT5_RENUMBERING_CORRECTION (2026-09-14)

**Correction to the entry above** (`PILOT3_FORMAL_CLOSEOUT_AND_PILOT4_TRANSITION_RESULT`),
**appended, not rewritten**, per this project's standing discipline
against altering already-recorded decision-log history.

**What happened:** the prior entry, and the Master Project Plan /
closeout record it summarized, labeled the newly chartered forced-flow/
ownership-dislocation experiment **"Pilot 4."** `docs/pilot4/` already
contains a separate, complete, frozen pilot dated September 2, 2026 —
the COST/PH/AMGN incumbent-substitution test that established the
"two-bar rule" (cash-initiation ≠ incumbent-substitution,
`pilot4/PILOT4_HEALTH_LEARNING_001.md`,
`PILOT4_STAGE7_FINAL_RECORD_001.md`, `PILOT4_STAGE8_HUMAN_DECISION_001.md`)
— substantively unrelated to forced-flow/ownership-dislocation
discovery. This was a genuine numbering collision, introduced without
first checking the repository for prior use of the number.

**Correction:** the new experiment is renumbered **Pilot 5**. The verdict
identifier is corrected to `CLOSE_PILOT3_ADVANCE_TO_PILOT5`.
`docs/pilot3/PILOT3_CLOSEOUT_AND_PILOT4_TRANSITION.md` was replaced with
`docs/pilot3/PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md` (same content,
numbering only, plus a disambiguation note); the Master Project Plan's
Pilot 3 status block and its chartered-pilot section were corrected the
same way, with disambiguation notes added in both places. **This is a
numbering correction only — no substantive conclusion, learning
objective, governance content, or experiment design from the prior
entry changed.** The frozen `docs/pilot4/` materials are, and remain,
completely untouched — verified zero-diff.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_FORCED_FLOW_SOURCING_DESIGN_RESULT (2026-09-14)

**Record:** `pilot5/PILOT5_FORCED_FLOW_SOURCING_DESIGN.md`. Defines the
lean sourcing approach for Pilot 5's `FORCED_FLOW / OWNERSHIP_DISLOCATION`
experiment — where and how to look, not what to find. No candidates
created, no company underwriting performed, no architecture change, no
permanent fields, no scoring, no new engine, no sentiment activation, no
Batch 001 started.

**Discovery principle**: begin with who may be compelled to transact,
why, when, and in what size — not which stock has recently fallen.
Search for the constraint first; identify affected securities only
afterward.

**Three search lenses (not a permanent taxonomy)**: (A) shareholder
mismatch/distributed securities (spin-offs, merger/restructuring
distributions, bankruptcy-emergence ownership); (B) mechanical
benchmark/mandate flow (index additions/deletions/reconstitutions,
mandate eligibility changes); (C) holder-specific forced or highly
constrained selling (fund liquidation/redemption, concentrated-holder
exit, lockups, tax-related selling, forced deleveraging). Quality
governs over diversity — three high-quality situations preferred over
three diversified-but-weak ones; no category is forced.

**Primary public source classes** recorded: corporate filings (SEC
filings, IR releases, spin-off registration filings, proxy/merger
materials, prospectuses, ownership filings), index/benchmark sources
(provider announcements, methodology/reconstitution notices), holder/
fund sources (liquidation notices, 13D/13G amendments), and corporate-
action sources. Secondary news/search/AI may help discover events, but
every opportunity is traced back to original evidence where possible.

**14 initial opportunity questions** recorded across seven dimensions
(constraint, size, timing, economics, recognition, expression,
falsification) — questions only, not converted to permanent fields or
scores. **Flow-magnitude approach**: a simple, judgment-based comparison
of estimated constrained shares versus ordinary trading liquidity — no
proprietary flow score created. **Fundamental-separation discipline**:
the ideal setup is ownership/flow changing materially while economics
changed little; skepticism required where earnings, leverage,
competitive position, or guidance genuinely deteriorated at the same
time — forced selling is not automatically mispricing.

**Original-source discipline, best-expression question, and discovery-
clock approach** all carried forward from the Pilot 5 charter unchanged
— no new provenance system, no optimizer, no timing engine.

**Scout search posture** defined as a qualitative instruction (find
situations where identifiable investors may be compelled to transact
for non-fundamental reasons; begin with the constraint; trace to
original evidence; estimate flow-vs-liquidity materiality; state the
cheapest falsification; explain why the market may not have fully
absorbed the distortion) rather than a stock-count request. Scout does
not rank, size, allocate, or promote — Atlas validates, unchanged.
**Human/manual sourcing remains live** (Chris, network observations,
manual research, ChatGPT/Grok/other technology) — "many sources
discover, Atlas validates, human allocates" unchanged. Technology
principle restated: use any tool that materially improves discovery,
validation, or decision quality; do not convert useful tools into new
Atlas architecture absent a repeated, demonstrated need.

**First-batch concept recorded for context only** (~3 high-quality
situations, not a large basket, not required to all survive triage) —
**not executed by this record.**

**No candidates created. No architecture change. Frozen control layer,
facade files, and docs/pilot4/ (the unrelated, frozen pilot) verified
untouched.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_DISCOVERY_SCAN_001_AND_VYLR_TRIAGE_RESULT (2026-09-14)

**Records:** `pilot5/PILOT5_DISCOVERY_SCAN_001_REGISTRATION.md`,
`pilot5/PILOT5_VYLR_FORCED_FLOW_TRIAGE_001.md`. Source:
`GROK_SCOUT_FORCED_FLOW_DISCOVERY`.

**Registration**: three situations registered without ranking — VYLR
(Corteva → Vylor spin-off), 646A/Crasus (Resonac → Crasus), MSGR (MSG
Sports → Rangers). Scout's "best research-use-of-time candidate: VYLR"
claim explicitly disregarded as a ranking input, per the standing
Discovery Source Neutrality rule. Only VYLR received forced-flow
triage.

**VYLR result: `PROMOTE_TO_FUNDAMENTAL_UNDERWRITING`** — Pilot 5's
first candidate, and the first test of the pilot's primary learning
objective. Canonical identity confirmed (Vylor Inc., CIK `0002128626`,
formerly Seed External Spinco Inc., clean CIK, no ticker collision);
the "VYLR" ticker itself was found to be secondary-sourced (blank in
the most recent primary SEC filing) — a sourcing-tier distinction
stated plainly rather than assumed.

Corporate-action mechanics (when-issued trading beginning the session
before the record date, regular-way beginning on the distribution
date, cash-in-lieu of fractional shares) confirmed directly from
Vylor's Form 10-12B/A information statement (downloaded directly at
22.1MB after standard fetch tooling exceeded its size limit, then
locally text-extracted). The specific dates (record date ~September
24, 2026; distribution ~October 1, 2026; 1:1 ratio; ticker VYLR)
were corroborated by a same-day secondary news report but explicitly
flagged as not yet confirmed by any Corteva- or Vylor-filed SEC 8-K as
of the evidence date (verified via SEC full-text search, zero
results).

Confirmed Corteva (CTVA) is an S&P 500 constituent since 2019 — the
structural fact underlying the entire forced-flow mechanism — and
located the issuer's own primary-sourced risk-factor language: "a
portion of Vylor common stock is held by index funds tied to stock
indices. If we are not included in these indices at the time of
spin-off, these index funds may be required to sell Vylor common
stock." No S&P Dow Jones Indices (or other index-provider) announcement
on Vylor's treatment was found in either direction.

Cheapest-falsification test run first, per instruction: none of the
four named kill conditions were satisfied on the evidence gathered.
Fundamental-separation check found no contemporaneous deterioration in
the Seed segment (Corteva's most recent guidance was raised, not cut;
Seed H1 2026 operating EBITDA up 11% YoY; the September 10 PFAS
settlement traces to legacy Crop Protection/DuPont/Chemours liability,
unrelated to Vylor). A coarse, explicitly labeled order-of-magnitude
estimate of constrained supply was built from confirmed CTVA shares
outstanding (~667.2M) and general, widely-cited passive-ownership
research; a security-specific, verified 13F/ETF-holdings breakdown
could not be obtained with free/public tooling — disclosed as a genuine
evidence gap. VYLR liquidity itself cannot yet be assessed (trading has
not begun; a TwelveData symbol search returned zero results).

Promotion is named explicitly as meaning only that the forced-flow
mechanism is credible enough to justify examining Vylor's underlying
economics and valuation next — not that VYLR is attractive. The
still-unannounced index-inclusion decision and the unresolved
constrained-vs-discretionary quantification are named as the specific,
evidence-gatherable focus for the next stage, mirroring how this
project's prior pilot named and carried forward NNBR's Series D
uncertainty rather than treating an open question as an automatic
block.

**646A/Crasus and MSGR remain `SURFACE_FOR_TRIAGE`, completely
untouched** — no identity check, no primary-evidence review, no
research performed on either. **No fundamental/deep underwriting of
Vylor performed. No Stage 7 or Stage 8 action. No Discovery Scan 002.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_VYLR_PRE_WI_FUNDAMENTAL_UNDERWRITING_RESULT (2026-09-14)

**Record:** `pilot5/PILOT5_VYLR_PRE_WI_FUNDAMENTAL_UNDERWRITING_001.md`.
Follows the prior forced-flow triage's `PROMOTE_TO_FUNDAMENTAL_
UNDERWRITING` disposition. The prior triage's coarse ~65-135M-share
constrained-supply estimate is explicitly re-labeled
`EXPLORATORY_CONTEXT_ONLY` in this record and used nowhere as a
decision fact.

**Result: `READY_FOR_WI_PRICE_TEST`** — meaning only that Vylor's
fundamentals are sufficiently attractive/understandable to compare
actual when-issued or regular-way pricing against the valuation
economics prepared here; not a buy signal, not Stage 7.

**Capital structure**, built from Vylor's primary Form 10-12B/A
information statement (downloaded directly and locally text-extracted
after its 22.1MB size exceeded standard fetch tooling): Vylor
distributes 100% to Corteva shareholders (New Corteva retains no
ownership); pro forma total borrowings ≈$5.579 billion, of which
≈$3.143 billion is short-term/seasonal (a PHI Bilateral Facility bridge
expected to be refinanced via new revolvers at spin) and ≈$2.436
billion is genuinely structural long-term debt (≈$1.28B of exchanged
legacy EIDP notes at a 4.12% weighted rate plus the $1.1B of new senior
notes issued August 2026). The single most important capital-structure
finding: Vylor is incurring ≈$5.476 billion of new debt specifically to
fund, in part, a ≈$3.560 billion cash distribution to New Corteva — a
debt-funded recapitalization, not organic growth capital. Pension
obligation retained by Vylor is small (~$82M of Corteva's $1.3B total).
Equity-award treatment and the incentive plan's terms are explicitly
deferred to a future Form 10 amendment — a genuine, disclosed dilution/
management-incentive evidence gap.

**5-period Seed-segment economics** (FY2023, FY2024, FY2025, H1 2025,
H1 2026), reconstructed from Corteva's segment MD&A and pro forma
statements: net sales $9,472M→$9,545M→$9,898M (FY2025 growth +3%
price/+2% volume/-1% FX — price-led, not FX- or mix-driven); gross
margin 47.4%→48.9%→53.8%; operating EBITDA $2,117M→$2,219M→$2,636M
(EBITDA margin 22.4%→23.3%→26.6%, accelerating); R&D $836M→$902M→$979M
(8.8%→9.9% of revenue, rising alongside margin expansion, not traded
off against it); capex $303M→$338M→$346M. H1 2026 continued the trend
(+4% revenue, +11% EBITDA YoY), though H1 margins (~37-40%) were
flagged explicitly as a seasonal artifact of front-loaded planting-
season revenue, not a new sustainable run-rate. Seed grew through
FY2023-2024 while total Corteva revenue declined — evidence of
relative cyclical resilience, not proof of acyclicality.

**Competitive quality**: confirmed the "flagship Pioneer® brand, the
number one corn and soybean brand in the United States" and Pioneer
Hi-Bred International as Vylor's key subsidiary (co-borrower on its
revolving credit facility). The Bayer agrobacterium/Enlist trait
litigation ($610M settlement, ~$546M already paid) was found to be
Seed/trait-technology-specific but substantially resolved and net
strategically positive (terminated ongoing royalty obligations, opened
new out-licensing arrangements).

**Standalone-cost analysis (load-bearing, per instruction)**: separated
TRANSITIONAL costs ($189M one-time separation SG&A; $16M debt-transfer
fees; the largely-paid Bayer settlement) from STRUCTURAL costs
(~$169M/year of new estimated interest expense, confirmed from the
pro forma adjustments; an unquantified further layer of dis-synergies
the issuer itself acknowledges may "exceed expectations" but does not
size). This unquantified dis-synergy figure was named as the single
cheapest fact that could most change the underwriting picture.

**Fundamental quality classification: `SOLID_CYCLICAL_BUSINESS`**
(case-specific, not a permanent scoring taxonomy) — real, multi-year
margin expansion and price-led growth with R&D investment maintained,
falling short of a compounder classification only because standalone
costs remain unquantified, growth platforms (gene editing, hybrid
wheat, biofuels) are unproven, and pricing power has not been tested
through a genuine Seed-specific downturn.

**Valuation sensitivity map** (explicitly labeled illustrative, not
price targets) built downside/base/strong-execution equity-value bands
from FY2025 EBITDA and a range of illustrative EV/EBITDA multiples.
Required-return/attractiveness observation: further capital comparison
would become warranted if actual price fell meaningfully below the
downside band without independent fundamental confirmation of that
degree of deterioration — a threshold, not a target price, and not a
Stage 7 decision. The three forced-flow/fundamentals interaction
scenarios (mediocre fundamentals; attractive fundamentals but rich
valuation; attractive fundamentals with price below reasonable
economics) were named explicitly, with the observable evidence that
would distinguish them.

**No capital decision. No Stage 7. 646A/Crasus and MSGR remain
`SURFACE_FOR_TRIAGE`, completely untouched. No Discovery Scan 002.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_CRASUS_646A_FORCED_FLOW_TRIAGE_RESULT

| | |
|---|---|
| Date | 2026-09-14 |
| Status | **CLOSED — `NO_DEMONSTRATED_FORCED_FLOW_EDGE`** |
| Context | Pilot 5 Discovery Scan 001, situation 2 of 3 |

### Decision

Forced-flow triage of Crasus Chemical Inc. (TSE 646A, pending listing),
Resonac Holdings Corporation's (TSE 4004) petrochemical-business
spin-off, closed **`NO_DEMONSTRATED_FORCED_FLOW_EDGE`**. Full record:
`pilot5/PILOT5_CRASUS_646A_FORCED_FLOW_TRIAGE_001.md`.

**Transaction mechanics** confirmed from Resonac's own July 6, 2026
primary IR documents (news release + explanatory material, both PDFs
extracted via `pdftotext` after WebFetch's binary-PDF ceiling made
direct extraction unreliable — same workaround pattern established for
TCS in Pilot 3): more than 80% of Crasus shares distributed to Resonac
shareholders at a 1:1 ratio via in-kind dividend, Resonac retaining
less than 20%; listing (Sept 29, 2026) preceding the distribution's
effective date (Oct 1, 2026); a direct listing (TSE Itayose call-
auction price discovery) raising no new capital.

**Mechanism-by-mechanism finding (load-bearing):** the spin-off is
confirmed a **tax-qualified partial spin-off under Japanese law** —
Resonac shareholders face no deemed-dividend taxation and capital-gains
tax is merely deferred, not triggered — directly refuting a
Japan-domestic-tax-driven forced-selling narrative for the majority of
the shareholder base. U.S. federal tax treatment was not addressed by
either primary document (disclosed evidence gap); a separate,
non-tax, U.S. securities-law mechanism (Crasus shares "have not been,
and will not be, registered under the U.S. Securities Act of 1933")
was identified as a more concrete potential constraint on U.S. holders,
but its actual operational effect (non-delivery vs. cash-out) could not
be confirmed. The most concrete confirmed forced-seller mechanism found
was the **Nikkei 225's own July 2025 methodology revision**: a spun-off
entity is temporarily included in the index from the ex-rights date and
mechanically removed the business day after listing — Nikkei Inc.'s
own reporting confirms Crasus specifically will be included on its
Sept 29 listing date and removed Sept 30, forcing Nikkei-225-tracking
passive funds to exit within roughly one trading day regardless of
fundamental view. This mechanism's magnitude could not be quantified
pre-listing (Crasus has no market price yet, and Nikkei 225 is a
price-weighted index with capping factors not available to Atlas).
TOPIX treatment of the new Standard Market listing remained an
unresolved evidence gap (JPX's own methodology page returned HTTP 403;
no dated confirmation found either way). Sector/mandate mismatch
(semiconductor-materials shareholder base inheriting a basic
petrochemical company) was found plausible but unconfirmed at the
specific-holder level.

**Fundamental-separation check — more consequential here than at Vylor,
as the sourcing design's own caution about basic-petrochemical
cyclicality anticipated.** Crasus's own May 15, 2026 pre-listing
disclosure (original, issuer-sourced) showed operating profit falling
51% year-over-year (¥8.6B→¥4.2B, 2024→2025), ROE falling from 7.8% to
4.7%, ROIC from 4.5% to 2.4%, and 2026 operating-profit guidance
explicitly placed "under review" due to a Middle East-conflict-linked
naphtha-supply disruption making customer demand and business-plan
impact "unpredictable" — in the issuer's own words. This sits against a
backdrop of Japan's ethylene industry hitting record-low utilization
(68.6% in March, 67.3% in April 2026, per Japan Petrochemical Industry
Association data via Argus Media/Hydrocarbon Processing) and a
disclosed structural industry contraction (4 of Japan's 12 ethylene
plants to close by ~2030). This independently and sufficiently explains
potential post-listing price weakness without requiring any
ownership-dislocation story.

**Cheapest falsification result:** of five proposed kill conditions,
two were affirmatively satisfied by primary evidence (Japan-domestic
tax treatment; sector mismatch unconfirmed at the holder level), one
was genuinely mixed (index treatment — Nikkei 225 real, TOPIX
unconfirmed), and the fundamental-separation confound independently
undermines the thesis's cleanliness. The forced-flow hypothesis was not
cleanly killed outright but did not clear the bar for promotion to
fundamental underwriting.

**Discovery-clock result:** Crasus's transaction terms have been
publicly disclosed in full detail since July 6, 2026 — over two months
before Scout's Sept 14, 2026 discovery — and a Japan special-situations
research platform had already published a dedicated primer and an
"expert call transcript" on Crasus dated Sept 8, 2026, six days before
Scout's surfacing. This is materially later in the security's own
recognition cycle than Vylor, which Atlas engaged before any price
discovery had begun.

**Pilot 5 comparative learning (Crasus vs. Vylor, learning only, no
capital ranking):** Vylor was found cleaner on every tested axis — the
more identifiable constrained seller (issuer's own risk-factor language
naming index funds directly, versus Crasus's index-provider-sourced but
issuer-silent mechanism), the cleaner fundamental separation (Corteva's
guidance raised vs. Crasus's guidance withdrawn), and the earlier
discovery relative to price discovery. This asymmetric result is
recorded as a genuine, useful Pilot 5 finding, not softened for
experimental symmetry between the two candidates.

**Vylor unchanged at `READY_FOR_WI_PRICE_TEST`. MSG Rangers (MSGR)
unchanged at `SURFACE_FOR_TRIAGE`, completely untouched. No deep or
fundamental underwriting of Crasus. No Stage 7. No capital allocated.
No new Pilot 5 discovery scan.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_MSGR_FORCED_FLOW_TRIAGE_RESULT

| | |
|---|---|
| Date | 2026-09-15 |
| Status | **CLOSED — `NO_DEMONSTRATED_FORCED_FLOW_EDGE`** |
| Context | Pilot 5 Discovery Scan 001, situation 3 of 3 (final — scan now fully triaged) |

### Decision

Forced-flow triage of MSGS Spinco, Inc. (CIK `0002132873`, to be
renamed MSG Rangers Corp., expected NYSE ticker MSGR), Madison Square
Garden Sports Corp.'s (NYSE MSGS, to be renamed MSG Knickerbockers
Corp., expected ticker MSGK) proposed spin-off of its New York Rangers
business, closed **`NO_DEMONSTRATED_FORCED_FLOW_EDGE`**. Full record:
`pilot5/PILOT5_MSGR_FORCED_FLOW_TRIAGE_001.md`.

**Transaction status** confirmed from the primary Form 10-12B/A,
Amendment No. 1 (filed Sept 3, 2026, 12 days before this triage) and
its Exhibit 99.1 Information Statement (2.09MB HTML, downloaded and
locally text-extracted via the same workaround pattern established for
Vylor/TCS/Crasus): 1-for-2 distribution ratio and MSGR/MSGK tickers
both confirmed matching Scout exactly. **Board approval of the
Distribution itself, league (NHL) approval, a final tax opinion (only
a draft, bracketed-placeholder Exhibit 8.1 from Sullivan & Cromwell LLP
exists), and Form 10 effectiveness all remain unsatisfied conditions**,
and the record date and distribution date remain genuinely blank in
the issuer's own most current filing — independently confirming
Scout's own caveat that terms were not yet final.

**Mechanism-by-mechanism finding (load-bearing):** the issuer's own
selling-pressure risk-factor language, quoted verbatim from the primary
filing and appearing in mirror-image form for both RemainCo and
SpinCo, is explicitly **preference-framed** ("stockholders sell their
shares because they are not interested in holding an investment,"
not "may be required to sell") — a meaningful, original-source
distinction from Vylor's compulsion-framed index-fund risk factor.
No index-treatment discussion exists anywhere in MSGR's own ~780,000-
character information statement. Atlas nonetheless identified a real,
previously-unstated structural mechanism beyond Scout's framing: MSGS
is a confirmed S&P SmallCap 600 member (since Aug 1, 2023), and S&P
Dow Jones Indices' own published methodology requires a spun-off
entity to independently qualify for index addition, including a
positive-earnings screen over the trailing four quarters — a screen
MSGR would very plausibly fail given its own disclosed net losses in
both FY2025 and FY2026. This is a materially weaker dynamic than
Vylor's or Crasus's index-removal mechanisms, since it describes a
stub never being added to an index rather than being mechanically
forced out of one it briefly held. Sector/mandate mismatch (EGC-averse
and controlled-company-averse institutional mandates) and stub-size
dynamics were both found plausible but unconfirmed at the specific-
holder level, consistent with the instruction not to assume a
mismatch or manufacture forced selling from position size alone.

**Fundamental-separation check** found a genuine confound: operating
loss of approximately $30.5 million (FY2026) and $23.3 million
(FY2025); net loss of $26.4 million (FY2026) and $23.0 million
(FY2025), both years unprofitable and worsening; revenue itself
playoff-sensitive ($401.5M in FY2024 versus $337.3M in FY2026); and
the issuer's own direct words — "We are likely not to be profitable in
the near term unless the Rangers make an extended playoff run." A
concrete, already-realized related-party finding: Rangers local media
rights revenue fell from $39.1 million (FY2025) to $35.3 million
(FY2026) after related-party MSG Networks' 2025 debt restructuring (a
~$510 million lender write-off) forced an 18% cut to the local
telecast rights fee, with no annual escalator.

**Franchise-value-vs-public-equity test:** the widely-reported
Knicks/Rangers "sum-of-the-parts" valuation gap (MSG Sports' combined
public equity value of roughly $9.6-9.8 billion against a combined
third-party sports-valuation estimate of $13.5-13.75 billion — Knicks
~$9.75-9.85B post-2026-championship, Rangers ~$3.65-4.0B) is real and
already the dominant, broadly-covered investment narrative for this
transaction, not an Atlas discovery. Whether that gap accrues cleanly
to minority MSGR public shareholders was found **not established**,
given the Dolan Family Group's permanent 100% Class B ownership,
controlled-company status, and the absence of any identified sale or
capital-return catalyst.

**Cheapest falsification result:** three of five proposed kill
conditions were satisfied or largely satisfied by primary evidence
(team preference confirmed discretionary; natural sports-specialist/
event-driven buyer interest already visible; standalone Rangers
fundamentals independently explain likely weakness), and the one real,
newly-identified index mechanism (S&P non-addition) is structurally
weaker than either Vylor's or Crasus's mechanisms. The forced-flow
hypothesis does not survive as a clean, well-isolated thesis.

**Discovery-clock result:** a nuanced, distinct finding from the other
two Discovery Scan 001 situations — Atlas is engaging before the
transaction has closed and before any MSGR price discovery exists
(closer to Vylor's position), but the underlying sum-of-the-parts
economic thesis has already been publicly known and actively covered
by dedicated sports-finance and event-driven media for four months
(since the May 18, 2026 announcement), meaning being early relative to
price discovery is not the same as being early relative to thesis
recognition.

**Three-way Pilot 5 comparative learning (Vylor / Crasus / MSGR,
learning only, no capital ranking):** each of the two non-promoted
situations failed for a genuinely different reason — Crasus on a
fundamental confound (record-low petrochemical-cycle utilization,
withdrawn guidance) despite a real, dated index mechanism; MSGR on
mechanism purity (preference-framed, not compulsion-framed language;
a non-addition rather than forced-removal index dynamic) compounded by
a fundamental confound of its own (playoff-dependent losses) and prior
public recognition of its core thesis. This asymmetry across all three
outcomes is recorded as a genuine, useful Pilot 5 finding rather than
smoothed into a single generic conclusion.

**Discovery Scan 001 is now fully triaged: Vylor
(`READY_FOR_WI_PRICE_TEST`), Crasus (`NO_DEMONSTRATED_FORCED_FLOW_EDGE`),
and MSGR (`NO_DEMONSTRATED_FORCED_FLOW_EDGE`) each carry a recorded
disposition. Vylor and Crasus records unchanged and untouched by this
turn. No deep or fundamental underwriting of MSGR. No Stage 7. No new
Pilot 5 discovery scan.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_SCAN001_RED_TEAM_CHECKPOINT

| | |
|---|---|
| Date | 2026-09-15 |
| Status | **RECORDED — checkpoint only, no dispositions changed** |
| Context | Pilot 5 Discovery Scan 001, post-triage Red Team review |

### Decision

Record-only Red Team checkpoint on Pilot 5 Discovery Scan 001, now that
all three surfaced situations (Vylor, Crasus, MSGR) carry a closed
disposition. Full record:
`pilot5/PILOT5_DISCOVERY_SCAN_001_REGISTRATION.md`, "Red Team
Checkpoint" section. **No architecture changed. No candidates created.
No new research performed. No frozen record modified.**

**Vylor (`READY_FOR_WI_PRICE_TEST`, preserved unchanged)**: Red Team
conclusion — Vylor remains the clean live Pilot 5 test fixture, but the
forced-flow mechanism should **not** yet be described as demonstrated.
Issuer index-selling language plus CTVA's confirmed S&P 500 membership
establishes a plausible structural constraint, not a measured forced
book. Exact constrained supply remains unknown. Vylor was discovered
early relative to trading, but not necessarily early relative to
specialist recognition. WI trading is the next falsification point.

**Crasus (`NO_DEMONSTRATED_FORCED_FLOW_EDGE`, preserved unchanged)**:
the tax-selling thesis was materially weakened by confirmed Japan tax
treatment; fundamental deterioration independently explains potential
weakness; dirty fundamental cases are poor forced-flow tests unless a
dated mechanical constraint is unusually strong.

**MSG Rangers (`NO_DEMONSTRATED_FORCED_FLOW_EDGE`, preserved
unchanged)**: issuer-described selling pressure was primarily
preference, not compulsion; preference mismatch should not be treated
as forced flow; natural specialist buyers and an already-known
sum-of-the-parts framing weaken the dislocation thesis.

**Scan 001 learning, recorded as research questions only (no permanent
fields, no scoring)**: Scan 001 clarified the rejection rules of
forced-flow discovery more than it demonstrated a profitable
dislocation. Carried forward: who must transact under a rule they do
not control? By when? Can the likely supply be bounded? Who is able
and motivated to absorb it? Are the fundamentals quiet enough that the
tape could plausibly reflect ownership pressure rather than operating
deterioration?

**Flow quantification (recorded, no flow score created)**: exact
forced-share counts are not required for initial triage, but a
meaningful bound on potential supply relative to liquidity becomes
necessary before Atlas can claim a forced-flow edge or progress toward
capital comparison.

**Timing (recorded, no timing engine or permanent field)**: early
relative to first trading is not the same as early relative to
specialist recognition.

**Scan 002: `WAIT_FOR_VYLOR_WI_PRICE_TEST`.** Scan 002 does not begin
before the Vylor WI test unless a material event invalidates the
current experiment. Current Red Team hypothesis for Scan 002, once it
begins: preferentially test genuinely different mechanisms — index
deletion/reconstitution; fund liquidation or concentrated-holder forced
exit; lockup/post-reorganization holder mismatch. These remain future
search directions only; no candidates are created now.

**Scout feedback: `SCOUT_UPDATE_EARNED`.** Three Pilot 5 lessons earned
a Scout instruction refinement: (1) distinguish must-sell-in-a-defined-
window from may-want-to-sell; (2) do not infer tax-driven selling
without confirming the actual tax treatment; (3) flag material
fundamental deterioration at the discovery hook rather than framing it
as a forced-flow opportunity. The broader Scout operating instructions
are not rewritten.

**Vylor, Crasus, and MSGR triage/underwriting records are unmodified by
this checkpoint. No Scan 002 started. No new securities researched. No
architecture change.**

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## PILOT5_VYLOR_TRADING_TRIGGER_UPDATE

| | |
|---|---|
| Date | 2026-09-24 (corporate action); recorded 2026-09-28 |
| Status | **RECORDED — trigger update only, no dispositions changed** |
| Context | Pilot 5 Vylor: WI market canceled; regular-way trading expected October 1, 2026 |

### Decision

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

Full record: `pilot5/PILOT5_DISCOVERY_SCAN_001_REGISTRATION.md`, "Trading-Trigger Update" section.

---

## PILOT5_VYLR_REGULAR_WAY_PRICE_TEST

| | |
|---|---|
| Date | 2026-10-01 |
| Status | **RECORDED — `NO_DEMONSTRATED_INVESTABLE_DISLOCATION`** |
| Context | Pilot 5 Vylor first completed regular-way session vs frozen pre-trading underwriting |

### Decision

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

## PILOT5_SCAN002_REGISTRATION_AND_CTVA_TRIAGE

| | |
|---|---|
| Date | 2026-10-01 |
| Status | **RECORDED — CTVA `PROMOTE_TO_FUNDAMENTAL_UNDERWRITING`; CBRS surfaced only** |
| Context | Pilot 5 Discovery Scan 002; CTVA S&P 500 → MidCap 400 migration effective before the Oct 6 open |

### Decision

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

## PILOT5_CTVA_PRE_EVENT_FUNDAMENTAL_UNDERWRITING

| | |
|---|---|
| Date | 2026-10-01 |
| Status | **RECORDED — `READY_FOR_POST_INDEX_EVENT_PRICE_TEST`** |
| Context | Pilot 5 Scan 002, CTVA; baseline frozen before the Oct 5 close |

### Decision

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

## PILOT5_CTVA_OCT2_LEGAL_CHECKPOINT

| | |
|---|---|
| Date | 2026-10-01 (evening) |
| Status | **RECORDED — `LEGAL_OUTCOME_PENDING_VERIFICATION`** |
| Context | Indiana TRO hearing set for Oct 2, 9 a.m.; underwriting `529286a` preserved |

### Decision

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

## PILOT5_CTVA_OCT5_LEGAL_RECHECK

| | |
|---|---|
| Date | 2026-10-05 (intraday, before the close) |
| Status | **RECORDED — `LEGAL_OUTCOME_PENDING_VERIFICATION`; Oct 5 observation not yet performed** |
| Context | Oct 2 Indiana TRO hearing outcome unverified; underwriting `529286a` preserved |

### Decision

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

## PILOT5_CTVA_OCT5_INDEX_EVENT_PRICE_TEST

| | |
|---|---|
| Date | 2026-10-05 |
| Status | **RECORDED — `NO_DEMONSTRATED_INVESTABLE_DISLOCATION`** |
| Context | Pilot 5 Scan 002, CTVA; frozen baseline `529286a` unchanged |

### Decision

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

## PILOT5_POST_CTVA_CHECKPOINT_REVIEW

| | |
|---|---|
| Date | 2026-10-05 |
| Status | **RECORDED — `CLOSE_PILOT5_INSUFFICIENT_EVIDENCE_OF_REPEATABLE_EDGE`** |
| Context | Review of VYLR, Crasus, MSGR, CTVA; CBRS evaluated at mechanism level only |

### Decision

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
