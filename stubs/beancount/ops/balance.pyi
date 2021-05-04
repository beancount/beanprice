from beancount.core import account as account, amount as amount, getters as getters, realization as realization
from beancount.core.data import Balance as Balance, Transaction as Transaction
from beancount.core.number import ONE as ONE, ZERO as ZERO
from collections import namedtuple
from typing import Any

__plugins__: Any

BalanceError = namedtuple('BalanceError', 'source message entry')

def get_balance_tolerance(balance_entry: Any, options_map: Any): ...
def check(entries: Any, options_map: Any): ...
