import unittest
from beancount.core.number import D as D
from typing import Any, Optional

def qSelect(target_spec: Optional[Any] = ..., from_clause: Optional[Any] = ..., where_clause: Optional[Any] = ..., group_by: Optional[Any] = ..., order_by: Optional[Any] = ..., pivot_by: Optional[Any] = ..., limit: Optional[Any] = ..., distinct: Optional[Any] = ..., flatten: Optional[Any] = ...): ...

class QueryParserTestBase(unittest.TestCase):
    maxDiff: int = ...
    parser: Any = ...
    def setUp(self) -> None: ...
    def parse(self, query: Any): ...
    def assertParse(self, expected: Any, query: Any, debug: bool = ...): ...

class TestSelectTarget(QueryParserTestBase):
    def test_unterminated__empty(self) -> None: ...
    def test_unterminated__non_empty(self) -> None: ...
    def test_empty(self) -> None: ...
    def test_target_wildcard(self) -> None: ...
    def test_target_one(self) -> None: ...
    def test_target_one_as(self) -> None: ...
    def test_target_multiple(self) -> None: ...
    def test_target_multiple_as(self) -> None: ...

class TestSelectExpression(QueryParserTestBase):
    def test_expr_constant_null(self) -> None: ...
    def test_expr_constant_boolean(self) -> None: ...
    def test_expr_constant_integer(self) -> None: ...
    def test_expr_constant_decimal(self) -> None: ...
    def test_expr_constant_string(self) -> None: ...
    def test_expr_constant_date(self) -> None: ...
    def test_expr_column(self) -> None: ...
    def test_expr_eq(self) -> None: ...
    def test_expr_ne(self) -> None: ...
    def test_expr_gt(self) -> None: ...
    def test_expr_gte(self) -> None: ...
    def test_expr_lt(self) -> None: ...
    def test_expr_lte(self) -> None: ...
    def test_expr_match(self) -> None: ...
    def test_expr_paren_single(self) -> None: ...
    def test_expr_paren_multi(self) -> None: ...
    def test_expr_and(self) -> None: ...
    def test_expr_or(self) -> None: ...
    def test_expr_not(self) -> None: ...
    def test_expr_paren_multi2(self) -> None: ...
    def test_expr_function__zero_args(self) -> None: ...
    def test_expr_function__one_args(self) -> None: ...
    def test_expr_function__two_args(self) -> None: ...
    def test_expr_function__five_args(self) -> None: ...
    def test_expr_mul(self) -> None: ...
    def test_expr_div(self) -> None: ...
    def test_expr_add(self) -> None: ...
    def test_expr_sub(self) -> None: ...
    def test_expr_numerical(self) -> None: ...

class TestSelectPrecedence(QueryParserTestBase):
    def test_expr_function__and_or(self) -> None: ...
    def test_expr_function__and_eq(self) -> None: ...
    def test_expr_function__and_not(self) -> None: ...
    def test_expr_function__and_plus_minus(self) -> None: ...
    def test_expr_function__mul_div_plus_minus(self) -> None: ...
    def test_expr_function__membership_precedence(self) -> None: ...

class TestSelectFromBase(QueryParserTestBase):
    targets: Any = ...
    expr: Any = ...
    def setUp(self) -> None: ...

class TestSelectFrom(TestSelectFromBase):
    def test_from_empty(self) -> None: ...
    def test_from(self) -> None: ...
    def test_from_open_default(self) -> None: ...
    def test_from_close_default(self) -> None: ...
    def test_from_close_dated(self) -> None: ...
    def test_from_close_no_expr(self) -> None: ...
    def test_from_close_no_expr_dated(self) -> None: ...
    def test_from_clear_default(self) -> None: ...
    def test_from_open_close_clear(self) -> None: ...

class TestSelectWhere(TestSelectFromBase):
    def test_where_empty(self) -> None: ...
    def test_where(self) -> None: ...

class TestSelectFromAndWhere(TestSelectFromBase):
    def test_both(self) -> None: ...

class TestSelectFromSelect(QueryParserTestBase):
    def test_from_select(self) -> None: ...

class TestSelectGroupBy(QueryParserTestBase):
    def test_groupby_empty(self) -> None: ...
    def test_groupby_one(self) -> None: ...
    def test_groupby_many(self) -> None: ...
    def test_groupby_expr(self) -> None: ...
    def test_groupby_having(self) -> None: ...
    def test_groupby_numbers(self) -> None: ...

class TestSelectOrderBy(QueryParserTestBase):
    def test_orderby_empty(self) -> None: ...
    def test_orderby_one(self) -> None: ...
    def test_orderby_many(self) -> None: ...
    def test_orderby_asc(self) -> None: ...
    def test_orderby_desc(self) -> None: ...

class TestSelectPivotBy(QueryParserTestBase):
    def test_pivotby_empty(self) -> None: ...
    def test_pivotby_one(self) -> None: ...
    def test_pivotby_many(self) -> None: ...

class TestSelectOptions(QueryParserTestBase):
    def test_distinct(self) -> None: ...
    def test_limit_empty(self) -> None: ...
    def test_limit_present(self) -> None: ...
    def test_flatten(self) -> None: ...
    def test_limit_and_flatten(self) -> None: ...

class TestBalances(QueryParserTestBase):
    def test_balances_empty(self) -> None: ...
    def test_balances_from(self) -> None: ...
    def test_balances_from_with_transformer(self) -> None: ...
    def test_balances_from_with_transformer_simple(self) -> None: ...

class TestJournal(QueryParserTestBase):
    def test_journal_empty(self) -> None: ...
    def test_journal_account(self) -> None: ...
    def test_journal_summary(self) -> None: ...
    def test_journal_account_and_summary(self) -> None: ...
    def test_journal_from(self) -> None: ...

class TestPrint(QueryParserTestBase):
    def test_print_empty(self) -> None: ...
    def test_print_from(self) -> None: ...

class TestExpressionName(QueryParserTestBase):
    def test_column(self) -> None: ...
    def test_function(self) -> None: ...
    def test_constant(self) -> None: ...
    def test_unary(self) -> None: ...
    def test_binary(self) -> None: ...

class TestExplain(QueryParserTestBase):
    def test_explain_select(self) -> None: ...
    def test_explain_balances(self) -> None: ...
    def test_explain_journal(self) -> None: ...
