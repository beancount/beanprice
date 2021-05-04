import unittest
from beancount import loader as loader
from beancount.parser import options as options
from beancount.reports import base_test as base_test, misc_reports as misc_reports
from typing import Any

class TestMiscReports(unittest.TestCase):
    def test_all_reports_empty(self) -> None: ...
    def test_errors(self, entries: Any, errors: Any, options_map: Any) -> None: ...
