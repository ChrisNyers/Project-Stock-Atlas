from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import json
import pytest

from stock_atlas.controls import (
    ControlFailure,
    evaluate_stage7_candidate,
    range_clearly_better,
    ranges_distinguishable,
    translate_weight_to_dollars,
    validate_common_driver_cluster,
    validate_etf_overlap,
    validate_funding_pocket,
    validate_period_granularity,
    validate_price_snapshot,
    validate_required_alternatives,
    validate_stage7_language,
)
from stock_atlas.decision_store import DecisionStore
from stock_atlas.models import *
from stock_atlas.portfolio import (
    ETFConstituentExposure,
    build_position_proposal,
    capacity_curve_dollars,
    driver_exposure_from_components,
    effective_name_exposure,
)

NOW = datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc)
SESSION = date(2026, 9, 1)


def price(key="SEC:ACN", ticker="ACN", *, stale=False, quoted_key="SAME", session=SESSION, latest=SESSION, mode=PriceMode.COMPLETED_SESSION, as_of=None):
    return PriceSnapshot(
        security_key=key,
        ticker=ticker,
        price=188.09,
        price_as_of=as_of or (NOW - timedelta(hours=20)),
        price_session_date=session,
        latest_completed_session_date=latest,
        currency="USD",
        provider="TEST",
        market_session_status="CLOSED" if mode == PriceMode.COMPLETED_SESSION else "OPEN",
        adjusted=False,
        freshness_status=FreshnessStatus.STALE if stale else FreshnessStatus.FRESH,
        price_mode=mode,
        quoted_security_key=key if quoted_key == "SAME" else quoted_key,
    )


def underwriting(
    key="SEC:ACN",
    ticker="ACN",
    *,
    rb=ReturnBand(0.11, 0.14),
    p=None,
    decision=SecurityDecision.BUY,
    block=False,
    provenance=("SEC filing",),
    drivers=("enterprise IT", "AI transformation"),
    required_rb=ReturnBand(0.10, 0.11),
    gate=UnderwritingGateStatus.CLEAR,
):
    return CandidateUnderwriting(
        security_key=key,
        ticker=ticker,
        security_decision=decision,
        price_snapshot=p or price(key, ticker),
        observable_regime="observable low-growth / disruption regime",
        observable_regime_evidence=("price/multiple regime evidence",),
        atlas_variant="operating story can prove more durable than tape implies",
        variant_evidence=("bookings / operating evidence",),
        return_band=rb,
        return_band_basis=("coarse scenario assumptions",),
        required_return_band=required_rb,
        underwriting_gate_status=gate,
        uncertainties=(TypedUncertainty("demand", "cyclical demand uncertainty", BlockFlag.YES if block else BlockFlag.NO),),
        dominant_drivers=drivers,
        revisit_triggers=RevisitTriggers("±25% price move", NOW + timedelta(days=90), "material thesis evidence"),
        underwriting_provenance=provenance,
    )


def portfolio(*, constraints=True, statuses=VerificationStatus.VERIFIED, trims=True, add_only=False, amount=100_000, total=1_000_000):
    return PortfolioSnapshot(
        snapshot_id="P1",
        as_of=NOW,
        total_value=total,
        holdings=(Holding("SEC:MSFT", "MSFT", total * 0.12, 0.12, "taxable", "taxable", total * 0.08, dominant_drivers=("AI transformation",)),),
        funding_pocket=FundingPocket(
            account="cash",
            account_type="taxable",
            amount=amount,
            t_plus_1_deployable=True,
            constraints_supplied=constraints,
            tax_status=statuses,
            liquidity_status=statuses,
            execution_status=statuses,
        ),
        trims_permitted=trims,
        add_only_policy=add_only,
    )


def position(p=None, dollars=50_000, capacity=CapacityStatus.AVAILABLE, remaining=0.08, mode=FundingMode.INTERNAL_CASH):
    p = p or portfolio()
    return build_position_proposal(
        p,
        current_weight=0.0,
        increment_dollars=dollars,
        classification=PositionClassification.STARTER,
        capacity_status=capacity,
        remaining_capacity=remaining,
        funding_source="cash",
        funding_mode=mode,
    )


def alternatives(*, overlap=OverlapStatus.UNMEASURED, cash_rb=ReturnBand(0.035, 0.045), beta_rb=ReturnBand(0.075, 0.105), recycle=True):
    rows = [
        ComparisonAlternative(
            AlternativeType.BETA,
            "SPY",
            beta_rb,
            security_key="ETF:SPY",
            overlap=ETFOverlap("SPY", "SEC:ACN", overlap, 0.001 if overlap == OverlapStatus.MEASURED else None, "fund source" if overlap == OverlapStatus.MEASURED else None, NOW if overlap == OverlapStatus.MEASURED else None),
            notes=("coarse SPY scenario basis",),
        ),
        ComparisonAlternative(
            AlternativeType.TREASURY_CASH,
            "3m Treasury/Cash",
            cash_rb,
            market_reference=MarketReferenceSnapshot("UST-13W", 0.039, NOW - timedelta(hours=2), "TEST", FreshnessStatus.FRESH, "USD"),
            duration_match_status=VerificationStatus.VERIFIED,
            notes=("annualized/reinvestment assumption normalized to comparison horizon",),
        ),
        ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing", None),
    ]
    if recycle:
        rows.append(ComparisonAlternative(AlternativeType.RECYCLE, "Current - MSFT + candidate"))
    return tuple(rows)


# C1 ETF / constituent overlap

def test_c1_unmeasured_overlap_blocks_diversification_claim():
    with pytest.raises(ControlFailure):
        validate_etf_overlap(ETFOverlap("SPY", "SEC:ACN", OverlapStatus.UNMEASURED), True)


def test_c1_measured_overlap_requires_metadata():
    with pytest.raises(ControlFailure):
        validate_etf_overlap(ETFOverlap("SPY", "SEC:ACN", OverlapStatus.MEASURED, lookthrough_weight=0.002))


def test_c1_effective_name_exposure_adds_direct_and_lookthrough_once():
    look = [ETFConstituentExposure("ETF:SPY", "SEC:NVDA", 0.25, 0.08, "2026-09-01", "fund")]
    assert effective_name_exposure("SEC:NVDA", {"SEC:NVDA": 0.13}, look) == pytest.approx(0.15)


def test_c1_driver_decomposition_does_not_accept_full_etf_weight_argument():
    out = driver_exposure_from_components({"AI": 0.30}, {"AI": 0.05, "rates": 0.02})
    assert out == {"AI": pytest.approx(0.35), "rates": pytest.approx(0.02)}


# C2 opportunity eligibility

def test_c2_missing_return_band_fails_closed_to_watch():
    u = underwriting(rb=None)
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW)
    assert result.status == "WATCH / NO DECISION"


def test_c2_blocking_uncertainty_prevents_eligibility():
    assert evaluate_stage7_candidate(underwriting(block=True), portfolio(), position(), alternatives(), NOW).status == "BLOCKED"


def test_c2_hold_security_decision_cannot_become_new_capital_candidate():
    result = evaluate_stage7_candidate(underwriting(decision=SecurityDecision.HOLD), portfolio(), position(), alternatives(), NOW)
    assert result.status == "WATCH / NO DECISION"


def test_c2_security_buy_with_failed_required_return_gate_cannot_advance():
    result = evaluate_stage7_candidate(
        underwriting(gate=UnderwritingGateStatus.FAIL), portfolio(), position(), alternatives(), NOW
    )
    assert result.status == "WATCH / NO DECISION"


def test_c2_required_return_horizon_must_match_candidate_horizon():
    result = evaluate_stage7_candidate(
        underwriting(required_rb=ReturnBand(0.10, 0.11, horizon_years=1.0)),
        portfolio(), position(), alternatives(), NOW,
    )
    assert result.status == "WATCH / NO DECISION"


def test_c2_expired_time_trigger_forces_fresh_review():
    base = underwriting()
    from dataclasses import replace
    expired = replace(base, revisit_triggers=RevisitTriggers("±25% price move", NOW - timedelta(seconds=1)))
    result = evaluate_stage7_candidate(expired, portfolio(), position(), alternatives(), NOW)
    assert result.status == "WATCH / NO DECISION"


# C3 Stage 7 language firewall
@pytest.mark.parametrize("text", [
    "Atlas recommends ACN",
    "Preferred candidate: ACN",
    "Best idea is RMD",
    "ACN earns increment",
    "Buy ACN now",
    "Allocate $50000 to ACN",
    "Fund RMD from cash",
    "1. ACN\n2. RMD\n3. TROW",
])
def test_c3_stage7_language_leakage_blocked(text):
    with pytest.raises(ControlFailure):
        validate_stage7_language(text)


def test_c3_security_decision_and_add_only_policy_can_be_displayed_structurally():
    validate_stage7_language("Security Decision: BUY. ADD-ONLY POLICY. ELIGIBLE FOR STAGE 8; funding remains human.")


# C4 price/security binding and freshness

def test_c4_security_key_mismatch_blocks():
    u = underwriting(key="SEC:BRK.B", ticker="BRK.B", p=price("SEC:BRK.B", "BRK.B", quoted_key="SEC:BRK.A"))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW)


def test_c4_missing_quoted_security_mapping_blocks():
    u = underwriting(p=price(quoted_key=None))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW)


def test_c4_stale_flag_blocks():
    with pytest.raises(ControlFailure):
        validate_price_snapshot(underwriting(p=price(stale=True)), NOW)


def test_c4_completed_session_must_equal_latest_completed_session():
    u = underwriting(p=price(session=date(2026, 8, 31), latest=date(2026, 9, 1)))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW)


def test_c4_weekend_gap_does_not_fail_by_arbitrary_hour_age_when_latest_session_matches():
    monday = datetime(2026, 9, 7, 13, 0, tzinfo=timezone.utc)
    friday = date(2026, 9, 4)
    u = underwriting(p=price(session=friday, latest=friday, as_of=datetime(2026, 9, 4, 20, 0, tzinfo=timezone.utc)))
    validate_price_snapshot(u, monday)


def test_c4_intraday_quote_age_is_enforced():
    u = underwriting(p=price(mode=PriceMode.EXECUTABLE_INTRADAY, as_of=NOW - timedelta(minutes=30)))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW, intraday_max_age_minutes=15)


def test_c4_ticker_mismatch_blocks_even_when_security_key_matches():
    u = underwriting(key="SEC:BRK.B", ticker="BRK.B", p=price("SEC:BRK.B", "BRK.A", quoted_key="SEC:BRK.B"))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW)


def test_c4_future_price_timestamp_blocks():
    u = underwriting(p=price(as_of=NOW + timedelta(minutes=5)))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW)


def test_c4_completed_session_requires_closed_status():
    p = price()
    p = PriceSnapshot(
        security_key=p.security_key, ticker=p.ticker, price=p.price, price_as_of=p.price_as_of,
        price_session_date=p.price_session_date, latest_completed_session_date=p.latest_completed_session_date,
        currency=p.currency, provider=p.provider, market_session_status="OPEN", adjusted=p.adjusted,
        freshness_status=p.freshness_status, price_mode=p.price_mode, quoted_security_key=p.quoted_security_key,
    )
    with pytest.raises(ControlFailure):
        validate_price_snapshot(underwriting(p=p), NOW)


def test_c4_foreign_security_requires_fx_binding():
    p = price("HK:0700", "0700", quoted_key="HK:0700")
    p = PriceSnapshot(
        security_key=p.security_key, ticker=p.ticker, price=p.price, price_as_of=p.price_as_of,
        price_session_date=p.price_session_date, latest_completed_session_date=p.latest_completed_session_date,
        currency="HKD", provider=p.provider, market_session_status=p.market_session_status, adjusted=p.adjusted,
        freshness_status=p.freshness_status, price_mode=p.price_mode, quoted_security_key=p.quoted_security_key,
    )
    u = underwriting(key="HK:0700", ticker="0700", p=p, rb=ReturnBand(0.12, 0.16))
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW)
    assert result.status == "BLOCKED"
    assert "FX" in result.reasons[0]


def test_c4_foreign_security_with_fresh_bound_fx_can_proceed():
    p = price("HK:0700", "0700", quoted_key="HK:0700")
    p = PriceSnapshot(
        security_key=p.security_key, ticker=p.ticker, price=p.price, price_as_of=p.price_as_of,
        price_session_date=p.price_session_date, latest_completed_session_date=p.latest_completed_session_date,
        currency="HKD", provider=p.provider, market_session_status=p.market_session_status, adjusted=p.adjusted,
        freshness_status=p.freshness_status, price_mode=p.price_mode, quoted_security_key=p.quoted_security_key,
    )
    base = underwriting(key="HK:0700", ticker="0700", p=p, rb=ReturnBand(0.12, 0.16))
    u = CandidateUnderwriting(
        security_key=base.security_key, ticker=base.ticker, security_decision=base.security_decision,
        price_snapshot=base.price_snapshot, observable_regime=base.observable_regime,
        observable_regime_evidence=base.observable_regime_evidence, atlas_variant=base.atlas_variant,
        variant_evidence=base.variant_evidence, return_band=base.return_band, return_band_basis=base.return_band_basis,
        required_return_band=base.required_return_band, underwriting_gate_status=base.underwriting_gate_status,
        uncertainties=base.uncertainties, dominant_drivers=base.dominant_drivers,
        revisit_triggers=base.revisit_triggers, fundamentals=base.fundamentals,
        underwriting_provenance=base.underwriting_provenance, return_currency="USD",
        fx_snapshot=FXSnapshot("HKD", "USD", 0.128, NOW - timedelta(hours=1), "TESTFX", FreshnessStatus.FRESH),
    )
    rows = list(alternatives())
    rows[0] = ComparisonAlternative(
        AlternativeType.BETA, "SPY", ReturnBand(0.075, 0.105), security_key="ETF:SPY",
        overlap=ETFOverlap("SPY", "HK:0700", OverlapStatus.UNMEASURED),
        notes=("coarse SPY scenario basis",),
    )
    result = evaluate_stage7_candidate(u, portfolio(), position(), tuple(rows), NOW)
    assert result.status == "ELIGIBLE FOR STAGE 8"


# M1 cash-departure rule

def test_m1_overlapping_return_ranges_not_distinguishable():
    assert not ranges_distinguishable(ReturnBand(0.08, 0.11), ReturnBand(0.10, 0.12))


def test_m1_distinguishable_ranges_can_advance():
    u = underwriting(rb=ReturnBand(0.12, 0.16))
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(beta_rb=ReturnBand(0.07, 0.10)), NOW)
    assert result.status == "ELIGIBLE FOR STAGE 8"


def test_m1_nonoverlapping_but_worse_than_cash_must_not_advance():
    u = underwriting(rb=ReturnBand(-0.10, -0.05))
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW)
    assert result.status == "NOT DISTINGUISHABLE"
    assert any("CASH/TREASURY" in reason for reason in result.reasons)


def test_m1_candidate_must_clear_alternative_not_merely_differ():
    assert not range_clearly_better(ReturnBand(0.01, 0.02), ReturnBand(0.03, 0.04))
    assert range_clearly_better(ReturnBand(0.05, 0.08), ReturnBand(0.03, 0.04))


def test_m1_horizon_mismatch_fails_closed():
    assert not range_clearly_better(ReturnBand(0.12, 0.16, 3.0), ReturnBand(0.03, 0.04, 1.0))


# M2 false precision

def test_m2_sub_one_point_gap_with_overlapping_ranges_not_distinguishable():
    assert not ranges_distinguishable(ReturnBand(0.118, 0.132), ReturnBand(0.121, 0.129))


# M3 capacity / sizing

def test_m3_capacity_unverified_blocks():
    u = underwriting(rb=ReturnBand(0.12, 0.16))
    assert evaluate_stage7_candidate(u, portfolio(), position(capacity=CapacityStatus.UNVERIFIED), alternatives(), NOW).status == "BLOCKED"


def test_m3_position_exceeding_remaining_capacity_blocks():
    p = portfolio()
    u = underwriting(rb=ReturnBand(0.12, 0.16))
    pos = position(p=p, dollars=100_000, remaining=0.05)
    assert evaluate_stage7_candidate(u, p, pos, alternatives(), NOW).status == "BLOCKED"


def test_m3_portfolio_size_translation_is_percentage_based():
    assert translate_weight_to_dollars(500_000, 0.05) == 25_000
    assert translate_weight_to_dollars(1_000_000, 0.05) == 50_000
    assert translate_weight_to_dollars(2_000_000, 0.05) == 100_000


def test_m3_external_50k_on_1m_reconciles_to_4_76_percent_post_money():
    p = portfolio(amount=0)
    pos = position(p=p, dollars=50_000, mode=FundingMode.EXTERNAL_NEW_CAPITAL)
    assert pos.post_trade_portfolio_value == 1_050_000
    assert pos.proposed_increment_weight == pytest.approx(50_000 / 1_050_000)


def test_m3_internal_50k_on_1m_is_5_percent():
    p = portfolio(amount=100_000)
    pos = position(p=p, dollars=50_000, mode=FundingMode.INTERNAL_CASH)
    assert pos.post_trade_portfolio_value == 1_000_000
    assert pos.proposed_increment_weight == pytest.approx(0.05)


def test_m3_capacity_curve_scales_with_basket_size():
    assert capacity_curve_dollars(500_000)[0.10] == 50_000
    assert capacity_curve_dollars(2_000_000)[0.10] == 200_000


def test_m3_external_new_capital_curve_uses_post_money_weight():
    curve = capacity_curve_dollars(1_000_000, funding_mode=FundingMode.EXTERNAL_NEW_CAPITAL)
    assert curve[0.05] == pytest.approx(52_631.578947)
    # $50k of external capital is 4.7619% post-money, not 5%.
    p = portfolio(amount=50_000)
    pos = position(p=p, dollars=50_000, mode=FundingMode.EXTERNAL_NEW_CAPITAL)
    assert pos.proposed_increment_weight == pytest.approx(50_000 / 1_050_000)


def test_m3_external_new_capital_cannot_exceed_named_funding_pocket():
    p = portfolio(amount=25_000)
    u = underwriting(rb=ReturnBand(0.12, 0.16))
    pos = position(p=p, dollars=50_000, mode=FundingMode.EXTERNAL_NEW_CAPITAL)
    assert evaluate_stage7_candidate(u, p, pos, alternatives(), NOW).status == "BLOCKED"


# M4 funding pocket / execution

def test_m4_unverified_constraints_block_stage7_without_human_acceptance():
    p = portfolio(statuses=VerificationStatus.UNVERIFIED)
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), p, position(p=p), alternatives(), NOW)
    assert result.status == "BLOCKED"


def test_m4_human_acceptance_can_advance_unverified_constraints_to_stage8_but_not_execute():
    p = portfolio(statuses=VerificationStatus.UNVERIFIED)
    result = evaluate_stage7_candidate(
        underwriting(rb=ReturnBand(0.12, 0.16)), p, position(p=p), alternatives(), NOW,
        human_accepts_unverified_constraints=True,
    )
    assert result.status == "ELIGIBLE FOR STAGE 8"
    with pytest.raises(ControlFailure):
        validate_funding_pocket(p, require_verified_constraints=True, human_accepts_unverified=False)


def test_m4_missing_constraints_blocks():
    with pytest.raises(ControlFailure):
        validate_funding_pocket(portfolio(constraints=False), require_verified_constraints=False)


# M5 recycle-from-holdings

def test_m5_missing_recycle_when_trims_permitted_blocks_stage7():
    u = underwriting(rb=ReturnBand(0.12, 0.16))
    result = evaluate_stage7_candidate(u, portfolio(trims=True), position(), alternatives(recycle=False), NOW)
    assert result.status == "BLOCKED"


def test_m5_add_only_policy_allows_no_recycle():
    p = portfolio(trims=False, add_only=True)
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), p, position(p=p), alternatives(recycle=False), NOW)
    assert result.status == "ELIGIBLE FOR STAGE 8"


# M6 common drivers

def test_m6_shared_driver_requires_cluster_note_case_insensitive():
    a = underwriting(key="SEC:A", ticker="AAA", drivers=("Enterprise IT", "AI Transformation"))
    b = underwriting(key="SEC:B", ticker="BBB", drivers=("enterprise   IT", "other"))
    with pytest.raises(ControlFailure):
        validate_common_driver_cluster((a, b), None)


def test_m6_shared_driver_with_note_passes():
    a = underwriting(key="SEC:A", ticker="AAA")
    b = underwriting(key="SEC:B", ticker="BBB")
    validate_common_driver_cluster((a, b), "Both depend on enterprise IT / AI spend.")


def test_m6_pairwise_shared_driver_among_three_requires_note():
    a = underwriting(key="SEC:A", ticker="AAA", drivers=("AI", "consumer"))
    b = underwriting(key="SEC:B", ticker="BBB", drivers=("AI", "rates"))
    c = underwriting(key="SEC:C", ticker="CCC", drivers=("healthcare", "policy"))
    with pytest.raises(ControlFailure):
        validate_common_driver_cluster((a, b, c), None)


# M7 append-only auditability

def _frozen_inputs(root):
    from stock_atlas.freeze import freeze_payload
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    return InputVersions(
        freeze_payload({"portfolio": "P1"}, version="p1", destination=root / "portfolio.json"),
        freeze_payload({"scenario": "s1"}, version="s1", destination=root / "scenario.json"),
        freeze_payload({"exposure": "e1"}, version="e1", destination=root / "exposure.json"),
        freeze_payload({"evidence": "ev1"}, version="ev1", destination=root / "evidence.json"),
        freeze_payload({"contract": "c1"}, version="c1", destination=root / "contract.json"),
    )


def _stage7_artifact(root, *, status="ELIGIBLE FOR STAGE 8", key="SEC:ACN", constraint="VERIFIED", position_payload=None):
    from stock_atlas.freeze import freeze_payload
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    return freeze_payload(
        {
            "decision_time": NOW,
            "result": {
                "security_key": key,
                "ticker": key.split(":")[-1],
                "status": status,
                "reasons": ["test"],
                "position": position_payload,
                "constraint_state": constraint,
                "overlap_status": "UNMEASURED",
            },
            "rendered_text": "COMPARISON AID — NO PORTFOLIO ACTION — STAGE 8 OPEN",
        },
        version="stage7-control-v0.2",
        destination=root / "stage7.json",
    )


def make_record(record_id="R1", prior=None, artifact_root=None):
    import tempfile
    root = Path(artifact_root or tempfile.mkdtemp(prefix=f"atlas-{record_id}-"))
    return DecisionRecord(
        record_id=record_id,
        created_at=NOW,
        review_event_type=ReviewEventType.FINAL_CAPITAL_DECISION,
        candidate_security_key="SEC:ACN",
        portfolio_snapshot_id="P1",
        input_versions=_frozen_inputs(root / "inputs"),
        stage7_status="ELIGIBLE FOR STAGE 8",
        stage7_reasons=("test",),
        human_stage8_action=PortfolioAction.HOLD_CASH,
        human_rationale="human choice",
        prior_record_id=prior,
        revisit_triggers=RevisitTriggers("±25% price move", NOW + timedelta(days=90)),
        alternatives_considered=("ACN", "SPY", "Treasury", "Do Nothing"),
        stage7_artifact=_stage7_artifact(root / "stage7"),
        constraint_state=VerificationStatus.VERIFIED,
    )


def test_m7_append_only_duplicate_rejected(tmp_path):
    store = DecisionStore(tmp_path / "decisions.jsonl")
    store.append(make_record("R1"))
    with pytest.raises(ControlFailure):
        store.append(make_record("R1"))


def test_m7_prior_record_must_exist(tmp_path):
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(make_record("R2", prior="MISSING"))


def test_m7_hash_chain_integrity_detects_tamper(tmp_path):
    path = tmp_path / "decisions.jsonl"
    store = DecisionStore(path)
    store.append(make_record("R1"))
    store.append(make_record("R2", prior="R1"))
    assert store.verify_integrity()
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    rows[0]["record"]["human_rationale"] = "tampered"
    path.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
    assert not store.verify_integrity()


def test_m7_manifest_hash_changes_after_append(tmp_path):
    store = DecisionStore(tmp_path / "decisions.jsonl")
    h0 = store.manifest_hash()
    store.append(make_record("R1"))
    assert store.manifest_hash() != h0


def test_m7_overwrite_prohibited(tmp_path):
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").overwrite()


def test_m7_final_decision_requires_human_action(tmp_path):
    from dataclasses import replace
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(replace(make_record(), human_stage8_action=None))


def test_m7_nonfinal_review_cannot_smuggle_portfolio_action(tmp_path):
    from dataclasses import replace
    record = replace(make_record(), review_event_type=ReviewEventType.TRIGGER_REVIEW)
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_m7_initiate_requires_revisit_triggers(tmp_path):
    from dataclasses import replace
    record = replace(make_record(), human_stage8_action=PortfolioAction.INITIATE, revisit_triggers=None)
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_m7_final_decision_requires_cash_and_do_nothing_alternatives(tmp_path):
    from dataclasses import replace
    record = replace(make_record(), alternatives_considered=("ACN", "SPY"))
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


# M8 period granularity

def test_m8_mixed_period_granularity_blocks():
    obs = (
        FundamentalObservation("revenue", 100, PeriodGranularity.QUARTER),
        FundamentalObservation("revenue", 200, PeriodGranularity.YTD),
    )
    with pytest.raises(ControlFailure):
        validate_period_granularity(obs)


def test_m8_normalized_granularity_passes():
    obs = (
        FundamentalObservation("revenue", 100, PeriodGranularity.QUARTER, normalized_to=PeriodGranularity.TTM, normalization_basis="converted to TTM from four quarters"),
        FundamentalObservation("revenue", 200, PeriodGranularity.YTD, normalized_to=PeriodGranularity.TTM, normalization_basis="converted to TTM from YTD plus prior-year bridge"),
    )
    validate_period_granularity(obs)


def test_m8_normalized_granularity_without_basis_blocks():
    obs = (
        FundamentalObservation("revenue", 100, PeriodGranularity.QUARTER, normalized_to=PeriodGranularity.TTM),
        FundamentalObservation("revenue", 200, PeriodGranularity.YTD, normalized_to=PeriodGranularity.TTM),
    )
    with pytest.raises(ControlFailure):
        validate_period_granularity(obs)


def test_m8_different_fields_may_use_different_natural_granularities():
    obs = (
        FundamentalObservation("revenue", 100, PeriodGranularity.QUARTER),
        FundamentalObservation("net_debt", 50, PeriodGranularity.POINT_IN_TIME),
    )
    validate_period_granularity(obs)


def test_m8_stage7_automatically_enforces_granularity_control():
    from dataclasses import replace
    base = underwriting(rb=ReturnBand(0.12, 0.16))
    mixed = replace(
        base,
        fundamentals=(
            FundamentalObservation("revenue", 100, PeriodGranularity.QUARTER),
            FundamentalObservation("revenue", 200, PeriodGranularity.YTD),
        ),
    )
    result = evaluate_stage7_candidate(mixed, portfolio(), position(), alternatives(), NOW)
    assert result.status == "BLOCKED"
    assert "granularities" in result.reasons[0]


# Required alternatives and Do Nothing

def test_do_nothing_and_treasury_are_distinct_required_decision_objects():
    rows = alternatives()
    validate_required_alternatives(rows)
    labels = {a.alternative_type for a in rows}
    assert AlternativeType.DO_NOTHING in labels and AlternativeType.TREASURY_CASH in labels


def test_missing_do_nothing_blocks_stage7():
    rows = tuple(a for a in alternatives() if a.alternative_type != AlternativeType.DO_NOTHING)
    with pytest.raises(ControlFailure):
        validate_required_alternatives(rows)


def test_duplicate_beta_alternative_blocks_ambiguous_comparison():
    rows = alternatives() + (ComparisonAlternative(AlternativeType.BETA, "QQQ", ReturnBand(0.08, 0.11), security_key="ETF:QQQ"),)
    with pytest.raises(ControlFailure):
        validate_required_alternatives(rows)


def test_treasury_reference_must_be_fresh_and_duration_verified():
    rows = list(alternatives())
    rows[1] = ComparisonAlternative(
        AlternativeType.TREASURY_CASH, "Treasury/Cash", ReturnBand(0.035, 0.045),
        market_reference=MarketReferenceSnapshot("UST-13W", 0.039, NOW, "TEST", FreshnessStatus.STALE, "USD"),
        duration_match_status=VerificationStatus.VERIFIED,
        notes=("duration basis",),
    )
    with pytest.raises(ControlFailure):
        validate_required_alternatives(tuple(rows))

    rows[1] = ComparisonAlternative(
        AlternativeType.TREASURY_CASH, "Treasury/Cash", ReturnBand(0.035, 0.045),
        market_reference=MarketReferenceSnapshot("UST-13W", 0.039, NOW, "TEST", FreshnessStatus.FRESH, "USD"),
        duration_match_status=VerificationStatus.UNVERIFIED,
        notes=("duration basis",),
    )
    with pytest.raises(ControlFailure):
        validate_required_alternatives(tuple(rows))


def test_treasury_reference_future_timestamp_blocks_stage7():
    rows = list(alternatives())
    rows[1] = ComparisonAlternative(
        AlternativeType.TREASURY_CASH, "Treasury/Cash", ReturnBand(0.035, 0.045),
        market_reference=MarketReferenceSnapshot("UST-13W", 0.039, NOW + timedelta(minutes=5), "TEST", FreshnessStatus.FRESH, "USD"),
        duration_match_status=VerificationStatus.VERIFIED,
        notes=("duration basis",),
    )
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), tuple(rows), NOW)
    assert result.status == "BLOCKED"


def test_beta_return_band_without_basis_notes_blocks():
    rows = list(alternatives())
    rows[0] = ComparisonAlternative(
        AlternativeType.BETA, "SPY", ReturnBand(0.075, 0.105), security_key="ETF:SPY",
        overlap=ETFOverlap("SPY", "SEC:ACN", OverlapStatus.UNMEASURED), notes=(),
    )
    with pytest.raises(ControlFailure):
        validate_required_alternatives(tuple(rows))


def test_etf_overlap_record_must_bind_to_candidate_being_evaluated():
    u = underwriting(key="SEC:RMD", ticker="RMD", rb=ReturnBand(0.12, 0.16), p=price("SEC:RMD", "RMD"))
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW)
    assert result.status == "BLOCKED"
    assert "different candidate" in result.reasons[0]


# Missing-data negative control

def test_missing_provenance_fails_closed():
    result = evaluate_stage7_candidate(underwriting(provenance=()), portfolio(), position(), alternatives(), NOW)
    assert result.status == "WATCH / NO DECISION"


# Stage 8 remains human

def test_stage7_never_emits_portfolio_action():
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), alternatives(), NOW)
    assert result.status == "ELIGIBLE FOR STAGE 8"
    assert not hasattr(result, "portfolio_action")


# Observable priced-in / variant claims require bound evidence
def test_priced_in_claim_without_evidence_fails_closed():
    u = underwriting()
    u = CandidateUnderwriting(
        security_key=u.security_key, ticker=u.ticker, security_decision=u.security_decision, price_snapshot=u.price_snapshot,
        observable_regime=u.observable_regime, observable_regime_evidence=(), atlas_variant=u.atlas_variant,
        variant_evidence=u.variant_evidence, return_band=u.return_band, return_band_basis=u.return_band_basis,
        required_return_band=u.required_return_band, underwriting_gate_status=u.underwriting_gate_status,
        uncertainties=u.uncertainties, dominant_drivers=u.dominant_drivers, revisit_triggers=u.revisit_triggers,
        fundamentals=u.fundamentals, underwriting_provenance=u.underwriting_provenance,
    )
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW)
    assert result.status == "WATCH / NO DECISION"


def test_return_band_without_basis_fails_closed():
    u = underwriting()
    u = CandidateUnderwriting(
        security_key=u.security_key, ticker=u.ticker, security_decision=u.security_decision, price_snapshot=u.price_snapshot,
        observable_regime=u.observable_regime, observable_regime_evidence=u.observable_regime_evidence, atlas_variant=u.atlas_variant,
        variant_evidence=u.variant_evidence, return_band=u.return_band, return_band_basis=(), uncertainties=u.uncertainties,
        required_return_band=u.required_return_band, underwriting_gate_status=u.underwriting_gate_status,
        dominant_drivers=u.dominant_drivers, revisit_triggers=u.revisit_triggers, fundamentals=u.fundamentals,
        underwriting_provenance=u.underwriting_provenance,
    )
    assert evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW).status == "WATCH / NO DECISION"


# Frozen input hashes bind record versions to immutable content
def test_frozen_input_ref_detects_payload_change(tmp_path):
    from stock_atlas.freeze import freeze_payload, verify_frozen_payload
    payload = {"portfolio": "P1", "weight": 0.12}
    ref = freeze_payload(payload, version="p1", destination=tmp_path / "p1.json")
    assert verify_frozen_payload(payload, ref)
    assert not verify_frozen_payload({"portfolio": "P1", "weight": 0.13}, ref)


def test_frozen_input_path_cannot_be_silently_reused_for_different_payload(tmp_path):
    from stock_atlas.freeze import freeze_payload
    path = tmp_path / "frozen.json"
    freeze_payload({"x": 1}, version="v1", destination=path)
    with pytest.raises(ControlFailure):
        freeze_payload({"x": 2}, version="v1", destination=path)


def test_frozen_payload_rejects_non_finite_numbers(tmp_path):
    from stock_atlas.freeze import freeze_payload
    with pytest.raises(ControlFailure):
        freeze_payload({"x": float("nan")}, version="v1", destination=tmp_path / "nan.json")


def test_stage7_renderer_is_non_directive():
    from stock_atlas.presentation import render_stage7_result
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), alternatives(), NOW)
    text = render_stage7_result(result)
    assert "HUMAN STAGE 8 ONLY" in text
    assert "Do Nothing" in text


def _concurrent_append_worker(path_str, record_id, queue):
    try:
        store = DecisionStore(path_str)
        store.append(make_record(record_id))
        queue.put("OK")
    except Exception as e:
        queue.put(type(e).__name__)


def test_m7_concurrent_duplicate_id_only_one_append_succeeds(tmp_path):
    import multiprocessing as mp
    ctx = mp.get_context("spawn")
    path = str(tmp_path / "decisions.jsonl")
    q = ctx.Queue()
    a = ctx.Process(target=_concurrent_append_worker, args=(path, "R1", q))
    b = ctx.Process(target=_concurrent_append_worker, args=(path, "R1", q))
    a.start(); b.start(); a.join(5); b.join(5)
    outcomes = sorted([q.get(timeout=2), q.get(timeout=2)])
    assert outcomes == ["ControlFailure", "OK"]
    assert DecisionStore(path).verify_integrity()


def test_m7_append_blocks_if_existing_history_is_tampered(tmp_path):
    path = tmp_path / "decisions.jsonl"
    store = DecisionStore(path)
    store.append(make_record("R1"))
    rows = [json.loads(x) for x in path.read_text().splitlines()]
    rows[0]["record"]["human_rationale"] = "tampered"
    path.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
    with pytest.raises(ControlFailure):
        store.append(make_record("R2", prior="R1"))


def test_numeric_models_reject_nan_and_infinity():
    with pytest.raises(ValueError):
        ReturnBand(float("nan"), 0.10)
    with pytest.raises(ValueError):
        PriceSnapshot(
            security_key="SEC:X", ticker="X", price=float("inf"), price_as_of=NOW,
            price_session_date=SESSION, latest_completed_session_date=SESSION, currency="USD",
            provider="TEST", market_session_status="CLOSED", adjusted=False,
            freshness_status=FreshnessStatus.FRESH, quoted_security_key="SEC:X",
        )


def test_canonical_stage7_pipeline_stops_before_portfolio_action():
    from stock_atlas.pipeline import run_stage7_pipeline
    run = run_stage7_pipeline(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), alternatives(), NOW)
    assert run.result.status == "ELIGIBLE FOR STAGE 8"
    assert "HUMAN STAGE 8 ONLY" in run.rendered_text
    assert not hasattr(run.result, "portfolio_action")

# Code Red Team remediation regressions — September 2, 2026

def _initiate_record(
    root,
    *,
    record_id="I1",
    key="SEC:ACN",
    action=PortfolioAction.INITIATE,
    stage7_status="ELIGIBLE FOR STAGE 8",
    constraint_state=VerificationStatus.VERIFIED,
    artifact_constraint="VERIFIED",
    current_weight=0.0,
    post_trade_weight=0.02,
    classification=PositionClassification.STARTER,
    starter_cap=0.03,
    drivers=("enterprise IT", "AI transformation"),
    cluster_note=None,
    prior=None,
):
    root = Path(root)
    position_payload = {
        "current_weight": current_weight,
        "proposed_increment_weight": max(0.0, post_trade_weight - current_weight),
        "proposed_increment_dollars": 20_000.0,
        "post_trade_portfolio_value": 1_000_000.0,
        "post_trade_weight": post_trade_weight,
        "classification": classification.value,
        "capacity_status": CapacityStatus.AVAILABLE.value,
        "remaining_capacity": 0.10,
        "funding_source": "cash",
        "funding_mode": FundingMode.INTERNAL_CASH.value,
        "sensitivity_weights": [0.01, 0.03, 0.05, 0.10],
    }
    return DecisionRecord(
        record_id=record_id,
        created_at=NOW,
        review_event_type=ReviewEventType.FINAL_CAPITAL_DECISION,
        candidate_security_key=key,
        portfolio_snapshot_id="P1",
        input_versions=_frozen_inputs(root / "inputs"),
        stage7_status=stage7_status,
        stage7_reasons=("test",),
        human_stage8_action=action,
        human_rationale="human selected action after comparison",
        prior_record_id=prior,
        revisit_triggers=RevisitTriggers("±25% price move", NOW + timedelta(days=90)),
        alternatives_considered=(key, "SPY", "Treasury", "Do Nothing"),
        stage7_artifact=_stage7_artifact(
            root / "stage7",
            status=stage7_status,
            key=key,
            constraint=artifact_constraint,
            position_payload=position_payload,
        ),
        constraint_state=constraint_state,
        dominant_drivers=drivers,
        cluster_note=cluster_note,
        position_classification=classification,
        post_trade_weight=post_trade_weight,
        starter_cap_weight=starter_cap,
    )


def test_code_rt_c01_initiate_after_blocked_stage7_is_rejected(tmp_path):
    record = _initiate_record(tmp_path / "r", stage7_status="BLOCKED")
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_code_rt_c01_initiate_requires_retained_hashed_eligible_bundle(tmp_path):
    record = _initiate_record(tmp_path / "r")
    stored = DecisionStore(tmp_path / "decisions.jsonl").append(record)
    assert stored.human_stage8_action == PortfolioAction.INITIATE


def test_code_rt_c01_stage7_artifact_status_must_match_record(tmp_path):
    from dataclasses import replace
    record = _initiate_record(tmp_path / "r")
    bad_artifact = _stage7_artifact(
        tmp_path / "bad-stage7", status="BLOCKED", key="SEC:ACN", constraint="VERIFIED",
        position_payload={
            "current_weight": 0.0, "post_trade_weight": 0.02,
            "classification": PositionClassification.STARTER.value,
        },
    )
    record = replace(record, stage7_artifact=bad_artifact)
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_code_rt_c02_self_consistent_old_completed_session_blocks():
    old = date(2026, 8, 1)
    u = underwriting(p=price(session=old, latest=old, as_of=datetime(2026, 8, 1, 20, 0, tzinfo=timezone.utc)))
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW)


def test_code_rt_c02_market_calendar_attestation_must_match_snapshot():
    u = underwriting()
    with pytest.raises(ControlFailure):
        validate_price_snapshot(u, NOW, known_latest_session_date=date(2026, 9, 2))


def test_code_rt_c02_stale_consistent_treasury_reference_blocks_stage7():
    rows = list(alternatives())
    rows[1] = ComparisonAlternative(
        AlternativeType.TREASURY_CASH,
        "Treasury/Cash",
        ReturnBand(0.035, 0.045),
        market_reference=MarketReferenceSnapshot(
            "UST-13W", 0.039, NOW - timedelta(days=20), "TEST", FreshnessStatus.FRESH, "USD"
        ),
        duration_match_status=VerificationStatus.VERIFIED,
        notes=("duration basis",),
    )
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), tuple(rows), NOW)
    assert result.status == "BLOCKED"
    assert "too old" in result.reasons[0]


def test_code_rt_c02_stale_consistent_fx_blocks():
    from dataclasses import replace
    base = underwriting(key="SEC:TCEHY", ticker="TCEHY", rb=ReturnBand(0.12, 0.16))
    foreign_price = replace(base.price_snapshot, currency="HKD", quoted_security_key="SEC:TCEHY")
    u = replace(
        base,
        price_snapshot=foreign_price,
        fx_snapshot=FXSnapshot("HKD", "USD", 0.128, NOW - timedelta(days=20), "TEST", FreshnessStatus.FRESH),
    )
    result = evaluate_stage7_candidate(u, portfolio(), position(), alternatives(), NOW)
    assert result.status == "BLOCKED"
    assert "FX snapshot is too old" in result.reasons[0]


def test_code_rt_c03_package_root_does_not_export_low_level_bypass_helpers():
    import stock_atlas
    assert not hasattr(stock_atlas, "evaluate_stage7_candidate")
    assert not hasattr(stock_atlas, "DecisionRecord")
    assert hasattr(stock_atlas, "run_stage7_pipeline")
    assert hasattr(stock_atlas, "DecisionStore")


def test_code_rt_m01_unverified_stage7_cannot_become_initiate(tmp_path):
    record = _initiate_record(
        tmp_path / "r",
        constraint_state=VerificationStatus.UNVERIFIED,
        artifact_constraint="UNVERIFIED",
    )
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_code_rt_m02_unmeasured_overlap_is_visible_without_portfolio_fit_credit():
    run = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), alternatives(), NOW)
    assert run.status == "ELIGIBLE FOR STAGE 8"
    assert run.overlap_status == OverlapStatus.UNMEASURED
    assert any("UNMEASURED_OVERLAP" in r for r in run.reasons)


def test_code_rt_m02_stage7_language_rejects_diversification_claim_and_imperative():
    with pytest.raises(ControlFailure):
        validate_stage7_language("This diversifies the portfolio versus SPY")
    with pytest.raises(ControlFailure):
        validate_stage7_language("Stage 8 should take the increment")


def test_code_rt_m03_second_funded_name_with_shared_driver_requires_cluster_note(tmp_path):
    store = DecisionStore(tmp_path / "decisions.jsonl")
    store.append(_initiate_record(tmp_path / "a", record_id="A1", key="SEC:A", drivers=("enterprise IT", "consumer")))
    second = _initiate_record(tmp_path / "b", record_id="B1", key="SEC:B", drivers=("enterprise IT", "rates"))
    with pytest.raises(ControlFailure):
        store.append(second)


def test_code_rt_m03_shared_driver_with_cluster_note_passes(tmp_path):
    store = DecisionStore(tmp_path / "decisions.jsonl")
    store.append(_initiate_record(tmp_path / "a", record_id="A1", key="SEC:A", drivers=("enterprise IT", "consumer")))
    second = _initiate_record(
        tmp_path / "b", record_id="B1", key="SEC:B", drivers=("enterprise IT", "rates"),
        cluster_note="Both funded names depend on enterprise IT spending; human accepted combined exposure.",
    )
    store.append(second)
    assert store.verify_integrity()


def test_code_rt_m04_repeated_starter_cannot_reset_current_weight(tmp_path):
    store = DecisionStore(tmp_path / "decisions.jsonl")
    store.append(_initiate_record(tmp_path / "a", record_id="A1", key="SEC:A", post_trade_weight=0.02, starter_cap=0.05))
    # A later ADD pretending the existing position is still zero must be rejected.
    second = _initiate_record(
        tmp_path / "b", record_id="A2", key="SEC:A", action=PortfolioAction.ADD,
        current_weight=0.0, post_trade_weight=0.02, starter_cap=0.05, prior="A1",
    )
    with pytest.raises(ControlFailure):
        store.append(second)


def test_code_rt_m04_starter_cap_binds_cumulative_post_trade_weight(tmp_path):
    record = _initiate_record(tmp_path / "r", post_trade_weight=0.04, starter_cap=0.03)
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_code_rt_m06_deleted_frozen_input_blocks_final_append(tmp_path):
    record = make_record("R1", artifact_root=tmp_path / "r")
    Path(record.input_versions.evidence_set.artifact_path).unlink()
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_code_rt_m06_deleted_stage7_artifact_blocks_final_append(tmp_path):
    record = make_record("R1", artifact_root=tmp_path / "r")
    Path(record.stage7_artifact.artifact_path).unlink()
    with pytest.raises(ControlFailure):
        DecisionStore(tmp_path / "decisions.jsonl").append(record)


def test_code_rt_m05_renderer_remains_structured_and_non_directive():
    from stock_atlas.presentation import render_stage7_result
    result = evaluate_stage7_candidate(underwriting(rb=ReturnBand(0.12, 0.16)), portfolio(), position(), alternatives(), NOW)
    text = render_stage7_result(result)
    assert "HUMAN STAGE 8 ONLY" in text
    assert "No portfolio action is authorized" in text
    validate_stage7_language(text)
