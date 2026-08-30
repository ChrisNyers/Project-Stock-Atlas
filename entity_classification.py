"""
Entity archetype + SEC filing-regime classification.

Phase 4A.5.1A: this logic was proven in the multi-security benchmark
(benchmark_4a5_1.py) and is now promoted to a core module so that SEC routing
does not depend on benchmark-specific if/else code.

A filer is routed to a broad SEC evidence archetype from three observable,
deterministic signals in its ``submissions`` JSON:
    - entityType         ("operating" | "other" | ...)
    - sic / sicDescription
    - the set of form types it actually files

No issuer names, tickers, or CIKs are ever used to classify.

The archetype then selects a FilingRegime (which family of forms carries the
periodic financial evidence). Corporate filers use 10-K / 10-Q; registered
investment companies (ETFs, mutual funds) use N-CEN / NPORT-P and have no
us-gaap CompanyFacts.
"""

from enum import Enum
from typing import Optional, Tuple


class EntityArchetype(str, Enum):
    OPERATING_COMPANY = "OPERATING_COMPANY"
    FINANCIAL_BANK = "FINANCIAL_BANK"
    REIT = "REIT"
    INSURANCE = "INSURANCE"
    INVESTMENT_COMPANY_ETF = "INVESTMENT_COMPANY_ETF"
    UNCLASSIFIED = "UNCLASSIFIED"


class FilingRegime(str, Enum):
    # Periodic financial evidence carried by 10-K (annual) + 10-Q (interim).
    SEC_CORPORATE = "SEC_CORPORATE"
    # Periodic evidence carried by N-CEN (annual) + NPORT-P (holdings); no
    # us-gaap CompanyFacts.
    SEC_INVESTMENT_COMPANY = "SEC_INVESTMENT_COMPANY"
    # Archetype could not be resolved -> no regime asserted.
    UNKNOWN = "UNKNOWN"


# Forms that only registered investment companies file.
INVESTMENT_COMPANY_FORMS = {
    "N-CEN", "NPORT-P", "N-PORT", "NPORT-EX", "N-CSR", "N-CSRS", "485BPOS", "485APOS",
    "497", "497K", "24F-2NT", "NSAR-U", "NSAR-B", "N-30D", "N-1A",
}

# SIC codes for depository / commercial / investment banks.
BANK_SIC = {"6021", "6022", "6020", "6029", "6199", "6120", "6712"}

# SIC codes for insurance carriers / agents.
INSURANCE_SIC = {"6311", "6321", "6331", "6411", "6351", "6361"}

# SIC code for real-estate investment trusts.
REIT_SIC = {"6798"}

# Which form types carry the periodic financial evidence for each regime.
REGIME_FORMS = {
    FilingRegime.SEC_CORPORATE: {
        "annual": ["10-K"],
        "interim": ["10-Q"],
    },
    FilingRegime.SEC_INVESTMENT_COMPANY: {
        "annual": ["N-CEN", "N-CSR", "N-CSRS", "24F-2NT", "485BPOS"],
        "holdings": ["NPORT-P", "N-PORT", "NPORT-EX"],
    },
}


def _forms_of(submissions: dict) -> set:
    return set(((submissions or {}).get("filings", {}).get("recent", {}) or {}).get("form", []) or [])


def _classify(submissions: dict) -> Tuple[EntityArchetype, str]:
    """Core classifier. Returns (archetype, human-readable reason)."""
    subs = submissions or {}
    etype = (subs.get("entityType") or "").strip().lower()
    sic = str(subs.get("sic") or "").strip()
    sic_desc = (subs.get("sicDescription") or "").strip()
    forms = _forms_of(subs)
    has_10k = "10-K" in forms
    has_10q = "10-Q" in forms

    if not (has_10k or has_10q) and (forms & INVESTMENT_COMPANY_FORMS):
        return EntityArchetype.INVESTMENT_COMPANY_ETF, (
            f"no 10-K/10-Q; files investment-company forms "
            f"({sorted(forms & INVESTMENT_COMPANY_FORMS)[:5]}); entityType={etype!r}"
        )
    if etype == "other" and not has_10k and not has_10q:
        return EntityArchetype.INVESTMENT_COMPANY_ETF, "entityType='other', no 10-K/10-Q"

    if sic in BANK_SIC or "bank" in sic_desc.lower():
        return EntityArchetype.FINANCIAL_BANK, f"SIC {sic} ({sic_desc})"
    if sic in REIT_SIC or "real estate investment trust" in sic_desc.lower():
        return EntityArchetype.REIT, f"SIC {sic} ({sic_desc})"
    if sic in INSURANCE_SIC or "insurance" in sic_desc.lower():
        return EntityArchetype.INSURANCE, f"SIC {sic} ({sic_desc})"

    if etype == "operating" and (has_10k or has_10q):
        return EntityArchetype.OPERATING_COMPANY, f"entityType='operating', SIC {sic} ({sic_desc})"

    return EntityArchetype.UNCLASSIFIED, (
        f"entityType={etype!r}, SIC {sic!r} ({sic_desc!r}), forms={sorted(forms)[:6]}"
    )


def classify_entity(submissions: dict) -> Tuple[EntityArchetype, str]:
    """Typed core API: (EntityArchetype, reason)."""
    return _classify(submissions)


def filing_regime_for(archetype) -> FilingRegime:
    """Map an archetype to the SEC filing regime that carries its periodic
    financial evidence."""
    a = getattr(archetype, "value", archetype)
    if a == EntityArchetype.INVESTMENT_COMPANY_ETF.value:
        return FilingRegime.SEC_INVESTMENT_COMPANY
    if a == EntityArchetype.UNCLASSIFIED.value:
        return FilingRegime.UNKNOWN
    return FilingRegime.SEC_CORPORATE


# ---------------------------------------------------------------------------
# Backward-compatible string API (used by benchmark_4a5_1.py verbatim)
# ---------------------------------------------------------------------------
def classify_archetype(subs: dict) -> Tuple[str, str]:
    """String-valued classifier, signature-compatible with the original
    benchmark helper. Returns (archetype_str, reason)."""
    arch, reason = _classify(subs)
    return arch.value, reason


def discover_regime(archetype, adapter, cik):
    """Return (regime_label, primary_filing, secondary_filing, notes).

    Signature-compatible with the original benchmark helper. ``primary`` is the
    latest annual-evidence filing, ``secondary`` the latest interim/holdings
    filing.
    """
    a = getattr(archetype, "value", archetype)
    notes = []
    if a == EntityArchetype.INVESTMENT_COMPANY_ETF.value:
        ncen = adapter.get_recent_filings(cik, "N-CEN", 1)
        nport = adapter.get_recent_filings(cik, "NPORT-P", 1) or adapter.get_recent_filings(cik, "N-PORT", 1)
        primary = ncen[0] if ncen else None
        secondary = nport[0] if nport else None
        if not primary and not secondary:
            for alt in ("N-CSR", "24F-2NT", "485BPOS"):
                got = adapter.get_recent_filings(cik, alt, 1)
                if got:
                    primary = got[0]
                    notes.append(f"fell back to {alt}")
                    break
        return "INVESTMENT_COMPANY (N-CEN annual + NPORT-P holdings)", primary, secondary, notes

    tk = adapter.get_recent_filings(cik, "10-K", 1)
    tq = adapter.get_recent_filings(cik, "10-Q", 1)
    return "OPERATING (10-K annual + 10-Q interim)", (tk[0] if tk else None), (tq[0] if tq else None), notes


def discover_filing_regime(archetype, adapter, cik) -> dict:
    """Typed core API. Returns a structured routing result."""
    regime = filing_regime_for(archetype)
    label, primary, secondary, notes = discover_regime(archetype, adapter, cik)
    return {
        "regime": regime.value,
        "regime_label": label,
        "primary_filing": primary,
        "secondary_filing": secondary,
        "notes": notes,
        "annual_forms": REGIME_FORMS.get(regime, {}).get("annual", []),
        "interim_or_holdings_forms": (
            REGIME_FORMS.get(regime, {}).get("interim")
            or REGIME_FORMS.get(regime, {}).get("holdings")
            or []
        ),
    }
