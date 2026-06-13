import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from ninaflash import cmd_code_audit_doc

def test_cmd_code_audit_doc_missing_file(capsys):
    args = MagicMock()
    args.file = "non_existent_file.py"
    cmd_code_audit_doc(args)
    captured = capsys.readouterr()
    assert "❌ File not found" in captured.out

def test_cmd_code_audit_doc_syntax_error(capsys):
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("def foo() -> :\n    pass")
        f_path = f.name

    args = MagicMock()
    args.file = f_path
    cmd_code_audit_doc(args)
    captured = capsys.readouterr()
    assert "❌ Syntax error in file" in captured.out

    Path(f_path).unlink()

def test_cmd_code_audit_doc_scoring(capsys):
    code = """
def good_func():
    \"\"\"This is a good function.

    Args:
        None
    Returns:
        None
    \"\"\"
    pass

def bad_func():
    pass

def short_func():
    \"\"\"Hi\"\"\"
    pass

class MyClass:
    \"\"\"This class has a long enough docstring without args or returns.\"\"\"
    pass
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f_path = f.name

    args = MagicMock()
    args.file = f_path
    cmd_code_audit_doc(args)
    captured = capsys.readouterr()

    # good_func: Exists (1), Length > 10 (1), "args:" or "returns:" (1) -> 3/3
    assert "Function good_func: 3/3" in captured.out
    # bad_func: Doesn't exist (0) -> 0/3
    assert "Function bad_func: 0/3" in captured.out
    # short_func: Exists (1), Length <= 10 (0), no keywords (0) -> 1/3
    assert "Function short_func: 1/3" in captured.out
    # MyClass: Exists (1), Length > 10 (1), no keywords (0) -> 2/3
    assert "Class MyClass: 2/3" in captured.out

    assert "Overall Score: 50.0% (6/12)" in captured.out
    assert "Verdict: ⚠️ WARN (Score below 80%)" in captured.out

    Path(f_path).unlink()
