from beancount.core import account_types as account_types, amount as amount, convert as convert, data as data, interpolate as interpolate, inventory as inventory
from beancount.core.number import ZERO as ZERO
from beancount.parser import options as options
from collections import namedtuple
from typing import Any

__plugins__: Any

SellGainsError = namedtuple('SellGainsError', 'source message entry')
EXTRA_TOLERANCE_MULTIPLIER: int

def validate_sell_gains(entries: Any, options_map: Any): ...
