from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
from io import StringIO

from tools.ninaflash import cmd_code_cycles

def test_cmd_code_cycles_no_cycles():
    class Args:
        pass

    # Mock the Path rglob to return a simple tree
    mock_file1 = MagicMock()
    mock_file1.parts = ("src", "module_a.py")
    mock_file1.relative_to.return_value = Path("src/module_a.py")
    mock_file1.read_text.return_value = "import module_b"

    mock_file2 = MagicMock()
    mock_file2.parts = ("src", "module_b.py")
    mock_file2.relative_to.return_value = Path("src/module_b.py")
    mock_file2.read_text.return_value = "def foo(): pass"

    with patch('tools.ninaflash.Path.rglob', return_value=[mock_file1, mock_file2]):
        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_code_cycles(Args())
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert '"status": "ok"' in output
        assert '"No circular imports found."' in output

def test_cmd_code_cycles_with_cycles():
    class Args:
        pass

    # Mock the Path rglob to return a circular tree
    mock_file1 = MagicMock()
    mock_file1.parts = ("src", "module_a.py")
    mock_file1.relative_to.return_value = Path("src/module_a.py")
    mock_file1.read_text.return_value = "import src.module_b\ndef foo(): pass"

    mock_file2 = MagicMock()
    mock_file2.parts = ("src", "module_b.py")
    mock_file2.relative_to.return_value = Path("src/module_b.py")
    mock_file2.read_text.return_value = "import src.module_c\ndef bar(): pass"

    mock_file3 = MagicMock()
    mock_file3.parts = ("src", "module_c.py")
    mock_file3.relative_to.return_value = Path("src/module_c.py")
    mock_file3.read_text.return_value = "import src.module_a\ndef baz(): pass"

    with patch('tools.ninaflash.Path.rglob', return_value=[mock_file1, mock_file2, mock_file3]):
        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_code_cycles(Args())
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        assert '"status": "error"' in output
        assert "src.module_a" in output
        assert "src.module_b" in output
        assert "src.module_c" in output
