# Controlled Live Pilot — Interim Checkpoint 001

| | |
|---|---|
| Date | 2026-10-14 |
| Scope | Cycle 1 (MCD) and Cycle 2 (RPM) — **process level only** |
| Status | **RECORDED — interim; NOT a live-pilot verdict** |
| Capital status | **NO REAL PORTFOLIO ACTION** |

**Limits of this record.** Two cycles show the *process works*. They do not show
that Atlas adds decision value, and nothing here claims alpha. No decision cycle
has completed (MCD parked until 2026-11-04; RPM parked until 2026-11-09), so no
outcome evidence exists. The pilot target remains 3–5 real decision cycles.

## What is working

- **Frozen counterfactual first.** The pre-Atlas stance was recorded before any
  research and never touched afterward; it is used only as the comparison point.
- **Labeled evidence.** FACT / MANAGEMENT CLAIM / CONTEXT / INFERENCE / VARIANT /
  CAPITAL IMPLICATION kept both cases honest; prices labeled uncertified.
- **Cheapest falsification first**, with unresolved questions preserved rather
  than filled.
- **Decisions stayed with the human.** No BUY/SELL forced. Both cycles moved from
  CONTINUE to PARK; the human challenge moved the RPM disposition.
- **Fail-closed controls and append-only records held.**
- **The two cycles posed different questions** (MCD: valuation of a quality
  franchise against rates; RPM: temporary vs cyclical slowdown).

## What is creating unnecessary friction

- No certified price or event source (`TWELVEDATA_API_KEY` absent), so price,
  yield and calendar data were gathered ad hoc.
- SEC filings / XBRL facts re-pulled by hand each cycle.
- Dated catalysts tracked by hand (an unverified MCD Q3 date of Oct 28 was
  carried; the official calendar said Nov 4).
- Triple logging (cycle file + Plan + Decision Log); the Plan status pointer is
  now a long stack.
- Two disposition vocabularies (MCD vs RPM label sets).
- Inconsistent threshold treatment (MCD pre-registered; RPM exploratory only).
- Underwriting records longer than needed.
- Atlas overreach: "valuation already discounts a downturn" exceeded the
  evidence; the human caught it.
- Fragile record-edit scripts failed on a text match twice.
- **Selection bias, not independent:** both candidates were human-selected, so
  Atlas has not yet tested opportunity selection; both were de-rated names.

## What must remain unchanged

- Control layer: models; `capital_decision_facade` as the only capital write
  path; ADD-ONLY / no-trims guard; T+1 funding-pocket rule; fail-closed tax,
  liquidity and execution.
- Gate B (TwelveData price-only; XNYS calendar as session authority) and
  Investor Policy v1.0 with its hash.
- Human Stage 8 as sole capital authority; no automated execution;
  append-only history; pre-Atlas stance frozen before analysis.
- Uncertified-price labeling; no alpha claims.

## What the Operating MVP should contain (as proposed)

- **Discovery Loop v0.1:** candidate intake recording source (HUMAN or SCOUT);
  immutable pre-Atlas stance capture; one underwriting template with the six
  tags and cheapest-falsification first; evidence ledger tagged PRIMARY /
  SECONDARY / UNCERTIFIED; parked-item registry with dated catalysts, an
  "officially verified?" flag and revisit questions; alternatives stubs (SPY,
  Treasury/Cash, Do Nothing); automated pulls of SEC filings, Treasury yields
  and the event calendar.
- **UI v0.1 (read-mostly):** cycle board with parked-until dates; candidate
  pages; portfolio baseline; dated-event alerts; visible CERTIFIED / UNCERTIFIED
  indicator; a Stage 8 form that stays gated and fail-closed.

## Readiness

Nothing blocks starting. Constraints: (1) the TwelveData key is absent and
rotation is pending; the live-binding path is unproven end to end (25 skips are
BLOCKED, not passes), so the UI must show BLOCKED rather than imply it works;
(2) the MVP must not absorb Stage 7 or write capital decisions; (3) Yahoo was
research context only — a built tool must not depend on it (terms unreviewed;
Tiingo already rejected on storage terms); (4) a single disposition vocabulary
was required before the template.

## Open items

MCD parked until 2026-11-04 (official IR calendar); RPM parked until 2026-11-09
(Investor Day); `TWELVEDATA_API_KEY` absent (key rotation pending); tax /
liquidity / execution fail-closed until materially relevant.

## Human direction on this checkpoint (2026-10-14)

Proceed. Single candidate-state vocabulary:
`SURFACED → QUICK TEST → UNDERWRITING → PARKED / REJECTED / READY FOR CAPITAL
COMPARISON`. "Continue underwriting" means remaining in `UNDERWRITING`, not a
separate disposition. Build the smallest usable Operating MVP (Discovery Loop
v0.1 + UI v0.1) as **workflow support**; add no new controls, ranking engines,
paid data, autonomous agents, execution or ML. MCD and RPM are current `PARKED`
examples; intake must accept new `SURFACED` ideas from HUMAN, SCOUT, Sue,
Nutstuff and other sources, preserving provenance without source privilege.

**Capital status: NO REAL PORTFOLIO ACTION.**
