from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from enum import Enum
import math
from typing import Optional


class SecurityDecision(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    WATCH = "WATCH"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    REJECT = "REJECT"
    NO_DECISION = "NO DECISION"


class PortfolioAction(str, Enum):
    INITIATE = "INITIATE"
    ADD = "ADD"
    HOLD = "HOLD"
    TRIM = "TRIM"
    EXIT = "EXIT"
    ROTATE = "ROTATE"
    HOLD_CASH = "HOLD CASH"
    REVIEW = "REVIEW"
    DO_NOTHING = "DO NOTHING"


class ReviewEventType(str, Enum):
    TRIGGER_REVIEW = "TRIGGER_REVIEW"
    PRICE_ONLY_CHANGE = "PRICE_ONLY_CHANGE"
    PORTFOLIO_ONLY_CHANGE = "PORTFOLIO_ONLY_CHANGE"
    THESIS_CHANGE = "THESIS_CHANGE"
    FINAL_CAPITAL_DECISION = "FINAL_CAPITAL_DECISION"
    ROUTINE_REAFFIRMATION = "ROUTINE_REAFFIRMATION"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"


class PriceMode(str, Enum):
    COMPLETED_SESSION = "COMPLETED_SESSION"
    EXECUTABLE_INTRADAY = "EXECUTABLE_INTRADAY"


class OverlapStatus(str, Enum):
    MEASURED = "MEASURED"
    UNMEASURED = "UNMEASURED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class CapacityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    CONSTRAINED = "CONSTRAINED"
    UNVERIFIED = "UNVERIFIED"


class PositionClassification(str, Enum):
    STARTER = "STARTER"
    ADD = "ADD"
    OTHER = "OTHER"


class BlockFlag(str, Enum):
    YES = "YES"
    NO = "NO"


class UnderwritingGateStatus(str, Enum):
    CLEAR = "CLEAR"
    MARGINAL = "MARGINAL"
    FAIL = "FAIL"
    UNVERIFIED = "UNVERIFIED"


class PeriodGranularity(str, Enum):
    QUARTER = "QUARTER"
    YTD = "YTD"
    TTM = "TTM"
    ANNUAL = "ANNUAL"
    POINT_IN_TIME = "POINT_IN_TIME"
    OTHER = "OTHER"


class AlternativeType(str, Enum):
    CANDIDATE = "CANDIDATE"
    BETA = "BETA"
    TREASURY_CASH = "TREASURY_CASH"
    DO_NOTHING = "DO_NOTHING"
    RECYCLE = "RECYCLE"


class FundingMode(str, Enum):
    INTERNAL_CASH = "INTERNAL_CASH"
    EXTERNAL_NEW_CAPITAL = "EXTERNAL_NEW_CAPITAL"
    RECYCLE = "RECYCLE"


@dataclass(frozen=True)
class MarketReferenceSnapshot:
    reference_key: str
    value: float
    as_of: datetime
    provider: str
    freshness_status: FreshnessStatus
    currency: Optional[str] = None

    def __post_init__(self):
        if not self.reference_key.strip():
            raise ValueError("reference_key is required")
        if not math.isfinite(self.value):
            raise ValueError("MarketReferenceSnapshot.value must be finite")
        if not self.provider.strip():
            raise ValueError("MarketReferenceSnapshot.provider is required")


@dataclass(frozen=True)
class FXSnapshot:
    from_currency: str
    to_currency: str
    rate: float
    as_of: datetime
    provider: str
    freshness_status: FreshnessStatus

    def __post_init__(self):
        if not self.from_currency.strip() or not self.to_currency.strip():
            raise ValueError("FX currencies are required")
        if not math.isfinite(self.rate) or self.rate <= 0:
            raise ValueError("FX rate must be finite and positive")
        if not self.provider.strip():
            raise ValueError("FX provider is required")


@dataclass(frozen=True)
class ReturnBand:
    low: float
    high: float
    horizon_years: float = 3.0

    def __post_init__(self):
        if not all(math.isfinite(x) for x in (self.low, self.high, self.horizon_years)):
            raise ValueError("ReturnBand values must be finite")
        if self.low > self.high:
            raise ValueError("ReturnBand.low cannot exceed high")
        if self.horizon_years <= 0:
            raise ValueError("horizon_years must be positive")

    def overlaps(self, other: "ReturnBand") -> bool:
        return max(self.low, other.low) <= min(self.high, other.high)


@dataclass(frozen=True)
class PriceSnapshot:
    security_key: str
    ticker: str
    price: float
    price_as_of: datetime
    price_session_date: date
    latest_completed_session_date: date
    currency: str
    provider: str
    market_session_status: str
    adjusted: bool
    freshness_status: FreshnessStatus
    price_mode: PriceMode = PriceMode.COMPLETED_SESSION
    quoted_security_key: Optional[str] = None
    quoted_instrument: Optional[str] = None

    def __post_init__(self):
        if not math.isfinite(self.price) or self.price <= 0:
            raise ValueError("price must be positive")


@dataclass(frozen=True)
class FundamentalObservation:
    field_name: str
    value: float | str
    period_granularity: PeriodGranularity
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    source: Optional[str] = None
    normalized_to: Optional[PeriodGranularity] = None
    normalization_basis: Optional[str] = None


@dataclass(frozen=True)
class TypedUncertainty:
    uncertainty_type: str
    description: str
    block_flag: BlockFlag


@dataclass(frozen=True)
class RevisitTriggers:
    price_trigger_description: str
    time_trigger_at: datetime
    thesis_trigger_description: Optional[str] = None


@dataclass(frozen=True)
class ETFOverlap:
    etf_ticker: str
    candidate_security_key: str
    status: OverlapStatus
    lookthrough_weight: Optional[float] = None
    source: Optional[str] = None
    as_of: Optional[datetime] = None


@dataclass(frozen=True)
class Holding:
    security_key: str
    ticker: str
    market_value: float
    weight: float
    account: str
    account_type: str
    cost_basis: Optional[float] = None
    currency: str = "USD"
    dominant_drivers: tuple[str, ...] = ()

    def __post_init__(self):
        if not math.isfinite(self.market_value) or self.market_value < 0:
            raise ValueError("market_value cannot be negative")
        if not math.isfinite(self.weight) or not 0 <= self.weight <= 1:
            raise ValueError("weight must be between 0 and 1")
        if self.cost_basis is not None and (not math.isfinite(self.cost_basis) or self.cost_basis < 0):
            raise ValueError("cost_basis must be finite and non-negative when supplied")


@dataclass(frozen=True)
class FundingPocket:
    account: str
    account_type: str
    amount: float
    t_plus_1_deployable: bool
    required_liquidity_reservation: float = 0.0
    constraints_supplied: bool = False
    tax_status: VerificationStatus = VerificationStatus.UNVERIFIED
    liquidity_status: VerificationStatus = VerificationStatus.UNVERIFIED
    execution_status: VerificationStatus = VerificationStatus.UNVERIFIED

    def __post_init__(self):
        if not math.isfinite(self.amount) or self.amount < 0:
            raise ValueError("FundingPocket.amount cannot be negative")
        if not math.isfinite(self.required_liquidity_reservation) or self.required_liquidity_reservation < 0:
            raise ValueError("required_liquidity_reservation cannot be negative")

    @property
    def deployable_amount(self) -> float:
        if not self.t_plus_1_deployable:
            return 0.0
        return max(0.0, self.amount - self.required_liquidity_reservation)


@dataclass(frozen=True)
class PortfolioSnapshot:
    snapshot_id: str
    as_of: datetime
    total_value: float
    holdings: tuple[Holding, ...]
    funding_pocket: FundingPocket
    trims_permitted: bool
    add_only_policy: bool = False
    base_currency: str = "USD"

    def __post_init__(self):
        if not math.isfinite(self.total_value) or self.total_value <= 0:
            raise ValueError("total_value must be positive")
        if self.trims_permitted and self.add_only_policy:
            raise ValueError("trims_permitted and add_only_policy cannot both be true")
        if not self.base_currency.strip():
            raise ValueError("base_currency is required")


@dataclass(frozen=True)
class PositionProposal:
    current_weight: float
    proposed_increment_weight: float
    proposed_increment_dollars: float
    post_trade_portfolio_value: float
    post_trade_weight: float
    classification: PositionClassification
    capacity_status: CapacityStatus
    remaining_capacity: Optional[float]
    funding_source: str
    funding_mode: FundingMode
    sensitivity_weights: tuple[float, ...] = (0.01, 0.03, 0.05, 0.10)

    def __post_init__(self):
        numeric = (
            self.current_weight,
            self.proposed_increment_weight,
            self.proposed_increment_dollars,
            self.post_trade_portfolio_value,
            self.post_trade_weight,
        )
        if not all(math.isfinite(x) for x in numeric):
            raise ValueError("PositionProposal numeric fields must be finite")
        if not 0 <= self.current_weight <= 1:
            raise ValueError("current_weight must be between 0 and 1")
        if not 0 <= self.proposed_increment_weight <= 1:
            raise ValueError("proposed_increment_weight must be between 0 and 1")
        if not 0 <= self.post_trade_weight <= 1:
            raise ValueError("post_trade_weight must be between 0 and 1")
        if self.proposed_increment_dollars <= 0:
            raise ValueError("proposed_increment_dollars must be positive")
        if self.post_trade_portfolio_value <= 0:
            raise ValueError("post_trade_portfolio_value must be positive")
        if self.remaining_capacity is not None and (not math.isfinite(self.remaining_capacity) or self.remaining_capacity < 0):
            raise ValueError("remaining_capacity cannot be negative")
        if not self.funding_source.strip():
            raise ValueError("funding_source is required")
        if any(not math.isfinite(w) or w <= 0 or w > 1 for w in self.sensitivity_weights):
            raise ValueError("sensitivity_weights must be in (0, 1]")


@dataclass(frozen=True)
class CandidateUnderwriting:
    security_key: str
    ticker: str
    security_decision: SecurityDecision
    price_snapshot: PriceSnapshot
    observable_regime: str
    observable_regime_evidence: tuple[str, ...]
    atlas_variant: str
    variant_evidence: tuple[str, ...]
    return_band: Optional[ReturnBand]
    return_band_basis: tuple[str, ...]
    required_return_band: Optional[ReturnBand]
    underwriting_gate_status: UnderwritingGateStatus
    uncertainties: tuple[TypedUncertainty, ...]
    dominant_drivers: tuple[str, ...]
    revisit_triggers: Optional[RevisitTriggers]
    fundamentals: tuple[FundamentalObservation, ...] = ()
    underwriting_provenance: tuple[str, ...] = ()
    return_currency: str = "USD"
    fx_snapshot: Optional[FXSnapshot] = None


@dataclass(frozen=True)
class ComparisonAlternative:
    alternative_type: AlternativeType
    label: str
    return_band: Optional[ReturnBand] = None
    security_key: Optional[str] = None
    overlap: Optional[ETFOverlap] = None
    notes: tuple[str, ...] = ()
    market_reference: Optional[MarketReferenceSnapshot] = None
    duration_match_status: VerificationStatus = VerificationStatus.UNVERIFIED


@dataclass(frozen=True)
class Stage7CandidateResult:
    security_key: str
    ticker: str
    status: str
    reasons: tuple[str, ...]
    position: Optional[PositionProposal]
    constraint_state: VerificationStatus = VerificationStatus.UNVERIFIED
    overlap_status: Optional[OverlapStatus] = None
    comparison_header: str = "COMPARISON AID — NO PORTFOLIO ACTION — STAGE 8 OPEN"


@dataclass(frozen=True)
class FrozenInputRef:
    version: str
    sha256: str
    artifact_path: Optional[str] = None

    def __post_init__(self):
        if not self.version.strip():
            raise ValueError("FrozenInputRef.version is required")
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256.lower()):
            raise ValueError("FrozenInputRef.sha256 must be a 64-character hex digest")
        if self.artifact_path is not None and not self.artifact_path.strip():
            raise ValueError("FrozenInputRef.artifact_path cannot be blank")


@dataclass(frozen=True)
class InputVersions:
    portfolio_snapshot: FrozenInputRef
    scenario_model: FrozenInputRef
    exposure_map: FrozenInputRef
    evidence_set: FrozenInputRef
    control_contract: FrozenInputRef


@dataclass(frozen=True)
class DecisionRecord:
    record_id: str
    created_at: datetime
    review_event_type: ReviewEventType
    candidate_security_key: Optional[str]
    portfolio_snapshot_id: str
    input_versions: InputVersions
    stage7_status: str
    stage7_reasons: tuple[str, ...]
    human_stage8_action: Optional[PortfolioAction]
    human_rationale: Optional[str]
    prior_record_id: Optional[str] = None
    revisit_triggers: Optional[RevisitTriggers] = None
    alternatives_considered: tuple[str, ...] = ()
    stage7_artifact: Optional[FrozenInputRef] = None
    constraint_state: VerificationStatus = VerificationStatus.UNVERIFIED
    dominant_drivers: tuple[str, ...] = ()
    cluster_note: Optional[str] = None
    position_classification: Optional[PositionClassification] = None
    post_trade_weight: Optional[float] = None
    starter_cap_weight: Optional[float] = None
    record_hash: Optional[str] = None

    def __post_init__(self):
        for name, value in (("post_trade_weight", self.post_trade_weight), ("starter_cap_weight", self.starter_cap_weight)):
            if value is not None and (not math.isfinite(value) or value < 0 or value > 1):
                raise ValueError(f"{name} must be finite and between 0 and 1")

    def to_dict(self) -> dict:
        return asdict(self)
