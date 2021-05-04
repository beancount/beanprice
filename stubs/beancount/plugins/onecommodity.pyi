from beancount.core import data as data
from collections import namedtuple
from typing import Any, Optional

__plugins__: Any

OneCommodityError = namedtuple('OneCommodityError', 'source message entry')

def validate_one_commodity(entries: Any, unused_options_map: Any, config: Optional[Any] = ...): ...
