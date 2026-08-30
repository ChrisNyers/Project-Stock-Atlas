# Live Validation Harness — Version Status

| File | Status | Notes |
|------|--------|-------|
| `validation_harness_live_v3.py` | **ACTIVE** | The live-validation harness. Invoked by `./run_live_validation.sh`. |
| `validation_harness_live_v2.py` | Historical | Predecessor. Retained for audit/history only. Do not run. |
| `validation_harness_live.py` (v1) | Historical | Original skeleton. Retained for audit/history only. Do not run. |

## Why v3 is active

Lineage: **v1** (skeleton, placeholder tests) → **v2** (real assertions, 11 gates
A–K, `NameError` crash at Gate I) → **v3** (fixes the 6 static-review defects,
documented in `V3_DELIVERY.md` / `V3_STATIC_AUDIT.md`).

## Phase 4A.5.0 baseline repairs applied to v3 (infrastructure only — no gate
meanings changed)

- SEC `filings.recent` field names corrected: `accessionNumber`,
  `acceptanceDateTime` (were `accession_number`, `acceptance_datetime`).
- `acceptanceDateTime` is parsed as the ISO-8601 **UTC** value SEC actually
  returns; the raw source string is preserved and normalized to a tz-aware UTC
  datetime with **no offset reinterpretation** (the old code wrongly treated it
  as US/Eastern and added 4 hours).
- Gate J no longer throws `IndexError`; missing amendment evidence yields the
  intended `BLOCKED` state.
- Every run now writes two artifacts to `live_validation_results/`:
  `<UTC-timestamp>_gate_results.json` and `<UTC-timestamp>_gate_results.md`.
  Artifacts are written even for a partial or failed run.
- A gate raising an exception is recorded as `FAIL` (with traceback) instead of
  aborting the harness.

Do not delete v1 or v2.
