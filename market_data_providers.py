"""
Free / public market-data provider adapters (Phase 4A.5.2 benchmark).

Thin, uniform adapters over the candidate FREE providers. This is BENCHMARK
infrastructure, not a production market-data build-out:

  - one common interface (MarketDataProvider) + thin per-provider adapters
  - every call returns an MDResult envelope with an explicit state
    (AVAILABLE / UNAVAILABLE / AMBIGUOUS / STALE / RATE_LIMITED / ERROR /
     NOT_EXERCISED / NOT_ELIGIBLE) — never a bare number, never zero, never a
     silent fallback to a different symbol
  - identity is Atlas-side: a provider symbol is only a lookup string; the
    observation is bound to the Stock Atlas security_key
    (identity_resolver.market_price_join_key), never the bare issuer CIK

Credentials are read from the environment. With no key an adapter is disabled
and reports NOT_EXERCISED (Twelve Data additionally supports the vendor's public
"demo" key, which only serves AAPL).
"""

import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from identity_resolver import market_price_join_key, IdentityJoinError

# ---------------------------------------------------------------------------
# result envelope
# ---------------------------------------------------------------------------
STATES = (
    "AVAILABLE", "UNAVAILABLE", "AMBIGUOUS", "STALE",
    "RATE_LIMITED", "ERROR", "NOT_EXERCISED", "NOT_ELIGIBLE",
)

CAPABILITIES = ("resolve", "latest_price", "daily_history", "dividends", "splits")

# Precise feed classification (Phase 4A.5.2A). A latest-price observation is
# labelled with exactly one of these — never left implicit.
FEED_CLASSES = ("REAL_TIME", "DELAYED", "EOD", "IEX_ONLY", "UNKNOWN")

# Usage-rights verdicts for the Stock Atlas audit/provenance use case
# (persistent decision records, private use by two people). Derived ONLY from
# each provider's written terms — no interpretation beyond the text.
USAGE_RIGHTS_VERDICTS = (
    "ELIGIBLE",
    "ELIGIBLE_WITH_LIMITATIONS",
    "INCOMPATIBLE_WITH_ATLAS_USE",
    "UNCLEAR_REQUIRES_CONFIRMATION",
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MDResult:
    provider: str
    capability: str
    query_symbol: str
    atlas_symbol: str
    state: str
    security_key: Optional[str] = None
    data: Any = None
    raw: Any = None
    provider_symbol_returned: Optional[str] = None
    provider_timestamp: Optional[str] = None
    provider_timezone: Optional[str] = None
    feed_class: Optional[str] = None          # one of FEED_CLASSES
    stated_delay: Optional[str] = None
    retrieved_at: str = field(default_factory=_utcnow_iso)
    http_status: Optional[int] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        # keep raw payloads small in artifacts
        if isinstance(self.raw, (dict, list)):
            d["raw"] = _truncate(self.raw)
        return d


def _truncate(obj, limit=1500):
    import json
    s = json.dumps(obj, default=str)
    return obj if len(s) <= limit else {"_truncated": s[:limit] + "..."}


# ---------------------------------------------------------------------------
# base
# ---------------------------------------------------------------------------
class MarketDataProvider:
    name = "base"
    eligibility = "NOT_ELIGIBLE"          # FREE_PUBLIC / FREE_WITH_KEY / FREE_MATERIAL_LIMITS / NOT_ELIGIBLE
    homepage = ""
    key_env = ()                          # tuple of env var names required
    published_limits = {}
    # Usage rights for the Stock Atlas use case — quotes/paraphrase of the
    # provider's WRITTEN terms only (Phase 4A.5.2A). Keys:
    #   verdict, persistent_storage, personal_internal_use, two_person_private_use,
    #   redistribution_display, audit_store_compatible, source
    usage_rights = {
        "verdict": "UNCLEAR_REQUIRES_CONFIRMATION",
        "source": "n/a",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "StockAtlas-4A52-benchmark/0.1"})
        self._configure()

    # --- credential / enablement -------------------------------------------
    def _configure(self):
        self.credentials = {k: os.getenv(k) for k in self.key_env}
        self.enabled = all(self.credentials.values()) if self.key_env else True

    def disabled_result(self, capability, atlas_symbol, query_symbol) -> MDResult:
        return MDResult(
            provider=self.name, capability=capability,
            atlas_symbol=atlas_symbol, query_symbol=query_symbol,
            state="NOT_EXERCISED",
            notes=[f"no credentials in environment ({', '.join(self.key_env) or 'n/a'}); "
                   f"adapter implemented but not exercised live"],
        )

    # --- Atlas symbol -> provider symbol ----------------------------------
    def provider_symbol(self, atlas_symbol: str) -> str:
        return atlas_symbol  # override per provider for share classes

    def _security_key(self, atlas_symbol: str) -> Optional[str]:
        try:
            return market_price_join_key(atlas_symbol)
        except IdentityJoinError:
            return None

    # --- capability stubs (override) -------------------------------------
    def resolve_symbol(self, atlas_symbol: str) -> MDResult:
        raise NotImplementedError

    def latest_price(self, atlas_symbol: str) -> MDResult:
        raise NotImplementedError

    def daily_history(self, atlas_symbol: str, days: int = 400) -> MDResult:
        raise NotImplementedError

    def dividends(self, atlas_symbol: str) -> MDResult:
        raise NotImplementedError

    def splits(self, atlas_symbol: str) -> MDResult:
        raise NotImplementedError

    # --- shared HTTP -----------------------------------------------------
    def _get(self, url, capability, atlas_symbol, query_symbol, **kw) -> tuple:
        """Returns (json_or_none, MDResult-on-failure-or-None)."""
        try:
            r = self.session.get(url, timeout=20, **kw)
        except requests.exceptions.RequestException as e:
            return None, MDResult(self.name, capability, query_symbol, atlas_symbol,
                                  "ERROR", notes=[f"request failed: {e!r}"])
        base = dict(provider=self.name, capability=capability, query_symbol=query_symbol,
                    atlas_symbol=atlas_symbol, http_status=r.status_code)
        if r.status_code == 429:
            return None, MDResult(**base, state="RATE_LIMITED", notes=["HTTP 429"])
        if r.status_code in (401, 403):
            return None, MDResult(**base, state="NOT_EXERCISED",
                                  notes=[f"HTTP {r.status_code}: credentials rejected/absent"])
        if r.status_code == 404:
            return None, MDResult(**base, state="UNAVAILABLE", notes=["HTTP 404"])
        if r.status_code >= 400:
            return None, MDResult(**base, state="ERROR", notes=[f"HTTP {r.status_code}: {r.text[:200]}"])
        try:
            return r.json(), None
        except ValueError:
            return None, MDResult(**base, state="ERROR", notes=["non-JSON response"])


# ---------------------------------------------------------------------------
# Twelve Data  (https://twelvedata.com)
# ---------------------------------------------------------------------------
class TwelveDataProvider(MarketDataProvider):
    name = "twelvedata"
    eligibility = "FREE_WITH_KEY"
    homepage = "https://twelvedata.com"
    key_env = ("TWELVEDATA_API_KEY",)
    published_limits = {
        "free_tier": "Free 'Basic' plan, API key required (free, lifetime). 8 requests/minute, "
                     "800 API credits/day; 1 WebSocket connection, 8 symbols.",
        "history": "time_series free; outputsize<=5000. Adjusted-close column is a paid add-on "
                   "on the free plan (OHLC is split-adjusted).",
        "realtime": "Current pricing page states the free Basic plan includes real-time US "
                    "stocks & ETFs, subject to per-plan credit / endpoint limits. ACTUAL feed "
                    "class must be confirmed with a real Basic key — the public 'demo' key does "
                    "not prove plan behaviour. Harness classifies from live quote freshness.",
        "corporate_actions": "/dividends and /splits available on free plan.",
        "demo_key": "public 'demo' key serves ONLY AAPL and must not be generalised to the plan.",
    }
    usage_rights = {
        "verdict": "ELIGIBLE_WITH_LIMITATIONS",
        "persistent_storage": "Terms 2.3(g): may not 'store or cache Data beyond permitted "
                              "timeframes specified in the Documentation'; 16.1: retain Data only "
                              "for the subscription duration / regulatory compliance; delete within "
                              "30 days of termination. Documentation gives no explicit free-plan "
                              "retention window -> a bounded personal cache is defensible, an "
                              "indefinite audit store is not clearly permitted.",
        "personal_internal_use": "Terms 2.1: 'Internal Use' only (default grant).",
        "two_person_private_use": "Not addressed. Internal Use by a 2-person private household is "
                                  "not obviously prohibited but is not spelled out -> confirm.",
        "redistribution_display": "Prohibited without a Redistribution Rights Add-On (2.2(e)).",
        "commercial_use": "Free Tier data: commercial use explicitly PROHIBITED (2.3(l)).",
        "audit_store_compatible": "PARTIAL — bounded cache yes; permanent audit retention unclear.",
        "source": "twelvedata.com/terms (fetched 2026-08-30)",
    }
    BASE = "https://api.twelvedata.com"

    def _configure(self):
        super()._configure()
        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        self.using_demo = False
        if not self.api_key:
            self.api_key = "demo"          # vendor public key, AAPL only
            self.using_demo = True
        self.enabled = True                # always has at least demo

    def provider_symbol(self, atlas_symbol: str) -> str:
        return atlas_symbol.replace("-", ".")   # BRK-B -> BRK.B

    def _demo_guard(self, capability, atlas_symbol, sym) -> Optional[MDResult]:
        if self.using_demo and sym != "AAPL":
            return MDResult(self.name, capability, sym, atlas_symbol, "NOT_EXERCISED",
                            notes=["demo key only serves AAPL; supply TWELVEDATA_API_KEY for full coverage"])
        return None

    def _err_payload(self, js) -> Optional[str]:
        if isinstance(js, dict) and js.get("status") == "error":
            return js.get("message", "error")
        return None

    # US primary-listing exchanges — used to disambiguate a symbol_search result.
    _US_PRIMARY_MICS = {"XNYS", "XNAS", "XNGS", "XNMS", "ARCX", "BATS"}

    def resolve_symbol(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        # symbol_search is NOT demo-restricted — it works for every symbol and is
        # where the identity/ambiguity signal lives.
        js, fail = self._get(f"{self.BASE}/symbol_search?symbol={sym}&apikey={self.api_key}&outputsize=30",
                             "resolve", atlas_symbol, sym)
        if fail:
            return fail
        matches = (js or {}).get("data", []) or []
        exact = [m for m in matches if str(m.get("symbol", "")).upper() == sym.upper()]
        us_primary = [m for m in exact
                      if m.get("country") == "United States"
                      and m.get("instrument_type") in ("Common Stock", "ETF", "REIT")
                      and m.get("mic_code") in self._US_PRIMARY_MICS]
        notes = []
        if len(us_primary) == 1:
            state = "AVAILABLE"
            chosen = us_primary[0]
        elif len(us_primary) > 1:
            state = "AMBIGUOUS"
            chosen = us_primary[0]
            notes.append(f"{len(us_primary)} US-primary common-stock matches for {sym!r}")
        elif exact:
            state = "AMBIGUOUS"
            chosen = exact[0]
            notes.append(f"no US-primary match; {len(exact)} exact-symbol matches across venues")
        else:
            return MDResult(self.name, "resolve", sym, atlas_symbol, "UNAVAILABLE",
                            raw={"matches": matches[:6]}, notes=["symbol_search returned no exact match"])

        # optional live confirmation via /quote (demo key: AAPL only)
        quote_confirmed = None
        if not (self.using_demo and sym != "AAPL"):
            q, qfail = self._get(f"{self.BASE}/quote?symbol={sym}&apikey={self.api_key}",
                                 "resolve", atlas_symbol, sym)
            if not qfail and not self._err_payload(q):
                quote_confirmed = {"symbol": q.get("symbol"), "name": q.get("name"),
                                   "exchange": q.get("exchange"), "mic_code": q.get("mic_code")}

        return MDResult(
            self.name, "resolve", sym, atlas_symbol, state,
            security_key=self._security_key(atlas_symbol),
            data={"provider_symbol": chosen.get("symbol"),
                  "instrument_name": chosen.get("instrument_name"),
                  "exchange": chosen.get("exchange"), "mic_code": chosen.get("mic_code"),
                  "instrument_type": chosen.get("instrument_type"),
                  "currency": chosen.get("currency"),
                  "us_primary_match_count": len(us_primary),
                  "quote_confirmed": quote_confirmed},
            raw={"matches": matches[:6]}, provider_symbol_returned=chosen.get("symbol"), notes=notes,
        )

    def latest_price(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        g = self._demo_guard("latest_price", atlas_symbol, sym)
        if g:
            return g
        js, fail = self._get(f"{self.BASE}/quote?symbol={sym}&apikey={self.api_key}",
                             "latest_price", atlas_symbol, sym)
        if fail:
            return fail
        if self._err_payload(js):
            return MDResult(self.name, "latest_price", sym, atlas_symbol, "UNAVAILABLE",
                            raw=js, notes=[self._err_payload(js)])
        ts = js.get("timestamp")
        prov_ts = datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat() if ts else js.get("datetime")
        age_s = None
        if ts:
            age_s = (datetime.now(timezone.utc)
                     - datetime.fromtimestamp(int(ts), tz=timezone.utc)).total_seconds()
        stale = "STALE" if (age_s is not None and age_s > 96 * 3600) else None
        mkt_open = js.get("is_market_open")
        feed = classify_feed_from_age(age_s, market_open=mkt_open)
        return MDResult(
            self.name, "latest_price", sym, atlas_symbol, stale or "AVAILABLE",
            security_key=self._security_key(atlas_symbol),
            data={"price": _f(js.get("close")), "previous_close": _f(js.get("previous_close")),
                  "open": _f(js.get("open")), "day_high": _f(js.get("high")), "day_low": _f(js.get("low")),
                  "volume": _f(js.get("volume")), "is_market_open": mkt_open,
                  "exchange": js.get("exchange"), "mic_code": js.get("mic_code"),
                  "observation_age_seconds": age_s},
            raw=js, provider_symbol_returned=js.get("symbol"),
            provider_timestamp=prov_ts, provider_timezone=js.get("exchange_timezone", "America/New_York"),
            feed_class=feed,
            stated_delay="feed class derived from live quote freshness "
                         f"(age={round(age_s) if age_s is not None else '?'}s, market_open={mkt_open})",
            notes=(["market closed: 'close' is the latest session close"] if mkt_open is False
                   else ["classified from observation age while market open"])
            + (["age>96h -> STALE"] if stale else []),
        )

    def daily_history(self, atlas_symbol, days=400):
        sym = self.provider_symbol(atlas_symbol)
        g = self._demo_guard("daily_history", atlas_symbol, sym)
        if g:
            return g
        n = min(max(days, 5), 5000)
        js, fail = self._get(
            f"{self.BASE}/time_series?symbol={sym}&interval=1day&outputsize={n}"
            f"&apikey={self.api_key}&adjust=all", "daily_history", atlas_symbol, sym)
        if fail:
            return fail
        if self._err_payload(js):
            return MDResult(self.name, "daily_history", sym, atlas_symbol, "UNAVAILABLE",
                            raw=js, notes=[self._err_payload(js)])
        vals = js.get("values", []) or []
        bars = [{"date": v.get("datetime"), "open": _f(v.get("open")), "high": _f(v.get("high")),
                 "low": _f(v.get("low")), "close": _f(v.get("close")),
                 "adjusted_close": _f(v.get("adjusted_close")) if v.get("adjusted_close") else None,
                 "volume": _f(v.get("volume"))} for v in vals]
        has_adj = any(b["adjusted_close"] is not None for b in bars)
        return MDResult(
            self.name, "daily_history", sym, atlas_symbol,
            "AVAILABLE" if bars else "UNAVAILABLE",
            security_key=self._security_key(atlas_symbol),
            data={"bar_count": len(bars), "first": bars[-1]["date"] if bars else None,
                  "last": bars[0]["date"] if bars else None,
                  "has_adjusted_close": has_adj, "adjustment_status": "split-adjusted OHLC; no adj-close column on free plan"},
            raw={"meta": js.get("meta"), "sample": bars[:3]},
            provider_timezone=js.get("meta", {}).get("exchange_timezone"),
            feed_class="EOD", notes=[] if bars else ["no values returned"],
        )

    def dividends(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        g = self._demo_guard("dividends", atlas_symbol, sym)
        if g:
            return g
        js, fail = self._get(f"{self.BASE}/dividends?symbol={sym}&apikey={self.api_key}&range=full",
                             "dividends", atlas_symbol, sym)
        if fail:
            return fail
        if self._err_payload(js):
            return MDResult(self.name, "dividends", sym, atlas_symbol, "UNAVAILABLE",
                            raw=js, notes=[self._err_payload(js)])
        divs = js.get("dividends", []) or []
        rows = [{"ex_date": d.get("ex_date"), "payment_date": d.get("payment_date"),
                 "declared_date": d.get("declared_date"), "amount": _f(d.get("amount")),
                 "currency": js.get("meta", {}).get("currency")} for d in divs]
        return MDResult(
            self.name, "dividends", sym, atlas_symbol,
            "AVAILABLE" if rows else "UNAVAILABLE",
            security_key=self._security_key(atlas_symbol),
            data={"count": len(rows), "latest": rows[0] if rows else None,
                  "fields_present": sorted({k for r in rows for k, v in r.items() if v is not None})},
            raw={"sample": rows[:4]},
            notes=["free plan returns ex_date + amount only; no payment/declared date"] if rows else ["none"],
        )

    def splits(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        g = self._demo_guard("splits", atlas_symbol, sym)
        if g:
            return g
        js, fail = self._get(f"{self.BASE}/splits?symbol={sym}&apikey={self.api_key}&range=full",
                             "splits", atlas_symbol, sym)
        if fail:
            return fail
        if self._err_payload(js):
            return MDResult(self.name, "splits", sym, atlas_symbol, "UNAVAILABLE",
                            raw=js, notes=[self._err_payload(js)])
        sp = js.get("splits", []) or []
        rows = [{"date": s.get("date"), "description": s.get("description"),
                 "ratio": _f(s.get("ratio")), "from_factor": s.get("from_factor"),
                 "to_factor": s.get("to_factor")} for s in sp]
        return MDResult(
            self.name, "splits", sym, atlas_symbol,
            "AVAILABLE" if rows else "UNAVAILABLE",
            security_key=self._security_key(atlas_symbol),
            data={"count": len(rows), "events": rows},
            raw={"sample": rows[:4]},
            notes=["split events are explicitly typed (from_factor/to_factor), distinct from price moves"]
            if rows else ["no splits on record"],
        )


# ---------------------------------------------------------------------------
# Alpaca Market Data  (https://alpaca.markets)
# ---------------------------------------------------------------------------
class AlpacaProvider(MarketDataProvider):
    name = "alpaca"
    eligibility = "FREE_WITH_KEY"
    homepage = "https://alpaca.markets"
    key_env = ("ALPACA_API_KEY_ID", "ALPACA_API_SECRET_KEY")
    published_limits = {
        "free_tier": "Free account (paper trading is enough). 200 requests/minute.",
        "feed": "Free data = IEX feed only (single venue, ~2-3% of consolidated volume), not full "
                "SIP. REST feed=iex is real-time for the IEX venue; SIP data is 15-min delayed on free.",
        "history": "Historical bars: 7+ years on IEX feed.",
        "corporate_actions": "/v1/corporate-actions covers splits, dividends, mergers, spinoffs.",
        "identity": "share classes use dotted tickers (BRK.A / BRK.B).",
    }
    usage_rights = {
        "verdict": "ELIGIBLE_WITH_LIMITATIONS",
        "persistent_storage": "Alpaca Data terms do not prohibit storing consumed data for the "
                              "subscriber's own use; the binding constraint is the IEX "
                              "Non-Professional Subscriber Agreement (via Alpaca).",
        "personal_internal_use": "IEX agreement: Non-Professional Subscriber may use Market Data "
                                 "'solely for personal, non-business use' / managing own assets.",
        "two_person_private_use": "Each individual receiving real-time IEX data must be a "
                                  "subscriber under the agreement -> two people need two free "
                                  "accounts; one shared account is not clearly permitted.",
        "redistribution_display": "'Subscriber shall not furnish Market Data to any other person "
                                  "or entity' — no redistribution / external display.",
        "commercial_use": "Non-Professional status excludes business/commercial use of real-time data.",
        "audit_store_compatible": "YES for EOD/derived records under personal non-business use; "
                                  "real-time redistribution/display is not.",
        "source": "alpaca.markets/data + IEX Non-Professional Subscriber Agreement (fetched 2026-08-30)",
    }
    DATA = "https://data.alpaca.markets"

    def _headers(self):
        return {"APCA-API-KEY-ID": self.credentials["ALPACA_API_KEY_ID"],
                "APCA-API-SECRET-KEY": self.credentials["ALPACA_API_SECRET_KEY"]}

    def provider_symbol(self, atlas_symbol: str) -> str:
        return atlas_symbol.replace("-", ".")

    def resolve_symbol(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("resolve", atlas_symbol, sym)
        js, fail = self._get(f"{self.DATA}/v2/stocks/{sym}/snapshot", "resolve", atlas_symbol, sym,
                             headers=self._headers())
        if fail:
            return fail
        ok = bool(js.get("latestTrade") or js.get("latestQuote"))
        return MDResult(self.name, "resolve", sym, atlas_symbol,
                        "AVAILABLE" if ok else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"symbol": sym, "has_trade": bool(js.get("latestTrade"))},
                        raw=js, provider_symbol_returned=sym,
                        notes=["Alpaca has no fuzzy symbol search; the ticker is the exact key"])

    def latest_price(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("latest_price", atlas_symbol, sym)
        js, fail = self._get(f"{self.DATA}/v2/stocks/{sym}/trades/latest?feed=iex",
                             "latest_price", atlas_symbol, sym, headers=self._headers())
        if fail:
            return fail
        t = js.get("trade", {})
        prov_ts = t.get("t")
        stale = None
        if prov_ts:
            try:
                age = (datetime.now(timezone.utc)
                       - datetime.fromisoformat(prov_ts.replace("Z", "+00:00"))).total_seconds()
                stale = "STALE" if age > 96 * 3600 else None
            except ValueError:
                pass
        return MDResult(self.name, "latest_price", sym, atlas_symbol, stale or ("AVAILABLE" if t else "UNAVAILABLE"),
                        security_key=self._security_key(atlas_symbol),
                        data={"price": t.get("p"), "size": t.get("s"), "venue": t.get("x")},
                        raw=js, provider_timestamp=prov_ts, provider_timezone="UTC",
                        feed_class="IEX_ONLY", stated_delay="IEX venue only; not consolidated SIP",
                        notes=["free feed=iex: real-time for the IEX venue, single venue only"])

    def daily_history(self, atlas_symbol, days=400):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("daily_history", atlas_symbol, sym)
        start = f"{datetime.now(timezone.utc).year - 2}-01-01"
        js, fail = self._get(
            f"{self.DATA}/v2/stocks/{sym}/bars?timeframe=1Day&start={start}&limit=10000&adjustment=all&feed=iex",
            "daily_history", atlas_symbol, sym, headers=self._headers())
        if fail:
            return fail
        bars = js.get("bars", []) or []
        rows = [{"date": b.get("t"), "open": b.get("o"), "high": b.get("h"), "low": b.get("l"),
                 "close": b.get("c"), "volume": b.get("v"), "vwap": b.get("vw")} for b in bars]
        return MDResult(self.name, "daily_history", sym, atlas_symbol,
                        "AVAILABLE" if rows else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"bar_count": len(rows), "adjustment_status": "adjustment=all (split+dividend adjusted)",
                              "first": rows[0]["date"] if rows else None, "last": rows[-1]["date"] if rows else None},
                        raw={"sample": rows[:3]}, feed_class="EOD")

    def dividends(self, atlas_symbol):
        return self._corporate_actions(atlas_symbol, "dividends", "cash_dividends")

    def splits(self, atlas_symbol):
        return self._corporate_actions(atlas_symbol, "splits", "forward_splits")

    def _corporate_actions(self, atlas_symbol, capability, ca_type):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result(capability, atlas_symbol, sym)
        start = "2015-01-01"
        js, fail = self._get(
            f"{self.DATA}/v1/corporate-actions?symbols={sym}&types={ca_type}&start={start}&limit=1000",
            capability, atlas_symbol, sym, headers=self._headers())
        if fail:
            return fail
        events = (js.get("corporate_actions", {}) or {}).get(ca_type, []) or []
        return MDResult(self.name, capability, sym, atlas_symbol,
                        "AVAILABLE" if events else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"count": len(events), "sample": events[:4], "ca_type": ca_type},
                        raw={"sample": events[:4]},
                        notes=[f"typed corporate action '{ca_type}' — distinct from price movement"])


# ---------------------------------------------------------------------------
# Tiingo  (https://tiingo.com)
# ---------------------------------------------------------------------------
class TiingoProvider(MarketDataProvider):
    name = "tiingo"
    eligibility = "FREE_WITH_KEY"
    homepage = "https://tiingo.com"
    key_env = ("TIINGO_API_TOKEN",)
    published_limits = {
        "free_tier": "Free 'Starter' plan. 50 requests/hour, 1000 requests/day, 500 unique "
                     "symbols/month, 1 GB/month bandwidth.",
        "history": "EOD daily prices with adjClose, adjOpen/High/Low, divCash, splitFactor columns; "
                   "30+ years of price history on the free plan.",
        "realtime": "/iex endpoint = real-time IEX (single venue). EOD covers consolidated close.",
        "corporate_actions": "dividends (divCash) and splits (splitFactor) are embedded in the daily price rows.",
    }
    usage_rights = {
        "verdict": "INCOMPATIBLE_WITH_ATLAS_USE",
        "persistent_storage": "Starter/Trial terms: 'you may not write, save, archive, back up, or "
                              "otherwise retain Tiingo Data in any persistent or durable storage'; "
                              "'process Tiingo Data only transiently in volatile memory or in a "
                              "temporary, non-persistent cache'; 'permanently remove ... immediately "
                              "after the calculation or operation is completed'. Applies to "
                              "databases, object stores, file systems, logs, backups.",
        "personal_internal_use": "Internal / personal use only.",
        "two_person_private_use": "'you may not display or share the data with another person or "
                                  "organization' -> a second person is not permitted on the free plan.",
        "redistribution_display": "Prohibited on the free plan; requires a paid Power/redistribution license.",
        "commercial_use": "Requires the paid Power plan.",
        "audit_store_compatible": "NO — explicit prohibition on persistent/durable storage is "
                                  "directly incompatible with Stock Atlas provenance/audit records.",
        "source": "app.tiingo.com/tos + tiingo.com/about/pricing (fetched 2026-08-30)",
    }
    BASE = "https://api.tiingo.com"

    def _params(self):
        return {"token": self.credentials["TIINGO_API_TOKEN"]}

    def provider_symbol(self, atlas_symbol: str) -> str:
        return atlas_symbol.replace(".", "-")   # BRK.B -> BRK-B

    def resolve_symbol(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("resolve", atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/tiingo/daily/{sym}", "resolve", atlas_symbol, sym,
                             params=self._params())
        if fail:
            return fail
        return MDResult(self.name, "resolve", sym, atlas_symbol,
                        "AVAILABLE" if js.get("ticker") else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"ticker": js.get("ticker"), "name": js.get("name"),
                              "exchange": js.get("exchangeCode"), "start": js.get("startDate"),
                              "end": js.get("endDate")},
                        raw=js, provider_symbol_returned=js.get("ticker"))

    def latest_price(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("latest_price", atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/iex/{sym}", "latest_price", atlas_symbol, sym,
                             params=self._params())
        if fail:
            return fail
        row = (js or [None])[0] if isinstance(js, list) else js
        if not row:
            return MDResult(self.name, "latest_price", sym, atlas_symbol, "UNAVAILABLE", raw=js)
        prov_ts = row.get("timestamp") or row.get("lastSaleTimestamp") or row.get("quoteTimestamp")
        return MDResult(self.name, "latest_price", sym, atlas_symbol, "AVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"price": row.get("last") or row.get("tngoLast"),
                              "prev_close": row.get("prevClose"), "volume": row.get("volume")},
                        raw=row, provider_timestamp=prov_ts, provider_timezone="UTC",
                        feed_class="IEX_ONLY", stated_delay="IEX venue only")

    def daily_history(self, atlas_symbol, days=400):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("daily_history", atlas_symbol, sym)
        start = f"{datetime.now(timezone.utc).year - 2}-01-01"
        js, fail = self._get(f"{self.BASE}/tiingo/daily/{sym}/prices?startDate={start}",
                             "daily_history", atlas_symbol, sym, params=self._params())
        if fail:
            return fail
        rows = js if isinstance(js, list) else []
        return MDResult(self.name, "daily_history", sym, atlas_symbol,
                        "AVAILABLE" if rows else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"bar_count": len(rows),
                              "columns": sorted(rows[0].keys()) if rows else [],
                              "adjustment_status": "raw + adjusted columns both supplied; divCash/splitFactor inline",
                              "first": rows[0]["date"] if rows else None, "last": rows[-1]["date"] if rows else None},
                        raw={"sample": rows[:3]}, feed_class="EOD")

    def dividends(self, atlas_symbol):
        return self._from_daily(atlas_symbol, "dividends", "divCash")

    def splits(self, atlas_symbol):
        return self._from_daily(atlas_symbol, "splits", "splitFactor")

    def _from_daily(self, atlas_symbol, capability, col):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result(capability, atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/tiingo/daily/{sym}/prices?startDate=2015-01-01",
                             capability, atlas_symbol, sym, params=self._params())
        if fail:
            return fail
        rows = js if isinstance(js, list) else []
        if col == "divCash":
            events = [{"ex_date": r["date"], "amount": r.get("divCash")} for r in rows if r.get("divCash")]
        else:
            events = [{"date": r["date"], "split_factor": r.get("splitFactor")}
                      for r in rows if r.get("splitFactor") and r.get("splitFactor") != 1.0]
        return MDResult(self.name, capability, sym, atlas_symbol,
                        "AVAILABLE" if events else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"count": len(events), "sample": events[:4],
                              "source": f"embedded '{col}' column in daily prices"},
                        raw={"sample": events[:4]})


# ---------------------------------------------------------------------------
# Massive  (https://massive.com — Stocks REST API, Polygon-compatible surface)
# ---------------------------------------------------------------------------
# Phase 4A.5.2A correction: the Phase 4A.5.2 conclusion that "Massive" was not a
# real free equities API was WRONG — it confused massive.com's Stocks API with
# an unrelated proxy/bandwidth SDK. massive.com publishes a "Stocks Basic" $0/mo
# plan (EOD, ~2 years history, corporate actions, reference universe, 5 req/min)
# and a Polygon.io-shaped REST surface (/v2/aggs, /v1/open-close, /v3/reference,
# apiKey query param, api.massive.com host).
class MassiveProvider(MarketDataProvider):
    name = "massive"
    eligibility = "FREE_WITH_KEY"
    homepage = "https://massive.com"
    key_env = ("MASSIVE_API_KEY",)
    published_limits = {
        "free_tier": "'Stocks Basic' plan, $0/month. API key required. 5 API calls/minute.",
        "history": "~2 years of historical data on the Basic plan; minute + daily aggregates.",
        "realtime": "End-of-day data only on Basic (delayed/real-time are paid tiers).",
        "corporate_actions": "Corporate actions (dividends, splits, ticker events) included on Basic.",
        "reference": "Full US ticker reference / 100% market coverage on Basic; financials are paid.",
        "api_shape": "Polygon.io-compatible: /v2/aggs/ticker/{t}/range, /v2/aggs/ticker/{t}/prev, "
                     "/v3/reference/dividends, /v3/reference/splits, /v3/reference/tickers/{t}; "
                     "apiKey query parameter; host api.massive.com.",
    }
    usage_rights = {
        "verdict": "UNCLEAR_REQUIRES_CONFIRMATION",
        "persistent_storage": "Market Data Terms require deleting all Market Data on termination "
                              "(Section 8) but state no explicit retention limit during an active "
                              "subscription; personal archival vs prohibited 'copying' is not "
                              "spelled out -> confirm with Massive.",
        "personal_internal_use": "Individuals ToS: use 'solely for your own personal, non-commercial, "
                                 "and non-business purposes'. NYSE non-professional: 'personal, "
                                 "non-business use' / managing own assets.",
        "two_person_private_use": "Individuals ToS explicitly prohibits 'sharing an account or API "
                                  "keys with others' -> two people need two separate free accounts.",
        "redistribution_display": "No copying/republishing/redistribution/public display; no "
                                  "business or commercial enterprise use.",
        "commercial_use": "Prohibited on the Individuals terms / Basic plan.",
        "audit_store_compatible": "UNCLEAR — no explicit persistent-storage ban, but no explicit "
                                  "permission either; must be confirmed before relying on it as "
                                  "an audit store.",
        "source": "massive.com/legal/individuals-terms-of-service + "
                  "massive.com/legal/market-data-terms-of-service + massive.com/pricing (fetched 2026-08-30)",
    }
    BASE = "https://api.massive.com"

    def _params(self, **extra):
        p = {"apiKey": self.credentials["MASSIVE_API_KEY"]}
        p.update(extra)
        return p

    def resolve_symbol(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("resolve", atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/v3/reference/tickers/{sym}", "resolve", atlas_symbol, sym,
                             params=self._params())
        if fail:
            return fail
        res = js.get("results") or {}
        if not res:
            return MDResult(self.name, "resolve", sym, atlas_symbol, "UNAVAILABLE", raw=js,
                            notes=["no reference record for ticker"])
        return MDResult(self.name, "resolve", sym, atlas_symbol, "AVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"ticker": res.get("ticker"), "name": res.get("name"),
                              "primary_exchange": res.get("primary_exchange"),
                              "type": res.get("type"), "market": res.get("market"),
                              "cik": res.get("cik"), "composite_figi": res.get("composite_figi"),
                              "currency": res.get("currency_name")},
                        raw=res, provider_symbol_returned=res.get("ticker"),
                        notes=["exact-ticker reference lookup (no fuzzy search needed)"])

    def latest_price(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("latest_price", atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/v2/aggs/ticker/{sym}/prev", "latest_price", atlas_symbol, sym,
                             params=self._params(adjusted="true"))
        if fail:
            return fail
        rows = js.get("results") or []
        if not rows:
            return MDResult(self.name, "latest_price", sym, atlas_symbol, "UNAVAILABLE", raw=js,
                            notes=["no previous-close bar"])
        bar = rows[0]
        ts_ms = bar.get("t")
        prov_ts = (datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).isoformat()
                   if ts_ms else None)
        age_s = ((datetime.now(timezone.utc).timestamp() - ts_ms / 1000) if ts_ms else None)
        stale = "STALE" if (age_s is not None and age_s > 5 * 86400) else None
        return MDResult(self.name, "latest_price", sym, atlas_symbol, stale or "AVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"price": _f(bar.get("c")), "open": _f(bar.get("o")),
                              "day_high": _f(bar.get("h")), "day_low": _f(bar.get("l")),
                              "volume": _f(bar.get("v")), "vwap": _f(bar.get("vw")),
                              "observation_age_seconds": age_s},
                        raw=js, provider_symbol_returned=js.get("ticker"),
                        provider_timestamp=prov_ts, provider_timezone="UTC",
                        feed_class="EOD",
                        stated_delay="Basic plan: previous-session close only (EOD)",
                        notes=["/v2/aggs/ticker/{sym}/prev — last completed daily bar"]
                        + (["age>5d -> STALE"] if stale else []))

    def daily_history(self, atlas_symbol, days=400):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("daily_history", atlas_symbol, sym)
        end = datetime.now(timezone.utc).date()
        start = end.replace(year=end.year - 2)
        js, fail = self._get(
            f"{self.BASE}/v2/aggs/ticker/{sym}/range/1/day/{start}/{end}",
            "daily_history", atlas_symbol, sym,
            params=self._params(adjusted="true", sort="asc", limit="50000"))
        if fail:
            return fail
        rows = js.get("results") or []
        bars = [{"date": datetime.fromtimestamp(r["t"] / 1000, tz=timezone.utc).date().isoformat(),
                 "open": _f(r.get("o")), "high": _f(r.get("h")), "low": _f(r.get("l")),
                 "close": _f(r.get("c")), "volume": _f(r.get("v"))} for r in rows if r.get("t")]
        return MDResult(self.name, "daily_history", sym, atlas_symbol,
                        "AVAILABLE" if bars else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"bar_count": len(bars),
                              "first": bars[0]["date"] if bars else None,
                              "last": bars[-1]["date"] if bars else None,
                              "adjustment_status": "adjusted=true (split-adjusted OHLC); "
                                                   "no separate adjusted-close column",
                              "history_span_note": "Basic plan caps history at ~2 years"},
                        raw={"sample": bars[:3]}, feed_class="EOD",
                        notes=[] if bars else ["no bars in range"])

    def dividends(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("dividends", atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/v3/reference/dividends", "dividends", atlas_symbol, sym,
                             params=self._params(ticker=sym, limit="1000"))
        if fail:
            return fail
        rows = js.get("results") or []
        evs = [{"ex_date": d.get("ex_dividend_date"), "pay_date": d.get("pay_date"),
                "record_date": d.get("record_date"), "declared_date": d.get("declaration_date"),
                "amount": _f(d.get("cash_amount")), "frequency": d.get("frequency"),
                "type": d.get("dividend_type")} for d in rows]
        return MDResult(self.name, "dividends", sym, atlas_symbol,
                        "AVAILABLE" if evs else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"count": len(evs), "latest": evs[0] if evs else None,
                              "fields_present": sorted({k for e in evs for k, v in e.items() if v is not None})},
                        raw={"sample": evs[:4]},
                        notes=["/v3/reference/dividends — full declared/ex/record/pay dates"]
                        if evs else ["none on record"])

    def splits(self, atlas_symbol):
        sym = self.provider_symbol(atlas_symbol)
        if not self.enabled:
            return self.disabled_result("splits", atlas_symbol, sym)
        js, fail = self._get(f"{self.BASE}/v3/reference/splits", "splits", atlas_symbol, sym,
                             params=self._params(ticker=sym, limit="1000"))
        if fail:
            return fail
        rows = js.get("results") or []
        evs = [{"date": s.get("execution_date"), "split_from": s.get("split_from"),
                "split_to": s.get("split_to"),
                "ratio": (_f(s.get("split_from")) / _f(s.get("split_to"))
                          if _f(s.get("split_to")) else None)} for s in rows]
        return MDResult(self.name, "splits", sym, atlas_symbol,
                        "AVAILABLE" if evs else "UNAVAILABLE",
                        security_key=self._security_key(atlas_symbol),
                        data={"count": len(evs), "events": evs},
                        raw={"sample": evs[:4]},
                        notes=["/v3/reference/splits — explicit split_from/split_to factors"]
                        if evs else ["no splits on record"])


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def classify_feed_from_age(age_seconds: Optional[float], *, market_open: Optional[bool] = None) -> str:
    """Map the age of a price observation to a FEED_CLASSES value.

    Only meaningful while the market is open: a stale reading after the close is
    simply EOD, not 'delayed'. Thresholds are deliberately coarse — this is a
    benchmark classifier, not an SLA.
    """
    if age_seconds is None:
        return "UNKNOWN"
    if market_open is False:
        return "EOD"
    if age_seconds <= 120:
        return "REAL_TIME"
    if age_seconds <= 30 * 60:
        return "DELAYED"
    return "EOD"


ALL_PROVIDERS = [TwelveDataProvider, AlpacaProvider, TiingoProvider, MassiveProvider]


def build_providers() -> List[MarketDataProvider]:
    return [cls() for cls in ALL_PROVIDERS]
