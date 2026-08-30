"""
Database configuration and SQLAlchemy ORM models.
Implements bitemporal architecture with strict separation of evidence layers.
"""

import os
import json
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    create_engine, Column, String, Float, Integer, DateTime,
    Boolean, Enum, ForeignKey, Text, JSON, Index, Table,
    event, and_, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

# Import enums from models
from models import (
    SecurityIdentityStatus, EvidenceClass, VerificationStatus,
    DecisionAuthority, DataQualityRating, ConflictType, ProviderStatus,
    PeriodType, FinancialFieldUnit
)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# SQLite in-memory for testing; PostgreSQL for production
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# SECURITY IDENTITY
# ============================================================================

class SecurityIdentityORM(Base):
    """Canonical security representation in database."""
    __tablename__ = "security_identity"

    security_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    issuer_id = Column(String(36), nullable=False)

    company_name = Column(String(255), nullable=False)
    ticker = Column(String(20), nullable=False, index=True)
    exchange = Column(String(10), nullable=False)

    security_type = Column(String(50))
    share_class = Column(String(20))

    cik = Column(String(20), index=True, nullable=False)

    currency = Column(String(3), default="USD")
    country = Column(String(2), default="US")

    fiscal_year_end = Column(String(5))  # MM-DD

    primary_listing = Column(Boolean, default=True)
    adr_status = Column(String(50), nullable=True)

    listing_status = Column(String(50), default="ACTIVE")

    status = Column(Enum(SecurityIdentityStatus), default=SecurityIdentityStatus.UNVERIFIED)

    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evidence_records = relationship("EvidenceRecordORM", back_populates="security")
    canonical_facts = relationship("CanonicalFactORM", back_populates="security")

    __table_args__ = (
        Index("ix_security_ticker_exchange", "ticker", "exchange"),
        Index("ix_security_cik", "cik"),
    )


# ============================================================================
# EVIDENCE LAYER
# ============================================================================

class EvidenceRecordORM(Base):
    """Immutable raw evidence record with timestamp precision."""
    __tablename__ = "evidence_record"

    evidence_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    field_name = Column(String(100), nullable=False)

    raw_value = Column(Text, nullable=True)
    normalized_value = Column(Float, nullable=True)

    unit = Column(String(50))

    # Bitemporal with Timezone-Aware Timestamp Precision (AMENDED + CORRECTED)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # AMENDED: Support both legacy and new timestamp fields
    # Legacy (for backward compatibility)
    effective_date = Column(DateTime, nullable=True)
    known_date = Column(DateTime, nullable=True)

    # NEW: Timezone-aware timestamp precision (required for live validation)
    # CORRECTED: SEC EDGAR timestamps are Eastern Time, not UTC

    # effective_at: When the economic event occurred (period end)
    effective_at = Column(DateTime, nullable=True)

    # SEC EDGAR Acceptance Timestamp (Eastern Time)
    raw_acceptance_datetime = Column(String(50), nullable=True)  # Raw from SEC
    source_timezone = Column(String(50), default="America/New_York")  # Explicit source

    # known_at: Normalized to UTC (timezone-aware)
    known_at = Column(DateTime, nullable=True)  # UTC timezone-aware

    # publication_at: When published by issuer (filing date)
    publication_at = Column(DateTime, nullable=True)

    # retrieved_at: When Atlas retrieved it
    retrieved_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Source
    source_type = Column(String(50), nullable=False)
    source_tier = Column(Enum(DecisionAuthority), nullable=False)

    source_name = Column(String(100), nullable=False)
    source_identifier = Column(String(255))  # e.g., accession number
    source_url = Column(Text, nullable=True)

    publication_date = Column(DateTime, nullable=True)

    # Classification
    evidence_class = Column(Enum(EvidenceClass), nullable=False)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    # Versioning
    parser_version = Column(String(20))
    schema_version = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    security = relationship("SecurityIdentityORM", back_populates="evidence_records")
    canonical_facts = relationship("CanonicalFactORM", secondary="canonical_fact_evidence", back_populates="evidence_records")

    __table_args__ = (
        Index("ix_evidence_security_field", "security_id", "field_name"),
        Index("ix_evidence_known_date", "known_date"),
        Index("ix_evidence_known_at", "known_at"),  # NEW: Timestamp precision index
        Index("ix_evidence_effective_date", "effective_date"),
        Index("ix_evidence_security_known_at", "security_id", "known_at"),  # NEW: Composite index
    )


# ============================================================================
# NORMALIZED & CANONICAL FACTS
# ============================================================================

class CanonicalFactORM(Base):
    """Validated and normalized fact available to calculations."""
    __tablename__ = "canonical_fact"

    canonical_fact_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)
    field_name = Column(String(100), nullable=False)

    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)

    period = Column(Enum(PeriodType), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    known_date = Column(DateTime, nullable=False)

    primary_evidence_id = Column(String(36), ForeignKey("evidence_record.evidence_id"))

    verification_status = Column(Enum(VerificationStatus), nullable=False)
    data_quality = Column(Enum(DataQualityRating), nullable=False)

    methodology_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    security = relationship("SecurityIdentityORM", back_populates="canonical_facts")
    evidence_records = relationship("EvidenceRecordORM", secondary="canonical_fact_evidence", back_populates="canonical_facts")

    __table_args__ = (
        Index("ix_canonical_security_field", "security_id", "field_name"),
        Index("ix_canonical_known_date", "known_date"),
    )


# Association table for many-to-many relationship
canonical_fact_evidence = Table(
    'canonical_fact_evidence',
    Base.metadata,
    Column('canonical_fact_id', String(36), ForeignKey('canonical_fact.canonical_fact_id')),
    Column('evidence_id', String(36), ForeignKey('evidence_record.evidence_id'))
)


class AssumptionRecordORM(Base):
    """Investment assumption with versioning."""
    __tablename__ = "assumption_record"

    assumption_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    metric = Column(String(100), nullable=False)
    scenario = Column(String(100), nullable=False)
    forecast_period = Column(String(50), nullable=False)

    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)

    basis = Column(Text)
    supporting_evidence_ids = Column(JSON, default=list)  # List of evidence_ids

    confidence = Column(Float, default=0.5)  # 0.0-1.0

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))

    methodology_version = Column(String(20), nullable=False)
    supersedes_assumption_id = Column(String(36), nullable=True)

    __table_args__ = (
        Index("ix_assumption_security_metric", "security_id", "metric"),
    )


# ============================================================================
# FORMULA & CALCULATION
# ============================================================================

class FormulaRegistryORM(Base):
    """Deterministic formula registry."""
    __tablename__ = "formula_registry"

    formula_id = Column(String(50), primary_key=True)  # e.g., "F_FCF_001"
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False, default="1.0")

    description = Column(Text, nullable=True)

    inputs = Column(JSON, nullable=False)  # List of field names
    expression = Column(Text, nullable=False)

    output_unit = Column(String(50), nullable=False)

    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_formula_id_version", "formula_id", "version"),
    )


class CalculationRecordORM(Base):
    """Deterministic calculation output."""
    __tablename__ = "calculation_record"

    calculation_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    formula_id = Column(String(50), ForeignKey("formula_registry.formula_id"), nullable=False)
    formula_version = Column(String(20), nullable=False)

    output_value = Column(Float, nullable=False)
    output_unit = Column(String(50), nullable=False)

    period = Column(Enum(PeriodType), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    known_date = Column(DateTime, nullable=False)

    input_evidence_ids = Column(JSON, default=list)  # List of evidence_ids

    calculation_timestamp = Column(DateTime, default=datetime.utcnow)
    methodology_version = Column(String(20), nullable=False)

    __table_args__ = (
        Index("ix_calculation_security_formula", "security_id", "formula_id"),
    )


# ============================================================================
# CONFLICT & QUALITY
# ============================================================================

class EvidenceConflictORM(Base):
    """Recorded evidence conflict."""
    __tablename__ = "evidence_conflict"

    conflict_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)
    field_name = Column(String(100), nullable=False)

    candidate_evidence_ids = Column(JSON, nullable=False)  # List
    conflict_type = Column(Enum(ConflictType), nullable=False)
    conflict_description = Column(Text)

    resolution_status = Column(String(50), default="UNRESOLVED")  # UNRESOLVED, RESOLVED, WAIVED
    resolution_rule = Column(String(255), nullable=True)
    resolved_evidence_id = Column(String(36), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_conflict_security_field", "security_id", "field_name"),
        Index("ix_conflict_status", "resolution_status"),
    )


class DataQualityAssessmentORM(Base):
    """Data quality evaluation."""
    __tablename__ = "data_quality_assessment"

    quality_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    fact_reference = Column(String(36), nullable=False)  # FK to CanonicalFact

    # Component scores
    source_authority_score = Column(Float, default=0.0)
    verification_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)
    period_match_score = Column(Float, default=0.0)
    cross_source_agreement = Column(Float, default=0.0)
    parser_confidence = Column(Float, default=0.0)

    overall_rating = Column(Enum(DataQualityRating), nullable=False)

    concerns = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    evaluated_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(String(100), nullable=True)


# ============================================================================
# SOURCE & PROVIDER MANAGEMENT
# ============================================================================

class SourceAuthorityRegistryORM(Base):
    """Source precedence and requirements registry."""
    __tablename__ = "source_authority_registry"

    registry_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    field_name = Column(String(100), nullable=False)
    atlas_object = Column(String(100), nullable=False)

    primary_source = Column(String(50), nullable=False)
    secondary_source = Column(String(50), nullable=True)
    fallback_source = Column(String(50), nullable=True)

    minimum_decision_authority = Column(Enum(DecisionAuthority), nullable=False)

    verification_requirement = Column(Enum(VerificationStatus), nullable=False)

    point_in_time_required = Column(Boolean, default=True)

    normalization_rule = Column(String(100), nullable=False)

    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_source_registry_field", "field_name", "atlas_object"),
    )


class FreshnessPolicyRegistryORM(Base):
    """Freshness requirements registry."""
    __tablename__ = "freshness_policy_registry"

    policy_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    field_name = Column(String(100), nullable=False)
    atlas_object = Column(String(100), nullable=False)

    maximum_age_hours = Column(Integer, nullable=False)
    acceptable_age_hours = Column(Integer, nullable=True)

    source_type = Column(String(50), nullable=False)

    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_freshness_field_source", "field_name", "source_type"),
    )


class ProviderHealthORM(Base):
    """Provider health monitoring."""
    __tablename__ = "provider_health"

    health_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    provider_name = Column(String(100), nullable=False, index=True)
    provider_type = Column(String(50), nullable=False)

    status = Column(Enum(ProviderStatus), default=ProviderStatus.AVAILABLE)

    last_success = Column(DateTime, nullable=True)
    last_error = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)

    error_rate_24h = Column(Float, default=0.0)
    latency_ms_p95 = Column(Float, nullable=True)
    latency_ms_p99 = Column(Float, nullable=True)

    last_validation = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# FREEZE INFRASTRUCTURE
# ============================================================================

class EvidenceFreezeORM(Base):
    """Immutable evidence snapshot."""
    __tablename__ = "evidence_freeze"

    freeze_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    security_identity_version = Column(String(20), nullable=False)
    evidence_manifest = Column(JSON, nullable=False)
    canonical_facts_manifest = Column(JSON, nullable=False)
    formula_registry_version = Column(String(20), nullable=False)
    source_authority_version = Column(String(20), nullable=False)

    canonical_serialization = Column(Text, nullable=False)
    freeze_hash = Column(String(64), nullable=False, index=True)

    atlas_version = Column(String(20), nullable=False)
    schema_version = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    created_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# FINANCIAL STATEMENTS
# ============================================================================

class FinancialStateORM(Base):
    """Financial state snapshot."""
    __tablename__ = "financial_state"

    financial_state_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    period_type = Column(Enum(PeriodType), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Income Statement
    revenue = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    operating_income = Column(Float, nullable=True)
    pretax_income = Column(Float, nullable=True)
    taxes = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    basic_eps = Column(Float, nullable=True)
    diluted_eps = Column(Float, nullable=True)

    # Cash Flow
    cash_from_operations = Column(Float, nullable=True)
    capex = Column(Float, nullable=True)
    fcf = Column(Float, nullable=True)
    sbc = Column(Float, nullable=True)
    share_repurchases = Column(Float, nullable=True)
    dividends = Column(Float, nullable=True)

    # Balance Sheet
    cash = Column(Float, nullable=True)
    marketable_securities = Column(Float, nullable=True)
    short_term_debt = Column(Float, nullable=True)
    long_term_debt = Column(Float, nullable=True)
    shareholders_equity = Column(Float, nullable=True)

    # Shares
    weighted_average_diluted_shares = Column(Float, nullable=True)
    period_end_shares = Column(Float, nullable=True)

    # Metadata
    data_quality = Column(Enum(DataQualityRating), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    known_date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_financial_security_period", "security_id", "period_end"),
    )


# ============================================================================
# MARKET DATA
# ============================================================================

class MarketStateORM(Base):
    """Market data snapshot."""
    __tablename__ = "market_state"

    market_state_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    timestamp = Column(DateTime, nullable=False)

    price = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)

    volume = Column(Integer, nullable=True)

    market_session = Column(String(50), default="REGULAR")

    price_source = Column(String(50), nullable=False)
    price_raw = Column(Boolean, default=False)

    provider_status = Column(Enum(ProviderStatus), nullable=False)
    freshness_hours = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_market_security_timestamp", "security_id", "timestamp"),
    )


# ============================================================================
# MACRO DATA
# ============================================================================

class MacroDataPointORM(Base):
    """Macroeconomic data point."""
    __tablename__ = "macro_data_point"

    macro_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    series_id = Column(String(20), nullable=False, index=True)
    series_name = Column(String(100), nullable=False)

    value = Column(Float, nullable=False)

    effective_date = Column(DateTime, nullable=False)
    known_date = Column(DateTime, nullable=False)

    publication_date = Column(DateTime, nullable=False)
    retrieved_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    source = Column(String(50), nullable=False)
    source_url = Column(Text, nullable=True)

    unit = Column(String(50), nullable=False)
    frequency = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_macro_series_effective", "series_id", "effective_date"),
        Index("ix_macro_series_known", "series_id", "known_date"),
    )


# ============================================================================
# RESEARCH EVENTS
# ============================================================================

class ResearchEventORM(Base):
    """Research event foundation."""
    __tablename__ = "research_event"

    research_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    security_id = Column(String(36), ForeignKey("security_identity.security_id"), nullable=False)

    event_type = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)

    claim_class = Column(Enum(EvidenceClass), nullable=False)
    source_tier = Column(Enum(DecisionAuthority), nullable=False)

    publication_date = Column(DateTime, nullable=False)
    effective_date = Column(DateTime, nullable=True)

    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.UNVERIFIED)

    materiality = Column(String(50))
    impact_class = Column(String(100))

    affected_objects = Column(JSON, default=list)

    recommended_action = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# VERSION & AUDIT
# ============================================================================

class AtlasVersionORM(Base):
    """Version tracking."""
    __tablename__ = "atlas_version"

    version_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    component = Column(String(100), nullable=False)
    version_number = Column(String(20), nullable=False)

    description = Column(Text, nullable=True)

    released_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_version_component", "component", "version_number"),
    )


class AuditTrailORM(Base):
    """Audit trail for important writes."""
    __tablename__ = "audit_trail"

    audit_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    record_type = Column(String(100), nullable=False)
    record_id = Column(String(36), nullable=False)

    action = Column(String(50), nullable=False)

    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=False)

    timestamp = Column(DateTime, nullable=False)
    process = Column(String(100), nullable=False)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_record", "record_type", "record_id"),
        Index("ix_audit_timestamp", "timestamp"),
    )


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
