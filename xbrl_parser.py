"""
XBRL Parser and Normalization

Handles issuer-specific XBRL tag mapping to canonical financial fields.
SEC CompanyFacts uses XBRL concepts that vary by issuer.
"""

from typing import Optional, Dict, List, Any
from datetime import date
from enum import Enum
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# XBRL CONCEPT MAPPING
# ============================================================================

# Canonical financial fields and their APPROVED XBRL concept families.
#
# Governing rule (Phase 4A.5.0): a canonical Stock Atlas field is an economic
# concept, never permanently bound to a single XBRL tag. Each family is an
# ORDERED priority list; selection searches only within the family and records
# the exact concept actually used in provenance (see select_canonical_fact).
XBRL_CONCEPT_MAPPINGS = {
    # Income Statement
    "revenue": [
        # ASC 606 revenue, net of assessed (sales/VAT) taxes — the modern default.
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        # ASC 606 revenue, gross of assessed taxes (some issuers file this instead).
        "us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax",
        # Pre-ASC-606 / legacy aggregate revenue tag.
        "us-gaap:Revenues",
        # Older ASC 606 aggregate + legacy alternatives already in the taxonomy.
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


# Period type each canonical field must be reported as:
#   "duration" -> flow measured over a period (income statement / cash flow); the
#                 XBRL fact carries a `start` and an `end`.
#   "instant"  -> stock measured at a point in time (balance sheet); the XBRL fact
#                 carries only an `end`.
CANONICAL_FIELD_PERIOD_TYPE = {
    "revenue": "duration",
    "gross_profit": "duration",
    "operating_income": "duration",
    "pretax_income": "duration",
    "taxes": "duration",
    "net_income": "duration",
    "basic_eps": "duration",
    "diluted_eps": "duration",
    "cash_from_operations": "duration",
    "capex": "duration",
    "sbc": "duration",
    "share_repurchases": "duration",
    "dividends": "duration",
    "weighted_average_diluted_shares": "duration",
    "cash": "instant",
    "marketable_securities": "instant",
    "short_term_debt": "instant",
    "long_term_debt": "instant",
    "shareholders_equity": "instant",
    "period_end_shares": "instant",
}

# Relative tolerance below which two candidate values are treated as the same
# number (absorbs XBRL rounding only). Larger disagreement between approved
# concepts for the SAME field and SAME period => CONFLICTED, never a silent pick.
_CANONICAL_CONFLICT_REL_TOL = 1e-4


# ============================================================================
# PERIOD GRANULARITY (Phase 4A.5.1A)
# ============================================================================
#
# SEC CompanyFacts routinely carries OVERLAPPING duration contexts that share
# the same period_end: e.g. a 10-Q reports both the current fiscal quarter
# (~3 months) and the fiscal year-to-date (6 or 9 months). Filtering on
# period_end + period_type alone is not enough — the caller must state which
# duration it wants. select_canonical_fact() must never silently return YTD when
# a quarter was requested (and vice versa).
#
# Granularity is classified DETERMINISTICALLY from the fact's own (start, end)
# span in days, never from context ordering or "earliest start wins".

class PeriodGranularity(str, Enum):
    ANNUAL = "ANNUAL"            # full fiscal year (~365 days)
    QUARTER = "QUARTER"          # a single fiscal quarter (~91 days)
    YEAR_TO_DATE = "YEAR_TO_DATE"  # fiscal-year start .. period end (H1 ~182, 9M ~273)
    INSTANT = "INSTANT"          # balance-sheet point in time (no start)


class PeriodIntentError(ValueError):
    """Raised by the production selection boundary when a duration financial
    fact is requested without an explicit period intent (ANNUAL / QUARTER /
    YEAR_TO_DATE). Fail closed — never silently fall through to earliest-start."""


# --- classification aid: broad day-span buckets (Phase 4A.5.1A) --------------
# These are TECHNICAL HEURISTICS, not accounting truth. They are used for
# provenance display and as a coarse hint. Confident matching for selection goes
# through classify_period() below, which additionally requires the fact's own
# SEC fiscal-period metadata (`fp`) to agree.
_QUARTER_MAX_DAYS = 105
_YTD_MAX_DAYS = 315
_ANNUAL_MAX_DAYS = 380

# --- confident classification windows (Phase 4A.5.1B) -----------------------
# Tight day-count windows around the STANDARD reporting periods. A duration that
# lands in none of these windows is NOT confidently classifiable -> fail closed.
# (13-week quarter = 91d, 14-week = 98d; H1 ~182d; 9-month ~273d; 52-week year
#  = 364d, 53-week = 371d, calendar leap year = 366d.)
_STD_QUARTER_DAYS = (78, 102)
_STD_H1_DAYS = (167, 197)
_STD_9M_DAYS = (258, 288)
_STD_ANNUAL_DAYS = (350, 380)


def _parse_iso_date(s: Optional[str]) -> Optional[date]:
    if not s or not isinstance(s, str):
        return None
    try:
        return date(int(s[0:4]), int(s[5:7]), int(s[8:10]))
    except (ValueError, IndexError):
        return None


def _span_days(start: Optional[str], end: Optional[str]) -> Optional[int]:
    ds, de = _parse_iso_date(start), _parse_iso_date(end)
    if ds is None or de is None:
        return None
    span = (de - ds).days
    return span if span > 0 else None


def _in(window, n) -> bool:
    return window[0] <= n <= window[1]


def duration_granularity(start: Optional[str], end: Optional[str]) -> Optional[str]:
    """Coarse classification aid: bucket a duration by day-span alone.

    Returns None if start is missing (an instant), dates cannot be parsed, or the
    span exceeds a fiscal year. NOT used for selection matching — see
    classify_period(). Kept for provenance display and backward compatibility."""
    span = _span_days(start, end)
    if span is None:
        return None
    if span <= _QUARTER_MAX_DAYS:
        return PeriodGranularity.QUARTER.value
    if span <= _YTD_MAX_DAYS:
        return PeriodGranularity.YEAR_TO_DATE.value
    if span <= _ANNUAL_MAX_DAYS:
        return PeriodGranularity.ANNUAL.value
    return None  # multi-year


def classify_period(fact: Dict) -> set:
    """Confidently classify an XBRL fact into the set of period granularities it
    can satisfy. Empty set => NOT confidently classifiable => fail closed.

    Uses the fact's own duration together with its SEC fiscal-period tag (`fp`,
    one of Q1/Q2/Q3/Q4/FY) when present:

      - instant fact (no start)                         -> {INSTANT}
      - standard-quarter duration                       -> {QUARTER}
          and if fp == "Q1"                             -> {QUARTER, YEAR_TO_DATE}
      - standard H1 / 9-month duration                  -> {YEAR_TO_DATE}
      - standard fiscal-year duration                   -> {ANNUAL}
      - fp present but inconsistent with the duration   -> {}  (fail closed)
      - unusual / stub / transition length              -> {}  (fail closed)

    Deliberately narrow: an unusual duration is NOT classified just because its
    length is under some broad upper bound.
    """
    if not fact.get("start"):
        return {PeriodGranularity.INSTANT.value}

    span = _span_days(fact.get("start"), fact.get("end"))
    if span is None:
        return set()
    fp = str(fact.get("fp") or "").strip().upper()

    is_quarter = _in(_STD_QUARTER_DAYS, span)
    is_h1 = _in(_STD_H1_DAYS, span)
    is_9m = _in(_STD_9M_DAYS, span)
    is_annual = _in(_STD_ANNUAL_DAYS, span)

    if fp == "FY":
        # A fiscal-year filing's flow fact must be an annual duration.
        return {PeriodGranularity.ANNUAL.value} if is_annual else set()

    if fp in ("Q1", "Q2", "Q3", "Q4"):
        if is_quarter:
            out = {PeriodGranularity.QUARTER.value}
            if fp == "Q1":
                out.add(PeriodGranularity.YEAR_TO_DATE.value)  # Q1 quarter == Q1 YTD
            return out
        if is_h1 or is_9m:
            return {PeriodGranularity.YEAR_TO_DATE.value}
        if is_annual:
            return {PeriodGranularity.ANNUAL.value}  # a 10-Q may still carry the prior FY
        return set()  # fp says interim, duration says stub -> fail closed

    # fp absent/unknown: classify only clearly-standard lengths.
    if is_quarter:
        return {PeriodGranularity.QUARTER.value}
    if is_h1 or is_9m:
        return {PeriodGranularity.YEAR_TO_DATE.value}
    if is_annual:
        return {PeriodGranularity.ANNUAL.value}
    return set()  # no fp + non-standard length -> fail closed


def _normalize_granularity(g) -> Optional[str]:
    if g is None:
        return None
    return str(getattr(g, "value", g)).strip().upper()


def _fact_satisfies_granularity(fact: Dict, requested: str) -> bool:
    """Does this fact CONFIDENTLY match the requested period granularity?
    Fails closed: an ambiguous / stub duration matches nothing."""
    return requested in classify_period(fact)


def _split_concept_id(concept_id: str):
    """'us-gaap:Revenues' -> ('us-gaap', 'Revenues'); bare name -> ('us-gaap', name)."""
    if ":" in concept_id:
        taxonomy, name = concept_id.split(":", 1)
        return taxonomy, name
    return "us-gaap", concept_id


def _fact_period_type(fact: Dict) -> str:
    return "duration" if fact.get("start") else "instant"


def select_canonical_fact(
    company_facts: Dict[str, Any],
    canonical_field: str,
    *,
    accession: Optional[str] = None,
    period_end: Optional[str] = None,
    period_start: Optional[str] = None,
    period_type: Optional[str] = None,
    period_granularity: Optional[str] = None,
    unit: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolve a canonical Stock Atlas field to ONE authoritative SEC XBRL fact.

    Searches ONLY the field's approved concept family (XBRL_CONCEPT_MAPPINGS), in
    priority order, over the SEC CompanyFacts JSON. Applies the Phase 4A.5.0
    selection rule:

      1. approved concept family only
      2. fact must match the intended filing (accession), when given
      3. fact must match the reporting period (period_end / period_start)
      4. fact must match the required period type (duration vs instant)
      5. unit must be compatible (when a unit is required)
      6. one fact is chosen by approved priority (highest-priority concept that
         has a match; deterministic within a concept)
      7. full provenance is preserved, including the EXACT concept used

    Never sums or averages alternative concepts. If two approved concepts give
    materially different values for the same field + same exact period, the
    result status is "CONFLICTED" (the numbers are surfaced, none is silently
    chosen to make anything pass).

    ``period_granularity`` (Phase 4A.5.1A) makes the requested duration explicit:
    "ANNUAL" | "QUARTER" | "YEAR_TO_DATE" | "INSTANT" (or the PeriodGranularity
    enum). When set, only facts whose own (start,end) day-span classifies to that
    granularity are eligible — so a QUARTER request can never fall through to a
    year-to-date context, and vice versa. When omitted, behavior is unchanged
    (period_end + period_type filtering only).

    Returns a dict with:
      status: "SELECTED" | "CONFLICTED" | "UNAVAILABLE"
      and, when not UNAVAILABLE: concept, taxonomy, unit, raw_value,
      normalized_value, period_start, period_end, period_type,
      period_granularity, requested_granularity, accession, form,
      fy, fp, frame, filed, candidates[], conflict
    """
    requested_granularity = _normalize_granularity(period_granularity)
    if requested_granularity is not None and period_type is None:
        period_type = "instant" if requested_granularity == PeriodGranularity.INSTANT.value else "duration"

    family = XBRL_CONCEPT_MAPPINGS.get(canonical_field)
    if not family:
        return {
            "canonical_field": canonical_field,
            "status": "UNAVAILABLE",
            "reason": f"No approved concept family defined for '{canonical_field}'",
        }

    if period_type is None:
        period_type = CANONICAL_FIELD_PERIOD_TYPE.get(canonical_field)

    facts_root = (company_facts or {}).get("facts", {})

    def _matches(fact: Dict) -> bool:
        if fact.get("val") is None:
            return False
        if accession is not None and fact.get("accn") != accession:
            return False
        if period_end is not None and fact.get("end") != period_end:
            return False
        if period_start is not None and fact.get("start") != period_start:
            return False
        if period_type is not None and _fact_period_type(fact) != period_type:
            return False
        if requested_granularity is not None and not _fact_satisfies_granularity(fact, requested_granularity):
            return False
        return True

    # Collect matches per concept, preserving family priority.
    per_concept = []  # [(concept_id, [fact + _unit/_concept]), ...]
    for concept_id in family:
        taxonomy, name = _split_concept_id(concept_id)
        cdata = facts_root.get(taxonomy, {}).get(name)
        if not cdata or "units" not in cdata:
            continue
        matches = []
        for u, flist in cdata["units"].items():
            if unit is not None and u != unit:
                continue
            if not isinstance(flist, list):
                continue
            for fact in flist:
                if not _matches(fact):
                    continue
                m = dict(fact)
                m["_unit"] = u
                m["_concept"] = f"{taxonomy}:{name}"
                matches.append(m)
        if matches:
            matches.sort(key=lambda m: (m.get("start") or "", m.get("end") or "", m["_unit"]))
            per_concept.append((f"{taxonomy}:{name}", matches))

    if not per_concept:
        return {
            "canonical_field": canonical_field,
            "status": "UNAVAILABLE",
            "period_type": period_type,
            "requested_granularity": requested_granularity,
            "reason": (
                "No fact in the approved concept family "
                f"{family} matches accession={accession}, period_end={period_end}, "
                f"period_start={period_start}, period_type={period_type}, "
                f"period_granularity={requested_granularity}, unit={unit}"
            ),
        }

    sel_concept, sel_matches = per_concept[0]
    selected = sel_matches[0]
    sel_period = (selected.get("start"), selected.get("end"))

    def _material(a: float, b: float) -> bool:
        if a == b:
            return False
        scale = max(abs(a), abs(b), 1.0)
        return abs(a - b) / scale > _CANONICAL_CONFLICT_REL_TOL

    conflict = None

    # (a) selected concept disagrees with itself for the SAME exact period
    same_period_vals = sorted({
        float(m["val"]) for m in sel_matches
        if (m.get("start"), m.get("end")) == sel_period
    })
    if len(same_period_vals) > 1 and _material(same_period_vals[0], same_period_vals[-1]):
        conflict = {
            "kind": "intra_concept",
            "concept": sel_concept,
            "period": {"start": sel_period[0], "end": sel_period[1]},
            "values": same_period_vals,
        }

    # (b) a lower-priority approved concept materially disagrees for the SAME period
    for other_concept, other_matches in per_concept[1:]:
        for m in other_matches:
            if (m.get("start"), m.get("end")) != sel_period:
                continue
            if _material(float(selected["val"]), float(m["val"])):
                conflict = conflict or {"kind": "cross_concept", "competing": []}
                conflict.setdefault("competing", []).append({
                    "concept": other_concept,
                    "unit": m["_unit"],
                    "value": float(m["val"]),
                })

    return {
        "canonical_field": canonical_field,
        "status": "CONFLICTED" if conflict else "SELECTED",
        "concept": sel_concept,
        "taxonomy": sel_concept.split(":", 1)[0],
        "unit": selected["_unit"],
        "raw_value": selected.get("val"),
        # SEC CompanyFacts delivers values in native units (already unscaled),
        # unlike raw XBRL instance documents. No thousands multiplier here.
        "normalized_value": float(selected["val"]),
        "normalization": "companyfacts_native_units",
        "period_start": selected.get("start"),
        "period_end": selected.get("end"),
        "period_type": _fact_period_type(selected),
        "period_granularity": (
            PeriodGranularity.INSTANT.value if not selected.get("start")
            else duration_granularity(selected.get("start"), selected.get("end"))
        ),
        "period_classification": sorted(classify_period(selected)),
        "requested_granularity": requested_granularity,
        "accession": selected.get("accn"),
        "form": selected.get("form"),
        "fy": selected.get("fy"),
        "fp": selected.get("fp"),
        "frame": selected.get("frame"),
        "filed": selected.get("filed"),
        "candidates": [
            {
                "concept": c,
                "unit": m["_unit"],
                "value": m.get("val"),
                "start": m.get("start"),
                "end": m.get("end"),
                "accession": m.get("accn"),
                "form": m.get("form"),
            }
            for c, ms in per_concept for m in ms
        ],
        "conflict": conflict,
    }


# ============================================================================
# PRODUCTION SELECTION BOUNDARY (Phase 4A.5.1B)
# ============================================================================
#
# select_canonical_fact() keeps its backward-compatible implicit path (period_end
# only -> earliest-start) for the frozen v3 harness and other already-tested
# callers. NEW production ingestion and NEW benchmark code MUST go through this
# boundary instead, which forces period intent to be explicit and fails closed.

_DURATION_GRANULARITIES = {
    PeriodGranularity.ANNUAL.value,
    PeriodGranularity.QUARTER.value,
    PeriodGranularity.YEAR_TO_DATE.value,
}


def select_canonical_fact_production(
    company_facts: Dict[str, Any],
    canonical_field: str,
    *,
    period_granularity,
    accession: Optional[str] = None,
    period_end: Optional[str] = None,
    period_start: Optional[str] = None,
    unit: Optional[str] = None,
) -> Dict[str, Any]:
    """Production-facing canonical-fact selection. ``period_granularity`` is
    REQUIRED (no default).

    - A duration field (revenue, cash_from_operations, ...) MUST be requested
      with ANNUAL / QUARTER / YEAR_TO_DATE. Passing None or INSTANT for a
      duration field raises PeriodIntentError (fail closed — never silently
      earliest-start / YTD).
    - An instant field (cash, long_term_debt, ...) MUST be requested with
      INSTANT.

    On a granularity/field-type mismatch: PeriodIntentError. Otherwise delegates
    to select_canonical_fact() with the explicit granularity, so a stub /
    transition duration that classify_period() cannot confidently place resolves
    to UNAVAILABLE, not a wrong period.
    """
    g = _normalize_granularity(period_granularity)
    field_period_type = CANONICAL_FIELD_PERIOD_TYPE.get(canonical_field)

    if field_period_type == "instant":
        if g != PeriodGranularity.INSTANT.value:
            raise PeriodIntentError(
                f"'{canonical_field}' is an instant (balance-sheet) field; "
                f"period_granularity must be INSTANT, got {g!r}"
            )
    elif field_period_type == "duration":
        if g not in _DURATION_GRANULARITIES:
            raise PeriodIntentError(
                f"'{canonical_field}' is a duration (flow) field; production "
                f"requests must state period intent explicitly as one of "
                f"{sorted(_DURATION_GRANULARITIES)}, got {g!r}"
            )
    else:
        # Unknown field: require SOME explicit intent rather than guess.
        if g not in _DURATION_GRANULARITIES and g != PeriodGranularity.INSTANT.value:
            raise PeriodIntentError(
                f"period_granularity must be explicit for '{canonical_field}', got {g!r}"
            )

    result = select_canonical_fact(
        company_facts, canonical_field,
        accession=accession, period_end=period_end, period_start=period_start,
        period_granularity=g, unit=unit,
    )
    result["selection_boundary"] = "production"
    return result


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
