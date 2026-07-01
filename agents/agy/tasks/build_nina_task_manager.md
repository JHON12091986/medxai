# AGY TASK: Build NINA Native Task Manager
**Task ID:** AGY-TASK-20260618-TASKMAN
**Date:** 2026-06-18
**Author:** @aibony (via Perplexity)
**Priority:** P1
**Estimated scope:** 6-8 files, ~800 lines total

---

## CONTEXT — WHY THIS EXISTS

Right now, tasks for Jules are written manually as static `.md` files in `.jules/tasks/scheduled/`.
This works, but it means:
- New tasks require a human (or Perplexity) to manually author a slot file and commit it
- There is no runtime queue — Jules can't discover new tasks NINA generates during operation
- `idleloop.py` generates backlog suggestions but can't directly emit Jules tasks
- `nina_ooda.py` does OODA cycles but has no way to persist actionable outputs as dispatchable tasks
- `agy_task.sh` dispatches tasks but reads from static prompts, not a live queue

**The goal:** Build `core/task_manager/` — a lightweight, file-backed task queue that NINA can write to at runtime,
AGY can read from to dispatch tasks, and Jules can consume as work items. No database. No external deps.
Pure Python + JSON files.

---

## REPO FACTS (read before starting)

- Repo: `github.com/aibony/nina` — Python 3.11+, FastAPI, APScheduler, asyncio
- PROTECTED files (NEVER touch): `core/router.py`, `core/nina.py`, `guardian_engine.py`, `main.py`,
  `.env`, `interfaces/telegram_interface.py`, `tools/shell.py`, `ninagate/main.py`
- Existing task dispatch: `agy_task.sh` (bash), `tools/jules.py` (Python Jules API client)
- Existing idle loop: `idleloop.py` — generates backlog suggestions from OODA analysis
- Existing backlog: `docs/space/jules_backlog.md` — markdown backlog, read-only for this task
- Existing queue seed: `data/task_queue.json` — you will create this
- Guardian: run `./guardian` before any PR — it MUST pass
- Tests: `./venv/bin/pytest tests/ -v` must pass

---

## WHAT TO BUILD

### Architecture Overview

```
NINA runtime (idleloop.py, nina_ooda.py)
          │
          ▼  enqueue(task_spec)
core/task_manager/
  ├── __init__.py          # public API: enqueue, dequeue, list_pending, mark_done
  ├── queue.py             # TaskQueue class — file-backed JSON queue
  ├── task_spec.py         # TaskSpec dataclass — schema for a task
  ├── dispatcher.py        # Dispatcher — reads queue, emits to Jules or AGY
  └── watcher.py           # FileWatcher — watches data/task_queue.json for changes
          │
          ▼  dispatch(task)
tools/jules.py  OR  agy_task.sh
          │
          ▼
     Jules PR
```

State is persisted in `data/task_queue.json`.
All queue mutations are atomic (write to `.tmp`, then `os.replace`).

---

## FILE SPECIFICATIONS

### 1. `core/task_manager/task_spec.py`

```python
# TaskSpec dataclass — the schema for a single dispatchable task

@dataclass
class TaskSpec:
    task_id: str          # unique, e.g. "VAULT-001" or "IDLE-20260618-1017"
    title: str            # human-readable one-line title
    body: str             # full task body — the prompt Jules will receive
    priority: str         # "P1" | "P2" | "P3"
    tier: str             # "INFRA" | "OMNI" | "PERF" | "OBS" | "GOVERN" | "BACKLOG"
    source: str           # "idleloop" | "ooda" | "manual" | "scheduler"
    status: str           # "PENDING" | "DISPATCHED" | "DONE" | "SKIPPED" | "FAILED"
    created_at: str       # ISO8601
    dispatched_at: str    # ISO8601 or ""
    done_at: str          # ISO8601 or ""
    pr_number: int        # 0 if not dispatched
    idempotency_key: str  # SHA-256 of (task_id + title) — dedup guard
    tags: list[str]       # free-form tags, e.g. ["vault", "security"]
    target_files: list[str]  # files this task will touch
    depends_on: list[str]    # task_ids that must be DONE first
```

- `to_dict()` and `from_dict(d)` classmethods for JSON serialization
- `idempotency_key` is computed on creation: `hashlib.sha256(f"{task_id}:{title}".encode()).hexdigest()[:16]`
- Validation: `priority` must be P1/P2/P3, `status` must be one of the 5 valid values

---

### 2. `core/task_manager/queue.py`

```python
class TaskQueue:
    """
    File-backed, thread-safe task queue.
    Persists to data/task_queue.json.
    All writes are atomic (write temp, os.replace).
    """

    QUEUE_FILE = Path("data/task_queue.json")

    def __init__(self, queue_file: Path = None):
        ...

    def enqueue(self, spec: TaskSpec) -> bool:
        """
        Add a task to the queue.
        Returns False (no-op) if a task with the same idempotency_key already exists
        in any status. This is the PRIMARY dedup guard.
        Returns True if successfully enqueued.
        """

    def dequeue(self, priority_order: list[str] = None) -> TaskSpec | None:
        """
        Pop the highest-priority PENDING task.
        priority_order defaults to ["P1", "P2", "P3"].
        Also checks depends_on — only returns a task whose dependencies are all DONE.
        Returns None if queue is empty or no unblocked tasks.
        """

    def peek(self, n: int = 5) -> list[TaskSpec]:
        """Return top N pending tasks without removing them."""

    def mark_done(self, task_id: str, pr_number: int = 0) -> bool:
        """Mark a task DONE, set done_at and pr_number."""

    def mark_skipped(self, task_id: str, reason: str = "") -> bool:
        """Mark a task SKIPPED."""

    def mark_failed(self, task_id: str, reason: str = "") -> bool:
        """Mark a task FAILED."""

    def list_pending(self) -> list[TaskSpec]:
        """Return all PENDING tasks."""

    def list_all(self) -> list[TaskSpec]:
        """Return all tasks regardless of status."""

    def stats(self) -> dict:
        """
        Return summary: {"total": N, "pending": N, "done": N,
                         "skipped": N, "failed": N, "dispatched": N}
        """

    def purge_done(self, keep_last: int = 50) -> int:
        """Remove all DONE/SKIPPED tasks older than keep_last. Returns count removed."""
```

**Thread safety:** Use `threading.Lock`. All reads and writes acquire the lock.
**Atomic writes:** `json.dump` to a `.tmp` file, then `os.replace(tmp, queue_file)`.
**File format:** JSON array of TaskSpec dicts at top level.

---

### 3. `core/task_manager/dispatcher.py`

```python
class TaskDispatcher:
    """
    Reads from TaskQueue and dispatches tasks to Jules or AGY.
    Does NOT modify core/router.py or any protected file.
    """

    def __init__(self, queue: TaskQueue, dry_run: bool = False):
        ...

    def dispatch_next(self) -> dict | None:
        """
        Pop the next PENDING unblocked task from the queue.
        Check idempotency via tools/jules.py (open PRs, git log).
        If clear: call tools/jules.py dispatch OR write .jules task file.
        Mark task as DISPATCHED in queue.
        Returns dispatch result dict or None if nothing to dispatch.
        """

    def dispatch_all_pending(self, limit: int = 3) -> list[dict]:
        """Dispatch up to `limit` pending tasks. Returns list of results."""

    def _check_idempotency(self, spec: TaskSpec) -> bool:
        """
        Returns True if task is safe to dispatch (not already done).
        Checks:
        1. Git log for task_id keyword
        2. data/task_queue.json for existing DONE/DISPATCHED entry with same idempotency_key
        3. docs/audit/scheduler_skip_log.md for skip entries
        Returns False (block dispatch) if evidence of prior implementation found.
        """

    def _build_jules_task_file(self, spec: TaskSpec) -> Path:
        """
        Write a .jules/tasks/runtime/<task_id>.md file from the spec.
        This is the handoff format Jules reads.
        Returns path to the written file.
        """

    def _notify_telegram(self, message: str):
        """
        Send Telegram notification via interfaces/telegram_interface.py.
        Import it read-only — do NOT modify it.
        Wrap in try/except so failure never blocks dispatch.
        """
```

---

### 4. `core/task_manager/watcher.py`

```python
class QueueWatcher:
    """
    Watches data/task_queue.json for new PENDING tasks.
    Uses polling (no inotify dependency) — checks every `interval` seconds.
    On new task detected: calls callback(task_spec).
    Runs in a daemon thread — safe to start from crons/manager.py.
    """

    def __init__(self, queue: TaskQueue, callback, interval: int = 30):
        ...

    def start(self):
        """Start the watcher daemon thread."""

    def stop(self):
        """Stop the watcher thread gracefully."""
```

---

### 5. `core/task_manager/__init__.py`

Public API — expose these at package level:

```python
from core.task_manager.queue import TaskQueue
from core.task_manager.task_spec import TaskSpec
from core.task_manager.dispatcher import TaskDispatcher
from core.task_manager.watcher import QueueWatcher

__all__ = ["TaskQueue", "TaskSpec", "TaskDispatcher", "QueueWatcher"]
```

---

### 6. `core/task_manager/cli.py`

Simple CLI for manual queue inspection and injection:

```bash
python3 -m core.task_manager.cli list           # list all pending tasks
python3 -m core.task_manager.cli stats          # show queue stats
python3 -m core.task_manager.cli dispatch       # dispatch next pending task
python3 -m core.task_manager.cli add --id VAULT-001 --title "..." --body "..." --priority P1 --tier INFRA
python3 -m core.task_manager.cli done VAULT-001 --pr 228
python3 -m core.task_manager.cli purge          # purge old DONE entries
```

Use `argparse`. No external CLI libraries.

---

### 7. Wire `idleloop.py` output → queue (MINIMAL CHANGE)

Read `idleloop.py` IN FULL before touching it. It is 12,864 bytes — understand the full structure.

Find where IDLE suggestions are written to `docs/space/jules_backlog.md` (the file-append block).
After that block, ADD (do not replace) a small shim:

```python
# After writing to backlog, also enqueue as a TaskSpec
try:
    from core.task_manager import TaskQueue, TaskSpec
    _tq = TaskQueue()
    _spec = TaskSpec(
        task_id=f"IDLE-{datetime.now().strftime('%Y%m%d-%H%M')}",
        title=suggestion_title,      # adapt to actual variable name in idleloop.py
        body=suggestion_body,        # adapt to actual variable name
        priority="P3",
        tier="BACKLOG",
        source="idleloop",
        status="PENDING",
        created_at=datetime.now().isoformat(),
        dispatched_at="",
        done_at="",
        pr_number=0,
        idempotency_key="",  # computed in __post_init__
        tags=["idle", "backlog"],
        target_files=[],
        depends_on=[]
    )
    _tq.enqueue(_spec)
except Exception as _e:
    pass  # Never let queue failure crash idleloop
```

**Wrap the entire shim in try/except.** If task_manager import fails, idleloop must continue working exactly as before. This is an additive, non-breaking change.

---

### 8. Wire scheduler slots → queue (NEW FILE — no existing file changes)

Create `core/task_manager/seed_from_slots.py`:
- Reads all 24 slot files from `.jules/tasks/scheduled/slot-*.md`
- Parses the `**Backlog ref:**` and `**PR title:**` lines
- Creates a `TaskSpec` for each slot and enqueues it (dedup guard prevents duplicates)
- Designed to be run once on first boot: `python3 -m core.task_manager.seed_from_slots`
- Also callable from `crons/manager.py` at startup

---

## TEST REQUIREMENTS

Create `tests/test_task_manager.py` covering:

```python
# 1. Enqueue + dedup guard
def test_enqueue_dedup():
    # Enqueue same task twice — second enqueue returns False, queue has 1 item

# 2. Priority ordering
def test_dequeue_priority():
    # Enqueue P3, P1, P2 — dequeue returns P1 first

# 3. Dependency blocking
def test_dequeue_dependency_blocking():
    # Task B depends_on=["task-A"]. Enqueue B, then A (DONE).
    # Before A is DONE: dequeue returns None
    # After mark_done(A): dequeue returns B

# 4. Atomic write (no corruption on concurrent access)
def test_concurrent_enqueue():
    # 10 threads enqueue 10 unique tasks — final queue has exactly 10 items

# 5. Purge
def test_purge_done():
    # Enqueue 5 tasks, mark 3 done, purge with keep_last=1 — 3 remain (2 pending + 1 done)

# 6. Stats
def test_stats():
    # Enqueue 2 P1 + 1 P2, mark 1 done — stats shows correct counts

# 7. CLI list command
def test_cli_list(capsys):
    # Enqueue 2 tasks, run cli.main(["list"]) — output contains both task IDs
```

Use `tmp_path` (pytest fixture) for all queue file operations — never write to real `data/task_queue.json` in tests.

---

## EXECUTION ORDER

1. Create `core/task_manager/task_spec.py`
2. Create `core/task_manager/queue.py`
3. Create `core/task_manager/dispatcher.py`
4. Create `core/task_manager/watcher.py`
5. Create `core/task_manager/__init__.py`
6. Create `core/task_manager/cli.py`
7. Create `core/task_manager/seed_from_slots.py`
8. Modify `idleloop.py` (minimal shim only)
9. Create `tests/test_task_manager.py`
10. Run `./venv/bin/pytest tests/test_task_manager.py -v` — fix until all pass
11. Run `./guardian` — fix until passes
12. Open PR titled: `feat(task-manager): build nina-native task queue engine`

---

## VALIDATION GATES (ALL must pass before opening PR)

```bash
# 1. Syntax check all new files
python3 -m py_compile core/task_manager/task_spec.py
python3 -m py_compile core/task_manager/queue.py
python3 -m py_compile core/task_manager/dispatcher.py
python3 -m py_compile core/task_manager/watcher.py
python3 -m py_compile core/task_manager/cli.py
python3 -m py_compile core/task_manager/seed_from_slots.py
python3 -m py_compile idleloop.py

# 2. Pyflakes (no unused imports)
pyflakes core/task_manager/
pyflakes idleloop.py

# 3. Tests
./venv/bin/pytest tests/test_task_manager.py -v

# 4. Import smoke test
python3 -c "from core.task_manager import TaskQueue, TaskSpec, TaskDispatcher, QueueWatcher; print('imports OK')"

# 5. CLI smoke test
python3 -m core.task_manager.cli stats

# 6. idleloop still imports cleanly
python3 -c "import idleloop; print('idleloop OK')"

# 7. Guardian
./guardian
```

---

## PROTECTED FILES (NEVER TOUCH)

```
core/router.py
core/nina.py
guardian_engine.py
main.py
.env
interfaces/telegram_interface.py
tools/shell.py
ninagate/main.py
agy_task.sh          # read-only reference
agy_prompt.md        # read-only reference
```

---

## PR TITLE

`feat(task-manager): build nina-native task queue engine`

## PR BODY TEMPLATE

```
Closes: (no issue — new feature)

## What
Builds `core/task_manager/` — a file-backed, thread-safe task queue that lets NINA
enqueue tasks at runtime (from idleloop, ooda cycles, or manual injection) and dispatch
them to Jules automatically.

## Files Added
- core/task_manager/task_spec.py — TaskSpec dataclass with idempotency_key
- core/task_manager/queue.py — atomic JSON queue with dedup and dependency ordering
- core/task_manager/dispatcher.py — reads queue, emits Jules task files
- core/task_manager/watcher.py — daemon thread polling for new tasks
- core/task_manager/__init__.py — public API
- core/task_manager/cli.py — argparse CLI for manual inspection
- core/task_manager/seed_from_slots.py — seeds queue from existing .jules slot files
- tests/test_task_manager.py — 7 test cases covering dedup, priority, concurrency

## Files Modified
- idleloop.py — additive shim only (wrapped in try/except, zero behaviour change on failure)
- data/task_queue.json — created as empty queue

## Guardian
- [ ] ./guardian PASS
- [ ] pytest tests/test_task_manager.py PASS
```
