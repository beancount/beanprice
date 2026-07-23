"""
A source fetching fund price(net value) from eastmoneyfund(天天基金)
which is a chinese securities company.

eastmoneyfund supports many kinds of fund, such as fixed income fund, ETF, etc.
this script only supports specific fund which table's header is following:
https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code=377240.

fixed income fund is not supported, likes:
https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code=040003

the API, as far as I know, is undocumented.

Prices are denoted in CNY.
Timezone information: the http API requests GMT+8,
    the function transfers timezone to GMT+8 automatically
"""

import datetime
import json
from pathlib import Path
import re
from decimal import Decimal
import requests
from beanprice import source


# All of the easymoney funds are in CNY.
CURRENCY = "CNY"

TIMEZONE = datetime.timezone(datetime.timedelta(hours=+8), "Asia/Shanghai")


headers = {
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0)"
    "Gecko/20100101 Firefox/22.0",
    "Referer": "http://fundf10.eastmoney.com/"
}


class EastMoneyFundError(ValueError):
    "An error from the EastMoneyFund API."


UnsupportTickerError = EastMoneyFundError("header not match, dont support this ticker type")


def parse_json(json_data):
    data = json_data.get("Data")
    if not data or not data.get("LSJZList"):
        return None

    try:
        return [
            (
                datetime.datetime.fromisoformat(item["FSRQ"]).replace(
                    hour=15,
                    tzinfo=TIMEZONE,
                ),
                Decimal(item["DWJZ"]),
            )
            for item in data["LSJZList"]
        ]
    except (KeyError, TypeError, ValueError):
        return None


def get_price_series(
    ticker: str, time_begin: datetime.datetime, time_end: datetime.datetime
):
    base_url = "http://api.fund.eastmoney.com/f10/lsjz"
    time_delta_day = (time_end - time_begin).days + 1
    pages = time_delta_day // 30 + 1
    res = []
    for page in range(1, pages + 1):
        query = {
            "fundCode": ticker,
            "pageIndex": str(page),
            "startDate": time_begin.astimezone(TIMEZONE).date().isoformat(),
            "endDate": time_end.astimezone(TIMEZONE).date().isoformat(),
            "pageSize": str(30),
        }
        response = requests.get(base_url, params=query, headers=headers)
        if response.status_code != requests.codes.ok:
            raise EastMoneyFundError(
                f"Invalid response ({response.status_code}): {response.text}"
            )
        json_data = response.json()
        price = parse_json(json_data)
        if price is None and page == 1:
            raise EastMoneyFundError(
                f"Invalid ticker {ticker} or "
                f"search day {time_begin.date().isoformat()}~{time_end.date().isoformat()}"
            )
        if price is None:
            break
        res.extend(price)
    return res


class Source(source.Source):
    def get_latest_price(self, ticker):
        end_time = datetime.datetime.now(TIMEZONE)
        begin_time = end_time - datetime.timedelta(days=10)
        prices = get_price_series(ticker, begin_time, end_time)
        last_price = prices[0]
        return source.SourcePrice(last_price[1], last_price[0], CURRENCY)

    def get_historical_price(self, ticker, time):
        prices = get_price_series(ticker, time - datetime.timedelta(days=10), time)
        last_price = prices[0]
        return source.SourcePrice(last_price[1], last_price[0], CURRENCY)

    def get_prices_series(self, ticker, time_begin, time_end):
        res = [
            source.SourcePrice(x[1], x[0], CURRENCY)
            for x in get_price_series(ticker, time_begin, time_end)
        ]
        return sorted(res, key=lambda x: x.time)
