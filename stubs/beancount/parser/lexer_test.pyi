import unittest
from beancount.core.number import D as D
from beancount.parser import lexer as lexer
from typing import Any

def print_tokens(tokens: Any) -> None: ...
def lex_tokens(fun: Any): ...

class TestLexer(unittest.TestCase):
    maxDiff: Any = ...
    def test_lex_iter(self, tokens: Any, errors: Any) -> None: ...
    def test_lex_unicode_account(self, tokens: Any, errors: Any) -> None: ...
    def test_lex_indent(self, tokens: Any, errors: Any) -> None: ...
    def test_comma_currencies(self, tokens: Any, errors: Any) -> None: ...
    def test_number_okay(self, tokens: Any, errors: Any) -> None: ...
    def test_number_space(self, tokens: Any, errors: Any) -> None: ...
    def test_number_dots(self, tokens: Any, errors: Any) -> None: ...
    def test_number_no_integer(self, tokens: Any, errors: Any) -> None: ...
    def test_currency_number(self, tokens: Any, errors: Any) -> None: ...
    def test_currency_dash(self, tokens: Any, errors: Any) -> None: ...
    def test_bad_date(self, tokens: Any, errors: Any) -> None: ...
    def test_date_followed_by_number(self, tokens: Any, errors: Any) -> None: ...
    def test_single_letter_account(self, tokens: Any, errors: Any) -> None: ...
    def test_account_names_with_numbers(self, tokens: Any, errors: Any) -> None: ...
    def test_account_names_with_dash(self, tokens: Any, errors: Any) -> None: ...
    def test_invalid_directive(self, tokens: Any, errors: Any) -> None: ...
    def test_string_too_long_warning(self) -> None: ...
    def test_very_long_string(self) -> None: ...
    def test_no_final_newline(self, tokens: Any, errors: Any) -> None: ...
    def test_string_escaped(self, tokens: Any, errors: Any) -> None: ...
    def test_string_newline(self, tokens: Any, errors: Any) -> None: ...
    def test_string_newline_long(self, tokens: Any, errors: Any) -> None: ...
    def test_string_newline_toolong(self) -> None: ...
    def test_popmeta(self, tokens: Any, errors: Any) -> None: ...
    def test_null_true_false(self, tokens: Any, errors: Any) -> None: ...

class TestIgnoredLines(unittest.TestCase):
    def test_ignored__long_comment(self, tokens: Any, errors: Any) -> None: ...
    def test_ignored__indented_comment(self, tokens: Any, errors: Any) -> None: ...
    def test_ignored__something_else(self, tokens: Any, errors: Any) -> None: ...
    def test_ignored__something_else_non_flag(self, tokens: Any, errors: Any) -> None: ...
    def test_ignored__org_mode_title(self, tokens: Any, errors: Any) -> None: ...
    def test_ignored__org_mode_drawer(self, tokens: Any, errors: Any) -> None: ...

class TestLexerErrors(unittest.TestCase):
    def test_lexer_invalid_token(self, tokens: Any, errors: Any) -> None: ...
    def test_lexer_exception__recovery(self, tokens: Any, errors: Any) -> None: ...
    def test_lexer_exception_DATE(self, tokens: Any, errors: Any) -> None: ...
    def test_lexer_exception_substring_with_quotes(self) -> None: ...

class TestLexerUnicode(unittest.TestCase):
    test_utf8_string: Any = ...
    expected_utf8_string: str = ...
    test_latin1_string: Any = ...
    expected_latin1_string: str = ...
    def test_bytes_encoded_utf8(self) -> None: ...
    def test_bytes_encoded_latin1_invalid(self) -> None: ...
    def test_bytes_encoded_latin1(self) -> None: ...
    def test_bytes_encoded_utf16_invalid(self) -> None: ...

class TestLexerMisc(unittest.TestCase):
    def test_valid_commas_in_number(self, tokens: Any, errors: Any) -> None: ...
    def test_invalid_commas_in_integral(self, tokens: Any, errors: Any) -> None: ...
    def test_invalid_commas_in_fractional(self, tokens: Any, errors: Any) -> None: ...
