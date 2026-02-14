"""Fetch prices from markets.ft.com.

This source uses Financial Times JSON API to fetch prices.
It requires an internal FT ID (xid) which is extracted from the tearsheet page.
"""

__copyright__ = "Copyright (C) 2026  Roman Medvedev"
__license__ = "GNU GPLv2"

import datetime
from decimal import Decimal
import json
import re
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Optional, Dict, Any

from beanprice import source

class FTError(ValueError):
    """An error from the FT source."""

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def get_url(url: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Fetch content from a URL using urllib."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {
        "User-Agent": _USER_AGENT,
        "Accept": "application/json, text/plain, */*",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as exc:
        raise FTError(f"Network error fetching {url}: {exc}") from exc

def post_json(url: str, data: Dict[str, Any]) -> str:
    """Post JSON data to a URL using urllib."""
    headers = {
        "User-Agent": _USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
    }
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as exc:
        raise FTError(f"Network error posting to {url}: {exc}") from exc

class Source(source.Source):
    """Financial Times price extractor."""

    def __init__(self):
        self._xid_cache = {}

    def _get_xid(self, ticker: str) -> str:
        """Get the internal FT ID (xid) for a ticker."""
        if ticker in self._xid_cache:
            return self._xid_cache[ticker]

        url = f"https://markets.ft.com/data/equities/tearsheet/summary?s={ticker}"
        content = get_url(url)

        # Look for xid followed by colon/equals, optional quotes, and digits
        pattern = (
            r'(?:xid|&quot;xid&quot;)\s*[:=]\s*'
            r'(?:["\']|&quot;)?(\d+)(?:["\']|&quot;)?'
        )
        match = re.search(pattern, content)
        if not match:
            raise FTError(f"Could not determine internal FT ID for ticker {ticker}")

        xid = match.group(1)
        self._xid_cache[ticker] = xid
        return xid

    def _fetch_history(self, ticker: str, days: int) -> List[Dict[str, Any]]:
        """Fetch historical series from FT."""
        xid = self._get_xid(ticker)
        url = "https://markets.ft.com/data/chartapi/series"

        payload = {
            "days": days,
            "dataNormalized": False,
            "dataPeriod": "Day",
            "dataInterval": 1,
            "realtime": False,
            "yFormat": "0.###",
            "timeServiceFormat": "JSON",
            "returnDateType": "ISO8601",
            "elements": [
                {"Type": "price", "Symbol": xid}
            ]
        }

        response_text = post_json(url, payload)
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise FTError(f"Invalid JSON response from FT for {ticker}: {exc}") from exc

        dates = data.get("Dates", [])
        elements = data.get("Elements", [])
        if not dates or not elements:
            return []

        price_comp = next((e for e in elements if e.get("Type") == "price"), None)
        if not price_comp:
            return []

        ohlc = price_comp.get("ComponentSeries", [])
        # Provide default empty list if "Values" missing
        closes: List[Any] = next(
            (s.get("Values", []) for s in ohlc if s.get("Type") == "Close"), []
        )

        history = []
        for i, d_str in enumerate(dates):
            if i < len(closes) and closes[i] is not None:
                # FT dates are like "2025-12-29T00:00:00"
                try:
                    date_time = datetime.datetime.fromisoformat(d_str).replace(
                        tzinfo=datetime.timezone.utc
                    )
                    history.append({
                        "time": date_time,
                        "price": Decimal(str(closes[i]))
                    })
                except ValueError:
                    continue  # Skip invalid dates
        return history

    def get_latest_price(self, ticker: str) -> Optional[source.SourcePrice]:
        """Fetch the current latest price."""
        try:
            # Fetch last 5 days to ensure we get a price (weekends)
            history = self._fetch_history(ticker, 5)
            if not history:
                return None

            latest = history[-1]
            return source.SourcePrice(latest["price"], latest["time"], None)
        except FTError as error:
            raise FTError("%s (ticker: %s)" % (error, ticker)) from error
        except Exception as exc:
            raise FTError("Unexpected error for ticker %s: %s" % (ticker, exc)) from exc

    def get_historical_price(
        self, ticker: str, time: datetime.datetime
    ) -> Optional[source.SourcePrice]:
        """Return the latest historical price found for the symbol at the given date."""
        try:
            # Normalize 'time' to be timezone-aware (UTC) if it isn't already.
            if time.tzinfo is None:
                time = time.replace(tzinfo=datetime.timezone.utc)

            # API 'days' is lookback from today.
            days_diff = (datetime.datetime.now(datetime.timezone.utc) - time).days + 7
            days_diff = max(days_diff, 1)

            # Fetch history
            history = self._fetch_history(ticker, max(days_diff, 30))
            if not history:
                return None

            # Sort history just in case API returns unsorted (unlikely but safe)
            history.sort(key=lambda x: x["time"])

            best_match = {}
            for entry in reversed(history):
                if entry["time"] <= time:
                    best_match = entry
                    break

            if best_match:
                # Check if it's within a reasonable range (e.g. 7 days as in ft.py base)
                if (time - best_match["time"]).days <= 7:
                    return source.SourcePrice(best_match["price"], best_match["time"], None)

            return None
        except FTError as error:
            raise FTError("%s (ticker: %s)" % (error, ticker)) from error
        except Exception as exc:
            raise FTError(
                "Unexpected error for ticker %s at %s: %s" % (ticker, time, exc)
            ) from exc
