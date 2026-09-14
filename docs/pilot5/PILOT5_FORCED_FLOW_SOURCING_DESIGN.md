# PILOT 5 — FORCED-FLOW DISCOVERY SOURCING DESIGN

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Sourcing design only. No candidates. No company underwriting. No
> architecture change. No permanent fields. No scoring. No new engine.
> No sentiment activation. No Batch 001.

| | |
|---|---|
| Date | September 14, 2026 |
| Pilot | Pilot 5 — `FORCED_FLOW / OWNERSHIP_DISLOCATION` |
| Governed by | `pilot3/PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md` §10-§12 |
| Purpose | Define where and how to look — not what to find |

**Numbering note, restated:** this is **Pilot 5**. `docs/pilot4/`
holds a separate, complete, frozen, unrelated pilot (September 2, 2026
— the COST/PH/AMGN incumbent-substitution test). This document does not
touch it.

---

## 1. Discovery principle

> Who may be compelled to transact, why, when, and in what size?

**Not**: *which stock has recently fallen?* Pilot 5 searches first for
the constraint or ownership change; only afterward does it identify
affected securities. A price move is a symptom to be explained, not a
starting point to be rationalized backward into a forced-flow story.

---

## 2. Primary hunting areas

**Search lenses only — not a permanent taxonomy.** Quality governs over
category diversity (§3): if one lens produces nothing credible, Pilot
5's first batch may contain zero examples from it. Three high-quality
situations beat three diversified-but-weak ones.

**A. Shareholder mismatch / distributed securities.** Spin-offs; merger
distributions; restructuring distributions; bankruptcy-emergence
ownership; securities received by holders who did not intentionally
choose them. Core question: *did investors receive a security they may
be structurally unwilling or unable to hold?*

**B. Mechanical benchmark / mandate flow.** Index additions/deletions;
index reconstitutions; benchmark changes; mandate eligibility changes;
market-cap or liquidity threshold changes; institutional-policy
constraints. Core question: *does an identifiable group have to
transact regardless of its view of intrinsic value?*

**C. Holder-specific forced or highly constrained selling.** Fund
liquidation; fund redemption pressure; concentrated-holder exit; lockup
expiration; mandate change; tax-related selling; forced deleveraging;
portfolio restructuring. Core question: *is supply entering the market
because of the holder's circumstances rather than deterioration in the
underlying company?*

---

## 3. Quality before category diversity

Do not force one example from each mechanism class. If a category
produces no credible opportunity, no candidate is manufactured for
experimental symmetry. **Prefer three high-quality situations over
three perfectly diversified but weak ones.**

---

## 4. Primary public source classes

Original/public evidence is preferred wherever possible; secondary
news/search/AI may help *discover* an event, but every surfaced
opportunity is traced back to original evidence where possible (§9).

- **Corporate filings** — SEC filings; issuer investor-relations
  releases; spin-off registration filings; merger/proxy materials;
  restructuring documents; prospectuses; ownership filings.
- **Index/benchmark sources** — official index-provider announcements;
  methodology/reconstitution notices; exchange announcements where
  relevant.
- **Holder/fund sources** — fund liquidation notices; fund disclosures;
  shareholder ownership filings; Schedule 13D/13G amendments where
  relevant; public institutional disclosures.
- **Corporate-action sources** — issuer announcements; exchange
  notices; regulatory filings.

---

## 5. Existing technology/tools that can assist

No source receives privilege; no new infrastructure is built merely to
run the experiment. Potential discovery contributors, used flexibly:

- Grok Scout (new search posture — §11)
- ChatGPT/web research
- human/manual observation (§12)
- issuer/SEC searches (`sec_adapter.py` and direct EDGAR fetches, the
  same tooling used throughout Pilot 3)
- public index-provider announcements
- simple scripts/search automation where useful
- existing public market data (`market_data_providers.py`,
  `live_session_calendar.py`, `live_price_binding.py` — Gate B, unchanged)

---

## 6. Initial opportunity questions

Answered **before** Atlas spends meaningful research effort. Questions
only — no permanent fields or scores.

**Constraint:** (1) who is potentially forced or strongly incentivized
to transact? (2) why? (3) can they avoid or delay the transaction?

**Size:** (4) approximately how many shares/securities could be
affected? (5) is that meaningful relative to normal trading volume,
public float, and natural market liquidity?

**Timing:** (6) when did the constraint become known? (7) when is the
transaction likely to occur? (8) is the flow upcoming, occurring, or
largely complete?

**Economics:** (9) have underlying business fundamentals materially
changed? (10) could the observed price move instead be economically
justified?

**Recognition:** (11) has price already materially incorporated the
event? (12) is enough potential mispricing left to justify further
Atlas work?

**Expression:** (13) if the economic thesis is correct, is the affected
security actually the best way to capture it?

**Falsification:** (14) what is the cheapest fact that could show the
apparent forced-flow thesis is wrong?

---

## 7. Flow-magnitude approach

Where data permit, a **simple comparison**: estimated constrained shares
versus ordinary trading liquidity — to judge whether the potential flow
is economically capable of distorting price. **No proprietary flow
score is created.** Judgment governs: a large forced transaction in an
extremely liquid security may be irrelevant; a smaller forced
transaction in a thinly traded security may matter materially. (Pilot
3 precedent for this kind of judgment call: SAIA's read-through triage
and TCS's liquidity finding both weighed flow/volume context
qualitatively rather than through a formal metric.)

---

## 8. Fundamental-separation approach

The ideal Pilot 5 setup resembles **ownership/flow changed materially
while underlying economics changed little.** Be skeptical where
earnings collapsed, leverage worsened, regulation changed materially,
competitive position deteriorated, management cut guidance, or
fundamental value clearly changed at the same time. **Forced selling is
not automatically mispricing** — the same discipline this pilot's
predecessor applied when it refused to credit growth or leverage
improvement alone (NNBR's dilution-earnback test; TCS's "not evaluated
merely on whether leverage improved" standard) carries forward
unchanged into distinguishing genuine dislocation from a security that
is simply going down for a good reason.

---

## 9. Original-source discipline

For every surfaced situation: **what is the original public
information?** Then distinguish original evidence, interpretation,
repetition/echo, and market reaction. Company release → article →
analyst comment → social discussion is **not** counted as multiple
independent signals. **No new provenance system is required — existing
provenance discipline remains sufficient**, the same discipline applied
throughout Pilot 3 (e.g., tracing NNBR's "$89 million paid off"
press-release shorthand back to the actual Exchange Agreement; tracing
SAIA's market reaction back to its own contemporaneous 8-K rather than
ODFL's).

---

## 10. Best-expression question

Before committing significant research effort: **if this economic
insight is right, is this security the cleanest way to be paid?**
Potential alternatives: another equity; parent; spin-off; competitor;
supplier; sector ETF; broader beta; Treasury/Cash; Do Nothing. **No
optimizer is built.** The surfaced security is only the first expression
considered — this question was carried forward explicitly from the
Pilot 3 closeout (§8 of `PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md`) as
an unresolved gap no Pilot 3 record tested.

---

## 11. Discovery-clock approach

Pilot 5 consciously asks: **are we early enough?** Observed
qualitatively: when original evidence appeared; when price responded;
when discovery occurred; whether meaningful opportunity remains. **This
is learning only — no timing engine is built.** Where useful, an
opportunity may be described as *before recognition*, *during
recognition*, or *after recognition* — a temporary Pilot 5 learning
observation, not a permanent canonical field (per the closeout's §9).

**Pilot 3 precedent for why this matters**: TCS's own September 10
guidance raise and the market's ~+11% reaction over the following days,
and SAIA's same-day-vs-T+1 reaction pattern, are both direct evidence
that by the time Atlas typically engages with a discovery-sourced hook,
meaningful recognition may already have occurred. Pilot 5's forced-flow
mechanism is chosen partly because a flow-driven dislocation has a more
identifiable *start* (the constraint event) than a narrative-driven one,
which may make "are we early enough" easier to answer qualitatively.

---

## 12. Proposed Scout search posture

Scout should **not** receive: *"Find five forced-flow stocks."*

Instead:

> Find current or upcoming situations where identifiable investors may
> be compelled or strongly incentivized to transact for reasons not
> primarily related to the underlying business fundamentals. Begin with
> the constraint or ownership event, identify the original public
> evidence, estimate whether the potential flow could matter relative
> to liquidity, identify affected securities, state the cheapest
> falsification, and explain why the market may not yet have fully
> absorbed the distortion.

**Scout does not rank, size, allocate, promote, or decide whether a
security deserves capital. Atlas validates.** This is a search-posture
instruction only — no ranking, scoring, or capital authority is created
for Scout, consistent with the standing Mandatory Scout Feedback
Governance and Discovery Source Neutrality rules already recorded in
the Master Project Plan's Governance Classification.

---

## 13. Human/manual sourcing role

Pilot 5 sourcing is **not Scout-only**. Potential opportunities may come
from Chris; network observations; manual research; public filings;
market events; ChatGPT research; Grok; other available technology.
**Standing principle, unchanged:**

> Many sources discover. Atlas validates. Human allocates.

---

## 14. Technology principle

Use any software, AI, data source, script, or research tool that
materially improves opportunity discovery, discovery speed, factual
validation, economic understanding, or decision quality. **Do not
convert useful tools into new Atlas architecture unless a repeated,
demonstrated need earns it** — the standing complexity discipline is
unchanged, and is the same discipline that kept TCS's Gate B gap a
disclosed limitation rather than a reason to add XTSE support (per
`PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md` §17, Infrastructure
Restraint).

---

## 15. Pilot 5 first-batch concept — recorded for context, not executed here

After this sourcing design is approved, the first experimental set
should likely contain **approximately 3 high-quality forced-flow
situations**, not a large basket. Prefer situations with identifiable
constrained actors; primary evidence; plausible non-fundamental flow;
measurable potential flow; sufficient liquidity information; and an
opportunity that may still be active. **Do not require that all three
ultimately survive triage — the experiment tests the information
family, not a candidate-count target.** This section records the
concept only; **no Batch 001 is started by this document.**

---

## 16. What Pilot 5 is trying to learn

> Can Atlas identify a non-fundamental ownership/flow distortion early
> enough, validate that the business economics remain attractive,
> determine the best security expression, and produce an opportunity
> worthy of Stage 7 comparison?

**That — not candidate count — is the success question**, matching
Pilot 5's primary learning objective as chartered
(`PILOT3_CLOSEOUT_AND_PILOT5_TRANSITION.md` §11).

---

## Confirmation — no candidates, no architecture

**No Pilot 5 candidate has been surfaced, registered, or researched by
this document.** No company underwriting was performed. No forced-flow
research has begun. No architecture, permanent field, scoring, or new
engine was added. Sentiment was not activated — it remains
`SHADOW_ONLY`, unchanged. No Batch 001 was started. The two narrow
fixes (Hook Reconstruction at Triage; Priced-In One-Liner) are
referenced, not modified. `docs/pilot4/`'s frozen, unrelated pilot is
untouched.

**Capital status: NO REAL PORTFOLIO ACTION.**
