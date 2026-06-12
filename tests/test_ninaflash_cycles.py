from unittest.mock import patch, MagicMock
from tools import ninaflash

def test_cmd_code_cycles_no_cycles(capsys, tmp_path):
    # Mock _find_py_files to return a DAG
    file_a = tmp_path / "a.py"
    file_b = tmp_path / "b.py"
    file_a.write_text("import b\n")
    file_b.write_text("def foo(): pass\n")

    with patch("tools.ninaflash._find_py_files", return_value=[file_a, file_b]):
        with patch("tools.ninaflash.REPO_ROOT", tmp_path):
            args = MagicMock()
            ninaflash.cmd_code_cycles(args)
            captured = capsys.readouterr()
            assert "No circular dependencies found." in captured.out

def test_cmd_code_cycles_with_cycles(capsys, tmp_path):
    file_a = tmp_path / "a.py"
    file_b = tmp_path / "b.py"
    file_a.write_text("import b\n")
    file_b.write_text("import a\n")

    with patch("tools.ninaflash._find_py_files", return_value=[file_a, file_b]):
        with patch("tools.ninaflash.REPO_ROOT", tmp_path):
            args = MagicMock()
            ninaflash.cmd_code_cycles(args)
            captured = capsys.readouterr()
            assert "Found 1 circular dependencies" in captured.out
            assert "a -> b -> a" in captured.out or "b -> a -> b" in captured.out
