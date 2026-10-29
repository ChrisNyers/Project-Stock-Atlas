# Backend completion — mandatory preflight note (2026-10-28)

**Repository** `/Users/chrisnyers/Documents/Project-Stock-Atlas/stock-atlas-sprint1-live`, branch `main`, working tree clean (only the untracked `deliverables/` export folder).
**HEAD** `11bd220` (2026-10-28 19:54 −04:00), parent `3466a03`. Recent: `11bd220` change-record correction · `3466a03` change 001 implementation · `af6f61f` change 001 proposal · `c8c8c09` UI remediation 2 · `d2df7af` · `fe268b5` · `106ba59` LIQN · `a1475dd` · `d94db95` · `2a672cc` checkpoint · `a1dd4df` RPM parked.
**Ancestry verified:** `af6f61f`, `3466a03`, `11bd220` and the accepted `4c71d06` are all ancestors of HEAD; HEAD is not newer than the reported closure.

**Authoritative records read at HEAD:** `docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md`, `docs/STOCK_ATLAS_DECISION_LOG.md`,
`controlled_live_pilot/CYCLE0_BASELINE_001.md` (Correction 002 governs), `FROZEN_CONTROL_CHANGE_001.md`, `INTERIM_CHECKPOINT_001.md`,
MCD/RPM stance and underwriting records, `atlas_ui/REMEDIATION_REPORT.md`, `operating_mvp/README.md`.
**Canonical state:** Cycle 0 Correction 002 (2026-10-07): 28 stocks exactly $624,905.93; defensive ≈ $59,000 (approximate); identified ≈ $683,905.93
(approximate); ADD-ONLY; new outside capital $25–50K, T+1. MCD PARKED until 2026-11-04 (official IR calendar); RPM PARKED until 2026-11-09
(company-announced Investor Day). Both are **revisit triggers, not promotions**; neither is READY, neither can start Stage 7. The September $500K handoff is
historical and loaded nowhere. No later approved record supersedes any of this.

**Control changes since the accepted baseline `4c71d06`:** earlier accepted pilot extensions (`allocation_rationale.py`, `live_price_binding.py`,
`live_session_calendar.py`) and change 001 (`stock_atlas/pipeline.py` +10 additive lines; `capital_decision_facade.py`). Pinned in `atlas_ui/FROZEN_CONTROL_SHA256.txt`.
**Test baseline at HEAD:** 473 passed, 25 skipped (live Gate B tests, BLOCKED), 1 warning.

**Existing capabilities (so nothing is rebuilt):** discovery ledger with QUICK_TEST, evidence grades and known-at (`operating_mvp`); SEC adapter (CIK/ticker
resolution, submissions, company facts, filings, archive), XBRL canonical-fact/period selection, identity resolver (security key ≠ issuer key), point-in-time service
(Phase 4A.5, repo-tested); Gate B price/session binding; Stage 7 facade, Human Stage 8, append-only ledger; `atlas_ui` dashboard.
**Remaining gaps:** no adapter from SEC/XBRL facts into the evidence ledger or UI; no source-backed assessment view; no cohort side-by-side; no outcome observation event;
live Gate B never run (key not in the server environment).

**Conflict / safety regression:** one — see `FROZEN_CONTROL_CHANGE_002_PROPOSED.md` (funded freshness measured against the caller-supplied `created_at`).
