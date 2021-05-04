from beancount import loader as loader
from beancount.core import account as account, account_types as account_types, convert as convert, data as data, getters as getters, realization as realization
from beancount.parser import options as options, version as version
from collections import namedtuple
from typing import Any

def group_accounts_by_metadata(accounts_map: Any, meta_name: Any): ...
def find_institutions(entries: Any, options_map: Any): ...
def get_first_meta(entries: Any, field_name: Any): ...

Report = namedtuple('Report', 'title institutions')

InstitutionReport = namedtuple('Institution', 'name fields accounts')

AccountReport = namedtuple('Account', 'name open_date balance num_postings fields')

def create_report(entries: Any, options_map: Any): ...

XHTML_TEMPLATE_PRE: str
XHTML_TEMPLATE_POST: str

def format_xhtml_report(report: Any, options_map: Any): ...
def format_xhtml_table(items: Any, klass: str = ...): ...
def main() -> None: ...
