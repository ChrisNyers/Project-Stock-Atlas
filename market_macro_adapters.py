"""
Market and Macro Data Adapters

Provider-neutral interfaces with concrete implementations.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ============================================================================
# MARKET DATA ADAPTER INTERFACE
# ============================================================================

class MarketDataAdapter(ABC):
    """Provider-neutral market data interface."""

    @abstractmethod
    def get_quote(self, ticker: str) -> Optional[Dict]:
        """Get current quote."""
        pass

    @abstractmethod
    def get_previous_close(self, ticker: str) -> Optional[float]:
        """Get previous day's close."""
        pass

    @abstractmethod
    def get_daily_bars(self, ticker: str, limit: int = 250) -> Optional[List[Dict]]:
        """Get recent daily OHLCV bars."""
        pass

    @abstractmethod
    def get_historical_bars(self, ticker: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """Get historical bars for date range."""
        pass

    @abstractmethod
    def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """Get dividend history."""
        pass

    @abstractmethod
    def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """Get stock split history."""
        pass

    @abstractmethod
    def get_provider_status(self) -> Dict[str, Any]:
        """Get provider health status."""
        pass


# ============================================================================
# MASSIVE ADAPTER (Market Data)
# ============================================================================

class MassiveAdapter(MarketDataAdapter):
    """
    Concrete implementation using Massive market data.
    Stub implementation for Sprint 1 - extend with actual API calls.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MASSIVE_API_KEY")
        self.base_url = "https://api.massive.com"  # Placeholder
        self.last_success = None
        self.last_error = None

    def get_quote(self, ticker: str) -> Optional[Dict]:
        """
        Get current quote.
        Stub: In production, call Massive API.
        """
        try:
            # Placeholder: would call Massive API
            # For testing: return mock data
            logger.info(f"Fetching quote for {ticker}")

            # Mock response
            return {
                "ticker": ticker,
                "price": 420.50,  # Mock price
                "previous_close": 418.75,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "Massive",
                "session": "REGULAR"
            }
        except Exception as e:
            logger.error(f"Error fetching quote: {e}")
            self.last_error = str(e)
            return None

    def get_previous_close(self, ticker: str) -> Optional[float]:
        """Get previous close."""
        quote = self.get_quote(ticker)
        return quote.get("previous_close") if quote else None

    def get_daily_bars(self, ticker: str, limit: int = 250) -> Optional[List[Dict]]:
        """
        Get recent daily bars.
        Stub implementation.
        """
        try:
            logger.info(f"Fetching daily bars for {ticker}")

            # Mock historical data
            bars = []
            base_price = 420.0
            for i in range(limit):
                date = datetime.utcnow() - timedelta(days=i)
                bars.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": base_price - i * 0.1,
                    "high": base_price - i * 0.05,
                    "low": base_price - i * 0.15,
                    "close": base_price - i * 0.1,
                    "volume": 25000000 + i * 100000
                })

            self.last_success = datetime.utcnow()
            return bars
        except Exception as e:
            logger.error(f"Error fetching bars: {e}")
            self.last_error = str(e)
            return None

    def get_historical_bars(self, ticker: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """Get bars for date range."""
        try:
            logger.info(f"Fetching historical bars {ticker} {start_date} to {end_date}")

            # Mock: In production, would query Massive API
            return []
        except Exception as e:
            logger.error(f"Error fetching historical bars: {e}")
            self.last_error = str(e)
            return None

    def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """Get dividend history."""
        try:
            logger.info(f"Fetching dividends for {ticker}")

            # Mock dividend data
            return [
                {
                    "ex_date": "2024-08-15",
                    "payment_date": "2024-09-15",
                    "amount": 0.68,
                    "type": "regular"
                }
            ]
        except Exception as e:
            logger.error(f"Error fetching dividends: {e}")
            self.last_error = str(e)
            return None

    def get_splits(self, ticker: str) -> Optional[List[Dict]]:
        """Get split history."""
        try:
            logger.info(f"Fetching splits for {ticker}")

            # Mock: MSFT had 3:1 split in 2024
            return [
                {
                    "ex_date": "2024-09-09",
                    "split_from": 1,
                    "split_to": 3
                }
            ]
        except Exception as e:
            logger.error(f"Error fetching splits: {e}")
            self.last_error = str(e)
            return None

    def get_provider_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            "provider": "Massive",
            "status": "AVAILABLE" if not self.last_error else "DEGRADED",
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error
        }


# ============================================================================
# MACRO DATA ADAPTER INTERFACE
# ============================================================================

class MacroDataAdapter(ABC):
    """Provider-neutral macro data interface."""

    @abstractmethod
    def get_series(self, series_id: str, start_date: Optional[str] = None) -> Optional[List[Dict]]:
        """Get macro series data."""
        pass

    @abstractmethod
    def get_multiple_series(self, series_ids: List[str]) -> Optional[Dict[str, List[Dict]]]:
        """Get multiple series."""
        pass

    @abstractmethod
    def get_latest_value(self, series_id: str) -> Optional[Dict]:
        """Get most recent value."""
        pass

    @abstractmethod
    def get_provider_status(self) -> Dict[str, Any]:
        """Get provider health status."""
        pass


# ============================================================================
# FRED ADAPTER (Federal Reserve Economic Data)
# ============================================================================

class FREDAdapter(MacroDataAdapter):
    """
    Concrete implementation using FRED (St. Louis Federal Reserve).
    Stub implementation for Sprint 1.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        self.base_url = "https://api.stlouisfed.org/fred"
        self.last_success = None
        self.last_error = None

    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Get macro series data.
        Stub: In production, call FRED API.
        """
        try:
            logger.info(f"Fetching FRED series {series_id}")

            # Mock data for key series
            if series_id == "DGS10":  # 10-Year Treasury
                return [
                    {
                        "date": "2024-08-12",
                        "value": 3.96,
                        "series_id": "DGS10",
                        "series_name": "10-Year Treasury Constant Maturity Rate"
                    }
                ]
            elif series_id == "DFF":  # Federal Funds Effective Rate
                return [
                    {
                        "date": "2024-08-12",
                        "value": 4.42,
                        "series_id": "DFF",
                        "series_name": "Federal Funds Effective Rate"
                    }
                ]
            elif series_id == "TB3MS":  # 3-Month Treasury Bill
                return [
                    {
                        "date": "2024-08-12",
                        "value": 5.35,
                        "series_id": "TB3MS",
                        "series_name": "3-Month Treasury Bill"
                    }
                ]

            self.last_success = datetime.utcnow()
            return []
        except Exception as e:
            logger.error(f"Error fetching FRED series: {e}")
            self.last_error = str(e)
            return None

    def get_multiple_series(self, series_ids: List[str]) -> Optional[Dict[str, List[Dict]]]:
        """Get multiple series."""
        results = {}
        for series_id in series_ids:
            data = self.get_series(series_id)
            if data:
                results[series_id] = data
        return results

    def get_latest_value(self, series_id: str) -> Optional[Dict]:
        """Get most recent value."""
        series = self.get_series(series_id)
        return series[0] if series else None

    def get_provider_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            "provider": "FRED",
            "status": "AVAILABLE" if not self.last_error else "DEGRADED",
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error
        }


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_market_adapter = None
_macro_adapter = None


def get_market_adapter() -> MarketDataAdapter:
    """Get market data adapter singleton."""
    global _market_adapter
    if _market_adapter is None:
        _market_adapter = MassiveAdapter()
    return _market_adapter


def get_macro_adapter() -> MacroDataAdapter:
    """Get macro data adapter singleton."""
    global _macro_adapter
    if _macro_adapter is None:
        _macro_adapter = FREDAdapter()
    return _macro_adapter
