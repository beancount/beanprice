from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from typing import Any

class TestExampleExcludeTag(cmptest.TestCase):
    def test_exclude_tag(self, entries: Any, errors: Any, __: Any) -> None: ...
