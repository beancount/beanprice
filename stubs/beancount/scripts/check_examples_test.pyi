from beancount.scripts import check as check
from beancount.utils import test_utils as test_utils

def find_example_files() -> None: ...

class TestCheckExamples(test_utils.TestCase):
    def test_example_files(self) -> None: ...
