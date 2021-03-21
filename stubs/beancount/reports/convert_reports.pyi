from beancount.core import amount as amount, convert as convert, data as data, display_context as display_context, interpolate as interpolate, position as position
from beancount.core.amount import Amount as Amount
from beancount.reports import base as base
from typing import Any, Optional

ROUNDING_ACCOUNT: str

def quote(match: Any): ...
def quote_currency(string: Any): ...
def postings_by_type(entry: Any): ...
def split_currency_conversions(entry: Any): ...

class LedgerReport(base.Report):
    names: Any = ...
    default_format: str = ...
    def render_ledger(self, entries: Any, errors: Any, options_map: Any, file: Any) -> None: ...

class LedgerPrinter:
    dcontext: Any = ...
    dformat: Any = ...
    dformat_max: Any = ...
    def __init__(self, dcontext: Optional[Any] = ...) -> None: ...
    def __call__(self, obj: Any): ...
    def Transaction(self, entry: Any, oss: Any) -> None: ...
    def Posting(self, posting: Any, entry: Any, oss: Any) -> None: ...
    def Balance(_: Any, entry: Any, oss: Any) -> None: ...
    def Note(_: Any, entry: Any, oss: Any) -> None: ...
    def Document(_: Any, entry: Any, oss: Any) -> None: ...
    def Pad(_: Any, entry: Any, oss: Any) -> None: ...
    def Commodity(_: Any, entry: Any, oss: Any) -> None: ...
    def Open(_: Any, entry: Any, oss: Any) -> None: ...
    def Close(_: Any, entry: Any, oss: Any) -> None: ...
    def Price(_: Any, entry: Any, oss: Any) -> None: ...
    def Event(_: Any, entry: Any, oss: Any) -> None: ...
    def Query(_: Any, entry: Any, oss: Any) -> None: ...
    def Custom(_: Any, entry: Any, oss: Any) -> None: ...

class HLedgerReport(base.Report):
    names: Any = ...
    default_format: str = ...
    def render_hledger(self, entries: Any, errors: Any, options_map: Any, file: Any) -> None: ...

class HLedgerPrinter(LedgerPrinter):
    def Transaction(self, entry: Any, oss: Any) -> None: ...
    def Posting(self, posting: Any, entry: Any, oss: Any) -> None: ...
    def Open(_: Any, entry: Any, oss: Any) -> None: ...

__reports__: Any
