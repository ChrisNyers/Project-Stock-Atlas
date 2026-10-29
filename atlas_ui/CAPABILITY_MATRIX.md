# Stock Atlas — capability matrix (2026-10-28, HEAD 11bd220 + backend-completion Workstream A)

Generated from `atlas_ui/app.py:CAPABILITIES`. Vocabulary: PROVEN LIVE / PROVEN CANONICAL OFFLINE / FIXTURE-TESTED / BLOCKED / NOT IMPLEMENTED.
Nothing is PROVEN LIVE. Paper only. Capital status: **NO REAL PORTFOLIO ACTION**.

| Capability | Status | Detail |
|---|---|---|
| A. Overview: canonical Cycle 0 portfolio/policy, pilot status, candidates | **PROVEN CANONICAL OFFLINE** | Parsed and re-validated from the frozen baseline record (28 names, sum $624,905.93; defensive ≈ $59K so the denominator is approximate); as-of and source shown. |
| B. Intake + immutable versioned pre-Atlas stance (source provenance, no source privilege, QUICK_TEST mandatory) | **PROVEN CANONICAL OFFLINE** | Writes the existing append-only discovery ledger; later stance versions are labelled revisions, never edits. |
| C1. SEC/issuer ingestion modules (sec_adapter, xbrl_parser, identity_resolver, point-in-time) | **PROVEN CANONICAL OFFLINE** | Exist and are regression-tested in the repo (Phase 4A.5); NOT yet connected to the UI or the evidence ledger. |
| C2. Filings-to-evidence adapter and source-backed underwriting view in the UI | **NOT IMPLEMENTED** | Held behind the Workstream A safety finding; evidence is still typed by the human with PRIMARY/SECONDARY/UNCERTIFIED labels. |
| D. Live price + XNYS session (Gate B) | **BLOCKED** | Wired to the verified Gate B path; not run live — TWELVEDATA_API_KEY is not in the server environment (a key exists in the gitignored .env but no code loads it), and the read-only check is held behind the safety finding. Offline fail-closed paths are tested. |
| E. Stage 7 via CapitalDecisionFacade.run_stage7, retained hashed run, side-by-side alternatives | **FIXTURE-TESTED** | Runs through the real facade with a FIXTURE price provider in DEMO mode and tests. No canonical run exists. MCD is PARKED until 2026-11-04. Treasury reference is human-attested; security decision is explicit; all % inputs use one unit. |
| F. Human Stage 8 (paper only): facade-enforced funded freshness, non-actions, ledger proof | **FIXTURE-TESTED** | Real facade + DecisionStore; funded freshness is mandatory (FundedFreshnessEvidence, frozen-control change 001) and rejected paths leave zero ledger rows. KNOWN MATERIAL GAP: freshness is measured against the caller-supplied created_at, so a direct caller can backdate it (reproduced; strict-xfail test; proposal FROZEN_CONTROL_CHANGE_002_PROPOSED.md awaits disposition). |
| G1. Decision history (append-only ledger) + manual linked revisit note | **PROVEN CANONICAL OFFLINE** | Reads the real ledger; a revisit is a dated linked note, the original record is never edited. |
| G2. Outcome vs time-matched cash/Treasury and SPY; monitoring cadence | **NOT IMPLEMENTED** | Needs reliable adjusted total-return and Treasury evidence per revisit; not claimed. |
| H. Candidate cohort side-by-side research comparison (no ranks) and 'attractive at the verified price?' assessment view | **NOT IMPLEMENTED** | Held behind the Workstream A safety finding. MCD and RPM stay PARKED; their dates are revisit triggers, not promotions. |
| Real trades / broker connectivity / execution | **NOT IMPLEMENTED** | By design: paper only. No order API exists. |

