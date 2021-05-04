from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from beancount.plugins import nounused as nounused
from typing import Any

class TestValidateUnusedAccounts(cmptest.TestCase):
    def test_validate_unused_accounts(self, entries: Any, _: Any, options_map: Any) -> None: ...
