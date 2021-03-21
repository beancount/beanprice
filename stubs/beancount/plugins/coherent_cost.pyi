from beancount.core import data as data
from collections import namedtuple
from typing import Any

__plugins__: Any

CoherentCostError = namedtuple('CoherentCostError', 'source message entry')

def validate_coherent_cost(entries: Any, unused_options_map: Any): ...
