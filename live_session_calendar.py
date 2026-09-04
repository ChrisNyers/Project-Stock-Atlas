"""Gate B3 / Pilot 2 venue readiness — authoritative latest-completed-session
truth.

Session truth is derived from an INDEPENDENT exchange calendar
(``exchange_calendars==4.13.2``), never from a market-data provider's own
market-state response.

    decision timestamp -> XNYS/XNAS calendar -> latest completed session
                       -> known_latest_session_date
                       -> existing Stock Atlas freshness validation

A provider may *report* ``is_market_open`` or an exchange schedule. That value
is captured as supporting evidence and may be cross-checked, but it never
overrides this calendar and never determines ``known_latest_session_date``.
Rationale: a provider that self-asserts freshness can assert a stale session is
current (Red Team C-02). An independent calendar cannot be talked into it.

Supported venues
-----------------
``XNYS``/``NYSE``; the two Nasdaq MICs present in the frozen Pilot 2 basket,
``XNGS`` (Nasdaq Global Select — MELI, JD, ADBE, GLNG) and ``XNMS`` (Nasdaq
Global Market — FISV); and ``ARCX`` (NYSE Arca), required because SPY — a
fixed Stage 7 alternative, not a basket name — primary-lists there. Each of
``XNGS``, ``XNMS`` and ``ARCX`` is bound by calling
``exchange_calendars.get_calendar(...)`` with **its own name**
(``"XNAS"`` for the two Nasdaq MICs, ``"ARCX"`` for NYSE Arca) rather than
reused from the ``XNYS`` lookup.

``exchange_calendars==4.13.2`` documents ``XNAS``, ``ARCX`` (and ``NASDAQ``,
``XASE``, ``BATS``, ``OOTC``) as aliases resolving to the same underlying
schedule object as ``XNYS`` — see
``exchange_calendars.calendar_utils._default_calendar_aliases``. This is not a
shortcut taken here: it reflects that NYSE, Nasdaq and NYSE Arca are all
regulated U.S. equity markets that observe SIFMA-coordinated market holidays
and identical 9:30 a.m.-4:00 p.m. ET regular sessions, so the trading-day/
session-hour data genuinely is the same. The binding is still deliberate and
explicit — each supported non-XNYS MIC requests its own calendar by name, is
recorded as bound to its own venue in its own attestation, and is never
silently satisfied by a caller that only asked for ``XNYS``.

Fail-closed behaviour
---------------------
Every failure raises :class:`SessionCalendarError`. Nothing here ever guesses,
falls back to "today", or silently substitutes a different exchange:

* unknown / unmapped exchange or MIC             -> raise
* decision timestamp outside calendar bounds     -> raise
* naive decision timestamp                       -> raise
* no completed session at/before decision time   -> raise

No generic "all U.S. exchanges" fallback exists. A MIC outside
:data:`SUPPORTED_MICS` fails closed regardless of how similar its calendar
might be to a supported one.

This module reads a calendar. It makes no capital decision, holds no
credentials, and performs no network I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

import exchange_calendars as xc
import pandas as pd

__all__ = [
    "SessionCalendarError",
    "SessionAttestation",
    "CALENDAR_PACKAGE_VERSION",
    "SUPPORTED_MICS",
    "calendar_for_mic",
    "latest_completed_session",
]

#: Pinned so the attestation records exactly which calendar produced session truth.
CALENDAR_PACKAGE_VERSION = "exchange_calendars==4.13.2"

#: MIC / exchange labels this build is authorized to resolve, mapped to their
#: calendar. Deliberately narrow: an unmapped venue fails closed rather than
#: borrowing another exchange's holiday schedule.
#:
#: XNGS and XNMS are the two Nasdaq-family MICs actually encountered while
#: resolving the frozen Pilot 2 basket (see PILOT2_NASDAQ_SESSION_BINDING_
#: EXTENSION in the Decision Log). Each is bound to "XNAS", requested by name,
#: not to "XNYS".
#:
#: ARCX (NYSE Arca) is added because SPY — a fixed Stage 7 alternative
#: required alongside every candidate, not a basket name — primary-lists
#: there (see PILOT2_STAGE8_BINDING_READINESS in the Decision Log). Bound to
#: "ARCX", requested by name, not to "XNYS".
#:
#: No other alias exchange_calendars recognises (NASDAQ, XASE, BATS, OOTC) is
#: added — extension is scoped to exactly the MICs Pilot 2's frozen basket and
#: required Stage 7 alternatives need, nothing broader.
SUPPORTED_MICS: dict[str, str] = {
    "XNYS": "XNYS",
    "NYSE": "XNYS",
    "XNGS": "XNAS",
    "XNMS": "XNAS",
    "ARCX": "ARCX",
}


class SessionCalendarError(Exception):
    """Raised when authoritative session truth cannot be established."""


@dataclass(frozen=True)
class SessionAttestation:
    """Independently derived session truth, with its provenance.

    ``session_date`` is what may be handed to Stock Atlas as
    ``known_latest_session_date``. ``provider_reported_market_open`` is carried
    only as evidence; it has no authority over ``session_date``.
    """

    session_date: date
    session_close_utc: datetime
    exchange: str
    calendar_name: str
    calendar_version: str
    decision_time_utc: datetime
    provider_reported_market_open: bool | None = None

    @property
    def provider_agrees(self) -> bool | None:
        """Cross-check only. ``None`` when the provider reported nothing.

        The provider claims the market is open; the calendar says the session
        has not yet closed. Disagreement is recorded, never resolved in the
        provider's favour.
        """
        if self.provider_reported_market_open is None:
            return None
        return self.provider_reported_market_open is False

    def to_dict(self) -> dict:
        return {
            "session_date": self.session_date.isoformat(),
            "session_close_utc": self.session_close_utc.isoformat(),
            "exchange": self.exchange,
            "calendar_name": self.calendar_name,
            "calendar_version": self.calendar_version,
            "decision_time_utc": self.decision_time_utc.isoformat(),
            "authority": "independent exchange calendar",
            "provider_reported_market_open": self.provider_reported_market_open,
            "provider_agrees_with_calendar": self.provider_agrees,
        }


def calendar_for_mic(mic: str):
    """Resolve a MIC/exchange label to its calendar, or fail closed."""
    if mic is None or not str(mic).strip():
        raise SessionCalendarError("Exchange/MIC is required to establish session truth")
    key = str(mic).strip().upper()
    if key not in SUPPORTED_MICS:
        raise SessionCalendarError(
            f"No authorized exchange calendar for MIC {key!r}; "
            f"supported: {', '.join(sorted(SUPPORTED_MICS))}"
        )
    return xc.get_calendar(SUPPORTED_MICS[key])


def latest_completed_session(
    decision_time: datetime,
    *,
    mic: str = "XNYS",
    provider_reported_market_open: bool | None = None,
) -> SessionAttestation:
    """Latest session whose close is at or before ``decision_time``.

    A session that has not yet closed is NOT completed, so a decision made
    before today's close attests to the *previous* session. Weekends and
    holidays fall out of the calendar itself rather than from day arithmetic.
    """
    if decision_time.tzinfo is None:
        raise SessionCalendarError(
            "decision_time must be timezone-aware; a naive timestamp cannot be "
            "bound to an exchange session"
        )
    dt = decision_time.astimezone(timezone.utc)
    cal = calendar_for_mic(mic)

    ts = pd.Timestamp(dt).tz_convert("UTC")
    bound_lo = cal.first_session.tz_localize("UTC") if cal.first_session.tz is None else cal.first_session
    bound_hi = cal.last_session.tz_localize("UTC") if cal.last_session.tz is None else cal.last_session
    if ts < bound_lo or ts > bound_hi + pd.Timedelta(days=1):
        raise SessionCalendarError(
            f"Decision time {dt.isoformat()} is outside calendar bounds "
            f"{bound_lo.date()}..{bound_hi.date()}; cannot attest session truth"
        )

    try:
        session = cal.date_to_session(ts.normalize().tz_localize(None), direction="previous")
    except Exception as exc:  # narrow calendars, out-of-range dates
        raise SessionCalendarError(f"Calendar could not resolve a session at/before {dt.date()}: {exc}") from exc

    # Walk back until we find a session that has actually closed.
    for _ in range(10):
        close = cal.session_close(session)
        close_utc = close.tz_convert("UTC") if close.tz is not None else close.tz_localize("UTC")
        if close_utc <= ts:
            return SessionAttestation(
                session_date=session.date(),
                session_close_utc=close_utc.to_pydatetime(),
                exchange=str(mic).strip().upper(),
                calendar_name=cal.name,
                calendar_version=CALENDAR_PACKAGE_VERSION,
                decision_time_utc=dt,
                provider_reported_market_open=provider_reported_market_open,
            )
        try:
            session = cal.previous_session(session)
        except Exception as exc:
            raise SessionCalendarError(f"No completed session at/before {dt.isoformat()}: {exc}") from exc

    raise SessionCalendarError(
        f"Could not establish a completed session at/before {dt.isoformat()} within 10 sessions"
    )
