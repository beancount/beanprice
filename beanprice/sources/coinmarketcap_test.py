import unittest
from decimal import Decimal
from os import environ

from unittest import mock

import requests

from beanprice import source
from beanprice.sources import coinmarketcap


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = contents
    return mock.patch("requests.get", return_value=response)


class CoinmarketcapPriceFetcher(unittest.TestCase):
    def setUp(self):
        environ["COINMARKETCAP_API_KEY"] = "foo"

    def tearDown(self):
        del environ["COINMARKETCAP_API_KEY"]

    def test_error_invalid_ticker(self):
        with self.assertRaises(ValueError):
            coinmarketcap.Source().get_latest_price("INVALID")

    def test_error_network(self):
        with response("Foobar", 404):
            with self.assertRaises(ValueError):
                coinmarketcap.Source().get_latest_price("BTC-CHF")

    def test_error_request(self):
        contents = {
            "status": {
                "error_code": 2,
                "error_message": "foobar",
            }
        }
        with response(contents):
            with self.assertRaises(ValueError):
                coinmarketcap.Source().get_latest_price("BTC-CHF")

    def test_valid_response(self):
        contents = {
            "data": {
                "BTC": {
                    "quote": {
                        "CHF": {
                            "price": 1234.56,
                            "last_updated": "2018-08-09T21:56:28.000Z",
                        }
                    }
                }
            },
            "status": {
                "error_code": 0,
                "error_message": "",
            },
        }
        with response(contents):
            srcprice = coinmarketcap.Source().get_latest_price("BTC-CHF")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("1234.56"), srcprice.price)
            self.assertEqual("CHF", srcprice.quote_currency)


if __name__ == "__main__":
    unittest.main()
