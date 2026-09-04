"""Gate B — live data binding proofs (B1–B5).

These tests bind REAL upstream observations into the frozen, Red-Team-accepted
architecture and prove the system still fails closed when identity, session,
currency or FX inputs are wrong, stale or missing.

Tests that reach the network are marked ``@pytest.mark.live`` and skip when
``TWELVEDATA_API_KEY`` is absent. A skip is a BLOCKED result, never a PASS.
Offline tests carry no marker and always run.

Naming: every test is prefixed with the requirement it proves
(``test_b1_``, ``test_b2_``, ...) so the closure matrix is reproducible by
selection, e.g. ``pytest -k b3``.

Nothing here changes the control layer, weakens a freshness rule, or produces a
capital action. Capital status: NO REAL PORTFOLIO ACTION.
"""

from __future__ import annotations

import os
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import market_data_providers as mdp
from capital_decision_facade import CapitalDecisionFacade, ControlFailure
from live_price_binding import (
    LiveBindingError,
    bind_fx_snapshot,
    bind_price_snapshot,
    fetch_fx_observation,
)
from live_session_calendar import (
    SessionAttestation,
    SessionCalendarError,
    latest_completed_session,
)
from stock_atlas.controls import validate_fx_binding, validate_price_snapshot
from stock_atlas.models import (
    AlternativeType,
    BlockFlag,
    CandidateUnderwriting,
    CapacityStatus,
    ComparisonAlternative,
    ETFOverlap,
    FreshnessStatus,
    FundingMode,
    FundingPocket,
    FXSnapshot,
    Holding,
    MarketReferenceSnapshot,
    OverlapStatus,
    PortfolioAction,
    PortfolioSnapshot,
    PositionClassification,
    PriceMode,
    ReturnBand,
    RevisitTriggers,
    SecurityDecision,
    TypedUncertainty,
    UnderwritingGateStatus,
    VerificationStatus,
)
from stock_atlas.portfolio import build_position_proposal

# Berkshire Hathaway: one issuer (CIK 0001067983), two economically distinct
# securities. The canonical B2 adversarial pair.
BRK_B_KEY = "SEC-CIK:0001067983:BRK-B"
BRK_A_KEY = "SEC-CIK:0001067983:BRK-A"

live = pytest.mark.live
requires_key = pytest.mark.skipif(
    not os.environ.get("TWELVEDATA_API_KEY"),
    reason="TWELVEDATA_API_KEY absent — Gate B live binding is BLOCKED, not passing",
)


# TwelveData's free tier allows 8 credits/minute and each binding spends two
# (resolve + quote). Without pacing the adapter fails closed with RATE_LIMITED,
# which is correct behaviour but makes the evidence non-reproducible. Throttle
# rather than weaken anything.
_MIN_CALL_INTERVAL_S = 8.5
_RATE_LIMIT_BACKOFF_S = 62.0
_RATE_LIMIT_RETRIES = 2
_last_call: list[float] = [0.0]


def _throttle() -> None:
    import time

    wait = _MIN_CALL_INTERVAL_S - (time.monotonic() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.monotonic()


def _with_rate_limit_retry(call, *args):
    """Retry only on provider rate limiting, so back-to-back runs reproduce.

    This paces the HARNESS. It never retries a control failure, never relaxes a
    freshness rule, and never converts a refusal into a pass — a RATE_LIMITED
    adapter result is a missing observation, not a failed control.
    """
    import time

    for attempt in range(_RATE_LIMIT_RETRIES + 1):
        _throttle()
        result = call(*args)
        state = getattr(result, "state", None)
        if str(state).upper() != "RATE_LIMITED" or attempt == _RATE_LIMIT_RETRIES:
            return result
        time.sleep(_RATE_LIMIT_BACKOFF_S)
    return result


class _ThrottledProvider:
    """Pass-through wrapper that paces live calls. Changes no adapter logic."""

    def __init__(self, inner):
        self._inner = inner

    def resolve_symbol(self, symbol):
        return _with_rate_limit_retry(self._inner.resolve_symbol, symbol)

    def latest_price(self, symbol):
        return _with_rate_limit_retry(self._inner.latest_price, symbol)

    def __getattr__(self, name):
        return getattr(self._inner, name)


@pytest.fixture(scope="module")
def provider():
    return _ThrottledProvider(mdp.TwelveDataProvider())


@pytest.fixture(scope="module")
def now() -> datetime:
    return datetime.now(timezone.utc)


@pytest.fixture(scope="module")
def attestation(now) -> SessionAttestation:
    """Independent session truth. Never sourced from the provider."""
    return latest_completed_session(now, mic="XNYS")


@pytest.fixture(scope="module")
def brk_b_evidence(provider, attestation):
    return bind_price_snapshot(
        provider,
        "BRK.B",
        expected_security_key=BRK_B_KEY,
        attestation=attestation,
    )


@pytest.fixture(scope="module")
def brk_a_evidence(provider, attestation):
    return bind_price_snapshot(
        provider,
        "BRK.A",
        expected_security_key=BRK_A_KEY,
        attestation=attestation,
    )


def _ledger_is_empty(facade) -> bool:
    """The append-only ledger holds no rows (file absent or zero entries)."""
    path = Path(facade.store.path) if hasattr(facade.store, "path") else None
    if path is None or not path.exists():
        return True
    return not [line for line in path.read_text().splitlines() if line.strip()]


# ===========================================================================
# B1 — real-provider price binding
# ===========================================================================


@live
@requires_key
def test_b1_live_observation_binds_with_complete_required_fields(brk_b_evidence):
    """Every decision-facing field B1 enumerates is present and non-empty."""
    p = brk_b_evidence.snapshot
    assert p.security_key == BRK_B_KEY
    assert p.quoted_security_key == BRK_B_KEY
    assert p.ticker == "BRK.B"
    assert p.price > 0
    assert p.currency == "USD"
    assert p.provider == "twelvedata"
    assert p.price_as_of.tzinfo is not None
    assert isinstance(p.price_session_date, date)
    assert isinstance(p.latest_completed_session_date, date)
    assert p.market_session_status == "COMPLETED"
    assert p.adjusted is False  # recorded honestly, not asserted as adjusted
    assert p.price_mode is PriceMode.COMPLETED_SESSION

    # Freshness depends on market state at run time, and BOTH outcomes are
    # correct behaviour:
    #   * outside market hours the quote's session IS the latest completed
    #     session -> FRESH;
    #   * during an open session the provider stamps an in-progress session
    #     date, which is NOT a completed session -> STALE, refused.
    # Asserting FRESH unconditionally would demand that an incomplete session
    # be accepted as completed — exactly what B3 forbids.
    if p.price_session_date == p.latest_completed_session_date:
        assert p.freshness_status is FreshnessStatus.FRESH
    else:
        assert p.price_session_date > p.latest_completed_session_date
        assert p.freshness_status is FreshnessStatus.STALE


@live
@requires_key
def test_b1_bound_live_snapshot_passes_frozen_price_validation(brk_b_evidence, now, attestation):
    """The live snapshot meets the unmodified control-layer validator.

    Mid-session the same validator must REFUSE the observation, because an
    in-progress session is not a completed-session close. Both branches assert
    the control is right; neither weakens it.
    """
    uw = _underwriting_from(brk_b_evidence.snapshot)
    snapshot = brk_b_evidence.snapshot
    if snapshot.price_session_date == snapshot.latest_completed_session_date:
        validate_price_snapshot(
            uw, now, known_latest_session_date=attestation.session_date
        )
    else:
        with pytest.raises(ControlFailure, match="STALE"):
            validate_price_snapshot(
                uw, now, known_latest_session_date=attestation.session_date
            )


@live
@requires_key
def test_b1_freshness_is_derived_not_copied_from_provider(brk_b_evidence):
    """FRESH is granted by calendar agreement, not by any provider label."""
    ev = brk_b_evidence.to_dict()
    assert ev["price_binding"]["freshness_basis"].startswith("derived from independent")
    assert ev["provider_self_report"]["authority"].startswith("NONE")


@live
@requires_key
def test_b1_missing_currency_blocks(provider, attestation, monkeypatch):
    """An observation stripped of currency cannot advance."""
    real = provider.latest_price

    def stripped(symbol):
        r = real(symbol)
        r.raw = dict(r.raw or {})
        r.raw.pop("currency", None)
        return r

    monkeypatch.setattr(provider, "latest_price", stripped)
    with pytest.raises(LiveBindingError, match="missing currency"):
        bind_price_snapshot(
            provider, "BRK.B", expected_security_key=BRK_B_KEY, attestation=attestation
        )


@live
@requires_key
def test_b1_wrong_currency_blocks(provider, attestation):
    """A USD observation cannot be bound as though it were EUR."""
    with pytest.raises(LiveBindingError, match="does not match expected"):
        bind_price_snapshot(
            provider,
            "BRK.B",
            expected_security_key=BRK_B_KEY,
            attestation=attestation,
            expected_currency="EUR",
        )


@live
@requires_key
def test_b1_venue_mismatch_blocks(provider, attestation):
    """A quote from a venue other than the attested one cannot borrow its calendar."""
    with pytest.raises(LiveBindingError, match="MIC"):
        bind_price_snapshot(
            provider,
            "BRK.B",
            expected_security_key=BRK_B_KEY,
            attestation=attestation,
            expected_mic="XNAS",
        )


# ===========================================================================
# B2 — security / class identity binding
# ===========================================================================


@live
@requires_key
def test_b2_brk_a_and_brk_b_resolve_to_distinct_security_keys(provider):
    """Same issuer CIK, different securities. Identity may not collapse."""
    a = provider.resolve_symbol("BRK.A").to_dict()
    b = provider.resolve_symbol("BRK.B").to_dict()
    assert a["security_key"] == BRK_A_KEY
    assert b["security_key"] == BRK_B_KEY
    assert a["security_key"] != b["security_key"]
    # Same issuer, so the issuer segment alone is NOT an identity.
    assert a["security_key"].rsplit(":", 1)[0] == b["security_key"].rsplit(":", 1)[0]


@live
@requires_key
def test_b2_brk_a_observation_cannot_satisfy_brk_b_identity(provider, attestation):
    """The mandatory adversarial case: wrong-class observation must fail closed."""
    with pytest.raises(LiveBindingError, match="identity mismatch"):
        bind_price_snapshot(
            provider, "BRK.A", expected_security_key=BRK_B_KEY, attestation=attestation
        )


@live
@requires_key
def test_b2_brk_b_observation_cannot_satisfy_brk_a_identity(provider, attestation):
    """Symmetric: the substitution is blocked in both directions."""
    with pytest.raises(LiveBindingError, match="identity mismatch"):
        bind_price_snapshot(
            provider, "BRK.B", expected_security_key=BRK_A_KEY, attestation=attestation
        )


@live
@requires_key
def test_b2_correctly_bound_class_passes(brk_a_evidence):
    """The normal correctly bound class still binds — this is not a blanket refusal."""
    assert brk_a_evidence.snapshot.security_key == BRK_A_KEY
    assert brk_a_evidence.snapshot.price > 0


@live
@requires_key
def test_b2_class_prices_are_economically_distinct(brk_a_evidence, brk_b_evidence):
    """Evidence that collapsing the classes would be a material economic error."""
    assert brk_a_evidence.snapshot.price > brk_b_evidence.snapshot.price * 100


@live
@requires_key
def test_b2_class_substitution_blocked_at_stage7_even_if_binding_bypassed(
    brk_b_evidence, now, attestation
):
    """Defense in depth: hand-swapping the key past the binder still fails."""
    swapped = replace(brk_b_evidence.snapshot, security_key=BRK_A_KEY, ticker="BRK.A")
    uw = _underwriting_from(swapped)
    with pytest.raises(ControlFailure, match="Quoted security"):
        validate_price_snapshot(uw, now, known_latest_session_date=attestation.session_date)


# ===========================================================================
# B3 — authoritative latest-session / calendar binding
# ===========================================================================


def test_b3_normal_latest_completed_session_resolves():
    """After the close, the attested session is that day."""
    att = latest_completed_session(
        datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic="XNYS"
    )
    assert att.session_date == date(2026, 9, 2)
    assert att.calendar_version == "exchange_calendars==4.13.2"


def test_b3_incomplete_session_is_not_treated_as_completed():
    """Before the close, the attested session is the PREVIOUS one."""
    att = latest_completed_session(
        datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc), mic="XNYS"
    )
    assert att.session_date == date(2026, 9, 1)


def test_b3_weekend_resolves_to_prior_friday():
    for probe in (
        datetime(2026, 8, 29, 12, 0, tzinfo=timezone.utc),  # Saturday
        datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc),  # Sunday
    ):
        assert latest_completed_session(probe, mic="XNYS").session_date == date(2026, 8, 28)


def test_b3_market_holiday_is_recognised():
    """Labor Day 2026-09-07 is not a session; truth falls back to Friday."""
    att = latest_completed_session(
        datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc), mic="XNYS"
    )
    assert att.session_date == date(2026, 9, 4)


def test_b3_stale_but_self_consistent_session_is_blocked():
    """C-02, live form: a three-week-old session that labels itself FRESH must block."""
    stale_session = date(2026, 8, 12)
    snap = _price_snapshot(
        session=stale_session,
        latest_completed=stale_session,  # internally consistent
        freshness=FreshnessStatus.FRESH,  # and self-asserted fresh
        as_of=datetime(2026, 8, 12, 20, 0, tzinfo=timezone.utc),
    )
    uw = _underwriting_from(snap)
    attested = latest_completed_session(
        datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic="XNYS"
    ).session_date
    with pytest.raises(ControlFailure, match="attested latest trading session"):
        validate_price_snapshot(
            uw,
            datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc),
            known_latest_session_date=attested,
        )


def test_b3_provider_market_state_cannot_override_calendar():
    """Deliberately contradict the provider: the calendar still governs."""
    att = latest_completed_session(
        datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc),
        mic="XNYS",
        provider_reported_market_open=True,  # provider insists the market is open
    )
    assert att.session_date == date(2026, 9, 2)  # unchanged by the provider's claim
    assert att.provider_agrees is False  # disagreement is recorded, not resolved
    assert att.to_dict()["authority"] == "independent exchange calendar"


def test_b3_unresolvable_exchange_fails_closed():
    with pytest.raises(SessionCalendarError, match="No authorized exchange calendar"):
        latest_completed_session(
            datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic="XNAS"
        )
    with pytest.raises(SessionCalendarError, match="required"):
        latest_completed_session(datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic="")


def test_b3_naive_decision_time_fails_closed():
    with pytest.raises(SessionCalendarError, match="timezone-aware"):
        latest_completed_session(datetime(2026, 9, 2, 21, 0), mic="XNYS")


def test_b3_out_of_bounds_decision_time_fails_closed():
    with pytest.raises(SessionCalendarError, match="outside calendar bounds"):
        latest_completed_session(datetime(1995, 1, 3, 21, 0, tzinfo=timezone.utc), mic="XNYS")


# ---------------------------------------------------------------------------
# Pilot 2 venue readiness — narrow Nasdaq extension (XNGS/XNMS only)
#
# The frozen Pilot 2 basket resolves five names to two Nasdaq-family MICs:
# XNGS (MELI, JD, ADBE, GLNG) and XNMS (FISV). See
# PILOT2_NASDAQ_SESSION_BINDING_EXTENSION in the Decision Log.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mic", ["XNGS", "XNMS"])
def test_b3_nasdaq_normal_completed_session_resolves(mic):
    """A completed Nasdaq session binds normally, for both basket MICs."""
    att = latest_completed_session(
        datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic=mic
    )
    assert att.session_date == date(2026, 9, 2)
    assert att.exchange == mic  # the requested MIC is preserved, not overwritten
    assert att.calendar_version == "exchange_calendars==4.13.2"


def test_b3_nasdaq_intraday_session_is_not_completed():
    """A quote stamped with the still-open Nasdaq session is not accepted."""
    att = latest_completed_session(
        datetime(2026, 9, 4, 15, 0, tzinfo=timezone.utc), mic="XNGS"
    )
    assert att.session_date == date(2026, 9, 3)  # the PRIOR session, not today


def test_b3_nasdaq_holiday_is_not_a_session():
    """Labor Day 2026-09-07 is not a Nasdaq trading session either."""
    att = latest_completed_session(
        datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc), mic="XNGS"
    )
    assert att.session_date == date(2026, 9, 4)


def test_b3_nasdaq_early_close_is_respected():
    """The day after Thanksgiving 2026 is a genuine early-close Nasdaq session."""
    import exchange_calendars as xc

    cal = xc.get_calendar("XNAS")
    early_close = cal.session_close(datetime(2026, 11, 27))
    assert early_close.hour == 18 and early_close.tzinfo is not None  # 13:00 ET / 18:00 UTC

    # A decision made after the early close attests to that same shortened session.
    att = latest_completed_session(
        datetime(2026, 11, 27, 19, 0, tzinfo=timezone.utc), mic="XNGS"
    )
    assert att.session_date == date(2026, 11, 27)

    # A decision made between the early close and a naive "market never closes
    # before 4pm" assumption must NOT still treat that session as open.
    att2 = latest_completed_session(
        datetime(2026, 11, 27, 18, 30, tzinfo=timezone.utc), mic="XNGS"
    )
    assert att2.session_date == date(2026, 11, 27)


def test_b3_nasdaq_binding_is_deliberate_not_a_silent_nyse_reuse():
    """XNGS/XNMS request the XNAS calendar BY NAME; NYSE lookups are untouched."""
    from live_session_calendar import SUPPORTED_MICS

    assert SUPPORTED_MICS["XNGS"] == "XNAS"
    assert SUPPORTED_MICS["XNMS"] == "XNAS"
    assert SUPPORTED_MICS["XNYS"] == "XNYS"
    assert SUPPORTED_MICS["NYSE"] == "XNYS"
    # Scoped to exactly the MICs this basket needs — no broader alias family.
    assert set(SUPPORTED_MICS) == {"XNYS", "NYSE", "XNGS", "XNMS"}


def test_b3_nyse_regression_unchanged_after_nasdaq_extension():
    """Every existing XNYS case from before the extension still holds."""
    assert latest_completed_session(
        datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic="XNYS"
    ).session_date == date(2026, 9, 2)
    assert latest_completed_session(
        datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc), mic="XNYS"
    ).session_date == date(2026, 9, 1)
    assert latest_completed_session(
        datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc), mic="XNYS"
    ).session_date == date(2026, 9, 4)


def test_b3_unsupported_mic_still_fails_closed_after_nasdaq_extension():
    """The extension is scoped; a non-basket venue is still refused."""
    for mic in ("XLON", "XHKG", "ARCX", "BATS", "XASE", "NASDAQ"):
        with pytest.raises(SessionCalendarError, match="No authorized exchange calendar"):
            latest_completed_session(
                datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic=mic
            )


def test_b3_no_generic_all_us_exchange_fallback():
    """A MIC merely resembling a supported one is not accepted."""
    with pytest.raises(SessionCalendarError):
        latest_completed_session(
            datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc), mic="XNCM"
        )


#: The frozen Pilot 2 discrimination basket (identity/venue only — no
#: investment analysis; see docs/pilot2_variant_edge/
#: PILOT2_VARIANT_EDGE_CHARTER_001.md section 18).
PILOT2_FROZEN_BASKET = (
    "FIS", "FISV", "MELI", "JD", "ADBE", "SNOW", "WCC", "GLNG", "NTR", "CVS",
)


@live
@requires_key
def test_b3_pilot2_frozen_basket_venue_readiness(provider):
    """Every frozen Pilot 2 name resolves to an explicitly supported MIC.

    Identity/MIC resolution only. No price is analysed, no valuation or
    fundamentals are consulted, and no investment conclusion is drawn — this
    proves venue readiness for session attestation, nothing else. A ticker
    resolving to an unsupported MIC is a surfaced blocker, not silently
    bypassed: the assertion below fails loudly and names the offender.
    """
    from live_session_calendar import SUPPORTED_MICS

    unresolved, unsupported = [], []
    for ticker in PILOT2_FROZEN_BASKET:
        result = provider.latest_price(ticker).to_dict()
        if result.get("state") != "AVAILABLE":
            unresolved.append((ticker, result.get("state")))
            continue
        data = result.get("data") or {}
        raw = result.get("raw") or {}
        mic = str(data.get("mic_code") or raw.get("mic_code") or "").strip().upper()
        if mic not in SUPPORTED_MICS:
            unsupported.append((ticker, mic))

    assert not unresolved, f"Could not resolve identity for: {unresolved}"
    assert not unsupported, (
        f"Frozen basket names resolve to unsupported MICs: {unsupported}. "
        "This is a surfaced blocker per the Pilot 2 freeze rule, not something "
        "to bypass automatically."
    )


# ===========================================================================
# B4 — live FX binding
# ===========================================================================


@pytest.fixture(scope="module")
def eurusd_observation():
    import time

    for attempt in range(_RATE_LIMIT_RETRIES + 1):
        _throttle()
        try:
            return fetch_fx_observation("EUR/USD")
        except LiveBindingError as exc:
            if "429" not in str(exc) or attempt == _RATE_LIMIT_RETRIES:
                raise
            time.sleep(_RATE_LIMIT_BACKOFF_S)


@live
@requires_key
def test_b4_correct_pair_and_fresh_observation_passes(eurusd_observation, now):
    fx = bind_fx_snapshot(
        eurusd_observation, from_currency="EUR", to_currency="USD", decision_time=now
    )
    assert (fx.from_currency, fx.to_currency) == ("EUR", "USD")
    assert fx.rate > 0
    assert fx.freshness_status is FreshnessStatus.FRESH
    assert fx.provider == "twelvedata"
    uw = _underwriting_from(_price_snapshot(currency="EUR"), fx=fx)
    validate_fx_binding(uw, _portfolio(), now)  # base USD, price EUR


@live
@requires_key
def test_b4_reversed_pair_blocks(eurusd_observation, now):
    """USD/EUR is a different quantity; it may not be silently inverted."""
    with pytest.raises(LiveBindingError, match="pair mismatch"):
        bind_fx_snapshot(
            eurusd_observation, from_currency="USD", to_currency="EUR", decision_time=now
        )


@live
@requires_key
def test_b4_wrong_pair_blocks(eurusd_observation, now):
    with pytest.raises(LiveBindingError, match="pair mismatch"):
        bind_fx_snapshot(
            eurusd_observation, from_currency="GBP", to_currency="USD", decision_time=now
        )


@live
@requires_key
def test_b4_stale_observation_blocks(eurusd_observation, now):
    """A real observation judged from far in the future is STALE and refused."""
    much_later = now + timedelta(days=30)
    fx = bind_fx_snapshot(
        eurusd_observation, from_currency="EUR", to_currency="USD", decision_time=much_later
    )
    assert fx.freshness_status is FreshnessStatus.STALE
    uw = _underwriting_from(_price_snapshot(currency="EUR"), fx=fx)
    with pytest.raises(ControlFailure, match="FX snapshot is STALE"):
        validate_fx_binding(uw, _portfolio(), much_later)


def test_b4_stale_consistent_fx_labelled_fresh_still_blocks():
    """Self-asserted FRESH on an old timestamp must not survive the age check."""
    old = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)
    fx = FXSnapshot("EUR", "USD", 1.15, old, "twelvedata", FreshnessStatus.FRESH)
    uw = _underwriting_from(_price_snapshot(currency="EUR"), fx=fx)
    with pytest.raises(ControlFailure, match="too old"):
        validate_fx_binding(uw, _portfolio(), datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc))


def test_b4_missing_fx_when_currencies_differ_blocks():
    uw = _underwriting_from(_price_snapshot(currency="EUR"), fx=None)
    with pytest.raises(ControlFailure, match="requires a bound FX snapshot"):
        validate_fx_binding(uw, _portfolio(), datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc))


def test_b4_not_required_when_currencies_match():
    """FX is not manufactured for a USD security in a USD portfolio."""
    uw = _underwriting_from(_price_snapshot(currency="USD"), fx=None)
    validate_fx_binding(uw, _portfolio(), datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc))


# ===========================================================================
# B5 — integrated production-adapter replay through the accepted facade
# ===========================================================================


@live
@requires_key
def test_b5_integrated_live_replay_through_facade(brk_b_evidence, now, attestation, tmp_path):
    """Real observation -> identity -> calendar -> PriceSnapshot -> Stage 7.

    The Stage 7 outcome is whatever the evidence produces. No ELIGIBLE or
    INITIATE result is forced: no human underwriting exists for BRK.B, so the
    controls are expected to refuse to advance, and that refusal is the proof.
    """
    facade = CapitalDecisionFacade(
        ledger_path=tmp_path / "decisions.jsonl", artifact_dir=tmp_path / "artifacts"
    )
    portfolio = _portfolio()
    uw = _underwriting_from(brk_b_evidence.snapshot)
    run = facade.run_stage7(
        uw,
        portfolio,
        _position(portfolio),
        _alternatives(BRK_B_KEY, now),
        now,
        artifact_name="gate_b_live_replay",
        known_latest_session_date=attestation.session_date,
    )

    # 1-4: the chain actually carried live identity, price and session truth.
    assert run.result.security_key == BRK_B_KEY
    assert uw.price_snapshot.provider == "twelvedata"
    assert uw.price_snapshot.latest_completed_session_date == attestation.session_date

    # 6: artifact frozen AND retained on disk, hash-verifiable.
    assert run.artifact_ref.artifact_path
    assert Path(run.artifact_ref.artifact_path).is_file()
    assert len(run.artifact_ref.sha256) == 64

    # 7: Stage 7 emits no PortfolioAction.
    assert not hasattr(run.result, "human_stage8_action")
    assert not isinstance(getattr(run.result, "status", None), PortfolioAction)
    assert "NO PORTFOLIO ACTION" in run.result.comparison_header

    # 8: the human Stage 8 boundary is still separate and unwritten.
    assert _ledger_is_empty(facade)

    # The evidence, not the test, decided the outcome.
    assert run.result.status in {
        "BLOCKED",
        "WATCH / NO DECISION",
        "NOT DISTINGUISHABLE",
        "ELIGIBLE FOR STAGE 8",
    }


@live
@requires_key
def test_b5_live_replay_forged_initiate_cannot_persist(
    brk_b_evidence, now, attestation, tmp_path
):
    """9: a direct INITIATE around the real Stage 7 result still cannot be written."""
    facade = CapitalDecisionFacade(
        ledger_path=tmp_path / "decisions.jsonl", artifact_dir=tmp_path / "artifacts"
    )
    portfolio = _portfolio()
    run = facade.run_stage7(
        _underwriting_from(brk_b_evidence.snapshot),
        portfolio,
        _position(portfolio),
        _alternatives(BRK_B_KEY, now),
        now,
        artifact_name="gate_b_live_forge",
        known_latest_session_date=attestation.session_date,
    )
    if run.result.status == "ELIGIBLE FOR STAGE 8":
        pytest.skip("live evidence produced ELIGIBLE; forgery case needs a non-eligible run")
    with pytest.raises(ControlFailure, match="requires Stage 7 status"):
        facade.record_final_decision(
            run,
            record_id="GATEB-FORGE-001",
            human_stage8_action=PortfolioAction.INITIATE,
            human_rationale="attempted funding on a non-eligible live comparison",
            alternatives_considered=("Treasury/Cash",),
            input_versions=_input_versions(),
            created_at=now,
            portfolio_snapshot_id=portfolio.snapshot_id,
        )
    assert _ledger_is_empty(facade)


@live
@requires_key
def test_b5_live_replay_evidence_is_reproducible(brk_b_evidence):
    """10: the retained evidence names its sources well enough to reproduce."""
    ev = brk_b_evidence.to_dict()
    assert ev["session_attestation"]["calendar_version"] == "exchange_calendars==4.13.2"
    assert ev["session_attestation"]["exchange"] == "XNYS"
    assert ev["price_binding"]["provider"] == "twelvedata"
    assert ev["raw_observation"]
    # No credential may appear anywhere in retained evidence.
    key = os.environ.get("TWELVEDATA_API_KEY")
    assert key and key not in str(ev)


# ===========================================================================
# helpers — fixtures only, no investment conclusions asserted
# ===========================================================================


def _price_snapshot(
    *,
    session: date = date(2026, 9, 2),
    latest_completed: date | None = None,
    currency: str = "USD",
    freshness: FreshnessStatus = FreshnessStatus.FRESH,
    as_of: datetime | None = None,
):
    from stock_atlas.models import PriceSnapshot

    return PriceSnapshot(
        security_key=BRK_B_KEY,
        ticker="BRK.B",
        price=505.0,
        price_as_of=as_of or datetime(2026, 9, 2, 19, 59, tzinfo=timezone.utc),
        price_session_date=session,
        latest_completed_session_date=latest_completed or session,
        currency=currency,
        provider="twelvedata",
        market_session_status="COMPLETED",
        adjusted=False,
        freshness_status=freshness,
        price_mode=PriceMode.COMPLETED_SESSION,
        quoted_security_key=BRK_B_KEY,
    )


def _underwriting_from(price, *, fx: FXSnapshot | None = None) -> CandidateUnderwriting:
    """Underwriting shell around a bound price.

    NOTE: no human underwriting exists for BRK.B. ``return_band`` is None and
    the gate is UNVERIFIED on purpose — Gate B proves the DATA path, and
    fabricating an investment conclusion to force an ELIGIBLE result would be a
    methodology change, which is out of scope.
    """
    return CandidateUnderwriting(
        security_key=price.security_key,
        ticker=price.ticker,
        security_decision=SecurityDecision.BUY,
        price_snapshot=price,
        observable_regime="NOT UNDERWRITTEN — Gate B data-binding replay only",
        observable_regime_evidence=("no human underwriting supplied",),
        atlas_variant="NOT UNDERWRITTEN — Gate B data-binding replay only",
        variant_evidence=("no human underwriting supplied",),
        return_band=None,
        return_band_basis=(),
        required_return_band=None,
        underwriting_gate_status=UnderwritingGateStatus.UNVERIFIED,
        uncertainties=(
            TypedUncertainty("underwriting", "no human underwriting exists", BlockFlag.YES),
        ),
        dominant_drivers=("not underwritten",),
        revisit_triggers=RevisitTriggers(
            "±25% price", datetime(2026, 12, 1, tzinfo=timezone.utc)
        ),
        underwriting_provenance=("Gate B live binding harness",),
        return_currency="USD",
        fx_snapshot=fx,
    )


def _portfolio() -> PortfolioSnapshot:
    return PortfolioSnapshot(
        snapshot_id="GATE-B-REPLAY",
        as_of=datetime(2026, 9, 2, 21, 0, tzinfo=timezone.utc),
        total_value=1_000_000,
        holdings=(Holding("SEC:MSFT", "MSFT", 120_000, 0.12, "taxable", "taxable"),),
        funding_pocket=FundingPocket(
            account="cash",
            account_type="taxable",
            amount=50_000,
            t_plus_1_deployable=True,
            constraints_supplied=True,
            tax_status=VerificationStatus.VERIFIED,
            liquidity_status=VerificationStatus.VERIFIED,
            execution_status=VerificationStatus.VERIFIED,
        ),
        trims_permitted=False,
        add_only_policy=True,
        base_currency="USD",
    )


def _alternatives(candidate_key: str, now: datetime):
    """Treasury/Cash, beta and Do Nothing remain distinct live alternatives."""
    return (
        ComparisonAlternative(
            AlternativeType.BETA,
            "SPY",
            ReturnBand(0.07, 0.10),
            security_key="ETF:SPY",
            overlap=ETFOverlap("SPY", candidate_key, OverlapStatus.UNMEASURED),
            notes=("coarse SPY range",),
        ),
        ComparisonAlternative(
            AlternativeType.TREASURY_CASH,
            "Treasury/Cash",
            ReturnBand(0.035, 0.045),
            market_reference=MarketReferenceSnapshot(
                "UST-13W", 0.039, now, "GATE_B_REFERENCE", FreshnessStatus.FRESH, "USD"
            ),
            duration_match_status=VerificationStatus.VERIFIED,
            notes=("duration/reinvestment normalized",),
        ),
        ComparisonAlternative(AlternativeType.DO_NOTHING, "Do Nothing"),
    )


def _position(portfolio: PortfolioSnapshot):
    return build_position_proposal(
        portfolio,
        current_weight=0.0,
        increment_dollars=50_000,
        classification=PositionClassification.STARTER,
        capacity_status=CapacityStatus.AVAILABLE,
        remaining_capacity=0.10,
        funding_source="cash",
        funding_mode=FundingMode.INTERNAL_CASH,
    )


def _input_versions():
    from stock_atlas.models import FrozenInputRef, InputVersions

    ref = FrozenInputRef("gate-b-v1", "0" * 64)
    return InputVersions(ref, ref, ref, ref, ref)
