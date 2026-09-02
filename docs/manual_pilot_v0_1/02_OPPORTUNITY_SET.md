# 02 — Opportunity Set

## Purpose

This file defines two distinct concepts used in Stock Atlas Pilot 1 — the
**Discovery Basket** and the **Opportunity Set** — and the relationship
between them. These are not the same thing, and conflating them is a
methodology error this file exists to prevent.

## Two Distinct Concepts — Not to Be Conflated

| | Discovery Basket | Opportunity Set |
|---|---|---|
| **What it is** | An experimental discovery control — a fixed input list for stress-testing Discovery Contract v0.1. | The realistic set of alternatives actually competing for the same capital, once sufficient underwriting exists to compare them. |
| **Membership** | Frozen: exactly the 33 stocks in `09_PILOT_1_DISCOVERY_BASKET.md`. | Dynamic: current holdings, underwritten alpha candidates, relevant beta exposure, Treasury/cash, and DO NOTHING. |
| **Governed by** | `01_DISCOVERY_CONTRACT.md` | `03_CAPITAL_COMPARISON_FRAMEWORK.md` |
| **What membership implies** | Eligibility to be considered during a Discovery Cycle. Nothing about quality or investability. | Eligibility to be weighed in a capital comparison. Still not a Security Decision or Portfolio Action. |

The frozen 33-stock Pilot 1 Discovery Basket is **not** the Opportunity Set.
It is the input pool Discovery Contract v0.1 draws SURFACED candidates from.
The Opportunity Set is a different, later, broader construct that only forms
once a candidate has been underwritten and is being weighed against real
alternatives.

## Definition: Discovery Basket

The Discovery Basket is the pool of securities a Discovery Cycle is
permitted to consider. It is the raw input to Discovery Contract v0.1
(`01_DISCOVERY_CONTRACT.md`); Discovery narrows it, by human judgment, to a
SURFACED list.

Membership in the Discovery Basket is not itself a claim of quality or
investability. It means only: *this security is eligible to be considered
during a Discovery Cycle.* Nothing more.

For Pilot 1, the Discovery Basket is the **frozen 33-stock Pilot 1 Discovery
Basket** recorded in `09_PILOT_1_DISCOVERY_BASKET.md` — an **experimental
discovery control**, deliberately narrow, used to stress-test whether the
Discovery Contract behaves sensibly across different sectors and business
models.

> **Test narrowly. Discover broadly.**

Pilot 1 tests the Discovery → Underwriting → Decision method *narrowly* — on
a small, fixed, diversified-by-sector basket — precisely so that "discover
broadly" can be exercised safely and legibly within that narrow test, without
the noise of an unbounded universe.

## Definition: Opportunity Set

The Opportunity Set is the realistic set of alternatives that are actually
competing for the same unit of capital at the moment a capital comparison is
made (`03_CAPITAL_COMPARISON_FRAMEWORK.md`). It forms only after sufficient
underwriting exists to populate it with real candidates — it is not
pre-populated by the Discovery Basket, and it is not frozen the way the
Discovery Basket is.

A capital comparison's Opportunity Set may include:

- **Current holdings / status quo** — what is already owned, including the
  option of simply continuing to hold it unchanged. Captured via
  `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md`.
- **Underwritten alpha candidates** — securities that have reached the
  UNDERWRITTEN state (`01_DISCOVERY_CONTRACT.md`) with a recorded
  conclusion, e.g. the results in `09_PILOT_1_DISCOVERY_BASKET.md`.
- **Relevant beta** — a comparable broad, low-cost market exposure judged
  relevant to the comparison at hand.
- **Treasury / cash** — the cash or cash-equivalent alternative.
- **DO NOTHING** — explicitly always an eligible member of the Opportunity
  Set, not an implicit default outside it.

A security does not enter the Opportunity Set merely by being SURFACED, or
merely by appearing in the Discovery Basket. It enters only once it is
UNDERWRITTEN and is actually being weighed as a realistic alternative for
specific capital.

## How the Two Relate

1. The Discovery Basket (frozen, 33 stocks) is the input to a Discovery
   Cycle.
2. Discovery Contract v0.1 narrows it to SURFACED, then PROMOTED, then
   UNDERWRITTEN candidates (`01_DISCOVERY_CONTRACT.md`).
3. An UNDERWRITTEN candidate *may* subsequently become one member of an
   Opportunity Set, alongside current holdings, relevant beta, cash, and DO
   NOTHING — but only when an actual capital comparison is being performed
   for it under `03_CAPITAL_COMPARISON_FRAMEWORK.md`.

The Discovery Basket answers "what did we look at?" The Opportunity Set
answers "what is actually competing for this capital, right now?" These are
different questions with different scopes, and Pilot 1 keeps them separate.

## Relationship of the Discovery Basket to a Production Discovery Universe

The Pilot 1 Discovery Basket is explicitly **not** a preview or a subset
selection of a future production universe in any statistically meaningful
sense. It is a controlled test fixture.

> The eventual production Discovery Universe may be much broader.

Nothing about a security's inclusion or exclusion from the Pilot 1 Discovery
Basket implies anything about its future eligibility, priority, or treatment
in a production Discovery Universe, and nothing about it implies membership
in any Opportunity Set. Expansion of the Discovery Basket beyond Pilot 1 is a
decision outside the scope of this document set and outside the scope of
this pilot.

## Constraints

- The **Discovery Basket** for Pilot 1 is **frozen**: no additions,
  removals, or substitutions during the pilot. See
  `09_PILOT_1_DISCOVERY_BASKET.md` and `08_PILOT_READINESS_FREEZE_GATE.md`.
- The **Opportunity Set** is not frozen and is not a fixed list — it is
  reconstructed for each capital comparison from whatever current holdings,
  underwritten candidates, relevant beta, and cash context actually apply at
  that time. It always includes DO NOTHING as an eligible member.
- Neither the Discovery Basket nor any Opportunity Set is derived from,
  filtered by, or scored by any production SEC/XBRL/market-data pipeline
  logic. Both are assembled and populated manually by a human.
- Neither construct carries a ranking or ordering. Sector groupings in
  `09_PILOT_1_DISCOVERY_BASKET.md` are for legibility only and do not imply
  relative priority; membership in an Opportunity Set does not imply
  relative priority either — see `03_CAPITAL_COMPARISON_FRAMEWORK.md` for
  how members are actually compared.
