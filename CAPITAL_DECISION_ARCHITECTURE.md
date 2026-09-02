# Stock Atlas — Capital-Decision Architecture

**Status:** merged control layer v0.2 · **Capital status: NO REAL PORTFOLIO ACTION**

This note documents the **single authorized capital-decision path** in the
merged repository, and the namespace separation that keeps the data domain and
the capital-decision domain apart.

---

## Two domains, deliberately separate namespaces

| | Data / ingestion domain | Capital-decision control layer |
|---|---|---|
| **Location** | repository top level | `stock_atlas/` package |
| **Modules** | `models.py`, `database.py`, `formulas.py`, `entity_classification.py`, `identity_resolver.py`, `point_in_time.py`, `sec_adapter.py`, `xbrl_parser.py`, `market_data_providers.py`, `market_macro_adapters.py`, `freeze_and_registry.py` | `controls.py`, `decision_store.py`, `freeze.py`, `models.py`, `pipeline.py`, `portfolio.py`, `presentation.py` |
| **Domain model** | `models.SecurityIdentityStatus`, `FinancialState`, `MarketState`, … | `stock_atlas.models.DecisionRecord`, `PortfolioAction`, `Stage7CandidateResult`, … |
| **Produces** | evidence | capital decisions |
| **May create a `PortfolioAction`?** | **No — never** | Only via the facade at Stage 8 |

`models.py` and `stock_atlas/models.py` are **different models with the same
filename** and are never merged. The package boundary keeps them distinct.
`tests/test_integration_facade.py::test_legacy_models_module_is_not_the_control_layer_model`
asserts this and fails if the separation is ever collapsed.

---

## The single authorized path

```
        legacy ingestion / evidence  (SEC, XBRL, prices, identity)
                          |
                          |  evidence only — no capital surface
                          v
        ┌─────────────────────────────────────────────────────┐
        │  capital_decision_facade.CapitalDecisionFacade      │
        └─────────────────────────────────────────────────────┘
                          |
              (1) run_stage7(...)  ──►  stock_atlas.run_stage7_pipeline
                          |                 · comparison only
                          |                 · emits NO PortfolioAction
                          |                 · language firewall applied
                          |                 · bundle hashed AND retained
                          v
                    Stage7Run  { result, rendered_text, artifact_ref }
                          |
              (2) record_final_decision(stage7_run, ...)
                          |
                          v
                 stock_atlas.DecisionStore.append
                          · re-verifies retained artifacts (M-06)
                          · binds INITIATE/ADD to ELIGIBLE bundle (C-01)
                          · requires VERIFIED constraints (M-01)
                          · driver-cluster check vs open funded history (M-03)
                          · STARTER cap vs ledger history (M-04)
                          · append-only hash chain, integrity before append
                          v
                    decisions.jsonl  (append-only ledger)
```

### Stage 7 writes. Stage 8 spends.

Stage 7 produces a comparison and nothing else. Only
`record_final_decision` — a human Stage 8 act — can place a capital decision in
the ledger.

---

## Fencing guarantees

1. **Artifacts are always retained.** `run_stage7` requires an `artifact_name`
   and always writes the frozen bundle to `artifact_dir`. A comparison that
   could not back a later record cannot be produced.
2. **A claimed Stage 7 is not accepted.** `record_final_decision` takes only a
   `Stage7Run` instance. Dicts, stubs, strings and hand-built results are
   rejected with `ControlFailure`.
3. **Stage 7 facts come from the frozen run, not the caller.** `stage7_status`,
   `stage7_reasons`, `candidate_security_key`, `constraint_state`,
   `position_classification` and `post_trade_weight` are read off the run. A
   caller cannot assert a status the comparison did not produce.
4. **Funding is bound to eligibility.** `INITIATE`/`ADD` require frozen status
   exactly `ELIGIBLE FOR STAGE 8`, checked at the facade and again independently
   inside `DecisionStore.append`.
5. **Refusal stays legal.** `HOLD CASH` and `DO NOTHING` remain valid after any
   Stage 7 outcome, including ELIGIBLE. Eligibility never forces deployment.
6. **The data domain has no capital surface.**
   `assert_no_legacy_capital_writer()` walks every legacy module and raises if
   any of them ever exposes `DecisionStore`, `DecisionRecord`, `PortfolioAction`
   or `run_stage7_pipeline`. It runs as a test.

---

## Why no retirement work was required

The Red Team's C-03 anticipated legacy ranking/recommendation writers that would
need retiring. **No such writer exists in this repository.** The only
`recommend*` symbols in the legacy tree are:

- `models.DataQualityAssessment.recommendations` — data-quality notes
- `models.ResearchEvent.recommended_action` — research triage
- `database.py` columns backing those two fields
- `benchmark_4a5_2*.recommended_stack()` — provider-selection benchmark output

None is a capital-decision writer; none can produce a `PortfolioAction`. The
facade is therefore the **first and only** capital-decision path, not a
replacement for an incumbent one. The guarantee is maintained forward by
`assert_no_legacy_capital_writer()` rather than by deleting anything.

---

## What this architecture does not do

- No ranking, scoring, or master score.
- No optimizer.
- No automatic Stage 8 decision.
- No trade execution or broker connectivity.
- No tax engine.
- No second market-data vendor.
- No driver NLP or factor model.
- No ETF look-through ingestion.

**Capital status: NO REAL PORTFOLIO ACTION.**
