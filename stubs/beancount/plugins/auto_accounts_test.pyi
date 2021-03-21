from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from beancount.plugins import auto_accounts as auto_accounts
from typing import Any

class TestAutoInsertOpen(cmptest.TestCase):
    def test_auto_open(self, entries: Any, _: Any, options_map: Any) -> None: ...
