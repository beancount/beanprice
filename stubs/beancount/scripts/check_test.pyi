from beancount.scripts import check as check
from beancount.utils import test_utils as test_utils
from typing import Any

class TestScriptCheck(test_utils.TestCase):
    def test_success(self, filename: Any) -> None: ...
    def test_fail(self, filename: Any) -> None: ...
