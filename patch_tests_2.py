import sys
import re

with open("tests/test_task_store.py", "r", encoding="utf-8") as f:
    content = f.read()

# Patch test_delete_task_hard
orig_test = """    def test_delete_task_hard(self, store: TaskStore):
        t = store.create_task("Delete me")
        assert store.delete_task(t.id) is True
        assert store.get_task(t.id) is None"""

new_test = """    def test_delete_task_hard(self, store: TaskStore):
        t = store.create_task("Delete me")
        assert store.delete_task(t.id) is True
        with pytest.raises(TaskNotFoundError):
            store.get_task(t.id)"""

content = content.replace(orig_test, new_test)

with open("tests/test_task_store.py", "w", encoding="utf-8") as f:
    f.write(content)
