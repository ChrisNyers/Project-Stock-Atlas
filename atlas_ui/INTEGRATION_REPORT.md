# Integration report — 2026-10-28

**Repo** `/Users/chrisnyers/Documents/Project-Stock-Atlas/stock-atlas-sprint1-live`, branch `main`.
Starting commit `106ba59`. Accepted baseline `4c71d06…` is an ancestor of HEAD; `stock_atlas/` is
byte-identical to it (tested). Control-layer files `capital_decision_facade.py`,
`allocation_rationale.py`, `live_price_binding.py`, `live_session_calendar.py` differ from
`4c71d06` only by earlier, already-accepted pilot work; nothing in them was changed here.

## Conflict between the handoff records and the repo (decision for you)

The handoff's records describe Cycle 0 as a **$500,000** sanitized snapshot (eight 10% equities,
cash-funded 2% MCD starter, dated 2026-09-02). The repo's frozen, later Cycle 0
(`CYCLE0_BASELINE_001.md`, 2026-10-07, Correction 002) is **$683,905.93**, 28 holdings,
new-outside-capital $25–50K, ADD-ONLY. MCD in the repo has been underwritten and is **PARKED until the
2026-11-04 Q3 release**. I treated the repo's later frozen records as canonical and displayed that;
the handoff snapshot is not loaded anywhere. If the handoff is the intended baseline, that needs a
documented human decision, not a silent switch.

## What works, what doesn't

See `CAPABILITY_MATRIX.md`. In short: read-only canonical state, immutable intake, history/revisit are
**proven against the real backend**. Stage 7 and paper Stage 8 are **fixture-tested only**: they run through
the real facade and DecisionStore, but no canonical run exists because `TWELVEDATA_API_KEY` is absent
(and MCD is parked). Filings ingestion into the UI, outcome-vs-benchmark tracking and automatic
monitoring are **not implemented**.

## Not done / honest gaps

- No live observation was bound; the Gate B live path is exercised only for its fail-closed branches.
- The handoff's Playwright smoke test was not adapted (Playwright is not installed); desktop and mobile
  were checked by hand in the browser pane (mobile: no horizontal overflow).
- The discovery board (evidence ledger edits) is a second local port over the same ledger, not embedded.
- Stage 7 inputs are human-typed (bands, Treasury reference, attestations); nothing is prefilled or invented.

## Single next permitted step

Put a valid, rotated `TWELVEDATA_API_KEY` in the server environment and open
`/stage7?ticker=MCD` to prove the live Gate B binding (read-only; starts no Stage 7 run). MCD stays
parked until its dated evidence arrives.
