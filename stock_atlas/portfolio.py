from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .controls import ControlFailure
from .models import FundingMode, PortfolioSnapshot, PositionProposal, PositionClassification, CapacityStatus


@dataclass(frozen=True)
class ETFConstituentExposure:
    etf_security_key: str
    constituent_security_key: str
    etf_portfolio_weight: float
    constituent_weight_in_etf: float
    holdings_as_of: str
    source: str

    @property
    def portfolio_lookthrough_weight(self) -> float:
        return self.etf_portfolio_weight * self.constituent_weight_in_etf


def effective_name_exposure(
    security_key: str,
    direct_weights: Mapping[str, float],
    etf_lookthrough: Sequence[ETFConstituentExposure],
) -> float:
    direct = direct_weights.get(security_key, 0.0)
    indirect = sum(
        x.portfolio_lookthrough_weight
        for x in etf_lookthrough
        if x.constituent_security_key == security_key
    )
    return direct + indirect


def driver_exposure_from_components(
    direct_driver_weights: Mapping[str, float],
    decomposed_etf_driver_weights: Mapping[str, float],
) -> dict[str, float]:
    """Combine direct + decomposed ETF driver exposure without adding full ETF weight again.

    The caller must decompose ETF exposure into driver weights first. This function deliberately
    has no argument for the ETF's full weight, preventing the common double-counting error.
    """
    keys = set(direct_driver_weights) | set(decomposed_etf_driver_weights)
    out = {k: direct_driver_weights.get(k, 0.0) + decomposed_etf_driver_weights.get(k, 0.0) for k in keys}
    for k, v in out.items():
        if v < -1e-12 or v > 1.0 + 1e-9:
            raise ControlFailure(f"Driver exposure out of range for {k}: {v}")
    return out


def build_position_proposal(
    portfolio: PortfolioSnapshot,
    *,
    current_weight: float,
    increment_dollars: float,
    classification: PositionClassification,
    capacity_status: CapacityStatus,
    remaining_capacity: float | None,
    funding_source: str,
    funding_mode: FundingMode,
) -> PositionProposal:
    if increment_dollars <= 0:
        raise ControlFailure("increment_dollars must be positive")
    if funding_mode == FundingMode.EXTERNAL_NEW_CAPITAL:
        post_total = portfolio.total_value + increment_dollars
    else:
        post_total = portfolio.total_value

    current_dollars = current_weight * portfolio.total_value
    post_weight = (current_dollars + increment_dollars) / post_total
    increment_weight = increment_dollars / post_total

    return PositionProposal(
        current_weight=current_weight,
        proposed_increment_weight=increment_weight,
        proposed_increment_dollars=increment_dollars,
        post_trade_portfolio_value=post_total,
        post_trade_weight=post_weight,
        classification=classification,
        capacity_status=capacity_status,
        remaining_capacity=remaining_capacity,
        funding_source=funding_source,
        funding_mode=funding_mode,
    )


def capacity_curve_dollars(
    portfolio_value: float,
    weights=(0.01, 0.03, 0.05, 0.10),
    *,
    funding_mode: FundingMode = FundingMode.INTERNAL_CASH,
) -> dict[float, float]:
    """Translate target portfolio weights to dollars without mixing pre/post-money math.

    Internal cash/recycle keeps total portfolio value unchanged: dollars = weight * NAV.
    External new capital increases NAV, so solving d / (NAV + d) = weight gives
    d = weight * NAV / (1 - weight).
    """
    if portfolio_value <= 0:
        raise ControlFailure("portfolio_value must be positive")
    out: dict[float, float] = {}
    for w in weights:
        if w <= 0 or w >= 1:
            raise ControlFailure("capacity-curve weights must be between 0 and 1 (exclusive)")
        if funding_mode == FundingMode.EXTERNAL_NEW_CAPITAL:
            out[w] = (w * portfolio_value) / (1.0 - w)
        else:
            out[w] = portfolio_value * w
    return out
