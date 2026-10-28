# Frozen-control change record 001 — mandatory funded-decision freshness safeguard

| | |
|---|---|
| Date | 2026-10-28 |
| Status | **PROPOSED (this commit, before any code change) → IMPLEMENTED (next commit)** |
| Authority | Human decision of 2026-10-28 (items 1–3), after the independent review of `d2df7af` and the remediation `c8c8c09` |
| Baseline | `c8c8c09`; frozen control files pinned in `atlas_ui/FROZEN_CONTROL_SHA256.txt` |
| Classification | Targeted safety remediation of a demonstrated defect. Not an architecture change. |

## 1. The demonstrated defect

`CapitalDecisionFacade.record_final_decision` accepts a funded `INITIATE`/`ADD` backed by a retained, hash-matching
`ELIGIBLE FOR STAGE 8` Stage 7 run of **any age**, priced on a session that is no longer the latest completed one, with no check
that the price or the Treasury reference still match what Stage 7 used. `tests/test_atlas_ui_remediation.py::
test_f6_characterization_the_frozen_facade_alone_does_not_check_run_age` shows an 8-day-old run accepted. The guard added in
`c8c8c09` lives in `atlas_ui/service.py`, so any other caller of the facade bypasses it.

## 2. Precise proposed change (and nothing else)

**A. `stock_atlas/pipeline.py` — retain the pricing basis inside the hashed Stage 7 artifact.**
`run_stage7_pipeline` adds one key, `price_basis`, to the bundle it already freezes:
`{"price_snapshot": underwriting.price_snapshot, "treasury_reference": <the TREASURY_CASH alternative's market_reference or null>,
"known_latest_session_date": known_latest_session_date}`. `evaluate_stage7_candidate`, the result, the rendered text, eligibility and
every other rule are untouched. Reason: the ledger already binds `stage7_artifact` by SHA-256, so putting the basis inside that artifact
means the frozen price/reference cannot be altered without breaking the ledger's own hash — a sidecar file would not have that property.

**B. `capital_decision_facade.py` — a funded action cannot be recorded without freshness evidence.**
- New frozen dataclass `FundedFreshnessEvidence(fresh_price: PriceSnapshot, treasury_reattested: MarketReferenceSnapshot)`.
- New keyword `funded_freshness: FundedFreshnessEvidence | None = None` on `record_final_decision`. The default exists only because
  HOLD CASH / DO NOTHING do not need it. **For INITIATE/ADD, `None` raises `ControlFailure`; omission can never bypass verification.**
- For INITIATE/ADD, after the existing "Stage 7 must be ELIGIBLE" check and before persistence, the facade requires ALL of:
  1. the retained Stage 7 artifact contains `price_basis` (older artifacts fail closed: re-run Stage 7);
  2. `created_at − decision_time` is between −60 s and `MAX_STAGE7_RUN_AGE_HOURS = 96.0` (provisional, subordinate rule);
  3. **session authority**: `latest_completed_session(created_at, mic)` (the repo's independent exchange calendar, offline, never the provider)
     equals the frozen price's completed session, and equals the fresh evidence's completed and price sessions; the MIC is taken from the
     frozen `quoted_instrument`, and a missing or unsupported MIC fails closed;
  4. **exact evidence consistency**: the fresh `PriceSnapshot` equals the frozen one on every field (security, quoted key and instrument,
     ticker, currency, provider, price, quote time, sessions, status, adjustment, mode, freshness). There is no tolerance;
  5. currency is `USD` (USD-only scope; no FX subsystem is added, a non-USD run fails closed);
  6. the re-attested Treasury `MarketReferenceSnapshot` equals the frozen reference on key, value, as-of, provider and currency, and its
     as-of is within 96 h of `created_at`; a missing frozen reference fails closed.
- On success the facade retains the checked evidence as a hashed artifact (`<record_id>.funded_freshness.json`) beside the Stage 7 artifact.
- `HOLD CASH` and `DO NOTHING` are unchanged and need no evidence.

**C. `atlas_ui/service.py`** passes the fresh Gate B snapshot and the human's Treasury re-attestation to the facade (its own earlier
checks stay as a first, more explanatory layer). This is the caller, not a control.

## 3. Explicitly NOT changed

`stock_atlas/controls.py`, `decision_store.py`, `models.py`, `freeze.py`, `presentation.py`, `portfolio.py`; `allocation_rationale.py`;
`live_price_binding.py`; `live_session_calendar.py`; Stage 7 eligibility, ranges, alternatives, constraints, the STARTER cap, ADD-ONLY policy;
Human Stage 8 authority; no new provider, agent, optimizer, scoring, FX handling, or ML.

## 4. Impact

- New Stage 7 artifacts carry one extra key, so their hashes differ from what the old code would have produced. No canonical Stage 7 run
  exists, so nothing real is invalidated; any older-format artifact can still back HOLD CASH / DO NOTHING but not INITIATE/ADD.
- Existing tests that record a **successful funded** decision through the facade must now supply evidence and a calendar-consistent session;
  these fixture updates are limited to supplying the new argument and aligning fixture dates with the real XNYS calendar. Their assertions
  about frozen behaviour are unchanged.
- Stage 8 paper decisions in the UI are unaffected when evidence is unchanged.

## 5. Residual (stated, not hidden)

- A caller that fabricates a `fresh_price` that merely copies the frozen one passes the equality check; provenance of the fresh bind remains
  the caller's Gate B call, as the provenance of every other caller-supplied input already is. The calendar check (independent) and the age
  bound are not caller-controlled.
- Appending a funded record straight into `DecisionStore` (skipping the facade) remains an unsanctioned path exactly as before; this change
  does not alter it. A repo-wide scan test asserts no production code does so.

## 6. Verification plan

Regression tests for direct-facade and UI-funded paths (stale run, new session, changed price/provider/instrument/currency, omitted evidence,
Treasury change, USD-only, old-format artifact); ledger byte-identity after every rejection; HOLD CASH / DO NOTHING still recorded; the previously
accepting direct-facade scenarios replayed against `c8c8c09` and against the fixed code; the control pin regenerated and reviewed against this record.


---

## 7. Implementation outcome (appended after the proposal; sections 1–6 are unchanged)

Status: **IMPLEMENTED** in the commit that follows `af6f61f`.

**Files changed in frozen-control territory (exactly two):** `stock_atlas/pipeline.py` (+11 lines: the `AlternativeType` import, the
Treasury lookup and the `price_basis` key; no existing line modified or removed — a test asserts the diff is purely additive) and
`capital_decision_facade.py` (new `FundedFreshnessEvidence`, `MAX_STAGE7_RUN_AGE_HOURS`, the `funded_freshness` keyword and
`_verify_funded_freshness`). The control pin `atlas_ui/FROZEN_CONTROL_SHA256.txt` differs from `c8c8c09` in exactly those two lines.
`controls.py`, `decision_store.py`, `models.py`, `freeze.py`, `presentation.py`, `portfolio.py`, `allocation_rationale.py`,
`live_price_binding.py`, `live_session_calendar.py` are byte-identical.

**Test fixtures adjusted (assertions about frozen behaviour unchanged):** `tests/test_integration_facade.py` (fixture session moved to
2026-09-02 so it agrees with the real XNYS calendar at `NOW`; `quoted_instrument` added; helper `funded_evidence`; the one funded-success
test passes the evidence), `tests/test_allocation_rationale.py` (`_fund` passes the evidence; one attested-session test now compares
against 2026-09-03, still a mismatch), `tests/test_atlas_ui*.py` (characterization of the old gap replaced by the rejection; frozen-layer
test now allows exactly the pipeline change).

**Previously accepting cases (replay of `atlas_ui/evidence/direct_facade_cases.py`):**

| Direct-facade funded INITIATE | `c8c8c09` | after this change |
|---|---|---|
| 8-day-old eligible run | ACCEPTED (1 row) | REJECTED, 0 rows — STALE Stage 7 run |
| same-session run, evidence omitted | ACCEPTED (1 row) | REJECTED, 0 rows — evidence is mandatory |
| fresh price $100 → $130 | ACCEPTED (1 row) | REJECTED, 0 rows — price does not reproduce |
| unchanged evidence (control) | ACCEPTED | ACCEPTED (1 row; check artifact retained) |

Raw outputs: `atlas_ui/evidence/EVIDENCE_BEFORE_c8c8c09.txt`, `EVIDENCE_AFTER_fix.txt`.

**Still true (section 5):** raw `DecisionStore.append` is not a sanctioned path and is unchanged; the freshness of the fresh bind is only as
trustworthy as its caller's Gate B call; the 96 h bound is provisional and subordinate to session authority and exact consistency.

*Correction to section 7 (append-only):* `git diff --stat c8c8c09 3466a03` measures `stock_atlas/pipeline.py` at **+10 lines, 0 removed**
(not +11) and `capital_decision_facade.py` at +127/−1 (the one removed line is the widened `datetime` import).
