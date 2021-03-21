from beancount.core import inventory as inventory
from beancount.query import query_parser as query_parser
from collections import namedtuple
from typing import Any

SUPPORT_IMPLICIT_GROUPBY: bool

class CompilationError(Exception): ...

class EvalNode:
    dtype: Any = ...
    def __init__(self, dtype: Any) -> None: ...
    def __eq__(self, other: Any) -> Any: ...
    def childnodes(self) -> None: ...
    def __call__(self, context: Any) -> None: ...

class EvalConstant(EvalNode):
    value: Any = ...
    def __init__(self, value: Any) -> None: ...
    def __call__(self, _: Any): ...

class EvalUnaryOp(EvalNode):
    operand: Any = ...
    operator: Any = ...
    def __init__(self, operator: Any, operand: Any, dtype: Any) -> None: ...
    def __call__(self, context: Any): ...

class EvalNot(EvalUnaryOp):
    def __init__(self, operand: Any) -> None: ...

class EvalBinaryOp(EvalNode):
    operator: Any = ...
    left: Any = ...
    right: Any = ...
    def __init__(self, operator: Any, left: Any, right: Any, dtype: Any) -> None: ...
    def __call__(self, context: Any): ...

class EvalEqual(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalAnd(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalOr(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalGreater(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalGreaterEq(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalLess(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalLessEq(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalMatch(EvalBinaryOp):
    @staticmethod
    def match(left: Any, right: Any): ...
    def __init__(self, left: Any, right: Any) -> None: ...

class EvalContains(EvalBinaryOp):
    def __init__(self, left: Any, right: Any) -> None: ...
    def __call__(self, context: Any): ...

class EvalMul(EvalBinaryOp):
    def __init__(self, left: Any, right: Any): ...

class EvalDiv(EvalBinaryOp):
    def __init__(self, left: Any, right: Any): ...

class EvalAdd(EvalBinaryOp):
    def __init__(self, left: Any, right: Any): ...

class EvalSub(EvalBinaryOp):
    def __init__(self, left: Any, right: Any): ...

OPERATORS: Any
ANY: Any

class EvalFunction(EvalNode):
    __intypes__: Any = ...
    operands: Any = ...
    def __init__(self, operands: Any, dtype: Any) -> None: ...
    def eval_args(self, context: Any): ...

class EvalColumn(EvalNode): ...

class EvalAggregator(EvalFunction):
    def allocate(self, allocator: Any) -> None: ...
    def initialize(self, store: Any) -> None: ...
    def update(self, store: Any, context: Any) -> None: ...
    def finalize(self, store: Any) -> None: ...
    def __call__(self, context: Any) -> None: ...

class CompilationEnvironment:
    context_name: Any = ...
    columns: Any = ...
    functions: Any = ...
    def get_column(self, name: Any): ...
    def get_function(self, name: Any, operands: Any): ...

class AttributeColumn(EvalColumn):
    def __call__(self, row: Any): ...

class ResultSetEnvironment(CompilationEnvironment):
    context_name: str = ...
    def get_column(self, name: Any): ...

def compile_expression(expr: Any, environ: Any): ...
def get_columns_and_aggregates(node: Any): ...
def is_aggregate(node: Any): ...
def is_hashable_type(node: Any): ...
def find_unique_name(name: Any, allocated_set: Any): ...

EvalTarget = namedtuple('EvalTarget', 'c_expr name is_aggregate')

def compile_targets(targets: Any, environ: Any): ...
def compile_group_by(group_by: Any, c_targets: Any, environ: Any): ...
def compile_order_by(order_by: Any, c_targets: Any, environ: Any): ...

EvalFrom = namedtuple('EvalFrom', 'c_expr open close clear')

def compile_from(from_clause: Any, environ: Any): ...

EvalQuery = namedtuple('EvalQuery', 'c_targets c_from c_where group_indexes order_indexes ordering limit distinct flatten')

def compile_select(select: Any, targets_environ: Any, postings_environ: Any, entries_environ: Any): ...
def transform_journal(journal: Any): ...
def transform_balances(balances: Any): ...

EvalPrint = namedtuple('EvalPrint', 'c_from')

def compile_print(print_stmt: Any, env_entries: Any): ...
def compile(statement: Any, targets_environ: Any, postings_environ: Any, entries_environ: Any): ...
