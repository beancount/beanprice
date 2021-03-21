from beancount.core import display_context as display_context
from beancount.parser import version as version
from beancount.utils import misc_utils as misc_utils
from collections import namedtuple
from typing import Any

def do_lex(filename: Any, unused_args: Any) -> None: ...
do_dump_lexer = do_lex

def do_parse(filename: Any, unused_args: Any) -> None: ...
def do_roundtrip(filename: Any, unused_args: Any) -> None: ...
def do_directories(filename: Any, args: Any) -> None: ...
def do_list_options(*unused_args: Any) -> None: ...
def do_print_options(filename: Any, *args: Any) -> None: ...
def get_commands(): ...
def do_deps(*unused_args: Any) -> None: ...
do_checkdeps = do_deps

def do_context(filename: Any, args: Any) -> None: ...

RenderError = namedtuple('RenderError', 'source message entry')

def do_linked(filename: Any, args: Any) -> None: ...
def find_linked_entries(entries: Any, links: Any, follow_links: bool) -> Any: ...
def do_missing_open(filename: Any, args: Any) -> None: ...
def do_display_context(filename: Any, args: Any) -> None: ...
def do_validate_html(directory: Any, args: Any) -> None: ...
def main() -> None: ...
