import unittest
from beancount import loader as loader
from beancount.core import display_context as display_context, realization as realization
from beancount.reports import html_formatter as html_formatter, tree_table as tree_table
from typing import Any

class TestActiveAccounts(unittest.TestCase):
    def test_is_account_active(self, entries: Any, _: Any, __: Any) -> None: ...

class TestTables(unittest.TestCase):
    real_root: Any = ...
    def setUp(self, entries: Any, _: Any, __: Any) -> None: ...
    def test_tree_table(self) -> None: ...
    def test_table_of_balances(self) -> None: ...
