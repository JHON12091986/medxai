import tempfile
from pathlib import Path
from tools.compile_extensions import compile_hotpaths

def test_compile_hotpaths_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid Python file
        test_file = Path(tmpdir) / "test_module.py"
        test_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")
        
        compiled_paths = compile_hotpaths(tmpdir)
        assert len(compiled_paths) == 1
        assert Path(compiled_paths[0]).exists()
        assert compiled_paths[0].endswith(".pyc")

def test_compile_hotpaths_graceful_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an invalid Python file (syntax error)
        test_file = Path(tmpdir) / "test_invalid.py"
        test_file.write_text("def hello(\n", encoding="utf-8")
        
        # Should not raise exception and should complete with empty or partial list
        compiled_paths = compile_hotpaths(tmpdir)
        assert len(compiled_paths) == 0

def test_compile_hotpaths_non_existent_directory():
    compiled_paths = compile_hotpaths("/non/existent/path/dir")
    assert compiled_paths == []
