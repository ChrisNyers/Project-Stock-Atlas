"""Valuation and benchmark arithmetic: pure functions checked against cases with a known answer.

No market data, no network. Each expected value is derivable by hand (stated beside it).
"""
from datetime import date, timedelta

import pytest

from atlas_ui import valuation as V

D0 = date(2026, 1, 1)


def test_xirr_known_cases():
    assert V.xirr([(D0, -100.0), (date(2027, 1, 1), 110.0)]) == pytest.approx(0.10, abs=1e-6)             # 365 days: 10% a year
    assert V.xirr([(D0, -100.0), (date(2028, 1, 1), 121.0)]) == pytest.approx(0.10, abs=1e-4)             # two years: 1.1^2
    assert V.xirr([(D0, -100.0), (date(2027, 1, 1), 100.0)]) == pytest.approx(0.0, abs=1e-8)
    assert V.xirr([(D0, 100.0), (date(2027, 1, 1), 110.0)]) is None                                       # no outflow
    assert V.xirr([(D0, -100.0)]) is None


def test_zero_growth_flat_multiple_no_dividends_is_a_zero_return():
    r = V.scenario_irr(price0=100, as_of=D0, eps_base=10, base_fy=2025, cagr=0.0, exit_pe=10.0, exit_date=date(2030, 12, 31), dps_run_rate=0.0)
    assert r == pytest.approx(0.0, abs=1e-8)                                                              # EPS 10 x 10 = 100 back


def test_a_constant_dividend_with_a_flat_price_returns_about_the_yield():
    r = V.scenario_irr(price0=100, as_of=D0, eps_base=10, base_fy=2025, cagr=0.0, exit_pe=10.0, exit_date=date(2030, 12, 31), dps_run_rate=4.0)
    assert 0.040 < r < 0.0415                                                                             # 4/100 a year, paid quarterly: just above 4%


def test_growth_raises_and_a_lower_exit_multiple_lowers_the_return():
    base = dict(price0=100, as_of=D0, eps_base=10, base_fy=2025, exit_date=date(2030, 12, 31), dps_run_rate=0.0)
    a, b, c = (V.scenario_irr(cagr=g, exit_pe=pe, **base) for g, pe in ((0.0, 10.0), (0.05, 10.0), (0.05, 8.0)))
    assert b > a and b > c                                                                                   # more growth helps; a lower exit multiple hurts
    assert b == pytest.approx(0.05, abs=2e-3)                                                             # price = 10 x EPS(2030) = 100 x 1.05^5, over 5.0 years


def test_reverse_valuation_inverts_the_scenario():
    kw = dict(price0=250.5, as_of=date(2026, 10, 28), eps_base=11.95, base_fy=2025, exit_pe=19.0, exit_date=date(2030, 12, 31), dps_run_rate=7.44)
    for target in (0.0418, 0.05, 0.08):
        g = V.implied_cagr(target_irr=target, **kw)
        assert V.scenario_irr(cagr=g, **kw) == pytest.approx(target, abs=1e-7)
    assert V.implied_cagr(target_irr=0.9, **kw) is None                                                   # out of reach: no root, no guess
    assert V.implied_cagr(target_irr=0.06, **kw) > V.implied_cagr(target_irr=0.05, **kw)                  # a higher hurdle needs more growth


def test_perpetual_growth_reverse_valuation():
    g = V.implied_perpetual_growth(fcf_per_share=10.0, price=200.0, required_return=0.09)
    assert g == pytest.approx((0.09 * 200 - 10) / 210)                                                     # 3.81%
    assert 10.0 * (1 + g) / (0.09 - g) == pytest.approx(200.0)                                             # it reproduces the price


def test_rolling_cagrs_and_summary_do_not_fill_gaps():
    s = {2020: 100.0, 2021: 110.0, 2022: 121.0, 2024: 146.41}                                              # 2023 missing
    c = V.rolling_cagrs(s, 2)
    assert c == {2022: pytest.approx(0.10), 2024: pytest.approx(0.10)} and 2023 not in c and 2021 not in c
    q = V.quantile_summary([0.01, 0.03, 0.05, 0.09])
    assert (q["n"], q["min"], q["median"], q["max"]) == (4, 0.01, 0.04, 0.09) and V.quantile_summary([])["median"] is None


def closes(start, n, f):
    return {start + timedelta(days=i): f(i) for i in range(n)}


def test_total_return_reinvests_dividends_at_the_ex_date_close_and_reports_the_dates_used():
    px = closes(date(2025, 1, 1), 400, lambda i: 100.0)                                                   # flat price
    tr = V.total_return(px, {date(2025, 7, 1): 2.0}, date(2025, 1, 1), date(2025, 12, 31))
    assert tr["price_return"] == 0.0 and tr["total_return"] == pytest.approx(0.02) and tr["dividends_in_window"] == 1
    two = V.total_return(px, {date(2025, 4, 1): 2.0, date(2025, 10, 1): 2.0}, date(2025, 1, 1), date(2025, 12, 31))
    assert two["total_return"] == pytest.approx(1.02 * 1.02 - 1)                                           # reinvested: compounding, not 4%
    assert V.total_return(px, {}, date(2025, 1, 1), date(2025, 12, 31))["annualized_total_return"] is None  # 364 days: not annualized
    assert V.total_return(px, {}, date(2024, 1, 1), date(2025, 6, 1)) is None                              # start not covered: no number
    assert V.total_return(px, {date(2024, 6, 1): 9.0}, date(2025, 1, 1), date(2025, 12, 31))["dividends_in_window"] == 0   # outside the window


def test_dividends_on_the_start_date_are_not_earned_and_the_end_date_is_included():
    px = closes(date(2025, 1, 1), 100, lambda i: 50.0)
    tr = V.total_return(px, {date(2025, 1, 1): 1.0, date(2025, 3, 1): 1.0}, date(2025, 1, 1), date(2025, 3, 1))
    assert tr["dividends_in_window"] == 1 and tr["total_return"] == pytest.approx(0.02)


def test_cash_accrual_known_values():
    ys = [(date(2025, 1, 1) + timedelta(days=i), 4.0) for i in range(0, 400)]
    one_year = V.cash_accrual(ys, date(2025, 1, 1), date(2026, 1, 1))
    assert one_year["total_return"] == pytest.approx(0.04 * 365 / 365 + 0, abs=2e-3) and 0.0399 < one_year["annualized"] < 0.0415
    assert V.cash_accrual(ys, date(2020, 1, 1), date(2021, 1, 1)) is None


def test_adjustment_diagnostic_tells_split_only_from_dividend_adjusted_series_and_quantifies_double_counting():
    start = date(2025, 1, 1)
    unadj = closes(start, 366, lambda i: 100.0 + 0.02 * i)                                                 # drifts up, no dividends in the price
    divs = {date(2025, 4, 1): 2.0, date(2025, 7, 1): 2.0, date(2025, 10, 1): 2.0}
    end = date(2025, 12, 31)
    tr = V.total_return(unadj, divs, start, end)
    split_only = dict(unadj)
    adj = {}
    factor = 1.0
    for d in sorted(unadj, reverse=True):                                                                  # a dividend-adjusted series: earlier days scaled down
        adj[d] = unadj[d] * factor
        if d in divs:
            factor *= 1 - divs[d] / unadj[d]
    a = V.adjustment_diagnostic(unadj, split_only, divs, start, end)
    assert a["verdict"] == "PRICE_ONLY"
    b = V.adjustment_diagnostic(unadj, adj, divs, start, end, tolerance=0.01)
    assert b["verdict"] in ("DIVIDEND_ADJUSTED", "UNCLEAR")
    assert a["double_counting_error_if_dividends_were_added_to_the_candidate"] == pytest.approx(0.0, abs=1e-9)   # a price-only series is the right input for reinvestment
    assert b["double_counting_error_if_dividends_were_added_to_the_candidate"] > 0.01                          # adding dividends to an adjusted series overstates the return


def test_dividends_are_recovered_from_a_dividend_adjusted_series():
    start = date(2025, 1, 1)
    unadj = closes(start, 366, lambda i: 100.0 + 0.05 * i)
    divs = {date(2025, 4, 1): 1.5, date(2025, 7, 1): 1.5, date(2025, 10, 1): 1.6}
    adj, factor = {}, 1.0
    for d in sorted(unadj, reverse=True):                                                                  # earlier days are scaled down at each ex-date
        adj[d] = unadj[d] * factor
        if d in divs:
            factor *= 1 - divs[d] / unadj[d - timedelta(days=1)]
    got = V.infer_dividends(unadj, adj)
    assert set(got) == set(divs) and all(got[d] == pytest.approx(divs[d], rel=1e-6) for d in divs)
    assert V.infer_dividends(unadj, unadj) == {}                                                           # a price-only series implies none
