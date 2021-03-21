from beancount import loader as loader
from beancount.core import data as data
from beancount.parser import cmptest as cmptest, parser as parser
from typing import Any

class TestMarkUnverified(cmptest.TestCase):
    def test_mark_unverified(self, entries: Any, errors: Any, options_map: Any) -> None: ...
