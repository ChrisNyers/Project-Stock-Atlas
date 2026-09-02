# 06 — Pilot Health Scorecard

## Purpose

This file defines how the *health of the Pilot 1 process itself* is tracked
— not investment returns, not portfolio performance, not whether any
particular Security Decision turned out to be "right."

## Core Rule

> **Technical success is not project success. Decision improvement is
> project success.**

A pilot can run flawlessly from a systems perspective — every file created,
every step logged — and still fail its actual purpose if it does not produce
*better-reasoned, better-documented, more disciplined* decisions than would
have been made without it. This scorecard tracks the latter, not the
former.

Symmetrically, this scorecard does **not** track portfolio returns, security
price performance, or realized P&L. Tracking returns this early would invite
judging the *method* by short-run *outcomes*, which the governing principles
explicitly reject — a correct process can lose money in the short run, and a
lucky guess is not evidence the process worked.

## Scorecard Dimensions

Each dimension below is assessed qualitatively by the human reviewer at each
Human Outcome Review — **Stage 10** of the eleven-stage loop in
`04_HUMAN_OPERATING_LOOP.md` — and feeds the human-authored Learning at
Stage 11. None of these dimensions is combined into a single composite
score — consistent with:

> **No opaque Atlas master score or ranking engine.**

Each dimension is reported and reviewed independently.

### 1. Process Discipline
Was the SURFACED → UNDERWRITTEN → DECIDED sequence respected for every
security touched this cycle? Were any states skipped or blurred?

### 2. Record Completeness
Does every Security Decision have a corresponding Decision Record? Are
underwriting conclusions recorded in the security's own words, not
paraphrased or upgraded/downgraded after the fact?

### 3. Boundary Integrity
Did any Security Decision get treated as a Portfolio Action without a
separate, explicit authorization? Did Discovery ever get treated as an
allocation signal? Any boundary breach is a health failure regardless of
investment outcome.

### 4. Capital Comparison Discipline
Did the comparison seriously test the full realistic Opportunity Set,
including incumbent/status quo, alpha, beta, Treasury/cash, and DO NOTHING
where relevant?

This is a question about whether real alternatives were genuinely weighed —
not about whether any fixed sequence was followed.
`03_CAPITAL_COMPARISON_FRAMEWORK.md` is deliberately not a rigid ranking
hierarchy, so there is no ordered set of steps to skip. The health failure
to watch for is a comparison that quietly omits the incumbent holding or DO
NOTHING, or that compares a candidate only against beta and cash in the
abstract. Also confirm the three required outputs were recorded: preferred
action, next-best alternative, and why the preferred action wins.

### 5. Willingness to Do Nothing
Did the process actually produce "DO NOTHING" or "HOLD CASH" outcomes where
warranted, or did every cycle produce an action-biased result? A pilot that
never says "no" is a warning sign, not a sign of productivity.

### 6. Immutability Compliance
Were any original Decision Records edited rather than appended to? Any
instance is a health failure.

### 7. Scope Containment
Did the pilot stay within its frozen Discovery Basket and frozen governance
boundaries (`08_PILOT_READINESS_FREEZE_GATE.md`), or did scope creep occur
(new tickers added to the basket, new scoring logic introduced, automation
attempted)? Note that the Opportunity Set is not frozen and is expected to
differ between comparisons — only the Discovery Basket is frozen.

## Reporting Format

At each review, the human records, per dimension: a short qualitative
status (e.g. "Held," "Minor lapse," "Breach") and a one- or two-sentence
note. No numeric or letter-grade rollup is produced.

## What a "Healthy" Pilot Looks Like

A healthy Pilot 1 is one that produces disciplined, well-documented,
occasionally boring decisions — including several DO NOTHING / HOLD CASH
outcomes — with clean state transitions and zero boundary breaches. It does
not need to have identified a great investment to be healthy.
