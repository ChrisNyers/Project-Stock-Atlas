# 00 — Pilot Overview: Stock Atlas Manual Pilot v0.1

## Status

Documentation-only artifact. No production code, scoring logic, ranking engine,
brokerage integration, or automated decision system is created, modified, or
implied by this package.

## What This Pilot Is

Stock Atlas Pilot 1 is a **manual, human-operated** exercise in applying a
disciplined Discovery → Underwriting → Decision process to a small, frozen set
of securities. It exists to test the *method*, not to produce investment
recommendations, not to generate alpha, and not to validate any automated
system.

Everything in this pilot is performed by a human, recorded by hand (with this
repository as the record-keeping substrate), and reviewed by a human. Nothing
here executes trades, connects to a brokerage, or ranks securities against
each other by an opaque composite score.

## Governing Principles

These principles govern every file in this package and every decision made
under Pilot 1. They are not aspirational — they are constraints.

1. **Test narrowly. Discover broadly. Underwrite deeply. Allocate selectively.**
2. **Discovery allocates attention, not capital.**
3. **SURFACED ≠ UNDERWRITTEN ≠ DECIDED.**
4. **Security Decision ≠ Portfolio Action.**
5. **Alpha must earn its place against beta, and beta must earn its place
   against cash.**
6. **Improve what we own. Compare what we could own. Test alternatives
   safely. Move capital only when the evidence earns it.**
7. **Technical success is not project success. Decision improvement is
   project success.**
8. **Method → Decision → Learning → Automation.**
9. **Prove the method manually before automating the method.**
10. **No opaque Atlas master score or ranking engine.**
11. **DO NOTHING and HOLD CASH are valid outcomes.**
12. **Portfolio inputs are user-controlled and privacy-minimized. No
    brokerage credentials or direct brokerage integration.**
13. **"What is priced in?" remains an OPEN METHODOLOGY QUESTION.**
14. **Original Decision Records are immutable; later reviews are appended.**

## What Pilot 1 Is Not

- It is not a buy list.
- It is not a portfolio construction system.
- It is not a scoring or ranking engine.
- It is not connected to any brokerage or execution venue.
- It is not an automated or algorithmic decision process.
- It does not advance to production or to later phases on its own — phase
  advancement is a human decision, made outside this document set.

## Package Contents

| File | Purpose |
|---|---|
| `00_PILOT_OVERVIEW.md` | This file — scope, principles, and package map. |
| `01_DISCOVERY_CONTRACT.md` | Defines what Discovery is and is not, and its output contract. |
| `02_OPPORTUNITY_SET.md` | Distinguishes the frozen Discovery Basket from the dynamic Opportunity Set; defines both. |
| `03_CAPITAL_COMPARISON_FRAMEWORK.md` | Defines how the full Opportunity Set — incumbent/status quo, alpha, beta, cash, DO NOTHING — is weighed before any capital moves. |
| `04_HUMAN_OPERATING_LOOP.md` | Defines the eleven-stage manual loop, roles, and cadence for Pilot 1. |
| `05_DECISION_RECORD_TEMPLATE.md` | The immutable record template used for every decision made in the pilot. |
| `06_PILOT_HEALTH_SCORECARD.md` | How the health of the pilot process itself (not returns) is tracked. |
| `07_PRIVACY_PRESERVING_PORTFOLIO_SNAPSHOT.md` | How portfolio state is captured without brokerage integration or credential exposure. |
| `08_PILOT_READINESS_FREEZE_GATE.md` | The freeze/readiness gate a human must clear before Pilot 1 can be considered complete. |
| `09_PILOT_1_DISCOVERY_BASKET.md` | The frozen 33-stock basket and the first manual Discovery Cycle results. |

## Scope Boundary

This package documents process and records results already produced by
manual human work. It does not itself perform underwriting, does not assign
new conclusions, and does not extend or reinterpret the results recorded in
`09_PILOT_1_DISCOVERY_BASKET.md` beyond what was provided by the human
operator.
