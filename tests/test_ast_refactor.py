import pytest
from core.ast_refactor import extract_method


def test_extract_method_multi_outputs():
    source = """
def my_func(x, y):
    print("Start")
    a = x + 1
    # -- start --
    b = a + y
    c = b * 2
    # -- end --
    print(c)
    return c + b
"""
    mod_source, new_func = extract_method(source, 6, 7, "extracted_func")

    assert "extracted_func(a, y)" in mod_source
    assert "b, c = extracted_func(a, y)" in mod_source
    assert "def extracted_func(a, y):" in new_func
    assert "return b, c" in new_func


def test_extract_method_single_output():
    source = """
class MyClass:
    def my_func(self, x, y):
        print("Start")
        a = x + 1
        b = a + y
        c = b * 2
        print(c)
        return c + b
"""
    # extracting lines 5 to 6 (a = x + 1, b = a + y), which means output is 'b'
    mod_source, new_func = extract_method(source, 5, 6, "extracted_func")

    assert "b = extracted_func(x, y)" in mod_source
    assert "def extracted_func(x, y):" in new_func
    assert "return b" in new_func


def test_extract_method_with_self():
    source = """
class MyClass:
    def __init__(self):
        self.factor = 2

    def my_func(self, x, y):
        print("Start")
        a = x + 1
        b = a + y
        c = b * self.factor
        print(c)
        return c + b
"""
    mod_source, new_func = extract_method(source, 9, 10, "extracted_func")

    assert "b, c = extracted_func(self, a, y)" in mod_source
    assert "def extracted_func(self, a, y):" in new_func
    assert "return b, c" in new_func


def test_extract_method_no_outputs():
    source = """
def my_func(x, y):
    print("Start")
    a = x + 1
    print("Middle")
    print(a)
    print("End")
    return a
"""
    mod_source, new_func = extract_method(source, 5, 6, "extracted_func")

    assert "extracted_func(a)" in mod_source
    assert (
        "=" not in mod_source.split("extracted_func(a)")[0].split("\n")[-1]
    )  # No assignment
    assert "def extracted_func(a):" in new_func
    assert "return" not in new_func


def test_extract_method_with_control_flow():
    source = """
def my_func(x):
    print("Start")
    if x > 0:
        return x
    print("End")
"""
    with pytest.raises(
        ValueError, match="Cannot extract block containing return/break/continue"
    ):
        extract_method(source, 4, 5, "extracted_func")
