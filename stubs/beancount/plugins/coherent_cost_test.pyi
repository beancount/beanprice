from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from beancount.plugins import coherent_cost as coherent_cost
from typing import Any

class TestValidateUnusedAccounts(cmptest.TestCase):
    def test_validate_unused_accounts(self, entries: Any, in_errors: Any, options_map: Any) -> None: ...
