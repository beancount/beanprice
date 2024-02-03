from datetime import datetime
import unittest
from decimal import Decimal
from os import environ

from unittest import mock

import requests

from beanprice import source
from beanprice.sources import financial_times

def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = contents
    return mock.patch('requests.get', return_value=response)


class CoinmarketcapPriceFetcher(unittest.TestCase):
    def setUp(self):
        environ['FINANCIAL_TIMES_API_KEY'] = 'foo'

    def tearDown(self):
        del environ['FINANCIAL_TIMES_API_KEY']

    def test_valid_response(self):
        contents = {
            "data": {
                "items": [
                {
                    "symbolInput": "pson:lse",
                    "basic": {
                        "symbol": "PSON:LSE",
                        "name": "Pearson",
                        "exchange": "London Stock Exchange",
                        "exhangeCode": "LSE",
                        "bridgeExchangeCode": "GBL",
                        "currency": "GBp"
                    },
                    "quote": {
                        "lastPrice": 857.2,
                        "openPrice": 856.0,
                        "high": 859.2,
                        "low": 847.0,
                        "closePrice": 857.2,
                        "previousClosePrice": 848.6,
                        "change1Day": 8.6000000000000227,
                        "change1DayPercent": 1.01343389111478,
                        "change1Week": 45.200000000000045,
                        "change1WeekPercent": 5.5665024630541931,
                        "ask": 885.0,
                        "askSize": 2400.0,
                        "bid": 801.40000000000009,
                        "bidSize": 700.0,
                        "timeStamp": "2021-07-23T15:35:13",
                        "volume": 757939.0
                    }
                },
                {
                    "symbolInput": "mrkt",
                    "partialError": "No symbol match found"
                }
                ]
            },
            "timeGenerated": "2021-07-24T12:27:24"
            }
        with response(contents):
            srcprice = financial_times.Source().get_latest_price('pson:lse')
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal('857.2'), srcprice.price)
            self.assertEqual('GBp', srcprice.quote_currency)

    def test_invalid_response(self):
        contents = {
            "error": {
                "code": 400,
                "message": "Missing or invalid parameters",
                "errors": [
                {
                    "reason": "InvalidParameter",
                    "message": "There are no matches on any of the symbols provided."
                }
                ]
            },
            "timeGenerated": "2021-07-27T10:12:59"
        }
        with response(contents):
            with self.assertRaises(financial_times.FinancialTimesError):
                financial_times.Source().get_latest_price('nonexistent')

    def test_get_price_series(self):
        contents = {
            "data": {
                "items": [
                {
                    "symbolInput": "pson:lse",
                    "basic": {
                    "symbol": "PSON:LSE",
                    "name": "Pearson",
                    "exchange": "London Stock Exchange",
                    "exhangeCode": "LSE",
                    "bridgeExchangeCode": "GBL",
                    "currency": "GBp"
                    },
                    "timeSeries": {
                    "timeSeriesData": [
                        {
                        "open": 856.0,
                        "high": 859.2,
                        "low": 847.0,
                        "close": 857.2,
                        "lastClose": "2021-07-23T15:35:00",
                        "lastCloseDateTime": "2021-07-23T15:35:00.038",
                        "volume": 1163977.0
                        },
                        {
                        "open": 855.6,
                        "high": 860.6,
                        "low": 837.0,
                        "close": 838.6,
                        "lastClose": "2021-07-26T15:35:00",
                        "lastCloseDateTime": "2021-07-26T15:35:00.038",
                        "volume": 2319095.0
                        },
                        {
                        "open": 836.80000000000007,
                        "high": 840.2,
                        "low": 833.0,
                        "close": 837.2,
                        "lastClose": "2021-07-27T15:35:00",
                        "lastCloseDateTime": "2021-07-27T15:35:00.038",
                        "volume": 208775.0
                        }
                    ],
                    "lastPrice": 837.2,
                    "lastPriceTimeStamp": "2021-07-27T09:43:47",
                    "lastSession": {
                        "timeOpen": "2021-07-27T07:00:00",
                        "timeClose": "2021-07-27T15:35:00",
                        "isInSession": True,
                        "isAfterOpen": True,
                        "isBeforeOpen": False,
                        "lastPrice": 837.2,
                        "previousClosePrice": 838.6,
                        "open": 836.80000000000007,
                        "high": 840.2,
                        "low": 833.0,
                        "lastCloseDateTime": "0001-01-01T00:00:00",
                        "volume": 184143.0
                    },
                    "boundaryData": {}
                    }
                }
                ]
            },
            "timeGenerated": "2021-07-27T10:17:23"
            }
        with response(contents):
            srcprice = financial_times.Source()\
                .get_prices_series('pson:lse', datetime(2021, 7, 23), datetime(2021, 7, 27))
            print(srcprice)
            self.assertIsInstance(srcprice[0], source.SourcePrice)
            self.assertEqual(Decimal('857.2'), srcprice[0].price)
            self.assertEqual('GBp', srcprice[0].quote_currency)
            self.assertIsInstance(srcprice[1], source.SourcePrice)
            self.assertEqual(Decimal('838.6'), srcprice[1].price)
            self.assertEqual('GBp', srcprice[1].quote_currency)
            self.assertIsInstance(srcprice[2], source.SourcePrice)
            self.assertEqual(Decimal('837.2'), srcprice[2].price)
            self.assertEqual('GBp', srcprice[2].quote_currency)
