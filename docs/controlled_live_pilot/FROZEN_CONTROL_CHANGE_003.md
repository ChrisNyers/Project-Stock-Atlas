# Frozen-control change record 003 — remove the `pytest`-presence clock exemption (pre-change record; written BEFORE implementation)

| | |
|---|---|
| Date | 2026-10-29 |
| Status | **AUTHORIZED by the human in chat (quoted in §5); IMPLEMENTED — see §6 (frozen-control change) and §7 (research portability, not a frozen control). §§1–5 are as written before implementation.** |
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

**What changed in `capital_decision_facade.py`** (diff in `SOURCE_DIFF_1683f98_to_corrected.patch`): removed `_now`, `_trusted_now`, `_ORIGINAL_NOW`, `import sys` and every `pytest`/`sys.modules`
reference; added the sealed clock `_BACKEND_UTC_NOW` (real `datetime.now`/`timezone.utc` bound in a closure at import); `record_final_decision` keeps its exact signature and forwards to the private
`_record_final_decision_at(..., now)` (the former body, with `now` threaded to `_verify_funded_freshness`, whose checks are unchanged; `now` must still be timezone-aware UTC, now validated by duck typing
so that patching the module's `datetime` name cannot change the verdict). No other control file changed (`git diff 1683f98 -- stock_atlas allocation_rationale.py live_price_binding.py live_session_calendar.py` is empty;
the 12-file pin was updated for `capital_decision_facade.py` only).

**Before / after, same extended probe, plain `python` (not pytest), pytest imported, real clock 2026-10-29, fixture run 2026-09-02:**

| Route | 1683f98 | after |
|---|---|---|
| replace instance `facade._now` (the reviewer's route) | **ACCEPTED**, 1 ledger row | REJECTED, ledger byte-identical |
| replace class `CapitalDecisionFacade._now` | **ACCEPTED** | REJECTED |
| subclass defining `_now` | **ACCEPTED** | REJECTED |
| replace `capital_decision_facade.datetime` | **ACCEPTED** | REJECTED |
| pytest imported, nothing replaced, honest stale call | REJECTED | REJECTED |
| RESIDUAL a: call private `_record_final_decision_at(now=...)` | n/a | ACCEPTED (documented, §4; not claimed closed) |
| RESIDUAL b: overwrite module `_BACKEND_UTC_NOW` | n/a | ACCEPTED (documented, §4; not claimed closed) |

Evidence: `atlas_ui/evidence/change003/clock_probe_BEFORE.txt` (original three-route probe), `clock_probe_BEFORE_extended_at_1683f98.txt`, `clock_probe_AFTER.txt`.

**Tests** (`tests/test_clock_not_caller_controllable.py`, 15): the reviewer's route run in a subprocess outside the pytest runner; instance / class / subclass / `datetime` patch / pytest-loaded / consistent-created_at / ADD as
well as INITIATE, each asserting REJECTED + ledger bytes identical + no freshness artifact; HOLD CASH / DO NOTHING still recordable through the real entry; a negative mutation inside the suite; source-text and AST checks
that the removed machinery stays removed and that only `tests/` and `atlas_ui/evidence/` reference the private time entry; naive / non-UTC time refused. **Mutation run:** re-introducing a replaceable clock into the facade
(`now=self._now() if hasattr(self, "_now") else ...`) fails 6 of the 15 (`change003/mutation_replaceable_clock_FAILS.txt`); the file was restored and its SHA-256 verified. Legitimate fresh funded decisions
(UI path, real clock) and the existing 100+ freshness/boundary/allocation tests pass with the fixture-side clock pin.

**Honest note on the residual.** Items a and b are accepted by the probe and are reported as such. They are not "ordinary caller" routes: both require code that deliberately calls a private name or overwrites a private
module global — editing the control from inside the process. Python cannot prevent that; who may run or modify backend code on the host must. The 96 h run-age bound remains provisional and subordinate.

## 7. Research snapshot portability (independent review finding 2) — NOT a frozen-control change

`atlas_ui/research.py` (not a control file) and `atlas_ui/app.py` only. Reproduced: the committed `research_index.jsonl` stored the writing Mac's absolute paths; `latest_snapshot` read only that path. **My own earlier
clean-extract check was falsely green** because the original Mac path still existed on the machine that built the ZIP, so the "extract" silently read the originals. Evidence: `change003/research_portability_BEFORE.txt`
(the extract's index points outside the extract; with the original path hidden all four of MCD/GEV/RMD/ORCL return `None`).

Fix: new entries store `artifact_rel`, a bare file name relative to the research workspace root (the directory holding `research_index.jsonl`); readers resolve a reference only inside that root (no separators, no `..`, NUL, hidden
or non-`.json` names, no symlinks, parent must equal the root), verify the index SHA-256, and check that the file belongs to the indexed ticker/security key. **Historical lines are not rewritten**: the four committed
lines (first-4-lines SHA-256 `96a3c536…`) and the four snapshot files keep their bytes and hashes (pinned in the tests); for their absolute `artifact_path` only the final file name is used and the directory part is never followed.
`latest_snapshot` returns `None` only when the index holds no snapshot for the candidate; a missing, tampered, mis-bound, symlinked, traversal or unreadable-index reference raises `ResearchIntegrityError`, an older snapshot is never
served in place of a corrupt newest one, and the UI/API show `RESEARCH EVIDENCE ERROR` / `UNAVAILABLE` and `research_error` instead of "no research".

**Tests** (`tests/test_research_portability.py`, 30): bare-name entries; moved workspace; byte-preserved history; all four committed snapshots load from a copy elsewhere; the original absolute path is never consulted (a tampered
copy is refused while the original is intact); foreign/Windows-style legacy paths; absent vs untrustworthy; corrupt newest not replaced by older; unreadable index line; cross-security binding; 13 malicious `artifact_rel`
values, legacy traversal, symlink, malformed hash; UI/API error surfacing; a clean extraction in another directory in a subprocess whose audit hook fails if any project file is opened from the original tree, rendering all four
cohort rows and assessment panels; and the extracted tree's own research tests. **Mutation run:** making the loader follow the old absolute path fails 6 of the 30 (`change003/mutation_absolute_path_FAILS.txt`); restored, hash verified.

**Not fixed, stated:** the Stage 7 run index in `atlas_ui/service.py` also stores each frozen reference's absolute `artifact_path` (the frozen `FrozenArtifactRef` carries it). No Stage 7 run exists in the committed data
(`decisions.jsonl` 0 bytes, no run index), so no delivered artifact is affected, but a workspace holding future runs would not be relocatable. That is the same class of defect in a path that touches a frozen control type;
I have not changed it without authorization and list it as a decision for the human.

