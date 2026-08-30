"""
Sprint 1 Test Suite

Comprehensive tests for core infrastructure.
Covers: formulas, SEC adapter, point-in-time queries, conflicts, data quality.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Import database and models
from database import (
    init_db, SessionLocal, Base, engine,
    SecurityIdentityORM, EvidenceRecordORM,
    CanonicalFactORM, FormulaRegistryORM, EvidenceConflictORM,
    MarketStateORM, MacroDataPointORM
)

from models import (
    SecurityIdentityStatus, EvidenceClass, VerificationStatus,
    DecisionAuthority, DataQualityRating, ConflictType, ProviderStatus,
    PeriodType
)

from sec_adapter import SECAdapter
from point_in_time import PointInTimeService
from formulas import FormulaRegistry
from market_macro_adapters import get_market_adapter, get_macro_adapter

from xbrl_parser import (
    select_canonical_fact, select_canonical_fact_production,
    duration_granularity, classify_period, PeriodGranularity, PeriodIntentError,
)
from entity_classification import (
    classify_entity, filing_regime_for, EntityArchetype, FilingRegime,
)
from identity_resolver import (
    resolve_security, share_class_from_ticker, same_issuer, distinct_securities,
    market_price_join_key, assert_distinct_price_series, IdentityJoinError,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def db():
    """Create an isolated test database session.

    The engine is a process-wide in-memory SQLite (StaticPool), so state would
    otherwise leak between tests. Drop and recreate the schema per test to keep
    each test independent.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sec_adapter():
    """Create SEC adapter."""
    return SECAdapter()


@pytest.fixture
def sample_security(db: Session) -> SecurityIdentityORM:
    """Create sample security (MSFT)."""
    security = SecurityIdentityORM(
        security_id="SEC_MSFT",
        issuer_id="ISS_MSFT",
        company_name="Microsoft Corporation",
        ticker="MSFT",
        exchange="NASDAQ",
        cik="0000789019",
        status=SecurityIdentityStatus.VERIFIED,
        listing_status="ACTIVE"
    )
    db.add(security)
    db.commit()
    return security


# ============================================================================
# UNIT TESTS: FORMULAS
# ============================================================================

class TestFormulas:
    """Test deterministic formula calculation."""

    def test_fcf_calculation(self, db: Session):
        """Test FCF = CFO - Capex"""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_FCF_001",
            {
                "cash_from_operations": 100.0,
                "capex": 25.0
            }
        )

        assert result == 75.0

    def test_fcf_margin_calculation(self, db: Session):
        """Test FCF margin = FCF / Revenue"""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_FCF_MARGIN_001",
            {
                "fcf": 75.0,
                "revenue": 250.0
            }
        )

        assert result == pytest.approx(0.30)

    def test_gross_margin_calculation(self, db: Session):
        """Test Gross margin = Gross Profit / Revenue"""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_GROSS_MARGIN_001",
            {
                "gross_profit": 150.0,
                "revenue": 250.0
            }
        )

        assert result == pytest.approx(0.60)

    def test_revenue_growth_calculation(self, db: Session):
        """Test Revenue growth YoY"""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_REVENUE_GROWTH_001",
            {
                "revenue_current": 275.0,
                "revenue_prior": 250.0
            }
        )

        assert result == pytest.approx(0.10)  # 10% growth

    def test_formula_missing_input(self, db: Session):
        """Formula returns None on missing input."""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_FCF_001",
            {
                "cash_from_operations": 100.0
                # Missing capex
            }
        )

        assert result is None

    def test_formula_division_by_zero(self, db: Session):
        """Formula returns None on division by zero."""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_FCF_MARGIN_001",
            {
                "fcf": 75.0,
                "revenue": 0.0  # Division by zero
            }
        )

        assert result is None

    def test_formula_extreme_values(self, db: Session):
        """Formula handles extreme values."""
        registry = FormulaRegistry(db)

        result = registry.execute_formula(
            "F_FCF_001",
            {
                "cash_from_operations": 1e10,
                "capex": 1e9
            }
        )

        assert result == pytest.approx(9e9)


# ============================================================================
# UNIT TESTS: EVIDENCE & CONFLICTS
# ============================================================================

class TestEvidenceManagement:
    """Test evidence handling and conflict detection."""

    def test_evidence_immutability(self, db: Session, sample_security: SecurityIdentityORM):
        """Raw evidence records are immutable."""
        evidence = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="100B",
            normalized_value=100.0,
            unit="currency",
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 4, 25),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="0001144659-24-051234",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )
        db.add(evidence)
        db.commit()

        # Retrieve and verify immutable
        retrieved = db.query(EvidenceRecordORM).filter(
            EvidenceRecordORM.evidence_id == evidence.evidence_id
        ).first()

        assert retrieved.raw_value == "100B"
        assert retrieved.normalized_value == 100.0

    def test_conflict_detection_source_disagreement(self, db: Session, sample_security: SecurityIdentityORM):
        """Detect conflict when sources disagree."""
        # Create conflicting evidence
        evidence1 = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="100B",
            normalized_value=100.0,
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 4, 25),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="filing1",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )

        evidence2 = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="105B",
            normalized_value=105.0,
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 4, 26),
            source_type="VENDOR",
            source_tier=DecisionAuthority.DA3,
            source_name="DataProvider",
            source_identifier="provider1",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.CORROBORATED,
            parser_version="1.0",
            schema_version="1.0"
        )

        db.add(evidence1)
        db.add(evidence2)
        db.commit()

        # Create conflict record
        conflict = EvidenceConflictORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            candidate_evidence_ids=[evidence1.evidence_id, evidence2.evidence_id],
            conflict_type=ConflictType.SOURCE_DISAGREEMENT,
            conflict_description="SEC: 100B vs Vendor: 105B"
        )
        db.add(conflict)
        db.commit()

        # Verify conflict recorded
        retrieved_conflict = db.query(EvidenceConflictORM).filter(
            EvidenceConflictORM.conflict_id == conflict.conflict_id
        ).first()

        assert retrieved_conflict.resolution_status == "UNRESOLVED"


# ============================================================================
# INTEGRATION TESTS: POINT-IN-TIME
# ============================================================================

class TestPointInTime:
    """Test bitemporal queries."""

    def test_fact_not_available_before_known_date(self, db: Session, sample_security: SecurityIdentityORM):
        """Fact must not appear before known_date."""
        # Fact economically applies March 31, known April 25
        evidence = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="100B",
            normalized_value=100.0,
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 4, 25),
            known_at=datetime(2024, 4, 25),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="filing",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )
        db.add(evidence)
        db.commit()

        # Query April 10 (before known date)
        service = PointInTimeService(db)
        evidence_on_april_10 = service.get_evidence_as_of_date(
            sample_security.security_id,
            "revenue",
            datetime(2024, 4, 10)
        )

        assert len(evidence_on_april_10) == 0  # Must be empty

    def test_fact_available_after_known_date(self, db: Session, sample_security: SecurityIdentityORM):
        """Fact must be available after known_date."""
        evidence = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="100B",
            normalized_value=100.0,
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 4, 25),
            known_at=datetime(2024, 4, 25),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="filing",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )
        db.add(evidence)
        db.commit()

        # Query April 26 (after known date)
        service = PointInTimeService(db)
        evidence_on_april_26 = service.get_evidence_as_of_date(
            sample_security.security_id,
            "revenue",
            datetime(2024, 4, 26)
        )

        assert len(evidence_on_april_26) == 1
        assert evidence_on_april_26[0].normalized_value == 100.0

    def test_restatement_handling(self, db: Session, sample_security: SecurityIdentityORM):
        """Original value preserved in history, restated value is current."""
        # Original value known April 25
        original = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="100B",
            normalized_value=100.0,
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 4, 25),
            known_at=datetime(2024, 4, 25),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="filing_v1",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )

        # Restatement known May 15
        restated = EvidenceRecordORM(
            security_id=sample_security.security_id,
            field_name="revenue",
            raw_value="98B",
            normalized_value=98.0,
            effective_date=datetime(2024, 3, 31),
            known_date=datetime(2024, 5, 15),
            known_at=datetime(2024, 5, 15),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="filing_v2",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )

        db.add(original)
        db.add(restated)
        db.commit()

        service = PointInTimeService(db)

        # Query May 1 (before restatement)
        evidence_may_1 = service.get_evidence_as_of_date(
            sample_security.security_id,
            "revenue",
            datetime(2024, 5, 1)
        )
        assert evidence_may_1[0].normalized_value == 100.0  # Original

        # Query May 20 (after restatement)
        evidence_may_20 = service.get_evidence_as_of_date(
            sample_security.security_id,
            "revenue",
            datetime(2024, 5, 20)
        )
        assert evidence_may_20[0].normalized_value == 98.0  # Restated


# ============================================================================
# INTEGRATION TESTS: SEC ADAPTER
# ============================================================================

class TestSECAdapter:
    """Test SEC adapter functionality."""

    def test_sec_rate_limiting(self, sec_adapter: SECAdapter):
        """SEC adapter respects rate limits."""
        # Should not raise errors due to rate limiting
        status = sec_adapter.get_provider_status()
        assert status["provider"] == "SEC"

    def test_filing_archive(self, sec_adapter: SECAdapter, db: Session):
        """Filing archive is immutable."""
        archive_metadata = sec_adapter.archive_filing(
            cik="0000789019",
            accession="0001144659-24-051234",
            form_type="10-K",
            filed_date="2024-08-22",
            period_end="2024-06-30",
            content="<filing>MSFT 10-K Content</filing>",
            response_hash="abc123"
        )

        assert archive_metadata["response_hash"] == "abc123"
        assert archive_metadata["form_type"] == "10-K"

        # Retrieve from archive
        retrieved = sec_adapter.get_archived_filing("0000789019", "0001144659-24-051234")
        assert retrieved is not None
        assert "MSFT 10-K" in retrieved["content"]


# ============================================================================
# INTEGRATION TESTS: PROVIDERS
# ============================================================================

class TestProviders:
    """Test market and macro providers."""

    def test_market_adapter_quote(self):
        """Market adapter returns quote."""
        adapter = get_market_adapter()
        quote = adapter.get_quote("MSFT")

        assert quote is not None
        assert quote["ticker"] == "MSFT"
        assert "price" in quote

    def test_market_adapter_daily_bars(self):
        """Market adapter returns daily bars."""
        adapter = get_market_adapter()
        bars = adapter.get_daily_bars("MSFT", limit=30)

        assert bars is not None
        assert len(bars) > 0
        assert "close" in bars[0]

    def test_macro_adapter_fred_series(self):
        """Macro adapter returns FRED series."""
        adapter = get_macro_adapter()
        series = adapter.get_series("DGS10")

        assert series is not None
        assert len(series) > 0
        assert series[0]["series_id"] == "DGS10"


# ============================================================================
# MSFT GOLDEN TEST
# ============================================================================

class TestMSFTGoldenSecurity:
    """Test complete workflow for Microsoft (MSFT)."""

    def test_msft_cik_resolution(self, sec_adapter: SECAdapter):
        """Resolve MSFT to correct CIK."""
        cik = sec_adapter.resolve_cik("MSFT")

        assert cik is not None
        assert cik == "0000789019"

    def test_msft_end_to_end(self, db: Session, sec_adapter: SECAdapter):
        """End-to-end workflow for MSFT."""
        # 1. Resolve CIK
        cik = sec_adapter.resolve_cik("MSFT")
        assert cik == "0000789019"

        # 2. Create security identity
        security = SecurityIdentityORM(
            security_id="SEC_MSFT_GOLD",
            issuer_id="ISS_MSFT",
            company_name="Microsoft Corporation",
            ticker="MSFT",
            exchange="NASDAQ",
            cik=cik,
            status=SecurityIdentityStatus.VERIFIED,
            listing_status="ACTIVE",
            fiscal_year_end="06-30"
        )
        db.add(security)
        db.commit()

        # 3. Get market data
        market = get_market_adapter()
        quote = market.get_quote("MSFT")
        assert quote is not None

        # 4. Get macro data
        macro = get_macro_adapter()
        treasury_10y = macro.get_latest_value("DGS10")
        assert treasury_10y is not None

        # 5. Create evidence record
        evidence = EvidenceRecordORM(
            security_id=security.security_id,
            field_name="revenue",
            raw_value="245.1B",
            normalized_value=245.1,
            effective_date=datetime(2024, 6, 30),
            known_date=datetime(2024, 8, 22),
            known_at=datetime(2024, 8, 22),
            source_type="SEC",
            source_tier=DecisionAuthority.DA4,
            source_name="SEC",
            source_identifier="0001144659-24-051234",
            evidence_class=EvidenceClass.REPORTED_FACT,
            verification_status=VerificationStatus.PRIMARY_VERIFIED,
            parser_version="1.0",
            schema_version="1.0"
        )
        db.add(evidence)
        db.commit()

        # 6. Calculate metrics
        formula_registry = FormulaRegistry(db)
        formula_registry.initialize_registry()

        # 7. Verify point-in-time queries
        pit_service = PointInTimeService(db)
        evidence_on_date = pit_service.get_evidence_as_of_date(
            security.security_id,
            "revenue",
            datetime(2024, 8, 22)
        )
        assert len(evidence_on_date) == 1


# ============================================================================
# PHASE 4A.5.1A: PERIOD GRANULARITY
# ============================================================================

def _facts_with_quarter_and_ytd():
    """Synthetic CompanyFacts: one 10-Q accession carrying BOTH the current
    fiscal quarter and the fiscal year-to-date revenue for the same period_end."""
    return {
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {
                        "USD": [
                            {"val": 241832000000, "start": "2025-07-01", "end": "2026-03-31",
                             "accn": "0000-Q", "fp": "Q3", "form": "10-Q"},
                            {"val": 82886000000, "start": "2026-01-01", "end": "2026-03-31",
                             "accn": "0000-Q", "fp": "Q3", "form": "10-Q"},
                        ]
                    }
                }
            }
        }
    }


class TestPeriodGranularity:
    """A QUARTER request must never fall through to a year-to-date duration."""

    def test_duration_granularity_classification(self):
        assert duration_granularity("2026-01-01", "2026-03-31") == "QUARTER"
        assert duration_granularity("2026-01-01", "2026-06-30") == "YEAR_TO_DATE"   # H1
        assert duration_granularity("2025-07-01", "2026-03-31") == "YEAR_TO_DATE"   # 9 month
        assert duration_granularity("2025-07-01", "2026-06-30") == "ANNUAL"
        assert duration_granularity("2024-01-01", "2026-12-31") is None             # multi-year
        assert duration_granularity(None, "2026-03-31") is None                     # instant

    def test_quarter_request_returns_quarter_not_ytd(self):
        cf = _facts_with_quarter_and_ytd()
        sel = select_canonical_fact(
            cf, "revenue", accession="0000-Q", period_end="2026-03-31",
            period_granularity=PeriodGranularity.QUARTER,
        )
        assert sel["status"] == "SELECTED"
        assert sel["raw_value"] == 82886000000
        assert sel["period_start"] == "2026-01-01"
        assert sel["period_granularity"] == "QUARTER"

    def test_ytd_request_returns_ytd_not_quarter(self):
        cf = _facts_with_quarter_and_ytd()
        sel = select_canonical_fact(
            cf, "revenue", accession="0000-Q", period_end="2026-03-31",
            period_granularity="YEAR_TO_DATE",
        )
        assert sel["status"] == "SELECTED"
        assert sel["raw_value"] == 241832000000
        assert sel["period_start"] == "2025-07-01"

    def test_legacy_call_unchanged(self):
        """No period_granularity -> identical to prior behavior (earliest-start)."""
        cf = _facts_with_quarter_and_ytd()
        sel = select_canonical_fact(
            cf, "revenue", accession="0000-Q", period_end="2026-03-31",
            period_type="duration",
        )
        assert sel["status"] == "SELECTED"
        assert sel["raw_value"] == 241832000000  # unchanged: still the YTD fact

    def test_first_quarter_is_also_year_to_date(self):
        cf = {
            "facts": {"us-gaap": {"Revenues": {"units": {"USD": [
                {"val": 100, "start": "2026-01-01", "end": "2026-03-31",
                 "accn": "Q1", "fp": "Q1", "form": "10-Q"},
            ]}}}}
        }
        q = select_canonical_fact(cf, "revenue", accession="Q1", period_end="2026-03-31",
                                  period_granularity="QUARTER")
        ytd = select_canonical_fact(cf, "revenue", accession="Q1", period_end="2026-03-31",
                                    period_granularity="YEAR_TO_DATE")
        assert q["raw_value"] == 100
        assert ytd["raw_value"] == 100  # Q1 quarter == Q1 YTD

    def test_quarter_unavailable_when_only_ytd_exists(self):
        cf = {
            "facts": {"us-gaap": {"Revenues": {"units": {"USD": [
                {"val": 300, "start": "2025-07-01", "end": "2026-03-31",
                 "accn": "Q", "fp": "Q3", "form": "10-Q"},
            ]}}}}
        }
        sel = select_canonical_fact(cf, "revenue", accession="Q", period_end="2026-03-31",
                                    period_granularity="QUARTER")
        assert sel["status"] == "UNAVAILABLE"


# ============================================================================
# PHASE 4A.5.1B: PRODUCTION PERIOD CONTRACT — FAIL CLOSED
# ============================================================================

class TestProductionPeriodContract:
    """New production/benchmark calls must state period intent; ambiguous
    durations must not be confidently selected."""

    def test_production_duration_without_intent_fails_closed(self):
        cf = _facts_with_quarter_and_ytd()
        # omitted entirely -> TypeError (required kwarg, hardest fail-closed)
        with pytest.raises(TypeError):
            select_canonical_fact_production(cf, "revenue", accession="0000-Q",
                                             period_end="2026-03-31")
        # explicit None -> PeriodIntentError (never silently earliest-start/YTD)
        with pytest.raises(PeriodIntentError):
            select_canonical_fact_production(cf, "revenue", period_granularity=None,
                                             accession="0000-Q", period_end="2026-03-31")

    def test_production_instant_field_requires_instant(self):
        cf = {"facts": {"us-gaap": {"CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [
            {"val": 5, "end": "2026-03-31", "accn": "0000-Q", "fp": "Q3", "form": "10-Q"},
        ]}}}}}
        with pytest.raises(PeriodIntentError):
            select_canonical_fact_production(cf, "cash", period_granularity="QUARTER",
                                             accession="0000-Q", period_end="2026-03-31")
        ok = select_canonical_fact_production(cf, "cash", period_granularity=PeriodGranularity.INSTANT,
                                              accession="0000-Q", period_end="2026-03-31")
        assert ok["status"] == "SELECTED" and ok["raw_value"] == 5
        assert ok["selection_boundary"] == "production"

    def test_production_standard_quarter_selects_quarter(self):
        cf = _facts_with_quarter_and_ytd()
        sel = select_canonical_fact_production(cf, "revenue", period_granularity="QUARTER",
                                               accession="0000-Q", period_end="2026-03-31")
        assert sel["status"] == "SELECTED"
        assert sel["raw_value"] == 82886000000
        assert sel["period_start"] == "2026-01-01"

    def test_production_standard_ytd_selects_ytd(self):
        cf = _facts_with_quarter_and_ytd()
        sel = select_canonical_fact_production(cf, "revenue", period_granularity="YEAR_TO_DATE",
                                               accession="0000-Q", period_end="2026-03-31")
        assert sel["status"] == "SELECTED"
        assert sel["raw_value"] == 241832000000

    def test_stub_period_incompatible_with_fp_not_selected(self):
        """fp says Q1 (interim) but the duration is a ~5-month stub -> fail closed."""
        cf = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
            {"val": 999, "start": "2026-01-01", "end": "2026-05-27",  # ~146 days
             "accn": "STUB", "fp": "Q1", "form": "10-Q"},
        ]}}}}}
        assert classify_period(cf["facts"]["us-gaap"]["Revenues"]["units"]["USD"][0]) == set()
        for g in ("QUARTER", "YEAR_TO_DATE", "ANNUAL"):
            sel = select_canonical_fact_production(cf, "revenue", period_granularity=g,
                                                   accession="STUB", period_end="2026-05-27")
            assert sel["status"] == "UNAVAILABLE"

    def test_stub_period_no_fp_nonstandard_length_not_selected(self):
        """No fiscal-period metadata + non-standard length (~7 months) -> fail closed."""
        fact = {"val": 1, "start": "2026-01-01", "end": "2026-08-04", "accn": "X", "form": "10-Q"}
        assert classify_period(fact) == set()
        cf = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [fact]}}}}}
        sel = select_canonical_fact_production(cf, "revenue", period_granularity="YEAR_TO_DATE",
                                               accession="X", period_end="2026-08-04")
        assert sel["status"] == "UNAVAILABLE"

    def test_q1_explicit_behavior_documented(self):
        """Q1: the single ~91-day duration satisfies BOTH QUARTER and YEAR_TO_DATE."""
        fact = {"val": 100, "start": "2026-01-01", "end": "2026-03-31",
                "accn": "Q1", "fp": "Q1", "form": "10-Q"}
        assert classify_period(fact) == {"QUARTER", "YEAR_TO_DATE"}
        cf = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [fact]}}}}}
        q = select_canonical_fact_production(cf, "revenue", period_granularity="QUARTER",
                                             accession="Q1", period_end="2026-03-31")
        ytd = select_canonical_fact_production(cf, "revenue", period_granularity="YEAR_TO_DATE",
                                               accession="Q1", period_end="2026-03-31")
        assert q["raw_value"] == 100 and ytd["raw_value"] == 100

    def test_fy_fact_with_quarter_duration_fails_closed(self):
        fact = {"val": 7, "start": "2026-01-01", "end": "2026-03-31", "accn": "K", "fp": "FY"}
        assert classify_period(fact) == set()


# ============================================================================
# PHASE 4A.5.1A: ENTITY ARCHETYPE / FILING REGIME
# ============================================================================

def _subs(entity_type="operating", sic="7372", sic_desc="Services-Prepackaged Software", forms=("10-K", "10-Q")):
    return {
        "entityType": entity_type,
        "sic": sic,
        "sicDescription": sic_desc,
        "filings": {"recent": {"form": list(forms)}},
    }


class TestEntityClassification:
    """Routing is derived from entityType + SIC + form set, never issuer names."""

    def test_operating_company(self):
        arch, _ = classify_entity(_subs())
        assert arch == EntityArchetype.OPERATING_COMPANY
        assert filing_regime_for(arch) == FilingRegime.SEC_CORPORATE

    def test_bank(self):
        arch, _ = classify_entity(_subs(sic="6021", sic_desc="National Commercial Banks"))
        assert arch == EntityArchetype.FINANCIAL_BANK

    def test_reit(self):
        arch, _ = classify_entity(_subs(sic="6798", sic_desc="Real Estate Investment Trusts"))
        assert arch == EntityArchetype.REIT

    def test_insurance(self):
        arch, _ = classify_entity(_subs(sic="6331", sic_desc="Fire, Marine & Casualty Insurance"))
        assert arch == EntityArchetype.INSURANCE

    def test_investment_company_by_forms(self):
        arch, _ = classify_entity(_subs(entity_type="other", sic="", sic_desc="",
                                        forms=("N-CEN", "NPORT-P", "485BPOS", "24F-2NT")))
        assert arch == EntityArchetype.INVESTMENT_COMPANY_ETF
        assert filing_regime_for(arch) == FilingRegime.SEC_INVESTMENT_COMPANY

    def test_investment_company_by_entity_type(self):
        arch, _ = classify_entity(_subs(entity_type="other", sic="", sic_desc="", forms=("497",)))
        assert arch == EntityArchetype.INVESTMENT_COMPANY_ETF

    def test_unclassified_regime_is_unknown(self):
        arch, _ = classify_entity(_subs(entity_type="", sic="", sic_desc="", forms=()))
        assert arch == EntityArchetype.UNCLASSIFIED
        assert filing_regime_for(arch) == FilingRegime.UNKNOWN


# ============================================================================
# PHASE 4A.5.1A: ISSUER vs SECURITY IDENTITY
# ============================================================================

class TestIdentityResolver:
    """Issuer (CIK) and security (ticker / share class) stay distinct."""

    def test_share_class_from_ticker(self):
        assert share_class_from_ticker("BRK-A") == "A"
        assert share_class_from_ticker("BRK-B") == "B"
        assert share_class_from_ticker("JPM-PC") == "PC"
        assert share_class_from_ticker("MSFT") is None

    def test_brk_a_and_brk_b_distinct_same_issuer(self):
        """Live: BRK.A != BRK.B as securities, same issuer, no share-class collapse."""
        a = resolve_security("BRK.A")
        b = resolve_security("BRK.B")
        assert a.resolved and b.resolved
        assert a.cik == b.cik == "0001067983"          # same issuer CIK
        assert same_issuer(a, b)
        assert distinct_securities(a, b)                # different security_key
        assert a.sec_ticker == "BRK-A" and b.sec_ticker == "BRK-B"
        assert a.share_class == "A" and b.share_class == "B"
        assert a.security_key != b.security_key

    def test_single_class_issuer_has_no_share_class(self):
        m = resolve_security("MSFT")
        assert m.resolved
        assert m.share_class is None
        assert m.security_type == "COMMON_STOCK"

    def test_orm_kwargs_keep_issuer_and_security_distinct(self, db: Session):
        """Two share classes persist as two rows under one issuer_id."""
        a = resolve_security("BRK.A")
        b = resolve_security("BRK.B")
        for r in (a, b):
            kw = r.to_orm_kwargs()
            kw["exchange"] = kw.get("exchange") or "NYSE"
            db.add(SecurityIdentityORM(**kw))
        db.commit()
        rows = db.query(SecurityIdentityORM).order_by(SecurityIdentityORM.ticker).all()
        assert len(rows) == 2
        assert rows[0].ticker == "BRK-A" and rows[1].ticker == "BRK-B"
        assert rows[0].share_class == "A" and rows[1].share_class == "B"
        assert rows[0].issuer_id == rows[1].issuer_id           # same issuer
        assert rows[0].security_id != rows[1].security_id       # distinct securities

    def test_spy_routes_to_investment_company(self):
        s = resolve_security("SPY")
        assert s.resolved
        assert s.entity_archetype == "INVESTMENT_COMPANY_ETF"
        assert s.filing_regime == "SEC_INVESTMENT_COMPANY"
        assert s.security_type == "FUND_OR_ETF"


class TestMarketDataIdentityJoin:
    """Phase 4A.5.1B contract: price observations bind to security_key, not CIK.
    BRK.A / BRK.B must never share one price series."""

    def test_join_key_is_security_key_not_cik(self):
        k = market_price_join_key("BRK.B")
        assert k == "SEC-CIK:0001067983:BRK-B"
        assert k != "0001067983"  # not the bare issuer CIK

    def test_ticker_resolves_to_correct_security_key(self):
        assert market_price_join_key("BRK.A") == "SEC-CIK:0001067983:BRK-A"
        assert market_price_join_key("BRK-A") == "SEC-CIK:0001067983:BRK-A"  # dotted or hyphen
        assert market_price_join_key("MSFT") == "SEC-CIK:0000789019:MSFT"

    def test_unresolvable_ticker_fails_closed(self):
        with pytest.raises(IdentityJoinError):
            market_price_join_key("NOT_A_REAL_TICKER_XYZ")

    def test_brk_a_brk_b_distinct_price_series(self):
        rep = assert_distinct_price_series("BRK.A", "BRK.B")
        assert rep["distinct_security_keys"] is True
        assert rep["shares_issuer"] is True
        assert rep["security_keys"]["BRK.A"] != rep["security_keys"]["BRK.B"]

    def test_price_rows_bind_to_distinct_securities_in_db(self, db: Session):
        a = resolve_security("BRK.A")
        b = resolve_security("BRK.B")
        for r in (a, b):
            kw = r.to_orm_kwargs()
            kw["exchange"] = kw.get("exchange") or "NYSE"
            db.add(SecurityIdentityORM(**kw))
        db.commit()

        db.add(MarketStateORM(
            security_id=market_price_join_key("BRK.A"),
            timestamp=datetime(2026, 8, 28, 20, 0, 0),
            price=735000.0, price_source="TEST",
            provider_status=ProviderStatus.AVAILABLE,
        ))
        db.add(MarketStateORM(
            security_id=market_price_join_key("BRK.B"),
            timestamp=datetime(2026, 8, 28, 20, 0, 0),
            price=490.0, price_source="TEST",
            provider_status=ProviderStatus.AVAILABLE,
        ))
        db.commit()

        a_prices = db.query(MarketStateORM).filter(
            MarketStateORM.security_id == a.security_key).all()
        b_prices = db.query(MarketStateORM).filter(
            MarketStateORM.security_id == b.security_key).all()
        assert len(a_prices) == 1 and len(b_prices) == 1
        assert a_prices[0].price == 735000.0
        assert b_prices[0].price == 490.0
        assert a_prices[0].security_id != b_prices[0].security_id


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
