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


---

# Addendum — review of `d2df7af` (critical: same-session price change)

**Reproduced first.** The reviewer's case (Stage 7 priced at $100, Stage 8 re-bound at $130, same session and security) was
accepted by the d2df7af gate because it compared only security, freshness and session date. It is now a failing-then-passing
regression test.

**Fix (`atlas_ui/service.py`, `_fresh_price_gate` only; no frozen control touched).** A funded INITIATE/ADD must now have a fresh Gate B bind
that reproduces the **frozen Stage 7 PriceSnapshot evidence exactly** — security key, quoted key, quoted instrument (venue/class label),
ticker, currency, provider, price, quote timestamp, price and completed-session dates, session status, adjustment basis, price mode,
freshness, and the XNYS attestation (exchange, calendar, session date). **There is no tolerance**: any difference means *re-run Stage 7*;
old return ranges are never reused. The Treasury reference must be **re-attested by the human at Stage 8** and must equal the frozen
value and date exactly and be inside the 96h window. Both sides of every passing check (frozen and fresh bindings, re-attestation) are
appended to `stage8_price_checks.jsonl`. Non-actions need none of this.

**Tests** (`tests/test_atlas_ui_price_consistency.py`, 19): $100→$130 rejected for INITIATE and ADD with a message naming the field; no tolerance
(100.01, 99.99, 100.5, 70); identical evidence is accepted and logged; other gates still apply; provider, quote-timestamp (same-session
re-quote), instrument/class label, venue, currency and security-identity changes rejected; Treasury value/date/source/attestation mismatches and
omissions rejected; non-USD cannot run; DO NOTHING stays available; every rejection leaves the ledger byte-identical. **Negative mutation shown:**
removing the price comparison fails 9 tests; removing the Treasury value comparison fails the Treasury test.

**Direct-facade bypass.** A repo-wide AST scan (a test) proves that in production code the only caller of `record_final_decision` is
`atlas_ui/service.py` and nothing but `capital_decision_facade.py` opens a `DecisionStore`. It cannot prove that an operator will not
write a script that calls the facade directly with an old run (the characterization test shows the unchanged facade would accept it).
Closing that is a **formally authorized narrow safety fix to a frozen control** — not made here. Proposal for your decision: an optional
`max_age_hours` / `price_check_ref` argument on `record_final_decision` that the UI always supplies.

**Open items for your approval (not decided by me):** (1) `MAX_RUN_AGE_HOURS = 96` is an adapter policy borrowed from the frozen reference-data window; the
primary freshness controls are now session equality and exact price/Treasury reproduction, so the age cap is a conservative secondary bound — keep,
change or drop; (2) the SPY/beta band is a human assumption, not a market observation, so there is nothing to re-bind — it is carried unchanged from the
frozen run; (3) FX: only USD is supported, so no FX/reference re-binding exists to check.

**Frozen controls:** the 12 pinned files are byte-identical (test + `git diff --quiet` against `d2df7af` and `4c71d06`).
