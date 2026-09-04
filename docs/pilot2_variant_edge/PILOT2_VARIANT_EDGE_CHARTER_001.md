# PILOT 2 — VARIANT EDGE & INTENTIONAL ALLOCATION — CHARTER 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**

| | |
|---|---|
| Charter date | September 4, 2026 |
| Status | **CHARTER / BASKET DESIGN** |
| Capital | $50,000 paper/shadow, live market data |
| Architecture | **FROZEN** |

**Not to be confused with** the historical `docs/pilot2/` artifacts, which
record the **Control Validation Dry Run** (ACN / RMD / TROW / VICI / ORCL).
That was a control/system validation exercise. This is a different experiment
with a different question.

---

## 1. Why this pilot exists

Pilot 1 proved Stock Atlas could run an end-to-end decision process and
legitimately refuse to deploy capital. It demonstrated **process coherence.**

> **It did not demonstrate investment edge.**

The governing mission is to make money by finding, validating, and capturing
genuine edge. Process quality is a supporting mechanism, not the objective.
Pilot 2 attacks the objective directly.

The September 3 calibration sharpened the target: an allocation described as
*"taking a stab in the dark"* revealed that strong underwriting did not
translate into explicit allocation reasoning. That produced
`ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`. Pilot 2 is the first test of whether
those fields, filled honestly, can carry a real edge claim.

---

## 2. Primary hypothesis

> Can Stock Atlas identify a **falsifiable variant view** and use that edge
> claim to support an intentional human allocation **or refusal** versus
> competing securities, SPY, Treasury/Cash, and Do Nothing?

### The distinction Pilot 2 must draw

| | |
|---|---|
| **Attractive under Atlas assumptions** | The model likes it. Says nothing about the market being wrong. |
| **Genuine potential mispricing / edge** | An identified observable consensus, a specific variant, and a reason the gap can persist and then close. |

A candidate that is merely attractive is **not** an edge claim. Pilot 2 fails
its own test if it cannot tell the two apart.

---

## 3. Required finalist evidence

For **each** final candidate:

| Field | Requirement |
|---|---|
| Observable priced-in view | What the market currently appears to assume — stated observably, not inferred |
| Atlas variant view | Where Atlas differs, specifically |
| Why the gap can exist | A structural reason the market could be wrong here |
| Gap closer / catalyst | What would cause the gap to close |
| Horizon | Over what period |
| `allocation_wrong_if` | Observable evidence that would make the allocation wrong |
| `why_this_vs_alternatives` | Why this instead of the live alternatives |
| `why_this_size` | Why approximately this size (qualitative) |
| `why_not_this_increment` | For any unfunded finalist |
| `EXPLORATORY_LOW_RATIONALE` | Applied where rationale is genuinely absent |

> **No score is created from these fields.** They are evidence and reasoning,
> never inputs to a ranking, weighting, or sizing computation. A finalist
> missing fields is recorded honestly — never backfilled.

---

## 4. Basket — discrimination set

**10 securities + SPY + Treasury/Cash + Do Nothing.**

> ### The basket must be FROZEN before underwriting starts.

### Construction requirement

The basket must be built as a **discrimination set, not simply ten attractive
stocks.** Ten names Atlas already likes cannot falsify anything — if every
candidate is attractive, a favourable result is indistinguishable from
selection bias, and the pilot teaches nothing about edge.

A discrimination set should make it possible for the process to be **wrong in
a visible way**: it should contain names where the priced-in view is genuinely
contested, where Atlas's variant could fail, and where the honest answer may be
Treasury/Cash or Do Nothing.

### Selection authority

> **The 10 names are selected by Chris, not by Atlas.**

Atlas does not choose the basket. Generating candidate securities would be
inventing investment conclusions, and it would contaminate the hypothesis:
a basket chosen by the same system being tested cannot test that system.
This charter specifies what the set must *do*; the names are a human input.

### Freeze gate

Underwriting may not begin until:

1. 10 security names are supplied by Chris;
2. each name is resolved to a canonical Atlas security identity;
3. SPY, Treasury/Cash and Do Nothing are present as distinct alternatives;
4. the basket is written to a frozen record and hashed;
5. the frozen record is committed.

**No underwriting before basket freeze.** Adding, removing or substituting a
name after the freeze invalidates the pilot.

---

## 5. Standing constraints

| Area | Rule |
|---|---|
| Sentiment | **SHADOW ONLY.** No effect on promotion, underwriting, Stage 7, Stage 8, or allocation. |
| Portfolio context | Existing lightweight snapshot / overlap / capacity / common-driver controls where useful. **No portfolio optimizer.** |
| Architecture | **FROZEN.** Pilot 2 is a learning experiment, not a feature sprint. |
| Stage 7 | Comparison only. Emits no `PortfolioAction`. Unranked. |
| Stage 8 | Human. Refusal (`HOLD CASH` / `DO NOTHING`) remains fully legal. |
| Capital | Paper/shadow only. **NO REAL PORTFOLIO ACTION.** |
| Source privilege | The provenance/privilege question is **parked** and is not part of Pilot 2. |

Nothing in this pilot authorizes an optimizer, score, conviction metric,
ranking layer, automated sizing, execution API, agent on the capital path, or a
second market-data vendor.

---

## 6. What would make Pilot 2 a success

Success is **not** a funded position, and **not** a profitable one — the
horizon is too short and the sample is one.

Pilot 2 succeeds if it produces **a clear verdict on the hypothesis**:

- Atlas articulated at least one falsifiable variant view with an observable
  priced-in counterpart, a reason the gap can exist, and a named catalyst; and
- the human Stage 8 decision — fund *or* refuse — was **intentional and
  traceable to that edge claim** rather than to a stab in the dark.

An honest **failure** is a valid and valuable outcome: if every candidate turns
out to be "attractive under Atlas assumptions" with no defensible variant, that
is a real finding about where Atlas currently stands against its mission, and
it should be recorded as such rather than dressed up.

---

## 7. Sequence

| # | Step | State |
|---|---|---|
| 1 | Freeze cleaned Master Project Plan | DONE |
| 2 | Create Pilot 2 Charter | DONE — this document |
| 3 | Select and freeze 10-name discrimination basket | **BLOCKED — awaiting Chris** |
| 4 | Underwrite finalists (not before freeze) | not started |
| 5 | Stage 7 capital comparison | not started |
| 6 | Stage 8 paper allocation | not started |
| 7 | Pilot 2 Health Review | not started |
| 8 | Red Team | not started |
| 9 | Decide what worked, failed, or is missing | not started |
| 10 | Build nothing unless the learning earns it | standing rule |

---

**Capital status: NO REAL PORTFOLIO ACTION.**
