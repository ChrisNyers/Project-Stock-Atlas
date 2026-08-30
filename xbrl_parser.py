"""
XBRL Parser and Normalization

Handles issuer-specific XBRL tag mapping to canonical financial fields.
SEC CompanyFacts uses XBRL concepts that vary by issuer.
"""

from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# XBRL CONCEPT MAPPING
# ============================================================================

# Canonical financial fields and their common XBRL concept mappings
XBRL_CONCEPT_MAPPINGS = {
    # Income Statement
    "revenue": [
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomer",
        "us-gaap:NetRevenue"
    ],
    "gross_profit": [
        "us-gaap:GrossProfit",
        "us-gaap:GrossProfitLoss"
    ],
    "operating_income": [
        "us-gaap:OperatingIncomeLoss",
        "us-gaap:OperatingIncomeOrLoss"
    ],
    "pretax_income": [
        "us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "us-gaap:PreTaxIncome"
    ],
    "taxes": [
        "us-gaap:IncomeTaxExpenseBenefit",
        "us-gaap:TaxExpense"
    ],
    "net_income": [
        "us-gaap:NetIncomeLoss",
        "us-gaap:NetIncomeAttributableToParent"
    ],
    "basic_eps": [
        "us-gaap:EarningsPerShareBasic"
    ],
    "diluted_eps": [
        "us-gaap:EarningsPerShareDiluted"
    ],

    # Cash Flow
    "cash_from_operations": [
        "us-gaap:NetCashProvidedByUsedInOperatingActivities"
    ],
    "capex": [
        "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",
        "us-gaap:CapitalExpenditure"
    ],
    "sbc": [
        "us-gaap:ShareBasedCompensation",
        "us-gaap:StockCompensationExpense"
    ],
    "share_repurchases": [
        "us-gaap:PaymentsForRepurchaseOfCommonStock",
        "us-gaap:RepurchaseOfCapitalStock"
    ],
    "dividends": [
        "us-gaap:PaymentOfDividends"
    ],

    # Balance Sheet
    "cash": [
        "us-gaap:Cash",
        "us-gaap:CashAndCashEquivalentsAtCarryingValue"
    ],
    "marketable_securities": [
        "us-gaap:MarketableSecurities",
        "us-gaap:ShortTermInvestments"
    ],
    "short_term_debt": [
        "us-gaap:CommercialPaper",
        "us-gaap:ShortTermBorrowings",
        "us-gaap:CurrentPortionOfDebt"
    ],
    "long_term_debt": [
        "us-gaap:LongTermDebt",
        "us-gaap:LongTermBorrowings"
    ],
    "shareholders_equity": [
        "us-gaap:StockholdersEquity",
        "us-gaap:ShareholdersEquity"
    ],

    # Shares
    "weighted_average_diluted_shares": [
        "us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding"
    ],
    "period_end_shares": [
        "us-gaap:CommonStockSharesOutstanding",
        "us-gaap:SharesOutstanding"
    ]
}


# ============================================================================
# CONTEXT UTILS
# ============================================================================

def is_quarterly_context(context_id: str) -> bool:
    """Determine if context is quarterly."""
    return "Q1" in context_id or "Q2" in context_id or "Q3" in context_id or "Q4" in context_id


def is_fiscal_year_context(context_id: str) -> bool:
    """Determine if context is fiscal year."""
    return "FY" in context_id or "FI" in context_id or context_id.endswith("0101")


def extract_period_from_context(context_id: str) -> Optional[str]:
    """Extract period type from context ID."""
    if "Q1" in context_id or "Q2" in context_id or "Q3" in context_id or "Q4" in context_id:
        return "QUARTER"
    elif "FY" in context_id or "FI" in context_id:
        return "FISCAL_YEAR"
    return None


# ============================================================================
# XBRL PARSER
# ============================================================================

class XBRLParser:
    """
    Parse XBRL tagged data from SEC CompanyFacts.
    Handle issuer-specific variations.
    """

    def __init__(self, db: Session = None):
        self.db = db

    def parse_company_facts(
        self,
        company_facts: Dict[str, Any],
        cik: str,
        period_end_filter: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Parse company facts JSON from SEC.

        Args:
            company_facts: SEC CompanyFacts JSON response
            cik: Company CIK
            period_end_filter: Optional period end date filter (YYYY-MM-DD)

        Returns:
            Dict mapping canonical field -> list of extracted facts
        """
        results = {}

        if not company_facts or "facts" not in company_facts:
            logger.warning(f"Invalid company facts for CIK {cik}")
            return results

        facts = company_facts["facts"]

        # Iterate through all taxonomies (us-gaap, ifrs-full, etc)
        for taxonomy, concepts in facts.items():
            for concept_id, concept_data in concepts.items():
                canonical_field = self._map_concept_to_canonical(concept_id)

                if canonical_field:
                    normalized_values = self._extract_values(
                        canonical_field,
                        concept_data,
                        period_end_filter
                    )

                    if normalized_values:
                        if canonical_field not in results:
                            results[canonical_field] = []
                        results[canonical_field].extend(normalized_values)

        return results

    def _map_concept_to_canonical(self, concept_id: str) -> Optional[str]:
        """
        Map XBRL concept to canonical field.

        Args:
            concept_id: XBRL concept (e.g., "us-gaap:Revenues")

        Returns:
            Canonical field name or None
        """
        for canonical_field, xbrl_concepts in XBRL_CONCEPT_MAPPINGS.items():
            if concept_id in xbrl_concepts:
                return canonical_field

        logger.debug(f"Unmapped XBRL concept: {concept_id}")
        return None

    def _extract_values(
        self,
        canonical_field: str,
        concept_data: Dict,
        period_end_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Extract values from concept data.

        Args:
            canonical_field: Canonical field name
            concept_data: Concept data from SEC
            period_end_filter: Optional filter

        Returns:
            List of extracted values with metadata
        """
        results = []

        if "units" not in concept_data:
            return results

        # Iterate through units (USD, shares, etc)
        for unit, unit_data in concept_data["units"].items():
            if not isinstance(unit_data, list):
                continue

            for entry in unit_data:
                # Skip if has future dates (not applicable)
                if entry.get("end") is None:
                    continue

                # Apply period filter if provided
                if period_end_filter and entry.get("end") != period_end_filter:
                    continue

                # Only use latest/consolidated values
                if entry.get("filed") is None or entry.get("value") is None:
                    continue

                results.append({
                    "canonical_field": canonical_field,
                    "raw_value": entry.get("value"),
                    "normalized_value": self._normalize_value(entry.get("value"), unit),
                    "unit": self._normalize_unit(unit),
                    "start_date": entry.get("start"),
                    "end_date": entry.get("end"),
                    "filed_date": entry.get("filed"),
                    "context": entry.get("fy", entry.get("form", "unknown")),
                    "accession": entry.get("accession")
                })

        return results

    def _normalize_value(self, value: Any, unit: str) -> float:
        """
        Normalize value from XBRL.
        SEC delivers most financial values in thousands.

        Args:
            value: Raw value
            unit: Unit string (e.g., "USD", "USD/shares")

        Returns:
            Normalized float
        """
        try:
            float_value = float(value)

            # Most SEC filings are in thousands for financial statements
            if unit == "USD" or "USD" in unit:
                # Multiply by 1000 to get actual value
                return float_value * 1000

            return float_value
        except (ValueError, TypeError):
            logger.error(f"Cannot normalize value: {value} (unit: {unit})")
            return 0.0

    def _normalize_unit(self, unit: str) -> str:
        """
        Normalize unit string.

        Args:
            unit: Unit string from XBRL

        Returns:
            Canonical unit
        """
        if "USD" in unit or unit == "USD":
            return "currency_usd"
        elif "shares" in unit.lower():
            return "shares"
        else:
            return unit.lower()


# ============================================================================
# XBRL MAPPING MANAGEMENT
# ============================================================================

class XBRLMappingManager:
    """Manage issuer-specific XBRL mappings."""

    def __init__(self, db: Session = None):
        self.db = db
        self.mappings = {}

    def register_issuer_mapping(
        self,
        issuer_id: str,
        xbrl_concept: str,
        canonical_field: str,
        confidence: float = 1.0,
        notes: Optional[str] = None
    ):
        """
        Register custom mapping for issuer.

        Args:
            issuer_id: Issuer identifier
            xbrl_concept: XBRL concept tag
            canonical_field: Canonical field name
            confidence: Mapping confidence (0.0-1.0)
            notes: Optional mapping notes
        """
        key = f"{issuer_id}:{xbrl_concept}"
        self.mappings[key] = {
            "canonical_field": canonical_field,
            "confidence": confidence,
            "notes": notes,
            "effective_date": "2024-01-01"
        }

    def get_mapping(self, issuer_id: str, xbrl_concept: str) -> Optional[Dict]:
        """Get mapping for issuer/concept."""
        key = f"{issuer_id}:{xbrl_concept}"
        return self.mappings.get(key)
