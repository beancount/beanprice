import unittest
from beancount.core.number import D as D
from beancount.prices import source as source
from beancount.prices.sources import iex as iex
from beancount.utils import date_utils as date_utils
from typing import Any

def response(contents: Any, status_code: Any = ...): ...

class IEXPriceFetcher(unittest.TestCase):
    def test_error_network(self) -> None: ...
    def test_valid_response(self) -> None: ...
