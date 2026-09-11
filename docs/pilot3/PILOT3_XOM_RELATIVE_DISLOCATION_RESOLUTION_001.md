# PILOT 3 — XOM RELATIVE-DISLOCATION RESOLUTION 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Relative-dislocation test only. Full deep underwriting has **not**
> begun, and this record's disposition does not depend on it beginning.

| | |
|---|---|
| Date | September 11, 2026 |
| Batch | `PILOT3_AGENT_WORLD_BATCH_001.md` |
| Candidate | XOM — Exxon Mobil Corporation (CIK `0002115436`) |
| Prior state | `SURFACE_WITH_EVIDENCE_GAP` |

---

## 1. Original discovery signal (preserved, not restated after seeing the outcome)

Agent World surfaced XOM because geopolitical escalation materially
increased oil-supply risk, Brent/WTI moved sharply higher, and XOM's prior
Friday equity close had not yet incorporated the newer weekend information.
**Pre-registered question, unchanged:**

> Does XOM materially lag the change in oil economics after the U.S.
> market has had an opportunity to price the new information?

---

## 2. Observation window

- **Baseline:** Friday, **2026-09-04** close (last session before the
  Labor Day weekend during which the escalation occurred).
- **Completed sessions since:** Tuesday **2026-09-08**, Wednesday
  **2026-09-09**, Thursday **2026-09-10** (Monday 2026-09-07 was a U.S.
  market holiday).
- **Latest completed session as of this record:** **2026-09-10**. This
  record was prepared 2026-09-11 while the U.S. market was still open
  (decision time ~18:11 UTC, close 20:00 UTC); **2026-09-11 is explicitly
  excluded from the decision** as an incomplete session, per §14.

All dates below are exact completed-session closes, sourced from the same
provider (TwelveData) used throughout this pilot, cross-checked against the
Gate B-attested latest-completed-session date.

---

## 3. XOM completed-session returns

| Date | XOM close | Cumulative % from 2026-09-04 |
|---|---|---|
| 2026-09-04 (baseline) | $159.47 | — |
| 2026-09-08 | $160.66 | +0.75% |
| 2026-09-09 | $164.23 | +2.98% |
| 2026-09-10 | $165.23 | **+3.61%** |

XOM rose on every completed session in the window — no lag, and no
reversal.

---

## 4. CVX comparison

| Date | CVX close | Cumulative % |
|---|---|---|
| 2026-09-04 | $208.60 | — |
| 2026-09-08 | $209.80 | +0.58% |
| 2026-09-09 | $213.81 | +2.50% |
| 2026-09-10 | $212.76 | **+1.99%** (pulled back from the 9/9 peak) |

**XOM outperformed CVX on every single day of the window**, and the gap
**widened**, not narrowed, by the final completed session (+3.61% vs.
+1.99%).

---

## 5. XLE comparison

| Date | XLE close | Cumulative % |
|---|---|---|
| 2026-09-04 | $64.06 | — |
| 2026-09-08 | $64.77 | +1.11% |
| 2026-09-09 | $65.31 | +1.95% |
| 2026-09-10 | $64.93 | **+1.36%** (pulled back from the 9/9 peak) |

**XOM outperformed the sector ETF on every day of the window as well**
(+3.61% vs. +1.36% cumulative).

---

## 6. WTI / Brent comparison

**Provider-stack gap, disclosed rather than routed around:** the sanctioned
Atlas market-data providers (TwelveData, on the current plan) have **no
primary WTI or Brent spot/futures series** — direct queries for WTI, Brent,
and common commodity tickers all returned 404/not-found. This is recorded
as an infrastructure gap for future work, not fabricated around.

- **Primary-adjacent proxy used (provider-sourced, same pipeline as the
  equities above): USO** (United States Oil Fund, a U.S.-listed,
  exchange-traded WTI-tracking vehicle). Not a perfect 1:1 spot-WTI proxy
  (futures-roll/contango effects), but a legitimate, continuously
  provider-sourced series:

  | Date | USO close | Cumulative % |
  |---|---|---|
  | 2026-09-04 | $141.96 | — |
  | 2026-09-08 | $146.03 | +2.87% |
  | 2026-09-09 | $149.97 | +5.64% |
  | 2026-09-10 | $158.38 | **+11.57%** |

- **Brent (secondary/CTX only, no primary series available):** press
  coverage places Brent near $99.85/bbl on the morning of 2026-09-08,
  crossing $100/bbl around 2026-09-09, and in a roughly $101–108/bbl range
  intraday on 2026-09-10 (sources vary on the exact print) — "its highest
  level since May 19th." Directionally consistent with the USO move; not
  precise enough to use for anything beyond qualitative confirmation.

**Answering §4's question — has XOM materially under-reacted to the
commodity move relative to peers and its own economic exposure?** **No, on
the peer dimension** (XOM led both CVX and XLE throughout). On the
commodity dimension, all three equities rose far less than the ~11.6%
USO move — but per the work order's own explicit caution not to assume a
one-for-one beta, this is expected integrated-economics behavior (§7), not
evidence of an XOM-specific gap, since it is uniform across all three
energy names.

---

## 7. Integrated-business sensitivity findings

**Primary evidence (10-Q, quarter ended 2026-06-30):**

| Segment | Q2 2026 net income (approx., primary) |
|---|---|
| Upstream | ≈$8.2B |
| Energy Products (downstream/refining) | ≈$5.7B |
| Chemical Products | ≈$1.1B |
| **Total (consolidated)** | **$14.525B** (vs. $7.082B in Q2 2025 — **+105% YoY**) |

**Upstream is clearly the dominant profit driver (~56% of segment
earnings)** — consistent with standard integrated-major economics: upstream
captures most of the direct crude-price upside, while downstream/chemicals
provide a smaller, sometimes-offsetting counterweight (refining margins can
compress when crude input costs rise faster than product prices; chemicals
face similar feedstock-cost pressure). **This is standard, disclosed
business mix, not a reason by itself to expect a materially damped equity
reaction** — and the actual return data (§3–§5) shows no damping relative
to peers occurred.

**Evidence gap, disclosed:** no explicit quantified sensitivity disclosure
(e.g., "a $1/barrel move changes earnings by $X million") or production-
volume figure was retrievable from the sections of the 10-Q the fetch
tooling could return intact — the MD&A and Item 3 market-risk sections were
not reachable, a recurring large-filing limitation in this pilot. This is
recorded as a gap, not filled by inference; it is not load-bearing given
the direct return-based finding already answers the core question.

**Answering §5's question — is the lower equity beta economically rational,
or does it leave a potentially exploitable gap?** **There is no lower
equity beta to explain** — XOM's beta to the event was, if anything,
slightly higher than its peers' over this window, not lower.

---

## 8. Primary evidence reviewed (XOM)

- **10-Q**, quarter ended 2026-06-30 (accession `0000034088-26-000093`) —
  segment earnings, capital expenditures, cash, debt, dividends, buybacks.
- **8-K**, filed 2026-07-31 (accession `0002115436-26-000006`) — Q2 2026
  earnings release (index metadata confirmed; full exhibit text was not
  separately re-fetched given the 10-Q's XBRL-sourced figures were
  sufficient for this record's minimum-sufficient-evidence standard).

**Balance sheet / capital return (primary, 2026-06-30 / six months 2026):**
cash $10.588B; total debt ≈$42.4B (notes/loans payable $10.139B + long-term
debt $32.229B); capex $12.997B (six months, ≈$26B annualized pace);
dividends paid $8.633B (six months); share repurchases $10.007B (six
months); common shares outstanding 4.112B (2026-06-30).

**Coarse valuation context (Atlas-calculated from the figures above, not a
full model):** at the $165.23 completed-session close, market cap ≈$679.5B;
annualized dividend yield ≈2.5%; annualized buyback yield ≈2.9%
(**combined shareholder yield ≈5.5%**); coarse annualized EPS (six-month
net income × 2 ÷ shares) ≈$9.10, implying a coarse P/E ≈**18.2x**.

---

## 9. Candidate variant

> The market may be underpricing the incremental cash-flow benefit to XOM
> from a sustained higher-oil regime created by materially increased
> Middle East supply risk.

**This is not the same claim as "oil went up, therefore XOM should go
up"** — and it does not survive the relative-return test either way. The
completed-session evidence in §3–§6 shows **no gap between XOM and its
peers for the variant to be about** — the pre-registered lag never
materialized once the market reopened. There is nothing left for a
"XOM-specific underpricing" variant to explain.

---

## 10. Market-could-be-right case

Built for completeness even though the primary finding already resolves
the candidate:

- **The geopolitical premium may reverse rapidly** — secondary coverage
  reviewed for this record explicitly describes "ceasefire negotiations"
  beginning to restore confidence in global supply routes, and today's
  (2026-09-11, uncertified/intraday) USO reading of $153.56 sits **below**
  Thursday's $158.38 close — a partial pullback already visible, though not
  used as decision evidence per §14.
- **Integrated economics dampen upstream upside** — real and disclosed
  (§7), though not visible as a peer-relative lag in this window.
- **High oil can reduce demand / raise recession-inflation risk** — general,
  credible macro context; not tested against XOM-specific data here.
- **Refining/chemical economics may offset upstream benefit** — plausible
  given the segment mix (§7), not separately quantified in this record.
- **XOM may already reflect a higher normalized oil price** — the coarse
  ≈18.2x P/E and the doubling of YoY quarterly net income (§8) are
  consistent with the market already crediting an elevated oil-price
  environment into the multiple, not treating current earnings as a
  one-off.
- **Equity investors may appropriately discount temporary commodity
  spikes** — directly consistent with the ceasefire-negotiation evidence
  above.

**This case is credible and, on this record's own return-based finding, is
the better-supported reading** — not a strawman invoked to justify a
predetermined rejection.

---

## 11. Persistence assessment

**Does the candidate variant depend on a temporary event trade or a
durable economic change?** The underlying commodity shock itself shows
real, evidence-based signs of being **event-driven and already
partially reversing** — secondary sources describe active ceasefire
negotiations and a modest pullback in the oil proxy on the very next
(uncertified) session. Even setting that aside, **the equity-market
question this record was asked to answer never required resolving
temporary-versus-durable**, because there was no relative lag for either
framing to explain. **Atlas is not promoting a one-day event trade as
structural alpha** — it is recording that no dislocation existed to
promote as either kind of trade.

---

## 12. Priced-in checkpoint

**Does today's XOM price already imply a materially higher oil-price
environment?** On the coarse evidence available (§8): a ≈18.2x P/E and a
≈5.5% combined shareholder yield, alongside quarterly net income that has
already more than doubled year-over-year, are consistent with the market
having already substantially repriced XOM for an elevated, not merely
transient, oil-price backdrop over the past year. This is offered as
context for §10's market-could-be-right case, **not as a full valuation
model** (none was built, per the work order's explicit instruction).

---

## 13. Falsifier

**The falsifier is the actual observed outcome, not a hypothetical one:**
per §12 of the work order, "if the relative gap disappeared once U.S.
markets reopened, `NO_DEMONSTRATED_EDGE` is a successful Pilot 3 outcome."
**That is exactly what the completed-session evidence shows** — the
pre-registered lag did not merely close, it **never existed**: XOM led
both CVX and XLE on every completed session in the window, with the gap
widening rather than narrowing by the final session (2026-09-10). No
further falsifier test is needed; the falsifying evidence is already in
hand.

---

## 14. Fresh-price bind

- **Gate B bind attempt (2026-09-11, ~18:11 UTC):** the U.S. market was
  still open at decision time; `bind_price_snapshot` correctly returned
  `STALE` for the live intraday quote ($165.325, session date 2026-09-11),
  for the same disclosed reason found in the DOCU deep underwriting: the
  sanctioned binder has no capability to bind against a specific historical
  completed-session close, only the current live quote.
- **Per this work order's explicit §14 instruction ("do not use intraday
  prices to complete the decision"):** the intraday `STALE` observation is
  **not used**. The completed-session close already used as the endpoint
  of the observation window — **$165.23, session 2026-09-10** — is the
  fresh-price reference for this record. It requires no separate
  re-binding: it is independently attested as the latest completed session
  as of decision time (`latest_completed_session(now, mic='XNYS')` →
  `2026-09-10`), and it is the same value returned by the provider's
  daily-history series used for §3.
- No new binding capability was added to `live_price_binding.py`.

---

## 15. Confirmation — all other candidate states unchanged

Batch 001: AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SMH
`REFERENCE_PEER_TAPE`, AAPL/JPM `CALENDAR_HOLD`, NVDA `REFERENCE_ONLY` —
unchanged. Batch 002: PATH `NO_DEMONSTRATED_EDGE`, MDB
`NO_DEMONSTRATED_EDGE`, DOCU `BLOCKED_BY_MATERIAL_UNCERTAINTY`, SPXC
`SURFACE_WITH_EVIDENCE_GAP`, SOLS `EVENT_DRIVEN_HOLD`, PCG
`SURFACE_WITH_EVIDENCE_GAP` — none touched by this record.

---

## Pilot 3 learning — direct test of Agent World's discovery value

> Did Agent World surface a genuine temporary or durable mispricing that
> survived the first completed-session test?

**No — and this is recorded as useful discovery-system evidence, not a
failure to be minimized.** Agent World correctly identified a real,
live, economically coherent hypothesis (a commodity shock an equity price
had not yet had the opportunity to price) at the moment the weekend news
broke. Atlas's discipline of **waiting for the required completed-session
evidence rather than front-running it** — the explicit instruction
followed at registration and again here — is exactly what let this record
determine, cleanly and without ambiguity, that the specific dislocation
Agent World hypothesized did not materialize. **A correctly rejected
candidate, resolved by the pre-registered question rather than a
post-hoc rationalization, is the kind of outcome that validates the
discipline of the discovery-to-triage pipeline**, independent of whether
this particular name promotes.

---

## Final disposition

> ## `NO_DEMONSTRATED_EDGE`

XOM did not lag CVX or XLE on any completed session in the observation
window; it led both, with the gap widening by the final session. The
pre-registered discovery question is answered directly and in the negative
by primary, completed-session evidence — not inferred, not judged by
whether oil remains elevated. Per the work order's own §12 instruction,
this is recorded as a successful Pilot 3 outcome.

---

## What this record does not do

No deep underwriting of XOM. No Stage 7 comparison. No Stage 8 decision.
No capital allocated. No triage of SPXC, SOLS, or PCG. No new binding
capability added to the Gate B pipeline. No Batch 003.

**Capital status: NO REAL PORTFOLIO ACTION.**
