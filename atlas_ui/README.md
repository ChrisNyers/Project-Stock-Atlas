# Stock Atlas decision UI (integration layer)

Presentation + thin server-side adapters over the EXISTING frozen engine. It computes no
Stage 7 eligibility, creates no `PortfolioAction`, ranks nothing, and writes capital records
only through `CapitalDecisionFacade`. **Paper decisions only. No real trades.**

The visual design is the supplied prototype (`theme.css` is its stylesheet). Pages are
server-rendered with no JavaScript; browser state is never a record.

## Run

```bash
# canonical records, live Gate B path (needs a key in the SERVER environment only)
export TWELVEDATA_API_KEY=...        # never pasted into the UI, never written to artifacts
.venv/bin/python -m atlas_ui serve    # dashboard http://127.0.0.1:8770, discovery board http://127.0.0.1:8765

# no key needed: isolated FIXTURE workspace (every page carries a DEMO banner)
.venv/bin/python -m atlas_ui serve --demo --port 8771 --board-port 8766
```

Both bind to loopback only. Without the key, canonical mode shows `BLOCKED` with the exact
reason; nothing is inferred or faked.

## What goes where

| Page | Backend it uses |
|---|---|
| Overview | `docs/controlled_live_pilot/CYCLE0_BASELINE_001.md` (parsed + re-validated, SHA-256 shown), discovery ledger, decision ledger, key presence |
| Intake | `operating_mvp.ledger` (`surface` + versioned, immutable `freeze_stance`) |
| Stage 7 | `live_price_binding.bind_price_snapshot` + `live_session_calendar` → `CapitalDecisionFacade.run_stage7`; five frozen input artifacts + a run index |
| Decision desk / run page | rehydrates the retained run, proves it reproduces its SHA-256, then `CapitalDecisionFacade.record_final_decision` |
| History | the real append-only `DecisionStore` ledger; revisit = linked note, never an edit |
| Capability matrix | `atlas_ui/app.py:CAPABILITIES` → `CAPABILITY_MATRIX.md` |

Stage 7 can start only for a candidate a human has moved to `READY_FOR_CAPITAL_COMPARISON`
(on the discovery board). `PARKED` candidates (MCD, RPM) cannot run.

Records live in `atlas_ui/data/live/` (canonical) — decisions ledger, `artifacts/`, `inputs/<run>/`,
`runs_index.jsonl`. Demo uses a fresh temp directory and a copy of the discovery ledger.

## Fail-closed behavior (tested)

Absent key · identity mismatch · wrong venue/MIC · stale session · fixture price in canonical mode ·
tampered artifact · unknown/duplicate run · missing confirmation · illegal action · UNVERIFIED
constraints on a funded action · STARTER over the 2% cap. Each leaves the ledger at zero new rows.
