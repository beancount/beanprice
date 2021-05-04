from beancount.core import account as account, convert as convert, data as data, inventory as inventory
from beancount.core.data import Posting as Posting, Transaction as Transaction
from typing import Any

__plugins__: Any
META_PROCESSED: str
DEFAULT_BASE_ACCOUNT: str

def insert_currency_trading_postings(entries: Any, options_map: Any, config: Any): ...
def group_postings_by_weight_currency(entry: Transaction) -> Any: ...
def get_neutralizing_postings(curmap: Any, base_account: Any, new_accounts: Any): ...
