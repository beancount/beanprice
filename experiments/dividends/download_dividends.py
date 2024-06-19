#!/usr/bin/env python3
"""Download all dividends in a particular date interval."""

__copyright__ = "Copyright (C) 2020  Martin Blais"
__license__ = "GNU GPLv2"

from datetime import date as Date
from decimal import Decimal
from typing import List, Tuple
import argparse
import csv
import datetime
import io
import pprint

import dateutil.parser
import requests


def download_dividends(
    instrument: str, start_date: Date, end_date: Date
) -> List[Tuple[Date, Decimal]]:
    """Download a list of dividends issued over a time interval."""
    tim = datetime.time()
    payload = {
        "period1": str(int(datetime.datetime.combine(start_date, tim).timestamp())),
        "period2": str(int(datetime.datetime.combine(end_date, tim).timestamp())),
        "interval": "1d",
        "events": "div",
        "includeAdjustedClose": "true",
    }
    template = " https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
    url = template.format(ticker=instrument)
    resp = requests.get(url, params=payload)
    if not resp.ok:
        raise ValueError("Error fetching dividends: {}".format(resp.text))

    rows = iter(csv.reader(io.StringIO(resp.text)))
    header = next(rows)
    if header != ["Date", "Dividends"]:
        raise ValueError(
            "Error fetching dividends: " "invalid response format: {}".format(header)
        )

    dividends = []
    for row in rows:
        date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
        dividend = Decimal(row[1])
        dividends.append((date, dividend))
    return dividends


def main():
    """Top-level function."""
    today = datetime.date.today()
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("instrument", help="Yahoo!Finance code for financial instrument.")
    parser.add_argument(
        "start",
        action="store",
        type=lambda x: dateutil.parser.parse(x).date(),
        default=today.replace(year=today.year - 1),
        help="Start date of interval. Default is one year ago.",
    )
    parser.add_argument(
        "end",
        action="store",
        type=lambda x: dateutil.parser.parse(x).date(),
        default=today,
        help="End date of interval. Default is today ago.",
    )

    args = parser.parse_args()

    dividends = download_dividends(args.instrument, args.start, args.end)
    pprint.pprint(dividends)


if __name__ == "__main__":
    main()
