"""Fetch prices from US Government Thrift Savings Plan

As of 7 July 2020, the Thrift Savings Plan (TSP) rolled out a new
web site that has an API (instead of scraping a CSV). Unable to
find docs on the API. A web directory listing with various tools
is available at:

https://secure.tsp.gov/components/CORS/
"""

__copyright__ = "Copyright (C) 2020 Martin Blais"
__license__ = "GNU GPLv2"

import csv
from collections import OrderedDict
import datetime
from decimal import Decimal
import io

from curl_cffi import requests

from beanprice import source

# All of the TSP funds are in USD.
CURRENCY = "USD"

TIMEZONE = datetime.timezone(datetime.timedelta(hours=-4), "America/New_York")

TSP_FUND_NAMES = [
    "LInco",  # 0
    "L2030",  # 1
    "L2035",  # 2
    "L2040",  # 3
    "L2045",  # 4
    "L2050",  # 5
    "L2055",  # 6
    "L2060",  # 7
    "L2065",  # 8
    "L2070",  # 9
    "L2075",  # 10
    "GFund",  # 11
    "FFund",  # 12
    "CFund",  # 13
    "SFund",  # 14
    "IFund",  # 15
]

csv.register_dialect(
    "tsp",
    delimiter=",",
    quoting=csv.QUOTE_NONE,
    # NOTE(blais): This fails to import in 3.12 (and perhaps before).
    # quotechar='',
    lineterminator="\n",
)


class TSPError(ValueError):
    "An error from the Thrift Savings Plan (TSP) API."


def parse_tsp_csv(response: requests.models.Response) -> OrderedDict:
    """Parses a Thrift Savings Plan output CSV file.

    Function takes in a requests response and returns an
    OrderedDict with newest closing cost at front of OrderedDict.
    """

    data = OrderedDict()

    text = io.StringIO(response.text)

    reader = csv.DictReader(text, dialect="tsp")


    for row in reader:
        if not row["Date"]:
            continue
        # Date from TSP looks like "2020-02-28"
        date = datetime.datetime.strptime(row["Date"], "%Y-%m-%d")
        date = date.replace(hour=16, tzinfo=TIMEZONE)
        names = [
            "L Income",
            "L 2030",
            "L 2035",
            "L 2040",
            "L 2045",
            "L 2050",
            "L 2055",
            "L 2060",
            "L 2065",
            "L 2070",
            "L 2075",
            "G Fund",
            "F Fund",
            "C Fund",
            "S Fund",
            "I Fund",
        ]
        data[date] = [
            Decimal(row[name]) if row[name] else Decimal() for name in map(str.strip, names)
        ]

    return OrderedDict(sorted(data.items(), key=lambda t: t[0], reverse=True))


def parse_response(response: requests.models.Response) -> OrderedDict:
    """Process as response from TSP.

    Raises:
      TSPError: If there is an error in the response.
    """
    if not response.ok:
        raise TSPError("Error from TSP Parsing Status {}".format(response.status_code))

    return parse_tsp_csv(response)


class Source(source.Source):
    "US Thrift Savings Plan API Price Extractor"

    def get_latest_price(self, fund):
        """See contract in beanprice.source.Source."""
        return self.get_historical_price(fund, datetime.datetime.now())

    def get_historical_price(self, fund, time):
        """See contract in beanprice.source.Source."""
        if requests is None:
            raise TSPError("You must install the 'requests' library.")

        if fund not in TSP_FUND_NAMES:
            raise TSPError(
                "Invalid TSP Fund Name '{}'. Valid Funds are:\n\t{}".format(
                    fund, "\n\t".join(TSP_FUND_NAMES)
                )
            )

        if time.tzinfo is None:
            requested_date = time.date()
        else:
            requested_date = time.astimezone(TIMEZONE).date()

        url = "https://www.tsp.gov/data/fund-price-history.csv"
        payload = {
            # The endpoint currently returns its full history regardless of these
            # parameters. Keep supplying them in case its filtering is restored.
            "startdate": (requested_date - datetime.timedelta(days=14)).strftime(
                "%Y%m%d"
            ),
            "enddate": requested_date.strftime("%Y%m%d"),
            "download": "0",
            "Lfunds": "1",
            "InvFunds": "1",
        }

        response = requests.get(url, params=payload, impersonate="chrome")
        result = parse_response(response)
        try:
            trade_time, prices = next(
                (trade_time, prices)
                for trade_time, prices in result.items()
                if trade_time.date() <= requested_date
            )
        except StopIteration as exc:
            raise TSPError(
                "No TSP prices available on or before {}.".format(
                    requested_date.isoformat()
                )
            ) from exc

        try:
            price = prices[TSP_FUND_NAMES.index(fund)]
        except KeyError as exc:
            raise TSPError("Invalid response from TSP: {}".format(repr(result))) from exc

        return source.SourcePrice(price, trade_time, CURRENCY)
