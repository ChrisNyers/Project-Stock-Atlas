# 03 — Capital Comparison Framework

## Purpose

This file defines how, once a security has been UNDERWRITTEN and a Security
Decision has been recorded, any question of moving actual capital must be
framed. It is the bridge — and the firewall — between analysis and action.

## Core Rule

> **Security Decision ≠ Portfolio Action.**

An UNDERWRITTEN conclusion, and even a recorded DECIDED Security Decision
(see `01_DISCOVERY_CONTRACT.md`, `05_DECISION_RECORD_TEMPLATE.md`), is a
statement about a security in isolation. It is never, by itself, an
instruction to buy, sell, size, or rebalance anything in an actual portfolio.
A separate, explicit Portfolio Action step — outside the scope of Pilot 1
manual documentation — is required before any capital moves, and Pilot 1
does not perform that step.

## The Comparison Principle — Not a Rigid Ranking

> **Alpha must earn its place against beta, and beta must earn its place
> against cash.**

This is a standing evidentiary bias, not a rigid, mechanical ranking
hierarchy that every comparison must march through in fixed order. It means:
the more idiosyncratic and manager-dependent an exposure is, the more
evidence it owes before capital is allocated to it. Cash starts with no
such burden; beta owes more than cash; alpha (a specific, actively selected
security or position) owes more than beta. But this is a bias applied
within a real comparison, not a mandatory sequential gate — a capital
comparison in Pilot 1 does not process cash, then beta, then alpha as
isolated pairwise steps. It weighs all realistic alternatives together.

No candidate security or strategy is compared in a vacuum, and no candidate
is compared only against beta and cash in the abstract. Every capital
comparison in Pilot 1 must be run against the **full realistic Opportunity
Set** as defined in `02_OPPORTUNITY_SET.md` — which explicitly includes:

- **Current holdings / status quo** (the incumbent position, including the
  option to change nothing about it),
- **Underwritten alpha candidates** relevant to the same capital,
- **Relevant beta** exposure,
- **Treasury / cash**, and
- **DO NOTHING**, as an always-eligible member of the Opportunity Set, not
  an implicit fallback outside it.

Leaving out the incumbent holding, or leaving out DO NOTHING, is not a
valid capital comparison under this framework — a comparison that only
pits a new candidate against beta and cash, without also weighing what is
already owned and the option to do nothing, has not compared against the
full Opportunity Set and is incomplete.

> **DO NOTHING and HOLD CASH are valid outcomes.**

The evidence may simply favor an existing member of the Opportunity Set
over any new candidate. That is not a failure of the process — it is the
process working. Pilot 1 explicitly treats "no action" as a legitimate,
recordable outcome of the comparison framework, not as an absence of a
result.

## Required Outputs of a Capital Comparison

A capital comparison is not complete, and may not be recorded via
`05_DECISION_RECORD_TEMPLATE.md`, unless it identifies all three of the
following in plain language:

1. **Preferred action** — which member of the Opportunity Set the human
   judges best for this capital right now (which may be the incumbent
   holding or DO NOTHING).
2. **Next-best alternative** — which other member of the Opportunity Set
   was the closest competing option, and was therefore not chosen.
3. **Why the preferred action wins** — the specific, plain-language reasons
   the preferred action was judged superior to the next-best alternative,
   referencing the underwriting conclusions, current holdings context, or
   beta/cash comparators actually considered.

No weighted score, numeric ranking, or optimizer is used to produce these
three outputs. They are a human judgment, documented in prose.

## Improve / Compare / Test / Move

> **Improve what we own. Compare what we could own. Test alternatives
> safely. Move capital only when the evidence earns it.**

This framework applies the comparison principle above in four distinct
modes, which must not be conflated. These are modes of use, not ordered
steps or a ranking sequence:

| Mode | Question | What it authorizes |
|---|---|---|
| **Improve** | Is there a better way to hold, size, or manage what is already owned? | Nothing beyond generating an idea for review — see `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md` for current holdings context. |
| **Compare** | How does an underwritten candidate stack up against the full Opportunity Set (`02_OPPORTUNITY_SET.md`) — current holdings, relevant beta, cash, and DO NOTHING? | Nothing beyond a documented comparison identifying preferred action, next-best alternative, and rationale (see below). |
| **Test** | Can an alternative be evaluated without risking real capital or committing to it? | Manual, paper-based, or otherwise non-capital evaluation only. |
| **Move** | Has a comparison actually cleared its hurdle with sufficient evidence? | Only this mode may lead toward an eventual, separately authorized, Portfolio Action — and only when the evidence, not conviction alone, earns it. |

## Explicit Non-Automation

This comparison framework is applied manually by a human in Pilot 1. No
scoring formula, optimizer, or automated capital allocation logic is created,
modified, or implied by this document. Consistent with
`00_PILOT_OVERVIEW.md`:

> **No opaque Atlas master score or ranking engine.**

Comparisons in Pilot 1 are qualitative, documented in plain language, and
recorded through `05_DECISION_RECORD_TEMPLATE.md` when they rise to the
level of a Security Decision.
