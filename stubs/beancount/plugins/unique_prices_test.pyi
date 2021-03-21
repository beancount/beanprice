from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from beancount.plugins import implicit_prices as implicit_prices, unique_prices as unique_prices
from typing import Any

class TestValidateAmbiguousPrices(cmptest.TestCase):
    def test_validate_unique_prices__different(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_validate_unique_prices__same(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_validate_unique_prices__from_costs(self, entries: Any, errors: Any, options_map: Any) -> None: ...
