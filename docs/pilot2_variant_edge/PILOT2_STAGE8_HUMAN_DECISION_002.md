# PILOT 2 — STAGE 8 HUMAN DECISION 002 (CYCLE 2)

> **STAGE 8 — HUMAN PAPER DECISION**
> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> This is a **separate, independent decision cycle** from
> `PILOT2_STAGE8_HUMAN_DECISION_001.md`. It does not modify, supersede, or
> reconcile with Cycle 1. Both are preserved independently. This record is
> frozen once committed; it is not rewritten based on later price
> performance.

| | |
|---|---|
| Date recorded | September 7, 2026 |
| Pilot | Pilot 2 — Variant Edge & Intentional Allocation |
| Cycle | **Cycle 2** (Cycle 1: September 4, 2026, randomized, preserved separately) |
| Applies to | `PILOT2_STAGE7_CAPITAL_COMPARISON_001.md` (commit `0819e54`) |
| Capital | $50,000 paper/shadow |

---

## The decision

| Alternative | Allocation | % of $50,000 |
|---|---:|---:|
| FIS | $18,000 | 36% |
| JD | $15,000 | 30% |
| SPY | $12,000 | 24% |
| Treasury/Cash | $5,000 | 10% |
| Do Nothing | $0 | 0% |
| **Total** | **$50,000** | **100%** |

MELI and GLNG receive **$0** — unchanged from Cycle 1, consistent with their
Stage 7 states (`NO_DEMONSTRATED_EDGE` and `BLOCKED_BY_MATERIAL_UNCERTAINTY`
respectively), neither of which was eligible to compete for this capital.

### Confidence

> **MEDIUM.**

Recorded exactly as given — distinct from Cycle 1's `LOW`.

### Decision method

> **Intentional / non-random.**

Distinct from Cycle 1, where the human explicitly requested a randomized
split. Here the human reviewed the opportunity set and allocated
deliberately.

---

## FIS rationale ($18,000)

**Why this versus alternatives:** the human decision-maker believed FIS
offered good upside potential relative to the alternatives.

**Why this size:** judgmental, not formula-driven —

> "It felt like a good allocation of capital."

No quantitative sizing rule is recorded or manufactured.

### `key_risks_considered`

Material risks explicitly reviewed by the human decision-maker at Stage 8.
This field **supplements** the Allocation Bridge — it does not replace
`why_this_vs_alternatives`, `why_this_size` or `allocation_wrong_if`, and does
not itself alter the derived allocation-rationale status (see below).
Human-reviewed, concise, no scoring, no fixed category list, no required
count:

- **Leverage:** FIS took on roughly $7.7B of new debt for the Issuer
  Solutions transaction. Management is prioritizing deleveraging toward
  approximately 2.8x gross leverage before resuming meaningful buybacks. This
  reduces financial flexibility if operating performance disappoints.
- **Underlying growth weakness:** while FCF guidance was raised to
  approximately $2.15–$2.25B, FIS simultaneously lowered pro-forma revenue and
  EBITDA growth expectations. The market may therefore be correctly
  discounting a slower underlying business.

No additional FIS risks are recorded beyond these two — none else was
explicitly human-reviewed.

---

## JD rationale ($15,000)

Recorded exactly as supplied — metrics reviewed, plus the human's own stated
reason. No separate thesis, sizing formula, or wrong-if statement is added
beyond what was given:

- dividend yield ≈ 3.5%
- buyback yield ≈ 4.1% over the prior year
- shares outstanding down ≈ 4.1% year over year
- positive free cash flow, trailing FCF ≈ $4.25B

### `key_risks_considered`

**Not supplied.** The existing record contains no explicit human-reviewed
risk discussion for JD, so this field is left empty rather than populated
with an invented risk. Absence here is valid test evidence, not an omission
to correct.

**Reason for allocation:**

> "These were positive factors supporting the investment decision."

---

## SPY / Treasury-Cash / Do Nothing

No detailed rationale is invented for these. They remained genuine
alternatives and were intentionally included in the final allocation:

- **SPY:** $12,000
- **Treasury/Cash:** $5,000
- **Do Nothing:** $0

### `key_risks_considered`

**Not supplied for any of the three.** No risk was invented merely to
populate the new field. Left blank.

---

## Allocation-rationale status — derived, not asserted

Cycle 2 is materially different from Cycle 1: Cycle 1 was explicitly
randomized; Cycle 2 has real, intentional human reasoning behind both funded
lines. That difference is Loop A's finding (below) — it is **not** the same
question as whether the formal three-field Allocation Bridge is complete.
Both are checked via the actual control
(`allocation_rationale.derive_allocation_rationale_status`):

```
FIS  status  -> EXPLORATORY_LOW_RATIONALE   missing -> ('allocation_wrong_if',)
JD   status  -> EXPLORATORY_LOW_RATIONALE   missing -> ('why_this_vs_alternatives',
                                                          'why_this_size',
                                                          'allocation_wrong_if')
```

| Line | Status | Why |
|---|---|---|
| **FIS** ($18,000) | `EXPLORATORY_LOW_RATIONALE` | `why_this_vs_alternatives` and `why_this_size` were genuinely supplied. `allocation_wrong_if` was **not** — the `key_risks_considered` content (leverage, growth weakness) is a human-reviewed risk list, not a direct answer to "what observable evidence would make this allocation wrong." Mapping that content onto the formal field would be exactly the kind of forcing this record was told not to do, so it is recorded as absent. |
| **JD** ($15,000) | `EXPLORATORY_LOW_RATIONALE` | None of the three fields were supplied in the form the Bridge asks for. The metrics are real and positive, but no comparative reason against the live alternatives, no sizing rationale for $15,000 specifically, and no wrong-if were given. `key_risks_considered` is also not supplied. |

**Neither line reaches `RATIONALE_COMPLETE`, and neither is forced there.**
This is the honest result of an intentional decision that nonetheless did not
produce a formally complete Allocation Bridge for either funded security —
Loop A intentionality and Bridge completeness are different axes, and Cycle 2
clears only the first.

**`key_risks_considered` does not change this derivation.** It is a
supplementary field, checked separately from, and never substituted into, the
three fields `derive_allocation_rationale_status` actually reads
(`why_this_vs_alternatives`, `why_this_size`, `allocation_wrong_if`). Re-run
with the identical three arguments as above — `key_risks_considered` was not
and could not be passed to that function — the result is unchanged:
`EXPLORATORY_LOW_RATIONALE` for both lines, exactly as before this field was
added.

---

## Stage 7 states entering this decision

Unchanged from Cycle 1 — Stage 7 was not re-run for this cycle.

| Candidate | Stage 7 state | Funded here? |
|---|---|---|
| FIS | `ELIGIBLE_FOR_STAGE8` | Yes — $18,000 |
| JD | `ELIGIBLE_FOR_STAGE8` | Yes — $15,000 |
| MELI | `NO_DEMONSTRATED_EDGE` | No — $0 |
| GLNG | `BLOCKED_BY_MATERIAL_UNCERTAINTY` | No — $0 |

---

## Price-currency note — recorded honestly

This decision is dated **September 7, 2026**. The most recent fresh-price
bind on record is the one used at Stage 7, **September 4, 2026** (see
`PILOT2_STAGE8_HUMAN_DECISION_001.md` for the full bind detail: FIS $41.895
FRESH, JD $28.275 FRESH, SPY blocked-then/$773.79 CTX). **No new live
price/session bind was performed for Cycle 2** — this work order's scope did
not request one, and none is manufactured here. This gap (three calendar
days) is flagged rather than silently carried forward as if it were current.

---

## Live alternatives

SPY, Treasury/Cash and Do Nothing were all present, genuine, and
intentionally included in this allocation.

---

## Revisit triggers

Unchanged, inherited from the same underwriting — not re-derived or altered
by this cycle's larger allocation size:

### FIS ($18,000)

> **Gap closer / horizon:** Capital Markets stabilization and leverage
> progress toward the disclosed 2.8x target, visible over 2–4 quarters.
>
> **Wrong-if:** Capital Markets softness spreads into Banking/Issuer
> Solutions; leverage fails to progress; the $500–700M FCF figure is later
> clarified as already net of foregone Worldpay income.

### JD ($15,000)

> **Gap closer / horizon:** JD Retail's trend, especially
> electronics/appliances, over the next 1–2 quarters against what a pure
> base-effect explanation would predict.
>
> **Wrong-if:** the core decline persists beyond the base-effect window, or
> buybacks slow materially (suggesting defensive cash preservation rather
> than confidence).

### SPY, Treasury/Cash, Do Nothing

No thesis-specific revisit trigger exists for these, unchanged from Cycle 1.

---

## Historical integrity

| | Cycle 1 | Cycle 2 |
|---|---|---|
| Method | Randomized | Intentional |
| Confidence | LOW | MEDIUM |
| Loop A | NO | YES |
| FIS / JD rationale status | `EXPLORATORY_LOW_RATIONALE` | `EXPLORATORY_LOW_RATIONALE` |

Cycle 1 is **not rewritten** in light of Cycle 2. Both are preserved as
independent, dated records of what the human actually decided at the time.

---

## Record freeze

This record preserves the decision-time allocation, MEDIUM confidence, the
intentional decision method, the FIS/JD rationale as supplied, the derived
`EXPLORATORY_LOW_RATIONALE` status for both funded lines, the Stage 7 states
entering the decision, the price-currency note, the live alternatives, and a
pointer to the Loop A result in `PILOT2_LOOP_LOG_002.md`. **Once committed,
it is not rewritten based on later price performance.**

**Capital status: NO REAL PORTFOLIO ACTION.**
