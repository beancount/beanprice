"""
A source fetching fund price(net value) from eastmoneyfund(天天基金)
which is a chinese securities company.

eastmoneyfund supports many kinds of fund, such as fixed income fund, ETF, etc.
This source uses https://api.fund.eastmoney.com/f10/lsjz for historical unit NAV.
Money-market yield tables are deliberately unsupported. parse_page is retained
for callers that need to read previously saved legacy HTML responses.

the API, as far as I know, is undocumented.

Prices are denoted in CNY.
Timezone information: the http API requests GMT+8,
    the function transfers timezone to GMT+8 automatically
"""

import datetime
import re
from decimal import Decimal, InvalidOperation
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
    if not table or not header_match.match(table[0]):
        raise UnsupportTickerError
    try:
        table = [
            (
                datetime.datetime.fromisoformat(t[0]).replace(hour=15, tzinfo=TIMEZONE),
                Decimal(t[1]),
            )
            for t in [item_re.match(x).groups() for x in table[1:]]
        ]
    except (AttributeError, ValueError, InvalidOperation) as exc:
        raise EastMoneyFundError("Malformed fund price row") from exc
    if any(not value.is_finite() or value <= 0 for _, value in table):
        raise EastMoneyFundError("Non-positive or non-finite fund NAV")
    return table


def get_price_series(ticker, time_begin, time_end):
    """Fetch native CNY NAV from the current paginated JSON endpoint.

    Money-market per-10,000 income and annualized yield are not unit prices.
    The legacy F10DataApi.aspx endpoint now returns HTTP 404.
    """
    if not ticker.isdigit() or len(ticker) != 6:
        raise EastMoneyFundError("Expected a six-digit fund code")
    begin_date = time_begin.astimezone(TIMEZONE).date()
    end_date = time_end.astimezone(TIMEZONE).date()
    if begin_date > end_date:
        raise EastMoneyFundError("Start date is after end date")
    by_date = {}
    page = 1
    received = 0
    while True:
        response = requests.get(
            "https://api.fund.eastmoney.com/f10/lsjz",
            params={"fundCode": ticker, "pageIndex": page, "pageSize": 30,
                    "startDate": begin_date.isoformat(), "endDate": end_date.isoformat()},
            headers={**headers, "Referer": "https://fundf10.eastmoney.com/"},
            timeout=30,
        )
        if response.status_code != requests.codes.ok:
            raise EastMoneyFundError(f"Invalid response ({response.status_code})")
        payload = response.json()
        if not isinstance(payload, dict) or payload.get("ErrCode") != 0:
            raise EastMoneyFundError("Fund API error")
        try:
            rows = payload["Data"]["LSJZList"]
            total = int(payload["TotalCount"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EastMoneyFundError("Malformed fund API response") from exc
        if payload.get("PageIndex", page) != page:
            raise EastMoneyFundError("Fund API returned the wrong page")
        if not isinstance(rows, list) or total < 0:
            raise EastMoneyFundError("Invalid fund pagination")
        if not rows:
            if received < total:
                raise EastMoneyFundError("Incomplete fund pagination")
            break
        for row in rows:
            if row.get("NAVTYPE") != "1" or row.get("ACTUALSYI"):
                raise UnsupportTickerError
            try:
                observed = datetime.datetime.fromisoformat(row["FSRQ"]).replace(
                    hour=15, tzinfo=TIMEZONE)
                value = Decimal(row["DWJZ"])
            except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
                raise EastMoneyFundError("Malformed NAV row") from exc
            if not value.is_finite() or value <= 0:
                raise EastMoneyFundError("Non-positive or non-finite NAV")
            if begin_date <= observed.date() <= end_date:
                if observed in by_date and by_date[observed] != value:
                    raise EastMoneyFundError(f"Conflicting NAV for {observed.date()}")
                by_date[observed] = value
        received += len(rows)
        if received >= total:
            break
        if page >= 1000:
            raise EastMoneyFundError("Fund pagination exceeded 1000 pages")
        page += 1
    if not by_date:
        raise EastMoneyFundError(f"No NAV within requested dates for {ticker}")
    return sorted(by_date.items(), reverse=True)


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
