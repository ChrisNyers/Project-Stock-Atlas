# Atlas Operating MVP v0.1 — Discovery Loop + UI

Workflow support only. Records and shows where each candidate is; it does not
rank, score, size, fetch data, or touch capital. Human Stage 8 remains the sole
capital authority. **NO REAL PORTFOLIO ACTION.**

## Vocabulary (the only one)

`SURFACED → QUICK_TEST → UNDERWRITING → PARKED / REJECTED / READY_FOR_CAPITAL_COMPARISON`

"Continue underwriting" = stay in `UNDERWRITING` (add a note). `QUICK_TEST` is
optional (human may go SURFACED → UNDERWRITING, as Cycles 1–2 did).
`READY_FOR_CAPITAL_COMPARISON` is a label; it starts nothing.

## Run

```bash
.venv/bin/python -m operating_mvp serve            # http://127.0.0.1:8765 (loopback only)
.venv/bin/python -m operating_mvp render board.html # static, non-interactive copy
.venv/bin/python -m operating_mvp verify            # hash-chain check
.venv/bin/python -m operating_mvp surface --name "X" --ticker X --source SUE --why "..." --question "..."
.venv/bin/python -m operating_mvp state X QUICK_TEST --reason "..."
.venv/bin/python -m operating_mvp state X PARKED --reason "..." --waiting-on "..." --until 2026-12-01 --verified --revisit-question "..."
.venv/bin/python -m operating_mvp note X "text"
```

## Structure

| File | Role |
|---|---|
| `ledger.py` | append-only, hash-chained event log; states, transitions, intake, replay |
| `data/candidate_ledger.jsonl` | the record (MCD, RPM backfilled, flagged `backfilled`) |
| `seed.py` | one-time backfill of MCD/RPM from the frozen cycle records |
| `ui.py` | board, candidate page, loopback server; intake / state / note forms |
| `__main__.py` | CLI |

## Rules enforced by tests

- Sources: HUMAN, SCOUT, SUE, NUTSTUFF, OTHER (needs detail). Recorded as
  provenance; never used to order, filter or gate.
- PARKED requires `waiting_on`; a date is optional and flagged *officially
  verified* or not. Dates are never invented.
- Nothing in this package imports the capital facade or control layer.
- Price evidence always displays `UNCERTIFIED`; `BLOCKED` while
  `TWELVEDATA_API_KEY` is absent.
- Untrusted intake text is HTML-escaped; only `docs/controlled_live_pilot/*.md`
  is served read-only.
