"""A source fetching exchangerates from https://exchangerate.host.

Valid tickers are in the form "XXX-YYY", such as "EUR-CHF".

Here is the API documentation:
https://api.frankfurter.app/

For example:

https://api.frankfurter.app/latest?base=EUR&symbols=CHF


Timezone information: Input and output datetimes are specified via UTC
timestamps.
"""

from decimal import Decimal

import re
import requests
from dateutil.tz import tz
from dateutil.parser import parse

from beanprice import source


class RatesApiError(ValueError):
    "An error from the Rates API."

def _parse_ticker(ticker):
    """Parse the base and quote currencies from the ticker.

    Args:
      ticker: A string, the symbol in XXX-YYY format.
    Returns:
      A pair of (base, quote) currencies.
    """
    match = re.match(r'^(?P<base>\w+)-(?P<symbol>\w+)$', ticker)
    if not match:
        raise ValueError(
            'Invalid ticker. Use "BASE-SYMBOL" format.')
    return match.groups()

def _get_quote(ticker, date):
    """Fetch a exchangerate from ratesapi."""
    base, symbol = _parse_ticker(ticker)
    params = {
        'base': base,
        'symbol': symbol,
    }
    response = requests.get(url='https://api.frankfurter.app/' + date, params=params)

    if response.status_code != requests.codes.ok:
        raise RatesApiError("Invalid response ({}): {}".format(response.status_code,
                                                            response.text))

    result = response.json()

    price = Decimal(str(result['rates'][symbol]))
    time = parse(result['date']).replace(tzinfo=tz.tzutc())

    return source.SourcePrice(price, time, symbol)


class Source(source.Source):

    def get_latest_price(self, ticker):
        return _get_quote(ticker, 'latest')

    def get_historical_price(self, ticker, time):
        return _get_quote(ticker, time.date().isoformat())
