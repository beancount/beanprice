from beancount.scripts import sql as sql
from beancount.utils import test_utils as test_utils
from typing import Any

ONE_OF_EACH_TYPE: str

class TestScriptSQL(test_utils.TestCase):
    def convert_to_sql(self, filename: Any): ...
    def test_all_types(self) -> None: ...
    def test_example(self) -> None: ...
