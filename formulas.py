"""
FormulaRegistry and deterministic formula execution.

All formulas versioned and immutable.
New methodology = new version.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from database import FormulaRegistryORM, CanonicalFactORM, CalculationRecordORM

logger = logging.getLogger(__name__)


# ============================================================================
# FORMULA DEFINITIONS
# ============================================================================

FORMULAS = {
    "F_FCF_001": {
        "name": "Free Cash Flow",
        "version": "1.0",
        "description": "Operating cash flow minus capital expenditures",
        "inputs": ["cash_from_operations", "capex"],
        "expression": "cash_from_operations - capex",
        "output_unit": "currency"
    },
    "F_FCF_MARGIN_001": {
        "name": "FCF Margin",
        "version": "1.0",
        "description": "FCF divided by revenue",
        "inputs": ["fcf", "revenue"],
        "expression": "fcf / revenue" if "fcf" and "revenue" else None,
        "output_unit": "ratio"
    },
    "F_GROSS_MARGIN_001": {
        "name": "Gross Margin",
        "version": "1.0",
        "description": "Gross profit divided by revenue",
        "inputs": ["gross_profit", "revenue"],
        "expression": "gross_profit / revenue",
        "output_unit": "ratio"
    },
    "F_OPERATING_MARGIN_001": {
        "name": "Operating Margin",
        "version": "1.0",
        "description": "Operating income divided by revenue",
        "inputs": ["operating_income", "revenue"],
        "expression": "operating_income / revenue",
        "output_unit": "ratio"
    },
    "F_REVENUE_GROWTH_001": {
        "name": "Revenue Growth",
        "version": "1.0",
        "description": "Year-over-year revenue growth",
        "inputs": ["revenue_current", "revenue_prior"],
        "expression": "(revenue_current - revenue_prior) / revenue_prior",
        "output_unit": "ratio"
    },
    "F_EPS_GROWTH_001": {
        "name": "EPS Growth",
        "version": "1.0",
        "description": "Year-over-year diluted EPS growth",
        "inputs": ["diluted_eps_current", "diluted_eps_prior"],
        "expression": "(diluted_eps_current - diluted_eps_prior) / diluted_eps_prior",
        "output_unit": "ratio"
    },
    "F_FCF_GROWTH_001": {
        "name": "FCF Growth",
        "version": "1.0",
        "description": "Year-over-year FCF growth",
        "inputs": ["fcf_current", "fcf_prior"],
        "expression": "(fcf_current - fcf_prior) / fcf_prior",
        "output_unit": "ratio"
    },
    "F_NET_DEBT_001": {
        "name": "Net Debt",
        "version": "1.0",
        "description": "Total debt minus cash",
        "inputs": ["short_term_debt", "long_term_debt", "cash"],
        "expression": "short_term_debt + long_term_debt - cash",
        "output_unit": "currency"
    },
    "F_SHARE_COUNT_GROWTH_001": {
        "name": "Share Count Growth",
        "version": "1.0",
        "description": "Year-over-year diluted share count growth",
        "inputs": ["diluted_shares_current", "diluted_shares_prior"],
        "expression": "(diluted_shares_current - diluted_shares_prior) / diluted_shares_prior",
        "output_unit": "ratio"
    },
    "F_SHARE_COUNT_CAGR_001": {
        "name": "Share Count CAGR",
        "version": "1.0",
        "description": "Share count compound annual growth rate",
        "inputs": ["diluted_shares_ending", "diluted_shares_beginning", "years"],
        "expression": "(diluted_shares_ending / diluted_shares_beginning) ** (1 / years) - 1",
        "output_unit": "ratio"
    },
    "F_SBC_REVENUE_001": {
        "name": "SBC / Revenue",
        "version": "1.0",
        "description": "Stock-based compensation as percentage of revenue",
        "inputs": ["sbc", "revenue"],
        "expression": "sbc / revenue",
        "output_unit": "ratio"
    },
    "F_SBC_FCF_001": {
        "name": "SBC / FCF",
        "version": "1.0",
        "description": "Stock-based compensation as percentage of FCF",
        "inputs": ["sbc", "fcf"],
        "expression": "sbc / fcf",
        "output_unit": "ratio"
    },
    "F_NET_BUYBACK_YIELD_001": {
        "name": "Net Buyback Yield",
        "version": "1.0",
        "description": "Net repurchases divided by market cap",
        "inputs": ["share_repurchases", "dividends", "market_cap"],
        "expression": "(share_repurchases - dividends) / market_cap",
        "output_unit": "ratio"
    }
}


# ============================================================================
# FORMULA REGISTRY SERVICE
# ============================================================================

class FormulaRegistry:
    """
    Registry and execution service for deterministic formulas.
    All formulas versioned, immutable, and traceable.
    """

    def __init__(self, db: Session):
        self.db = db
        self.formulas = FORMULAS

    def initialize_registry(self):
        """Initialize formula registry in database."""
        for formula_id, definition in self.formulas.items():
            existing = self.db.query(FormulaRegistryORM).filter(
                FormulaRegistryORM.formula_id == formula_id,
                FormulaRegistryORM.version == definition.get("version", "1.0")
            ).first()

            if not existing:
                formula_orm = FormulaRegistryORM(
                    formula_id=formula_id,
                    name=definition["name"],
                    version=definition.get("version", "1.0"),
                    description=definition.get("description"),
                    inputs=definition.get("inputs", []),
                    expression=definition.get("expression"),
                    output_unit=definition.get("output_unit"),
                    effective_from=datetime.utcnow()
                )
                self.db.add(formula_orm)

        self.db.commit()
        logger.info(f"Initialized {len(self.formulas)} formulas in registry")

    def get_formula(self, formula_id: str, version: Optional[str] = None) -> Optional[Dict]:
        """Get formula definition."""
        if formula_id not in self.formulas:
            return None

        formula = self.formulas[formula_id].copy()
        if version:
            formula["requested_version"] = version
        return formula

    def execute_formula(
        self,
        formula_id: str,
        inputs: Dict[str, float],
        version: str = "1.0"
    ) -> Optional[float]:
        """
        Execute formula with provided inputs.

        Args:
            formula_id: Formula ID (e.g., "F_FCF_001")
            inputs: Dict of input values
            version: Formula version

        Returns:
            Calculated output or None
        """
        formula = self.get_formula(formula_id, version)
        if not formula or not formula.get("expression"):
            logger.error(f"Formula not found: {formula_id} v{version}")
            return None

        try:
            # Build safe evaluation context
            eval_context = {}
            for input_name, value in inputs.items():
                if value is None:
                    return None  # No guessing on missing inputs
                eval_context[input_name] = float(value)

            # Evaluate expression safely
            result = eval(formula["expression"], {"__builtins__": {}}, eval_context)
            return float(result)

        except ZeroDivisionError:
            logger.warning(f"Division by zero in formula {formula_id}")
            return None
        except KeyError as e:
            logger.error(f"Missing input {e} for formula {formula_id}")
            return None
        except Exception as e:
            logger.error(f"Error executing formula {formula_id}: {e}")
            return None

    def calculate_derived_metrics(
        self,
        security_id: str,
        financial_data: Dict[str, float]
    ) -> Dict[str, Optional[float]]:
        """
        Calculate all available derived metrics from financial data.

        Args:
            security_id: Security ID
            financial_data: Dict of financial values

        Returns:
            Dict of formula_id -> calculated value
        """
        results = {}

        for formula_id, formula_def in self.formulas.items():
            required_inputs = formula_def.get("inputs", [])
            available_inputs = {
                name: financial_data[name]
                for name in required_inputs
                if name in financial_data
            }

            if len(available_inputs) == len(required_inputs):
                value = self.execute_formula(formula_id, available_inputs)
                results[formula_id] = value
            else:
                results[formula_id] = None

        return results


# ============================================================================
# METRIC CALCULATION
# ============================================================================

class MetricsCalculator:
    """Calculate financial metrics from canonical facts."""

    def __init__(self, db: Session, formula_registry: FormulaRegistry):
        self.db = db
        self.formula_registry = formula_registry

    def get_financial_metrics(
        self,
        security_id: str,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Get all financial metrics for a security at period end.

        Args:
            security_id: Security ID
            period_end: Period end date

        Returns:
            Dict of metric_id -> value
        """
        # Gather canonical facts
        facts = self.db.query(CanonicalFactORM).filter(
            CanonicalFactORM.security_id == security_id,
            CanonicalFactORM.effective_date <= period_end
        ).all()

        financial_data = {
            fact.field_name: fact.value
            for fact in facts
        }

        # Calculate metrics
        metrics = self.formula_registry.calculate_derived_metrics(security_id, financial_data)

        return metrics


# ============================================================================
# FORMULA VERSIONING
# ============================================================================

def create_formula_version(
    db: Session,
    formula_id: str,
    old_version: str,
    new_version: str,
    new_expression: str,
    reason: str
):
    """
    Create new version of formula.
    Old version kept for historical reference.

    Args:
        db: Database session
        formula_id: Formula ID
        old_version: Previous version
        new_version: New version
        new_expression: Updated expression
        reason: Reason for update
    """
    # Deactivate old version
    old_formula = db.query(FormulaRegistryORM).filter(
        FormulaRegistryORM.formula_id == formula_id,
        FormulaRegistryORM.version == old_version
    ).first()

    if old_formula:
        old_formula.effective_to = datetime.utcnow()

    # Create new version
    new_formula = db.query(FormulaRegistryORM).filter(
        FormulaRegistryORM.formula_id == formula_id
    ).first()

    new_formula_orm = FormulaRegistryORM(
        formula_id=formula_id,
        name=new_formula.name,
        version=new_version,
        description=f"{new_formula.description} (v{new_version}) - {reason}",
        inputs=new_formula.inputs,
        expression=new_expression,
        output_unit=new_formula.output_unit,
        effective_from=datetime.utcnow()
    )

    db.add(new_formula_orm)
    db.commit()

    logger.info(f"Created formula version: {formula_id} v{new_version}")
