from beancount.scripts import format as format
from beancount.utils import test_utils as test_utils
from typing import Any

class TestScriptFormat(test_utils.TestCase):
    def test_success(self, filename: Any) -> None: ...
    def test_align_posting_starts(self, filename: Any) -> None: ...
    def test_open_only_issue80(self, filename: Any) -> None: ...
    def test_commas(self, filename: Any) -> None: ...
    def test_currency_issue146(self, filename: Any) -> None: ...
    def test_fixed_width(self, filename: Any) -> None: ...
    def test_fixed_column(self, filename: Any) -> None: ...
    def test_metadata_issue400(self, filename: Any) -> None: ...
    def test_arithmetic_expressions(self, filename: Any) -> None: ...
