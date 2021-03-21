from beancount.ingest import extract as extract, scripts_utils as scripts_utils
from beancount.utils import test_utils as test_utils
from typing import Any

extract_main: Any

def run(args: Any, parser: Any, importers_list: Any, files_or_directories: Any) -> None: ...

class TestParseArguments(scripts_utils.TestScriptsBase):
    def test_test_scripts_base(self) -> None: ...
    def test_parse_arguments__insufficient(self) -> None: ...
    def test_parse_arguments__invalid(self) -> None: ...
    def test_parse_arguments__sufficient(self) -> None: ...
    def test_parse_arguments__multiple(self) -> None: ...

INGEST_MAIN_WITH_DUPS: str

class TestImplicitInvocationMethods(scripts_utils.TestScriptsBase):
    FILES: Any = ...
    def test_implicit_invocation(self) -> None: ...
    def test_implicit_invocation_with_ingest_call(self) -> None: ...
