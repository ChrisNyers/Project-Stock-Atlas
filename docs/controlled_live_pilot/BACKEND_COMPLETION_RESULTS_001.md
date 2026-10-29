# Backend completion — results (2026-10-28, after change 002)

Capital status: **NO REAL PORTFOLIO ACTION.** Read-only market/SEC retrieval only; no Stage 7 run, no Stage 8 decision, canonical `decisions.jsonl` has **0 rows**.
MCD (2026-11-04) and RPM (2026-11-09) remain PARKED; GEV, RMD, ORCL are SURFACED (named by the human; no stance, no QUICK_TEST, no promotion).

## 1. Trusted-clock safety correction (change 002) — verified
`capital_decision_facade.py` measures run age, XNYS session and Treasury freshness on a trusted backend UTC clock; a caller `created_at` never sets that time and must be within 5 min of it in
either direction; there is no public clock parameter; a replaced clock fails closed outside a pytest run. The eight-day-old funded call with a backdated timestamp, ACCEPTED at `11bd220`
(`EVIDENCE_BACKDATED_CREATED_AT_at_11bd220.txt`), is REJECTED with zero ledger writes (`…_after_change_002.txt`). Promoted regression + 25 trusted-clock tests + 3 negative mutations. Fresh legitimate
decisions and HOLD CASH / DO NOTHING still work.

## 2. Live market-data results (TwelveData + independent XNYS calendar), actual
- Read-only bind, 2026-10-28 close, all `provider=twelvedata`, USD, FRESH, quoted instrument `(XNYS)`: MCD $250.50 · GEV $878.03 · RMD $250.17 · ORCL $144.54. Identity keys `SEC-CIK:0000063908:MCD`, `…1996810:GEV`, `…0000943819:RMD`, `…0001341439:ORCL`. XNYS venue eligibility confirmed (the bind enforces MIC).
- Live Gate B suite (`tests/test_gate_b_live_binding.py`, key loaded for the process only, throttled by the harness): **54 passed, 1 failed, 0 skipped** in 255 s. The failure was
  `test_b3_pilot2_frozen_basket_venue_readiness`: one provider call (ADBE) returned state `ERROR` inside a burst of ~10 symbols. **Re-run of that test alone: passed (77 s)**, and a direct ADBE call returned
  AVAILABLE / XNGS. The cause of the single ERROR is not established (no detail is kept by the adapter); I treat it as a transient provider/network error, not a pass-by-assumption. Output kept in `LIVE_GATE_B_SUITE_OUTPUT.txt`.
- Cross-check, research context only (Yahoo chart API, not a dependency): `regularMarketPrice` equals the Gate B price for all four names. ORCL moved from 130.53 to 144.54 (+10.7%) on 2026-10-28.
- Limitations: price evidence is a completed-session close (no intraday); the ELIGIBLE funded branch has never been run on live data (no eligible candidate exists); the key used is the one in the gitignored `.env`
  (no code loads it; I passed it to the process on request only) — rotate it if it was ever exposed.

## 3. Research and data-source verification (MCD, GEV, RMD, ORCL)
- SEC company facts → PRIMARY evidence in the existing ledger (33 / 27 / 34 / 29 facts), each with accession URL, filing date as known-at, period, units; gaps recorded as UNVERIFIED/CONFLICTED questions (not imputed).
- **25/25** selected core facts (revenue, operating income, net income where selected, diluted EPS, CFO, capex, diluted shares) re-found as printed numbers in each company's own 10-K primary document
  (`evidence/SOURCE_VERIFICATION_001.json`, document SHA-256 recorded; the documents are not stored). This verifies selection/scale/period against the filing; it is not a second vendor.
- Honest data findings: MCD's share count is tagged in millions (verified by EPS × shares ≈ net income); GEV capex and several debt legs are UNVERIFIED (so GEV free cash flow is not established); RMD and ORCL net income is CONFLICTED between approved
  concepts (so FCF conversion and yield are omitted); ORCL FY2026 capex ($55.7B) exceeds operating cash flow ($32.0B), i.e. free cash flow ≈ −$23.7B, verified in the filing.
- Assessments (descriptive research level, **DRAFT_BY_RECORDER**, not human-accepted): MCD PARKED FOR REVISIT (lifecycle; earlier 10-07 cases NOT re-run at today's price; +7.9% price-only observation linked); GEV, RMD, ORCL INSUFFICIENT EVIDENCE
  (no stance, no QUICK_TEST, no variant, no return band substantiated). **No example reached SUPPORTED — none is permitted yet** under the lifecycle rules, and I did not invent a stance or a conviction.

## 4. Not done / requires a decision
See `DELIVERY_REPORT.md`.

## 5. Corrections after independent review (appended 2026-10-29; §§1–4 unchanged)
- The statement above that "a replaced clock fails closed outside a pytest run" is **withdrawn**: that guard was bypassable by an ordinary script (see `FROZEN_CONTROL_CHANGE_003.md`); it was removed and the clock is no longer replaceable through any facade attribute.
- The "clean ZIP extract 519 passed / 26 skipped" check reported with this delivery was **not valid evidence of portability**: the research index held absolute paths to the original machine, which still existed, so the extract read the originals. Fixed and re-verified with the original tree blocked (`FROZEN_CONTROL_CHANGE_003.md` §7).
