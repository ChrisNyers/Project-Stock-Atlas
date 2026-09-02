# 08 — Pilot Readiness / Freeze Gate

## Purpose

This file defines the freeze conditions under which Pilot 1 operates, and
the readiness checklist a human must review before treating Pilot 1 as
complete or before considering any advancement beyond it. This gate does not
itself advance anything — it only defines what "ready" means, for a human to
judge.

## Core Rule

Consistent with `00_PILOT_OVERVIEW.md`:

> Do not advance phases on your own.

Nothing in this document set, and no automated process, is authorized to
declare Pilot 1 "complete" or to trigger any subsequent phase. Advancement
is a human decision made outside this document set, informed by — but not
performed by — this gate.

## Current Readiness Status (as of this writing)

The full manual capital-allocation loop defined in
`04_HUMAN_OPERATING_LOOP.md` (Discovery → Promotion/Reject → Underwriting →
Security Decision → Opportunity Set → Sandbox → Capital Comparison → Human
Portfolio Decision → Decision Record → Human Outcome Review → Learning) has
**not** passed readiness. This gate does not certify the full loop as ready
at this time.

What has actually occurred so far:

- **Discovery and Underwriting are underway**, using the frozen 33-stock
  Pilot 1 Discovery Basket (`09_PILOT_1_DISCOVERY_BASKET.md`). A first
  Discovery Cycle and a first underwriting pass have been recorded there.
- **Capital Comparison readiness has not been reached.** Per
  `02_OPPORTUNITY_SET.md` and `03_CAPITAL_COMPARISON_FRAMEWORK.md`, a valid
  capital comparison requires a real Opportunity Set — including current
  holdings/status quo and relevant beta/cash comparators — not merely
  underwritten candidates in isolation. That requires:
  - A **privacy-preserving real portfolio snapshot**, completed per
    `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md`, and
  - Identification of **relevant beta and cash comparators** for the
    capital in question.
  Neither has been completed as part of this documentation package, and
  **no portfolio data is invented or assumed here** to fill that gap.
- Stages 5 through 11 of `04_HUMAN_OPERATING_LOOP.md` (Opportunity Set
  onward) accordingly have not yet been exercised in Pilot 1.

This status section should be updated by the human operator as the pilot
progresses; it is not self-updating and this documentation package does not
advance it.

## What Is Frozen for the Duration of Pilot 1

- **The Discovery Basket**: the 33-stock Pilot 1 Discovery Basket
  (`09_PILOT_1_DISCOVERY_BASKET.md`) is frozen. No additions, removals, or
  substitutions during the pilot. This is distinct from the Opportunity Set
  defined in `02_OPPORTUNITY_SET.md`, which is not frozen — see "Current
  Readiness Status" above.
- **The Discovery Contract**: Discovery Contract v0.1
  (`01_DISCOVERY_CONTRACT.md`) is frozen as written. Refinements are logged
  as proposals for a future version, not applied retroactively to Pilot 1
  cycles already run.
- **The production codebase**: no production SEC/XBRL/market-data logic in
  this repository is modified as part of Pilot 1. Pilot 1 is documentation
  and manual process only.
- **The baseline**: the existing clean baseline at HEAD `59911d2` is
  preserved. This documentation package adds new files under
  `docs/manual_pilot_v0_1/` only and modifies nothing else.

## Readiness Checklist (Human Review Required)

This checklist covers readiness for the **full** manual loop
(`04_HUMAN_OPERATING_LOOP.md`), not only the Discovery/Underwriting portion
described in "Current Readiness Status" above. As of this writing, the
Capital Comparison-related items below are not yet met — see that section.
Before treating Pilot 1 as ready for closure or review, a human should
confirm:

- [ ] All SURFACED securities in the current Discovery Cycle are recorded
      with a plain-language reason.
- [ ] All PROMOTED FOR FIRST UNDERWRITING securities have a recorded
      underwriting conclusion (UNDERWRITTEN state reached).
- [ ] All SURFACED — WATCH securities remain correctly marked as not yet
      underwritten.
- [ ] Every Security Decision made has a corresponding, immutable Decision
      Record (`05_DECISION_RECORD_TEMPLATE.md`).
- [ ] No Decision Record's original entry has been edited; all updates are
      appended Review Entries.
- [ ] No Portfolio Action has been taken or implied without a separate,
      explicit authorization outside the Security Decision itself.
- [ ] The most recent Pilot Health Scorecard review
      (`06_PILOT_HEALTH_SCORECARD.md`) shows no unresolved boundary
      breaches.
- [ ] Any Portfolio Snapshot in use follows the privacy-minimization rules
      in `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md` — no brokerage
      credentials or integrations exist anywhere in the pilot.
- [ ] The Discovery Basket remains exactly the frozen 33-stock basket — no
      drift.
- [ ] No scoring, ranking, optimization, or automated-learning logic has
      been introduced anywhere in the pilot process.
- [ ] A privacy-preserving real portfolio snapshot
      (`07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md`) has been completed —
      not yet met as of this writing; no portfolio data is invented to
      satisfy this item.
- [ ] Relevant beta and cash comparators have been identified for any
      capital comparison performed — not yet met as of this writing.

## What Clearing This Gate Does — and Does Not — Do

Clearing this checklist means Pilot 1's manual process has been executed
with integrity and is ready for human review and reflection. It does **not**:

- Automatically advance Stock Atlas to a next phase.
- Automatically expand the Discovery Basket.
- Automatically authorize automation of any part of the method.
- Constitute a Portfolio Action of any kind.

Any of those steps requires a separate, explicit, human decision made
outside this document set.
