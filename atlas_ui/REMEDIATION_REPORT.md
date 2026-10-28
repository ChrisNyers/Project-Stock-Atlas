# Remediation report — independent review of `fe268b5`

Paper only. No funded decision, no trade, no live call. Capital status: **NO REAL PORTFOLIO ACTION**.

| Finding | Fix (atlas_ui only) | Regression tests |
|---|---|---|
| F1 percent unit | `_pct`: every % field divides by 100; finite and -100..100 only; remaining capacity and Treasury yield now percents too | boundaries 0, 0.5, 1, 3, 12, -2, 100; nan/inf/abc/blank/out-of-range; 0.5–1 not 50–100; 1–1 not 100%; mixed/inverted; facade spy sees 0.005/0.01 |
| F2 implicit BUY | `decision` + `decision_basis` required; no default; blank first option in the form; horizon no longer defaults to 5 | missing/blank/invalid refused with nothing written; explicit WATCH respected; form has no preselected BUY |
| F3 identity | ticker taken from the server-side candidate record; differing client ticker refused; bound price ticker re-checked; the form posts a candidate id only | cross-ticker forgery both ways, parked MCD/RPM, no-ticker candidate, HTTP 400, identity mismatch |
| F4 Treasury | source reference + explicit attestation required; typed value is HUMAN-ATTESTED, UNVERIFIED_BY_ATLAS in the evidence artifact and UI; future/malformed dates refused; old attested reference stays STALE (frozen control blocks) | no attest, no source, future, malformed, 30-day stale run blocked and cannot fund |
| F5 portfolio as-of | snapshot `as_of` = baseline valuation date 2026-10-07; evaluation time, age in days and the approximate-denominator note are retained; acknowledgement required; Overview shows ≈ $683,906 (stocks exact $624,905.93) | as_of, artifact fields, ack required, display |
| F6 stale Stage 7 → Stage 8 | **Investigated: the unchanged facade/store accept an 8-day-old ELIGIBLE run** (characterization test). Added adapter-level fresh-price checkpoint for INITIATE/ADD: run ≤ 96h, no newer completed XNYS session, candidate still READY, fresh Gate B rebind reproduces the security/session; check logged | week-old run, newer session, re-parked candidate, failed rebind, absent key; non-actions stay available; each leaves the ledger byte-identical |
| F7 run-id collision | microsecond timestamp + random suffix; existence checked before any write | rapid duplicate runs get distinct ids; forced collision rejected with the whole workspace tree hash unchanged |
| Artifact download | indexed artifacts served only if all retained hashes verify (409 otherwise) | tamper then download |

F8 (multi-candidate comparison, filings ingestion, outcomes) is deliberately not started.

## Baseline reconciliation
- Authoritative: `CYCLE0_BASELINE_001.md`, frozen 2026-10-07, Correction 002 (SHA-256 shown in the UI).
- 28 stocks sum **exactly $624,905.93** (checked by the loader; WSO $2,247.24).
- Defensive balance **≈ $59,000** (T-bills + money market, split not supplied) → identified value **≈ $683,905.93, approximate**. The denominator's uncertainty is not quantified in the record; every weight is therefore approximate, and a size near the 2% STARTER cap needs human caution.
- MCD is governed by the official IR calendar date **2026-11-04** (Q3); RPM by the company-announced **2026-11-09** Investor Day. Both remain PARKED; Stage 7 is refused for them, and revisit notes cannot change state. The handoff's $500,000 / 2026-09-02 snapshot is superseded and loaded nowhere.

## Frozen-control verification
`git diff --quiet fe268b5 -- stock_atlas capital_decision_facade.py allocation_rationale.py live_price_binding.py live_session_calendar.py market_data_providers.py identity_resolver.py` → no diff. `git diff 4c71d06 -- stock_atlas` → no diff. SHA-256 of the 12 control files is pinned in `FROZEN_CONTROL_SHA256.txt` and enforced by a test.

## Not done
Live Gate B smoke test (needs `TWELVEDATA_API_KEY` supplied locally by you); Playwright not installed, UI checked by hand and over HTTP; F8 features.
