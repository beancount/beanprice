from beancount.core import data as data, realization as realization
from beancount.reports import base as base, journal_html as journal_html, journal_text as journal_text
from beancount.utils import misc_utils as misc_utils
from typing import Any

class JournalReport(base.HTMLReport, metaclass=base.RealizationMeta):
    names: Any = ...
    default_format: str = ...
    default_width: int = ...
    test_args: Any = ...
    @classmethod
    def add_args(cls, parser: Any) -> None: ...
    def get_postings(self, real_root: Any): ...
    def render_real_text(self, real_root: Any, price_map: Any, price_date: Any, options_map: Any, file: Any) -> None: ...
    def render_real_csv(self, real_root: Any, price_map: Any, price_date: Any, options_map: Any, file: Any) -> None: ...
    def render_real_htmldiv(self, real_root: Any, price_map: Any, price_date: Any, options_map: Any, file: Any) -> None: ...

class ConversionsReport(base.HTMLReport):
    names: Any = ...
    def render_htmldiv(self, entries: Any, errors: Any, options_map: Any, file: Any) -> None: ...

class DocumentsReport(base.HTMLReport):
    names: Any = ...
    def render_htmldiv(self, entries: Any, errors: Any, options_map: Any, file: Any) -> None: ...

__reports__: Any
