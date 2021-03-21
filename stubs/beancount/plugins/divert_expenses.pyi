from beancount.core import account_types as account_types
from beancount.core.data import Transaction as Transaction
from beancount.parser import options as options
from typing import Any

__plugins__: Any

def divert_expenses(entries: Any, options_map: Any, config_str: Any): ...
def replace_diverted_accounts(entry: Any, replacement_account: Any, acctypes: Any): ...
