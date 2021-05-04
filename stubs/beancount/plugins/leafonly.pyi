from beancount.core import data as data, getters as getters, realization as realization
from collections import namedtuple
from typing import Any

__plugins__: Any

LeafOnlyError = namedtuple('LeafOnlyError', 'source message entry')

def validate_leaf_only(entries: Any, unused_options_map: Any): ...
