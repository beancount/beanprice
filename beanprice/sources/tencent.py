"""Unadjusted daily closes from Tencent's public, undocumented quote API.

Symbols use the same six-digit mainland / five-digit HKD convention as
East Money. The empty adjustment parameter and the `day` response key are
intentional: qfqday/hfqday are not raw market prices and must not be substituted.
"""
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import requests

from beanprice import source
from beanprice.sources.eastmoneystock import TIMEZONE, _get_market_and_currency


class TencentError(ValueError):
    """An invalid or unavailable Tencent daily quote."""


def _parse(payload, symbol, currency):
    try:
        if payload["code"] != 0:
            raise TencentError("Tencent API error")
        security = payload["data"][symbol]
        rows = security["day"]
        quote = security.get("qt", {}).get(symbol)
        if quote and (quote[2] != symbol[2:] or currency not in quote):
            raise TencentError("Security or currency mismatch")
        result = {}
        for row in rows:
            stamp = datetime.fromisoformat(row[0]).replace(
                hour=16 if currency == "HKD" else 15, tzinfo=TIMEZONE)
            close = Decimal(row[2])
            if not close.is_finite() or close <= 0:
                raise TencentError("Non-positive or non-finite close")
            if stamp in result and result[stamp] != close:
                raise TencentError(f"Conflicting close for {stamp.date()}")
            result[stamp] = close
        return result
    except (KeyError, IndexError, TypeError, InvalidOperation) as exc:
        raise TencentError("Malformed or missing unadjusted daily prices") from exc


def get_price_series(ticker, time_begin, time_end):
    market, currency = _get_market_and_currency(ticker)
    symbol = {"0": "sz", "1": "sh", "116": "hk"}[market] + ticker
    begin, end = time_begin.astimezone(TIMEZONE).date(), time_end.astimezone(TIMEZONE).date()
    if begin > end:
        raise TencentError("Start date is after end date")
    result = {}
    cursor = begin
    while cursor <= end:
        # Stay within the endpoint's daily-record limit, including long backfills.
        stop = min(end, cursor + timedelta(days=499))
        response = requests.get(
            "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",
            params={"param": f"{symbol},day,{cursor},{stop},500,"},
            headers={"Referer": "https://gu.qq.com/", "User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
        if response.status_code != requests.codes.ok:
            raise TencentError(f"Invalid response ({response.status_code})")
        for stamp, value in _parse(response.json(), symbol, currency).items():
            if cursor <= stamp.date() <= stop:
                result[stamp] = value
        cursor = stop + timedelta(days=1)
    if not result:
        raise TencentError(f"No closing price in requested range for {ticker}")
    return sorted(result.items())


class Source(source.Source):
    """Native CNY/HKD daily closing prices."""

    def get_latest_price(self, ticker):
        return self.get_historical_price(ticker, datetime.now(TIMEZONE))

    def get_historical_price(self, ticker, time):
        _, currency = _get_market_and_currency(ticker)
        rows = get_price_series(ticker, time - timedelta(days=10), time)
        stamp, close = rows[-1]
        return source.SourcePrice(close, stamp, currency)

    def get_prices_series(self, ticker, time_begin, time_end):
        _, currency = _get_market_and_currency(ticker)
        return [source.SourcePrice(close, stamp, currency)
                for stamp, close in get_price_series(ticker, time_begin, time_end)]
