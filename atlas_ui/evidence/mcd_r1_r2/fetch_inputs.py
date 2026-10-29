"""Fetch and cache the inputs for the MCD R1/R2 research run. Read-only. Never prints or writes the API key.

TwelveData (price history, personal research use; the /dividends endpoint is NOT on the free plan: HTTP 403, so dividends are never fetched): raw responses are cached under ``atlas_cache/`` (git-ignored: the provider's terms do not clearly
permit an indefinite audit store or redistribution), and only their SHA-256 and derived numbers are committed. The U.S. Treasury yield curve (primary source,
public) is retained in this directory. SEC company facts come through the existing ``sec_adapter``.

    .venv/bin/python atlas_ui/evidence/mcd_r1_r2/fetch_inputs.py [--refresh]
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[3]
CACHE = REPO / "atlas_cache" / "mcd_r1_r2"
HERE = Path(__file__).resolve().parent
UA = "Project Stock Atlas research (read-only evaluation)"
TSY_URL = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all"
           "?type=daily_treasury_yield_curve&field_tdr_date_value={y}&page&_format=csv")


def load_env():
    f = REPO / ".env"
    for ln in f.read_text().splitlines() if f.is_file() else []:
        if "=" in ln and not ln.lstrip().startswith("#"):
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def td(name: str, path: str, refresh: bool) -> dict:
    """One TwelveData call, cached by name. Pacing keeps the free plan's 8 requests/minute."""
    f = CACHE / f"{name}.json"
    if f.is_file() and not refresh:
        return json.loads(f.read_text())
    time.sleep(9)
    r = requests.get(f"https://api.twelvedata.com/{path}&apikey={os.environ['TWELVEDATA_API_KEY']}", headers={"User-Agent": UA}, timeout=60)
    js = r.json()
    if r.status_code != 200 or (isinstance(js, dict) and js.get("status") == "error"):
        raise SystemExit(f"{name}: provider error {js.get('code') if isinstance(js, dict) else r.status_code}: {js.get('message') if isinstance(js, dict) else ''}")
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(js))
    return js


def main(refresh=False):
    load_env()
    if not os.environ.get("TWELVEDATA_API_KEY"):
        raise SystemExit("TWELVEDATA_API_KEY absent: BLOCKED (nothing fetched)")
    for sym in ("MCD", "SPY"):
        td(f"{sym}_ts_none", f"time_series?symbol={sym}&interval=1day&outputsize=5000&adjust=none", refresh)
        td(f"{sym}_ts_all", f"time_series?symbol={sym}&interval=1day&outputsize=5000&adjust=all", refresh)
    facts = CACHE / "MCD_companyfacts.json"
    if refresh or not facts.is_file():
        sys.path.insert(0, str(REPO))
        from sec_adapter import SECAdapter
        js = SECAdapter().get_company_facts("0000063908")
        if not js:
            raise SystemExit("SEC company facts unavailable")
        facts.write_text(json.dumps(js))
    HERE.mkdir(exist_ok=True)
    for y in range(2006, 2027):
        f = HERE / f"treasury_par_yield_curve_{y}.csv"
        if refresh or not f.is_file():
            r = requests.get(TSY_URL.format(y=y), headers={"User-Agent": UA}, timeout=60)
            if r.status_code != 200 or not r.text.startswith("Date,"):
                raise SystemExit(f"Treasury {y}: HTTP {r.status_code}, unexpected content")
            f.write_text(r.text)
    out = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(CACHE.glob("*.json"))}
    print(json.dumps({"cached_twelvedata_files": out, "treasury_years": sorted(p.name for p in HERE.glob("treasury_par_yield_curve_*.csv"))}, indent=1))


if __name__ == "__main__":
    main("--refresh" in sys.argv)
