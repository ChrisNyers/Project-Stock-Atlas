from datetime import date, datetime, timedelta, timezone

from stock_atlas.controls import evaluate_stage7_candidate
from stock_atlas.models import *
from stock_atlas.portfolio import build_position_proposal

NOW = datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc)
SESSION = date(2026, 9, 1)


def px(key, ticker, value):
    return PriceSnapshot(
        security_key=key,
        ticker=ticker,
        price=value,
        price_as_of=datetime(2026, 9, 1, 20, 0, tzinfo=timezone.utc),
        price_session_date=SESSION,
        latest_completed_session_date=SESSION,
        currency="USD",
        provider="PILOT2_REPLAY",
        market_session_status="CLOSED",
        adjusted=False,
        freshness_status=FreshnessStatus.FRESH,
        price_mode=PriceMode.COMPLETED_SESSION,
        quoted_security_key=key,
    )


def u(key, ticker, value, *, rb, block=False, drivers=("equity beta",), decision=SecurityDecision.BUY):
    return CandidateUnderwriting(
        security_key=key,
        ticker=ticker,
        security_decision=decision,
        price_snapshot=px(key, ticker, value),
        observable_regime="preserved observable market regime",
        observable_regime_evidence=("Pilot 2 preserved artifact",),
        atlas_variant="preserved competing operating story",
        variant_evidence=("Pilot 2 preserved operating evidence",),
        return_band=rb,
        return_band_basis=("preserved coarse scenario basis" if rb else "",) if rb else (),
        required_return_band=ReturnBand(0.10, 0.11) if rb else None,
        underwriting_gate_status=UnderwritingGateStatus.CLEAR if rb else UnderwritingGateStatus.UNVERIFIED,
        uncertainties=(TypedUncertainty("pilot2", "preserved uncertainty", BlockFlag.YES if block else BlockFlag.NO),),
        dominant_drivers=drivers,
        revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
        underwriting_provenance=("Pilot 2 control replay",),
    )


def test_patched_pilot2_replay_preserves_differentiation_and_no_forced_deployment():
    portfolio = PortfolioSnapshot(
        snapshot_id="PILOT2",
        as_of=NOW,
        total_value=1_000_000,
        holdings=(
            Holding("SEC:MSFT", "MSFT", 120_000, 0.12, "taxable", "taxable"),
            Holding("SEC:LLY", "LLY", 80_000, 0.08, "taxable", "taxable"),
            Holding("SEC:BRK.B", "BRK.B", 100_000, 0.10, "taxable", "taxable"),
            Holding("ETF:VNQ", "VNQ", 120_000, 0.12, "taxable", "taxable"),
            Holding("ETF:SPY", "SPY", 280_000, 0.28, "taxable", "taxable"),
        ),
        funding_pocket=FundingPocket(
            account="synthetic external cash",
            account_type="taxable",
            amount=50_000,
            t_plus_1_deployable=True,
            constraints_supplied=True,
            tax_status=VerificationStatus.VERIFIED,
            liquidity_status=VerificationStatus.VERIFIED,
            execution_status=VerificationStatus.VERIFIED,
        ),
        trims_permitted=True,
    )

    alternatives = (
        ComparisonAlternative(
            AlternativeType.BETA, "SPY", ReturnBand(0.07, 0.11), security_key="ETF:SPY",
            overlap=ETFOverlap("SPY", "MIXED", OverlapStatus.UNMEASURED),
            notes=("preserved coarse SPY comparison basis",),
        ),
        ComparisonAlternative(
            AlternativeType.TREASURY_CASH, "Treasury/Cash", ReturnBand(0.035, 0.045),
            market_reference=MarketReferenceSnapshot("UST-13W", 0.039, NOW, "PILOT2_REPLAY", FreshnessStatus.FRESH, "USD"),
            duration_match_status=VerificationStatus.VERIFIED,
            notes=("paper annualized/reinvestment normalization to comparison horizon",),
        ),
        ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing"),
        ComparisonAlternative(AlternativeType.RECYCLE, "Recycle from current holding; friction must be verified separately"),
    )

    def pos(capacity=CapacityStatus.AVAILABLE):
        return build_position_proposal(
            portfolio,
            current_weight=0,
            increment_dollars=50_000,
            classification=PositionClassification.STARTER,
            capacity_status=capacity,
            remaining_capacity=0.10,
            funding_source="external cash",
            funding_mode=FundingMode.EXTERNAL_NEW_CAPITAL,
        )

    acn = u("SEC:ACN", "ACN", 188.09, rb=None, drivers=("enterprise IT", "AI transformation", "global cycle"))
    rmd = u("SEC:RMD", "RMD", 231.36, rb=None, drivers=("sleep apnea utilization", "GLP-1", "device competition"))
    trow = u("SEC:TROW", "TROW", 108.98, rb=ReturnBand(0.10, 0.14), block=True, drivers=("active AUM flows", "market levels", "fee compression"))
    vici = u("SEC:VICI", "VICI", 25.54, rb=ReturnBand(0.10, 0.14), drivers=("rates", "REIT", "tenant concentration"))
    orcl = u("SEC:ORCL", "ORCL", 141.32, rb=ReturnBand(0.12, 0.17), block=True, drivers=("AI infrastructure", "capex", "financing"))

    assert evaluate_stage7_candidate(acn, portfolio, pos(), alternatives, NOW).status == "WATCH / NO DECISION"
    assert evaluate_stage7_candidate(rmd, portfolio, pos(), alternatives, NOW).status == "WATCH / NO DECISION"
    assert evaluate_stage7_candidate(trow, portfolio, pos(), alternatives, NOW).status == "BLOCKED"
    assert evaluate_stage7_candidate(vici, portfolio, pos(CapacityStatus.CONSTRAINED), alternatives, NOW).status == "BLOCKED"
    assert evaluate_stage7_candidate(orcl, portfolio, pos(), alternatives, NOW).status == "BLOCKED"

    # No candidate is converted into a PortfolioAction by Stage 7.
    for candidate in (acn, rmd, trow, vici, orcl):
        result = evaluate_stage7_candidate(candidate, portfolio, pos(), alternatives, NOW)
        assert not hasattr(result, "portfolio_action")


def test_pilot2_happy_path_reaches_eligible_then_human_can_hold_cash_with_frozen_record(tmp_path):
    from stock_atlas.decision_store import DecisionStore
    from stock_atlas.freeze import freeze_payload
    from stock_atlas.pipeline import run_stage7_pipeline

    portfolio = PortfolioSnapshot(
        snapshot_id="PILOT2-HAPPY",
        as_of=NOW,
        total_value=1_000_000,
        holdings=(Holding("SEC:MSFT", "MSFT", 120_000, 0.12, "taxable", "taxable"),),
        funding_pocket=FundingPocket(
            account="cash", account_type="taxable", amount=50_000, t_plus_1_deployable=True,
            constraints_supplied=True, tax_status=VerificationStatus.VERIFIED,
            liquidity_status=VerificationStatus.VERIFIED, execution_status=VerificationStatus.VERIFIED,
        ),
        trims_permitted=False,
        add_only_policy=True,
    )
    candidate = u(
        "SEC:ELIG", "ELIG", 100.0,
        rb=ReturnBand(0.13, 0.17),
        block=False,
        drivers=("enterprise IT", "business cycle"),
    )
    alternatives = (
        ComparisonAlternative(
            AlternativeType.BETA, "SPY", ReturnBand(0.07, 0.10), security_key="ETF:SPY",
            overlap=ETFOverlap("SPY", "SEC:ELIG", OverlapStatus.UNMEASURED),
            notes=("coarse SPY range",),
        ),
        ComparisonAlternative(
            AlternativeType.TREASURY_CASH, "Treasury/Cash", ReturnBand(0.035, 0.045),
            market_reference=MarketReferenceSnapshot("UST-13W", 0.039, NOW, "PILOT2_REPLAY", FreshnessStatus.FRESH, "USD"),
            duration_match_status=VerificationStatus.VERIFIED,
            notes=("duration/reinvestment normalized",),
        ),
        ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing"),
    )
    pos = build_position_proposal(
        portfolio, current_weight=0.0, increment_dollars=50_000,
        classification=PositionClassification.STARTER, capacity_status=CapacityStatus.AVAILABLE,
        remaining_capacity=0.10, funding_source="cash", funding_mode=FundingMode.INTERNAL_CASH,
    )
    run = run_stage7_pipeline(
        candidate, portfolio, pos, alternatives, NOW,
        artifact_destination=tmp_path / "stage7.json",
    )
    assert run.result.status == "ELIGIBLE FOR STAGE 8"
    assert run.result.constraint_state == VerificationStatus.VERIFIED

    refs = InputVersions(
        freeze_payload({"portfolio": "PILOT2-HAPPY"}, version="p", destination=tmp_path / "portfolio.json"),
        freeze_payload({"scenario": "v1"}, version="s", destination=tmp_path / "scenario.json"),
        freeze_payload({"exposure": "v1"}, version="e", destination=tmp_path / "exposure.json"),
        freeze_payload({"evidence": "v1"}, version="ev", destination=tmp_path / "evidence.json"),
        freeze_payload({"contract": "v0.2"}, version="c", destination=tmp_path / "contract.json"),
    )
    record = DecisionRecord(
        record_id="P2-HOLD-CASH",
        created_at=NOW,
        review_event_type=ReviewEventType.FINAL_CAPITAL_DECISION,
        candidate_security_key="SEC:ELIG",
        portfolio_snapshot_id=portfolio.snapshot_id,
        input_versions=refs,
        stage7_status=run.result.status,
        stage7_reasons=run.result.reasons,
        human_stage8_action=PortfolioAction.HOLD_CASH,
        human_rationale="Human declined to deploy despite an eligible comparison.",
        revisit_triggers=candidate.revisit_triggers,
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        stage7_artifact=run.artifact_ref,
        constraint_state=run.result.constraint_state,
    )
    DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_pilot2_eligible_cannot_be_initiated_without_retained_stage7_artifact(tmp_path):
    from stock_atlas.decision_store import DecisionStore
    from stock_atlas.freeze import freeze_payload
    import pytest
    from dataclasses import replace
    from stock_atlas.controls import ControlFailure

    refs = InputVersions(
        freeze_payload({"portfolio": "P"}, version="p", destination=tmp_path / "p.json"),
        freeze_payload({"scenario": "S"}, version="s", destination=tmp_path / "s.json"),
        freeze_payload({"exposure": "E"}, version="e", destination=tmp_path / "e.json"),
        freeze_payload({"evidence": "EV"}, version="ev", destination=tmp_path / "ev.json"),
        freeze_payload({"contract": "C"}, version="c", destination=tmp_path / "c.json"),
    )
    record = DecisionRecord(
        record_id="P2-BAD-INIT",
        created_at=NOW,
        review_event_type=ReviewEventType.FINAL_CAPITAL_DECISION,
        candidate_security_key="SEC:ELIG",
        portfolio_snapshot_id="P",
        input_versions=refs,
        stage7_status="ELIGIBLE FOR STAGE 8",
        stage7_reasons=("claimed eligible",),
        human_stage8_action=PortfolioAction.INITIATE,
        human_rationale="attempted bypass",
        revisit_triggers=RevisitTriggers("±25%", NOW + timedelta(days=90)),
        alternatives_considered=("ELIG", "SPY", "Treasury", "Do Nothing"),
        stage7_artifact=None,
        constraint_state=VerificationStatus.VERIFIED,
        dominant_drivers=("enterprise IT",),
        position_classification=PositionClassification.STARTER,
        post_trade_weight=0.02,
        starter_cap_weight=0.03,
    )
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "bad.jsonl").append(record)
