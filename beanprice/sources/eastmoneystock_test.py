import datetime
import unittest
from decimal import Decimal

from unittest import mock

from beanprice.sources import eastmoneystock
from beanprice import source


# ruff: noqa: E501

# Sample API response for kline data (600519 - Kweichow Moutai).
KLINE_RESPONSE = {
    "rc": 0,
    "rt": 6,
    "svr": 123456,
    "lt": 1,
    "full": 0,
    "data": {
        "code": "600519",
        "market": 1,
        "name": "贵州茅台",
        "decimal": 2,
        "dktotal": 5,
        "klines": [
            "2024-01-02,1726.00",
            "2024-01-03,1718.30",
            "2024-01-04,1706.88",
            "2024-01-05,1694.00",
            "2024-01-08,1678.01",
        ],
    },
}

# Response with no klines data.
EMPTY_RESPONSE = {
    "rc": 0,
    "rt": 6,
    "data": {
        "code": "600519",
        "market": 1,
        "klines": [],
    },
}


def mock_response(json_data, status_code=200):
    """Return a context manager to patch a JSON response."""
    resp = mock.Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.text = str(json_data)
    return mock.patch("requests.get", return_value=resp)


class TestGetMarketAndCurrency(unittest.TestCase):
    def test_shenzhen_stock(self):
        code, currency = eastmoneystock._get_market_and_currency("000858")
        self.assertEqual("0", code)
        self.assertEqual("CNY", currency)

    def test_shanghai_stock(self):
        code, currency = eastmoneystock._get_market_and_currency("600519")
        self.assertEqual("1", code)
        self.assertEqual("CNY", currency)

    def test_hk_stock(self):
        code, currency = eastmoneystock._get_market_and_currency("00700")
        self.assertEqual("116", code)
        self.assertEqual("HKD", currency)

    def test_unsupported_ticker(self):
        with self.assertRaises(eastmoneystock.EastMoneyStockError):
            eastmoneystock._get_market_and_currency("AAPL")


class TestParseKlineData(unittest.TestCase):
    def test_parse_valid_data(self):
        result = eastmoneystock._parse_kline_data(KLINE_RESPONSE)
        self.assertEqual(5, len(result))
        self.assertEqual(
            datetime.datetime(
                2024, 1, 2, 15, 0, 0, tzinfo=eastmoneystock.TIMEZONE
            ),
            result[0][0],
        )
        self.assertEqual(Decimal("1726.00"), result[0][1])

    def test_parse_empty_klines(self):
        result = eastmoneystock._parse_kline_data(EMPTY_RESPONSE)
        self.assertIsNone(result)

    def test_parse_none_data(self):
        result = eastmoneystock._parse_kline_data(None)
        self.assertIsNone(result)


class TestEastMoneyStock(unittest.TestCase):
    def test_error_network(self):
        with mock_response(None, 404):
            with self.assertRaises(eastmoneystock.EastMoneyStockError):
                eastmoneystock.get_price_series(
                    "600519",
                    datetime.datetime.now(eastmoneystock.TIMEZONE),
                    datetime.datetime.now(eastmoneystock.TIMEZONE),
                )

    def test_get_latest_price(self):
        rows = eastmoneystock._parse_kline_data(KLINE_RESPONSE)
        with mock.patch.object(eastmoneystock, "get_price_series", return_value=rows):
            srcprice = eastmoneystock.Source().get_latest_price("600519")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("1678.01"), srcprice.price)
            self.assertEqual("CNY", srcprice.quote_currency)
            self.assertEqual(
                datetime.datetime(
                    2024, 1, 8, 15, 0, 0,
                    tzinfo=eastmoneystock.TIMEZONE,
                ),
                srcprice.time,
            )

    def test_get_historical_price(self):
        with mock_response(KLINE_RESPONSE):
            time = datetime.datetime(
                2024, 1, 5, 0, 0, 0, tzinfo=eastmoneystock.TIMEZONE
            )
            srcprice = eastmoneystock.Source().get_historical_price(
                "600519", time
            )
            self.assertIsInstance(srcprice, source.SourcePrice)
            # Must not use January 8 for a January 5 valuation.
            self.assertEqual(Decimal("1694.00"), srcprice.price)
            self.assertEqual("CNY", srcprice.quote_currency)

    def test_get_prices_series(self):
        with mock_response(KLINE_RESPONSE):
            begin = datetime.datetime(
                2024, 1, 1, 0, 0, 0, tzinfo=eastmoneystock.TIMEZONE
            )
            end = datetime.datetime(
                2024, 1, 10, 0, 0, 0, tzinfo=eastmoneystock.TIMEZONE
            )
            prices = eastmoneystock.Source().get_prices_series(
                "600519", begin, end
            )
            self.assertIsInstance(prices, list)
            self.assertEqual(5, len(prices))
            # Sorted ascending
            self.assertEqual(Decimal("1726.00"), prices[0].price)
            self.assertEqual(Decimal("1678.01"), prices[-1].price)
            self.assertEqual("CNY", prices[0].quote_currency)

    def test_empty_response_raises(self):
        with mock_response(EMPTY_RESPONSE):
            with self.assertRaises(eastmoneystock.EastMoneyStockError):
                eastmoneystock.get_price_series(
                    "600519",
                    datetime.datetime.now(eastmoneystock.TIMEZONE),
                    datetime.datetime.now(eastmoneystock.TIMEZONE),
                )


if __name__ == "__main__":
    unittest.main()
