"""Fetch prices from Yahoo Finance's CSV API.

As of late 2017, the older Yahoo finance API deprecated. In particular, the
ichart endpoint is gone, and the download endpoint requires a cookie (which
could be gotten - here's some documentation for that
http://blog.bradlucas.com/posts/2017-06-02-new-yahoo-finance-quote-download-url/).

We're using both the v7 and v8 APIs here, both of which are, as far as I can
tell, undocumented:

https://query1.finance.yahoo.com/v7/finance/quote
https://query1.finance.yahoo.com/v8/finance/chart/SYMBOL

Timezone information: Input and output datetimes are specified via UNIX
timestamps, but the timezone of the particular market is included in the output.
"""
__copyright__ = "Copyright (C) 2015-2020  Martin Blais"
__license__ = "GNU GPLv2"

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

from beanprice import source

class YahooError(ValueError):
    "An error from the Yahoo API."


def _requestor(*args, **kwargs):
    if "headers" not in kwargs:
        kwargs["headers"] = {}
    # Yahoo! balks without this header.
    kwargs["headers"]["User-Agent"] = (
        "Mozilla/5.0 (X11; Linux x86_64; "
        "rv:109.0) Gecko/20100101 Firefox/110.0"
    )
    response = requests.get(*args, **kwargs)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise YahooError(
            "HTTP status {}: {}".format(
                response.status_code,
                response.text(),
            )
        ) from exc
    return response


def parse_response(response: requests.models.Response) -> Dict:
    """Process as response from Yahoo.

    Assumes the response code is among the OK response codes.

    Raises:
      YahooError: If there is an error in the response.
    """
    json = response.json(parse_float=Decimal)
    content = next(iter(json.values()))
    if len(json) != 1:
        raise YahooError("Invalid format in response from Yahoo; many keys: {}".format(
            ','.join(json.keys())))
    if content['error'] is not None:
        raise YahooError("Error fetching Yahoo data: {}".format(content['error']))
    return content['result'][0]


# Note: Feel free to suggest more here via a PR.
_MARKETS = {
    'us_market': 'USD',
    'ca_market': 'CAD',
}


def parse_currency(result: Dict[str, Any]) -> Optional[str]:
    """Infer the currency from the result."""
    if 'market' not in result:
        return None
    return _MARKETS.get(result['market'], None)


_DEFAULT_PARAMS = {
    'lang': 'en-US',
    'corsDomain': 'finance.yahoo.com',
    '.tsrc': 'finance',
}


def get_price_series(ticker: str,
                     time_begin: datetime,
                     time_end: datetime) -> Tuple[List[Tuple[datetime, Decimal]], str]:
    """Return a series of timestamped prices."""

    if requests is None:
        raise YahooError("You must install the 'requests' library.")
    url = "https://query1.finance.yahoo.com/v8/finance/chart/{}".format(ticker)
    payload: Dict[str, Union[int, str]] = {
        'period1': int(time_begin.timestamp()),
        'period2': int(time_end.timestamp()),
        'interval': '1d',
    }
    payload.update(_DEFAULT_PARAMS)
    response = _requestor(url, params=payload)
    try:
        result = parse_response(response)
    except IndexError as exc:
        raise YahooError(
            (
                "Could not destructure price series for ticker {}: "
                "the content contains zero-length result"
            ).format(ticker)
        ) from exc

    meta = result['meta']
    tzone = timezone(timedelta(hours=meta['gmtoffset'] / 3600),
                     meta['exchangeTimezoneName'])

    if 'timestamp' not in result:
        raise YahooError(
            "Yahoo returned no data for ticker {} for time range {} - {}".format(
                ticker, time_begin, time_end))

    timestamp_array = result['timestamp']
    close_array = result['indicators']['quote'][0]['close']
    series = [(datetime.fromtimestamp(timestamp, tz=tzone), Decimal(price))
              for timestamp, price in zip(timestamp_array, close_array)]

    currency = result['meta']['currency']
    return series, currency


class Source(source.Source):
    "Yahoo Finance CSV API price extractor."

    def get_latest_price(self, ticker: str) -> Optional[source.SourcePrice]:
        """See contract in beanprice.source.Source."""

        url = "https://query1.finance.yahoo.com/v7/finance/quote"
        fields = ['symbol', 'regularMarketPrice', 'regularMarketTime']
        payload = {
            'symbols': ticker,
            'fields': ','.join(fields),
            'exchange': 'NYSE',
        }
        payload.update(_DEFAULT_PARAMS)
        response = _requestor(url, params=payload)
        try:
            result = parse_response(response)
        except IndexError as exc:
            raise YahooError(
                (
                    "Could not destructure latest price for ticker {}: "
                    "the content contains zero-length result"
                ).format(ticker)
            ) from exc
        try:
            price = Decimal(result['regularMarketPrice'])

            tzone = timezone(
                timedelta(hours=result['gmtOffSetMilliseconds'] / 3600000),
                result['exchangeTimezoneName'])
            trade_time = datetime.fromtimestamp(result['regularMarketTime'],
                                                tz=tzone)
        except KeyError as exc:
            raise YahooError("Invalid response from Yahoo: {}".format(
                repr(result))) from exc

        currency = parse_currency(result)

        return source.SourcePrice(price, trade_time, currency)

    def get_historical_price(self, ticker: str,
                             time: datetime) -> Optional[source.SourcePrice]:
        """See contract in beanprice.source.Source."""

        # Get the latest data returned over the last 5 days.
        series, currency = get_price_series(ticker, time - timedelta(days=5), time)
        latest = None
        for data_dt, price in sorted(series):
            if data_dt >= time:
                break
            latest = data_dt, price
        if latest is None:
            raise YahooError("Could not find price before {} in {}".format(time, series))

        return source.SourcePrice(price, data_dt, currency)

    def get_daily_prices(self,
                         ticker: str,
                         time_begin: datetime,
                         time_end: datetime) -> Optional[List[source.SourcePrice]]:
        """See contract in beanprice.source.Source."""
        series, currency = get_price_series(ticker, time_begin, time_end)
        return [source.SourcePrice(price, time, currency)
                for time, price in series]
