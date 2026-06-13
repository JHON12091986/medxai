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
    assert "tree = ast.parse(path.read_text(" in res.stdout


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

def test_cmd_code_call_graph(tmp_path):
    import json
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def a():\n  b()\n  c()\n\ndef b():\n  pass\n")

    res = run_nf("code", "call-graph", str(test_file))
    assert res.returncode == 0
    output_json = json.loads(res.stdout)

    try:
        rel_path = str(test_file.relative_to(REPO_ROOT))
    except ValueError:
        rel_path = str(test_file)
    key = f"{rel_path}:a"
    assert key in output_json
    assert "b" in output_json[key]
    assert "c" in output_json[key]

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

    res = run_nf("code", "call-stack", str(test_file), "func_a")
    assert res.returncode == 0

    output = res.stdout
    assert "--- func_a ---" in output
    assert "--- func_b ---" in output
    assert "--- func_c ---" in output
    assert "--- func_d ---" in output
    assert "def func_a():" in output
    assert "def func_b():" in output
    assert "def func_c():" in output
    assert "def func_d():" in output

def test_cmd_code_migrate(tmp_path):
    test_file = tmp_path / "dummy_migrate.py"
    test_file.write_text("def old_sym():\n    pass\nold_sym()", encoding="utf-8")
    res = run_nf("code", "migrate", "old_sym", "new_sym", "--dir", str(test_file))
    assert res.returncode == 0
    assert "✅ Migrated" in res.stdout
    assert "🚀 Successfully migrated symbol in 1 files" in res.stdout
    content = test_file.read_text(encoding="utf-8")
    assert "def new_sym():" in content
    assert "new_sym()" in content
    assert "old_sym" not in content
