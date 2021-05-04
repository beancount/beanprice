import unittest
from beancount import loader as loader
from typing import Any

class TestPedantic(unittest.TestCase):
    def test_plugins_pedantic(self, entries: Any, _: Any, options_map: Any) -> None: ...
