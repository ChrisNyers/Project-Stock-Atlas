# Stock Atlas UI integration — capability matrix

Generated from `atlas_ui/app.py:CAPABILITIES` (single source of truth; a test keeps this file in sync).
Paper only. Capital status: **NO REAL PORTFOLIO ACTION**.

| Capability | Status | Detail |
|---|---|---|
| A. Overview: canonical Cycle 0 portfolio/policy, pilot status, candidates | **PROVEN WORKING WITH REAL BACKEND** | Parsed and re-validated from the frozen baseline record (28 names, sum $624,905.93); as-of and source shown. |
| B. Intake + immutable pre-Atlas stance (versioned, provenance, no source privilege) | **PROVEN WORKING WITH REAL BACKEND** | Writes the existing append-only discovery ledger; later versions are labelled revisions, never edits. |
| C. Filings / financial research ingestion into the UI | **NOT IMPLEMENTED** | Evidence is typed by the human with PRIMARY/SECONDARY/UNCERTIFIED labels (existing evidence ledger). No SEC fetch is wired to the UI yet. |
| D. Live price + XNYS session (Gate B) | **BLOCKED WITH EXACT REASON** | Wired to the verified Gate B path; TWELVEDATA_API_KEY is absent in this environment, so no live observation can be bound. Offline fail-closed paths are tested. |
| E. Stage 7 via CapitalDecisionFacade.run_stage7, retained hashed run, side-by-side grid | **FIXTURE-TESTED ONLY** | Runs through the real facade; exercised with a clearly-labelled FIXTURE price provider in DEMO mode and tests. No canonical run exists. MCD is PARKED until 2026-11-04. The Treasury reference is HUMAN-ATTESTED (not independently verified by Atlas); security decision is explicit, never defaulted; all % inputs use one unit. |
| F. Human Stage 8 (paper only): server-side recheck, non-action, ledger proof | **FIXTURE-TESTED ONLY** | Real facade + DecisionStore; funded actions also pass an adapter-level fresh-price checkpoint (run age, newer XNYS session, fresh Gate B rebind) because the facade alone does not check run age; rejected paths leave zero rows in tests; no canonical decision exists. |
| G1. Decision history (existing append-only ledger) + manual revisit note | **PROVEN WORKING WITH REAL BACKEND** | Reads the real ledger; revisit is a linked dated note, the original record is never edited. |
| G2. Outcome vs cash/SPY with matched as-of dates; automatic trigger monitoring | **NOT IMPLEMENTED** | Needs a fresh bound price per revisit and approved cadence/alert delivery; not claimed. |
| Real trades / broker connectivity / execution | **NOT IMPLEMENTED (by design)** | Paper only. No order API exists. |

