"""
A source fetching cryptocurrency prices from Coincap.

Tickers can be in two formats: Either using the coincap currency id (bitcoin,
ethereum, etc.), or using a currency ticker (BTC, ETH, etc.). In the latter
case, any ambiguity will be resolved using the coin ranking.

Prices are denoted in USD.

The documentation can be found here:
https://docs.coincap.io/

"""

import datetime
import math
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
import requests
from beanprice import source

API_BASE_URL = 'https://api.coincap.io/v2/'


class CoincapError(ValueError):
    "An error from the Coincap importer."


def get_asset_list() -> List[Dict[str, str]]:
    """
    Get list of currencies supported by Coincap. Returned is a list with
    elements with many properties, including "id", representing the Coincap id,
    and "symbol", representing the ticker symbol.
    """
    path = 'assets/'
    url = API_BASE_URL + path
    response = requests.get(url)
    data = response.json()['data']
    return data


def get_currency_id(currency: str) -> Optional[str]:
    """
    Find currency ID by its symbol.
    If results are ambiguous, select currency with the highest market cap
    """
    # Array is already sorted based on market cap
    for coin in get_asset_list():
        if coin['symbol'] == currency:
            return coin['id']
    return None


def resolve_currency_id(base_currency: str) -> str:
    """
    Obtain the currency ID from the ticker, which can either already be a
    currency id (bitcoin), or a coin ticker (BTC).
    """
    if base_currency.isupper():
        # Try to find currency ID by its symbol
        base_currency_id = get_currency_id(base_currency)
        if not isinstance(base_currency_id, str):
            raise CoincapError("Could not find currency id with ticker '"
                               + base_currency + "'")
        return base_currency_id
    else:
        return base_currency


def get_latest_price(base_currency: str) -> Tuple[float, float]:
    path = 'assets/'
    url = API_BASE_URL + path + resolve_currency_id(base_currency)
    response = requests.get(url)
    data = response.json()
    timestamp = data['timestamp'] / 1000.0
    price_float = data['data']['priceUsd']
    return price_float, timestamp


def get_price_series(base_currency_id: str, time_begin: datetime.datetime,
                     time_end: datetime.datetime) -> List[source.SourcePrice]:
    path = 'assets/{}/history'.format(base_currency_id)
    params = {
        'interval': 'd1',
        'start': str(math.floor(time_begin.timestamp() * 1000.0)),
        'end': str(math.ceil(time_end.timestamp() * 1000.0))
    }
    url = API_BASE_URL + path
    response = requests.get(url, params=params)
    return [source.SourcePrice(
        Decimal(item['priceUsd']),
        datetime.datetime.fromtimestamp(
            item['time'] / 1000.0).replace(tzinfo=datetime.timezone.utc),
        'USD'
    )
        for item in response.json()['data']]


class Source(source.Source):
    """A price source for the Coincap API v2. Supports only prices denoted in USD.
    There are two ways of expressing a ticker, either by their coincap id (bitcoin)
    or by their ticker (BTC), in which case the highest ranked coin will be picked."""

    def get_latest_price(self, ticker) -> source.SourcePrice:
        price_float, timestamp = get_latest_price(ticker)
        price = Decimal(price_float)
        price_time = datetime.datetime.fromtimestamp(timestamp).\
            replace(tzinfo=datetime.timezone.utc)
        return source.SourcePrice(price, price_time, 'USD')

    def get_historical_price(self, ticker: str,
                             time: datetime.datetime) -> Optional[source.SourcePrice]:
        for datapoint in self.get_prices_series(ticker,
                                                time +
                                                datetime.timedelta(days=-1),
                                                time + datetime.timedelta(days=1)):
            if datapoint.time is not None and datapoint.time.date() == time.date():
                return datapoint
        return None

    def get_prices_series(self, ticker: str,
                          time_begin: datetime.datetime,
                          time_end: datetime.datetime
                          ) -> List[source.SourcePrice]:
        return get_price_series(resolve_currency_id(ticker), time_begin, time_end)
