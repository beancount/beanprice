from beancount.core import account_types as account_types, amount as amount, data as data
from beancount.core.number import MISSING as MISSING
from beancount.parser import printer as printer
from typing import Any

__plugins__: Any
DEBUG: int

def add_ira_contribs(entries: Any, options_map: Any, config_str: Any): ...
def add_postings(entry: Any, amount_: Any, neg_account: Any, pos_account: Any, flag: Any): ...
