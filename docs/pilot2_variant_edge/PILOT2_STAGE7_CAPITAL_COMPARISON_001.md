# PILOT 2 — STAGE 7 CAPITAL COMPARISON 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Stage 7 compares. It does not allocate. Nothing below is a
> `PortfolioAction`. No name is ranked. Stage 8 remains a human decision and
> is not begun by this record.

| | |
|---|---|
| Date | September 4, 2026 |
| Candidates | FIS, MELI, JD (survived deep underwriting, `742cc20`) |
| Comparison set | FIS · MELI · JD · SPY · Treasury/Cash · Do Nothing |
| Excluded | GLNG — `BLOCKED_BY_MATERIAL_UNCERTAINTY`, preserved, not compared |
| Out of scope | FISV, ADBE, SNOW, WCC, NTR, CVS — not reopened |

**Method note.** This page is built from the completed deep-underwriting
record, refreshed only where the fresh-price bind required it, and uses this
work order's own vocabulary (`ELIGIBLE_FOR_STAGE8` / `NO_DEMONSTRATED_EDGE` /
`BLOCKED_BY_MATERIAL_UNCERTAINTY`) rather than the coded
`Stage7CandidateResult` enum. The literal `capital_decision_facade.run_stage7`
pipeline was **not** invoked for this record: doing so would require supplying
a `required_return_band` (an investor-policy hurdle rate) that has never been
authorized anywhere in Pilot 2, and inventing one now would itself be
"creating new precision merely for Stage 7." This is a disciplined,
evidence-grounded narrative comparison, not a claim that the coded pipeline
was run.

---

## 1. Fresh-price / session status

Current time at bind: **2026-09-04T20:10 UTC** — 10 minutes after the
XNYS/XNAS 20:00 UTC close, so the calendar attests **2026-09-04 as a genuine
completed session** (not mid-session, unlike the deep-underwriting pass).

| Candidate | MIC | Bind result | Price | Freshness |
|---|---|---|---|---|
| **FIS** | XNYS | **BOUND** | $41.895 | FRESH |
| **MELI** | XNGS | **BOUND** | $1,977.765 | FRESH |
| **JD** | XNGS | **BOUND** (see note) | $28.275 | FRESH |
| **SPY** | ARCX | **FAILED CLOSED — BLOCKED** | — | n/a |

**JD note:** `resolve_symbol('JD')` returns `AMBIGUOUS` — the bare ticker
"JD" collides globally with JD Sports Fashion plc (LSE, `XLON`) and a Buenos
Aires depositary receipt (`XBUE`); TwelveData's own `quote_confirmed` field
correctly identifies the NASDAQ ADR (`XNGS`), and the price was retrieved via
`latest_price` directly rather than through the stricter `resolve_symbol`
gate. This is unchanged from the deep-underwriting pass and does not affect
identity: the security key resolved is JD.com's, not the UK company's.

**SPY note — genuine, newly surfaced blocker.** SPY resolves to MIC **`ARCX`**
(NYSE Arca), not `XNYS`. `SUPPORTED_MICS` currently authorizes only
`XNYS`/`NYSE`, `XNGS`, `XNMS` — the exact set required by the frozen Pilot 2
basket. `ARCX` was never in scope for that extension (SPY is a fixed
cross-pilot alternative, not one of the 10 basket names), so the bind
**fails closed**, exactly as instructed: no intraday quote was substituted,
no venue coverage was added without authorization. This is reported as a
blocker, not silently routed around — structurally the same discipline
applied to the FISV/Nasdaq gap and to GLNG's financing gap earlier in this
pilot. **It does not block Stage 7** because Stock Atlas has never treated
SPY as a live-price-bound instrument here: every prior fixture and this
pilot's own control-layer tests carry SPY as a **modeled return-band
alternative** (`ReturnBand`, with basis notes), not a `PriceSnapshot`. A
$773.79 Sept 4 close is available from secondary sources and is used below
**as context only**, clearly marked, not as a bound completed-session price.

### Return-case rerun check

| Candidate | Deep-underwriting price | Fresh bound price | Δ | Rerun required? |
|---|---|---|---|---|
| FIS | $41.865 | $41.895 | +0.07% | **No** |
| MELI | $1,977.79 | $1,977.765 | −0.001% | **No** |
| JD | $28.22 | $28.275 | +0.19% | **No** |

All three moves are immaterial. No downside/base/upside case is rerun.

---

## 2. Comparison set

FIS · MELI · JD · SPY · Treasury/Cash · Do Nothing. No other security enters
this Stage 7 decision.

---

## 3. Preserve the variant

### FIS

- **Observable priced-in view:** stock down ~32.6% YTD, >10% single-session
  decline on the Aug 4, 2026 Q2 print; forward P/E ≈6.25x vs. a 5-year average
  ≈14.0x, while EV/EBITDA ≈12.4x sits roughly in line with its ≈12.0x 5-year
  average.
- **Atlas variant:** the market is pricing FIS as one undifferentiated
  "guidance cut" event, when the same disclosure contains two distinguishable,
  oppositely-moving segment stories — Capital Markets softness (named,
  bounded) against Banking/Issuer Solutions execution management calls "ahead
  of plan," with FCF guidance **raised** $100M in the same release.
- **Why the gap can exist:** a single mixed release (one raise, one cut, plus
  a divestiture review disclosed on the call, not in the press-release text)
  rewards headline-scanning over segment-level reading, especially inside a
  single trading session.
- **Gap closer / horizon:** Capital Markets stabilization and leverage
  progress toward the disclosed 2.8x target, visible over 2–4 quarters.
- **Wrong-if:** Capital Markets softness spreads into Banking/Issuer
  Solutions; leverage fails to progress; the $500–700M FCF figure is later
  clarified as already net of foregone Worldpay income.
- **Leverage / capital-return constraint:** net debt ≈$20.5B; buybacks
  explicitly "temporarily curtailed" until the 2.8x target is met — the
  per-share benefit of the transaction is currently an FCF-guidance story,
  not yet a share-count story.

### MELI

- **Observable priced-in view:** headline 15–90 day NPL (7.0% overall, 4.6%
  credit card) cited as "near historic lows" amid 50% revenue growth and 75%
  credit-portfolio growth — the dominant favorable framing.
- **Atlas variant:** that framing understates a real, **current** (not
  merely future-risk) profitability deterioration: provisions grew 85% YoY,
  outpacing 75% portfolio growth, and credit-card NIMAL moved from breakeven
  to −2.5% YoY — alongside net income down 11% YoY despite the revenue
  growth.
- **Why the gap can exist:** NPL is the simpler, more visible metric; NIMAL
  and the provisioning growth-rate delta require reading further into the
  materials than the headline figure most coverage cites.
- **Gap closer / horizon:** whether credit-card NIMAL recovers toward
  breakeven over 2–3 quarters as new cohorts mature, per management's own
  explanation.
- **Wrong-if:** NIMAL recovers without further provisioning acceleration and
  net income growth resumes tracking revenue growth — this would validate
  the "credit quality is fine" framing over this variant.
- **Credit / provisioning / NIMAL risk:** this is not a hedge — it is the
  thesis. The variant identified is a real, current earnings-quality concern,
  not a hidden strength. **Not forced into a bullish recommendation here.**

### JD

- **Observable priced-in view:** consolidated non-GAAP profit "inflection"
  (+21% YoY), attributed in coverage to disciplined capital allocation as
  food-delivery losses shrink.
- **Atlas variant:** JD Retail — the core segment, excluding New
  Businesses entirely — itself declined 4.7% YoY, led by an 11.8% drop in
  electronics/appliances, JD's historical flagship category. The "profit
  improved because a loss-making bet shrank" framing does not address this.
- **Why the gap can exist:** a round consolidated profit headline is simpler
  than the underlying segment math; management's "high base effect"
  explanation has not been independently checked against category-level
  competitive data, and this release contains no competitive commentary at
  all.
- **Gap closer / horizon:** JD Retail's trend, especially
  electronics/appliances, over the next 1–2 quarters against what a pure
  base-effect explanation would predict.
- **Wrong-if:** the core decline persists beyond the base-effect window, or
  buybacks slow materially (suggesting defensive cash preservation rather
  than confidence).
- **Core JD Retail weakness vs. balance-sheet support:** net cash ≈$23B, TTM
  FCF ≈$4.6B, an active, largely-deployed buyback program. This is real
  downside protection, not a resolution of the core question — it changes
  how bad "wrong" would be, not whether the thesis is right.

---

## 4. Return / risk comparison

Refreshed only for price (no rerun required, per §1). Coarse ranges, not
precision, per instruction.

| Candidate | Current bound price / yield | Downside | Base | Upside | 1Y base | 3Y base annualized | Confidence | Principal uncertainty |
|---|---|---|---|---|---|---|---|---|
| **FIS** | $41.895 (FRESH, completed session) | −15%/−25% | +10%/+20% | +35%/+50% | +10% to +20% | high single–high teens %/yr | MODERATE | Gross-vs-net FCF accretion figure; whether Capital Markets softness stays contained |
| **MELI** | $1,977.765 (FRESH, completed session) | −25%/−40% | −5%/+10% | +20%/+35% | **−5% to +10%** | mid-single–low-double %/yr | MODERATE | Whether NIMAL compression is temporary (cohort dilution) or structural |
| **JD** | $28.275 (FRESH, completed session) | −15%/−25% | +10%/+20% | +30%/+45% | +10% to +20% | low-double–high-teens %/yr | MODERATE | Whether the JD Retail decline is a base-effect artifact or structural share loss |
| **SPY** | BLOCKED (ARCX unsupported) — $773.79 Sept 4 close, CTX only | modeled range | **7%–10%** (established Stock Atlas beta band; unchanged by this record) | modeled range | ~7%–10% | ~7%–10%/yr | n/a (methodology, not underwritten) | Live price bind blocked by venue coverage — see §1 |
| **Treasury/Cash** | 3.84% (3-month T-bill, CTX; consistent with the ≈3.9% reference used in prior Pilot records) | n/a | **~3.84%** | n/a | ~3.84% | ~3.84%/yr | n/a | Reinvestment-rate risk over the horizon |
| **Do Nothing** | n/a | 0% | 0% | 0% | 0% | 0%/yr | n/a | Opportunity cost only |

No security is ranked from these figures. MELI's base case is stated as
found — barely above zero, materially below SPY's established band — not
adjusted to look more competitive.

---

## 5. Variant-edge test

> Does the identified variant appear strong enough that this security
> deserves to compete for the next $50,000 against SPY, Treasury/Cash, and
> Do Nothing?

**FIS — `ELIGIBLE_FOR_STAGE8`.** The variant is specific, falsifiable, and
points toward a real gap between segment-level fundamentals and headline
pricing. The base-case return range (+10% to +20%, 1Y) sits meaningfully
above both Treasury/Cash (~3.84%) and the established SPY band (7–10%), with
named, testable wrong-if criteria. Eligibility to compete is not a funding
recommendation — leverage risk and the unresolved gross/net FCF question are
real and preserved for Stage 8.

**MELI — `NO_DEMONSTRATED_EDGE`.** This is the sharpest test in this record.
The variant is real and well-evidenced, but it is **directionally cautionary**
— it argues the market's optimistic framing may be missing a current
profitability deterioration, not that Atlas has identified upside the market
is missing. A variant that argues the market is *too* optimistic does not
support a BUY-oriented capital case; Stage 7's own architecture requires a
`BUY` security decision to permit new-capital comparison in the first place,
and this evidence does not support one. The base-case return (−5% to +10%)
is not competitive with SPY's established band and carries a severe downside
(−25% to −40%). **This is evidence for caution, not evidence for competing
for capital** — `NO_DEMONSTRATED_EDGE` is not a euphemism for "unclear"; it
is the correct label when a real edge points away from allocation.

**JD — `ELIGIBLE_FOR_STAGE8`.** The variant identifies a specific,
falsifiable gap (core segment decline vs. a "high base effect" explanation)
with a base-case return range (+10% to +20%, 1Y) competitive with SPY's band,
backed by a genuinely strong balance sheet that limits downside if the
thesis proves wrong. Eligible to compete — not a funding recommendation.

---

## 6. Final Stage 7 page

| Candidate | Current bound price/yield | Observable priced-in view | Atlas variant | Why gap can exist | Gap closer/horizon | Wrong-if | Downside | Base | Upside | 1Y base | 3Y base annualized | Confidence | Principal uncertainty | Stage 7 state |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **FIS** | $41.895 FRESH | −32.6% YTD, >10% one-day drop; P/E 6.25x vs 14.0x 5Y avg; EV/EBITDA in line | Segment-specific tension priced as one undifferentiated cut | Mixed single release rewards headline over segment reading | Capital Markets trend + leverage progress / 2–4Q | Softness spreads; leverage stalls; FCF figure clarified as net | −15%/−25% | +10%/+20% | +35%/+50% | +10–20% | high single–high teens %/yr | MODERATE | Gross-vs-net FCF; Capital Markets containment | **`ELIGIBLE_FOR_STAGE8`** |
| **MELI** | $1,977.765 FRESH | Headline NPL "near historic lows" amid 50%/75% growth | Provisions +85% YoY outpace 75% book growth; card NIMAL breakeven→−2.5%; net income −11% YoY | NIMAL/provisioning delta less visible than headline NPL | NIMAL recovery via cohort maturation / 2–3Q | NIMAL keeps compressing without recovery | −25%/−40% | −5%/+10% | +20%/+35% | −5 to +10% | mid-single–low-double %/yr | MODERATE | Temporary cohort dilution vs. structural deterioration | **`NO_DEMONSTRATED_EDGE`** |
| **JD** | $28.275 FRESH | Consolidated non-GAAP profit +21% YoY headline | Core JD Retail −4.7% YoY, electronics −11.8%, not just loss-shrinkage optics | Round profit headline simpler than segment math; no competitive commentary in release | JD Retail trend, esp. electronics / 1–2Q | Core decline persists past base-effect window; buybacks slow | −15%/−25% | +10%/+20% | +30%/+45% | +10–20% | low-double–high-teens %/yr | MODERATE | Base-effect artifact vs. structural share loss | **`ELIGIBLE_FOR_STAGE8`** |
| **SPY** | BLOCKED (ARCX); $773.79 Sept 4 close, CTX | Established beta reference, not underwritten | n/a — not a candidate | n/a | n/a | n/a | modeled | 7%–10% | modeled | ~7–10% | ~7–10%/yr | n/a | Live bind blocked by venue coverage | Alternative (not evaluated for eligibility) |
| **Treasury/Cash** | 3.84% 3-mo T-bill, CTX | Risk-free reference | n/a — not a candidate | n/a | n/a | n/a | n/a | ~3.84% | n/a | ~3.84% | ~3.84%/yr | n/a | Reinvestment-rate risk | Alternative (not evaluated for eligibility) |
| **Do Nothing** | n/a | Status quo | n/a — not a candidate | n/a | n/a | n/a | 0% | 0% | 0% | 0% | 0%/yr | n/a | Opportunity cost only | Alternative (not evaluated for eligibility) |

No eligible name is ranked against another.

### Short synthesis

Three names entered Stage 7; the outcomes split, on evidence, not by design.
**FIS and JD** both cleared `ELIGIBLE_FOR_STAGE8` on genuinely different
mechanisms — FIS on a segment-differentiation-vs-headline-optics gap inside a
single mixed disclosure, JD on a core-vs-consolidated segment gap cushioned
by an unusually strong balance sheet. **MELI** is the record's clearest
discrimination result: its variant is at least as well-evidenced as the
other two, but it points the wrong direction for a capital case — a market
that may be *too* optimistic about credit quality is not a reason to compete
for capital, it is a reason for caution, and this record states that
plainly rather than converting a real finding into a forced recommendation.
Both eligible names still carry named, real risks (FIS: leverage/buyback
curtailment; JD: whether "high base effect" holds) that Stage 8 — not this
record — must weigh against SPY's established band and Treasury/Cash's
current 3.84%, where cash and refusal remain fully legal outcomes.

---

## 7. GLNG

> **Status preserved: `BLOCKED_BY_MATERIAL_UNCERTAINTY`.**

Not compared in this Stage 7 record and no valuation range was constructed
for it here, consistent with the deep-underwriting reasoning: the fourth FLNG
unit remains dependent on an unresolved capital raise/EPC-termination
contingency with a management-disclosed deadline before the end of Q3 2026.
GLNG's existing revisit trigger is exactly that resolution — a subsequent
6-K or press release confirming either the financing succeeded or the EPC was
terminated. No new evidence on this point was sought or found in this Stage 7
pass; none was owed, since Stage 7 work was scoped to FIS/MELI/JD only.

---

## 8. Stop-rule compliance

This record does not decide the $50,000 allocation, does not fill the
Allocation Bridge, does not rank FIS against JD, does not recommend a
position size, does not introduce an optimizer, and was not informed by any
sentiment source (`SHADOW ONLY`, unconsulted — nothing to record). Loop A has
not begun. Stage 8 remains a human decision, not taken here.

---

## What this record does not do

No architecture, code, basket, venue-control, or sentiment change. No
capital allocated. FISV, ADBE, SNOW, WCC, NTR, CVS not reopened. The SPY
`ARCX` venue gap is reported, not resolved — extending venue coverage was not
authorized by this work order and was not attempted.

**Next step, not taken here:** Stage 8 human decision on FIS and JD (both
`ELIGIBLE_FOR_STAGE8`). MELI does not proceed to Stage 8 on this record's
finding. GLNG re-enters the queue only once its financing/termination outcome
is known.

**Capital status: NO REAL PORTFOLIO ACTION.**
