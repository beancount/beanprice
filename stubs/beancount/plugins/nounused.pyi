from beancount.core import data as data, getters as getters
from collections import namedtuple
from typing import Any

__plugins__: Any

UnusedAccountError = namedtuple('UnusedAccountError', 'source message entry')

def validate_unused_accounts(entries: Any, unused_options_map: Any): ...
