import unittest
from beancount import loader as loader
from beancount.core import realization as realization
from beancount.parser import options as options
from beancount.web import views as views
from typing import Any

class TestViewsFromEmpty(unittest.TestCase):
    def test_from_empty(self) -> None: ...

class TestViews(unittest.TestCase):
    entries: Any = ...
    options_map: Any = ...
    empty_realization: Any = ...
    def setUp(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_View(self) -> None: ...
    def test_EmptyView(self) -> None: ...
    def test_AllView(self) -> None: ...
    def test_YearView(self) -> None: ...
    def test_TagView(self) -> None: ...
    def test_PayeeView(self) -> None: ...
    def test_ComponentView(self) -> None: ...
