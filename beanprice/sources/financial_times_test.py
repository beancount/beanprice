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

    def test_valid_response(self):contents = {
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
            srcprice = coinmarketcap.Source().get_latest_price('pson:lse')
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal('857.2'), srcprice.price)
            self.assertEqual('GBp', srcprice.quote_currency)
