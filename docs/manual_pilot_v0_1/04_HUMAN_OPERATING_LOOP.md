# 04 — Human Operating Loop

## Purpose

This file defines the manual operating cadence for Pilot 1: who does what,
in what order, and how often. Every step in this loop is performed by a
human. Nothing in this loop is automated.

## Loop Stages

The operating loop mirrors the governing sequence from `00_PILOT_OVERVIEW.md`:

> **Method → Decision → Learning → Automation.**

Pilot 1 occupies **Method**, **Decision**, and the human-performed part of
**Learning** — a later, human-run Outcome Review and Learning step is part
of the full loop below. **Automation** (building systems on top of a proven
method) is explicitly out of scope for this package and is not initiated,
described, or implied by anything in this document set. Learning in Pilot 1
is a human reviewing outcomes and writing notes — it is never an automated
or algorithmic learning process.

The full manual loop, in order, is:

**Discovery → Promotion/Reject → Underwriting → Security Decision →
Opportunity Set → Sandbox → Capital Comparison → Human Portfolio Decision →
Decision Record → (later) Human Outcome Review → Learning.**

Every stage below is performed by a human. None is automated.

### Stage 1 — Discovery (human)

- Human reviews the frozen Discovery Basket (`02_OPPORTUNITY_SET.md`,
  `09_PILOT_1_DISCOVERY_BASKET.md`).
- Human applies Discovery Contract v0.1 (`01_DISCOVERY_CONTRACT.md`) and
  records SURFACED securities with a plain-language reason.

### Stage 2 — Promotion / Reject (human)

- Human selects, from SURFACED, which securities are PROMOTED FOR
  UNDERWRITING given available underwriting time, and which are rejected
  for this cycle.
- Promoted securities proceed to Stage 3. Rejected/not-promoted SURFACED
  securities are recorded as SURFACED — WATCH and proceed no further this
  cycle.

### Stage 3 — Underwriting (human)

- Human performs a deep, manual review of each PROMOTED security.
- Human records a qualitative underwriting conclusion per security.
  Underwriting conclusions in Pilot 1 are categorical and qualitative (e.g.
  "ATTRACTIVE WITH MATERIAL UNCERTAINTY," "NEUTRAL / INSUFFICIENT EDGE") —
  not numeric scores.
- Underwriting output is UNDERWRITTEN, not DECIDED (`01_DISCOVERY_CONTRACT.md`).

### Stage 4 — Security Decision (human)

- For an UNDERWRITTEN security, the human forms an explicit view on the
  security in isolation (e.g. "this looks attractive enough to weigh against
  real alternatives").
- This is a **Security Decision**, not a Portfolio Action
  (`03_CAPITAL_COMPARISON_FRAMEWORK.md`). It authorizes moving the security
  into an Opportunity Set for comparison — nothing more.

### Stage 5 — Opportunity Set (human)

- Human assembles the realistic Opportunity Set this Security Decision
  should actually be weighed against, per `02_OPPORTUNITY_SET.md`: current
  holdings/status quo, other relevant underwritten alpha candidates,
  relevant beta, Treasury/cash, and DO NOTHING.
- Populated using `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md` for current
  holdings context.

### Stage 6 — Sandbox (human)

- Human tests the candidate against the Opportunity Set without committing
  real capital — the "Test alternatives safely" mode of
  `03_CAPITAL_COMPARISON_FRAMEWORK.md`. This is manual, paper-based, or
  otherwise non-capital evaluation only.

### Stage 7 — Capital Comparison (human)

- Human applies `03_CAPITAL_COMPARISON_FRAMEWORK.md` across the full
  Opportunity Set and records the required outputs: preferred action,
  next-best alternative, and why the preferred action wins.

### Stage 8 — Human Portfolio Decision (human)

- Human decides whether the Capital Comparison's preferred action justifies
  an actual Portfolio Action. This is the only stage that may authorize
  moving real capital, and it is always a distinct, explicit human decision
  — never inferred automatically from a Security Decision or a Capital
  Comparison result.

### Stage 9 — Decision Record (human)

- Human records the Security Decision, the Capital Comparison outputs, and
  any Portfolio Decision using `05_DECISION_RECORD_TEMPLATE.md`.
- Decision Records are immutable once written; later re-evaluation is
  appended as a dated review entry, never edited into the original text.

### Stage 10 — Human Outcome Review (human, later)

- At a later date (cadence set by the human operator, not by this
  document), the human reviews how prior decisions actually played out,
  using `06_PILOT_HEALTH_SCORECARD.md` for process health and an updated
  `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md` for current context.
- Review is appended to existing Decision Records; originals are never
  altered.

### Stage 11 — Learning (human)

- Human draws explicit, written lessons from the Outcome Review — about the
  Discovery Contract, the Capital Comparison Framework, or the process
  itself — and records them as notes for a possible future version of this
  method.
- Learning in Pilot 1 is manual and human-authored only. No automated
  learning, model training, or algorithmic feedback loop is initiated,
  described, or implied by this stage. Any future automation of any part of
  this loop follows only after the method has been proven manually
  (**Method → Decision → Learning → Automation**; **Prove the method
  manually before automating the method.**)

## Roles

Pilot 1 is a single-human-operator pilot. One person may perform all roles
below, but the roles are conceptually distinct and should be recorded as
such in the Decision Record's actor field:

| Role | Responsibility |
|---|---|
| **Discovery operator** | Applies the Discovery Contract to the Discovery Basket; handles Promotion/Reject. |
| **Underwriter** | Performs deep review and records underwriting conclusions. |
| **Decision-maker** | Records Security Decisions, assembles Opportunity Sets, and runs Capital Comparisons. |
| **Portfolio decision-maker** | Makes the Human Portfolio Decision — the only role that may authorize an actual Portfolio Action. |
| **Reviewer** | Periodically performs Human Outcome Review, records Learning, and appends to Decision Records. |

## Explicit Boundaries on This Loop

- This loop does not advance Stock Atlas phases. Phase advancement is a
  decision made by the human operator outside this document set.
- This loop does not modify, call, or depend on any production
  SEC/XBRL/market-data logic in this repository.
- This loop does not introduce scoring, ranking, optimization, brokerage
  connectivity, or automated learning of any kind — including at the
  Learning stage, which is human-authored notes only.
- This loop stops — it does not silently continue — when the freeze gate in
  `08_PILOT_READINESS_FREEZE_GATE.md` has not been cleared.
