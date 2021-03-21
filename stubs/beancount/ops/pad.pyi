from beancount.core import account as account, amount as amount, data as data, flags as flags, inventory as inventory, position as position, realization as realization
from beancount.ops import balance as balance
from beancount.utils import misc_utils as misc_utils
from collections import namedtuple
from typing import Any

__plugins__: Any

PadError = namedtuple('PadError', 'source message entry')

def pad(entries: Any, options_map: Any): ...
