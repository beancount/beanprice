import unittest
from beancount.core import data as data, display_context as display_context, inventory as inventory
from beancount.reports import html_formatter as html_formatter

class TestHTMLFormatter(unittest.TestCase):
    def test_functions(self) -> None: ...
    def test_render_inventory(self) -> None: ...
