from beancount.core import data as data
from collections import namedtuple
from typing import Any

__plugins__: Any

UniquePricesError = namedtuple('UniquePricesError', 'source message entry')

def validate_unique_prices(entries: Any, unused_options_map: Any): ...
