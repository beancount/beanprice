import unittest
from beancount import loader as loader
from beancount.core import display_context as display_context, realization as realization
from beancount.core.number import D as D
from beancount.parser import options as options
from beancount.reports import base as base
from beancount.utils import table as table
from typing import Any

def iter_reports(report_classes: Any) -> None: ...

class ExampleReport(base.Report):
    names: Any = ...
    default_format: str = ...
    @classmethod
    def add_args(cls, parser: Any) -> None: ...
    def render_html(self, entries: Any, errors: Any, options_map: Any, file: Any) -> None: ...
    def render_text(self, entries: Any, errors: Any, options_map: Any, file: Any) -> None: ...

class TestReport(unittest.TestCase):
    ReportClass: Any = ...
    entries: Any = ...
    errors: Any = ...
    options_map: Any = ...
    def setUp(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_from_args(self) -> None: ...
    def test_add_args(self) -> None: ...
    def test_supported_formats(self) -> None: ...
    def test_render__html(self) -> None: ...
    def test_render__text(self) -> None: ...
    def test_call(self) -> None: ...

class ExampleTableReport(base.TableReport):
    names: Any = ...
    def generate_table(self, entries: Any, errors: Any, options_map: Any): ...

class TestTableReport(unittest.TestCase):
    ReportClass: Any = ...
    entries: Any = ...
    errors: Any = ...
    options_map: Any = ...
    report: Any = ...
    def setUp(self, entries: Any, errors: Any, options_map: Any) -> None: ...
    def test_generate_table(self) -> None: ...
    def test_table__render_text(self) -> None: ...
    def test_table__render_html(self) -> None: ...
    def test_table__render_htmldiv(self) -> None: ...
    def test_table__render_csv(self) -> None: ...

class TestRealizationMeta(unittest.TestCase):
    def test_realization_metaclass(self) -> None: ...

class TestReportFunctions(unittest.TestCase):
    def test_get_html_template(self) -> None: ...
