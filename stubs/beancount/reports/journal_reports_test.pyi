import unittest
from beancount.parser import options as options
from beancount.reports import base_test as base_test, journal_reports as journal_reports

class TestJournalReports(unittest.TestCase):
    def test_all_reports_empty(self) -> None: ...
