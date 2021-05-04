from beancount.core import data as data
from beancount.core.amount import CURRENCY_RE as CURRENCY_RE
from collections import namedtuple
from typing import Any

__plugins__: Any

CheckCommodityError = namedtuple('CheckCommodityError', 'source message entry')

def get_commodity_map_ex(entries: Any, metadata: bool = ...): ...
def validate_commodity_directives(entries: Any, options_map: Any): ...
