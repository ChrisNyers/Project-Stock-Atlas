# Atlas Operating MVP v0.1 — Discovery Loop + UI

Workflow support only. Records and shows where each candidate is; it does not
rank, score, size, fetch data, or touch capital. Human Stage 8 remains the sole
capital authority. **NO REAL PORTFOLIO ACTION.**

## Vocabulary (the only one)

`SURFACED → QUICK_TEST → UNDERWRITING → PARKED / REJECTED / READY_FOR_CAPITAL_COMPARISON`

"Continue underwriting" = stay in `UNDERWRITING` (add a note).
**`QUICK_TEST` is mandatory** for every candidate except the grandfathered MCD
and RPM (`ledger.GRANDFATHERED`), whose direct SURFACED → UNDERWRITING history is
preserved unrewritten. A new candidate reaches `UNDERWRITING` only after it has
been in `QUICK_TEST` and has a recorded cheapest-falsification result that is not
`FALSIFIED` (including via PARKED).
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

## Candidate page = the underwriting template

Glance card (state, why surfaced, survived QUICK_TEST?, strongest FOR/AGAINST,
unresolved question, next dated catalyst) → investment question → cheapest
falsification + result → six tagged evidence groups (FACT, MANAGEMENT CLAIM,
CONTEXT, INFERENCE, VARIANT, CAPITAL IMPLICATION) → unresolved questions →
current state → capital-comparison **placeholders** (SPY, Treasury/Cash, Do
Nothing, relevant existing holdings; nothing computed; Stage 7 never invoked).

Every evidence item carries `PRIMARY` / `SECONDARY` / `UNCERTIFIED`, a
direction (FOR / AGAINST / NEUTRAL), an optional reference and a known-at date.
"Strongest" is a human designation, never computed. Errors are retracted, not
edited; the original event stays in history. For INFERENCE and CAPITAL
IMPLICATION use the weakest input source as the grade.

```bash
.venv/bin/python -m operating_mvp falsify X --test "..." --result SURVIVED --grade PRIMARY --ref "..." --known-at 2026-10-01
.venv/bin/python -m operating_mvp evidence X --tag FACT --direction AGAINST --grade PRIMARY --text "..." --ref "10-K" --known-at 2026-02-24
.venv/bin/python -m operating_mvp strongest X AGAINST 12
.venv/bin/python -m operating_mvp unresolved X "question"
.venv/bin/python -m operating_mvp resolve X 12 RETRACTED --note "why"
```

## Structure

| File | Role |
|---|---|
| `ledger.py` | append-only, hash-chained event log; states, transitions, intake, replay |
| `data/candidate_ledger.jsonl` | the record (MCD, RPM backfilled, flagged `backfilled`) |
| `seed.py` | one-time backfill of MCD/RPM history, then their template/evidence entries, from the frozen cycle records (appends only) |
| `ui.py` | board, candidate page, loopback server; intake / state / note forms |
| `__main__.py` | CLI |

## Rules enforced by tests

- Sources: HUMAN, SCOUT, SUE, NUTSTUFF, LIQN, OTHER (needs detail). Recorded as
  provenance; never used to order, filter or gate.
- PARKED requires `waiting_on`; a date is optional and flagged *officially
  verified* or not. Dates are never invented.
- Nothing in this package imports the capital facade or control layer.
- Price evidence always displays `UNCERTIFIED`; `BLOCKED` while
  `TWELVEDATA_API_KEY` is absent.
- Untrusted intake text is HTML-escaped; only `docs/controlled_live_pilot/*.md`
  is served read-only.
