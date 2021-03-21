from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from typing import Any

class TestIraContributions(cmptest.TestCase):
    def test_ira_contribs(self, entries: Any, errors: Any, __: Any) -> None: ...
