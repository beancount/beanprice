"""A source fetching exchange rates and crypto prices from UniRateAPI.

UniRateAPI (https://unirateapi.com) is a currency-and-crypto exchange-rates
service with a free tier covering latest rates and conversion across ~170
fiat currencies and major crypto. Historical rates and timeseries are
available on the Pro plan.

Set your API key in the environment variable UNIRATE_API_KEY.

Valid tickers are in the form "BASE-QUOTE", e.g. "USD-EUR" or "BTC-USD".
The price returned is the value of one unit of BASE expressed in QUOTE.

The API documentation is at https://unirateapi.com/docs.

For example:
https://api.unirateapi.com/api/rates?from=USD&to=EUR&api_key=...
https://api.unirateapi.com/api/historical/rates?date=2024-06-15&from=USD&to=EUR&api_key=...

Timezone information: latest prices are stamped with the current UTC time;
historical prices are stamped at midnight UTC of the requested date.
"""

import datetime
import re
from decimal import Decimal
from os import environ

import requests
from dateutil.tz import tz

from beanprice import source


class UniRateError(ValueError):
    "An error from the UniRateAPI."


def _parse_ticker(ticker):
    """Parse the base and quote currencies from the ticker.

    Args:
      ticker: A string in BASE-QUOTE format.
    Returns:
      A (base, quote) tuple of currency codes.
    """
    match = re.match(r"^(?P<base>\w+)-(?P<quote>\w+)$", ticker)
    if not match:
        raise ValueError('Invalid ticker. Use "BASE-QUOTE" format, e.g. "USD-EUR".')
    return match.group("base"), match.group("quote")


def _get_api_key():
    try:
        return environ["UNIRATE_API_KEY"]
    except KeyError as exc:
        raise UniRateError(
            "Missing required environment variable UNIRATE_API_KEY"
        ) from exc


def _get(path, params):
    params = dict(params)
    params["api_key"] = _get_api_key()
    url = "https://api.unirateapi.com" + path
    # /api/currencies returns HTML 404 without an explicit JSON Accept header;
    # set it on every request for consistency.
    response = requests.get(url, params=params, headers={"Accept": "application/json"})
    if response.status_code == 403:
        raise UniRateError(
            "UniRateAPI returned 403: this endpoint requires a Pro subscription"
        )
    if response.status_code != requests.codes.ok:
        raise UniRateError(
            "Invalid response ({}): {}".format(response.status_code, response.text)
        )
    return response.json()


def _extract_rate(data):
    if "rate" not in data:
        raise UniRateError("Unexpected response shape: {}".format(data))
    return Decimal(str(data["rate"]))


class Source(source.Source):
    "UniRateAPI price extractor."

    def get_latest_price(self, ticker):
        base, quote = _parse_ticker(ticker)
        data = _get("/api/rates", {"from": base, "to": quote})
        price = _extract_rate(data)
        time = datetime.datetime.now(tz.tzutc())
        return source.SourcePrice(price, time, quote)

    def get_historical_price(self, ticker, time):
        base, quote = _parse_ticker(ticker)
        date = time.astimezone(tz.tzutc()).date()
        data = _get(
            "/api/historical/rates",
            {"date": date.isoformat(), "from": base, "to": quote},
        )
        price = _extract_rate(data)
        timestamp = datetime.datetime.combine(
            date, datetime.time.min, tzinfo=tz.tzutc()
        )
        return source.SourcePrice(price, timestamp, quote)
