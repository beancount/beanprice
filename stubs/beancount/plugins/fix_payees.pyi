from beancount.core import data as data
from collections import namedtuple
from typing import Any

__plugins__: Any

FixPayeesError = namedtuple('FixPayeesError', 'source message entry')

def fix_payees(entries: Any, options_map: Any, config: Any): ...
