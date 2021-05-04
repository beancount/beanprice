from beancount.core import account as account, convert as convert, data as data, inventory as inventory
from collections import namedtuple
from typing import Any

__plugins__: Any

FillAccountError = namedtuple('FillAccountError', 'source message entry')

def fill_account(entries: Any, unused_options_map: Any, insert_account: Any): ...
