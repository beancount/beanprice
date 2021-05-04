from beancount.core import account as account, amount as amount, data as data, flags as flags, getters as getters, prices as prices
from beancount.core.data import EMPTY_SET as EMPTY_SET
from beancount.core.number import ZERO as ZERO
from beancount.ops import holdings as holdings
from beancount.parser import options as options
from collections import namedtuple
from typing import Any, Optional

__plugins__: Any

UnrealizedError = namedtuple('UnrealizedError', 'source message entry')

def add_unrealized_gains(entries: Any, options_map: Any, subaccount: Optional[Any] = ...): ...
def get_unrealized_entries(entries: Any): ...
