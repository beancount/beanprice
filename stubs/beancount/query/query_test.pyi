import unittest
from beancount import loader as loader
from beancount.query import query as query
from beancount.utils import test_utils as test_utils

class TestSimple(unittest.TestCase):
    def test_run_query(self) -> None: ...
