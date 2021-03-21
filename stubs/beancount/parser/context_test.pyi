from beancount import loader as loader
from beancount.parser import context as context
from beancount.utils import test_utils as test_utils
from typing import Any

class TestContext(test_utils.TestCase):
    def test_context(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    maxDiff: int = ...
