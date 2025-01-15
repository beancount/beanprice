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
}


class EastMoneyFundError(ValueError):
    "An error from the EastMoneyFund API."


UnsupportTickerError = EastMoneyFundError("header not match, dont support this ticker type")


def parse_page(page):
    tr_re = re.compile(r"<tr>(.*?)</tr>")
    item_re = re.compile(
        r"<td>(\d{4}-\d{2}-\d{2})</td><td.*?>(.*?)</td><td.*?>(.*?)</td>"
        "<td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?></td>",
        re.X,
    )
    header_match = re.compile(
        r"<th.*?净值日期</th><th>单位净值</th><th>累计净值</th><th>日增长率</th>"
        "<th>申购状态</th><th>赎回状态</th>.*?分红送配</th>"
    )
    table = tr_re.findall(page)
    if not header_match.match(table[0]):
        raise UnsupportTickerError
    try:
        table = [
            (
                datetime.datetime.fromisoformat(t[0]).replace(hour=15, tzinfo=TIMEZONE),
                Decimal(t[1]),
            )
            for t in [item_re.match(x).groups() for x in table[1:]]
        ]
    except AttributeError:
        return None
    return table


def get_price_series(
    ticker: str, time_begin: datetime.datetime, time_end: datetime.datetime
):
    base_url = "https://fundf10.eastmoney.com/F10DataApi.aspx"
    time_delta_day = (time_end - time_begin).days + 1
    pages = time_delta_day // 30 + 1
    res = []
    for page in range(1, pages + 1):
        query = {
            "code": ticker,
            "page": page,
            "sdate": time_begin.astimezone(TIMEZONE).date().isoformat(),
            "edate": time_end.astimezone(TIMEZONE).date().isoformat(),
            "type": "lsjz",
            "per": 30,
        }
        response = requests.get(base_url, params=query, headers=headers)
        if response.status_code != requests.codes.ok:
            raise EastMoneyFundError(
                f"Invalid response ({response.status_code}): {response.text}"
            )

        price = parse_page(response.text)
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
