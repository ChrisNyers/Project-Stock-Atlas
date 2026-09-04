# PILOT 2 — STAGE 8 HUMAN DECISION 001

> **STAGE 8 — HUMAN PAPER DECISION**
> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> This record is frozen once committed. It is not rewritten based on later
> price performance. Reviews are appended only, in a separate loop log.

| | |
|---|---|
| Date recorded | September 4, 2026 |
| Pilot | Pilot 2 — Variant Edge & Intentional Allocation |
| Applies to | `PILOT2_STAGE7_CAPITAL_COMPARISON_001.md` (commit `0819e54`) |
| Capital | $50,000 paper/shadow |

---

## The decision

| Alternative | Allocation |
|---|---:|
| FIS | $5,000 |
| JD | $5,000 |
| SPY | $5,000 |
| Treasury/Cash | $30,000 |
| Do Nothing | $5,000 |
| **Total** | **$50,000** |

MELI and GLNG receive **$0** — consistent with their Stage 7 states
(`NO_DEMONSTRATED_EDGE` and `BLOCKED_BY_MATERIAL_UNCERTAINTY` respectively),
neither of which was eligible to compete for this capital.

### Decision method

> **The human decision-maker explicitly requested that the allocation be
> randomized.**

The allocation was **not derived from the Stage 7 variant analysis or the
Allocation Bridge rationale**. No security-specific reason is recorded for
why FIS, JD and SPY each received $5,000, Treasury/Cash received $30,000, or
Do Nothing received $5,000, because none was supplied and none is
manufactured here.

### Confidence

> **LOW.**

Recorded exactly as given.

---

## Allocation-rationale status

Derived via the existing control (`allocation_rationale.
derive_allocation_rationale_status`), not asserted:

```
derive_allocation_rationale_status(PortfolioAction.INITIATE) -> EXPLORATORY_LOW_RATIONALE
missing_rationale_fields() -> ('why_this_vs_alternatives', 'why_this_size', 'allocation_wrong_if')
```

| Line | Status |
|---|---|
| **FIS** ($5,000) | `EXPLORATORY_LOW_RATIONALE` |
| **JD** ($5,000) | `EXPLORATORY_LOW_RATIONALE` |

`why_this_vs_alternatives` and `why_this_size` are **not supplied** for
either line and are **not backfilled** with Atlas-generated language. The
absence of rationale is itself evidence from this pilot cycle, per
`ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`.

SPY, Treasury/Cash and Do Nothing are allocation targets, not underwritten
candidates — the Allocation Bridge rationale fields apply to candidate
securities compared at Stage 7 (FIS, JD, MELI, GLNG) and are not constructed
for the fixed alternatives themselves.

**"Do Nothing — $5,000" is recorded exactly as given.** It represents $5,000
of the $50,000 increment deliberately held back from every active
alternative — a legal, distinct Stage 8 outcome per the charter — and is not
reinterpreted as an allocation to any security.

---

## Stage 7 states entering this decision

(`PILOT2_STAGE7_CAPITAL_COMPARISON_001.md`, commit `0819e54`)

| Candidate | Stage 7 state | Funded here? |
|---|---|---|
| FIS | `ELIGIBLE_FOR_STAGE8` | Yes — $5,000 |
| JD | `ELIGIBLE_FOR_STAGE8` | Yes — $5,000 |
| MELI | `NO_DEMONSTRATED_EDGE` | No — $0 |
| GLNG | `BLOCKED_BY_MATERIAL_UNCERTAINTY` | No — $0 |

---

## Fresh-price bind used for Stage 7

Preserved exactly as it stood when Stage 7 was run (2026-09-04T20:10 UTC,
10 minutes after the XNYS/XNGS close) — not re-bound for this freeze:

| Candidate | Price | Session | Freshness |
|---|---|---|---|
| FIS | $41.895 | 2026-09-04, completed | FRESH |
| JD | $28.275 | 2026-09-04, completed | FRESH |
| SPY | — | — | **BLOCKED** (ARCX unsupported at Stage 7 time) — $773.79 Sept 4 close cited as secondary context only |
| Treasury/Cash | 3.84% (3-month T-bill) | — | context (CTX) |

**Provenance note, recorded honestly rather than smoothed over:** at Stage 7
time, JD's price was retrieved via a bare `latest_price` call, because
`bind_price_snapshot`'s full identity-verification path did not yet exist for
an ambiguous ticker. The rigorous MIC-qualified disambiguation
(`_disambiguate_via_known_mic`) and SPY's `ARCX` venue support were both added
**after** Stage 7 concluded, in `PILOT2_STAGE8_BINDING_READINESS` (commit
`3597967`). That later work closed both gaps for future binds; it does not
retroactively upgrade the historical Stage 7 price record, which is preserved
as it actually was.

---

## Live alternatives

SPY, Treasury/Cash and Do Nothing were all present and considered as live
alternatives at Stage 7 and remain so in this Stage 8 decision, per the
charter's requirement that all three stay genuine.

---

## Loop A

Recorded separately, in full, in `PILOT2_LOOP_LOG_001.md` (this pilot's
one-page Loop Log per charter §13). Summary: **Loop A result is NO** — this
cycle does not demonstrate intentional allocation edge, because the dollar
split was randomized rather than derived from the Stage 7 evidence.

---

## Revisit triggers preserved

Not newly invented — carried forward exactly from the already-established
thesis material in `PILOT2_STAGE7_CAPITAL_COMPARISON_001.md`. These govern
when Loop B may fire for the two funded candidates.

### FIS ($5,000)

> **Gap closer / horizon:** Capital Markets stabilization and leverage
> progress toward the disclosed 2.8x target, visible over 2–4 quarters.
>
> **Wrong-if:** Capital Markets softness spreads into Banking/Issuer
> Solutions; leverage fails to progress; the $500–700M FCF figure is later
> clarified as already net of foregone Worldpay income.

### JD ($5,000)

> **Gap closer / horizon:** JD Retail's trend, especially
> electronics/appliances, over the next 1–2 quarters against what a pure
> base-effect explanation would predict.
>
> **Wrong-if:** the core decline persists beyond the base-effect window, or
> buybacks slow materially (suggesting defensive cash preservation rather
> than confidence).

### SPY, Treasury/Cash, Do Nothing

No thesis-specific revisit trigger exists for these — none was ever
underwritten, and none is invented here solely because the allocation was
randomized.

---

## Record freeze

This record preserves the decision-time allocation, LOW confidence, the
randomized decision method, `EXPLORATORY_LOW_RATIONALE` status, the Stage 7
states entering the decision, the fresh-price bind actually used at Stage 7,
the live alternatives, and a pointer to the Loop A result. **Once committed,
it is not rewritten based on later price performance.** Any later Loop B or
Loop C observation is recorded as a new, separate entry in the loop log —
never as an edit to this record.

**Capital status: NO REAL PORTFOLIO ACTION.**
