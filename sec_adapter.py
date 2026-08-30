"""
SEC Data Adapter

Provides deterministic access to SEC filings, company facts, and XBRL data.
Implements rate limiting, caching, and filing archive.
Rate limit target: ≤8 requests/second (well below SEC's maximum).
"""

import os
import time
import json
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# SEC ADAPTER CONFIGURATION
# ============================================================================

SEC_BASE_URL = "https://data.sec.gov"
SEC_WWW_URL = "https://www.sec.gov"
SEC_FILINGS_URL = f"{SEC_BASE_URL}/submissions"
SEC_FACTS_URL = f"{SEC_BASE_URL}/api/xbrl"
# Ticker -> CIK map (published on www.sec.gov, not data.sec.gov)
SEC_COMPANY_TICKERS_URL = f"{SEC_WWW_URL}/files/company_tickers.json"

# Rate limiting
SEC_RATE_LIMIT = 8  # requests per second (SEC allows more, we're conservative)
SEC_REQUEST_INTERVAL = 1.0 / SEC_RATE_LIMIT  # seconds between requests

# Cache configuration
CACHE_DIR = Path(os.getenv("CACHE_DIR", "/tmp/atlas_cache/sec"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FILING_ARCHIVE_DIR = Path(os.getenv("FILING_ARCHIVE_DIR", "/tmp/atlas_archive/sec"))
FILING_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# Request headers
USER_AGENT = "AtlasEquities/1.0 (contact@example.com)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Encoding": "gzip, deflate"
}


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """
    Implements rate limiting for SEC requests.
    Ensures we stay below SEC's published maximum.
    """

    def __init__(self, requests_per_second: float = SEC_RATE_LIMIT):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0

    def wait(self):
        """Wait until next request is allowed."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()


rate_limiter = RateLimiter(SEC_RATE_LIMIT)


# ============================================================================
# CACHING
# ============================================================================

def get_cache_path(cache_key: str) -> Path:
    """Generate cache file path."""
    safe_key = hashlib.md5(cache_key.encode()).hexdigest()
    return CACHE_DIR / f"{safe_key}.json"


def get_from_cache(cache_key: str, max_age_seconds: int = 86400) -> Optional[Dict]:
    """
    Retrieve from cache if valid.

    Args:
        cache_key: Key to cache
        max_age_seconds: Maximum age of cache (default 24 hours)

    Returns:
        Cached data or None if not found/stale
    """
    cache_path = get_cache_path(cache_key)
    if not cache_path.exists():
        return None

    file_age = time.time() - cache_path.stat().st_mtime
    if file_age > max_age_seconds:
        logger.debug(f"Cache expired for {cache_key}")
        return None

    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading cache {cache_key}: {e}")
        return None


def save_to_cache(cache_key: str, data: Dict) -> None:
    """Save data to cache."""
    cache_path = get_cache_path(cache_key)
    try:
        with open(cache_path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error writing cache {cache_key}: {e}")


# ============================================================================
# SEC ADAPTER
# ============================================================================

class SECAdapter:
    """
    Provides deterministic access to SEC data via official API.
    Implements rate limiting, caching, and filing archive.
    """

    def __init__(self, rate_limit: float = SEC_RATE_LIMIT, cache_enabled: bool = True):
        self.rate_limit = rate_limit
        self.cache_enabled = cache_enabled
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.last_error = None
        self.last_success = None

    def _request(self, url: str, timeout: int = 10, cache_key: Optional[str] = None) -> Optional[Dict]:
        """
        Make HTTP request to SEC with rate limiting and caching.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            cache_key: Optional cache key for result

        Returns:
            JSON response or None on error
        """
        # Try cache first
        if cache_key and self.cache_enabled:
            cached = get_from_cache(cache_key)
            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return cached

        # Rate limit
        rate_limiter.wait()

        # Make request
        try:
            logger.debug(f"SEC request: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            self.last_success = datetime.utcnow()

            # Save to cache
            if cache_key and self.cache_enabled:
                save_to_cache(cache_key, data)

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"SEC request failed: {url} - {e}")
            self.last_error = str(e)
            return None

    @staticmethod
    def _norm_ticker(t: str) -> str:
        """Normalize a ticker for matching. SEC uses a hyphen for share-class /
        preferred tickers (e.g. "BRK-B", "JPM-PC"); callers often pass the dotted
        form ("BRK.B")."""
        return str(t or "").upper().strip().replace(".", "-")

    def get_company_tickers(self) -> Optional[Dict]:
        """
        Fetch the SEC ticker -> CIK map.

        SEC publishes it as a single JSON object keyed by row index:
        {"0": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"}, ...}
        One row per listed ticker, so a single issuer (CIK) can appear on several
        rows (e.g. BRK-A and BRK-B both map to CIK 1067983).
        """
        return self._request(SEC_COMPANY_TICKERS_URL, cache_key="cik_lookup_all")

    def resolve_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Resolve a ticker to its SEC row.

        Returns ``{"cik": <10-digit>, "sec_ticker": <exact SEC ticker>,
        "title": <issuer title>}`` or None. ``sec_ticker`` is the hyphenated form
        SEC (and most market-data vendors) expect — preserve it for downstream
        adapters rather than the caller's dotted input.
        """
        data = self.get_company_tickers()
        if not data:
            return None

        wanted = self._norm_ticker(ticker)
        for row in data.values():
            if self._norm_ticker(row.get("ticker", "")) == wanted:
                return {
                    "cik": str(int(row["cik_str"])).zfill(10),
                    "sec_ticker": row.get("ticker"),
                    "title": row.get("title"),
                }

        logger.warning(f"ticker not found in SEC company_tickers: {ticker}")
        return None

    def tickers_for_cik(self, cik: str) -> List[Dict]:
        """
        List every SEC ticker row that maps to ``cik``.

        Used to enumerate the distinct securities (share classes, preferred
        series) that share one issuer CIK. Returns [] if the map is unavailable.
        """
        data = self.get_company_tickers()
        if not data:
            return []
        try:
            target = int(cik)
        except (TypeError, ValueError):
            return []
        rows = []
        for row in data.values():
            if int(row.get("cik_str", -1)) == target:
                rows.append({"sec_ticker": row.get("ticker"), "title": row.get("title")})
        return rows

    def resolve_cik(self, ticker: str) -> Optional[str]:
        """
        Resolve ticker to CIK (zero-padded 10 digits) or None.

        Thin wrapper over resolve_ticker for callers that only need the issuer
        CIK. Note: a CIK identifies the ISSUER, not the security/share class —
        use resolve_ticker (or identity_resolver.resolve_security) when the
        distinction matters.
        """
        row = self.resolve_ticker(ticker)
        return row["cik"] if row else None

    def get_company_submissions(self, cik: str) -> Optional[Dict]:
        """
        Get company submissions (10-K, 10-Q, etc).

        Args:
            cik: 10-digit CIK (zero-padded)

        Returns:
            Submissions data or None
        """
        cache_key = f"submissions_{cik}"

        # Normalize CIK
        cik_normalized = str(int(cik)).zfill(10)

        url = f"{SEC_FILINGS_URL}/CIK{cik_normalized}.json"
        return self._request(url, cache_key=cache_key)

    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """
        Get company facts (XBRL tagged data).

        Args:
            cik: 10-digit CIK (zero-padded)

        Returns:
            Company facts or None
        """
        cache_key = f"facts_{cik}"

        cik_normalized = str(int(cik)).zfill(10)

        url = f"{SEC_FACTS_URL}/companyfacts/CIK{cik_normalized}.json"
        return self._request(url, cache_key=cache_key)

    # Fields SEC exposes as parallel arrays under filings.recent. These are the
    # ones downstream code relies on; each is preserved verbatim (raw SEC value).
    RECENT_FILING_FIELDS = (
        "accessionNumber",
        "form",
        "filingDate",
        "reportDate",
        "acceptanceDateTime",
        "primaryDocument",
        "primaryDocDescription",
        "isXBRL",
        "isInlineXBRL",
        "size",
    )

    @staticmethod
    def _iter_recent_filings(submissions: Dict):
        """
        Yield one dict per filing from the SEC ``filings.recent`` block.

        SEC returns ``recent`` as a dict of column arrays (accessionNumber[],
        form[], acceptanceDateTime[], ...), NOT a list of records. This zips the
        columns back into per-filing rows by index. Missing/short columns yield
        ``None`` for that field (never a substituted value).
        """
        recent = (submissions or {}).get("filings", {}).get("recent", {})
        if not isinstance(recent, dict):
            return
        accessions = recent.get("accessionNumber", []) or []
        for i in range(len(accessions)):
            row = {}
            for field in SECAdapter.RECENT_FILING_FIELDS:
                col = recent.get(field, [])
                row[field] = col[i] if isinstance(col, list) and i < len(col) else None
            yield row

    def get_recent_filings(self, cik: str, form_type: str = "10-K", limit: int = 10) -> List[Dict]:
        """
        Get recent filings of a specific type, newest first.

        Args:
            cik: 10-digit CIK
            form_type: Form type (10-K, 10-Q, 8-K, etc)
            limit: Maximum filings to return

        Returns:
            List of filing metadata dicts (raw SEC field names/values preserved)
        """
        submissions = self.get_company_submissions(cik)
        if not submissions or "filings" not in submissions:
            return []

        filings = []
        for filing in self._iter_recent_filings(submissions):
            if filing.get("form") == form_type:
                filings.append(filing)
                if len(filings) >= limit:
                    break

        return filings

    def get_filing_metadata(self, cik: str, accession: str) -> Optional[Dict]:
        """
        Get metadata for a specific filing by accession number.

        Args:
            cik: 10-digit CIK
            accession: Accession number (e.g., "0001193125-26-323660")

        Returns:
            Filing metadata dict (raw SEC values preserved) or None if not in
            the recent-filings window.
        """
        submissions = self.get_company_submissions(cik)
        if not submissions:
            return None

        for filing in self._iter_recent_filings(submissions):
            if filing.get("accessionNumber") == accession:
                return filing

        # Older filings live in filings.files[*].name (paged JSON); not fetched here.
        return None

    def download_filing(self, cik: str, accession: str, filename: str = "0001144659-21-015555.htm") -> Optional[str]:
        """
        Download filing document from EDGAR.

        Args:
            cik: 10-digit CIK
            accession: Accession number
            filename: Document filename within filing

        Returns:
            Document content or None
        """
        # Convert accession format
        accession_path = accession.replace("-", "")

        url = f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={int(cik)}&accession_number={accession}&xbrl_type=v"

        # Fallback direct URL
        cik_normalized = str(int(cik)).zfill(10)
        url = f"https://www.sec.gov/Archives/edgar/container/1144659/{accession_path}/{filename}"

        try:
            rate_limiter.wait()
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.last_success = datetime.utcnow()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download filing {accession}: {e}")
            self.last_error = str(e)
            return None

    def archive_filing(
        self,
        cik: str,
        accession: str,
        form_type: str,
        filed_date: str,
        period_end: str,
        content: str,
        response_hash: Optional[str] = None,
        sec_acceptance_datetime: Optional[str] = None
    ) -> Dict:
        """
        Archive raw filing for future reference.
        Immutable archive prevents data loss.
        Preserves SEC acceptance timestamp with timezone.

        Args:
            cik: 10-digit CIK
            accession: Accession number
            form_type: Form type (10-K, 10-Q, etc)
            filed_date: Date filed (YYYY-MM-DD)
            period_end: Period end date (YYYY-MM-DD)
            content: Raw filing content
            response_hash: Optional hash of response
            sec_acceptance_datetime: SEC EDGAR acceptance timestamp (raw, Eastern Time)

        Returns:
            Archive metadata
        """
        # Create archive directory structure
        archive_subdir = FILING_ARCHIVE_DIR / cik / accession
        archive_subdir.mkdir(parents=True, exist_ok=True)

        # Generate response hash if not provided
        if not response_hash:
            response_hash = hashlib.sha256(content.encode()).hexdigest()

        # Archive metadata
        metadata = {
            "cik": cik,
            "accession_number": accession,
            "form_type": form_type,
            "filed_date": filed_date,
            "period_end": period_end,
            "response_hash": response_hash,
            "retrieved_at": datetime.utcnow().isoformat(),
            "parser_version": "1.0",
            "schema_version": "1.0"
        }

        # Save metadata
        metadata_path = archive_subdir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Save content
        content_path = archive_subdir / "filing.xml"
        with open(content_path, "w") as f:
            f.write(content)

        logger.info(f"Archived filing: {cik}/{accession}")

        return metadata

    def get_archived_filing(self, cik: str, accession: str) -> Optional[Dict]:
        """
        Retrieve archived filing.

        Args:
            cik: 10-digit CIK
            accession: Accession number

        Returns:
            Filing content and metadata or None
        """
        archive_subdir = FILING_ARCHIVE_DIR / cik / accession

        if not archive_subdir.exists():
            return None

        try:
            # Load metadata
            metadata_path = archive_subdir / "metadata.json"
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Load content
            content_path = archive_subdir / "filing.xml"
            with open(content_path, "r") as f:
                content = f.read()

            return {
                "metadata": metadata,
                "content": content
            }
        except Exception as e:
            logger.error(f"Error reading archived filing: {e}")
            return None

    def get_provider_status(self) -> Dict[str, Any]:
        """Get provider health status."""
        return {
            "provider": "SEC",
            "status": "AVAILABLE" if self.last_success else "UNKNOWN",
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error,
            "rate_limit": f"{self.rate_limit} req/sec"
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_sec_adapter = None


def get_sec_adapter() -> SECAdapter:
    """Get SEC adapter singleton."""
    global _sec_adapter
    if _sec_adapter is None:
        _sec_adapter = SECAdapter()
    return _sec_adapter
