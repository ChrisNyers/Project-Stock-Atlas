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

---

# PILOT 2 FEEDBACK LOOPS

*Added to this charter September 4, 2026. Sections 1–7 above are unchanged.*

Pilot 2 uses three feedback loops.

Only **Loop A** is required to run the initial Pilot 2 decision cycle. Loops B
and C run **only when their triggering evidence exists.**

Feedback may change the **next cycle's questions.**

Feedback must **not**:

- rewrite a frozen record
- change architecture by default
- automatically add features
- allocate capital
- use hindsight to repair prior reasoning

---

## 8. Loop A — Decision Loop

**When:** during the same sitting as Stage 8.

> ### Primary question: Did we allocate or refuse capital on purpose?

### Capture

For every relevant finalist, preserve:

- observable priced-in view
- Atlas variant
- why the gap can exist
- `allocation_wrong_if`
- fresh-price / session bind
- Stage 7 status
- `why_this_vs_alternatives`
- `why_this_size`
- `why_not_this_increment`
- `EXPLORATORY_LOW_RATIONALE` where applicable

Also record:

> **What did Atlas cause the human decision-maker(s) to do or not do
> differently from gut alone?**

This is the **primary Pilot 2 decision-usefulness question.**

### Interpretation

If funded names have substantially **interchangeable** rationale or variant
language, treat that as evidence that the decision remains **noisy**.

**Do not solve that automatically by adding a score.**

A higher modeled return is **not** evidence of intentional allocation by
itself.

---

## 9. Loop B — Revisit Loop

**When:** only when a previously defined revisit trigger fires.

Valid triggers: a named price condition · a TIME/date trigger · a named
operating/thesis fact · a catalyst previously defined in the frozen record.

> **Do not revisit merely because someone wants to check the stock.**

> ### Primary question: Is the standing conclusion still valid under current evidence?

### Path

```
trigger → fresh price/calendar bind → same Stage 7 door → new decision record
```

**The prior record remains untouched.**

### Capture

- trigger type
- trigger evidence
- current price/session bind
- what changed or did not change in the priced-in view
- what changed or did not change in the Atlas variant
- updated uncertainty
- new Stage 7 conclusion
- new Stage 8 decision where required, including HOLD, cash, or refusal

### Prohibition

Do **not** use current price action or new information to rewrite the original
`why_this_vs_alternatives`, `why_this_size`, variant claim, confidence, or
decision record.

**Every revisit creates a new point-in-time record.**

A future Watchman capability may automate trigger detection. **Pilot 2 requires
only the existing human/checklist process.**

---

## 10. Loop C — Outcome Loop

**When:** later, at the horizon specified in the original variant thesis, or at
the named catalyst / gap-closing event.

> **Do not run so early that one earnings print or price move is treated as
> proof of edge.**

> ### Primary question: Was the claimed edge real, or was the research merely coherent?

Evaluate using the **frozen decision record** and subsequent evidence.

### Four broad outcome categories

| Original decision | Thesis held | Thesis broke |
|---|---|---|
| **Funded** | Possible edge — one observation only | Edge claim wrong; preserve the record |
| **Refused / Cash / SPY** | Good refusal or possible missed edge | Correct refusal |

Compare realized/path outcomes against the **actual alternatives identified at
the original decision** — SPY, Treasury/Cash, Do Nothing.

> **Do not compare against a hindsight-created portfolio or benchmark.**

### Feedback allowed

- variant language was too thin
- modeled return anchored the decision
- overlap should have blocked the allocation
- stated gap closer never occurred
- the market expectation was misidentified

### Feedback prohibited

- stock rose, therefore add sentiment
- stock fell, therefore loosen the cash hurdle
- one winner proves the model
- one loser disproves the architecture
- last outcome automatically triggers a new module

> **One outcome is one observation.**

---

## 11. How feedback changes the next cycle

After Pilot 2, use **only preserved records** to ask:

1. How many funded lines contained a genuine variant rather than a cheapness story?
2. How many allocations were marked `EXPLORATORY_LOW_RATIONALE`?
3. Did SPY, Treasury/Cash, or Do Nothing win for a stated reason?
4. Did lookalike candidates receive different treatment because of variant quality?
5. Did any revisit trigger fire and correctly re-enter through fresh data?
6. In shadow only, would sentiment information actually have changed a decision?
7. What did Atlas cause the human decision-maker(s) to do differently from gut alone?

Then choose **one** disposition:

| Disposition | Meaning |
|---|---|
| **`IGNORE`** | **Default.** No change warranted. |
| **`CHANGE`** | Adjust existing process language or underwriting discipline. **Do not assume code changes are required.** |
| **`ADD`** | Use an already-specified capability, or add a narrowly justified control, only when the evidence supports it. |
| **`REMOVE`** | Drop a process element or hypothesis that repeatedly adds noise without decision value. |

> **Building is the exception.**

---

## 12. Do not create as feedback loops

- live P&L dashboard as a Stage 8 input
- agent voting on capital
- rolling model changes based on last week's winner
- sentiment promotion because it happened to be recorded
- a separate feature-idea loop
- automatic allocation changes
- hindsight rewriting

---

## 13. Minimum Pilot 2 record set

Each Pilot 2 cycle produces:

1. **Frozen Stage 7 packet + fresh-price bind**
2. **Stage 8 + Allocation Bridge or exploratory flag**
3. **Defined revisit triggers**
4. **One-page Loop Log**

The Loop Log contains:

| Section | Contents |
|---|---|
| **Decision** | Loop A result |
| **Revisit** | Loop B result — only if triggered |
| **Outcome** | Loop C result — only when due |

> If the Loop Log cannot answer **"What did Atlas cause us to do
> differently?"**, then the cycle demonstrated **process mechanics but not
> decision edge.**

---

## Governing summary

> **Loop A proves intention.
> Loop B keeps old labels honest.
> Loop C tests whether the variant was a guess.
> None of them can spend money or rewrite yesterday.**

---

# PILOT 2 FORMAL VERDICT STATES

*Appended to this charter September 4, 2026. All prior content is unchanged.*

At Pilot 2 closeout, assign **exactly one** of the following.

---

## 14. `PASS`

Use when the primary Pilot 2 hypothesis is **materially demonstrated**.

### Minimum evidence

- Atlas can state a credible **priced-in view** and a **falsifiable variant**;
- at least one **superficially comparable** opportunity receives different
  treatment **because of variant quality rather than modeled-return ranking**;
- funded decisions are intentional and supported by genuine Allocation Bridge
  rationale;
- unfunded finalists are refused **for stated reasons**;
- SPY, Treasury/Cash and Do Nothing remain **genuine** alternatives;
- the fresh-price control holds;
- human Stage 8 authority remains intact;
- **a later reviewer can reconstruct what Atlas believed the edge was at the
  decision date.**

> **A PASS does not prove investment edge statistically.** It means Pilot 2
> successfully demonstrated the intended edge-identification and
> intentional-allocation *behavior*.

---

## 15. `PASS WITH FINDINGS`

Use when the core hypothesis is **substantially demonstrated** but the pilot
exposes **one material weakness** that should inform the next learning cycle.

### Examples

- variant views remain too thin or generic;
- Allocation Bridge language is partly boilerplate;
- significant capital remains `EXPLORATORY_LOW_RATIONALE`;
- portfolio overlap changes an otherwise attractive increment;
- cash/SPY wins because no candidate demonstrates sufficient edge;
- a narrow process weakness is exposed.

**Identify the single most important finding.**

> **`PASS WITH FINDINGS` is not automatic authorization for new software or
> architecture.** The default response remains **`IGNORE`** unless the evidence
> clearly earns `CHANGE`, `ADD`, or `REMOVE` (§11).

---

## 16. `FAIL`

Use when Pilot 2 **does not demonstrate** the primary hypothesis.

### Examples

- allocations still feel like a stab in the dark;
- higher modeled return effectively determines the allocation;
- "cheap" substitutes for a real variant thesis;
- priced-in assumptions cannot be stated credibly;
- funded names have interchangeable rationale;
- Atlas cannot explain what it believes the market is getting wrong;
- the Allocation Bridge becomes boilerplate;
- the pilot turns into a feature-development exercise.

> **FAIL is a valid learning outcome.**

Do **not** repair a FAIL by rewriting frozen records or adding features
mid-pilot.

---

## 17. Relationship to the feedback loops

The formal verdict is assigned using evidence from the **preserved Pilot 2
records**.

| Loop | Role in the verdict |
|---|---|
| **Loop A** | **Required** for the initial Pilot 2 verdict |
| **Loop B** | Included **only if** a revisit trigger has actually fired by closeout |
| **Loop C** | Included **only if** the stated horizon or catalyst has occurred |

**Pilot 2 does not wait artificially for Loops B or C in order to assign the
initial verdict.**

A later Loop B or Loop C observation may create a **new learning record**, but
it **does not rewrite the original Pilot 2 verdict.**

---

# PILOT 2 FROZEN DISCRIMINATION BASKET

*Appended September 4, 2026. All prior charter content is unchanged.*

| | |
|---|---|
| Pilot | Pilot 2 — Variant Edge & Intentional Allocation |
| Capital | $50,000 paper/shadow |
| Freeze date | September 4, 2026 |

> ## Basket status: `FROZEN / PRE-REGISTERED`

---

## 18. The frozen 10-name basket

| # | Ticker |
|---|---|
| 1 | `FIS` |
| 2 | `FISV` |
| 3 | `MELI` |
| 4 | `JD` |
| 5 | `ADBE` |
| 6 | `SNOW` |
| 7 | `WCC` |
| 8 | `GLNG` |
| 9 | `NTR` |
| 10 | `CVS` |

### Live capital alternatives

| Alternative | Role |
|---|---|
| **SPY** | beta |
| **Treasury/Cash** | productive waiting capital |
| **Do Nothing** | status quo |

All three remain **genuine, live alternatives** throughout Pilot 2. Any of them
winning is a valid outcome.

---

## 19. What these securities are — and are not

These securities are **test inputs for Pilot 2.** They are **not**
recommendations, endorsements, rankings, or preliminary investment
conclusions.

**No security begins Pilot 2 as:**

- preferred
- promoted
- eligible
- underwritten
- funded

The basket's purpose is to test whether Stock Atlas can **discriminate among
superficially attractive opportunities** by identifying a genuine falsifiable
variant view.

The list order above is **transcription order only.** It carries no ranking,
priority, or preference, and must never be read as one.

---

## 20. Freeze rule

After this record is committed:

- **no additions**
- **no substitutions**
- **no removals**
- **no rebalancing** of the test basket

— unless an **explicit documented scope change** is approved.

A technical issue alone should **first be evaluated against the existing frozen
architecture.** Do not expand architecture merely to preserve a candidate.

> If a genuine operational blocker eventually requires a substitution,
> **stop and surface it** before changing the frozen basket.

The commit recording this section is the freeze anchor: the basket's content
and its freeze time are fixed by that commit, and any later change is visible
as a subsequent commit rather than a silent edit.

---

## 21. Governing Pilot 2 rule

> **People and agents may surface ideas. Atlas must prove a variant before an
> idea can compete for capital. Humans allocate — including to cash, beta, or
> nothing.**

> ### Surface does not mean promote.
> ### Modeled return does not prove edge.

---

**Capital status: NO REAL PORTFOLIO ACTION.**
