from beancount.core import data as data, display_context as display_context, getters as getters, inventory as inventory, number as number, position as position, prices as prices
from beancount.ops import summarize as summarize
from beancount.parser import options as options, printer as printer
from beancount.query import query_compile as query_compile, query_env as query_env
from beancount.utils import misc_utils as misc_utils
from typing import Any

def filter_entries(c_from: Any, entries: Any, options_map: Any, context: Any): ...
def execute_print(c_print: Any, entries: Any, options_map: Any, file: Any) -> None: ...

class Allocator:
    size: int = ...
    def __init__(self) -> None: ...
    def allocate(self): ...
    def create_store(self): ...

class RowContext:
    posting: Any = ...
    entry: Any = ...
    balance: Any = ...
    options_map: Any = ...
    account_types: Any = ...
    open_close_map: Any = ...
    commodity_map: Any = ...
    price_map: Any = ...

def uses_balance_column(c_expr: Any): ...
def row_sortkey(order_indexes: Any, values: Any, c_exprs: Any): ...
def create_row_context(entries: Any, options_map: Any): ...
def execute_query(query: Any, entries: Any, options_map: Any): ...
def flatten_results(result_types: Any, result_rows: Any): ...
