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
