import subprocess
import subprocess
import sys
import pytest

@pytest.mark.monkeytype
def test_enforce_type_hints_basic(tmp_path):
    test_file = tmp_path / "test_temp.py"
    test_file.write_text('def f(a, b=2):\n    pass\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert "from typing import Any" in content

@pytest.mark.monkeytype
def test_enforce_type_hints_with_docstring(tmp_path):
    test_file = tmp_path / "test_temp2.py"
    test_file.write_text('"""Module docstring"""\n\ndef g(c):\n    return c\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert content.startswith('"""Module docstring"""\nfrom typing import Any\n')

@pytest.mark.monkeytype
def test_enforce_type_hints_returns_any(tmp_path):
    test_file = tmp_path / "test_temp3.py"
    test_file.write_text('def h(x):\n    return x * 2\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert "def h(x: Any) -> Any:" in content

@pytest.mark.monkeytype
def test_enforce_type_hints_future_import(tmp_path):
    test_file = tmp_path / "test_temp4.py"
    test_file.write_text('from __future__ import annotations\ndef i(x):\n    pass\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert "from __future__ import annotations\nfrom typing import Any" in content

@pytest.mark.monkeytype
def test_enforce_type_hints_nested_function(tmp_path):
    test_file = tmp_path / "test_temp5.py"
    test_file.write_text('def outer():\n    def inner():\n        return 1\n    pass\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert "def inner() -> Any:" in content

@pytest.mark.monkeytype
def test_enforce_type_hints_generator(tmp_path):
    test_file = tmp_path / "test_temp6.py"
    test_file.write_text('def gen():\n    yield 1\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert "def gen() -> Any:" in content

@pytest.mark.monkeytype
def test_enforce_type_hints_yield_from(tmp_path):
    test_file = tmp_path / "test_temp7.py"
    test_file.write_text('def gen2():\n    yield from [1, 2]\n')
    subprocess.run([sys.executable, 'tools/enforce_type_hints.py', '--fix', str(test_file)], check=True)
    content = test_file.read_text()
    assert "def gen2() -> Any:" in content
