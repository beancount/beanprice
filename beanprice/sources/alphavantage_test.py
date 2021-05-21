import datetime
import unittest
from os import environ
from decimal import Decimal

from unittest import mock
from dateutil import tz

import requests

from beanprice import source
from beanprice.sources import alphavantage


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = contents
    return mock.patch('requests.get', return_value=response)


class AlphavantagePriceFetcher(unittest.TestCase):

    def setUp(self):
        environ['ALPHAVANTAGE_API_KEY'] = 'foo'

    def tearDown(self):
        del environ['ALPHAVANTAGE_API_KEY']

    def test_error_invalid_ticker(self):
        with self.assertRaises(ValueError):
            alphavantage.Source().get_latest_price('INVALID')

    def test_error_network(self):
        with response('Foobar', 404):
            with self.assertRaises(alphavantage.AlphavantageApiError):
                alphavantage.Source().get_latest_price('price:IBM:USD')

    def test_error_response(self):
        contents = {
            "Error Message": "Something wrong"
        }
        with response(contents):
            with self.assertRaises(alphavantage.AlphavantageApiError):
                alphavantage.Source().get_latest_price('price:IBM:USD')

    def test_valid_response_price(self):
        contents = {
            "Global Quote": {
                "05. price": "144.7400",
                "07. latest trading day": "2021-01-21",
            }
        }
        with response(contents):
            srcprice = alphavantage.Source().get_latest_price('price:FOO:USD')
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal('144.7400'), srcprice.price)
            self.assertEqual('USD', srcprice.quote_currency)
            self.assertEqual(datetime.datetime(2021, 1, 21, 0, 0, 0, tzinfo=tz.tzutc()),
                             srcprice.time)

    def test_valid_response_fx(self):
        contents = {
            "Realtime Currency Exchange Rate": {
                "5. Exchange Rate": "108.94000000",
                "6. Last Refreshed": "2021-02-21 20:32:25",
                "7. Time Zone": "UTC",
            }
        }
        with response(contents):
            srcprice = alphavantage.Source().get_latest_price('fx:USD:CHF')
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal('108.94000000'), srcprice.price)
            self.assertEqual('CHF', srcprice.quote_currency)
            self.assertEqual(datetime.datetime(2021, 2, 21, 20, 32, 25, tzinfo=tz.tzutc()),
                             srcprice.time)


if __name__ == '__main__':
    unittest.main()
