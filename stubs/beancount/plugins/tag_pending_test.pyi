from beancount import loader as loader
from beancount.core import data as data
from beancount.plugins import tag_pending as tag_pending
from beancount.utils import test_utils as test_utils
from typing import Any

class TestExampleTrackPending(test_utils.TestCase):
    def test_tag_pending(self, filename: Any) -> None: ...
