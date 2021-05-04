import unittest
from beancount.core import flags as flags
from typing import Any

class TestFlags(unittest.TestCase):
    ALLOW_NOT_UNIQUE: Any = ...
    def test_unique_flags(self) -> None: ...
