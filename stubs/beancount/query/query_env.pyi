from beancount.core import account as account, account_types as account_types, amount as amount, convert as convert, data as data, getters as getters, inventory as inventory, position as position, prices as prices
from beancount.core.compare import hash_entry as hash_entry
from beancount.core.data import Transaction as Transaction
from beancount.core.number import ZERO as ZERO
from beancount.query import query_compile as query_compile
from beancount.utils.date_utils import parse_date_liberally as parse_date_liberally
from typing import Any

class _Neg(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class NegDecimal(_Neg):
    __intypes__: Any = ...

class NegAmount(_Neg):
    __intypes__: Any = ...

class NegPosition(_Neg):
    __intypes__: Any = ...

class NegInventory(_Neg):
    __intypes__: Any = ...

class AbsDecimal(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class AbsPosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class AbsInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class SafeDiv(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class SafeDivInt(SafeDiv):
    __intypes__: Any = ...

class Length(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Str(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class MaxWidth(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Year(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Month(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class YearMonth(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Quarter(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Day(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Weekday(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Today(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Root(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Parent(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Leaf(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Grep(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class GrepN(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Subst(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Upper(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Lower(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class OpenDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class CloseDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Meta(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class EntryMeta(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class AnyMeta(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class OpenMeta(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class AccountSortKey(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class CurrencyMeta(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class UnitsPosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class UnitsInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class CostPosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class CostInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ConvertAmount(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ConvertAmountWithDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ConvertPosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ConvertPositionWithDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ValuePosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ValuePositionWithDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ConvertInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ConvertInventoryWithDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ValueInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ValueInventoryWithDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Price(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class PriceWithDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Number(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Currency(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class GetItemStr(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class FindFirst(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class JoinStr(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class OnlyInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class FilterCurrencyPosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class FilterCurrencyInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class PosSignDecimal(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class PosSignAmount(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class PosSignPosition(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class PosSignInventory(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Coalesce(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class Date(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class ParseDate(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class DateDiff(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

class DateAdd(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

SIMPLE_FUNCTIONS: Any

class Count(query_compile.EvalAggregator):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, unused_ontext: Any) -> None: ...
    def __call__(self, context: Any): ...

class Sum(query_compile.EvalAggregator):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, context: Any) -> None: ...
    def __call__(self, context: Any): ...

class SumBase(query_compile.EvalAggregator):
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def __call__(self, context: Any): ...

class SumAmount(SumBase):
    __intypes__: Any = ...
    def update(self, store: Any, context: Any) -> None: ...

class SumPosition(SumBase):
    __intypes__: Any = ...
    def update(self, store: Any, context: Any) -> None: ...

class SumInventory(SumBase):
    __intypes__: Any = ...
    def update(self, store: Any, context: Any) -> None: ...

class First(query_compile.EvalAggregator):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, context: Any) -> None: ...
    def __call__(self, context: Any): ...

class Last(query_compile.EvalAggregator):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, context: Any) -> None: ...
    def __call__(self, context: Any): ...

class Min(query_compile.EvalAggregator):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, context: Any) -> None: ...
    def __call__(self, context: Any): ...

class Max(query_compile.EvalAggregator):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    handle: Any = ...
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, context: Any) -> None: ...
    def __call__(self, context: Any): ...

AGGREGATOR_FUNCTIONS: Any

class IdEntryColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class TypeEntryColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class FilenameEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class LineNoEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class DateEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class YearEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class MonthEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class DayEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class FlagEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class PayeeEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class NarrationEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class DescriptionEntryColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

EMPTY_SET: Any

class TagsEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class LinksEntryColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class MatchAccount(query_compile.EvalFunction):
    __intypes__: Any = ...
    def __init__(self, operands: Any) -> None: ...
    def __call__(self, context: Any): ...

ENTRY_FUNCTIONS: Any

class FilterEntriesEnvironment(query_compile.CompilationEnvironment):
    context_name: str = ...
    columns: Any = ...
    functions: Any = ...

class IdColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class TypeColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class FilenameColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class LineNoColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class FileLocationColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class DateColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class YearColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class MonthColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class DayColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class FlagColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class PayeeColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class NarrationColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class DescriptionColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class TagsColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class LinksColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class PostingFlagColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class AccountColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class OtherAccountsColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class NumberColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class CurrencyColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class CostNumberColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class CostCurrencyColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class CostDateColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class CostLabelColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class PositionColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class PriceColumn(query_compile.EvalColumn):
    __equivalent__: str = ...
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class WeightColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class BalanceColumn(query_compile.EvalColumn):
    __intypes__: Any = ...
    def __init__(self) -> None: ...
    def __call__(self, context: Any): ...

class FilterPostingsEnvironment(query_compile.CompilationEnvironment):
    context_name: str = ...
    columns: Any = ...
    functions: Any = ...

class TargetsEnvironment(FilterPostingsEnvironment):
    context_name: str = ...
    functions: Any = ...
    wildcard_columns: Any = ...
