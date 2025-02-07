import datetime
import decimal
import unittest
from decimal import Decimal
from unittest import mock

import requests

from beanprice import source
from beanprice.sources import portfolioreport

SYMBOL_A1JX52_UUID = '9a49754d8fd941bfa1dd2cff1922fe9b:EUR'


def response(contents, status_code=requests.codes.ok):
    """Produce a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = ""
    response.json.return_value = contents
    return mock.patch("requests.get", return_value=response)


class PortfolioreportPriceFetcher(unittest.TestCase):
    def setUp(self):
        # reset the Decimal context since other tests override this
        decimal.getcontext().prec = 10
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        self.sut = portfolioreport.Source()

    def test_error_network(self):
        with response(None, 404):
            with self.assertRaises(portfolioreport.PortfolioreportError):
                self.sut.get_historical_price(
                    SYMBOL_A1JX52_UUID,
                    datetime.datetime(2024, 1, 1),
                )
            with self.assertRaises(portfolioreport.PortfolioreportError):
                self.sut.get_latest_price(SYMBOL_A1JX52_UUID)
            with self.assertRaises(portfolioreport.PortfolioreportError):
                self.sut.get_prices_series(
                    SYMBOL_A1JX52_UUID,
                    datetime.datetime(2024, 1, 1),
                    datetime.datetime(2024, 1, 14),
                )

    def test_valid_response(self):
        contents = [
            {"date":"2024-01-02","close":88.37800000},
            {"date":"2024-01-03","close":87.99600000},
            {"date":"2024-01-04","close":87.89400000},
            {"date":"2024-01-05","close":87.72000000},
        ]
        with response(contents):
            price_1 = self.sut.get_historical_price(
                SYMBOL_A1JX52_UUID,
                datetime.datetime(2024, 1, 1),
            )
            self.assertEqual(
                source.SourcePrice(
                    Decimal('88.37800000'),
                    datetime.datetime(2024, 1, 2, tzinfo=datetime.timezone.utc),
                    'EUR',
                ),
                price_1,
            )
            self.assertTrue(price_1.time.tzinfo)

            price_2 = self.sut.get_latest_price(SYMBOL_A1JX52_UUID)
            self.assertEqual(
                source.SourcePrice(
                    Decimal('87.72000000'),
                    datetime.datetime(2024, 1, 5, tzinfo=datetime.timezone.utc),
                    'EUR',
                ),
                price_2,
            )
            self.assertTrue(price_2.time.tzinfo)

            price_3 = self.sut.get_prices_series(
                SYMBOL_A1JX52_UUID,
                datetime.datetime(2024, 1, 3),
                datetime.datetime(2024, 1, 4),
            )
            self.assertEqual(
                [
                    source.SourcePrice(
                        Decimal('87.99600000'),
                        datetime.datetime(2024, 1, 3, tzinfo=datetime.timezone.utc),
                        'EUR',
                    ),
                    source.SourcePrice(
                        Decimal('87.89400000'),
                        datetime.datetime(2024, 1, 4, tzinfo=datetime.timezone.utc),
                        'EUR',
                    ),
                ],
                price_3,
            )
            self.assertTrue(price_3[0].time.tzinfo)
            self.assertTrue(price_3[1].time.tzinfo)

    def test_empty_response(self):
        contents = []
        with response(contents):
            price_1 = self.sut.get_historical_price(
                SYMBOL_A1JX52_UUID,
                datetime.datetime(2024, 1, 1),
            )
            self.assertIsNone(price_1)

            price_2 = self.sut.get_latest_price(SYMBOL_A1JX52_UUID)
            self.assertIsNone(price_2)

            price_3 = self.sut.get_prices_series(
                SYMBOL_A1JX52_UUID,
                datetime.datetime(2024, 1, 3),
                datetime.datetime(2024, 1, 4),
            )
            self.assertIsNone(price_3)


if __name__ == "__main__":
    unittest.main()
