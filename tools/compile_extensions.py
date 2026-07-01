import os
import py_compile
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger("nina.perf.compile")

def compile_hotpaths(directory: str) -> List[str]:
    """
    Programmatically compile .py files in the target directory to bytecode .pyc.
    Gracefully handles and logs errors without raising exceptions to maintain system resilience.
    """
    compiled_files: List[str] = []
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.warning(f"Directory {directory} does not exist or is not a directory.")
        return compiled_files

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                py_file = Path(root) / file
                try:
                    # Compile the .py file to bytecode (.pyc) in __pycache__
                    pyc_path = py_compile.compile(str(py_file), doraise=True)
                    if pyc_path:
                        compiled_files.append(pyc_path)
                except Exception as e:
                    logger.error(f"Failed to compile {py_file}: {e}")
                    # Gracefully continue to let imports fallback to source .py files
                    pass

    return compiled_files
