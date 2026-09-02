# 05 — Decision Record Template

## Purpose

This is the template for recording every Security Decision made in Pilot 1.
It exists to make decisions traceable, dated, attributable to a human, and
permanently auditable.

## Immutability Rule

> **Original Decision Records are immutable; later reviews are appended.**

Once a Decision Record's original entry is written and dated, its original
text is never edited or deleted — including to "correct" it. If
circumstances, evidence, or the human's view change later, that change is
recorded as a **new, dated Review Entry appended below the original**, never
as a modification of the original. This preserves an honest, unretouched
history of what was decided, when, and why — including decisions that later
turn out to have been mistaken.

## Scope Reminder

A Decision Record documents a **Security Decision** — a conclusion about one
security. Per `03_CAPITAL_COMPARISON_FRAMEWORK.md`:

> **Security Decision ≠ Portfolio Action.**

Completing this template does not move capital, place an order, or
constitute an instruction to any brokerage. It is a record of human
judgment only.

---

## Template

```
DECISION RECORD

Record ID:            [unique identifier, e.g. DR-2026-09-01-ACN-001]
Date recorded:        [YYYY-MM-DD]
Recorded by:          [human name / identifier]
Security:             [ticker — company name]

Pipeline state at time of record:
  SURFACED:            [yes/no + Discovery Cycle reference]
  UNDERWRITTEN:        [yes/no + underwriting conclusion reference]

Underwriting conclusion referenced:
  [verbatim categorical conclusion, e.g. "ATTRACTIVE WITH MATERIAL
  UNCERTAINTY" — must match the conclusion recorded in
  09_PILOT_1_DISCOVERY_BASKET.md or a later underwriting cycle record;
  do not paraphrase into a different conclusion here]

Security Decision:
  [explicit statement of the decision being recorded about this security
  in isolation — e.g. "Continue to monitor," "No action," "Candidate for
  comparison against beta exposure." A Security Decision is not a trade
  instruction.]

Capital Comparison Framework applied (03_CAPITAL_COMPARISON_FRAMEWORK.md):
  [If no capital comparison was performed for this record, state
  "Not performed — Security Decision only" and leave the fields below blank.
  If one was performed, all members considered must be listed, and the three
  required outputs must all be completed.]

  Funding source:
    [what capital this comparison is actually about — e.g. "new cash
    contribution," "proceeds from trimming an existing position," "existing
    cash balance." A comparison with no identified funding source is
    hypothetical and should be marked as such.]

  Opportunity Set considered (02_OPPORTUNITY_SET.md):
    a. Incumbent / current holding or status quo:
       [what is already held for this capital and the option of leaving it
       unchanged, or "none — uninvested capital"]
    b. Alpha candidate(s):
       [underwritten candidates considered, each with its recorded
       underwriting conclusion]
    c. Relevant beta:
       [the broad, low-cost market exposure judged relevant, or "none
       judged relevant — state why"]
    d. Treasury / cash:
       [the cash or cash-equivalent alternative considered]
    e. DO NOTHING:
       [how the do-nothing option was weighed — it is always an eligible
       member and may never be omitted]

  Required outputs (all three mandatory):
    f. Preferred action:
       [which member of the Opportunity Set is judged best for this capital
       right now — may be the incumbent holding or DO NOTHING]
    g. Next-best alternative:
       [the closest competing member that was not chosen]
    h. Why the preferred action wins:
       [plain-language reasons the preferred action was judged superior to
       the next-best alternative, referencing the underwriting conclusions,
       current holdings context, or beta/cash comparators actually
       considered]

  [No weighted score, numeric ranking, optimizer, or composite Atlas score
  is produced here. These are human judgments documented in prose. This is
  not a rigid ranking hierarchy — the alpha/beta/cash principle is an
  evidentiary bias applied across the full set, not a sequence of gates.]

Portfolio Action authorized by this record:
  [must state explicitly: "NONE — Security Decision only, per
  03_CAPITAL_COMPARISON_FRAMEWORK.md" unless a separate, explicitly
  authorized Portfolio Action process outside this pilot has occurred.
  Recording a preferred action above does NOT authorize a Portfolio Action:
  Security Decision ≠ Portfolio Action, and only the Human Portfolio
  Decision at Stage 8 of 04_HUMAN_OPERATING_LOOP.md may authorize capital
  to move.]

Open questions / uncertainty noted:
  [plain-language list]

---
REVIEW ENTRIES (appended only — original above is never edited)

Review date:     [YYYY-MM-DD]
Reviewed by:     [human name / identifier]
Review notes:    [what changed, what was learned, whether the original
                  Security Decision still holds]
---
```

## Usage Notes

- One Decision Record per Security Decision. A security may accumulate
  multiple Decision Records over time as circumstances change; each is a new
  record, not an edit of a prior one.
- The "Portfolio Action authorized by this record" field defaults to NONE
  and should almost always remain NONE within the scope of this pilot.
- Decision Records for Pilot 1 should be filed alongside this package (e.g.
  in a `decision_records/` subdirectory) as they are created; creating that
  subdirectory and its contents is a separate, later action and is not part
  of this initial documentation package.
