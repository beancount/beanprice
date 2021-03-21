import unittest
from typing import Any, Optional

PROGRAM: Any
DEBUG: int

def treeify(string: Any, options: Optional[Any] = ...): ...

class TestTreeifyBase(unittest.TestCase):
    maxDiff: int = ...
    def treeify(self, string: Any, expect_errors: bool = ..., options: Optional[Any] = ...): ...
    def treeify_equal(self, string: Any, expected: Any, expect_errors: bool = ..., options: Optional[Any] = ...): ...

class TestTreeify(TestTreeifyBase):
    def test_simple(self) -> None: ...
    def test_empty_string(self) -> None: ...
    def test_no_columns(self) -> None: ...
    def test_flush_left(self) -> None: ...
    def test_flush_right(self) -> None: ...
    def test_two_columns(self) -> None: ...
    def test_overlapping_column(self) -> None: ...
    def test_parents(self) -> None: ...
    def test_unsorted(self) -> None: ...
    def test_consecutive(self) -> None: ...
    def test_noise_before(self) -> None: ...
    def test_noise_after(self) -> None: ...
    def test_noise_middle_between_nodes(self) -> None: ...
    def test_noise_middle_same_node(self) -> None: ...
    def test_noise_middle_parent_child(self) -> None: ...
    def test_filenames(self) -> None: ...
    def test_filenames_tree(self) -> None: ...
    def test_width_wider(self) -> None: ...
    def test_width_narrower(self) -> None: ...
    def test_whitespace(self) -> None: ...
