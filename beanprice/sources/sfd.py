"""
A source fetching prices from https://www.swissfunddata.ch/sfdpub/investment-funds

"""
import datetime
from decimal import Decimal
from typing import Optional, Dict
from csv import DictReader
from dateutil.tz import tz
from dateutil.parser import parse
import logging
import subprocess
from beanprice import source
from pathlib import Path


class SfdApiError(ValueError):
    """An error from the SCIF API."""


def _fetch_prices(fund_id: str) -> (Dict[str, source.SourcePrice], source.SourcePrice):
    # Download file, or was it cached?
    filename = '/tmp/beanprice_sfd_{}.csv'.format(fund_id)
    path = Path(filename)
    if not path.is_file():
        logging.debug('Fetching data from server for fund {}'.format(fund_id))
        # Fetch the HTML workbook, we have to use curl, see PortfolioPerformance documentation
        link = 'https://www.swissfunddata.ch/sfdpub/en/funds/excelData/{}'.format(fund_id)
        try:
            response = subprocess.check_output(['curl', '-s', link]).decode("utf-8")
        except BaseException as e:
            raise SfdApiError('Error connecting to server on URL {}'.format(link))

        # Save to file for future access
        with open(path, "w") as text_file:
            text_file.write(response)

    # Read CSV file
    prices: Dict[str, source.SourcePrice] = dict()
    latest_price = None

    with open(filename, 'r', encoding='utf8') as csvfile:
        reader = DictReader(
            csvfile,
            fieldnames=[
                "date",
                "ccy",
                "price",
            ],
            delimiter=";"
        )

        # This skips the first row of the CSV file.
        next(reader)
        next(reader)
        next(reader)

        for row in reader:
            the_date = parse(row["date"]).replace(tzinfo=tz.gettz('Europe/Zurich'))
            key = the_date.strftime("%Y%m%d")
            latest_price = source.SourcePrice(
                Decimal(row["price"].replace("'", '')),
                the_date,
                row["ccy"].strip()
            )
            prices[key] = latest_price

    return prices, latest_price


class Source(source.Source):

    def get_latest_price(self, ticker) -> Optional[source.SourcePrice]:
        # Fetch data
        _, latest_price = _fetch_prices(ticker)

        logging.debug('Latest price: {} {}, {}'.format(
            latest_price.price,
            latest_price.time,
            latest_price.quote_currency
        ))
        return latest_price

    def get_historical_price(self, ticker, time) -> Optional[source.SourcePrice]:
        # Fetch data
        prices, _ = _fetch_prices(ticker)

        # Find relevant date
        key = time.strftime("%Y%m%d")
        if key not in prices:
            return None
        else:
            the_price = prices[key]
            logging.debug('Historical price: {} {}, {}'.format(
                the_price.price,
                the_price.time,
                the_price.quote_currency
            ))
            return the_price
