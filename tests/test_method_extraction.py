import ast
import tempfile
import pathlib
import os
import unittest
from unittest.mock import patch, MagicMock

# Assuming tools directory is in PYTHONPATH
from tools.ninaflash import cmd_code_extract_method

class TestMethodExtraction(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = pathlib.Path(self.temp_dir.name) / "test_extract.py"
        self.test_file.write_text("""
def calculate(a, b):
    x = a + 1
    y = b + 1
    # BLOCK
    z = x + y
    w = z * 2
    # BLOCK END
    return w
""", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_basic(self):
        args = MagicMock()
        args.file = str(self.test_file)
        args.func_name = "calculate"
        args.start_line = 6
        args.end_line = 7
        args.new_name = "extracted_calc"

        with patch("tools.ninaflash.REPO_ROOT", pathlib.Path(self.temp_dir.name)):
            cmd_code_extract_method(args)

        content = self.test_file.read_text(encoding="utf-8")
        self.assertIn("def extracted_calc(x, y):", content)
        self.assertIn("return w", content)
        self.assertIn("w = extracted_calc(x, y)", content)

    def test_extract_class_method(self):
        class_file = pathlib.Path(self.temp_dir.name) / "test_class.py"
        class_file.write_text("""
class MyClass:
    def process(self, a, b):
        x = a + 1
        y = b + 1
        z = x + y
        w = z * 2
        self.val = w
        return self.val
""", encoding="utf-8")
        args = MagicMock()
        args.file = str(class_file)
        args.func_name = "process"
        args.start_line = 5
        args.end_line = 6
        args.new_name = "extracted_process"

        with patch("tools.ninaflash.REPO_ROOT", pathlib.Path(self.temp_dir.name)):
            cmd_code_extract_method(args)

        content = class_file.read_text(encoding="utf-8")
        self.assertIn("def extracted_process(self, b, x):", content)
        self.assertIn("z = self.extracted_process(b, x)", content)

if __name__ == "__main__":
    unittest.main()
