"""A source fetching prices and exchangerates from https://www.alphavantage.co.

It requires a free api key which needs to be set in the
environment variable "ALPHAVANTAGE_API_KEY"

Valid tickers for prices are in the form "price:XXX:YYY", such as "price:IBM:USD"
where XXX is the symbol and YYY is the expected quote currency in which the data
is returned. The api currently does not support converting to a specific ccy and
does unfortunately not return in which ccy the result is.

Valid tickers for exchangerates are in the form "fx:XXX:YYY", such as "fx:USD:CHF".

Here is the API documentation:
https://www.alphavantage.co/documentation/

For example:


https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo

https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=JPY&apikey=demo

"""

from decimal import Decimal

import re
from os import environ
from time import sleep
import requests
from dateutil.tz import tz
from dateutil.parser import parse

from beanprice import source


class AlphavantageApiError(ValueError):
    "An error from the Alphavantage API."


def _parse_ticker(ticker):
    """Parse the base and quote currencies from the ticker.

    Args:
      ticker: A string, the symbol in kind-XXX-YYY format.
    Returns:
      A (kind, symbol, base) tuple.
    """
    match = re.match(r"^(?P<kind>price|fx):(?P<symbol>[^:]+):(?P<base>\w+)$", ticker)
    if not match:
        raise ValueError('Invalid ticker. Use "price:SYMBOL:BASE" or "fx:CCY:BASE" format.')
    return match.groups()


def _do_fetch(params):
    params["apikey"] = environ["ALPHAVANTAGE_API_KEY"]

    resp = requests.get(url="https://www.alphavantage.co/query", params=params)
    data = resp.json()
    # This is for dealing with the rate limit, sleep for 60 seconds and then retry
    if "Note" in data:
        sleep(60)
        resp = requests.get(url="https://www.alphavantage.co/query", params=params)
        data = resp.json()

    if resp.status_code != requests.codes.ok:
        raise AlphavantageApiError(
            "Invalid response ({}): {}".format(resp.status_code, resp.text)
        )

    if "Error Message" in data:
        raise AlphavantageApiError("Invalid response: {}".format(data["Error Message"]))

    return data


class Source(source.Source):
    def get_latest_price(self, ticker):
        kind, symbol, base = _parse_ticker(ticker)

        if kind == "price":
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
            }
            data = _do_fetch(params)

            price_data = data["Global Quote"]
            price = Decimal(price_data["05. price"])
            date = parse(price_data["07. latest trading day"]).replace(tzinfo=tz.tzutc())
        else:
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": symbol,
                "to_currency": base,
            }
            data = _do_fetch(params)

            price_data = data["Realtime Currency Exchange Rate"]
            price = Decimal(price_data["5. Exchange Rate"])
            date = parse(price_data["6. Last Refreshed"]).replace(
                tzinfo=tz.gettz(price_data["7. Time Zone"])
            )

        return source.SourcePrice(price, date, base)

    def get_historical_price(self, ticker, time):
        return None
