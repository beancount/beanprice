import unittest
from beancount.utils import defdict as defdict

class TestDefDictWithKey(unittest.TestCase):
    def test_defdict_with_key(self) -> None: ...

class TestImmutableDictWithDefault(unittest.TestCase):
    def test_dict_with_default(self) -> None: ...
    def test_pickle_defdict(self) -> None: ...
