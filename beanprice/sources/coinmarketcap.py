"""A source fetching cryptocurrency prices from Coinmarketcap.

Valid tickers are in the form "XXX-YYY", such as "BTC-CHF".

It requires a free api key which needs to be set in the
environment variable "COINMARKETCAP_API_KEY"

Here is the API documentation:
https://coinmarketcap.com/api/documentation/v1/
"""

from decimal import Decimal
import re
from os import environ
import requests
from dateutil.parser import parse
from beanprice import source


class CoinmarketcapApiError(ValueError):
    "An error from the CoinMarketCap API."


def _parse_ticker(ticker):
    """Parse the base and quote currencies from the ticker.

    Args:
      ticker: A string, the symbol in XXX-YYY format.
    Returns:
      A pair of (base, quote) currencies.
    """
    match = re.match(r'^(?P<symbol>\w+)-(?P<base>\w+)$', ticker)
    if not match:
        raise ValueError(
            'Invalid ticker. Use "BASE-SYMBOL" format.')
    return match.groups()


class Source(source.Source):

    def get_latest_price(self, ticker):
        symbol, base = _parse_ticker(ticker)
        headers = {
            'X-CMC_PRO_API_KEY': environ['COINMARKETCAP_API_KEY'],
        }
        params = {
            'symbol': symbol,
            'convert': base,
        }

        resp = requests.get(
            url='https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
            params=params, headers=headers)
        if resp.status_code != requests.codes.ok:
            raise CoinmarketcapApiError(
                "Invalid response ({}): {}".format(resp.status_code, resp.text)
            )
        data = resp.json()
        if data['status']['error_code'] != 0:
            status = data['status']
            raise CoinmarketcapApiError(
                "Invalid response ({}): {}".format(
                    status['error_code'], status['error_message'])
            )

        quote = data['data'][symbol]['quote'][base]
        price = Decimal(str(quote['price']))
        date = parse(quote['last_updated'])

        return source.SourcePrice(price, date, base)

    def get_historical_price(self, ticker, time):
        return None
