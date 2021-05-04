from beancount.core import convert as convert, getters as getters, inventory as inventory
from beancount.core.amount import Amount as Amount
from beancount.core.data import Posting as Posting, Transaction as Transaction
from beancount.core.inventory import Inventory as Inventory
from beancount.core.number import D as D, MISSING as MISSING, ONE as ONE, ZERO as ZERO
from beancount.core.position import Cost as Cost, CostSpec as CostSpec
from beancount.utils import defdict as defdict
from collections import namedtuple
from typing import Any, Optional

MAXIMUM_TOLERANCE: Any
MAX_TOLERANCE_DIGITS: int

def is_tolerance_user_specified(tolerance: Any): ...

BalanceError = namedtuple('BalanceError', 'source message entry')

def has_nontrivial_balance(posting: Any): ...
def compute_residual(postings: Any): ...
def infer_tolerances(postings: Any, options_map: Any, use_cost: Optional[Any] = ...): ...

AUTOMATIC_META: str
AUTOMATIC_RESIDUAL: str
AUTOMATIC_TOLERANCES: str

def get_residual_postings(residual: Any, account_rounding: Any): ...
def fill_residual_posting(entry: Any, account_rounding: Any): ...
def compute_entries_balance(entries: Any, prefix: Optional[Any] = ..., date: Optional[Any] = ...): ...
def compute_entry_context(entries: Any, context_entry: Any, additional_accounts: Optional[Any] = ...): ...
def quantize_with_tolerance(tolerances: Any, currency: Any, number: Any): ...
