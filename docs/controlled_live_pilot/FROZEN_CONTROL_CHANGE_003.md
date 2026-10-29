# Frozen-control change record 003 — remove the `pytest`-presence clock exemption (pre-change record; written BEFORE implementation)

| | |
|---|---|
| Date | 2026-10-29 |
| Status | **AUTHORIZED by the human in chat (quoted in §5); not yet implemented when this section was written — see §6 for the outcome** |
| Trigger | Independent review of `1683f98` (`Stock_Atlas_1683f98_Independent_Review_2026-10-28.md`), Material finding 1 |
| Baseline | HEAD `1683f98` (change 002 included) |
| Frozen-control files touched | `capital_decision_facade.py` only. `stock_atlas/*`, `allocation_rationale.py`, `live_price_binding.py`, `live_session_calendar.py` are not touched. |
| Classification | Targeted repair of my own change 002 guard; not an architecture change, no investment control (size, thresholds, 96 h bound, USD-only scope) is altered |

## 1. The reproduced failure

Change 002 made the funded-decision clock a private method `CapitalDecisionFacade._now()` and tried to stop a caller replacing it:
`_trusted_now()` refused a replaced `_now` **unless `"pytest" in sys.modules`**. That condition is not a trust boundary — any ordinary Python
process can `import pytest` and then assign `facade._now = lambda: <September>`.

Reproduced on `1683f98` by `atlas_ui/evidence/probe_standalone_clock_replacement.py`, run as a plain `python` script (no pytest runner),
pytest merely imported, real wall clock 2026-10-29, fixture run dated 2026-09-02 (≈57 days old, limit 96 h):

```
ACCEPTED  ledger_rows=1  replace instance facade._now
ACCEPTED  ledger_rows=1  replace class CapitalDecisionFacade._now
ACCEPTED  ledger_rows=1  replace capital_decision_facade.datetime
```
(`atlas_ui/evidence/change003/clock_probe_BEFORE.txt`.) The reviewer's reproduction (instance `_now`) is the first line. The two other lines are
further ordinary routes I found while reproducing; the fix must close them as well. My change-002 tests missed this because they only
simulated "production" by *deleting* `pytest` from `sys.modules` inside a pytest run.

## 2. Change (smallest that closes it)

`capital_decision_facade.py` only.

**Removed:** `CapitalDecisionFacade._now`, `CapitalDecisionFacade._trusted_now`, the `_ORIGINAL_NOW` sentinel, and every reference to `pytest` /
`sys.modules`. Nothing in the production path consults the test runner any more, and no attribute, subclass override or class patch on the facade
can choose the clock.

**Public entry point `record_final_decision` keeps its exact signature** (no clock parameter) and now reads the time from a sealed module-level
clock, `_BACKEND_UTC_NOW`, built once at import from the real `datetime.now`/`timezone.utc` objects bound into a closure (so a later patch of the
module's `datetime` name no longer changes it). It forwards everything unchanged to a **private** implementation
`_record_final_decision_at(..., now)` that contains the existing body, with `now` threaded to `_verify_funded_freshness(..., now)`.
`_verify_funded_freshness` becomes a pure function of its inputs plus the `now` it is given (still no ledger write on failure; same checks,
same 96 h provisional bound, same ±5-minute `created_at` consistency check, same UTC-only requirement for `now`).

**Deterministic testing without a production switch:** tests pin time with a pytest fixture (`tests/conftest.py::facade_clock`) that replaces the
*test-side* binding of `record_final_decision` with a function calling `_record_final_decision_at(..., now=<pinned>)`. That code lives only under
`tests/`; no production module references `_record_final_decision_at` (enforced by an AST test).

No change to: size caps, thresholds, price/Treasury/session checks, the Stage 7 artifact format, the decision ledger schema, `FundedFreshnessEvidence`,
HOLD CASH / DO NOTHING behaviour, or the 96 h bound (it stays provisional).

## 3. Tests required (written to fail on `1683f98`, pass after)

Run in **subprocess scripts outside the pytest runner** (pytest imported on purpose), each asserting REJECTED + ledger byte-identical + no freshness
artifact written: replace instance `_now`; patch class `_now`; subclass defining `_now`; patch `capital_decision_facade.datetime`; plain
`import pytest` + honest-looking stale call. In-runner: `record_final_decision` has no clock parameter; no `pytest`/`sys.modules`/`_now` text in the
module; AST test that only `tests/` and `atlas_ui/evidence/` reference `_record_final_decision_at`; legitimate fresh funded decision accepted;
HOLD CASH / DO NOTHING still recordable; mutation test (re-introducing a replaceable clock must fail the new tests).

## 4. Residual (stated, not hidden)

Python cannot stop code **running inside the same process with the ability to modify that process** from changing it. After this change an
ordinary caller can no longer choose the clock through any facade attribute, subclass, `pytest` import or `datetime` patch. A caller who
deliberately (a) calls the private `_record_final_decision_at(..., now=...)`, (b) overwrites the module's `_BACKEND_UTC_NOW`, or (c) replaces
`record_final_decision` itself is editing the control, not using it; that is prevented operationally (who may run or modify backend code on the
host), not by Python. The evidence probe reports (a) and (b) separately and labelled as this residual; they are not claimed closed.

## 5. Disposition (recorded before implementation)

The human's message of 2026-10-29: "Trusted clock: The current check permits clock replacement when `pytest` is imported. An ordinary standalone
Python script reproduced acceptance of a stale paper INITIATE using this mechanism. Remove that bypass and retain deterministic testing without
making the production clock caller-controllable. Document any frozen-control change before implementation." and "Do not add new features or begin
another workstream until these corrections pass. … No live funded decisions."

I read that as authorization for exactly the change in §2 and nothing else. Anything beyond it (any other control file, any threshold, any new
data source or feature) is not authorized and is not done.

## 6. Implementation outcome

_(appended after implementation; §§1–5 stay unchanged)_
