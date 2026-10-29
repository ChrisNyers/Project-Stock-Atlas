"""Independent cross-check of retained SEC company-facts values against the filing's own primary document.

For each cohort name: fetch the 10-K primary document named in EDGAR's submissions (read-only, held in memory, SHA-256 recorded; the
document itself is not stored), then look for each selected value as a printed number in the filing text. companyfacts and the filing
HTML are two renderings of the same XBRL submission, so this proves the adapter selected the number the company PRINTED (concept/scale/period
mistakes show up as 'not found'); it is not a second data vendor. Mismatches are reported, never repaired.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from sec_adapter import SECAdapter, rate_limiter
from atlas_ui import research

ROOT = Path(__file__).resolve().parents[2]
RD = ROOT / "atlas_ui" / "data" / "live" / "research"
FIELDS = ("revenue", "operating_income", "net_income", "diluted_eps", "cash_from_operations", "capex", "weighted_average_diluted_shares")


def printed_forms(field, value, unit):
    """Ways a filing may print this value: whole dollars, thousands, millions (commas), or per-share to 2 decimals."""
    if unit == "USD/shares":
        return [f"{value:.2f}"]
    a = abs(value)
    forms = [f"{round(a):,}", f"{round(a / 1e3):,}", f"{round(a / 1e6):,}", f"{round(a / 1e6, 1):,.1f}"]
    if a < 1e5:  # a count already tagged in millions (e.g. 718.4) is printed with one decimal
        forms.append(f"{a:,.1f}")
    # a short token such as "1" or "12" appears everywhere; require at least 3 digits so a match is meaningful
    return [x for x in forms if len(re.sub(r"\D", "", x)) >= 3]


def text_of(html: str) -> str:
    t = re.sub(r"<[^>]+>", " ", html)
    t = re.sub(r"&nbsp;|&#160;|&#xa0;", " ", t)
    return re.sub(r"\s+", " ", t)


def check(ticker, ad):
    snap = research.latest_snapshot(RD, ticker)["data"]
    le = max(snap["periods"])
    row = snap["periods"][le]
    accn = row["revenue"]["accession"]
    cik = snap["issuer_cik"]
    filings = ad.get_recent_filings(cik, "10-K", 8)
    doc = next((f for f in filings if f["accessionNumber"] == accn), None)
    if not doc:
        return {"ticker": ticker, "accession": accn, "status": "NOT_VERIFIED — accession not in recent 10-K list"}
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn.replace('-', '')}/{doc['primaryDocument']}"
    rate_limiter.wait()
    r = ad.session.get(url, timeout=60)
    r.raise_for_status()
    body = r.text
    txt = text_of(body)
    out = {"ticker": ticker, "fiscal_year_end": le, "accession": accn, "document_url": url, "document_sha256": hashlib.sha256(r.content).hexdigest(),
           "document_bytes": len(r.content), "filing_date": doc["filingDate"], "checks": []}
    for f in FIELDS:
        x = row.get(f)
        if not x or "value" not in x:
            out["checks"].append({"field": f, "status": "SKIPPED — no selected SEC fact (already listed as UNVERIFIED/CONFLICTED)"})
            continue
        if x["accession"] != accn:
            out["checks"].append({"field": f, "status": f"SKIPPED — selected from a different filing {x['accession']}"})
            continue
        hit = None
        for form in printed_forms(f, x["value"], x["unit"]):
            if re.search(rf"(?<![\d.,]){re.escape(form)}(?![\d,]|\.\d)", txt):
                hit = form
                break
        out["checks"].append({"field": f, "selected_value": x["value"], "unit": x["unit"], "concept": x["concept"],
                              "printed_form_found": hit, "status": "VERIFIED_IN_FILING" if hit else "NOT_FOUND_IN_FILING_TEXT"})
    return out


if __name__ == "__main__":
    ad = SECAdapter()
    res = [check(t, ad) for t in sys.argv[1:] or ("MCD", "GEV", "RMD", "ORCL")]
    print(json.dumps(res, indent=1))
