import datetime
import unittest
from decimal import Decimal

from unittest import mock
from dateutil import tz

import requests

from beanprice.sources import eastmoneyfund
from beanprice import source


# ruff: noqa: E501,RUF001

CONTENTS = """
var apidata={ content:"<table class='w782 comm lsjz'><thead><tr><th class='first'>净值日期</th><th>单位净值</th><th>累计净值</th><th>日增长率</th><th>申购状态</th><th>赎回状态</th><th class='tor last'>分红送配</th></tr></thead><tbody><tr><td>2020-10-09</td><td class='tor bold'>5.1890</td><td class='tor bold'>5.1890</td><td class='tor bold red'>4.11%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-30</td><td class='tor bold'>4.9840</td><td class='tor bold'>4.9840</td><td class='tor bold red'>0.12%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-29</td><td class='tor bold'>4.9780</td><td class='tor bold'>4.9780</td><td class='tor bold red'>1.14%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-28</td><td class='tor bold'>4.9220</td><td class='tor bold'>4.9220</td><td class='tor bold red'>0.22%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-25</td><td class='tor bold'>4.9110</td><td class='tor bold'>4.9110</td><td class='tor bold red'>0.88%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-24</td><td class='tor bold'>4.8680</td><td class='tor bold'>4.8680</td><td class='tor bold grn'>-3.81%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-23</td><td class='tor bold'>5.0610</td><td class='tor bold'>5.0610</td><td class='tor bold red'>2.41%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-22</td><td class='tor bold'>4.9420</td><td class='tor bold'>4.9420</td><td class='tor bold grn'>-1.02%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-21</td><td class='tor bold'>4.9930</td><td class='tor bold'>4.9930</td><td class='tor bold grn'>-1.29%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-18</td><td class='tor bold'>5.0580</td><td class='tor bold'>5.0580</td><td class='tor bold red'>0.48%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-17</td><td class='tor bold'>5.0340</td><td class='tor bold'>5.0340</td><td class='tor bold red'>0.60%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-16</td><td class='tor bold'>5.0040</td><td class='tor bold'>5.0040</td><td class='tor bold grn'>-1.28%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-15</td><td class='tor bold'>5.0690</td><td class='tor bold'>5.0690</td><td class='tor bold red'>1.06%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-14</td><td class='tor bold'>5.0160</td><td class='tor bold'>5.0160</td><td class='tor bold red'>0.42%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-11</td><td class='tor bold'>4.9950</td><td class='tor bold'>4.9950</td><td class='tor bold red'>3.39%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr><tr><td>2020-09-10</td><td class='tor bold'>4.8310</td><td class='tor bold'>4.8310</td><td class='tor bold grn'>-0.29%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></td></tr></tbody></table>",records:16,pages:1,curpage:1};\
"""

UNSUPPORT_CONTENT = """
var apidata={ content:"<table class='w782 comm lsjz'><thead><tr><th class='first'>净值日期</\
th><th>每万份收益</th><th>7日年化收益率（%）</th><th>申购状态</th><th>赎回状态</th><th class='tor \
last'>分红送配</th></tr></thead><tbody><tr><td>2020-09-10</td><td class='tor bold'>0.4230</td\
><td class='tor bold'>1.5730%</td><td>开放申购</td><td>开放赎回</td><td class='red unbold'></t\
d></tr></tbody></table>",records:1,pages:1,curpage:1};"""


def response(contents, status_code=requests.codes.ok):
    """Return a context manager to patch a JSON response."""
    response = mock.Mock()
    response.status_code = status_code
    response.text = contents
    if contents == CONTENTS:
        rows = eastmoneyfund.parse_page(contents)
        response.json.return_value = {"ErrCode": 0, "TotalCount": len(rows), "Data": {
            "LSJZList": [{"FSRQ": day.date().isoformat(), "DWJZ": str(value),
                          "NAVTYPE": "1", "ACTUALSYI": ""} for day, value in rows]}}
    else:
        response.json.return_value = {"ErrCode": 0, "TotalCount": 1, "Data": {
            "LSJZList": [{"NAVTYPE": "2", "ACTUALSYI": "1.5730"}]}}
    return mock.patch("requests.get", return_value=response)


class EastMoneyFundFetcher(unittest.TestCase):
    def test_error_network(self):
        with response(None, 404):
            with self.assertRaises(ValueError):
                eastmoneyfund.get_price_series(
                    "377240", datetime.datetime.now(), datetime.datetime.now()
                )

    def test_unsupport_page(self):
        with response(UNSUPPORT_CONTENT):
            with self.assertRaises(ValueError) as exc:
                eastmoneyfund.get_price_series(
                    "377240", datetime.datetime.now(), datetime.datetime.now()
                )
            self.assertEqual(eastmoneyfund.UnsupportTickerError, exc.exception)

    def test_latest_price(self):
        rows = eastmoneyfund.parse_page(CONTENTS)
        with mock.patch.object(eastmoneyfund, "get_price_series", return_value=rows):
            srcprice = eastmoneyfund.Source().get_latest_price("377240")
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("5.1890"), srcprice.price)
            self.assertEqual("CNY", srcprice.quote_currency)

    def test_historical_price(self):
        with response(CONTENTS):
            time = datetime.datetime(2020, 10, 9, 0, 0, 0, tzinfo=tz.tzutc())
            srcprice = eastmoneyfund.Source().get_historical_price("377240", time)
            self.assertIsInstance(srcprice, source.SourcePrice)
            self.assertEqual(Decimal("5.1890"), srcprice.price)
            self.assertEqual("CNY", srcprice.quote_currency)
            self.assertEqual(
                datetime.datetime(2020, 10, 9, 15, 0, 0, tzinfo=eastmoneyfund.TIMEZONE),
                srcprice.time,
            )

    def test_get_prices_series(self):
        with response(CONTENTS):
            time = datetime.datetime(2020, 10, 9, 0, 0, 0, tzinfo=tz.tzutc())
            srcprice = eastmoneyfund.Source().get_prices_series(
                "377240", time - datetime.timedelta(days=30), time
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



class FundPaginationRegression(unittest.TestCase):
    @staticmethod
    def page(index, rows, total=2):
        value = mock.Mock(status_code=200)
        value.json.return_value = {"ErrCode": 0, "PageIndex": index,
                                  "TotalCount": total, "Data": {"LSJZList": rows}}
        return value

    @staticmethod
    def row(day, value="1.2"):
        return {"FSRQ": day, "DWJZ": value, "NAVTYPE": "1", "ACTUALSYI": ""}

    def fetch(self):
        return eastmoneyfund.get_price_series(
            "022947", datetime.datetime(2026, 9, 1, tzinfo=eastmoneyfund.TIMEZONE),
            datetime.datetime(2026, 9, 11, tzinfo=eastmoneyfund.TIMEZONE))

    def test_all_pages_fetched(self):
        pages = [self.page(1, [self.row("2026-09-11")]),
                 self.page(2, [self.row("2026-09-10")])]
        with mock.patch("requests.get", side_effect=pages) as get:
            result = self.fetch()
        self.assertEqual(2, len(result))
        self.assertEqual([1, 2], [call.kwargs["params"]["pageIndex"]
                                  for call in get.call_args_list])

    def test_repeated_page_is_rejected(self):
        page = self.page(1, [self.row("2026-09-11")])
        with mock.patch("requests.get", return_value=page), self.assertRaises(ValueError):
            self.fetch()

    def test_truncated_pagination_is_rejected(self):
        pages = [self.page(1, [self.row("2026-09-11")]), self.page(2, [])]
        with mock.patch("requests.get", side_effect=pages), self.assertRaises(ValueError):
            self.fetch()

    def test_nonfinite_nav_is_rejected(self):
        page = self.page(1, [self.row("2026-09-11", "NaN")], total=1)
        with mock.patch("requests.get", return_value=page), self.assertRaises(ValueError):
            self.fetch()


if __name__ == "__main__":
    unittest.main()
