# Stock Atlas — Master Project Plan

Authoritative status record. Updated as gates close; prior entries are not
rewritten.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## Architecture (unchanged)

```
Discovery → Underwriting → Stage 7 Capital Comparison → Fresh-Price Check
         → Human Stage 8 → Decision Record → Revisit
```

Stage 7 compares and emits no `PortfolioAction`. Stage 8 is human. Human
allocation authority is unchanged.

---

## Status

| Workstream | Status | Commit |
|---|---|---|
| Phase 4A.5.0 baseline | **COMPLETE / FROZEN** | `d37f654` |
| Phase 4A.5.1 – 4A.5.2A (SEC, identity, period, market data) | **COMPLETE** | `59911d2` |
| Pilots 1–4 manual methodology + doctrine | **COMPLETE** | `bf03986` |
| v0.2 control-layer merge + capital-decision facade | **ACCEPTED** (Final Code Red Team) | `8dba996` |
| Gate B live data binding (B1–B5) | **CLOSED** — awaiting Gate B Red Team review | `4c71d06` |
| **Pilot 1 Red Team Closeout — Stage 8 Allocation Rationale Fields** | **COMPLETE** | this commit |

---

## Pilot 1 Red Team Closeout — Stage 8 Allocation Rationale Fields

**Status: `COMPLETE`**

Three human-authored rationale fields bound to `FINAL_CAPITAL_DECISION`, plus a
completeness status and an unfunded-finalist field. Record/schema and
validation enhancement only — see
[`STOCK_ATLAS_DECISION_LOG.md`](STOCK_ATLAS_DECISION_LOG.md),
`ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`.

### Acceptance gate

| Criterion | Result |
|---|---|
| Three funded-line rationale fields bound to `FINAL_CAPITAL_DECISION` | **MET** |
| Low-rationale state supported | **MET** — `EXPLORATORY_LOW_RATIONALE` |
| Unfunded-finalist rationale supported | **MET** — `why_not_this_increment`, no rejection state |
| No ranking or sizing engine introduced | **MET** — asserted by tests E and D |
| Historical Pilot 1 decision preserved | **MET** — recorded verbatim, nothing backfilled |
| Governing tests pass | **MET** — 245 passed |

### Test evidence

| Suite | Result |
|---|---|
| Legacy `test_atlas.py` | 60 passed |
| Control layer v0.2 | 106 passed |
| Integration / facade | 16 passed |
| Gate B live binding | 31 passed |
| **Allocation rationale (new)** | **32 passed** |
| **Total** | **245 passed** |

Acceptance tests A–H all pass: complete funded line → `RATIONALE_COMPLETE`;
paper funded line with gaps → persisted as `EXPLORATORY_LOW_RATIONALE`; no
synthetic rationale; unfunded finalist without rejection; no sizing engine;
human authority preserved; Stage 7 unchanged; fresh-price control unchanged.

All 10 v0.2 control-layer files remain **byte-identical** to the accepted
archive — the new record subclasses `DecisionRecord` rather than modifying it.

---

## Pilot 1 Freeze Gate

| # | Condition | Status |
|---|---|---|
| 1 | Allocation-rationale fields implemented | **MET** |
| 2 | Validation behaviour passes | **MET** |
| 3 | Historical September 3 decision unchanged | **MET** |
| 4 | Master Project Plan updated | **MET** (this document) |
| 5 | Decision Log records `ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE` | **MET** |
| 6 | Governing test suite passes | **MET** — 245 passed |

> ## PILOT 1 — `FROZEN / COMPLETE`

One item is recorded for the human to resolve and does not block this freeze:
`PILOT1_SEPT3_ALLOCATION_RECORD_001.md` and
`PILOT1_STAGE8_HUMAN_DECISION_001.md` describe different decisions on different
dates over different universes. Both are preserved; neither supersedes the
other; no reconciliation was invented.

---

## Not authorized by this package

Pilot 2 · sentiment implementation · any further Pilot 1 architecture work.

Sentiment, if later explored, is `SHADOW_ONLY` and must not affect discovery
promotion, Stage 7, Stage 8, sizing, or final decision state until pilot
evidence establishes value.

Portfolio snapshot, capacity, overlap/`UNMEASURED`, common-driver cluster and
funding-pocket controls remain required before a controlled live-capital pilot.
They are **not** blockers for closing Pilot 1.
