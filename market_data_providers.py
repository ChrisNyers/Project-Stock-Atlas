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
    feed_class: Optional[str] = None          # REALTIME_SIP / REALTIME_IEX / DELAYED_15MIN / EOD / UNKNOWN
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
        "free_tier": "API key required (free, lifetime). 8 requests/minute, 800 requests/day.",
        "history": "time_series free; outputsize<=5000; adjusted close not on free plan.",
        "realtime": "US equities: no real-time trade feed on free plan; /quote returns latest EOD/delayed.",
        "corporate_actions": "/dividends and /splits available on free plan.",
        "demo_key": "public 'demo' key serves ONLY AAPL.",
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
        stale = None
        if ts:
            age_h = (datetime.now(timezone.utc) - datetime.fromtimestamp(int(ts), tz=timezone.utc)).total_seconds() / 3600
            stale = "STALE" if age_h > 96 else None
        return MDResult(
            self.name, "latest_price", sym, atlas_symbol, stale or "AVAILABLE",
            security_key=self._security_key(atlas_symbol),
            data={"price": _f(js.get("close")), "previous_close": _f(js.get("previous_close")),
                  "open": _f(js.get("open")), "day_high": _f(js.get("high")), "day_low": _f(js.get("low")),
                  "volume": _f(js.get("volume")), "is_market_open": js.get("is_market_open"),
                  "exchange": js.get("exchange"), "mic_code": js.get("mic_code")},
            raw=js, provider_symbol_returned=js.get("symbol"),
            provider_timestamp=prov_ts, provider_timezone=js.get("exchange_timezone", "America/New_York"),
            feed_class="EOD_OR_DELAYED", stated_delay="free plan: no real-time trade feed for US equities",
            notes=["'close' here is the latest session close, not a live trade"] + (["age>96h"] if stale else []),
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
        "free_tier": "Free brokerage/data account. 200 requests/minute.",
        "feed": "Free data = IEX feed only (single venue, ~2-3% of consolidated volume), not full SIP.",
        "history": "Historical bars: full history on IEX; SIP history limited to last ~15 min delay barrier on free.",
        "corporate_actions": "/v1/corporate-actions covers splits, dividends, mergers, spinoffs.",
        "identity": "share classes use dotted tickers (BRK.A / BRK.B).",
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
                        feed_class="REALTIME_IEX", stated_delay="IEX venue only; not consolidated SIP",
                        notes=["free feed=iex: real-time but single venue"])

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
                        raw={"sample": rows[:3]}, feed_class="EOD_IEX")

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
        "free_tier": "Free API token. 50 requests/hour, 1000 requests/day, 500 unique symbols/month.",
        "history": "EOD daily prices with adjClose, adjOpen/High/Low, divCash, splitFactor columns.",
        "realtime": "/iex endpoint = real-time IEX (single venue). EOD covers consolidated close.",
        "corporate_actions": "dividends (divCash) and splits (splitFactor) are embedded in the daily price rows.",
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
                        feed_class="REALTIME_IEX", stated_delay="IEX venue only")

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
# Massive  (named in Phase 4A.5 planning; not a verifiable market-data API)
# ---------------------------------------------------------------------------
class MassiveProvider(MarketDataProvider):
    name = "massive"
    eligibility = "NOT_ELIGIBLE"
    homepage = "(unresolved)"
    key_env = ()
    published_limits = {
        "status": "No verifiable free/public equities market-data API located under the name "
                  "'Massive'. The Sprint-1 stub pointed at api.massive.com (placeholder). "
                  "The domain in public use (joinmassive.com) is a bandwidth/proxy SDK, not "
                  "a market-data vendor.",
    }

    def _not_eligible(self, capability, atlas_symbol):
        return MDResult(self.name, capability, atlas_symbol, atlas_symbol, "NOT_ELIGIBLE",
                        notes=["no identifiable free market-data API for 'Massive'"])

    def resolve_symbol(self, s): return self._not_eligible("resolve", s)
    def latest_price(self, s): return self._not_eligible("latest_price", s)
    def daily_history(self, s, days=400): return self._not_eligible("daily_history", s)
    def dividends(self, s): return self._not_eligible("dividends", s)
    def splits(self, s): return self._not_eligible("splits", s)


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


ALL_PROVIDERS = [TwelveDataProvider, AlpacaProvider, TiingoProvider, MassiveProvider]


def build_providers() -> List[MarketDataProvider]:
    return [cls() for cls in ALL_PROVIDERS]
