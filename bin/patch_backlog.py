from pathlib import Path

backlog_path = Path("docs/space/jules_backlog.md")
content = backlog_path.read_text()
content = content.replace(
    "| AG-J-02 | `tests/test_task_store.py` | Unit tests for TaskStore: CRUD, persistence, TTL, status transitions | `NEEDS_SPEC` | AG-B-01 |",
    "| AG-J-02 | `tests/test_task_store.py` | Unit tests for TaskStore: CRUD, persistence, TTL, status transitions | `DONE` | AG-B-01 |"
)
backlog_path.write_text(content)
