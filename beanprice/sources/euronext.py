"""Fetch prices from the Euronext website.

This doesn't use the API, just the ablity to download a CSV with historical
prices. As such, it does not require an API key.
"""

import datetime
import re
from zoneinfo import ZoneInfo
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import requests

from beanprice import source

cet = ZoneInfo("CET")

REGEX_PATTERN = (r"^'?(\d\d)\/(\d\d)\/(\d\d\d\d);"
    r"'?(\d+.?\d+);"
    r"'?\d+.?\d+;"
    r"'?\d+.?\d+;"
    r"'?\d+.?\d+;"
    r"'?\d+.?\d+;"
    r"'?\d+;"
    r"'?\d+;"
    r"'?\d+;"
    r"('?\d+(.\d+)?)?$")

class EuronextError(ValueError):
    "Prices could not be fetched"


# We store the known prices here. This may be None, if we know the date does
# not have a price.
known_prices: Dict[str, List[source.SourcePrice]] = {}

# Since we store the known prices, we should also cache which ranges we have
# obtained. This is because even for queried dates, the price may not exist
# and we should not try again.
queried_ranges: List[Tuple[datetime.datetime, datetime.datetime]] = []

"""Get the key to be used in the known prices dict."""


def known_prices_key(ticker: str, date: datetime.date) -> str:
    return ticker + "__" + date.isoformat()

def date_to_exchange_time(date: datetime.date) -> datetime.datetime:
    # We do not obtain times for the fetching. Since this is a European
    # source, take an early time as a good-enough solution. This way, any
    # time after opening of the exchange will yield today's price (opening
    # times may vary), while we are unlikely to obtain tomorrows price.
    return datetime.datetime(date.year, date.month, date.day, 5, 0, tzinfo=cet)

def parse_ticker_line(line: str) -> Optional[source.SourcePrice]:
    if not line:
        return None
    match_result = re.search(REGEX_PATTERN, line)
    if match_result is None:
        raise EuronextError("could not parse response")
    date = datetime.date(
        int(match_result.group(3)),
        int(match_result.group(2)),
        int(match_result.group(1)),
    )
    price = Decimal(match_result.group(4))

    date_with_time = date_to_exchange_time(date)
    return source.SourcePrice(price, date_with_time, "EUR")

def read_csv(contents: str, ticker: str):
    lines = contents.splitlines()
    # Sanity checking
    assert lines[0].endswith('"Historical Data"')
    assert ticker.startswith(lines[2])

    # Get the date range used
    match_result = re.search(
        r'^"From (\d\d)\/(\d\d)\/(\d\d\d\d) to (\d\d)\/(\d\d)\/(\d\d\d\d)"$', lines[1]
    )
    if match_result is None:
        raise EuronextError("could not parse response")

    from_date = datetime.date(
        int(match_result.group(3)),
        int(match_result.group(2)),
        int(match_result.group(1)),
    )
    # Exclusive date!
    until_date = datetime.date(
        int(match_result.group(6)),
        int(match_result.group(5)),
        int(match_result.group(4)),
    )
    queried_ranges.append(
        (date_to_exchange_time(from_date), date_to_exchange_time(until_date))
    )

    # Parse included dates
    for line in lines[4:]:
        sourceprice = parse_ticker_line(line)
        if not sourceprice is None:
            known_prices[ticker].append(sourceprice)

class Source(source.Source):
    "Euronext price source."

    def get_latest_price(self, ticker: str) -> Optional[source.SourcePrice]:
        """We attempt to get the latest price through the historical price function."""
        return self.get_historical_price(ticker.upper(), datetime.datetime.now())

    def get_historical_price(
        self, ticker: str, time: datetime.datetime
    ) -> Optional[source.SourcePrice]:
        # Capitalize
        ticker = ticker.upper()
        time = time.replace(tzinfo=ZoneInfo("localtime"))

        # Initialize the dict
        if not ticker in known_prices:
            known_prices[ticker] = []

        # If the date has not already been queried, download.
        if not any(start <= time < end for start, end in queried_ranges):
            # Although there is a from and until date parameter, this is simply
            # ignored: in practice we always obtain the last two years.
            url = f"https://live.euronext.com/nl/ajax/AwlHistoricalPrice/\
getFullDownloadAjax/{ticker}?format=csv&decimal_separator=.&date_form=d/m/Y"
            response = requests.get(url, timeout=10)
            if response.status_code != requests.codes.ok:
                raise EuronextError("request failed")
            read_csv(response.text, ticker)

        # Find the closest price.
        closest: Optional[source.SourcePrice] = None
        for price in known_prices[ticker]:
            # These conditions look somewhat involved to satisfy type checking.
            # We only assert that the datetime is always defined, since we
            # create SourcePrice's ourselves, so we know this to be true.
            assert not price[1] is None
            if price[1] > time:
                continue
            if closest is None:
                closest = price
            assert not closest[1] is None
            if price[1] > closest[1]:
                closest = price

        return closest
