import datetime
import unittest
from decimal import Decimal

from unittest import mock
from dateutil import tz

import requests

from beanprice import source
from beanprice.sources import ratesapi


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = contents
    return mock.patch("requests.get", return_value=response)


class RatesapiPriceFetcher(unittest.TestCase):
    def test_error_invalid_ticker(self):
        with self.assertRaises(ValueError):
            ratesapi.Source().get_latest_price("INVALID")

    def test_error_network(self):
        with response("Foobar", 404):
            with self.assertRaises(ValueError):
                ratesapi.Source().get_latest_price("EUR-CHF")

    def test_valid_response(self):
        contents = {
            "base": "EUR",
            "rates": {"CHF": "1.2001"},
            "date": "2019-04-20",
        }
        with response(contents):
            srcprice = ratesapi.Source().get_latest_price("EUR-CHF")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("1.2001"), srcprice.price)
            self.assertEqual("CHF", srcprice.quote_currency)

    def test_historical_price(self):
        time = datetime.datetime(2018, 3, 27, 0, 0, 0, tzinfo=tz.tzutc())
        contents = {
            "base": "EUR",
            "rates": {"CHF": "1.2001"},
            "date": "2018-03-27",
        }
        with response(contents):
            srcprice = ratesapi.Source().get_historical_price("EUR-CHF", time)
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("1.2001"), srcprice.price)
            self.assertEqual("CHF", srcprice.quote_currency)
            self.assertEqual(
                datetime.datetime(2018, 3, 27, 0, 0, 0, tzinfo=tz.tzutc()), srcprice.time
            )


if __name__ == "__main__":
    unittest.main()
