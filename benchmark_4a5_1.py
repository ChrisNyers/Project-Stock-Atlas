"""
=============================================================================
Phase 4A.5.1 — Multi-Security SEC Reality Test
=============================================================================

Empirical source-validation exercise. Runs the FROZEN Stock Atlas SEC/XBRL
ingestion + normalization architecture (sec_adapter.py, xbrl_parser.py) against
six materially different security types and records what happens. It does NOT
fix substantive normalization gaps — it collects them as evidence.

Rules honored:
  - xbrl_parser.py is the single normalization authority. No issuer-specific
    concept mappings live in this harness.
  - No approved concept family is modified to turn a failure into a pass.
  - known_at is always the SEC acceptanceDateTime, never filingDate.
  - Every field ends in a terminal state:
        SELECTED | UNAVAILABLE | NOT_APPLICABLE | CONFLICTED | MAPPING_CANDIDATE | ERROR
  - Unhandled exceptions are never allowed to abort the run.

Artifacts: live_validation_results/<UTC-timestamp>_phase4a5_1.{json,md}
=============================================================================
"""

import json
import os
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from sec_adapter import SECAdapter
from xbrl_parser import (
    XBRL_CONCEPT_MAPPINGS,
    CANONICAL_FIELD_PERIOD_TYPE,
    select_canonical_fact,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Test universe
# ---------------------------------------------------------------------------
UNIVERSE = [
    {"symbol": "MSFT",  "resolve": "MSFT",  "role": "frozen regression control / ordinary large operating company"},
    {"symbol": "AAPL",  "resolve": "AAPL",  "role": "operating company with non-calendar fiscal periods"},
    {"symbol": "JPM",   "resolve": "JPM",   "role": "financial institution / bank reporting"},
    {"symbol": "O",     "resolve": "O",     "role": "REIT + acceptance-timestamp edge case"},
    {"symbol": "BRK.B", "resolve": "BRK.B", "role": "insurance/conglomerate + multi-class security identity"},
    {"symbol": "SPY",   "resolve": "SPY",   "role": "ETF / investment-company filing regime"},
]

# Canonical Stock Atlas fields under test (fcf is DERIVED, not an XBRL family).
CANONICAL_FIELDS = [
    "revenue", "gross_profit", "operating_income", "net_income",
    "cash_from_operations", "capex", "fcf", "sbc", "cash",
    "short_term_debt", "long_term_debt", "diluted_shares",
]

# Harness field -> xbrl_parser.XBRL_CONCEPT_MAPPINGS key.
FIELD_TO_CANONICAL = {
    "revenue": "revenue",
    "gross_profit": "gross_profit",
    "operating_income": "operating_income",
    "net_income": "net_income",
    "cash_from_operations": "cash_from_operations",
    "capex": "capex",
    "sbc": "sbc",
    "cash": "cash",
    "short_term_debt": "short_term_debt",
    "long_term_debt": "long_term_debt",
    "diluted_shares": "weighted_average_diluted_shares",
}

# Per-archetype economic expectation for each canonical field. This is an
# ANNOTATION for review (Category C evidence), never a normalization rule:
# the selector's raw state is always recorded alongside it.
ARCHETYPE_FIELD_EXPECTATION = {
    "OPERATING_COMPANY": {f: "APPLICABLE" for f in CANONICAL_FIELDS},
    "FINANCIAL_BANK": {
        "revenue": "APPLICABLE_AS_TOTAL_REVENUE", "gross_profit": "NOT_APPLICABLE",
        "operating_income": "NOT_APPLICABLE", "net_income": "APPLICABLE",
        "cash_from_operations": "APPLICABLE", "capex": "NOT_APPLICABLE", "fcf": "NOT_APPLICABLE",
        "sbc": "APPLICABLE", "cash": "UNCERTAIN", "short_term_debt": "APPLICABLE",
        "long_term_debt": "APPLICABLE", "diluted_shares": "APPLICABLE",
    },
    "REIT": {
        "revenue": "APPLICABLE", "gross_profit": "NOT_APPLICABLE", "operating_income": "UNCERTAIN",
        "net_income": "APPLICABLE", "cash_from_operations": "APPLICABLE", "capex": "UNCERTAIN",
        "fcf": "UNCERTAIN", "sbc": "APPLICABLE", "cash": "APPLICABLE",
        "short_term_debt": "APPLICABLE", "long_term_debt": "APPLICABLE", "diluted_shares": "APPLICABLE",
    },
    "INSURANCE": {
        "revenue": "CONFLICT_PRONE", "gross_profit": "NOT_APPLICABLE", "operating_income": "NOT_APPLICABLE",
        "net_income": "APPLICABLE", "cash_from_operations": "APPLICABLE", "capex": "APPLICABLE",
        "fcf": "UNCERTAIN", "sbc": "UNCERTAIN", "cash": "APPLICABLE",
        "short_term_debt": "UNCERTAIN", "long_term_debt": "APPLICABLE", "diluted_shares": "UNCERTAIN",
    },
    "INVESTMENT_COMPANY_ETF": {f: "NOT_APPLICABLE" for f in CANONICAL_FIELDS},
    "UNCLASSIFIED": {f: "UNCERTAIN" for f in CANONICAL_FIELDS},
}

# Curated EXACT us-gaap concept names that are genuine economic alternatives for a
# canonical field. Used ONLY to surface MAPPING_CANDIDATEs for review — a hit is
# never admitted into an approved family by this harness. Matched by full name
# (case-insensitive), so debt maturity schedules / derivative offsets don't leak in.
FIELD_CANDIDATE_CONCEPTS = {
    "revenue": {
        "revenues", "revenuesnetofinterestexpense", "interestanddividendincomeoperating",
        "regulatedandunregulatedoperatingrevenue", "salesrevenuenet",
        "revenuefromcontractwithcustomerincludingassessedtax",
    },
    "gross_profit": {"grossprofit", "grossprofitloss"},
    "operating_income": {"operatingincomeloss", "operatingincomeorloss"},
    "net_income": {"netincomeloss", "profitloss", "netincomelossavailabletocommonstockholdersbasic"},
    "cash_from_operations": {
        "netcashprovidedbyusedinoperatingactivities",
        "netcashprovidedbyusedinoperatingactivitiescontinuingoperations",
    },
    "capex": {
        "paymentstoacquirepropertyplantandequipment", "paymentsforcapitalimprovements",
        "paymentstoacquireproductiveassets", "paymentstoacquirerealestateheldforinvestment",
        "paymentstodeveloprealestateassets", "paymentstoacquireoilandgasproperty",
        "paymentstoacquireotherproductiveassets",
    },
    "sbc": {
        "sharebasedcompensation", "sharebasedcompensationexpense", "stockcompensationexpense",
        "allocatedsharebasedcompensationexpense",
    },
    "cash": {
        "cashandcashequivalentsatcarryingvalue", "cash", "cashandduefrombanks",
        "cashcashequivalentsrestrictedcashandrestrictedcashequivalents",
        "cashequivalentsatcarryingvalue", "restrictedcashandcashequivalents",
        "interestbearingdepositsinbanks",
    },
    "short_term_debt": {
        "shorttermborrowings", "commercialpaper", "longtermdebtcurrent", "debtcurrent",
        "shorttermdebt", "othershorttermborrowings", "securitiessoldunderagreementstorepurchase",
        "federalfundspurchasedandsecuritiessoldunderagreementstorepurchase",
        "shorttermborrowingsandcurrentportionoflongtermdebt",
    },
    "long_term_debt": {
        "longtermdebt", "longtermdebtnoncurrent", "longtermborrowings",
        "longtermdebtandcapitalleaseobligations",
        "longtermdebtandcapitalleaseobligationsincludingcurrentmaturities",
        "notespayable", "seniorlongtermnotes", "subordinatedlongtermdebt",
        "secureddebt", "unsecureddebt", "debtlongtermandshorttermcombinedamount", "seniornotes",
    },
    "diluted_shares": {
        "weightedaveragenumberofdilutedsharesoutstanding",
        "weightedaveragenumberofshareoutstandingbasicanddiluted",
        "weightedaveragenumberofsharesoutstandingbasic",
        "weightedaveragelimitedpartnershipandgeneralpartnershipunitoutstanding",
    },
}

INVESTMENT_COMPANY_FORMS = {
    "N-CEN", "NPORT-P", "N-PORT", "NPORT-EX", "N-CSR", "N-CSRS", "485BPOS", "485APOS",
    "497", "497K", "24F-2NT", "NSAR-U", "NSAR-B", "N-30D", "N-1A",
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def parse_accepted_utc(raw):
    """SEC acceptanceDateTime -> tz-aware UTC datetime (raw preserved by caller).
    No offset reinterpretation."""
    if not raw or not isinstance(raw, str):
        return None
    iso = raw.strip()
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def classify_archetype(subs):
    """Route a filer to a broad SEC evidence archetype from entityType + SIC +
    the set of forms it actually files. No issuer names involved."""
    etype = (subs.get("entityType") or "").strip().lower()
    sic = str(subs.get("sic") or "").strip()
    sic_desc = (subs.get("sicDescription") or "").strip()
    forms = set(subs.get("filings", {}).get("recent", {}).get("form", []))
    has_10k = "10-K" in forms
    has_10q = "10-Q" in forms

    if not (has_10k or has_10q) and (forms & INVESTMENT_COMPANY_FORMS):
        return "INVESTMENT_COMPANY_ETF", (
            f"no 10-K/10-Q; files investment-company forms "
            f"({sorted(forms & INVESTMENT_COMPANY_FORMS)[:5]}); entityType={etype!r}"
        )
    if etype == "other" and not has_10k and not has_10q:
        return "INVESTMENT_COMPANY_ETF", f"entityType='other', no 10-K/10-Q"

    if sic in {"6021", "6022", "6020", "6029", "6199", "6120", "6712"} or sic_desc.lower().find("bank") >= 0:
        return "FINANCIAL_BANK", f"SIC {sic} ({sic_desc})"
    if sic == "6798" or "real estate investment trust" in sic_desc.lower():
        return "REIT", f"SIC {sic} ({sic_desc})"
    if sic in {"6311", "6321", "6331", "6411", "6351", "6361"} or "insurance" in sic_desc.lower():
        return "INSURANCE", f"SIC {sic} ({sic_desc})"

    if etype == "operating" and (has_10k or has_10q):
        return "OPERATING_COMPANY", f"entityType='operating', SIC {sic} ({sic_desc})"
    return "UNCLASSIFIED", f"entityType={etype!r}, SIC {sic!r} ({sic_desc!r}), forms={sorted(forms)[:6]}"


def latest_filing_of(subs_recent_iter, form):
    for f in subs_recent_iter:
        if f.get("form") == form:
            return f
    return None


def discover_regime(archetype, adapter, cik):
    """Return (regime_label, primary_filing_dict, secondary_filing_dict, notes)."""
    notes = []
    if archetype == "INVESTMENT_COMPANY_ETF":
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

    # operating-company-like regimes (bank / REIT / insurance / operating all file 10-K/10-Q)
    tk = adapter.get_recent_filings(cik, "10-K", 1)
    tq = adapter.get_recent_filings(cik, "10-Q", 1)
    return "OPERATING (10-K annual + 10-Q interim)", (tk[0] if tk else None), (tq[0] if tq else None), notes


def scan_mapping_candidates(company_facts, field, accession, period_end, period_type):
    """List us-gaap concepts NOT in the approved family that carry a fact matching
    the target accession + period + period type and whose name suggests the field.
    Evidence only — never admitted."""
    out = []
    if not company_facts:
        return out
    ug = company_facts.get("facts", {}).get("us-gaap", {})
    approved = {c.split(":", 1)[-1] for c in XBRL_CONCEPT_MAPPINGS.get(FIELD_TO_CANONICAL.get(field, field), [])}
    allow = FIELD_CANDIDATE_CONCEPTS.get(field, set())
    for concept, cdata in ug.items():
        if concept in approved:
            continue
        if concept.lower() not in allow:
            continue
        for unit, flist in cdata.get("units", {}).items():
            for fact in flist:
                if fact.get("val") is None:
                    continue
                if accession and fact.get("accn") != accession:
                    continue
                if period_end and fact.get("end") != period_end:
                    continue
                ftype = "duration" if fact.get("start") else "instant"
                if period_type and ftype != period_type:
                    continue
                out.append({
                    "concept": f"us-gaap:{concept}",
                    "unit": unit,
                    "value": fact.get("val"),
                    "period_start": fact.get("start"),
                    "period_end": fact.get("end"),
                    "accession": fact.get("accn"),
                    "form": fact.get("form"),
                })
    return out


def family_concepts_present(company_facts, field):
    """Which approved-family concepts exist anywhere in the facts (any period)."""
    if not company_facts:
        return []
    ug = company_facts.get("facts", {}).get("us-gaap", {})
    fam = XBRL_CONCEPT_MAPPINGS.get(FIELD_TO_CANONICAL.get(field, field), [])
    return [c.split(":", 1)[-1] for c in fam if c.split(":", 1)[-1] in ug]


# ---------------------------------------------------------------------------
# per-security evaluation
# ---------------------------------------------------------------------------
def evaluate_security(entry, adapter):
    sym = entry["symbol"]
    rec = {
        "symbol": sym,
        "resolve_ticker": entry["resolve"],
        "role": entry["role"],
        "warnings": [],
        "identity": {},
        "archetype": None,
        "archetype_reason": None,
        "filing_regime": None,
        "primary_filing": None,
        "secondary_filing": None,
        "companyfacts_available": None,
        "fields": {},
        "field_state_counts": {s: 0 for s in
                               ["SELECTED", "UNAVAILABLE", "NOT_APPLICABLE", "CONFLICTED", "MAPPING_CANDIDATE", "ERROR"]},
        "mapping_candidates": [],
        "period_selection": None,
        "known_at_check": None,
        "overall": None,
    }

    # 1. identity
    cik = adapter.resolve_cik(entry["resolve"])
    if not cik:
        rec["overall"] = "ERROR: identity not resolved"
        rec["warnings"].append("resolve_cik returned None")
        return rec
    subs = adapter.get_company_submissions(cik)
    if not subs:
        rec["overall"] = "ERROR: submissions not retrieved"
        rec["warnings"].append("get_company_submissions returned None")
        return rec

    rec["identity"] = {
        "cik": cik,
        "name": subs.get("name"),
        "entityType": subs.get("entityType"),
        "sic": subs.get("sic"),
        "sicDescription": subs.get("sicDescription"),
        "category": subs.get("category"),
        "fiscalYearEnd": subs.get("fiscalYearEnd"),
        "tickers": subs.get("tickers"),
        "exchanges": subs.get("exchanges"),
        "former_names": [n.get("name") for n in subs.get("formerNames", [])],
    }

    # 2/3. archetype + filing regime
    archetype, reason = classify_archetype(subs)
    rec["archetype"], rec["archetype_reason"] = archetype, reason
    regime, primary, secondary, notes = discover_regime(archetype, adapter, cik)
    rec["filing_regime"] = regime
    rec["warnings"].extend(notes)

    def _filing_block(f):
        if not f:
            return None
        accepted_raw = f.get("acceptanceDateTime")
        accepted_utc = parse_accepted_utc(accepted_raw)
        return {
            "form": f.get("form"),
            "accession": f.get("accessionNumber"),
            "report_date": f.get("reportDate"),
            "filing_date": f.get("filingDate"),
            "accepted_datetime_raw": accepted_raw,
            "known_at_utc": accepted_utc.isoformat() if accepted_utc else None,
            "primary_document": f.get("primaryDocument"),
        }

    rec["primary_filing"] = _filing_block(primary)
    rec["secondary_filing"] = _filing_block(secondary)

    # known_at vs filing-date check (Realty Income edge case, but run for all)
    if primary:
        araw = primary.get("acceptanceDateTime")
        autc = parse_accepted_utc(araw)
        fdate = primary.get("filingDate")
        rec["known_at_check"] = {
            "source_field": "acceptanceDateTime",
            "accepted_raw": araw,
            "known_at_utc": autc.isoformat() if autc else None,
            "filing_date": fdate,
            "accepted_calendar_date_utc": autc.date().isoformat() if autc else None,
            "filing_date_differs_from_accepted_date": bool(autc and fdate and autc.date().isoformat() != fdate),
            "uses_filing_date_as_known_at": False,
        }
        if rec["known_at_check"]["filing_date_differs_from_accepted_date"]:
            rec["warnings"].append(
                f"filingDate {fdate} != acceptance calendar date {autc.date().isoformat()} "
                f"-> known_at must be acceptanceDateTime {araw}"
            )

    # 4. CompanyFacts
    company_facts = None
    if archetype == "INVESTMENT_COMPANY_ETF":
        company_facts = adapter.get_company_facts(cik)  # expected None (404)
        rec["companyfacts_available"] = company_facts is not None
        if company_facts is None:
            rec["warnings"].append("no us-gaap CompanyFacts (expected for investment company); corporate fields -> NOT_APPLICABLE")
    else:
        company_facts = adapter.get_company_facts(cik)
        rec["companyfacts_available"] = company_facts is not None
        if company_facts is None:
            rec["warnings"].append("CompanyFacts unexpectedly unavailable for a 10-K/10-Q filer")

    # target = latest annual filing (10-K) — unambiguous period
    target = primary if (rec["primary_filing"] and rec["primary_filing"]["form"] == "10-K") else None
    target_accn = target.get("accessionNumber") if target else None
    target_end = target.get("reportDate") if target else None
    target_accepted = target.get("acceptanceDateTime") if target else None

    # 5-9. field normalization via the single authority
    field_results = {}
    for field in CANONICAL_FIELDS:
        expectation = ARCHETYPE_FIELD_EXPECTATION.get(archetype, {}).get(field, "UNCERTAIN")
        fr = {
            "canonical_field": field,
            "archetype_expectation": expectation,
            "selector_status": None,
            "state": None,
            "concept": None,
            "concept_family": XBRL_CONCEPT_MAPPINGS.get(FIELD_TO_CANONICAL.get(field, field)),
            "value": None, "unit": None,
            "period_start": None, "period_end": None, "period_type": None,
            "accession": None, "accepted_datetime": target_accepted,
            "candidates_in_family_present": [],
            "mapping_candidates": [],
            "note": None,
        }

        if field == "fcf":
            fr["selector_status"] = "DERIVED"
            fr["concept_family"] = ["DERIVED: cash_from_operations - capex"]
            fr = _resolve_fcf(fr, field_results, expectation)
            field_results[field] = fr
            rec["field_state_counts"][fr["state"]] = rec["field_state_counts"].get(fr["state"], 0) + 1
            continue

        canonical_key = FIELD_TO_CANONICAL[field]
        period_type = CANONICAL_FIELD_PERIOD_TYPE.get(canonical_key)

        if company_facts is None or target_accn is None:
            fr["selector_status"] = "NO_COMPANYFACTS" if company_facts is None else "NO_ANNUAL_TARGET"
            fr["state"] = "NOT_APPLICABLE" if archetype == "INVESTMENT_COMPANY_ETF" else "UNAVAILABLE"
            fr["note"] = ("no us-gaap CompanyFacts for this filer"
                          if company_facts is None else "no latest 10-K annual target filing found")
            field_results[field] = fr
            rec["field_state_counts"][fr["state"]] += 1
            continue

        try:
            sel = select_canonical_fact(
                company_facts, canonical_key,
                accession=target_accn, period_end=target_end, period_type=period_type,
            )
        except Exception as e:  # pragma: no cover - defensive
            fr["selector_status"] = "ERROR"
            fr["state"] = "ERROR"
            fr["note"] = f"select_canonical_fact raised: {e!r}"
            field_results[field] = fr
            rec["field_state_counts"]["ERROR"] += 1
            continue

        fr["selector_status"] = sel.get("status")

        if sel.get("status") in ("SELECTED", "CONFLICTED"):
            fr["concept"] = sel.get("concept")
            fr["value"] = sel.get("raw_value")
            fr["unit"] = sel.get("unit")
            fr["period_start"] = sel.get("period_start")
            fr["period_end"] = sel.get("period_end")
            fr["period_type"] = sel.get("period_type")
            fr["accession"] = sel.get("accession")
            fr["candidates_in_family_present"] = [c["concept"] for c in sel.get("candidates", [])]
            fr["conflict"] = sel.get("conflict")
            fr["state"] = "SELECTED" if sel.get("status") == "SELECTED" else "CONFLICTED"
        else:  # UNAVAILABLE
            present = family_concepts_present(company_facts, field)
            fr["candidates_in_family_present"] = present
            cands = scan_mapping_candidates(company_facts, field, target_accn, target_end, period_type)
            fr["mapping_candidates"] = cands
            fr["note"] = sel.get("reason")
            if cands:
                fr["state"] = "MAPPING_CANDIDATE"
                for c in cands:
                    rec["mapping_candidates"].append({
                        "issuer": sym, "cik": cik, "canonical_field": field,
                        "candidate_concept": c["concept"], "raw_value": c["value"],
                        "unit": c["unit"], "period": f"{c['period_start']}..{c['period_end']}",
                        "accession": c["accession"], "form": c["form"],
                        "why_equivalent": f"name matches {field} keyword; carries a matching "
                                          f"{period_type or 'period'} fact in the target 10-K",
                        "cross_issuer_impact": "REVIEW — could shift values for other filers that "
                                               "also tag this concept; not admitted.",
                    })
            elif expectation in ("NOT_APPLICABLE",):
                fr["state"] = "NOT_APPLICABLE"
                fr["note"] = (fr["note"] or "") + " | archetype expectation: NOT_APPLICABLE"
            else:
                fr["state"] = "UNAVAILABLE"

        field_results[field] = fr
        rec["field_state_counts"][fr["state"]] = rec["field_state_counts"].get(fr["state"], 0) + 1

    rec["fields"] = field_results

    # 10-Q quarter-vs-YTD period-selection evidence
    tq_filing = secondary if (rec["secondary_filing"] and rec["secondary_filing"]["form"] == "10-Q") else None
    if company_facts is not None and tq_filing:
        rec["period_selection"] = probe_period_selection(company_facts, tq_filing)

    # overall
    c = rec["field_state_counts"]
    if any(f.get("state") == "ERROR" for f in field_results.values()):
        rec["overall"] = "ROUTED, with ERROR in field selection"
    elif archetype == "INVESTMENT_COMPANY_ETF":
        rec["overall"] = "ROUTED to investment-company regime; corporate fields NOT_APPLICABLE (expected)"
    else:
        rec["overall"] = (
            f"ROUTED to {archetype}; {c['SELECTED']} SELECTED / {c['UNAVAILABLE']} UNAVAILABLE / "
            f"{c['NOT_APPLICABLE']} NOT_APPLICABLE / {c['CONFLICTED']} CONFLICTED / "
            f"{c['MAPPING_CANDIDATE']} MAPPING_CANDIDATE"
        )
    return rec


def _resolve_fcf(fr, field_results, expectation):
    cfo = field_results.get("cash_from_operations", {})
    capex = field_results.get("capex", {})
    if cfo.get("state") == "SELECTED" and capex.get("state") == "SELECTED":
        try:
            fr["value"] = cfo["value"] - capex["value"]
            fr["unit"] = cfo.get("unit")
            fr["concept"] = f"DERIVED: {cfo.get('concept')} - {capex.get('concept')}"
            fr["accession"] = cfo.get("accession")
            fr["period_start"] = cfo.get("period_start")
            fr["period_end"] = cfo.get("period_end")
            fr["period_type"] = "duration"
            fr["state"] = "SELECTED"
            fr["note"] = "derived from CFO and CapEx (same accession)" \
                if cfo.get("accession") == capex.get("accession") else "derived; CFO/CapEx accessions differ"
        except Exception as e:  # pragma: no cover
            fr["state"] = "ERROR"
            fr["note"] = f"fcf derivation failed: {e!r}"
    else:
        if expectation == "NOT_APPLICABLE":
            fr["state"] = "NOT_APPLICABLE"
            fr["note"] = "CFO/CapEx not both SELECTED and archetype expectation is NOT_APPLICABLE"
        else:
            fr["state"] = "UNAVAILABLE"
            fr["note"] = f"cannot derive: CFO={cfo.get('state')}, CapEx={capex.get('state')}"
    return fr


def probe_period_selection(company_facts, tq_filing):
    """Enumerate revenue duration facts in the latest 10-Q's period and classify
    each as quarter / YTD / annual / other. Show whether select_canonical_fact
    (period_end only) would silently take YTD."""
    accn = tq_filing.get("accessionNumber")
    end = tq_filing.get("reportDate")
    ug = company_facts.get("facts", {}).get("us-gaap", {})
    rev_family = [c.split(":", 1)[-1] for c in XBRL_CONCEPT_MAPPINGS["revenue"]]
    facts = []
    for concept in rev_family:
        cd = ug.get(concept)
        if not cd:
            continue
        for unit, flist in cd.get("units", {}).items():
            for f in flist:
                if f.get("end") != end or f.get("accn") != accn or not f.get("start"):
                    continue
                s, e = f["start"], f["end"]
                months = (int(e[:4]) - int(s[:4])) * 12 + (int(e[5:7]) - int(s[5:7]))
                kind = ("quarter" if months <= 4 else "half-year" if months <= 7
                        else "nine-month" if months <= 10 else "annual" if months <= 13 else "multi-year")
                facts.append({
                    "concept": f"us-gaap:{concept}", "unit": unit, "start": s, "end": e,
                    "approx_months": months, "period_kind": kind, "frame": f.get("frame"),
                    "fp": f.get("fp"), "value": f.get("val"),
                })
    facts.sort(key=lambda x: (x["start"], x["concept"]))
    sel = select_canonical_fact(company_facts, "revenue", accession=accn, period_end=end, period_type="duration")
    would_pick = None
    if sel.get("status") in ("SELECTED", "CONFLICTED"):
        would_pick = {
            "concept": sel.get("concept"), "start": sel.get("period_start"),
            "end": sel.get("period_end"), "value": sel.get("raw_value"),
        }
    kinds = {f["period_kind"] for f in facts}
    return {
        "quarter_10q_accession": accn,
        "quarter_10q_period_end": end,
        "revenue_duration_facts": facts,
        "distinct_period_kinds_for_same_end": sorted(kinds),
        "overlapping_contexts": len(kinds) > 1,
        "select_canonical_fact_would_pick_period_end_only": would_pick,
        "risk": ("select_canonical_fact(period_end only) picks earliest-start = "
                 + (would_pick["start"] + ".." + would_pick["end"] if would_pick else "n/a")
                 + " which is NOT the current quarter when YTD contexts exist; a quarterly "
                   "request must pass period_start explicitly."),
    }


# ---------------------------------------------------------------------------
# cross-cutting reports
# ---------------------------------------------------------------------------
def short_term_debt_cross_issuer(results):
    rows = []
    for r in results:
        if r["archetype"] == "INVESTMENT_COMPANY_ETF":
            continue
        fr = r.get("fields", {}).get("short_term_debt", {})
        entry = {
            "issuer": r["symbol"], "archetype": r["archetype"],
            "state": fr.get("state"),
            "selected_concept": fr.get("concept"),
            "selected_value": fr.get("value"),
            "family_concepts_present": fr.get("candidates_in_family_present"),
            "mapping_candidates": fr.get("mapping_candidates"),
        }
        rows.append(entry)
    return {
        "rows": rows,
        "approved_family": XBRL_CONCEPT_MAPPINGS["short_term_debt"],
        "observations": [
            "MSFT: no approved-family fact for the FY period (learning item carried from 4A.5.0).",
            "AAPL: CommercialPaper populates cleanly (approved family, priority 1).",
            "O (REIT): CommercialPaper populates cleanly.",
            "JPM (bank): ShortTermBorrowings populates; banks also carry repo / fed-funds-purchased "
            "which are economically 'short-term funding' but NOT the same as corporate ST debt.",
            "BRK.B (insurance conglomerate): no approved-family fact; current debt is disclosed "
            "per operating segment, not as a single holdco line.",
        ],
        "questions_for_review": [
            "Is a single canonical 'short_term_debt' field defensible across archetypes, or is it "
            "archetype-specific (corporate CP/ST-borrowings vs bank wholesale funding vs holdco segment debt)?",
            "Should LongTermDebtCurrent (current maturities) be admitted, and if so for which archetypes?",
            "Does aggregation (CP + current maturities + ST borrowings) need an explicit, versioned rule?",
        ],
        "decision": "NO CHANGE — evidence only, pending review.",
    }


def build_matrix(results):
    matrix = {}
    for field in CANONICAL_FIELDS:
        matrix[field] = {}
        for r in results:
            fr = r.get("fields", {}).get(field, {})
            matrix[field][r["symbol"]] = fr.get("state") or "ERROR"
    return matrix


# ---------------------------------------------------------------------------
# artifacts
# ---------------------------------------------------------------------------
def write_artifacts(summary, results_dir="live_validation_results"):
    d = Path(results_dir)
    d.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jp = d / f"{ts}_phase4a5_1.json"
    mp = d / f"{ts}_phase4a5_1.md"

    jp.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))

    L = []
    L.append("# Phase 4A.5.1 — Multi-Security SEC Reality Test")
    L.append("")
    L.append(f"- Generated (UTC): {summary['generated_utc']}")
    L.append(f"- Universe: {', '.join(s['symbol'] for s in UNIVERSE)}")
    L.append(f"- Unhandled exceptions: {summary['unhandled_exceptions']}")
    L.append(f"- Verdict: **{summary['verdict']}**")
    L.append("")

    L.append("## Cross-security matrix (canonical field × security)")
    L.append("")
    syms = [s["symbol"] for s in UNIVERSE]
    L.append("| field | " + " | ".join(syms) + " |")
    L.append("|" + "---|" * (len(syms) + 1))
    for field, row in summary["matrix"].items():
        L.append(f"| {field} | " + " | ".join(row.get(s, "-") for s in syms) + " |")
    L.append("")
    L.append("States: SELECTED · UNAVAILABLE · NOT_APPLICABLE · CONFLICTED · MAPPING_CANDIDATE · ERROR")
    L.append("")

    for r in summary["securities"]:
        L.append(f"## {r['symbol']} — {r['role']}")
        idn = r.get("identity", {})
        L.append(f"- CIK {idn.get('cik')} · {idn.get('name')} · entityType={idn.get('entityType')} "
                 f"· SIC {idn.get('sic')} ({idn.get('sicDescription')}) · FYE {idn.get('fiscalYearEnd')}")
        L.append(f"- tickers: {idn.get('tickers')}")
        L.append(f"- **archetype: {r['archetype']}** — {r['archetype_reason']}")
        L.append(f"- filing regime: {r['filing_regime']}")
        pf = r.get("primary_filing")
        if pf:
            L.append(f"- primary filing: {pf['form']} {pf['accession']} · report {pf['report_date']} · "
                     f"filed {pf['filing_date']} · accepted `{pf['accepted_datetime_raw']}` · "
                     f"known_at(UTC) `{pf['known_at_utc']}`")
        sf = r.get("secondary_filing")
        if sf:
            L.append(f"- secondary filing: {sf['form']} {sf['accession']} · report {sf['report_date']} · "
                     f"accepted `{sf['accepted_datetime_raw']}`")
        kc = r.get("known_at_check")
        if kc:
            L.append(f"- known_at check: source={kc['source_field']}; filing_date {kc['filing_date']} "
                     f"vs accepted-date {kc['accepted_calendar_date_utc']} — "
                     f"{'DIFFER (uses acceptanceDateTime)' if kc['filing_date_differs_from_accepted_date'] else 'same'}")
        L.append(f"- companyfacts available: {r['companyfacts_available']}")
        L.append(f"- state counts: {r['field_state_counts']}")
        L.append(f"- overall: {r['overall']}")
        if r["warnings"]:
            L.append("- warnings:")
            for w in r["warnings"]:
                L.append(f"    - {w}")
        L.append("")
        L.append("| field | state | expectation | concept | value | period | accn |")
        L.append("|---|---|---|---|---|---|---|")
        for field in CANONICAL_FIELDS:
            fr = r.get("fields", {}).get(field, {})
            per = ""
            if fr.get("period_start") or fr.get("period_end"):
                per = f"{fr.get('period_start') or ''}..{fr.get('period_end') or ''}"
            L.append(f"| {field} | {fr.get('state')} | {fr.get('archetype_expectation')} | "
                     f"{fr.get('concept') or ''} | {fr.get('value')} | {per} | {fr.get('accession') or ''} |")
        L.append("")
        ps = r.get("period_selection")
        if ps:
            L.append(f"### {r['symbol']} — quarter-vs-YTD evidence (latest 10-Q {ps['quarter_10q_accession']}, "
                     f"period end {ps['quarter_10q_period_end']})")
            L.append(f"- overlapping contexts: {ps['overlapping_contexts']} "
                     f"(kinds: {ps['distinct_period_kinds_for_same_end']})")
            L.append(f"- select_canonical_fact(period_end only) would pick: "
                     f"{ps['select_canonical_fact_would_pick_period_end_only']}")
            L.append(f"- risk: {ps['risk']}")
            L.append("")
            L.append("| concept | period | ~months | kind | frame | value |")
            L.append("|---|---|---|---|---|---|")
            for f in ps["revenue_duration_facts"]:
                L.append(f"| {f['concept']} | {f['start']}..{f['end']} | {f['approx_months']} | "
                         f"{f['period_kind']} | {f['frame']} | {f['value']} |")
            L.append("")

    L.append("## Mapping candidates discovered (NOT admitted)")
    L.append("")
    if summary["mapping_candidates"]:
        L.append("| issuer | field | candidate concept | value | period | accession | why | cross-issuer impact |")
        L.append("|---|---|---|---|---|---|---|---|")
        for m in summary["mapping_candidates"]:
            L.append(f"| {m['issuer']} | {m['canonical_field']} | {m['candidate_concept']} | {m['raw_value']} | "
                     f"{m['period']} | {m['accession']} | {m['why_equivalent']} | {m['cross_issuer_impact']} |")
    else:
        L.append("_none_")
    L.append("")

    st = summary["short_term_debt_report"]
    L.append("## Short-term-debt cross-issuer evidence")
    L.append("")
    L.append(f"Approved family: `{st['approved_family']}`")
    L.append("")
    L.append("| issuer | archetype | state | selected concept | value | family concepts present | mapping candidates |")
    L.append("|---|---|---|---|---|---|---|")
    for row in st["rows"]:
        mc = ", ".join(c["concept"] for c in (row["mapping_candidates"] or [])) or "-"
        L.append(f"| {row['issuer']} | {row['archetype']} | {row['state']} | {row['selected_concept'] or '-'} | "
                 f"{row['selected_value']} | {row['family_concepts_present']} | {mc} |")
    L.append("")
    for o in st["observations"]:
        L.append(f"- {o}")
    L.append("")
    L.append("Questions for review:")
    for q in st["questions_for_review"]:
        L.append(f"- {q}")
    L.append(f"\n**{st['decision']}**")
    L.append("")

    L.append("## Issue register (categorized)")
    L.append("")
    for item in summary["issue_register"]:
        L.append(f"- **[{item['category']}] {item['title']}** — {item['detail']}")
    L.append("")

    mp.write_text("\n".join(L))
    return {"json": str(jp), "md": str(mp)}


# ---------------------------------------------------------------------------
# issue categorization
# ---------------------------------------------------------------------------
def build_issue_register(results):
    reg = []
    reg.append({
        "category": "A", "title": "resolve_cik dotted vs hyphen ticker",
        "detail": "sec_adapter.resolve_cik('BRK.B') returned None; SEC company_tickers.json uses "
                  "'BRK-B'. Fixed in this phase: normalize '.'->'-' before lookup. Plumbing only.",
    })
    for r in results:
        sym = r["symbol"]
        arch = r["archetype"]
        if arch == "INVESTMENT_COMPANY_ETF":
            reg.append({
                "category": "E", "title": f"{sym}: investment-company filing regime",
                "detail": "No us-gaap CompanyFacts (404). Routed to N-CEN + NPORT-P. Corporate canonical "
                          "fields are NOT_APPLICABLE, not ERROR. Security Master has no ETF/fund identity "
                          "or filing-regime concept — routing lives only in this harness.",
            })
        for field, fr in r.get("fields", {}).items():
            if fr.get("state") == "CONFLICTED":
                reg.append({
                    "category": "C", "title": f"{sym}: '{field}' CONFLICTED across approved concepts",
                    "detail": f"{fr.get('conflict')}. Architecture correctly refused to silently pick. "
                              f"Needs archetype-specific normalization (e.g. insurance 'total revenues' "
                              f"vs 'contract revenue').",
                })
            if fr.get("state") == "MAPPING_CANDIDATE":
                for m in fr.get("mapping_candidates", []):
                    reg.append({
                        "category": "B", "title": f"{sym}: '{field}' mapping candidate {m['concept']}",
                        "detail": f"value {m['value']} for {m['period_start']}..{m['period_end']} in "
                                  f"{m['accession']}. Economically resembles '{field}' but not in the "
                                  f"approved family. NOT admitted — review for cross-issuer impact.",
                    })
            if fr.get("state") == "UNAVAILABLE" and fr.get("archetype_expectation") in ("APPLICABLE", "UNCERTAIN"):
                reg.append({
                    "category": "C", "title": f"{sym}: '{field}' UNAVAILABLE though archetype-plausible",
                    "detail": f"family concepts present anywhere: {fr.get('candidates_in_family_present')}; "
                              f"reason: {fr.get('note')}. Possible archetype-specific normalization gap.",
                })
            if (fr.get("state") == "NOT_APPLICABLE" and fr.get("selector_status") not in (None, "NO_COMPANYFACTS")
                    and arch != "INVESTMENT_COMPANY_ETF"):
                reg.append({
                    "category": "F", "title": f"{sym}: '{field}' NOT_APPLICABLE for archetype {arch}",
                    "detail": f"selector said {fr.get('selector_status')}; no approved-family concept and "
                              f"the field is not an economic concept for this archetype. Expected, no issue.",
                })
        kc = r.get("known_at_check")
        if kc and kc.get("filing_date_differs_from_accepted_date"):
            reg.append({
                "category": "F", "title": f"{sym}: acceptance date != filing date (handled correctly)",
                "detail": f"accepted {kc['accepted_raw']} (UTC date {kc['accepted_calendar_date_utc']}) "
                          f"vs filingDate {kc['filing_date']}. known_at uses acceptanceDateTime. Expected, no issue.",
            })
        ps = r.get("period_selection")
        if ps and ps.get("overlapping_contexts"):
            reg.append({
                "category": "C", "title": f"{sym}: 10-Q revenue has overlapping quarter/YTD contexts",
                "detail": f"kinds {ps['distinct_period_kinds_for_same_end']}. select_canonical_fact with "
                          f"period_end only picks earliest-start (YTD). A quarterly request needs an "
                          f"explicit period_start / period-granularity rule. No rule established here.",
            })

    # BRK.B multi-class
    brk = next((r for r in results if r["symbol"] == "BRK.B"), None)
    if brk:
        reg.append({
            "category": "D", "title": "BRK.B / BRK.A share the CIK (issuer) but are distinct securities",
            "detail": f"company_tickers.json maps both 'BRK-A' and 'BRK-B' to CIK "
                      f"{brk['identity'].get('cik')}; submissions.tickers={brk['identity'].get('tickers')}. "
                      f"resolve_cik returns only a CIK — it cannot distinguish share class. "
                      f"SecurityIdentityORM HAS security_id / issuer_id / ticker / share_class / cik so it "
                      f"CAN represent both as separate securities under one issuer, but there is no logic to "
                      f"populate share_class from a ticker. Not redesigned in this pass.",
        })
    return reg


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def run():
    adapter = SECAdapter()
    results = []
    unhandled = 0
    for entry in UNIVERSE:
        try:
            results.append(evaluate_security(entry, adapter))
        except Exception as e:
            unhandled += 1
            results.append({
                "symbol": entry["symbol"], "role": entry["role"],
                "overall": f"UNHANDLED EXCEPTION: {e!r}",
                "traceback": traceback.format_exc(),
                "fields": {}, "field_state_counts": {}, "warnings": ["unhandled exception"],
                "archetype": "ERROR", "identity": {},
            })

    matrix = build_matrix(results)
    st_report = short_term_debt_cross_issuer(results)
    issue_register = build_issue_register(results)

    # verdict
    routed_ok = all(r.get("archetype") not in (None, "ERROR", "UNCLASSIFIED") for r in results)
    msft = next((r for r in results if r["symbol"] == "MSFT"), None)
    msft_ok = bool(msft and msft["field_state_counts"].get("SELECTED", 0) >= 9
                   and msft["field_state_counts"].get("ERROR", 0) == 0)
    no_exc = unhandled == 0 and not any(
        f.get("state") == "ERROR" for r in results for f in r.get("fields", {}).values())
    spy = next((r for r in results if r["symbol"] == "SPY"), None)
    spy_ok = bool(spy and spy["archetype"] == "INVESTMENT_COMPANY_ETF"
                  and spy["field_state_counts"].get("ERROR", 0) == 0)

    has_learnings = any(i["category"] in ("B", "C", "D") for i in issue_register)

    if routed_ok and msft_ok and no_exc and spy_ok:
        verdict = ("PHASE 4A.5.1 PASS WITH MAPPING/ARCHETYPE LEARNINGS" if has_learnings
                   else "PHASE 4A.5.1 PASS — ARCHITECTURE GENERALIZES")
    else:
        verdict = "PHASE 4A.5.1 FAIL — ARCHITECTURAL CORRECTION REQUIRED"

    summary = {
        "phase": "4A.5.1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "universe": UNIVERSE,
        "unhandled_exceptions": unhandled,
        "securities": results,
        "matrix": matrix,
        "mapping_candidates": [m for r in results for m in r.get("mapping_candidates", [])],
        "short_term_debt_report": st_report,
        "issue_register": issue_register,
        "acceptance_checks": {
            "all_routed": routed_ok,
            "msft_regression_fields_ok": msft_ok,
            "no_unhandled_exceptions_or_field_errors": no_exc,
            "spy_routed_as_investment_company": spy_ok,
        },
        "verdict": verdict,
    }
    artifacts = write_artifacts(summary)
    summary["artifacts"] = artifacts

    # console
    print("\n" + "=" * 70)
    print("PHASE 4A.5.1 — MULTI-SECURITY SEC REALITY TEST")
    print("=" * 70)
    for r in results:
        print(f"\n[{r['symbol']}] archetype={r.get('archetype')} regime={r.get('filing_regime')}")
        print(f"   {r.get('overall')}")
        if r.get("warnings"):
            for w in r["warnings"]:
                print(f"   ! {w}")
    print("\nMATRIX (field x security):")
    syms = [s["symbol"] for s in UNIVERSE]
    print("   " + "field".ljust(22) + " ".join(s.rjust(16) for s in syms))
    for field, row in matrix.items():
        print("   " + field.ljust(22) + " ".join((row.get(s, "-")).rjust(16) for s in syms))
    print(f"\nArtifacts:\n   JSON: {artifacts['json']}\n   MD:   {artifacts['md']}")
    print(f"\nVERDICT: {verdict}")
    return summary


if __name__ == "__main__":
    s = run()
    raise SystemExit(0 if s["verdict"] != "PHASE 4A.5.1 FAIL — ARCHITECTURAL CORRECTION REQUIRED" else 1)
