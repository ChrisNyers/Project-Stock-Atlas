# 01 — Discovery Contract v0.1

## Purpose

This file defines what "Discovery" means inside Stock Atlas Pilot 1, what it
produces, and — just as importantly — what it explicitly does not produce.
Discovery is the first stage of the pipeline described in
`00_PILOT_OVERVIEW.md`: **Test narrowly. Discover broadly. Underwrite deeply.
Allocate selectively.**

## Core Rule

> **Discovery allocates attention, not capital.**

Discovery's only output is a claim of the form: *"a human should spend
underwriting time looking at this security."* Discovery does not say a
security is good, cheap, attractive, or investable. It says only that it is
worth someone's attention.

## The Three-State Contract

> **SURFACED ≠ UNDERWRITTEN ≠ DECIDED.**

Every security that passes through the pilot process occupies exactly one of
these states at any point in time, and each state has a distinct meaning:

| State | Meaning | Who assigns it | What it authorizes |
|---|---|---|---|
| **SURFACED** | A human, applying Discovery Contract v0.1, judged this security worth underwriting attention. | Human, during a Discovery Cycle. | Nothing beyond further review. Not a signal to buy, hold, or avoid. |
| **UNDERWRITTEN** | A human completed a deep review of the security and recorded a qualitative underwriting conclusion. | Human, during underwriting. | Nothing beyond informing a decision. Underwriting is analysis, not action. |
| **DECIDED** | A human made an explicit Security Decision, recorded via `05_DECISION_RECORD_TEMPLATE.md`. | Human, via a Decision Record. | Nothing by itself — see `03_CAPITAL_COMPARISON_FRAMEWORK.md`: **Security Decision ≠ Portfolio Action.** |

No security may skip a state. A security cannot be UNDERWRITTEN without
first being SURFACED, and cannot be DECIDED without first being
UNDERWRITTEN.

## What Discovery Operates On

Discovery draws from the **Discovery Basket**, not from an Opportunity Set.
For Pilot 1 the Discovery Basket is the frozen 33-stock experimental
discovery control recorded in `09_PILOT_1_DISCOVERY_BASKET.md`, plus any
external ideas the human operator is permitted to bring in and considers
during a cycle. Externally sourced ideas are subject to the same contract
and the same three states as basket members, and must be recorded with the
same plain-language reason.

The **Opportunity Set** (`02_OPPORTUNITY_SET.md`) is strictly downstream of
Discovery. It does not exist for a candidate until sufficient underwriting
has occurred, and Discovery neither reads from it nor adds to it.

## What Discovery Is

- A broad, deliberately low-bar filter over the Discovery Basket, intended
  to catch anything plausibly worth a closer look.
- Manual in Pilot 1: a human reviews the Discovery Basket and records which
  securities are SURFACED, and why, in plain language.
- Explicitly permitted to surface securities that later turn out, on
  underwriting, to be uninteresting. A high false-positive rate in Discovery
  is acceptable and expected — the cost of underwriting attention is the
  only cost Discovery spends.

## What Discovery Is Not

- **Not a ranking engine.** Discovery does not produce a sorted list, a
  composite score, or a single number representing quality. There is **no
  opaque Atlas master score.**
- **Not an allocation decision.** Nothing that is SURFACED is thereby
  entitled to capital.
- **Not a prediction of returns.** Discovery does not estimate expected
  return, fair value, or price target.
- **Not automated in Pilot 1.** Discovery Contract v0.1 is applied by a
  human, by hand. Any future automation of Discovery follows only after the
  method has been proven manually (**Method → Decision → Learning →
  Automation**; **Prove the method manually before automating the method.**)

## Discovery Cycle Output Format

A Discovery Cycle produces, at minimum:

1. **SURFACED** — the list of securities a human judged worth underwriting
   attention, drawn from the Discovery Basket (plus any permitted external
   ideas considered in the cycle).
2. **PROMOTED FOR FIRST UNDERWRITING** — the subset of SURFACED securities a
   human has chosen to actually spend underwriting effort on in this cycle,
   given finite underwriting capacity. This is a capacity-driven human
   choice, not a further scoring step.
3. **SURFACED — WATCH** — SURFACED securities not promoted for underwriting
   in this cycle. They remain SURFACED, not UNDERWRITTEN, and carry no
   conclusion.

See `09_PILOT_1_DISCOVERY_BASKET.md` for the first applied instance of this
contract.

## Open Methodology Question

> **"What is priced in?" remains an OPEN METHODOLOGY QUESTION.**

Discovery Contract v0.1 does not resolve, and does not attempt to resolve,
the question of what information or expectation is already reflected in a
security's price. Discovery criteria in Pilot 1 are qualitative and
human-judged for this reason — a quantitative Discovery filter would
implicitly assume an answer to this open question that has not been settled.
