"""
Core database models for Atlas: Equities.

Follows strict separation of FACT, ASSUMPTION, CALCULATION, JUDGMENT, DECISION, PORTFOLIO_ACTION.
Implements bitemporal architecture (effective_date, known_date).
No silent overwrites. All conflicts recorded.
"""

from datetime import datetime
from typing import Optional
from enum import Enum
import json

# ============================================================================
# ENUMS
# ============================================================================

class SecurityIdentityStatus(str, Enum):
    """Status of security identity resolution."""
    UNVERIFIED = "UNVERIFIED"  # Identity not yet verified (initial state)
    VERIFIED = "VERIFIED"
    AMBIGUOUS = "AMBIGUOUS"  # Evidence exists but identity cannot be resolved cleanly
    INACTIVE = "INACTIVE"
    CORPORATE_ACTION_PENDING = "CORPORATE_ACTION_PENDING"


class EvidenceClass(str, Enum):
    """Classification of evidence origin and nature."""
    REPORTED_FACT = "REPORTED_FACT"
    MARKET_FACT = "MARKET_FACT"
    MANAGEMENT_GUIDANCE = "MANAGEMENT_GUIDANCE"
    MANAGEMENT_CLAIM = "MANAGEMENT_CLAIM"
    MARKET_EXPECTATION = "MARKET_EXPECTATION"
    ATLAS_ASSUMPTION = "ATLAS_ASSUMPTION"
    DERIVED_CALCULATION = "DERIVED_CALCULATION"
    QUALITATIVE_EVIDENCE = "QUALITATIVE_EVIDENCE"
    EXTERNAL_CLAIM = "EXTERNAL_CLAIM"
    NARRATIVE = "NARRATIVE"


class VerificationStatus(str, Enum):
    """Verification status of evidence."""
    UNVERIFIED = "UNVERIFIED"
    DISCOVERED = "DISCOVERED"
    CORROBORATED = "CORROBORATED"
    PRIMARY_VERIFIED = "PRIMARY_VERIFIED"
    CONFLICTED = "CONFLICTED"
    REJECTED = "REJECTED"
    STALE = "STALE"


class DecisionAuthority(str, Enum):
    """Authority tier for decision-making."""
    DA0 = "DA0"  # No decision authority
    DA1 = "DA1"  # Research / trigger only
    DA2 = "DA2"  # Supporting evidence
    DA3 = "DA3"  # Approved calculation input
    DA4 = "DA4"  # Primary fact / hard policy


class DataQualityRating(str, Enum):
    """Overall data quality assessment."""
    HIGH = "HIGH"
    ACCEPTABLE = "ACCEPTABLE"
    WEAK = "WEAK"
    UNUSABLE = "UNUSABLE"


class ConflictType(str, Enum):
    """Type of evidence conflict."""
    SOURCE_DISAGREEMENT = "SOURCE_DISAGREEMENT"
    PERIOD_MISMATCH = "PERIOD_MISMATCH"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    RESTATEMENT = "RESTATEMENT"
    XBRL_MAPPING_CONFLICT = "XBRL_MAPPING_CONFLICT"
    SHARE_COUNT_CONFLICT = "SHARE_COUNT_CONFLICT"
    CORPORATE_ACTION_CONFLICT = "CORPORATE_ACTION_CONFLICT"
    TIMESTAMP_CONFLICT = "TIMESTAMP_CONFLICT"


class ProviderStatus(str, Enum):
    """Health status of external data provider."""
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class PeriodType(str, Enum):
    """Type of financial period."""
    QUARTER = "QUARTER"
    TTM = "TTM"
    FISCAL_YEAR = "FISCAL_YEAR"


class FinancialFieldUnit(str, Enum):
    """Units for financial fields."""
    CURRENCY = "CURRENCY"
    SHARES = "SHARES"
    RATIO = "RATIO"
    PERCENTAGE = "PERCENTAGE"
    COUNT = "COUNT"


# ============================================================================
# SECURITY IDENTITY
# ============================================================================

class SecurityIdentity:
    """
    Canonical security representation.
    Ticker is NOT the permanent identity.
    Ticker changes preserved via corporate actions.
    """

    security_id: str                           # Permanent UUID
    issuer_id: str                             # Issuer UUID

    company_name: str
    ticker: str
    exchange: str

    security_type: str                         # Equity, ADR, etc.
    share_class: str                           # Class A, Class B, etc.

    cik: str                                   # SEC CIK

    currency: str                              # USD, etc.
    country: str                               # US, etc.

    fiscal_year_end: str                       # MM-DD

    primary_listing: bool
    adr_status: Optional[str]

    listing_status: str                        # ACTIVE, DELISTED, etc.

    status: SecurityIdentityStatus

    effective_from: datetime
    effective_to: Optional[datetime]

    created_at: datetime
    updated_at: datetime


# ============================================================================
# EVIDENCE LAYER
# ============================================================================

class EvidenceRecord:
    """
    Immutable record of raw evidence.
    Never mutate. New evidence = new record.
    """

    evidence_id: str                           # UUID
    security_id: str                           # FK to SecurityIdentity

    field_name: str                            # e.g., "revenue"

    raw_value: Optional[str]                   # As reported
    normalized_value: Optional[float]          # Normalized

    unit: str                                  # e.g., "USD millions"

    # Bitemporal
    period_start: Optional[datetime]           # e.g., Q1 start
    period_end: Optional[datetime]             # e.g., Q1 end

    effective_date: datetime                   # When economically applies
    known_date: datetime                       # When Atlas learned of it

    # Source
    source_type: str                           # SEC, MARKET_DATA, MACRO, etc.
    source_tier: DecisionAuthority

    source_name: str                           # e.g., "SEC"
    source_identifier: str                     # e.g., accession number
    source_url: Optional[str]

    publication_date: Optional[datetime]
    retrieved_at: datetime

    # Classification
    evidence_class: EvidenceClass
    verification_status: VerificationStatus

    # Parser/schema versioning
    parser_version: str
    schema_version: str

    # Timestamps
    created_at: datetime


# ============================================================================
# NORMALIZED & CANONICAL FACTS
# ============================================================================

class CanonicalFact:
    """
    Validated and normalized fact available to calculations.
    Produced from EvidenceRecord(s) via SourceAuthorityRegistry.
    """

    canonical_fact_id: str                     # UUID
    security_id: str
    field_name: str

    value: float
    unit: str

    period: PeriodType
    effective_date: datetime
    known_date: datetime

    primary_evidence_id: str                   # FK to EvidenceRecord
    secondary_evidence_ids: list[str]          # Alternative sources

    verification_status: VerificationStatus
    data_quality: DataQualityRating

    methodology_version: str
    created_at: datetime


class AssumptionRecord:
    """
    Investment assumption. Does not overwrite history.
    New assumption = new record with version.
    """

    assumption_id: str                         # UUID
    security_id: str

    metric: str                                # e.g., "revenue_growth"

    scenario: str                              # e.g., "base_case"
    forecast_period: str                       # e.g., "5y"

    value: float
    unit: str

    basis: str                                 # Justification
    supporting_evidence_ids: list[str]         # FK to EvidenceRecord

    confidence: float                          # 0.0-1.0

    created_at: datetime
    created_by: str

    methodology_version: str
    supersedes_assumption_id: Optional[str]    # Version chain


# ============================================================================
# CALCULATION & FORMULA LAYER
# ============================================================================

class FormulaRegistry:
    """
    Explicit identity and version for all deterministic formulas.
    Immutable. New methodology = new version.
    """

    formula_id: str                            # e.g., "F_FCF_001"
    name: str                                  # e.g., "Free Cash Flow"
    version: str                               # e.g., "1.0"

    description: Optional[str]

    inputs: list[str]                          # Field names required

    expression: str                            # e.g., "cfo - capex"

    output_unit: str                           # e.g., "currency"

    effective_from: datetime
    effective_to: Optional[datetime]

    created_at: datetime


class CalculationRecord:
    """
    Record of deterministic calculation output.
    References formula version and input evidence.
    """

    calculation_id: str                        # UUID
    security_id: str

    formula_id: str                            # FK to FormulaRegistry
    formula_version: str                       # Snapshot

    output_value: float
    output_unit: str

    period: PeriodType
    effective_date: datetime
    known_date: datetime

    input_evidence_ids: list[str]              # FK to EvidenceRecord

    calculation_timestamp: datetime
    methodology_version: str


# ============================================================================
# CONFLICT & QUALITY MANAGEMENT
# ============================================================================

class EvidenceConflict:
    """
    Recorded conflict between evidence sources.
    Prevents silent overwrites.
    Requires explicit resolution.
    """

    conflict_id: str                           # UUID
    security_id: str
    field_name: str

    candidate_evidence_ids: list[str]          # FK to EvidenceRecord

    conflict_type: ConflictType

    conflict_description: str

    resolution_status: str                     # UNRESOLVED, RESOLVED, WAIVED
    resolution_rule: Optional[str]             # Rule that resolved it
    resolved_evidence_id: Optional[str]        # Winning evidence

    created_at: datetime
    resolved_at: Optional[datetime]


class DataQualityAssessment:
    """
    Explicit data quality evaluation.
    Not a vague estimate. Scored and componentized.
    """

    quality_id: str                            # UUID
    fact_reference: str                        # FK to CanonicalFact or similar

    # Components
    source_authority_score: float               # 0.0-1.0
    verification_score: float                  # 0.0-1.0
    freshness_score: float                     # 0.0-1.0
    period_match_score: float                  # 0.0-1.0
    cross_source_agreement: float               # 0.0-1.0
    parser_confidence: float                   # 0.0-1.0

    # Overall rating
    overall_rating: DataQualityRating

    # Notes
    concerns: list[str]
    recommendations: list[str]

    evaluated_at: datetime
    reviewed_by: Optional[str]


# ============================================================================
# SOURCE & PROVIDER MANAGEMENT
# ============================================================================

class SourceAuthorityRegistry:
    """
    Defines source precedence and requirements for each field.
    NOT hardcoded. Queryable registry.
    """

    registry_id: str                           # UUID

    field_name: str                            # e.g., "revenue"
    atlas_object: str                          # e.g., "FinancialState"

    primary_source: str                        # e.g., "SEC"
    secondary_source: Optional[str]
    fallback_source: Optional[str]

    minimum_decision_authority: DecisionAuthority

    verification_requirement: VerificationStatus

    point_in_time_required: bool

    normalization_rule: str                    # e.g., "REVENUE_CANONICAL_V1"

    effective_from: datetime
    effective_to: Optional[datetime]

    created_at: datetime


class FreshnessPolicyRegistry:
    """
    Defines freshness requirements for each data element.
    Determines when data becomes stale.
    """

    policy_id: str                             # UUID

    field_name: str
    atlas_object: str

    maximum_age_hours: int                     # e.g., 24

    acceptable_age_hours: Optional[int]        # Warning threshold

    source_type: str                           # SEC, MARKET_DATA, MACRO, etc.

    effective_from: datetime
    effective_to: Optional[datetime]

    created_at: datetime


class ProviderHealth:
    """
    Health monitoring for external data providers.
    Detects degradation, outages, issues.
    """

    health_id: str                             # UUID

    provider_name: str                         # e.g., "Massive", "SEC", "FRED"
    provider_type: str                         # MARKET_DATA, SEC, MACRO, etc.

    status: ProviderStatus

    last_success: Optional[datetime]
    last_error: Optional[datetime]
    last_error_message: Optional[str]

    error_rate_24h: float                      # 0.0-1.0
    latency_ms_p95: Optional[float]
    latency_ms_p99: Optional[float]

    last_validation: Optional[datetime]

    notes: Optional[str]

    updated_at: datetime


# ============================================================================
# FREEZE INFRASTRUCTURE
# ============================================================================

class EvidenceFreeze:
    """
    Immutable snapshot of evidence state at a point in time.
    Includes manifest, hashes, and reproducibility metadata.
    """

    freeze_id: str                             # UUID
    security_id: str

    # Manifest
    security_identity_version: str
    evidence_manifest: dict                    # List of evidence_ids and hashes
    canonical_facts_manifest: dict             # List of fact_ids and values
    formula_registry_version: str
    source_authority_version: str

    # Hash & verification
    canonical_serialization: str               # Deterministic JSON
    freeze_hash: str                           # SHA-256

    # Metadata
    atlas_version: str
    schema_version: str
    timestamp: datetime

    created_by: Optional[str]
    notes: Optional[str]

    # Audit
    created_at: datetime


class DecisionFreeze:
    """
    (Sprint 2+) Immutable snapshot of investment decision state.
    """
    pass


class PortfolioFreeze:
    """
    (Sprint 2+) Immutable snapshot of portfolio state at a point in time.
    """
    pass


# ============================================================================
# FINANCIAL STATEMENTS
# ============================================================================

class FinancialState:
    """
    Canonical financial state for a security.
    Stores facts as CanonicalFacts, not here.
    This is a view/aggregation class.
    """

    financial_state_id: str                    # UUID
    security_id: str

    period_type: PeriodType
    period_start: datetime
    period_end: datetime

    # Income Statement
    revenue: Optional[float]
    gross_profit: Optional[float]
    operating_income: Optional[float]
    pretax_income: Optional[float]
    taxes: Optional[float]
    net_income: Optional[float]
    basic_eps: Optional[float]
    diluted_eps: Optional[float]

    # Cash Flow
    cash_from_operations: Optional[float]
    capex: Optional[float]
    fcf: Optional[float]                       # Calculated
    sbc: Optional[float]
    share_repurchases: Optional[float]
    dividends: Optional[float]

    # Balance Sheet
    cash: Optional[float]
    marketable_securities: Optional[float]
    short_term_debt: Optional[float]
    long_term_debt: Optional[float]
    shareholders_equity: Optional[float]

    # Shares
    weighted_average_diluted_shares: Optional[float]
    period_end_shares: Optional[float]

    # Quality/metadata
    data_quality: DataQualityRating
    effective_date: datetime
    known_date: datetime

    created_at: datetime


# ============================================================================
# MARKET DATA
# ============================================================================

class MarketState:
    """
    Current or recent market data for a security.
    """

    market_state_id: str                       # UUID
    security_id: str

    timestamp: datetime

    price: Optional[float]
    previous_close: Optional[float]

    volume: Optional[int]

    market_session: str                        # REGULAR, EXTENDED, etc.

    price_source: str                          # Massive, etc.
    price_raw: bool                            # AS_TRADED vs ADJUSTED

    provider_status: ProviderStatus
    freshness_hours: float

    created_at: datetime


# ============================================================================
# MACRO DATA
# ============================================================================

class MacroDataPoint:
    """
    Single macroeconomic data point from FRED or similar.
    Supports ALFRED historical vintages later.
    """

    macro_id: str                              # UUID

    series_id: str                             # e.g., "DFF", "DGS10", "TB3MS"
    series_name: str

    value: float

    effective_date: datetime                   # When the value is economically applicable
    known_date: datetime                       # When published/known

    publication_date: datetime
    retrieved_at: datetime

    source: str                                # FRED, etc.
    source_url: Optional[str]

    unit: str
    frequency: str                             # DAILY, MONTHLY, etc.

    created_at: datetime


# ============================================================================
# RESEARCH EVENTS (Grok Foundation)
# ============================================================================

class ResearchEvent:
    """
    Foundation for research/discovery.
    Grok integration comes later.
    Enforced noise firewall: cannot directly populate FinancialState, ValuationState, etc.
    """

    research_id: str                           # UUID
    security_id: str

    event_type: str                            # Discovery, Catalyst, Risk, etc.
    summary: str

    claim_class: EvidenceClass                 # EXTERNAL_CLAIM, NARRATIVE, etc.
    source_tier: DecisionAuthority

    publication_date: datetime
    effective_date: Optional[datetime]

    verification_status: VerificationStatus

    materiality: str                           # HIGH, MEDIUM, LOW
    impact_class: str                          # INTRINSIC_VALUE, RISK, NARRATIVE_ONLY, etc.

    affected_objects: list[str]                # Fields potentially affected

    recommended_action: str

    created_at: datetime


# ============================================================================
# VERSION & AUDIT
# ============================================================================

class AtlasVersion:
    """Version tracking for system components."""

    version_id: str
    component: str                             # "atlas_core", "formulas", etc.
    version_number: str

    description: Optional[str]

    released_at: datetime
    created_at: datetime


class AuditTrail:
    """Audit record for important writes."""

    audit_id: str                              # UUID

    record_type: str                           # EvidenceRecord, CanonicalFact, etc.
    record_id: str

    action: str                                # CREATE, UPDATE, DELETE

    previous_value: Optional[dict]
    new_value: dict

    timestamp: datetime
    process: str                               # Process/user responsible
    reason: Optional[str]

    created_at: datetime
