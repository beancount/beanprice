import requests
from beancount.core.number import D as D
from beancount.prices import source as source
from collections import OrderedDict
from typing import Any

CURRENCY: str
TIMEZONE: Any
TSP_FUND_NAMES: Any

class TSPError(ValueError): ...

def parse_tsp_csv(response: requests.models.Response) -> OrderedDict: ...
def parse_response(response: requests.models.Response) -> OrderedDict: ...

class Source(source.Source):
    def get_latest_price(self, fund: Any): ...
    def get_historical_price(self, fund: Any, time: Any): ...
