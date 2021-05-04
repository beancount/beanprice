from beancount.core import data as data
from collections import namedtuple
from typing import Any

__plugins__: Any

ConfigError = namedtuple('ConfigError', 'source message entry')

CommodityError = namedtuple('CommodityError', 'source message entry')

def validate_commodity_attr(entries: Any, unused_options_map: Any, config_str: Any): ...
