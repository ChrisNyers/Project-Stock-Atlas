# Stock Atlas — Code & Implementation v0.2 Remediation

This package translates the validated Stock Atlas paper controls into a small executable, fail-closed control layer.

## Current gate

**Local control-layer remediation: COMPLETE.**

**Controlled live pilot: BLOCKED** until the remediated control layer is merged into the legacy `stock-atlas-sprint1-live` ingestion/orchestration stack and an integrated replay proves that legacy callers cannot write around the canonical path.

## Canonical path

`stock_atlas.pipeline.run_stage7_pipeline(...)` is the authoritative Stage 7 entry point. It returns a structured comparison result, a non-directive rendered comparison, and a hash of the exact Stage 7 bundle. A retained Stage 7 artifact is required for any final capital DecisionRecord.

Human Stage 8 decisions are persisted separately through `DecisionStore`. The store now verifies the frozen Stage 7 artifact, frozen input artifacts, prior position state, constraint state, and driver-cluster state before accepting final capital records.

The package root intentionally exports only:

- `run_stage7_pipeline`
- `Stage7Run`
- `DecisionStore`
- `ControlFailure`

Low-level helpers remain explicit-module implementation details rather than advertised application entry points.

## Red Team remediation implemented

- INITIATE/ADD cannot be written unless the retained Stage 7 artifact says `ELIGIBLE FOR STAGE 8`.
- Final capital records require retained, hash-matching input artifacts and a retained Stage 7 artifact.
- INITIATE/ADD requires `constraint_state=VERIFIED`; a human may acknowledge UNVERIFIED constraints for comparison, but cannot convert them into an executable capital action.
- Completed-session prices cannot be arbitrarily old while labeled FRESH. A recent-session max-age rule applies unless an explicit latest-session attestation is supplied.
- FX and Treasury/market-reference snapshots receive the same stale-consistent age check.
- UNMEASURED ETF overlap remains visible and receives no portfolio-fit credit; Stage 7 language rejects diversification claims.
- A second funded name sharing a normalized dominant driver requires a cluster note.
- Decision persistence reconciles the current weight in the frozen Stage 7 bundle to prior funded history.
- STARTER decisions require an investor-policy starter cap and cannot exceed it.
- Stage 7 language firewall includes additional imperative/paraphrase tripwires while the renderer remains structured and non-directive.
- Pilot 2 replay now includes an ELIGIBLE happy path followed by a human HOLD CASH decision, proving eligibility does not force deployment.

## Verification

Run:

```bash
python -m pytest -q
python -m pytest --cov=stock_atlas --cov-report=term-missing -q
python -m compileall -q stock_atlas tests
```

Current local result after Code Red Team remediation:

- **106/106 tests passing**
- **89% line coverage**
- compileall PASS

Coverage percentage declined slightly from the pre-Red-Team freeze because the remediation added persistence and validation branches. The newly reported failure paths themselves have explicit regression tests.

## Remaining Critical integration blocker

This working environment does not contain the legacy `stock-atlas-sprint1-live` repository. Prior audit material shows that older stack had an import-blocking enum mismatch and ambiguous live harnesses, but its source files are not available here for a real merge.

Before any controlled live pilot:

1. obtain the actual legacy repository/source tree;
2. establish a reproducible green baseline;
3. merge this v0.2 control layer;
4. retire or hard-fence any ranking/recommendation/decision writer that bypasses `run_stage7_pipeline` + `DecisionStore.append`;
5. perform one integrated replay using the production security resolver, price/session timestamps, FX, Treasury reference, period granularity, portfolio snapshot, and final persistence facade;
6. prove a legacy-style direct INITIATE is rejected;
7. rerun the full merged test suite and Code Red Team closure.

Until that happens: **NO REAL PORTFOLIO ACTION AUTHORIZED.**
