import datetime
import unittest
from decimal import Decimal
from os import environ
from unittest import mock

import requests
from dateutil import tz

from beanprice import source
from beanprice.sources import unirate


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = contents
    return mock.patch("requests.get", return_value=response)


class UniRatePriceFetcher(unittest.TestCase):
    def setUp(self):
        environ["UNIRATE_API_KEY"] = "test-key"

    def tearDown(self):
        environ.pop("UNIRATE_API_KEY", None)

    def test_error_invalid_ticker(self):
        with self.assertRaises(ValueError):
            unirate.Source().get_latest_price("INVALID")

    def test_error_missing_api_key(self):
        del environ["UNIRATE_API_KEY"]
        with self.assertRaises(unirate.UniRateError):
            unirate.Source().get_latest_price("USD-EUR")

    def test_error_network(self):
        with response("Foobar", 500):
            with self.assertRaises(unirate.UniRateError):
                unirate.Source().get_latest_price("USD-EUR")

    def test_error_pro_required_on_historical(self):
        with response({"error": "Pro plan required"}, 403):
            with self.assertRaises(unirate.UniRateError):
                unirate.Source().get_historical_price(
                    "USD-EUR",
                    datetime.datetime(2024, 1, 1, tzinfo=tz.tzutc()),
                )

    def test_error_unexpected_response_shape(self):
        with response({"unexpected": "payload"}):
            with self.assertRaises(unirate.UniRateError):
                unirate.Source().get_latest_price("USD-EUR")

    def test_valid_response_latest_fx(self):
        with response({"rate": "0.92"}):
            srcprice = unirate.Source().get_latest_price("USD-EUR")
        self.assertIsInstance(srcprice, source.SourcePrice)
        self.assertEqual(Decimal("0.92"), srcprice.price)
        self.assertEqual("EUR", srcprice.quote_currency)
        self.assertIsNotNone(srcprice.time.tzinfo)

    def test_valid_response_latest_crypto(self):
        with response({"rate": "65000.50"}):
            srcprice = unirate.Source().get_latest_price("BTC-USD")
        self.assertIsInstance(srcprice, source.SourcePrice)
        self.assertEqual(Decimal("65000.50"), srcprice.price)
        self.assertEqual("USD", srcprice.quote_currency)

    def test_valid_response_historical(self):
        with response({"rate": "1.21"}):
            srcprice = unirate.Source().get_historical_price(
                "EUR-USD",
                datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=tz.tzutc()),
            )
        self.assertIsInstance(srcprice, source.SourcePrice)
        self.assertEqual(Decimal("1.21"), srcprice.price)
        self.assertEqual("USD", srcprice.quote_currency)
        self.assertEqual(
            datetime.datetime(2024, 6, 15, 0, 0, 0, tzinfo=tz.tzutc()),
            srcprice.time,
        )


if __name__ == "__main__":
    unittest.main()
