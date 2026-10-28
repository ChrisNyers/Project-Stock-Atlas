"""Integration tests for the single authorized capital-decision path.

These tests exist to close the integration half of Red Team finding C-03:
the control layer is only a control if nothing in the merged repository can
write a funded capital decision around it.

They assert three families of property:

1. The legacy data/ingestion layer has no capital-decision surface at all.
2. The facade is the only sanctioned path, and it cannot be handed a claimed
   or hand-built Stage 7 result.
3. Funding actions (INITIATE/ADD) are impossible unless a genuine, retained,
   hash-matching ELIGIBLE Stage 7 bundle backs them — while HOLD CASH and
   DO NOTHING remain legal after any Stage 7 outcome.

Capital status: NO REAL PORTFOLIO ACTION. Every value here is a fixture.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from capital_decision_facade import (
    FundedFreshnessEvidence,
    CapitalDecisionFacade,
    ControlFailure,
    assert_no_legacy_capital_writer,
)
from stock_atlas.freeze import freeze_payload
from stock_atlas.models import (
    AlternativeType,
    BlockFlag,
    CandidateUnderwriting,
    CapacityStatus,
    ComparisonAlternative,
    DecisionRecord,
    ETFOverlap,
    FreshnessStatus,
    FundingMode,
    FundingPocket,
    Holding,
    InputVersions,
    MarketReferenceSnapshot,
    OverlapStatus,
    PortfolioAction,
    PortfolioSnapshot,
    PositionClassification,
    PriceMode,
    PriceSnapshot,
    ReturnBand,
    ReviewEventType,
    RevisitTriggers,
    SecurityDecision,
    TypedUncertainty,
    UnderwritingGateStatus,
    VerificationStatus,
)
from stock_atlas.pipeline import Stage7Run
from stock_atlas.portfolio import build_position_proposal

NOW = datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc)
SESSION = date(2026, 9, 2)  # the XNYS session that closed (20:00Z) before NOW; keeps the fixture calendar-consistent


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


def _price(key: str, ticker: str, value: float) -> PriceSnapshot:
    return PriceSnapshot(
        security_key=key,
        ticker=ticker,
        price=value,
        price_as_of=datetime(2026, 9, 2, 20, 0, tzinfo=timezone.utc),
        price_session_date=SESSION,
        latest_completed_session_date=SESSION,
        currency="USD",
        provider="INTEGRATION_FIXTURE",
        market_session_status="CLOSED",
        adjusted=False,
        freshness_status=FreshnessStatus.FRESH,
        price_mode=PriceMode.COMPLETED_SESSION,
        quoted_security_key=key,
        quoted_instrument=f"{ticker} (XNYS)",
    )


def _underwriting(key: str, ticker: str, *, rb: ReturnBand | None, drivers=("enterprise IT",)):
    return CandidateUnderwriting(
        security_key=key,
        ticker=ticker,
        security_decision=SecurityDecision.BUY,
        price_snapshot=_price(key, ticker, 100.0),
        observable_regime="observable market regime",
        observable_regime_evidence=("integration fixture",),
        atlas_variant="competing operating story",
        variant_evidence=("integration operating evidence",),
        return_band=rb,
        return_band_basis=("coarse scenario basis",) if rb else (),
        required_return_band=ReturnBand(0.10, 0.11) if rb else None,
        underwriting_gate_status=(
            UnderwritingGateStatus.CLEAR if rb else UnderwritingGateStatus.UNVERIFIED
        ),
        uncertainties=(TypedUncertainty("integration", "fixture uncertainty", BlockFlag.NO),),
        dominant_drivers=drivers,
        revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
        underwriting_provenance=("integration facade test",),
    )


def funded_evidence(key: str = "SEC:ELIG", ticker: str = "ELIG", price: float = 100.0, now=None):
    """What a funded Stage 8 must now supply: a fresh bind and Treasury re-attestation that match the frozen Stage 7 evidence."""
    return FundedFreshnessEvidence(
        fresh_price=_price(key, ticker, price),
        treasury_reattested=MarketReferenceSnapshot("UST-13W", 0.039, now or NOW, "INTEGRATION_FIXTURE", FreshnessStatus.FRESH, "USD"),
    )


def _portfolio(snapshot_id: str = "INTEGRATION") -> PortfolioSnapshot:
    return PortfolioSnapshot(
        snapshot_id=snapshot_id,
        as_of=NOW,
        total_value=1_000_000,
        holdings=(Holding("SEC:MSFT", "MSFT", 120_000, 0.12, "taxable", "taxable"),),
        funding_pocket=FundingPocket(
            account="cash",
            account_type="taxable",
            amount=50_000,
            t_plus_1_deployable=True,
            constraints_supplied=True,
            tax_status=VerificationStatus.VERIFIED,
            liquidity_status=VerificationStatus.VERIFIED,
            execution_status=VerificationStatus.VERIFIED,
        ),
        trims_permitted=False,
        add_only_policy=True,
    )


def _alternatives(candidate_key: str = "SEC:ELIG"):
    return (
        ComparisonAlternative(
            AlternativeType.BETA,
            "SPY",
            ReturnBand(0.07, 0.10),
            security_key="ETF:SPY",
            overlap=ETFOverlap("SPY", candidate_key, OverlapStatus.UNMEASURED),
            notes=("coarse SPY range",),
        ),
        ComparisonAlternative(
            AlternativeType.TREASURY_CASH,
            "Treasury/Cash",
            ReturnBand(0.035, 0.045),
            market_reference=MarketReferenceSnapshot(
                "UST-13W", 0.039, NOW, "INTEGRATION_FIXTURE", FreshnessStatus.FRESH, "USD"
            ),
            duration_match_status=VerificationStatus.VERIFIED,
            notes=("duration/reinvestment normalized",),
        ),
        ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing"),
    )


def _position(portfolio: PortfolioSnapshot, current_weight: float = 0.0):
    return build_position_proposal(
        portfolio,
        current_weight=current_weight,
        increment_dollars=50_000,
        classification=PositionClassification.STARTER,
        capacity_status=CapacityStatus.AVAILABLE,
        remaining_capacity=0.10,
        funding_source="cash",
        funding_mode=FundingMode.INTERNAL_CASH,
    )


def _facade(tmp_path: Path) -> CapitalDecisionFacade:
    return CapitalDecisionFacade(
        ledger_path=tmp_path / "decisions.jsonl",
        artifact_dir=tmp_path / "artifacts",
    )


def _input_versions(tmp_path: Path) -> InputVersions:
    return InputVersions(
        freeze_payload({"portfolio": "INTEGRATION"}, version="p", destination=tmp_path / "portfolio.json"),
        freeze_payload({"scenario": "v1"}, version="s", destination=tmp_path / "scenario.json"),
        freeze_payload({"exposure": "v1"}, version="e", destination=tmp_path / "exposure.json"),
        freeze_payload({"evidence": "v1"}, version="ev", destination=tmp_path / "evidence.json"),
        freeze_payload({"contract": "v0.2"}, version="c", destination=tmp_path / "contract.json"),
    )


def _eligible_run(facade: CapitalDecisionFacade, *, name="stage7-elig", key="SEC:ELIG"):
    portfolio = _portfolio()
    run = facade.run_stage7(
        _underwriting(key, "ELIG", rb=ReturnBand(0.13, 0.17)),
        portfolio,
        _position(portfolio),
        _alternatives(key),
        NOW,
        artifact_name=name,
    )
    assert run.result.status == "ELIGIBLE FOR STAGE 8"
    return run


# ---------------------------------------------------------------------------
# 1. the legacy data/ingestion layer has no capital-decision surface
# ---------------------------------------------------------------------------


def test_legacy_ingestion_layer_exposes_no_capital_decision_surface():
    """The data domain must not be able to create or persist a capital action."""
    assert_no_legacy_capital_writer()


def test_legacy_models_module_is_not_the_control_layer_model():
    """Namespace separation: legacy `models` != `stock_atlas.models`."""
    import models as legacy_models
    import stock_atlas.models as control_models

    assert legacy_models is not control_models
    assert Path(legacy_models.__file__) != Path(control_models.__file__)
    # The legacy domain model has no notion of a portfolio action.
    assert not hasattr(legacy_models, "PortfolioAction")
    assert not hasattr(legacy_models, "DecisionRecord")
    # The control layer does, and it is reached only via stock_atlas.
    assert hasattr(control_models, "PortfolioAction")
    assert hasattr(control_models, "DecisionRecord")


def test_legacy_security_identity_status_is_untouched_by_merge():
    """The merge must not have altered the legacy ingestion enum."""
    import models as legacy_models

    assert legacy_models.SecurityIdentityStatus.UNVERIFIED.value == "UNVERIFIED"
    assert legacy_models.SecurityIdentityStatus.VERIFIED.value == "VERIFIED"


# ---------------------------------------------------------------------------
# 2. the facade cannot be handed a claimed Stage 7 result
# ---------------------------------------------------------------------------


def test_facade_rejects_non_stage7run_object(tmp_path):
    facade = _facade(tmp_path)
    for bogus in (None, {}, {"status": "ELIGIBLE FOR STAGE 8"}, "ELIGIBLE FOR STAGE 8", 42):
        with pytest.raises(ControlFailure, match="requires a Stage7Run"):
            facade.record_final_decision(
                bogus,
                record_id="BOGUS",
                human_stage8_action="INITIATE",
                human_rationale="attempted bypass",
                alternatives_considered=("SPY", "Treasury/Cash", "Do Nothing"),
                input_versions=_input_versions(tmp_path),
                created_at=NOW,
                portfolio_snapshot_id="INTEGRATION",
            )


def test_facade_always_retains_the_stage7_artifact(tmp_path):
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    assert run.artifact_ref.artifact_path
    assert Path(run.artifact_ref.artifact_path).exists()
    assert Path(run.artifact_ref.artifact_path).parent == facade.artifact_dir


def test_facade_requires_an_artifact_name(tmp_path):
    facade = _facade(tmp_path)
    portfolio = _portfolio()
    with pytest.raises(ControlFailure, match="artifact_name"):
        facade.run_stage7(
            _underwriting("SEC:ELIG", "ELIG", rb=ReturnBand(0.13, 0.17)),
            portfolio,
            _position(portfolio),
            _alternatives(),
            NOW,
            artifact_name="   ",
        )


def test_facade_stage7_emits_no_portfolio_action(tmp_path):
    """Stage 7 compares; it never produces a capital action."""
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    assert not hasattr(run.result, "portfolio_action")
    assert "NO PORTFOLIO ACTION" in run.result.comparison_header
    assert "STAGE 8" in run.rendered_text


# ---------------------------------------------------------------------------
# 3. funding requires a genuine ELIGIBLE bundle; refusal stays legal
# ---------------------------------------------------------------------------


def test_initiate_blocked_when_stage7_did_not_reach_eligible(tmp_path):
    """A WATCH/BLOCKED comparison cannot be funded through the facade."""
    facade = _facade(tmp_path)
    portfolio = _portfolio()
    run = facade.run_stage7(
        _underwriting("SEC:WATCH", "WATCH", rb=None),  # missing band -> not eligible
        portfolio,
        _position(portfolio),
        _alternatives("SEC:WATCH"),
        NOW,
        artifact_name="stage7-watch",
    )
    assert run.result.status != "ELIGIBLE FOR STAGE 8"
    with pytest.raises(ControlFailure, match="requires Stage 7 status"):
        facade.record_final_decision(
            run,
            record_id="BAD-INITIATE",
            human_stage8_action="INITIATE",
            human_rationale="attempted funding after a non-eligible comparison",
            alternatives_considered=("WATCH", "SPY", "Treasury/Cash", "Do Nothing"),
            input_versions=_input_versions(tmp_path),
            created_at=NOW,
            portfolio_snapshot_id=portfolio.snapshot_id,
            dominant_drivers=("enterprise IT",),
            revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
            starter_cap_weight=0.05,
        )
    assert not (tmp_path / "decisions.jsonl").exists() or facade.verify_ledger()


def test_hold_cash_remains_legal_after_an_eligible_stage7(tmp_path):
    """Eligibility never forces deployment."""
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    record = facade.record_final_decision(
        run,
        record_id="HOLD-CASH-1",
        human_stage8_action="HOLD CASH",
        human_rationale="Human declined to deploy despite an eligible comparison.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
    )
    assert record.human_stage8_action == PortfolioAction.HOLD_CASH
    assert facade.verify_ledger()


def test_do_nothing_remains_a_distinct_legal_decision(tmp_path):
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    record = facade.record_final_decision(
        run,
        record_id="DO-NOTHING-1",
        human_stage8_action="DO NOTHING",
        human_rationale="No new active mandate for this unit.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
    )
    assert record.human_stage8_action == PortfolioAction.DO_NOTHING
    assert record.human_stage8_action != PortfolioAction.HOLD_CASH


def test_initiate_succeeds_only_through_the_facade_with_a_real_bundle(tmp_path):
    """The legal happy path: genuine ELIGIBLE bundle -> funded record."""
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    record = facade.record_final_decision(
        run,
        record_id="INITIATE-1",
        human_stage8_action="INITIATE",
        human_rationale="Human accepted the comparison and funded a starter increment.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
        dominant_drivers=("enterprise IT",),
        revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
        starter_cap_weight=0.10,
        funded_freshness=funded_evidence(),
    )
    assert record.human_stage8_action == PortfolioAction.INITIATE
    assert record.stage7_status == "ELIGIBLE FOR STAGE 8"
    assert record.stage7_artifact is not None
    assert facade.verify_ledger()


def test_stage7_facts_are_taken_from_the_frozen_run_not_the_caller(tmp_path):
    """A caller cannot assert a status or key the comparison did not produce."""
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    record = facade.record_final_decision(
        run,
        record_id="PROVENANCE-1",
        human_stage8_action="HOLD CASH",
        human_rationale="Checking that ledger facts come from the frozen bundle.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
    )
    assert record.stage7_status == run.result.status
    assert record.candidate_security_key == run.result.security_key
    assert record.stage7_reasons == tuple(run.result.reasons)
    assert record.constraint_state == run.result.constraint_state


def test_deleting_the_frozen_stage7_artifact_blocks_the_append(tmp_path):
    """M-06 at the integration boundary: hashes without artifacts are refused."""
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    Path(run.artifact_ref.artifact_path).unlink()
    with pytest.raises(ControlFailure):
        facade.record_final_decision(
            run,
            record_id="MISSING-ARTIFACT",
            human_stage8_action="INITIATE",
            human_rationale="artifact deleted before append",
            alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
            input_versions=_input_versions(tmp_path),
            created_at=NOW,
            portfolio_snapshot_id="INTEGRATION",
            dominant_drivers=("enterprise IT",),
            revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
            starter_cap_weight=0.10,
        )


def test_legacy_style_direct_record_cannot_forge_an_initiate(tmp_path):
    """C-03 regression: a legacy-shaped direct append is rejected at persistence.

    This simulates a would-be legacy writer that constructs a DecisionRecord
    itself and claims Stage 7 passed. The store must refuse it because no
    retained hash-matching ELIGIBLE bundle backs the claim.
    """
    facade = _facade(tmp_path)
    forged = DecisionRecord(
        record_id="LEGACY-FORGED",
        created_at=NOW,
        review_event_type=ReviewEventType.FINAL_CAPITAL_DECISION,
        candidate_security_key="SEC:ELIG",
        portfolio_snapshot_id="INTEGRATION",
        input_versions=_input_versions(tmp_path),
        stage7_status="ELIGIBLE FOR STAGE 8",
        stage7_reasons=("claimed eligible",),
        human_stage8_action=PortfolioAction.INITIATE,
        human_rationale="legacy-style direct write",
        revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        stage7_artifact=None,  # no retained bundle
        constraint_state=VerificationStatus.VERIFIED,
        dominant_drivers=("enterprise IT",),
        position_classification=PositionClassification.STARTER,
        post_trade_weight=0.05,
        starter_cap_weight=0.10,
    )
    with pytest.raises(ControlFailure):
        facade.store.append(forged)


def test_tampering_with_ledger_history_blocks_the_next_append(tmp_path):
    """Gate F: integrity is verified before any new append."""
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    facade.record_final_decision(
        run,
        record_id="HOLD-CASH-BASE",
        human_stage8_action="HOLD CASH",
        human_rationale="baseline record",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
    )
    ledger = tmp_path / "decisions.jsonl"
    ledger.write_text(ledger.read_text(encoding="utf-8").replace("baseline record", "tampered"), encoding="utf-8")
    assert facade.verify_ledger() is False
    run2 = _eligible_run(facade, name="stage7-elig-2")
    with pytest.raises(ControlFailure, match="integrity"):
        facade.record_final_decision(
            run2,
            record_id="AFTER-TAMPER",
            human_stage8_action="HOLD CASH",
            human_rationale="append after tamper",
            alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
            input_versions=_input_versions(tmp_path),
            created_at=NOW,
            portfolio_snapshot_id="INTEGRATION",
        )


def test_ledger_is_append_only_through_the_facade(tmp_path):
    facade = _facade(tmp_path)
    with pytest.raises(ControlFailure, match="append-only"):
        facade.store.overwrite()
