from beancount.core import amount as amount, data as data, inventory as inventory
from beancount.core.data import Transaction as Transaction
from collections import namedtuple
from typing import Any

__plugins__: Any

ImplicitPriceError = namedtuple('ImplicitPriceError', 'source message entry')
METADATA_FIELD: str

def add_implicit_prices(entries: Any, unused_options_map: Any): ...
