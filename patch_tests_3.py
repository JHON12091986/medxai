import sys
import re

with open("tests/test_task_store.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix unused variables
content = content.replace("original_content = (tmp_path / \"tasks.json\").read_text()", "_ = (tmp_path / \"tasks.json\").read_text()")
content = content.replace("mock_instance = mock_lock_cls.return_value.__enter__ = None", "mock_lock_cls.return_value.__enter__ = None")

with open("tests/test_task_store.py", "w", encoding="utf-8") as f:
    f.write(content)
