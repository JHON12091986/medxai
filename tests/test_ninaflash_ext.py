import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.resolve()

def run_nf(*args):
    cmd = [sys.executable, str(REPO_ROOT / "tools" / "ninaflash.py")] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res

def test_cmd_code_symbol():
    res = run_nf("code", "symbol", "tools/ninaflash.py", "cmd_code_outline")
    assert res.returncode == 0
    assert "def cmd_code_outline(args):" in res.stdout
    assert "tree = ast.parse(path.read_text())" in res.stdout

def test_cmd_find_symbol():
    res = run_nf("find-symbol", "cmd_code_outline")
    assert res.returncode == 0
    assert "tools/ninaflash.py:" in res.stdout

def test_cmd_code_sigs():
    res = run_nf("code", "sigs", "tools")
    assert res.returncode == 0
    assert "def cmd_code_outline(args):" in res.stdout
    assert "Extract signatures/docstrings only using AST." in res.stdout

def test_cmd_code_doc():
    res = run_nf("code", "doc", "Extract signatures")
    assert res.returncode == 0
    assert "tools/ninaflash.py:" in res.stdout
    assert "Extract signatures" in res.stdout


def test_cmd_code_call_stack(tmp_path):
    source_code = """
def func_a():
    func_b()
    func_c()

def func_b():
    func_d()

def func_c():
    pass

def func_d():
    pass
"""
    test_file = tmp_path / "test_file.py"
    test_file.write_text(source_code)

    env = os.environ.copy()
    env["PYTHONPATH"] = "./tools:."
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "tools/ninaflash.py", "code", "call-stack", str(test_file), "func_a"], capture_output=True, text=True, env=env)

    output = result.stdout
    assert "--- func_a ---" in output
    assert "--- func_b ---" in output
    assert "--- func_c ---" in output
    assert "--- func_d ---" in output
    assert "def func_a():" in output
    assert "def func_b():" in output
    assert "def func_c():" in output
    assert "def func_d():" in output
