"""
Freeze Infrastructure and Source Authority Registry

Freeze: Immutable snapshot of evidence state with cryptographic hash.
Registry: Queryable source precedence and requirements.
"""

import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session

from database import (
    EvidenceFreezeORM, CanonicalFactORM, EvidenceRecordORM,
    SourceAuthorityRegistryORM, FreshnessPolicyRegistryORM
)

from models import DecisionAuthority, VerificationStatus


# ============================================================================
# FREEZE INFRASTRUCTURE
# ============================================================================

class FreezeManager:
    """
    Create and verify immutable evidence freezes.
    Freezes preserve evidence state at a point in time.
    Hash detects any mutation.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_evidence_freeze(
        self,
        security_id: str,
        atlas_version: str = "1.0",
        schema_version: str = "1.0",
        created_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> EvidenceFreezeORM:
        """
        Create immutable freeze of current evidence state.

        Args:
            security_id: Security ID
            atlas_version: Atlas system version
            schema_version: Database schema version
            created_by: User/process creating freeze
            notes: Optional notes

        Returns:
            EvidenceFreezeORM with freeze_hash
        """
        # Collect all evidence and canonical facts
        evidence_records = self.db.query(EvidenceRecordORM).filter(
            EvidenceRecordORM.security_id == security_id
        ).all()

        canonical_facts = self.db.query(CanonicalFactORM).filter(
            CanonicalFactORM.security_id == security_id
        ).all()

        # Build manifest
        evidence_manifest = {}
        for evidence in evidence_records:
            evidence_manifest[evidence.evidence_id] = {
                "field": evidence.field_name,
                "value": evidence.normalized_value or evidence.raw_value,
                "source": evidence.source_name,
                "known_date": evidence.known_date.isoformat(),
                "hash": self._hash_evidence(evidence)
            }

        canonical_manifest = {}
        for fact in canonical_facts:
            canonical_manifest[fact.canonical_fact_id] = {
                "field": fact.field_name,
                "value": fact.value,
                "known_date": fact.known_date.isoformat()
            }

        # Create deterministic serialization
        freeze_content = {
            "security_id": security_id,
            "timestamp": datetime.utcnow().isoformat(),
            "atlas_version": atlas_version,
            "schema_version": schema_version,
            "evidence_manifest": evidence_manifest,
            "canonical_manifest": canonical_manifest,
            "evidence_count": len(evidence_records),
            "fact_count": len(canonical_facts)
        }

        # Sort for deterministic serialization (critical for hash reproducibility)
        canonical_json = json.dumps(freeze_content, sort_keys=True, default=str)
        freeze_hash = hashlib.sha256(canonical_json.encode()).hexdigest()

        # Create freeze record
        freeze = EvidenceFreezeORM(
            security_id=security_id,
            security_identity_version="1.0",
            evidence_manifest=evidence_manifest,
            canonical_facts_manifest=canonical_manifest,
            formula_registry_version="1.0",
            source_authority_version="1.0",
            canonical_serialization=canonical_json,
            freeze_hash=freeze_hash,
            atlas_version=atlas_version,
            schema_version=schema_version,
            timestamp=datetime.utcnow(),
            created_by=created_by,
            notes=notes
        )

        self.db.add(freeze)
        self.db.commit()

        return freeze

    def verify_freeze_integrity(self, freeze_id: str) -> bool:
        """
        Verify that freeze has not been mutated.
        Recomputes hash from serialization.

        Args:
            freeze_id: Freeze ID

        Returns:
            True if hash matches, False if mutated
        """
        freeze = self.db.query(EvidenceFreezeORM).filter(
            EvidenceFreezeORM.freeze_id == freeze_id
        ).first()

        if not freeze:
            return False

        # Recompute hash
        canonical_json = freeze.canonical_serialization
        computed_hash = hashlib.sha256(canonical_json.encode()).hexdigest()

        return computed_hash == freeze.freeze_hash

    def _hash_evidence(self, evidence: EvidenceRecordORM) -> str:
        """Compute hash of evidence record."""
        content = json.dumps({
            "field": evidence.field_name,
            "value": str(evidence.normalized_value or evidence.raw_value),
            "source": evidence.source_name,
            "known_date": evidence.known_date.isoformat()
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


# ============================================================================
# SOURCE AUTHORITY REGISTRY
# ============================================================================

class SourceAuthorityRegistry:
    """
    Queryable registry of source precedence and requirements.
    NOT hardcoded throughout application.
    """

    def __init__(self, db: Session):
        self.db = db
        self._initialize_default_registry()

    def _initialize_default_registry(self):
        """Initialize with Sprint 1 defaults."""
        default_rules = [
            {
                "field_name": "revenue",
                "atlas_object": "FinancialState",
                "primary_source": "SEC",
                "secondary_source": "COMPANY_IR",
                "fallback_source": "APPROVED_STRUCTURED_PROVIDER",
                "minimum_decision_authority": DecisionAuthority.DA4,
                "verification_requirement": VerificationStatus.PRIMARY_VERIFIED,
                "point_in_time_required": True,
                "normalization_rule": "REVENUE_CANONICAL_V1"
            },
            {
                "field_name": "cash_from_operations",
                "atlas_object": "FinancialState",
                "primary_source": "SEC",
                "secondary_source": None,
                "fallback_source": None,
                "minimum_decision_authority": DecisionAuthority.DA4,
                "verification_requirement": VerificationStatus.PRIMARY_VERIFIED,
                "point_in_time_required": True,
                "normalization_rule": "CFO_CANONICAL_V1"
            },
            {
                "field_name": "capex",
                "atlas_object": "FinancialState",
                "primary_source": "SEC",
                "secondary_source": None,
                "fallback_source": None,
                "minimum_decision_authority": DecisionAuthority.DA4,
                "verification_requirement": VerificationStatus.PRIMARY_VERIFIED,
                "point_in_time_required": True,
                "normalization_rule": "CAPEX_CANONICAL_V1"
            },
            {
                "field_name": "price",
                "atlas_object": "MarketState",
                "primary_source": "MARKET_DATA",
                "secondary_source": "MARKET_DATA_BACKUP",
                "fallback_source": None,
                "minimum_decision_authority": DecisionAuthority.DA3,
                "verification_requirement": VerificationStatus.CORROBORATED,
                "point_in_time_required": False,
                "normalization_rule": "PRICE_CANONICAL_V1"
            },
            {
                "field_name": "10_year_treasury",
                "atlas_object": "MacroData",
                "primary_source": "FRED",
                "secondary_source": None,
                "fallback_source": None,
                "minimum_decision_authority": DecisionAuthority.DA2,
                "verification_requirement": VerificationStatus.CORROBORATED,
                "point_in_time_required": True,
                "normalization_rule": "TREASURY_CANONICAL_V1"
            }
        ]

        for rule in default_rules:
            existing = self.db.query(SourceAuthorityRegistryORM).filter(
                SourceAuthorityRegistryORM.field_name == rule["field_name"],
                SourceAuthorityRegistryORM.atlas_object == rule["atlas_object"]
            ).first()

            if not existing:
                registry_orm = SourceAuthorityRegistryORM(
                    field_name=rule["field_name"],
                    atlas_object=rule["atlas_object"],
                    primary_source=rule["primary_source"],
                    secondary_source=rule.get("secondary_source"),
                    fallback_source=rule.get("fallback_source"),
                    minimum_decision_authority=rule["minimum_decision_authority"],
                    verification_requirement=rule["verification_requirement"],
                    point_in_time_required=rule["point_in_time_required"],
                    normalization_rule=rule["normalization_rule"]
                )
                self.db.add(registry_orm)

        self.db.commit()

    def get_rule(
        self,
        field_name: str,
        atlas_object: str
    ) -> Optional[SourceAuthorityRegistryORM]:
        """
        Get authority rule for field.

        Args:
            field_name: Field name
            atlas_object: Object type (FinancialState, MarketState, etc)

        Returns:
            Registry rule or None
        """
        return self.db.query(SourceAuthorityRegistryORM).filter(
            SourceAuthorityRegistryORM.field_name == field_name,
            SourceAuthorityRegistryORM.atlas_object == atlas_object,
            SourceAuthorityRegistryORM.effective_to == None
        ).first()

    def validate_source_authority(
        self,
        field_name: str,
        atlas_object: str,
        source_tier: DecisionAuthority,
        verification_status: VerificationStatus
    ) -> bool:
        """
        Validate that source meets requirements for field.

        Args:
            field_name: Field name
            atlas_object: Object type
            source_tier: Source decision authority
            verification_status: Verification status

        Returns:
            True if valid, False otherwise
        """
        rule = self.get_rule(field_name, atlas_object)
        if not rule:
            return False

        # Check decision authority
        if source_tier.value < rule.minimum_decision_authority.value:
            return False

        # Check verification
        if verification_status.value < rule.verification_requirement.value:
            return False

        return True


# ============================================================================
# FRESHNESS POLICY REGISTRY
# ============================================================================

class FreshnessPolicyRegistry:
    """
    Define when data becomes stale.
    Critical for investment readiness decisions.
    """

    def __init__(self, db: Session):
        self.db = db
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """Initialize with Sprint 1 defaults."""
        default_policies = [
            {
                "field_name": "price",
                "atlas_object": "MarketState",
                "maximum_age_hours": 24,
                "acceptable_age_hours": 4,
                "source_type": "MARKET_DATA"
            },
            {
                "field_name": "revenue",
                "atlas_object": "FinancialState",
                "maximum_age_hours": 8760,  # 1 year
                "acceptable_age_hours": 2160,  # 3 months
                "source_type": "SEC"
            },
            {
                "field_name": "10_year_treasury",
                "atlas_object": "MacroData",
                "maximum_age_hours": 48,
                "acceptable_age_hours": 24,
                "source_type": "FRED"
            }
        ]

        for policy in default_policies:
            existing = self.db.query(FreshnessPolicyRegistryORM).filter(
                FreshnessPolicyRegistryORM.field_name == policy["field_name"],
                FreshnessPolicyRegistryORM.atlas_object == policy["atlas_object"]
            ).first()

            if not existing:
                policy_orm = FreshnessPolicyRegistryORM(
                    field_name=policy["field_name"],
                    atlas_object=policy["atlas_object"],
                    maximum_age_hours=policy["maximum_age_hours"],
                    acceptable_age_hours=policy.get("acceptable_age_hours"),
                    source_type=policy["source_type"]
                )
                self.db.add(policy_orm)

        self.db.commit()

    def get_policy(
        self,
        field_name: str,
        atlas_object: str
    ) -> Optional[FreshnessPolicyRegistryORM]:
        """Get freshness policy for field."""
        return self.db.query(FreshnessPolicyRegistryORM).filter(
            FreshnessPolicyRegistryORM.field_name == field_name,
            FreshnessPolicyRegistryORM.atlas_object == atlas_object,
            FreshnessPolicyRegistryORM.effective_to == None
        ).first()

    def is_data_stale(
        self,
        field_name: str,
        atlas_object: str,
        data_timestamp: datetime
    ) -> bool:
        """
        Check if data is stale based on policy.

        Args:
            field_name: Field name
            atlas_object: Object type
            data_timestamp: Timestamp of data

        Returns:
            True if stale, False otherwise
        """
        policy = self.get_policy(field_name, atlas_object)
        if not policy:
            return False

        age_seconds = (datetime.utcnow() - data_timestamp).total_seconds()
        age_hours = age_seconds / 3600

        return age_hours > policy.maximum_age_hours
