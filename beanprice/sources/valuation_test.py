"""Regression checks for financial quote integrity (no live network)."""
import datetime as dt
from decimal import Decimal, getcontext
from unittest.mock import patch

import pytest

from beanprice.sources import eastmoneystock as stock, eastmoneyfund as fund, ecbrates
from beanprice.sources.eastmoneystock_test import mock_response, KLINE_RESPONSE
from beanprice.sources.eastmoneyfund_test import CONTENTS, response


@pytest.mark.parametrize("value", ["NaN", "Infinity", "0", "-1", "bad"])
def test_invalid_stock_prices(value):
    with pytest.raises(ValueError):
        stock._parse_kline_data({"data": {"klines": [f"2024-01-05,{value}"]}})


@pytest.mark.parametrize("ticker", ["200001", "900901", "80700"])
def test_unsupported_currency_counters(ticker):
    with pytest.raises(ValueError):
        stock._get_market_and_currency(ticker)


def test_stock_never_uses_future_day():
    with mock_response(KLINE_RESPONSE):
        value = stock.Source().get_historical_price(
            "600519", dt.datetime(2024, 1, 6, tzinfo=stock.TIMEZONE))
    assert value.time.date() == dt.date(2024, 1, 5)
    assert value.price == Decimal("1694.00")


def test_wrong_security_rejected():
    with mock_response(KLINE_RESPONSE), pytest.raises(ValueError):
        stock.Source().get_historical_price(
            "00700", dt.datetime(2024, 1, 6, tzinfo=stock.TIMEZONE))


def test_fund_future_records_filtered():
    with response(CONTENTS):
        value = fund.Source().get_historical_price(
            "377240", dt.datetime(2020, 10, 1, tzinfo=fund.TIMEZONE))
    assert value.time.date() == dt.date(2020, 9, 30)


def test_fund_empty_page_is_controlled_error():
    with pytest.raises(ValueError):
        fund.parse_page("<html>service unavailable</html>")


def test_ecb_does_not_change_decimal_context():
    precision = getcontext().prec
    with patch.object(ecbrates, "_get_rate_EUR_to_CCY", side_effect=[
        (Decimal("8.5"), "2024-01-05", 2),
        (Decimal("7.8"), "2024-01-05", 2),
    ]):
        value = ecbrates.Source().get_latest_price("HKD-CNY")
    assert getcontext().prec == precision
    assert abs(value.price - Decimal("0.9176470588235294117647058824")) < Decimal("1e-27")
