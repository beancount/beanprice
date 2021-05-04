from beancount.ingest import cache as cache
from beancount.utils import file_utils as file_utils
from typing import Any, Optional

SECTION: str
FILE_TOO_LARGE_THRESHOLD: Any

def find_imports(importer_config: Any, files_or_directories: Any, logfile: Optional[Any] = ...) -> None: ...
def identify(importers_list: Any, files_or_directories: Any) -> None: ...

DESCRIPTION: str

def add_arguments(parser: Any) -> None: ...
def run(_: Any, __: Any, importers_list: Any, files_or_directories: Any, hooks: Optional[Any] = ...): ...
