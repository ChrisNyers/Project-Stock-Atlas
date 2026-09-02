from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Sequence
import re
import math

from .models import (
    AlternativeType,
    BlockFlag,
    CandidateUnderwriting,
    CapacityStatus,
    ComparisonAlternative,
    ETFOverlap,
    FreshnessStatus,
    FXSnapshot,
    FundingMode,
    OverlapStatus,
    PortfolioSnapshot,
    PositionProposal,
    PriceMode,
    ReturnBand,
    SecurityDecision,
    Stage7CandidateResult,
    UnderwritingGateStatus,
    VerificationStatus,
)


STAGE7_HEADER = "COMPARISON AID — NO PORTFOLIO ACTION — STAGE 8 OPEN"
# These phrases are banned when used as free-form Stage 7 treatment language.
# Structured Security Decision fields remain separate from this free-form text scan.
PROHIBITED_STAGE7_PATTERNS = (
    r"\bpreferred\b",
    r"\brecommend(?:s|ed|ation)?\b",
    r"\bbest\b",
    r"\btop pick\b",
    r"\bwinner\b",
    r"\brank(?:ed|ing)?\b",
    r"\bearn(?:s|ed)? increment\b",
    r"\b(?:buy|sell|trim|add|allocate|fund|initiate|increase|reduce)\s+(?:\$?[0-9]|[A-Z][A-Z0-9\.\-]{0,9})",
    r"\bshould\b.{0,40}\b(?:buy|sell|fund|allocate|initiate|add|take)\b",
    r"\bclears? (?:the )?cash bar\b",
    r"\bdiversif(?:y|ies|ied|ication)\b",
)


class ControlFailure(ValueError):
    """Raised when a binding control fails closed."""


def validate_stage7_language(text: str) -> None:
    for pattern in PROHIBITED_STAGE7_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise ControlFailure(f"Stage 7 recommendation leakage detected: {pattern}")
    ordered = re.findall(r"(?m)^\s*\d+[\.)]\s+[A-Z][A-Z0-9\.\-]{0,9}\b", text)
    if len(ordered) >= 2:
        raise ControlFailure("Stage 7 ordered candidate ranking detected")


def validate_price_snapshot(
    underwriting: CandidateUnderwriting,
    decision_time: datetime,
    intraday_max_age_minutes: float = 15.0,
    *,
    known_latest_session_date: date | None = None,
    max_completed_session_age_days: int = 4,
) -> None:
    p = underwriting.price_snapshot
    required_text = {
        "security_key": p.security_key,
        "ticker": p.ticker,
        "currency": p.currency,
        "provider": p.provider,
        "market_session_status": p.market_session_status,
        "quoted_security_key": p.quoted_security_key,
    }
    missing = [name for name, value in required_text.items() if value is None or not str(value).strip()]
    if missing:
        raise ControlFailure(f"Missing price-binding fields: {', '.join(missing)}")
    if p.security_key != underwriting.security_key:
        raise ControlFailure("Underwriting security_key does not match bound price security_key")
    if p.ticker.strip().upper() != underwriting.ticker.strip().upper():
        raise ControlFailure("Underwriting ticker does not match bound price ticker")
    if p.quoted_security_key != underwriting.security_key:
        raise ControlFailure("Quoted security does not match underwriting security")
    if p.freshness_status != FreshnessStatus.FRESH:
        raise ControlFailure("Price snapshot is STALE")

    dt = decision_time if decision_time.tzinfo else decision_time.replace(tzinfo=timezone.utc)
    pa = p.price_as_of if p.price_as_of.tzinfo else p.price_as_of.replace(tzinfo=timezone.utc)
    if (pa - dt).total_seconds() > 60:
        raise ControlFailure("Price timestamp is materially in the future")

    if p.price_mode == PriceMode.COMPLETED_SESSION:
        if p.price_session_date != p.latest_completed_session_date:
            raise ControlFailure("Completed-session price is not from the latest completed trading session")
        if p.latest_completed_session_date > dt.date():
            raise ControlFailure("Latest completed session cannot be after the decision date")
        if known_latest_session_date is not None:
            if p.latest_completed_session_date != known_latest_session_date:
                raise ControlFailure("Completed-session price is not bound to the attested latest trading session")
        else:
            age_days = (dt.date() - p.latest_completed_session_date).days
            if age_days > max_completed_session_age_days:
                raise ControlFailure("Completed-session price is too old to be accepted as FRESH without a market-calendar attestation")
        if p.market_session_status.strip().upper() not in {"CLOSED", "COMPLETED"}:
            raise ControlFailure("Completed-session snapshot must identify a closed/completed market session")
    else:
        age_minutes = (dt - pa).total_seconds() / 60.0
        if age_minutes < -1:
            raise ControlFailure("Intraday price timestamp is materially in the future")
        if age_minutes > intraday_max_age_minutes:
            raise ControlFailure("Executable intraday quote exceeds freshness window")


def validate_opportunity_eligibility(underwriting: CandidateUnderwriting) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    def nonblank(items: Sequence[str]) -> bool:
        return bool(items) and all(str(item).strip() for item in items)

    if underwriting.security_decision != SecurityDecision.BUY:
        reasons.append(f"security_decision={underwriting.security_decision.value} does not permit new-capital comparison")
    if not underwriting.observable_regime.strip():
        reasons.append("missing observable priced-in regime")
    if not nonblank(underwriting.observable_regime_evidence):
        reasons.append("missing evidence for observable priced-in regime")
    if not underwriting.atlas_variant.strip():
        reasons.append("missing Atlas variant")
    if not nonblank(underwriting.variant_evidence):
        reasons.append("missing evidence for Atlas variant")
    if underwriting.return_band is None:
        reasons.append("missing coarse return/variant band")
    if not nonblank(underwriting.return_band_basis):
        reasons.append("missing return-band basis/provenance")
    if underwriting.required_return_band is None:
        reasons.append("missing required-return band")
    elif underwriting.return_band is not None and abs(underwriting.required_return_band.horizon_years - underwriting.return_band.horizon_years) > 1e-9:
        reasons.append("required-return horizon does not match candidate return horizon")
    if underwriting.underwriting_gate_status != UnderwritingGateStatus.CLEAR:
        reasons.append(f"underwriting_gate_status={underwriting.underwriting_gate_status.value} does not permit new-capital comparison")
    if not underwriting.uncertainties:
        reasons.append("missing typed uncertainty")
    if not nonblank(underwriting.dominant_drivers) or len(underwriting.dominant_drivers) > 3:
        reasons.append("dominant drivers must contain 1–3 items")
    if underwriting.revisit_triggers is None:
        reasons.append("missing price/time revisit triggers")
    if not nonblank(underwriting.underwriting_provenance):
        reasons.append("missing underwriting provenance")
    return (not reasons, tuple(reasons))


def ranges_distinguishable(candidate: ReturnBand | None, alternative: ReturnBand | None) -> bool:
    if candidate is None or alternative is None:
        return False
    if abs(candidate.horizon_years - alternative.horizon_years) > 1e-9:
        return False
    return not candidate.overlaps(alternative)


def range_clearly_better(candidate: ReturnBand | None, alternative: ReturnBand | None) -> bool:
    """True only when the entire candidate band sits above the alternative band.

    Stage 7 is a capital-departure gate, so merely being different from cash/beta is
    not enough. A clearly worse non-overlapping range must fail closed rather than
    being treated as an investable distinction.
    """
    if candidate is None or alternative is None:
        return False
    if abs(candidate.horizon_years - alternative.horizon_years) > 1e-9:
        return False
    return candidate.low > alternative.high


def validate_etf_overlap(overlap: ETFOverlap | None, comparison_depends_on_diversification: bool = False) -> None:
    if overlap is None:
        if comparison_depends_on_diversification:
            raise ControlFailure("ETF/proxy overlap required but missing")
        return
    if overlap.status == OverlapStatus.MEASURED:
        if overlap.lookthrough_weight is None or overlap.source is None or overlap.as_of is None:
            raise ControlFailure("MEASURED overlap requires weight, source, and as-of")
        if not 0 <= overlap.lookthrough_weight <= 1:
            raise ControlFailure("ETF look-through weight must be between 0 and 1")
    if overlap.status == OverlapStatus.UNMEASURED and comparison_depends_on_diversification:
        raise ControlFailure("Cannot claim diversification with UNMEASURED ETF overlap")


def validate_period_granularity(observations: Sequence, comparison_requested: bool = True) -> None:
    if not comparison_requested or len(observations) <= 1:
        return
    for obs in observations:
        if obs.normalized_to is not None and not (obs.normalization_basis and obs.normalization_basis.strip()):
            raise ControlFailure("Normalized fundamentals require explicit normalization_basis")
    by_field: dict[str, list] = {}
    for obs in observations:
        by_field.setdefault(str(obs.field_name).strip().lower(), []).append(obs)
    for field_name, field_obs in by_field.items():
        effective = [obs.normalized_to or obs.period_granularity for obs in field_obs]
        if len(set(effective)) > 1:
            raise ControlFailure(f"Mixed period granularities for {field_name} are INVALID unless normalized")


def validate_fx_binding(
    underwriting: CandidateUnderwriting,
    portfolio: PortfolioSnapshot,
    decision_time: datetime,
    *,
    max_age_hours: float = 96.0,
) -> None:
    price_ccy = underwriting.price_snapshot.currency.strip().upper()
    base_ccy = portfolio.base_currency.strip().upper()
    return_ccy = underwriting.return_currency.strip().upper()
    if return_ccy != base_ccy:
        raise ControlFailure("Decision-facing return band must be expressed in portfolio base currency")
    if price_ccy == base_ccy:
        return
    fx = underwriting.fx_snapshot
    if fx is None:
        raise ControlFailure("Foreign-currency security requires a bound FX snapshot")
    if fx.from_currency.strip().upper() != price_ccy or fx.to_currency.strip().upper() != base_ccy:
        raise ControlFailure("FX snapshot currencies do not bind price currency to portfolio base currency")
    if fx.freshness_status != FreshnessStatus.FRESH:
        raise ControlFailure("FX snapshot is STALE")
    dt = decision_time if decision_time.tzinfo else decision_time.replace(tzinfo=timezone.utc)
    fa = fx.as_of if fx.as_of.tzinfo else fx.as_of.replace(tzinfo=timezone.utc)
    if (fa - dt).total_seconds() > 60:
        raise ControlFailure("FX timestamp is materially in the future")
    age_hours = (dt - fa).total_seconds() / 3600.0
    if age_hours > max_age_hours:
        raise ControlFailure("FX snapshot is too old to be accepted as FRESH")


def validate_revisit_triggers(underwriting: CandidateUnderwriting, decision_time: datetime) -> None:
    t = underwriting.revisit_triggers
    if t is None:
        raise ControlFailure("Missing revisit triggers")
    if not t.price_trigger_description.strip():
        raise ControlFailure("Price revisit trigger description is required")
    dt = decision_time if decision_time.tzinfo else decision_time.replace(tzinfo=timezone.utc)
    tt = t.time_trigger_at if t.time_trigger_at.tzinfo else t.time_trigger_at.replace(tzinfo=timezone.utc)
    if tt <= dt:
        raise ControlFailure("Time revisit trigger is already due/expired; fresh review required")


def validate_funding_pocket(
    portfolio: PortfolioSnapshot,
    *,
    require_verified_constraints: bool,
    human_accepts_unverified: bool = False,
) -> None:
    p = portfolio.funding_pocket
    if not p.constraints_supplied:
        raise ControlFailure("Portfolio constraints not supplied")
    if p.deployable_amount <= 0:
        raise ControlFailure("No deployable funding capacity")
    statuses = (p.tax_status, p.liquidity_status, p.execution_status)
    if require_verified_constraints and any(s != VerificationStatus.VERIFIED for s in statuses):
        if not human_accepts_unverified:
            raise ControlFailure("Tax/liquidity/execution are UNVERIFIED; human acceptance required")


def funding_constraint_state(portfolio: PortfolioSnapshot) -> VerificationStatus:
    p = portfolio.funding_pocket
    statuses = (p.tax_status, p.liquidity_status, p.execution_status)
    if p.constraints_supplied and all(s == VerificationStatus.VERIFIED for s in statuses):
        return VerificationStatus.VERIFIED
    return VerificationStatus.UNVERIFIED


def validate_position_proposal(position: PositionProposal, portfolio: PortfolioSnapshot) -> None:
    if position.proposed_increment_weight <= 0 or position.proposed_increment_dollars <= 0:
        raise ControlFailure("Proposed increment must be positive")
    if position.post_trade_weight < position.current_weight:
        raise ControlFailure("ADD/STARTER proposal cannot reduce post-trade weight")
    if position.capacity_status == CapacityStatus.UNVERIFIED:
        raise ControlFailure("Capacity is UNVERIFIED")
    if position.capacity_status == CapacityStatus.CONSTRAINED:
        raise ControlFailure("Capacity is CONSTRAINED")

    expected_post_total = (
        portfolio.total_value + position.proposed_increment_dollars
        if position.funding_mode == FundingMode.EXTERNAL_NEW_CAPITAL
        else portfolio.total_value
    )
    if abs(position.post_trade_portfolio_value - expected_post_total) > max(1.0, expected_post_total * 1e-9):
        raise ControlFailure("Post-trade portfolio value inconsistent with funding mode")

    current_dollars = position.current_weight * portfolio.total_value
    expected_post_weight = (current_dollars + position.proposed_increment_dollars) / expected_post_total
    expected_increment_weight = position.proposed_increment_dollars / expected_post_total
    if abs(position.post_trade_weight - expected_post_weight) > 1e-6:
        raise ControlFailure("Post-trade weight does not reconcile to dollars")
    if abs(position.proposed_increment_weight - expected_increment_weight) > 1e-6:
        raise ControlFailure("Increment weight does not reconcile to dollars")

    if position.funding_mode in {FundingMode.INTERNAL_CASH, FundingMode.EXTERNAL_NEW_CAPITAL}:
        if position.proposed_increment_dollars > portfolio.funding_pocket.deployable_amount + 1e-6:
            raise ControlFailure("Increment exceeds deployable funding pocket")
    if position.remaining_capacity is not None and position.proposed_increment_weight > position.remaining_capacity + 1e-12:
        raise ControlFailure("Increment exceeds remaining portfolio-specific capacity")


def translate_weight_to_dollars(portfolio_value: float, weight: float) -> float:
    if not math.isfinite(portfolio_value) or portfolio_value <= 0:
        raise ControlFailure("Portfolio value must be positive")
    if not math.isfinite(weight) or weight < 0 or weight > 1:
        raise ControlFailure("Weight must be between 0 and 1")
    return portfolio_value * weight


def validate_required_alternatives(alternatives: Sequence[ComparisonAlternative]) -> None:
    types = {a.alternative_type for a in alternatives}
    required = {AlternativeType.BETA, AlternativeType.TREASURY_CASH, AlternativeType.DO_NOTHING}
    missing = required - types
    if missing:
        raise ControlFailure(f"Missing required Stage 7 alternatives: {', '.join(sorted(x.value for x in missing))}")
    for required_type in required:
        count = sum(a.alternative_type == required_type for a in alternatives)
        if count != 1:
            raise ControlFailure(f"Stage 7 requires exactly one {required_type.value} alternative; found {count}")

    cash = next(a for a in alternatives if a.alternative_type == AlternativeType.TREASURY_CASH)
    if cash.return_band is not None:
        if cash.market_reference is None:
            raise ControlFailure("Treasury/Cash return band requires a bound market reference")
        if cash.market_reference.freshness_status != FreshnessStatus.FRESH:
            raise ControlFailure("Treasury/Cash market reference is STALE")
        if cash.duration_match_status != VerificationStatus.VERIFIED:
            raise ControlFailure("Treasury/Cash duration/reinvestment comparability is UNVERIFIED")
        if not cash.notes or not all(str(note).strip() for note in cash.notes):
            raise ControlFailure("Treasury/Cash return band requires explicit duration/reinvestment basis notes")

    beta = next(a for a in alternatives if a.alternative_type == AlternativeType.BETA)
    if beta.return_band is not None and (not beta.notes or not all(str(note).strip() for note in beta.notes)):
        raise ControlFailure("Beta return band requires explicit basis/provenance notes")


def validate_alternative_reference_times(
    alternatives: Sequence[ComparisonAlternative],
    decision_time: datetime,
    *,
    max_age_hours: float = 96.0,
) -> None:
    dt = decision_time if decision_time.tzinfo else decision_time.replace(tzinfo=timezone.utc)
    for alt in alternatives:
        ref = alt.market_reference
        if ref is None:
            continue
        ra = ref.as_of if ref.as_of.tzinfo else ref.as_of.replace(tzinfo=timezone.utc)
        if (ra - dt).total_seconds() > 60:
            raise ControlFailure(f"{alt.label} market reference timestamp is materially in the future")
        age_hours = (dt - ra).total_seconds() / 3600.0
        if age_hours > max_age_hours:
            raise ControlFailure(f"{alt.label} market reference is too old to be accepted as FRESH")


def validate_recycle_policy(portfolio: PortfolioSnapshot, alternatives: Sequence[ComparisonAlternative]) -> None:
    has_recycle = any(a.alternative_type == AlternativeType.RECYCLE for a in alternatives)
    if portfolio.trims_permitted and not has_recycle:
        raise ControlFailure("Trims permitted but no recycle-from-holdings comparison is present")
    if portfolio.add_only_policy and has_recycle:
        raise ControlFailure("Recycle comparison present despite ADD-ONLY POLICY")


def _normalized_driver_set(c: CandidateUnderwriting) -> set[str]:
    return {" ".join(x.lower().split()) for x in c.dominant_drivers}


def validate_common_driver_cluster(candidates: Sequence[CandidateUnderwriting], cluster_note: str | None) -> None:
    if len(candidates) <= 1:
        return
    driver_sets = [_normalized_driver_set(c) for c in candidates]
    shared: set[str] = set()
    for i, left in enumerate(driver_sets):
        for right in driver_sets[i + 1 :]:
            shared |= left & right
    if shared and not (cluster_note and cluster_note.strip()):
        raise ControlFailure("Shared economic drivers require a cluster note for multi-name funding")


def evaluate_stage7_candidate(
    underwriting: CandidateUnderwriting,
    portfolio: PortfolioSnapshot,
    position: PositionProposal | None,
    alternatives: Sequence[ComparisonAlternative],
    decision_time: datetime,
    *,
    human_accepts_unverified_constraints: bool = False,
    known_latest_session_date: date | None = None,
    max_reference_age_hours: float = 96.0,
) -> Stage7CandidateResult:
    try:
        validate_price_snapshot(underwriting, decision_time, known_latest_session_date=known_latest_session_date)
        validate_fx_binding(underwriting, portfolio, decision_time, max_age_hours=max_reference_age_hours)
        validate_period_granularity(underwriting.fundamentals)
    except ControlFailure as e:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", (str(e),), position)

    eligible, eligibility_reasons = validate_opportunity_eligibility(underwriting)
    if not eligible:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "WATCH / NO DECISION", eligibility_reasons, position)
    try:
        validate_revisit_triggers(underwriting, decision_time)
    except ControlFailure as e:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "WATCH / NO DECISION", (str(e),), position)
    if any(u.block_flag == BlockFlag.YES for u in underwriting.uncertainties):
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", ("blocking uncertainty present",), position)

    try:
        validate_required_alternatives(alternatives)
        validate_alternative_reference_times(alternatives, decision_time, max_age_hours=max_reference_age_hours)
        validate_recycle_policy(portfolio, alternatives)
    except ControlFailure as e:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", (str(e),), position)

    if position is None:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", ("missing position proposal",), position)
    if position.capacity_status == CapacityStatus.UNVERIFIED:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", ("Capacity is UNVERIFIED",), position)
    if position.capacity_status == CapacityStatus.CONSTRAINED:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", ("Capacity is CONSTRAINED",), position)

    overlap_status = None
    beta = next((a for a in alternatives if a.alternative_type == AlternativeType.BETA), None)
    cash = next((a for a in alternatives if a.alternative_type == AlternativeType.TREASURY_CASH), None)
    if beta and beta.security_key and beta.security_key.startswith("ETF:"):
        if beta.overlap is None:
            return Stage7CandidateResult(
                underwriting.security_key,
                underwriting.ticker,
                "BLOCKED",
                ("ETF beta alternative requires explicit MEASURED/UNMEASURED overlap status",),
                position,
            )
        if beta.overlap.candidate_security_key != underwriting.security_key:
            return Stage7CandidateResult(
                underwriting.security_key,
                underwriting.ticker,
                "BLOCKED",
                ("ETF overlap record is bound to a different candidate security",),
                position,
            )
        overlap_status = beta.overlap.status
        try:
            validate_etf_overlap(beta.overlap, comparison_depends_on_diversification=False)
        except ControlFailure as e:
            return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", (str(e),), position)

    reasons: list[str] = []
    if not range_clearly_better(underwriting.return_band, cash.return_band if cash else None):
        reasons.append("DOES NOT CLEAR CASH/TREASURY RETURN BAND")
    if not range_clearly_better(underwriting.return_band, beta.return_band if beta else None):
        reasons.append("DOES NOT CLEAR BETA RETURN BAND")
    if reasons:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "NOT DISTINGUISHABLE", tuple(reasons), position)

    try:
        validate_funding_pocket(
            portfolio,
            require_verified_constraints=True,
            human_accepts_unverified=human_accepts_unverified_constraints,
        )
        validate_position_proposal(position, portfolio)
    except ControlFailure as e:
        return Stage7CandidateResult(underwriting.security_key, underwriting.ticker, "BLOCKED", (str(e),), position)

    constraint_state = funding_constraint_state(portfolio)
    final_reasons = ["security bar and comparison gates cleared; funding remains human"]
    if overlap_status == OverlapStatus.UNMEASURED:
        final_reasons.append("UNMEASURED_OVERLAP — no portfolio-fit credit assigned")
    return Stage7CandidateResult(
        underwriting.security_key,
        underwriting.ticker,
        "ELIGIBLE FOR STAGE 8",
        tuple(final_reasons),
        position,
        constraint_state=constraint_state,
        overlap_status=overlap_status,
    )
