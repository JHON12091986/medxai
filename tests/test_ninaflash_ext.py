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

def test_cmd_code_call_graph(tmp_path):
    import json
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def a():\n  b()\n  c()\n\ndef b():\n  pass\n")

    res = run_nf("code", "call-graph", str(test_file))
    assert res.returncode == 0
    output_json = json.loads(res.stdout)

    assert "a" in output_json
    assert "b" in output_json["a"]
    assert "c" in output_json["a"]
