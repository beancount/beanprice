"""Fetch prices from the https://api.portfolio-report.net API.

The symbols must be referred to by the symbol's UUID and the desired currency in
the format "<UUID>:<CURRENCY>".  The symbol's UUIDs can be looked up here:
https://www.portfolio-report.net/search

Timezone information: Input and output datetimes are limited to dates, and I
believe the dates are presumed to be UTC (It's unclear, not documented.)
"""

import datetime
from decimal import Decimal
from typing import List, Tuple

import requests

from beanprice import source


class PortfolioreportError(ValueError):
    "An error from the portfolio-report.net API."


def _get_price_series(
    ticker: str,
    currency: str,
    time_begin: datetime.datetime = datetime.datetime.min,
    time_end: datetime.datetime = datetime.datetime.max,
) -> List[source.SourcePrice]:
    base_url = \
        f"https://api.portfolio-report.net/securities/uuid/{ticker}/prices/{currency}"

    query = {}
    if time_begin != datetime.datetime.min:
        query = {
            'from': time_begin.date().isoformat(),
        }
    response = requests.get(base_url, params=query)
    if response.status_code != requests.codes.ok:
        raise PortfolioreportError(
            f"Invalid response ({response.status_code}): {response.text}"
        )
    response_data = response.json()

    def to_decimal(val: float) -> Decimal:
        return Decimal(str(val)).quantize(Decimal('0.00000000'))

    ret = []
    for entry in response_data:
        date = datetime.datetime.fromisoformat(entry['date']).date()
        if date < time_begin.date() or date > time_end.date():
            continue
        ret.append(source.SourcePrice(
            price=to_decimal(entry['close']),
            time=datetime.datetime(
                date.year,
                date.month,
                date.day,
                tzinfo=datetime.timezone.utc,
            ),
            quote_currency=currency
        ))
    return ret


def _parse_ticker(ticker: str) -> Tuple[str, str]:
    if ticker.count(':') != 1:
        raise PortfolioreportError('ticker must be in the format "UUID:CURRENCY"')
    parts = ticker.split(':', maxsplit=1)
    return parts[0], parts[1]


class Source(source.Source):
    def get_latest_price(self, ticker):
        uuid, currency = _parse_ticker(ticker)
        prices = _get_price_series(uuid, currency)
        if len(prices) < 1:
            return None
        return prices[-1]

    def get_historical_price(self, ticker, time):
        uuid, currency = _parse_ticker(ticker)
        prices = _get_price_series(uuid, currency, time)
        if len(prices) < 1:
            return None
        return prices[0]

    def get_prices_series(self, ticker, time_begin, time_end):
        uuid, currency = _parse_ticker(ticker)
        prices = _get_price_series(uuid, currency, time_begin, time_end)
        if len(prices) < 1:
            return None
        return prices
