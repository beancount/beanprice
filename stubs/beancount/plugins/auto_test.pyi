import unittest
from beancount import loader as loader
from typing import Any

class TestAuto(unittest.TestCase):
    def test_plugins_auto(self, entries: Any, _: Any, options_map: Any) -> None: ...
