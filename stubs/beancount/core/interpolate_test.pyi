import unittest
from beancount import loader as loader
from beancount.core import convert as convert, data as data, interpolate as interpolate, inventory as inventory, position as position
from beancount.core.amount import A as A, ZERO as ZERO
from beancount.core.number import D as D
from beancount.parser import cmptest as cmptest, parser as parser
from beancount.utils import defdict as defdict
from typing import Any

OPTIONS_MAP: Any

class TestBalance(cmptest.TestCase):
    def test_has_nontrivial_balance(self) -> None: ...
    def test_compute_residual(self) -> None: ...
    def test_fill_residual_posting(self, entries: Any, _: Any, __: Any) -> None: ...

class TestComputeBalance(unittest.TestCase):
    def test_compute_entries_balance_currencies(self, entries: Any, _: Any, __: Any) -> None: ...
    def test_compute_entries_balance_at_cost(self, entries: Any, _: Any, __: Any) -> None: ...
    def test_compute_entries_balance_conversions(self, entries: Any, _: Any, __: Any) -> None: ...
    def test_compute_entry_context(self, entries: Any, _: Any, __: Any) -> None: ...

class TestInferTolerances(cmptest.TestCase):
    def test_tolerances__no_precision(self, entries: Any, _: Any, options_map: Any) -> None: ...
    def test_tolerances__dubious_precision(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__ignore_price(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__ignore_cost(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__ignore_cost_and_price(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__cost_and_number_ignored(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__number_on_cost_used(self, entries: Any, _: Any, options_map: Any) -> None: ...
    def test_tolerances__number_on_cost_used_overrides(self, entries: Any, _: Any, options_map: Any) -> None: ...
    def test_tolerances__number_on_cost_fail_to_succ(self) -> None: ...
    def test_tolerances__minimum_on_costs(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__with_inference(self, entries: Any, _: Any, options_map: Any) -> None: ...
    def test_tolerances__capped_inference(self, entries: Any, _: Any, options_map: Any) -> None: ...
    def test_tolerances__multiplier(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_tolerances__bug(self, entries: Any, errors: Any, _: Any) -> None: ...
    def test_tolerances__bug53a(self, entries: Any, errors: Any, _: Any) -> None: ...
    def test_tolerances__bug53b(self, entries: Any, errors: Any, _: Any) -> None: ...
    def test_tolerances__bug53_price(self, entries: Any, errors: Any, _: Any) -> None: ...
    def test_tolerances__missing_units_only(self, entries: Any, errors: Any, options_map: Any) -> None: ...

class TestQuantize(unittest.TestCase):
    def test_quantize_with_tolerance(self) -> None: ...
