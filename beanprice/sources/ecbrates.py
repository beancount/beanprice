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
import csv
from io import StringIO
from dateutil.tz import tz
from dateutil.parser import parse
import requests

from beanprice import source


class ECBRatesError(ValueError):
    "An error from the ECB Rates."


def _parse_ticker(ticker):
    """Parse the base and quote currencies from the ticker.

    Args:
      ticker: A string, the symbol in XXX-YYY format.
    Returns:
      A pair of (base, quote) currencies.
    """
    match = re.match(r"^(?P<base>\w+)-(?P<symbol>\w+)$", ticker)
    if not match:
        raise ValueError('Invalid ticker. Use "BASE-SYMBOL" format.')
    return match.groups()


def _get_rate_EUR_to_CCY(currency, date):
    # Call API
    symbol = f"D.{currency}.EUR.SP00.A"
    params = {"format": "csvdata", "detail": "full", "lastNObservations": 1}
    if date is not None:
        params["endPeriod"] = date
    url = f"https://data-api.ecb.europa.eu/service/data/EXR/{symbol}"
    response = requests.get(url, params=params)
    if response.status_code != requests.codes.ok:
        raise ECBRatesError(
            f"Invalid response ({response.status_code}): {response.text}"
        )

    # Parse results to a DictReader iterator
    results = csv.DictReader(StringIO(response.text))

    # Retrieve exchange rate
    try:
        observation = next(results)
    except StopIteration:
        # When there's no data for a given date, an empty string is returned
        return None, None, None
    else:
        # Checking only the first observation and raising errors if there's a date mismatch
        rate = observation.get("OBS_VALUE")
        obs_date = observation.get("TIME_PERIOD")
        decimals = observation.get("DECIMALS")
        precision = int(decimals) + len(rate.split(".")[0].lstrip("0"))
        return Decimal(rate), obs_date, precision


def _get_quote(ticker, date):
    base, symbol = _parse_ticker(ticker)

    if base == symbol:
        raise ECBRatesError(
            f"Base currency {base} must be different than symbol currency {symbol}"
        )

    # Get EUR rates by calling the API (or use defaults)
    if base == "EUR" and symbol != "EUR":
        eur_to_symbol, symbol_rate_date, symbol_rate_precision = _get_rate_EUR_to_CCY(
            symbol, date
        )
        eur_to_base = Decimal(1)
        base_rate_date = symbol_rate_date
        base_rate_precision = 28
    elif base != "EUR" and symbol == "EUR":
        eur_to_base, base_rate_date, base_rate_precision = _get_rate_EUR_to_CCY(
            base, date
        )
        eur_to_symbol = Decimal(1)
        symbol_rate_date = base_rate_date
        symbol_rate_precision = 28
    else:
        eur_to_base, base_rate_date, base_rate_precision = _get_rate_EUR_to_CCY(
            base, date
        )
        eur_to_symbol, symbol_rate_date, symbol_rate_precision = _get_rate_EUR_to_CCY(
            symbol, date
        )

    # Raise error if retrieved subrates for differnt dates
    if base_rate_date != symbol_rate_date:
        raise ECBRatesError(
            f"Subrates for different dates: ({base}, {base_rate_date}) \
vs. ({symbol}, {symbol_rate_date})"
        )

    # Calculate base -> symbol
    if eur_to_symbol is None or eur_to_base is None:
        raise ECBRatesError(
            f"At least one of the subrates returned None: \
(EUR{symbol}: {eur_to_symbol}, EUR{base}: {eur_to_base})"
        )

    # Derive precision from sunrates (must be at least 5)
    minimal_precision = 5
    getcontext().prec = max(
        minimal_precision, min(base_rate_precision, symbol_rate_precision)
    )
    price = eur_to_symbol / eur_to_base
    time = parse(base_rate_date).replace(tzinfo=tz.tzutc())
    return source.SourcePrice(price, time, symbol)


class Source(source.Source):

    def get_latest_price(self, ticker):
        return _get_quote(ticker, None)

    def get_historical_price(self, ticker, time):
        return _get_quote(ticker, time.date().isoformat())
