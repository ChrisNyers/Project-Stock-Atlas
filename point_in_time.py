"""
Point-in-Time Query Infrastructure

Enforces bitemporal constraints: information cannot leak from future into past.
All historical queries restricted to known_date <= query_date.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import (
    SecurityIdentityORM, EvidenceRecordORM, CanonicalFactORM,
    FinancialStateORM, MarketStateORM, MacroDataPointORM
)


class PointInTimeService:
    """
    Enforces temporal constraints on queries.
    Prevents future information from leaking into historical analysis.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_security_identity_at_date(
        self,
        security_id: str,
        knowledge_date: datetime,
        current: bool = False
    ) -> Optional[SecurityIdentityORM]:
        """
        Get security identity as known at specific date.

        Args:
            security_id: Security ID
            knowledge_date: Date for which to retrieve state
            current: If True, return current state regardless of date

        Returns:
            SecurityIdentity or None
        """
        if current:
            return self.db.query(SecurityIdentityORM).filter(
                SecurityIdentityORM.security_id == security_id,
                SecurityIdentityORM.effective_to == None
            ).first()

        return self.db.query(SecurityIdentityORM).filter(
            SecurityIdentityORM.security_id == security_id,
            SecurityIdentityORM.effective_from <= knowledge_date,
            or_(
                SecurityIdentityORM.effective_to == None,
                SecurityIdentityORM.effective_to > knowledge_date
            )
        ).first()

    def get_evidence_as_of_timestamp(
        self,
        security_id: str,
        field_name: str,
        query_timestamp: datetime,
        period_type: Optional[str] = None,
        limit: int = 100
    ) -> List[EvidenceRecordORM]:
        """
        Get evidence known on or before specific TIMESTAMP (NEW - timestamp precision).
        CRITICAL: Only returns evidence with known_at <= query_timestamp.

        Supports intra-day precision:
        - Filing at 16:06:24 not visible at 10:00:00 same day
        - Filing at 16:06:24 visible at 16:06:25 same day

        Args:
            security_id: Security ID
            field_name: Field name (e.g., "revenue")
            query_timestamp: Query timestamp (with hour/minute/second precision)
            period_type: Optional period filter
            limit: Maximum results

        Returns:
            List of evidence records
        """
        query = self.db.query(EvidenceRecordORM).filter(
            EvidenceRecordORM.security_id == security_id,
            EvidenceRecordORM.field_name == field_name,
            EvidenceRecordORM.known_at <= query_timestamp  # TIMESTAMP PRECISION CONSTRAINT
        ).order_by(
            EvidenceRecordORM.known_at.desc(),
            EvidenceRecordORM.retrieved_at.desc()
        )

        if period_type:
            query = query.filter(
                EvidenceRecordORM.period_end == period_type
            )

        return query.limit(limit).all()

    def get_evidence_as_of_date(
        self,
        security_id: str,
        field_name: str,
        knowledge_date: datetime,
        period_type: Optional[str] = None,
        limit: int = 100
    ) -> List[EvidenceRecordORM]:
        """
        Get evidence known by end of day (LEGACY - date only, end-of-day mode).
        CRITICAL: Only returns evidence with known_at <= end-of-day boundary.

        Args:
            security_id: Security ID
            field_name: Field name (e.g., "revenue")
            knowledge_date: Query date
            period_type: Optional period filter
            limit: Maximum results

        Returns:
            List of evidence records
        """
        # Convert to end-of-day timestamp
        from datetime import time
        end_of_day = datetime.combine(knowledge_date, time(23, 59, 59, 999999))

        query = self.db.query(EvidenceRecordORM).filter(
            EvidenceRecordORM.security_id == security_id,
            EvidenceRecordORM.field_name == field_name,
            EvidenceRecordORM.known_at <= end_of_day  # END-OF-DAY BOUNDARY
        ).order_by(
            EvidenceRecordORM.known_at.desc(),
            EvidenceRecordORM.retrieved_at.desc()
        )

        if period_type:
            query = query.filter(
                EvidenceRecordORM.period_end == period_type
            )

        return query.limit(limit).all()

    def get_canonical_fact_as_of_date(
        self,
        security_id: str,
        field_name: str,
        knowledge_date: datetime,
        period_type: Optional[str] = None
    ) -> Optional[CanonicalFactORM]:
        """
        Get canonical fact as known on specific date.

        Args:
            security_id: Security ID
            field_name: Field name
            knowledge_date: Query date
            period_type: Optional period filter

        Returns:
            CanonicalFact or None
        """
        query = self.db.query(CanonicalFactORM).filter(
            CanonicalFactORM.security_id == security_id,
            CanonicalFactORM.field_name == field_name,
            CanonicalFactORM.known_date <= knowledge_date  # CRITICAL CONSTRAINT
        )

        if period_type:
            from models import PeriodType
            query = query.filter(
                CanonicalFactORM.period == PeriodType(period_type)
            )

        return query.order_by(
            CanonicalFactORM.known_date.desc()
        ).first()

    def get_financial_state_as_of_date(
        self,
        security_id: str,
        period_end: Optional[datetime] = None,
        knowledge_date: Optional[datetime] = None
    ) -> Optional[FinancialStateORM]:
        """
        Get financial state as known on specific date.

        Args:
            security_id: Security ID
            period_end: Optional specific period end
            knowledge_date: Query date (None = current)

        Returns:
            FinancialState or None
        """
        query = self.db.query(FinancialStateORM).filter(
            FinancialStateORM.security_id == security_id
        )

        if knowledge_date:
            query = query.filter(
                FinancialStateORM.known_date <= knowledge_date  # CRITICAL CONSTRAINT
            )

        if period_end:
            query = query.filter(
                FinancialStateORM.period_end == period_end
            )

        return query.order_by(
            FinancialStateORM.period_end.desc(),
            FinancialStateORM.known_date.desc()
        ).first()

    def get_market_state_as_of_date(
        self,
        security_id: str,
        knowledge_date: datetime
    ) -> Optional[MarketStateORM]:
        """
        Get most recent market price as known on specific date.

        Args:
            security_id: Security ID
            knowledge_date: Query date

        Returns:
            MarketState or None
        """
        return self.db.query(MarketStateORM).filter(
            MarketStateORM.security_id == security_id,
            MarketStateORM.timestamp <= knowledge_date  # CRITICAL CONSTRAINT
        ).order_by(
            MarketStateORM.timestamp.desc()
        ).first()

    def get_macro_data_as_of_date(
        self,
        series_id: str,
        knowledge_date: datetime
    ) -> Optional[MacroDataPointORM]:
        """
        Get macro data point as known on specific date.

        Args:
            series_id: FRED series ID
            knowledge_date: Query date

        Returns:
            MacroDataPoint or None
        """
        return self.db.query(MacroDataPointORM).filter(
            MacroDataPointORM.series_id == series_id,
            MacroDataPointORM.known_date <= knowledge_date  # CRITICAL CONSTRAINT
        ).order_by(
            MacroDataPointORM.known_date.desc()
        ).first()

    def get_multiple_macro_series_as_of_date(
        self,
        series_ids: List[str],
        knowledge_date: datetime
    ) -> Dict[str, MacroDataPointORM]:
        """
        Get multiple macro series as known on specific date.

        Args:
            series_ids: List of FRED series IDs
            knowledge_date: Query date

        Returns:
            Dict mapping series_id to MacroDataPoint
        """
        results = {}
        for series_id in series_ids:
            point = self.get_macro_data_as_of_date(series_id, knowledge_date)
            if point:
                results[series_id] = point
        return results

    def validate_temporal_consistency(
        self,
        security_id: str,
        field_name: str,
        knowledge_date: datetime
    ) -> bool:
        """
        Validate that no evidence from after knowledge_date exists for this fact.
        Used in testing to confirm constraints are enforced.

        Args:
            security_id: Security ID
            field_name: Field name
            knowledge_date: Query date

        Returns:
            True if no future evidence exists, False otherwise
        """
        future_evidence = self.db.query(EvidenceRecordORM).filter(
            EvidenceRecordORM.security_id == security_id,
            EvidenceRecordORM.field_name == field_name,
            EvidenceRecordORM.known_date > knowledge_date
        ).count()

        return future_evidence == 0

    def get_fact_history(
        self,
        security_id: str,
        field_name: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get complete history of a fact value (for analysis/debugging).

        Args:
            security_id: Security ID
            field_name: Field name
            limit: Maximum results

        Returns:
            List of historical values
        """
        evidence = self.db.query(EvidenceRecordORM).filter(
            EvidenceRecordORM.security_id == security_id,
            EvidenceRecordORM.field_name == field_name
        ).order_by(
            EvidenceRecordORM.known_date.asc()
        ).limit(limit).all()

        return [
            {
                "evidence_id": e.evidence_id,
                "value": e.normalized_value or e.raw_value,
                "effective_date": e.effective_date.isoformat() if e.effective_date else None,
                "known_date": e.known_date.isoformat(),
                "source": e.source_name,
                "verification": e.verification_status.value
            }
            for e in evidence
        ]


class TemporalQuery:
    """Helper for building temporal queries."""

    @staticmethod
    def build_temporal_constraint(
        known_date_column,
        knowledge_date: datetime,
        include_equals: bool = True
    ):
        """Build temporal constraint for queries."""
        if include_equals:
            return known_date_column <= knowledge_date
        else:
            return known_date_column < knowledge_date

    @staticmethod
    def build_effective_constraint(
        effective_from_column,
        effective_to_column,
        target_date: datetime
    ):
        """Build constraint for effective date range."""
        return and_(
            effective_from_column <= target_date,
            or_(
                effective_to_column == None,
                effective_to_column > target_date
            )
        )
