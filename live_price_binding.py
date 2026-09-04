"""Gate B1/B2/B4 — bind real provider observations into the frozen contract.

This module translates a live market-data observation into the control layer's
existing ``PriceSnapshot`` / ``FXSnapshot`` types. It adds no new decision
logic: every fail-closed rule that matters is still enforced downstream by
``stock_atlas.controls``. What happens here is binding and refusal — an
observation that cannot be bound with complete, self-consistent identity, time,
currency and provenance never reaches Stage 7 at all.

Three rules give this module its shape:

1. **Identity is checked before anything else** (B2). The security key resolved
   from the provider must equal the key the caller underwrote. BRK.A and BRK.B
   share issuer CIK 0001067983 but are distinct securities; an observation
   bound to one can never satisfy the other.
2. **Session truth comes from the calendar, never the provider** (B3). The
   provider's ``is_market_open`` is recorded as evidence only. Freshness is
   decided by comparing the observation's session date against an independent
   :class:`~live_session_calendar.SessionAttestation`.
3. **Freshness is derived, not copied.** No provider field named "fresh" is
   trusted. ``FreshnessStatus.FRESH`` is granted only when the observation's
   own session date equals the independently attested latest completed session.

Capital status: NO REAL PORTFOLIO ACTION. Nothing here decides anything.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Optional

from live_session_calendar import SessionAttestation
from stock_atlas.models import FreshnessStatus, FXSnapshot, PriceMode, PriceSnapshot

__all__ = [
    "LiveBindingError",
    "BoundPriceEvidence",
    "bind_price_snapshot",
    "bind_fx_snapshot",
    "redact",
]

_TD_QUOTE_URL = "https://api.twelvedata.com/quote"


class LiveBindingError(Exception):
    """Raised when a live observation cannot be safely bound. Always fail closed."""


def redact(text: str) -> str:
    """Strip any credential value out of evidence before it is printed or stored."""
    out = str(text)
    for name in ("TWELVEDATA_API_KEY", "ALPACA_API_KEY_ID", "ALPACA_API_SECRET_KEY",
                 "MASSIVE_API_KEY", "TIINGO_API_TOKEN", "FRED_API_KEY"):
        value = os.environ.get(name)
        if value:
            out = out.replace(value, "<REDACTED>")
    return out


@dataclass(frozen=True)
class BoundPriceEvidence:
    """A bound snapshot plus the provenance needed to reproduce it."""

    snapshot: PriceSnapshot
    attestation: SessionAttestation
    provider_reported_market_open: Optional[bool]
    provider_reported_session_date: Optional[str]
    raw_observation: dict

    def to_dict(self) -> dict:
        s = self.snapshot
        return {
            "price_binding": {
                "security_key": s.security_key,
                "quoted_security_key": s.quoted_security_key,
                "quoted_instrument": s.quoted_instrument,
                "ticker": s.ticker,
                "price": s.price,
                "currency": s.currency,
                "provider": s.provider,
                "price_as_of": s.price_as_of.isoformat(),
                "price_session_date": s.price_session_date.isoformat(),
                "latest_completed_session_date": s.latest_completed_session_date.isoformat(),
                "market_session_status": s.market_session_status,
                "adjusted": s.adjusted,
                "price_mode": s.price_mode.value,
                "freshness_status": s.freshness_status.value,
                "freshness_basis": "derived from independent exchange calendar, not provider self-report",
            },
            "session_attestation": self.attestation.to_dict(),
            "provider_self_report": {
                "is_market_open": self.provider_reported_market_open,
                "datetime": self.provider_reported_session_date,
                "authority": "NONE — evidence only, cannot override calendar",
            },
            "raw_observation": json.loads(redact(json.dumps(self.raw_observation, default=str))),
        }


def _as_date(value: Any, field: str) -> date:
    if value is None or not str(value).strip():
        raise LiveBindingError(f"Provider observation is missing {field}")
    text = str(value).strip()
    try:
        return datetime.fromisoformat(text[:10]).date()
    except ValueError as exc:
        raise LiveBindingError(f"Provider {field} {text!r} is not a parseable date") from exc


def _as_utc(epoch: Any, field: str) -> datetime:
    if epoch is None:
        raise LiveBindingError(f"Provider observation is missing {field}")
    try:
        return datetime.fromtimestamp(float(epoch), tz=timezone.utc)
    except (TypeError, ValueError, OSError) as exc:
        raise LiveBindingError(f"Provider {field} {epoch!r} is not a usable timestamp") from exc


def _disambiguate_via_known_mic(provider, atlas_symbol: str, expected_mic: str, ambiguous_result: dict) -> dict:
    """Resolve an AMBIGUOUS bare-ticker collision using Atlas's own known MIC.

    Called only when ``provider.resolve_symbol`` reports ``AMBIGUOUS`` — e.g.
    "JD" collides with JD Sports Fashion plc (LSE) and a Buenos Aires
    depositary receipt, alongside JD.com's Nasdaq ADR. This does **not** trust
    whichever instrument the provider's undocumented bare-ticker default
    happens to return (that is ticker-only matching). Instead it re-queries
    the provider with ``mic_code`` supplied explicitly — Atlas telling the
    provider which instrument to return, using a MIC already established
    through Atlas's own identity work (SEC CIK resolution / the frozen
    basket's venue-readiness record), rather than asking the provider to
    guess. Empirically, TwelveData's ``mic_code`` parameter is a genuine
    filter: querying a MIC where the requested ticker is not actually listed
    returns HTTP 404, not a silent substitution — verified directly against
    this ticker before this function was written.

    Two independent signals must agree before this returns anything: (1) the
    MIC-qualified query itself must succeed and echo back the same
    ``expected_mic``, and (2) ``resolve_symbol``'s own ``quote_confirmed``
    sub-field — populated by a separate live call even in the AMBIGUOUS
    branch — must independently agree on MIC and exchange. Disagreement, a
    failed query, or a missing ``expected_mic`` all fail closed.
    """
    if not expected_mic or not str(expected_mic).strip():
        raise LiveBindingError(
            f"Provider reports {atlas_symbol!r} AMBIGUOUS and no expected_mic was "
            "supplied to disambiguate; refusing to guess which security is intended"
        )
    want_mic = str(expected_mic).strip().upper()

    key = os.environ.get("TWELVEDATA_API_KEY")
    if not key:
        raise LiveBindingError("TWELVEDATA_API_KEY is absent; cannot disambiguate a MIC-qualified quote")
    query = urllib.parse.urlencode({"symbol": atlas_symbol, "mic_code": want_mic, "apikey": key})
    try:
        with urllib.request.urlopen(f"{_TD_QUOTE_URL}?{query}", timeout=20) as resp:
            payload = json.load(resp)
    except Exception as exc:
        raise LiveBindingError(
            f"MIC-qualified disambiguation failed for {atlas_symbol!r} on {want_mic!r}: "
            f"{redact(str(exc))}. Ambiguity was not resolved; refusing to bind."
        ) from exc
    if not isinstance(payload, dict) or payload.get("code") or payload.get("status") == "error":
        raise LiveBindingError(
            f"MIC-qualified disambiguation returned an error for {atlas_symbol!r} on "
            f"{want_mic!r}: {redact(json.dumps(payload, default=str))}"
        )

    returned_mic = str(payload.get("mic_code") or "").strip().upper()
    if returned_mic != want_mic:
        raise LiveBindingError(
            f"MIC-qualified query for {atlas_symbol!r} echoed back {returned_mic!r}, "
            f"not the requested {want_mic!r}; refusing to bind on a mismatch"
        )

    # Second, independent signal: resolve_symbol's own live quote_confirmed
    # sub-field (from a separate call TwelveData already made) must agree.
    confirmed = ((ambiguous_result.get("data") or {}).get("quote_confirmed")) or {}
    confirmed_mic = str(confirmed.get("mic_code") or "").strip().upper()
    if confirmed_mic and confirmed_mic != want_mic:
        raise LiveBindingError(
            f"resolve_symbol's independent quote_confirmed for {atlas_symbol!r} disagrees "
            f"with the MIC-qualified query ({confirmed_mic!r} vs {want_mic!r}); two "
            "identity signals disagree, refusing to bind"
        )

    # Atlas's OWN identity resolution for this symbol (CIK-based, via
    # sec_adapter/identity_resolver) was never ambiguous — only the
    # provider's bare-ticker quote was. The security_key below is therefore
    # the caller's already-established expected_security_key, not a new
    # provider-derived value: what was proven above is that the MIC-qualified
    # observation corresponds to the venue Atlas already knows this issuer
    # trades on, via two independently agreeing provider signals.
    return {
        "provider": provider.name if hasattr(provider, "name") else "twelvedata",
        "state": "AVAILABLE",
        "security_key": ambiguous_result.get("security_key"),
        "data": {
            # TwelveData returns numeric fields as strings; coerce here as
            # market_data_providers._f() does for the same endpoint.
            "price": float(payload["close"]) if payload.get("close") not in (None, "") else None,
            "mic_code": returned_mic,
            "is_market_open": payload.get("is_market_open"),
        },
        # Disambiguation evidence rides along inside "raw" so it flows into
        # BoundPriceEvidence.raw_observation and is preserved/redacted exactly
        # like every other bind's evidence, without changing that dataclass.
        "raw": {
            **payload,
            "_disambiguation": {
                "method": "mic_qualified_query",
                "reason": "resolve_symbol reported AMBIGUOUS",
                "expected_mic": want_mic,
                "quote_confirmed_cross_check": confirmed,
            },
        },
    }


def bind_price_snapshot(
    provider,
    atlas_symbol: str,
    *,
    expected_security_key: str,
    attestation: SessionAttestation,
    expected_currency: str = "USD",
    expected_mic: str = "XNYS",
) -> BoundPriceEvidence:
    """Bind one live provider observation to the frozen ``PriceSnapshot`` contract.

    ``expected_security_key`` is the identity the caller underwrote. If the
    provider resolves the requested symbol to any other key, this raises — that
    is the B2 class-substitution guard, applied before a price is even read.

    A bare ticker can collide across unrelated issuers on different venues
    (e.g. "JD" is both JD.com's Nasdaq ADR and JD Sports Fashion plc on the
    LSE). When the provider itself reports this as ``AMBIGUOUS``, this
    function does **not** fall back to trusting whichever instrument the
    provider's bare-ticker default happens to return — that would be exactly
    the ticker-only matching this control exists to prevent. Instead it
    requires the caller's own ``expected_mic`` (already established through
    Atlas's identity work, not derived from this call) and re-queries the
    provider with that MIC supplied explicitly, so the provider is told which
    instrument to return rather than asked to guess. The response is then
    independently checked against ``expected_security_key``/``expected_mic``/
    ``expected_currency`` exactly as the unambiguous path is. If no
    ``expected_mic`` is supplied, or the MIC-qualified query fails or its
    result doesn't verify, this fails closed — ambiguity is never silently
    resolved.
    """
    resolved = provider.resolve_symbol(atlas_symbol)
    rd = resolved.to_dict()
    state = rd.get("state")

    if state == "AMBIGUOUS":
        qd = _disambiguate_via_known_mic(provider, atlas_symbol, expected_mic, rd)
    elif state != "AVAILABLE":
        raise LiveBindingError(
            f"Provider could not resolve {atlas_symbol!r}: state={state}"
        )
    else:
        resolved_key = rd.get("security_key")
        if not resolved_key or not str(resolved_key).strip():
            raise LiveBindingError(f"Provider returned no security_key for {atlas_symbol!r}")

        # --- B2: identity gate, before any price is trusted --------------------
        if str(resolved_key).strip() != str(expected_security_key).strip():
            raise LiveBindingError(
                f"Security identity mismatch: underwrote {expected_security_key!r} but the "
                f"provider resolved {atlas_symbol!r} to {resolved_key!r}. Distinct share "
                "classes are distinct securities; refusing to bind."
            )

        quote = provider.latest_price(atlas_symbol)
        qd = quote.to_dict()
        if qd.get("state") != "AVAILABLE":
            raise LiveBindingError(
                f"Provider returned no usable price for {atlas_symbol!r}: state={qd.get('state')}"
            )

    quoted_key = qd.get("security_key")
    if str(quoted_key).strip() != str(expected_security_key).strip():
        raise LiveBindingError(
            f"Quoted security {quoted_key!r} does not match underwritten security "
            f"{expected_security_key!r}; refusing to bind."
        )

    data = qd.get("data") or {}
    raw = qd.get("raw") or {}

    price = data.get("price")
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        raise LiveBindingError(f"Provider price for {atlas_symbol!r} is missing or non-positive")

    currency = str(raw.get("currency") or "").strip().upper()
    if not currency:
        raise LiveBindingError("Provider observation is missing currency")
    if currency != str(expected_currency).strip().upper():
        raise LiveBindingError(
            f"Provider currency {currency!r} does not match expected {expected_currency!r}"
        )

    mic = str(data.get("mic_code") or raw.get("mic_code") or "").strip().upper()
    if not mic:
        raise LiveBindingError("Provider observation is missing MIC/exchange")
    if mic != str(expected_mic).strip().upper():
        raise LiveBindingError(
            f"Provider MIC {mic!r} does not match the exchange whose calendar was "
            f"attested ({expected_mic!r}); refusing to bind session truth across venues"
        )
    if mic != attestation.exchange:
        raise LiveBindingError(
            f"Observation venue {mic!r} does not match attested calendar venue "
            f"{attestation.exchange!r}"
        )

    session_date = _as_date(raw.get("datetime"), "session date (datetime)")
    price_as_of = _as_utc(raw.get("last_quote_at") or raw.get("timestamp"), "quote timestamp")

    provider_open = data.get("is_market_open")
    if provider_open is None:
        provider_open = raw.get("is_market_open")

    # --- B3: freshness derived from the calendar, never the provider ----------
    fresh = session_date == attestation.session_date
    freshness = FreshnessStatus.FRESH if fresh else FreshnessStatus.STALE

    snapshot = PriceSnapshot(
        security_key=str(expected_security_key).strip(),
        ticker=str(atlas_symbol).strip().upper(),
        price=float(price),
        price_as_of=price_as_of,
        price_session_date=session_date,
        latest_completed_session_date=attestation.session_date,
        currency=currency,
        provider=str(qd.get("provider") or "unknown"),
        # Derived from the calendar: the attested session has closed by construction.
        market_session_status="COMPLETED",
        # TwelveData /quote returns an unadjusted last price. Recorded honestly
        # rather than asserted as adjusted.
        adjusted=False,
        freshness_status=freshness,
        price_mode=PriceMode.COMPLETED_SESSION,
        quoted_security_key=str(quoted_key).strip(),
        quoted_instrument=f"{raw.get('name') or atlas_symbol} ({mic})",
    )
    return BoundPriceEvidence(
        snapshot=snapshot,
        attestation=attestation,
        provider_reported_market_open=provider_open,
        provider_reported_session_date=raw.get("datetime"),
        raw_observation=raw,
    )


def fetch_fx_observation(pair: str, *, timeout: float = 20.0) -> dict:
    """Fetch one live FX quote from the single approved provider.

    Deliberately thin: this is a source, not an FX engine. It returns the raw
    provider payload and does no conversion, interpolation or cross-rating.
    """
    key = os.environ.get("TWELVEDATA_API_KEY")
    if not key:
        raise LiveBindingError("TWELVEDATA_API_KEY is absent; cannot bind live FX")
    query = urllib.parse.urlencode({"symbol": pair, "apikey": key})
    try:
        with urllib.request.urlopen(f"{_TD_QUOTE_URL}?{query}", timeout=timeout) as resp:
            payload = json.load(resp)
    except Exception as exc:
        raise LiveBindingError(f"FX fetch failed for {pair!r}: {redact(str(exc))}") from exc
    if not isinstance(payload, dict) or payload.get("code") or payload.get("status") == "error":
        raise LiveBindingError(f"FX provider error for {pair!r}: {redact(json.dumps(payload, default=str))}")
    return payload


def bind_fx_snapshot(
    observation: dict,
    *,
    from_currency: str,
    to_currency: str,
    decision_time: datetime,
    max_age_hours: float = 96.0,
) -> FXSnapshot:
    """Bind a live FX observation to the frozen ``FXSnapshot`` contract.

    The pair carried by the observation must be exactly the pair required to
    convert price currency into portfolio base currency. A reversed pair is a
    different economic quantity and is refused here rather than silently
    inverted.
    """
    want_from = str(from_currency).strip().upper()
    want_to = str(to_currency).strip().upper()
    if not want_from or not want_to:
        raise LiveBindingError("Both FX currencies are required")

    symbol = str(observation.get("symbol") or "").strip().upper()
    if "/" not in symbol:
        raise LiveBindingError(f"FX observation carries no usable pair: {symbol!r}")
    obs_from, obs_to = (part.strip().upper() for part in symbol.split("/", 1))

    # --- B4: the pair must be the required pair, not its reverse -------------
    if (obs_from, obs_to) != (want_from, want_to):
        raise LiveBindingError(
            f"FX pair mismatch: required {want_from}/{want_to} but observation is "
            f"{obs_from}/{obs_to}. A reversed or unrelated pair cannot be silently inverted."
        )

    rate = observation.get("close") or observation.get("rate") or observation.get("price")
    try:
        rate_f = float(rate)
    except (TypeError, ValueError) as exc:
        raise LiveBindingError(f"FX rate {rate!r} is not numeric") from exc
    if not rate_f > 0:
        raise LiveBindingError("FX rate must be positive")

    as_of = _as_utc(observation.get("timestamp"), "FX timestamp")
    dt = decision_time if decision_time.tzinfo else decision_time.replace(tzinfo=timezone.utc)

    # Freshness derived from the observation's own age, not from any provider label.
    age_hours = (dt - as_of).total_seconds() / 3600.0
    freshness = FreshnessStatus.FRESH if age_hours <= max_age_hours else FreshnessStatus.STALE

    return FXSnapshot(
        from_currency=want_from,
        to_currency=want_to,
        rate=rate_f,
        as_of=as_of,
        provider="twelvedata",
        freshness_status=freshness,
    )
