from beancount import loader as loader
from beancount.ops import validation as validation
from beancount.scripts import example as example
from beancount.utils import test_utils as test_utils

class TestScriptExample(test_utils.TestCase):
    def test_generate(self) -> None: ...
