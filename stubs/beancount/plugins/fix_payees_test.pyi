from beancount import loader as loader
from beancount.parser import cmptest as cmptest
from beancount.plugins import fix_payees as fix_payees
from typing import Any

class TestFixPayees(cmptest.TestCase):
    options_map: Any = ...
    in_entries: Any = ...
    exp_entries: Any = ...
    def setUp(self, entries: Any, _: Any, options_map: Any) -> None: ...
    def fix(self, config: Any): ...
    def test_config_syntax_errors(self) -> None: ...
    def test_account_rule(self) -> None: ...
    def test_match_payee(self) -> None: ...
    def test_match_narration(self) -> None: ...
    def test_partial_not_matches(self) -> None: ...
