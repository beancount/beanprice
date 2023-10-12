"""A source fetching exchange rates using European Central Bank's datasets

This source leverages daily avarage rates to/from EUR. For other currency pairs
the final rate is derived by dividing rates to/from EUR.

Valid tickers are in the form "XXX-YYY", such as "EUR-CHF", which denotes rate EUR->CHF

Here is the API documentation:
https://data.ecb.europa.eu/help/api/overview

Timezone information: Input and output datetimes are specified via UTC
timestamps.
"""

from decimal import Decimal, getcontext

import re
import requests
import csv
from dateutil.tz import tz
from dateutil.parser import parse
from io import StringIO

from beanprice import source
from beanprice.price import now

class ECBRatesError(ValueError):
    "An error from the ECB Rates."

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

def _get_rate_EUR_to_CCY(currency, date):
    # Temporarily uses fixed precision
    getcontext().prec = 5
    
    # Return consatant rate for EUR
    if currency == 'EUR':
        return Decimal('1')

    # Call API
    symbol = f"D.{currency}.EUR.SP00.A"
    params = {
        "startPeriod": date,
        "endPeriod": date,
        "format": "csvdata",
        "detail": "full",
        }
    url = f"https://data-api.ecb.europa.eu/service/data/EXR/{symbol}"
    response = requests.get(url, params=params)
    if response.status_code != requests.codes.ok:
        raise ECBRatesError(f"Invalid response ({response.status_code}): {response.text}")

    # Parse results to a DictReader iterator
    results = csv.DictReader(StringIO(response.text))

    # Retrieve exchange rate
    try:
        observation = next(results)
    except StopIteration:
        # When there's no data for a given date, an empty string is returned
        return None
    else:
        # Checking only the first observation and raising errors if there's a date mismatch
        rate = observation.get("OBS_VALUE")
        obs_date = observation.get("TIME_PERIOD")
        decimals = observation.get("DECIMALS")
        if obs_date != date:
            raise ECBRatesError(f"Requested rate for {date}, received for {obs_date}")
        return Decimal(rate)

def _get_quote(ticker, date):
    base, symbol = _parse_ticker(ticker)

    # Get EUR rates by calling the API 
    EUR_to_base = _get_rate_EUR_to_CCY(base, date)
    EUR_to_symbol = _get_rate_EUR_to_CCY(symbol, date)

    # Calculate base -> symbol
    if EUR_to_symbol is None or EUR_to_base is None:
        return None
    else:
        price = EUR_to_symbol / EUR_to_base
        time = parse(date).replace(tzinfo=tz.tzutc())
        return source.SourcePrice(price, time, symbol)


class Source(source.Source):

    def get_latest_price(self, ticker):
        return _get_quote(ticker, now().date().isoformat())

    def get_historical_price(self, ticker, time):
        return _get_quote(ticker, time.date().isoformat())
