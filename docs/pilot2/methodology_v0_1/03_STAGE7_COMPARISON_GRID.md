# 03 — STAGE 7 COMPARISON GRID

> **FIXED QUALITATIVE GRID — NON-SCORED**
>
> No weights. No composite. No optimizer. No automatic winner.

---

## Purpose

Give Stage 7 a fixed set of questions answered the same way for every
candidate, so that survivors can be compared like with like and can receive
**different, defensible treatments with written reasons**.

The grid organizes human judgment for legibility and comparability. It does
not compute a result. No cell, and no combination of cells, selects an
alternative.

---

## Required Rows — Every Candidate

| Row | Content |
|---|---|
| **Security Decision** | The recorded underwriting conclusion |
| **Named edge vs cash / status quo** | Specific, named — not "looks attractive" |
| **Named edge vs beta** | Specific, named |
| **Priced-In / Variant View summary** | Short summary; full record per `01_PRICED_IN_VARIANT_VIEW.md` |
| **Uncertainty type** | Category/categories per `02_TYPED_MATERIAL_UNCERTAINTY.md` |
| **Uncertainty blocks increment?** | YES / NO |
| **Portfolio factor overlap** | Clearly supportable overlap only |
| **Liquidity / reversibility** | How readily the position can be undone |
| **Relevant time horizon** | Over what period the thesis is expected to play out |
| **Falsification condition** | What would show the thesis is wrong |
| **Funding source** | Per `05_FUNDING_SOURCE_RULE.md` |
| **Next-best alternative** | The closest competing member not chosen |
| **Treatment** | One of the permitted treatments below |

---

## Permitted Treatments

- **EARNS INCREMENT**
- **ATTRACTIVE — BLOCKED BY UNCERTAINTY**
- **ATTRACTIVE — INFERIOR TO ANOTHER ALTERNATIVE**
- **ATTRACTIVE — BLOCKED BY PORTFOLIO FIT / CAPACITY**
- **PARK / REVISIT**
- **BETA PREFERRED**
- **TREASURY / CASH PREFERRED**
- **DO NOTHING**

**Treatments are descriptive human conclusions, not scores.** They are not
ordered, not ranked, and not convertible into a number. Two candidates may
carry the same treatment for entirely different reasons, and the written
reasons are the substance.

Any candidate assigned **PARK / REVISIT** must carry a revisit trigger per
`07_REVISIT_TRIGGER.md`.

---

## Template

```
STAGE 7 COMPARISON GRID

Comparison date:       [YYYY-MM-DD]
Recorded by:           [human name / identifier]
Capital question:      [what capital, for what]
Funding source:        [per 05_FUNDING_SOURCE_RULE.md]

--- Candidate: [TICKER] ---
Security Decision:              [recorded underwriting conclusion]
Named edge vs cash/status quo:  [specific and named]
Named edge vs beta:             [specific and named]
Priced-In / Variant View:       [short summary]
Uncertainty type:               [category/categories]
Uncertainty blocks increment?   [YES / NO]
Portfolio factor overlap:       [clearly supportable overlap only]
Liquidity / reversibility:      [ ]
Relevant time horizon:          [ ]
Falsification condition:        [ ]
Funding source:                 [ ]
Next-best alternative:          [ ]
Treatment:                      [one of the permitted treatments]
Reason for treatment:           [plain language — required]

--- Candidate: [TICKER] (repeat per candidate) ---
...

--- Non-equity members of the Opportunity Set ---
Relevant beta:                  [ ]
Treasury / Cash Sleeve:         [ ]
Current book / related holding: [ ]
DO NOTHING:                     [always eligible]
```

---

## Constraints

- **No weights.**
- **No composite.**
- **No optimizer.**
- **No automatic winner.**

Completing the grid does not produce a decision. A human reads the
completed grid and assigns treatments with written reasons. Filling every
row for a candidate does not entitle it to capital, and the grid never
declares a winner on its own.

**Security Decision ≠ Portfolio Action.** Stage 7 compares; Stage 8 human
decides (`../../manual_pilot_v0_1/04_HUMAN_OPERATING_LOOP.md`).

---

## Package Governance

- Pilot 2 tests **differentiation, not breadth**.
- Same or smaller written Pilot Universe. **Do not broaden discovery yet.**
- Do not automate methodology.
- No ranking engine. No master score. No optimizer. No estimate feed. No
  sentiment system. No second market-data provider. No live brokerage. No
  tax engine.
- **No forced equity deployment.**
