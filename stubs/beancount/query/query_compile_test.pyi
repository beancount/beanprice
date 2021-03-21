import unittest
from beancount.core.number import D as D
from typing import Any

class TestCompileExpression(unittest.TestCase):
    def test_expr_invalid(self) -> None: ...
    def test_expr_column(self) -> None: ...
    def test_expr_function(self) -> None: ...
    def test_expr_unaryop(self) -> None: ...
    def test_expr_binaryop(self) -> None: ...
    def test_expr_constant(self) -> None: ...

class TestCompileExpressionDataTypes(unittest.TestCase):
    def test_expr_function_arity(self) -> None: ...

class TestCompileAggregateChecks(unittest.TestCase):
    def test_is_aggregate_derived(self) -> None: ...
    def test_get_columns_and_aggregates(self) -> None: ...

class TestCompileDataTypes(unittest.TestCase):
    def test_compile_EvalConstant(self) -> None: ...
    def test_compile_EvalNot(self) -> None: ...
    def test_compile_EvalEqual(self) -> None: ...
    def test_compile_EvalGreater(self) -> None: ...
    def test_compile_EvalGreaterEq(self) -> None: ...
    def test_compile_EvalLess(self) -> None: ...
    def test_compile_EvalLessEq(self) -> None: ...
    def test_compile_EvalMatch(self) -> None: ...
    def test_compile_EvalAnd(self) -> None: ...
    def test_compile_EvalOr(self) -> None: ...
    def test_compile_EvalMul(self) -> None: ...
    def test_compile_EvalDiv(self) -> None: ...
    def test_compile_EvalAdd(self) -> None: ...
    def test_compile_EvalSub(self) -> None: ...

class TestCompileMisc(unittest.TestCase):
    def test_find_unique_names(self) -> None: ...

class CompileSelectBase(unittest.TestCase):
    maxDiff: int = ...
    xcontext_entries: Any = ...
    xcontext_targets: Any = ...
    xcontext_postings: Any = ...
    parser: Any = ...
    def setUp(self) -> None: ...
    def parse(self, query: Any): ...
    def compile(self, query: Any): ...
    def assertSelectInvariants(self, query: Any) -> None: ...
    def assertIndexes(self, query: Any, expected_simple_indexes: Any, expected_aggregate_indexes: Any, expected_group_indexes: Any, expected_order_indexes: Any) -> None: ...
    def assertCompile(self, expected: Any, query: Any, debug: bool = ...): ...

class TestCompileSelect(CompileSelectBase):
    def test_compile_from(self) -> None: ...
    def test_compile_from_invalid_dates(self) -> None: ...
    def test_compile_targets_wildcard(self) -> None: ...
    def test_compile_targets_named(self) -> None: ...
    def test_compile_mixed_aggregates(self) -> None: ...
    def test_compile_aggregates_of_aggregates(self) -> None: ...
    def test_compile_having(self) -> None: ...
    def test_compile_group_by_inventory(self) -> None: ...

class TestCompileSelectGroupBy(CompileSelectBase):
    def test_compile_group_by_non_aggregates(self) -> None: ...
    def test_compile_group_by_reference_by_name(self) -> None: ...
    def test_compile_group_by_reference_by_number(self) -> None: ...
    def test_compile_group_by_reference_an_aggregate(self) -> None: ...
    def test_compile_group_by_implicit(self) -> None: ...
    def test_compile_group_by_coverage(self) -> None: ...
    def test_compile_group_by_reconcile(self) -> None: ...

class TestCompileSelectOrderBy(CompileSelectBase):
    def test_compile_order_by_simple(self) -> None: ...
    def test_compile_order_by_simple_2(self) -> None: ...
    def test_compile_order_by_create_non_agg(self) -> None: ...
    def test_compile_order_by_reconcile(self) -> None: ...
    def test_compile_order_by_reference_invisible(self) -> None: ...
    def test_compile_order_by_aggregate(self) -> None: ...

class TestTranslationJournal(CompileSelectBase):
    maxDiff: int = ...
    def test_journal(self) -> None: ...
    def test_journal_with_account(self) -> None: ...
    def test_journal_with_account_and_from(self) -> None: ...
    def test_journal_with_account_func_and_from(self) -> None: ...

class TestTranslationBalance(CompileSelectBase):
    group_by: Any = ...
    order_by: Any = ...
    def test_balance(self) -> None: ...
    def test_balance_with_units(self) -> None: ...
    def test_balance_with_units_and_from(self) -> None: ...

class TestCompilePrint(CompileSelectBase):
    def test_print(self) -> None: ...
    def test_print_from(self) -> None: ...
