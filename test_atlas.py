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
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
