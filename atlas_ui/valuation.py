"""Arithmetic for investment research: reverse valuation, history-bounded scenarios, total return and cash accrual.

Pure functions of their inputs. No data access, no forecast, no score, no rank, no recommendation: each result is a conditional statement
("if EPS compounds at g and the exit multiple is m, the IRR from this price is r"). Facts, assumptions and outputs are labelled by the caller.

Conventions (stated once; every caller inherits them):
  * IRR is XIRR on dated cash flows, actual/365, annual effective.
  * A scenario's dividends are paid quarterly at calendar quarter-ends; the dividend per share in a year is the current annual run-rate scaled by
    EPS(year)/EPS(base year) (a constant payout ratio).
  * The terminal price is exit P/E x EPS of the exit fiscal year, received on the exit date together with that quarter's dividend.
  * Total return reinvests each cash dividend at the (ex-dividend, unadjusted) close of its ex-date. It must be computed from UNADJUSTED closes; applying it
    to a dividend-adjusted series counts dividends twice. ``adjustment_diagnostic`` tests which kind of series a provider returned.
  * Cash accrual compounds a par-yield proxy: each interval earns yield_at_interval_start x days/365.
"""
from __future__ import annotations

from bisect import bisect_right
from datetime import date, timedelta


# ------------------------------------------------------------------------------------------------------------------------------ IRR
def xirr(flows: list[tuple[date, float]], lo: float = -0.95, hi: float = 5.0, tol: float = 1e-10) -> float | None:
    """Annual effective IRR of dated flows (the first is the outflow). None if the flows do not change sign or no root is bracketed."""
    flows = sorted(flows)
    if len(flows) < 2 or not (any(c < 0 for _, c in flows) and any(c > 0 for _, c in flows)):
        return None
    d0 = flows[0][0]

    def npv(r: float) -> float:
        return sum(c / (1.0 + r) ** ((d - d0).days / 365.0) for d, c in flows)

    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < tol or (hi - lo) < tol:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def quarter_ends(after: date, through: date) -> list[date]:
    """Calendar quarter-end dates d with after < d <= through."""
    out, y = [], after.year
    while y <= through.year:
        for m, dd in ((3, 31), (6, 30), (9, 30), (12, 31)):
            d = date(y, m, dd)
            if after < d <= through:
                out.append(d)
        y += 1
    return out


# ------------------------------------------------------------------------------------------------------------------------------ scenarios
def scenario_flows(*, price0: float, as_of: date, eps_base: float, base_fy: int, cagr: float, exit_pe: float, exit_date: date,
                   dps_run_rate: float) -> list[tuple[date, float]]:
    """Dated cash flows of buying at ``price0`` on ``as_of`` and selling at ``exit_pe`` x EPS(exit fiscal year) on ``exit_date``."""
    eps = lambda fy: eps_base * (1.0 + cagr) ** (fy - base_fy)
    flows = [(as_of, -price0)]
    for q in quarter_ends(as_of, exit_date):
        flows.append((q, dps_run_rate * eps(q.year) / eps_base / 4.0))
    flows.append((exit_date, exit_pe * eps(exit_date.year)))
    return flows


def scenario_irr(**kw) -> float | None:
    return xirr(scenario_flows(**kw))


def implied_cagr(*, target_irr: float, price0: float, as_of: date, eps_base: float, base_fy: int, exit_pe: float, exit_date: date,
                 dps_run_rate: float, lo: float = -0.30, hi: float = 0.50) -> float | None:
    """REVERSE VALUATION: the constant EPS growth rate (from ``base_fy``) at which buying at ``price0`` earns exactly ``target_irr`` given ``exit_pe``.
    IRR rises with growth, so a root is bracketed or None is returned (the target is out of reach inside [lo, hi])."""
    f = lambda g: (scenario_irr(price0=price0, as_of=as_of, eps_base=eps_base, base_fy=base_fy, cagr=g, exit_pe=exit_pe, exit_date=exit_date,
                                dps_run_rate=dps_run_rate) or -1.0) - target_irr
    if f(lo) > 0 or f(hi) < 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-10:
            break
    return (lo + hi) / 2


def implied_perpetual_growth(*, fcf_per_share: float, price: float, required_return: float) -> float | None:
    """Gordon reverse valuation: P = FCF0 (1+g) / (r - g)  =>  g = (r P - FCF0) / (P + FCF0)."""
    return (required_return * price - fcf_per_share) / (price + fcf_per_share) if price > 0 and fcf_per_share is not None else None


def rolling_cagrs(series: dict[int, float], window: int) -> dict[int, float]:
    """CAGR over every ``window``-year span in a {fiscal year: value} series, keyed by the END year. Only positive values; gaps are skipped, not filled."""
    out = {}
    for y, v in sorted(series.items()):
        s = series.get(y - window)
        if s is not None and s > 0 and v > 0:
            out[y] = (v / s) ** (1.0 / window) - 1.0
    return out


def quantile_summary(values: list[float]) -> dict:
    """Observed minimum, median and maximum (no smoothing, no inference); empty input gives None."""
    v = sorted(values)
    if not v:
        return {"n": 0, "min": None, "median": None, "max": None}
    mid = len(v) // 2
    return {"n": len(v), "min": v[0], "median": v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2, "max": v[-1]}


# ------------------------------------------------------------------------------------------------------------------------------ price series
def on_or_before(closes: dict[date, float], d: date) -> tuple[date, float] | None:
    ds = sorted(closes)
    i = bisect_right(ds, d)
    return (ds[i - 1], closes[ds[i - 1]]) if i else None


def annualize(total_return: float, start: date, end: date, min_days: int = 365) -> float | None:
    """Annualized only for windows of at least ``min_days``: shorter windows are reported as a plain period return (None here), never extrapolated."""
    days = (end - start).days
    return (1.0 + total_return) ** (365.0 / days) - 1.0 if days >= min_days and total_return > -1 else None


def total_return(closes: dict[date, float], dividends: dict[date, float], start: date, end: date) -> dict | None:
    """Total return of holding from the close on/before ``start`` to the close on/before ``end``, reinvesting each dividend at its ex-date close.
    ``closes`` MUST be unadjusted for dividends. Returns the dates actually used so nothing is silently shifted; None if the window is not covered."""
    a, b = on_or_before(closes, start), on_or_before(closes, end)
    if not a or not b or b[0] <= a[0] or a[0] > start + timedelta(days=7):
        return None
    units, divs, ds = 1.0, 0.0, 0
    for d in sorted(dividends):
        if a[0] < d <= b[0]:
            px = on_or_before(closes, d)
            if px:
                units *= 1.0 + dividends[d] / px[1]
                divs += dividends[d]
                ds += 1
    tr = units * b[1] / a[1] - 1.0
    return {"start_requested": start.isoformat(), "start_used": a[0].isoformat(), "end_used": b[0].isoformat(), "start_close": a[1], "end_close": b[1],
            "price_return": b[1] / a[1] - 1.0, "total_return": tr, "dividends_in_window": ds, "dividends_per_share_sum": divs,
            "annualized_total_return": annualize(tr, a[0], b[0]), "days": (b[0] - a[0]).days}


def cash_accrual(yields: list[tuple[date, float]], start: date, end: date) -> dict | None:
    """Compounded return of rolling a par-yield proxy (percent, bond-equivalent) between two dates; the yield at the start of each interval is earned."""
    ys = sorted(yields)
    obs = [(d, y) for d, y in ys if start <= d <= end]
    first = on_or_before({d: y for d, y in ys}, start)
    if first is None or not obs or (obs[0][0] - start).days > 7:
        return None
    pts = [(start, first[1])] + [o for o in obs if o[0] > start]
    f = 1.0
    for (d0, y0), (d1, _y1) in zip(pts, pts[1:] + [(end, pts[-1][1])]):
        f *= 1.0 + y0 / 100.0 * (d1 - d0).days / 365.0
    return {"total_return": f - 1.0, "annualized": annualize(f - 1.0, start, end), "start": start.isoformat(), "end": end.isoformat(),
            "observations": len(pts), "yield_at_start_pct": first[1], "yield_at_end_pct": pts[-1][1]}


# ------------------------------------------------------------------------------------------------------------------------------ adjustment convention
def adjustment_diagnostic(unadjusted: dict[date, float], candidate: dict[date, float], dividends: dict[date, float], start: date, end: date,
                          tolerance: float = 0.005) -> dict:
    """Is ``candidate`` a DIVIDEND-ADJUSTED series, a price-only (split-adjusted) series, or neither, relative to the unadjusted closes?
    Compares the candidate's plain price return with the unadjusted series' price return and total return over the same window."""
    tr = total_return(unadjusted, dividends, start, end)
    a, b = on_or_before(candidate, start), on_or_before(candidate, end)
    if not tr or not a or not b:
        return {"verdict": "UNKNOWN", "reason": "window not covered by both series"}
    cand_pr = b[1] / a[1] - 1.0
    near_total, near_price = abs(cand_pr - tr["total_return"]) <= tolerance, abs(cand_pr - tr["price_return"]) <= tolerance
    # the wrong way to use an adjusted series: reinvest dividends on top of it
    double = total_return(candidate, dividends, start, end)
    verdict = ("DIVIDEND_ADJUSTED" if near_total and not near_price else "PRICE_ONLY" if near_price and not near_total else
               "INDISTINGUISHABLE (dividends too small over the window)" if near_total and near_price else "UNCLEAR")
    return {"verdict": verdict, "window": [tr["start_used"], tr["end_used"]], "candidate_price_return": cand_pr, "unadjusted_price_return": tr["price_return"],
            "unadjusted_total_return_with_reinvested_dividends": tr["total_return"], "tolerance": tolerance,
            "double_counting_error_if_dividends_were_added_to_the_candidate": (double["total_return"] - tr["total_return"]) if double else None}


def infer_dividends(unadjusted: dict[date, float], adjusted: dict[date, float], min_fraction: float = 2e-4) -> dict[date, float]:
    """Cash dividends per share implied by a DIVIDEND-ADJUSTED series: the adjusted/unadjusted ratio steps down at each ex-date, and the step is the
    dividend over the previous unadjusted close. ``D = unadjusted[prev] x (1 - ratio[prev] / ratio[exdate])``. Steps smaller than ``min_fraction``
    are rounding noise and ignored. This is an INFERENCE from a secondary series: it must be checked against a primary dividend record before use."""
    ds = sorted(d for d in unadjusted if d in adjusted)
    out = {}
    for prev, d in zip(ds, ds[1:]):
        rp, rd = adjusted[prev] / unadjusted[prev], adjusted[d] / unadjusted[d]
        step = 1.0 - rp / rd
        if step > min_fraction:
            out[d] = unadjusted[prev] * step
    return out
