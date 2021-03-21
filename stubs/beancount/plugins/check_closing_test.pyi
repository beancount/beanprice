from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from beancount.plugins import auto_accounts as auto_accounts
from typing import Any

class TestCheckClosing(cmptest.TestCase):
    def test_check_closing(self, entries: Any, _: Any, options_map: Any) -> None: ...
