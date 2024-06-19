import datetime
import unittest
from decimal import Decimal

from unittest import mock
from dateutil import tz

import requests

from beanprice.sources import eastmoneyfund
from beanprice import source


# ruff: noqa: E501,RUF001

contents = """
var apidata={ content:"<table class='w782 comm lsjz'><thead><tr><th class='first'>净值日期</th><th>单位净值</th><th>累计净值</th><th>日增长率</th><th>申购状态</th><th>赎回状态</th><th class='tor last'>分红送配</th></tr></thead><tbody><tr><td>2020-10-09</td><td class='tor bold'>5.1890</td><td class='tor bold'>5.1890</td><td class='tor bold red'>4.11%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-30</td><td class='tor bold'>4.9840</td><td class='tor bold'>4.9840</td><td class='tor bold red'>0.12%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-29</td><td class='tor bold'>4.9780</td><td class='tor bold'>4.9780</td><td class='tor bold red'>1.14%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-28</td><td class='tor bold'>4.9220</td><td class='tor bold'>4.9220</td><td class='tor bold red'>0.22%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-25</td><td class='tor bold'>4.9110</td><td class='tor bold'>4.9110</td><td class='tor bold red'>0.88%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-24</td><td class='tor bold'>4.8680</td><td class='tor bold'>4.8680</td><td class='tor bold grn'>-3.81%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-23</td><td class='tor bold'>5.0610</td><td class='tor bold'>5.0610</td><td class='tor bold red'>2.41%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-22</td><td class='tor bold'>4.9420</td><td class='tor bold'>4.9420</td><td class='tor bold grn'>-1.02%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-21</td><td class='tor bold'>4.9930</td><td class='tor bold'>4.9930</td><td class='tor bold grn'>-1.29%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-18</td><td class='tor bold'>5.0580</td><td class='tor bold'>5.0580</td><td class='tor bold red'>0.48%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-17</td><td class='tor bold'>5.0340</td><td class='tor bold'>5.0340</td><td class='tor bold red'>0.60%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-16</td><td class='tor bold'>5.0040</td><td class='tor bold'>5.0040</td><td class='tor bold grn'>-1.28%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-15</td><td class='tor bold'>5.0690</td><td class='tor bold'>5.0690</td><td class='tor bold red'>1.06%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-14</td><td class='tor bold'>5.0160</td><td class='tor bold'>5.0160</td><td class='tor bold red'>0.42%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-11</td><td class='tor bold'>4.9950</td><td class='tor bold'>4.9950</td><td class='tor bold red'>3.39%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-10</td><td class='tor bold'>4.8310</td><td class='tor bold'>4.8310</td><td class='tor bold grn'>-0.29%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr></tbody></table>",records:16,pages:1,curpage:1};\
"""

unsupport_content = """
var apidata={ content:"<table class='w782 comm lsjz'><thead><tr><th class='first'>净值日期</th><th>每万份收益</th><th>7日年化收益率（%）</th><th>申购状态</th><th>赎回状态</th><th class='tor last'>分红送配</th></tr></thead><tbody><tr><td>2020-09-10</td><td class='tor bold'>0.4230</td><td class='tor bold'>1.5730%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr></tbody></table>",records:1,pages:1,curpage:1};"""


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = contents
    return mock.patch("requests.get", return_value=response)


class EastMoneyFundFetcher(unittest.TestCase):

    def test_error_network(self):
        with response(None, 404):
            with self.assertRaises(ValueError):
                eastmoneyfund.get_price_series(
                    "377240", datetime.datetime.now(), datetime.datetime.now()
                )

    def test_unsupport_page(self):
        with response(unsupport_content):
            with self.assertRaises(ValueError) as exc:
                eastmoneyfund.get_price_series(
                    "377240", datetime.datetime.now(), datetime.datetime.now()
                )
            self.assertEqual(eastmoneyfund.UnsupportTickerError, exc.exception)

    def test_latest_price(self):
        with response(contents):
            srcprice = eastmoneyfund.Source().get_latest_price("377240")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("5.1890"), srcprice.price)
            self.assertEqual("CNY", srcprice.quote_currency)

    def test_historical_price(self):
        with response(contents):
            time = datetime.datetime(2018, 3, 27, 0, 0, 0, tzinfo=tz.tzutc())
            srcprice = eastmoneyfund.Source().get_historical_price("377240", time)
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("5.1890"), srcprice.price)
            self.assertEqual("CNY", srcprice.quote_currency)
            self.assertEqual(
                datetime.datetime(2020, 10, 9, 15, 0, 0, tzinfo=eastmoneyfund.TIMEZONE),
                srcprice.time,
            )

    def test_get_prices_series(self):
        with response(contents):
            time = datetime.datetime(2018, 3, 27, 0, 0, 0, tzinfo=tz.tzutc())
            srcprice = eastmoneyfund.Source().get_prices_series(
                "377240", time - datetime.timedelta(days=10), time
            )
            self.assertIsInstance(srcprice, list)
            self.assertIsInstance(srcprice[-1], source.SourcePrice)
            self.assertEqual(Decimal("5.1890"), srcprice[-1].price)
            self.assertEqual("CNY", srcprice[-1].quote_currency)
            self.assertEqual(
                datetime.datetime(2020, 10, 9, 15, 0, 0, tzinfo=eastmoneyfund.TIMEZONE),
                srcprice[-1].time,
            )
            self.assertIsInstance(srcprice[0], source.SourcePrice)
            self.assertEqual(Decimal("4.8310"), srcprice[0].price)
            self.assertEqual("CNY", srcprice[0].quote_currency)
            self.assertEqual(
                datetime.datetime(2020, 9, 10, 15, 0, 0, tzinfo=eastmoneyfund.TIMEZONE),
                srcprice[0].time,
            )


if __name__ == "__main__":
    unittest.main()
