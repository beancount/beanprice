from beancount.core import account as account, getters as getters
from typing import Any

class ValidateDirectoryError(Exception): ...

def validate_directory(accounts: Any, document_dir: Any): ...
def validate_directories(entries: Any, document_dirs: Any) -> None: ...
