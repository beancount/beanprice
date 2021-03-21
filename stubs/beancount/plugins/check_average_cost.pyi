from beancount.core import getters as getters, inventory as inventory
from beancount.core.data import Booking as Booking, Transaction as Transaction
from beancount.core.number import D as D, ZERO as ZERO
from collections import namedtuple
from typing import Any, Optional

__plugins__: Any

MatchBasisError = namedtuple('MatchBasisError', 'source message entry')
DEFAULT_TOLERANCE: float

def validate_average_cost(entries: Any, options_map: Any, config_str: Optional[Any] = ...): ...
