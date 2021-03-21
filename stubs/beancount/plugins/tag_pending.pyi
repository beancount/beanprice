from beancount.core import inventory as inventory
from beancount.ops import basicops as basicops
from typing import Any

__plugins__: Any

def tag_pending_transactions(entries: Any, tag_name: str = ...): ...
def tag_pending_plugin(entries: Any, options_map: Any): ...
