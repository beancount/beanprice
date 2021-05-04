from beancount.core import account as account, data as data, getters as getters
from collections import namedtuple
from typing import Any, Optional

__plugins__: Any

DocumentError = namedtuple('DocumentError', 'source message entry')

def process_documents(entries: Any, options_map: Any): ...
def verify_document_files_exist(entries: Any, unused_options_map: Any): ...
def find_documents(directory: Any, input_filename: Any, accounts_only: Optional[Any] = ..., strict: bool = ...): ...
