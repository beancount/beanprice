"""A source fetching prices and exchangerates from https://amfunds.credit-suisse.com

Valid tickers for prices are in the form "IBAN", such as "CH0031341875".

Here is the API documentation:
https://www.alphavantage.co/documentation/

Example:
    https://amfunds.credit-suisse.com/ch/de/institutional/fund/history/CH0031341875

Based on: https://github.com/buchen/portfolio/blob/effa5b7baf9a918e1b5fe83942ddc480e0fd48b9/name.abuchen.portfolio/src/name/abuchen/portfolio/online/impl/CSQuoteFeed.java

"""

from decimal import Decimal
from typing import Optional
from dateutil.tz import tz
from dateutil.parser import parse
import logging
import subprocess
from beanprice import source
from pathlib import Path


class CsifApiError(ValueError):
    """An error from the CSIF API."""


def _fetch_response(ticker):
    # Download file, or was it cached?
    filename = '/tmp/beanprice_csif_{}.html'.format(ticker)
    path = Path(filename)
    if not path.is_file():
        logging.debug('Fetching data from server for ticker {}'.format(ticker))
        # Fetch the HTML workbook, we have to use curl, see PortfolioPerformance documentation
        link = 'https://amfunds.credit-suisse.com/ch/de/institutional/fund/history/{}?currency=CHF'.format(ticker)
        try:
            response = subprocess.check_output(['curl', '-s', link]).decode("utf-8")
        except BaseException as e:
            raise CsifApiError('Error connecting to server on URL {}'.format(link))

        # Save to file for future access
        with open(path, "w") as text_file:
            text_file.write(response)
    else:
        # Read the response from text file
        logging.debug('Retrieving cached data for ticker {}'.format(ticker))
        with open(path, "r") as text_file:
            response = text_file.read()

    # Find first occurrence of HTML tag "<td>IBAN</td>"
    pos = response.find('<td>{}</td>'.format(ticker))
    if pos < 0:
        raise CsifApiError('Ticker {} not fund'.format(ticker))
    pos = pos + 4

    # Next occurrence of "<td>": security number
    pos = pos + response[pos:].find('<td>') + 4
    end_pos = pos + response[pos:].find('</td>')
    sec_number = response[pos:end_pos]

    # Next occurrence of "<td>": currency
    pos = pos + response[pos:].find('<td>') + 4
    end_pos = pos + response[pos:].find('</td>')
    currency = response[pos:end_pos]
    logging.debug('Ticker {} data loaded: sec. number {}, currency {}'.format(
        ticker,
        sec_number,
        currency
    ))

    return response, currency, sec_number


class Source(source.Source):

    def get_latest_price(self, ticker) -> Optional[source.SourcePrice]:
        # Fetch data
        response, currency, sec_number = _fetch_response(ticker)

        # Find first occurrence of security number
        pos = response.find('<td>{}</td>'.format(sec_number))
        if pos < 0:
            return None
        pos = pos + 4

        # Next two occurrences of HTML tags "<td>" and "</td>"
        pos = pos + response[pos:].find('<td>') + 4
        pos = pos + response[pos:].find('<td>') + 4
        end_pos = pos + response[pos:].find('</td>')

        # Parse date
        date_str = response[pos:end_pos]
        logging.debug('Date: {}'.format(date_str))
        date = parse(date_str).replace(tzinfo=tz.gettz('Europe/Zurich'))

        # Next occurrence of HTML tags "<td>" and "</td>"
        pos = pos + response[pos:].find('<td>') + 4
        end_pos = pos + response[pos:].find('</td>')

        # Parse value
        logging.debug('Price: {}'.format(response[pos:end_pos]))
        price = Decimal(response[pos:end_pos])

        logging.debug('Latest price: {} {}, {}'.format(price, currency, date_str))
        return source.SourcePrice(price, date, currency)

    def get_historical_price(self, ticker, time) -> Optional[source.SourcePrice]:
        # Fetch data
        response, currency, sec_number = _fetch_response(ticker)

        # Find relevant date
        date_str = time.strftime("%d.%m.%Y")
        pos = response.find(date_str)

        # Found?
        if pos < 0:
            # It can happen that a date is missing
            raise source.MissingDate
        pos = pos + 10

        # Next occurrences of HTML tags "<td>" and "</td>"
        pos = pos + response[pos:].find('<td>') + 4
        end_pos = pos + response[pos:].find('</td>')

        # Parse value
        try:
            price = Decimal(response[pos:end_pos])
        except BaseException as e:
            raise CsifApiError('Error parsing price {} for date {}'.format(response[pos:end_pos], date_str))

        logging.debug('Historical price: {} {}, {}'.format(price, currency, date_str))
        return source.SourcePrice(price, time, currency)
