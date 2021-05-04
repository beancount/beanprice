from beancount.core.number import D as D
from beancount.prices import source as source
from beancount.utils import net_utils as net_utils
from typing import Any

URL: str

class Source(source.Source):
    def get_latest_price(self, ticker: Any): ...
    def get_historical_price(self, ticker: Any, time: Any): ...
