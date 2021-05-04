import unittest
from beancount.utils import regexp_utils as regexp_utils
from typing import Any

def match(regexp: Any, string: Any): ...

class TestRegexpUtils(unittest.TestCase):
    def test_replace_unicode(self) -> None: ...
