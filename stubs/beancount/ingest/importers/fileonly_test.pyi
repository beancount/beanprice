import unittest
from beancount.ingest import cache as cache
from beancount.ingest.importers import fileonly as fileonly
from beancount.utils import file_type as file_type, test_utils as test_utils
from typing import Any

class TestFileOnly(unittest.TestCase):
    def test_constructors(self) -> None: ...
    def test_match(self, filename: Any) -> None: ...
