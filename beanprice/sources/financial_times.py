"""
A price source for the Financial Times API.

Requires an API key, which should be stored in the environment variable
"FINANCIAL_TIMES_API_KEY".

Valid symbol sets include FTStandard, Bridge, Street & ISIN symbols.

"""

import datetime
import math
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
import requests
from beanprice import source
from os import environ

class FinancialTimesError(ValueError):
    "An error from the Financial Times API."


def get_price_series(ticker: str, time_begin: datetime.datetime,
                     time_end: datetime.datetime) -> List[source.SourcePrice]:
    dayCount = ceil((time_end - time_begin).days)
    headers = {
            'X-FT-Source': environ['FINANCIAL_TIMES_API_KEY'],
        }
        params = {
            'symbols': ticker,
            'endDate': time_end.date.iso_format(),
            'intervalType': 'day',
            'interval': '1',
            'dayCount': dayCount
        }

        resp = requests.get(
            url='https://markets.ft.com/research/webservices/securities/v1/time-series-interday',
            params=params, headers=headers)
        if resp.status_code != requests.codes.ok:
            raise FinancialTimesError(
                "Invalid response ({}): {}".format(resp.status_code, resp.text)
            )
        data = resp.json()
        if not data['error'] is None:
            raise FinancialTimesError(
                "API Errors: ({}): {}".format(data['error']['errors'][0]['reason'], data['error']['errors'][0]['message'])
            )

        base = data['data']['items'][0]['basic']['currency']

        return [source.SourcePrice(
                Decimal(str(item['close'])),
                datetime.datetime.fromisoformat(item['lastCloseDateTime']),
                base
            )
                for item in data['items'][0]['timeSeries']['timeSeriesData']]

class Source(source.Source):
    def get_latest_price(self, ticker) -> source.SourcePrice:
        headers = {
            'X-FT-Source': environ['FINANCIAL_TIMES_API_KEY'],
        }
        params = {
            'symbols': ticker
        }

        resp = requests.get(
            url='https://markets.ft.com/research/webservices/securities/v1/quotes',
            params=params, headers=headers)
        if resp.status_code != requests.codes.ok:
            raise FinancialTimesError(
                "Invalid response ({}): {}".format(resp.status_code, resp.text)
            )
        data = resp.json()
        if not data['error'] is None:
            raise FinancialTimesError(
                "API Errors: ({}): {}".format(data['error']['errors'][0]['reason'], data['error']['errors'][0]['message'])
            )

        base = data['data']['items'][0]['basic']['currency']
        quote = data['data']['items'][0]['quote']
        price = Decimal(str(quote['lastPrice']))
        date = parse(quote['timeStamp'])

        return source.SourcePrice(price, date, base)

    def get_historical_price(self, ticker: str,
                             time: datetime.datetime) -> Optional[source.SourcePrice]:
        for datapoint in self.get_prices_series(ticker,
                                                time +
                                                datetime.timedelta(days=-1),
                                                time + datetime.timedelta(days=1)):
            if not datapoint.time is None and datapoint.time.date() == time.date():
                return datapoint
        return None

    def get_prices_series(self, ticker: str,
                          time_begin: datetime.datetime,
                          time_end: datetime.datetime
                          ) -> List[source.SourcePrice]:
        return get_price_series(ticker, time_begin, time_end)
