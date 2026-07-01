import threading
from core.task_manager.task_spec import TaskSpec
from core.task_manager.queue import TaskQueue
from core.task_manager import cli

def test_enqueue_dedup(tmp_path):
    queue_file = tmp_path / "task_queue.json"
    queue = TaskQueue(queue_file=queue_file)

    spec1 = TaskSpec(
        task_id="TEST-001",
        title="Test Task 1",
        body="Body 1",
        priority="P1",
        tier="INFRA",
        source="manual",
        status="PENDING"
    )
    spec2 = TaskSpec(
        task_id="TEST-001",
        title="Test Task 1",
        body="Body 1",
        priority="P1",
        tier="INFRA",
        source="manual",
        status="PENDING"
    )

    assert queue.enqueue(spec1) is True
    assert queue.enqueue(spec2) is False
    assert len(queue.list_all()) == 1

def test_dequeue_priority(tmp_path):
    queue_file = tmp_path / "task_queue.json"
    queue = TaskQueue(queue_file=queue_file)

    spec3 = TaskSpec(task_id="T3", title="T3", body="B3", priority="P3", tier="INFRA", source="manual", status="PENDING")
    spec1 = TaskSpec(task_id="T1", title="T1", body="B1", priority="P1", tier="INFRA", source="manual", status="PENDING")
    spec2 = TaskSpec(task_id="T2", title="T2", body="B2", priority="P2", tier="INFRA", source="manual", status="PENDING")

    queue.enqueue(spec3)
    queue.enqueue(spec1)
    queue.enqueue(spec2)

    dequeued = queue.dequeue()
    assert dequeued is not None
    assert dequeued.task_id == "T1"

def test_dequeue_dependency_blocking(tmp_path):
    queue_file = tmp_path / "task_queue.json"
    queue = TaskQueue(queue_file=queue_file)

    spec_b = TaskSpec(task_id="task-B", title="B", body="Body B", priority="P1", tier="INFRA", source="manual", status="PENDING", depends_on=["task-A"])
    spec_a = TaskSpec(task_id="task-A", title="A", body="Body A", priority="P2", tier="INFRA", source="manual", status="PENDING")

    queue.enqueue(spec_b)
    queue.enqueue(spec_a)

    # Before A is DONE: B is blocked. A is returned.
    first = queue.dequeue()
    assert first is not None
    assert first.task_id == "task-A"

    queue.mark_dispatched("task-A")
    assert queue.dequeue() is None

    # After A is DONE: B is returned.
    queue.mark_done("task-A")
    second = queue.dequeue()
    assert second is not None
    assert second.task_id == "task-B"

def test_concurrent_enqueue(tmp_path):
    queue_file = tmp_path / "task_queue.json"
    queue = TaskQueue(queue_file=queue_file)

    def worker(i):
        spec = TaskSpec(
            task_id=f"CONC-{i}",
            title=f"Concurrent {i}",
            body="Body",
            priority="P3",
            tier="INFRA",
            source="manual",
            status="PENDING"
        )
        queue.enqueue(spec)

    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert len(queue.list_all()) == 10

def test_purge_done(tmp_path):
    queue_file = tmp_path / "task_queue.json"
    queue = TaskQueue(queue_file=queue_file)

    for i in range(5):
        spec = TaskSpec(task_id=f"T-{i}", title=f"T {i}", body="Body", priority="P3", tier="INFRA", source="manual", status="PENDING")
        queue.enqueue(spec)

    queue.mark_done("T-0")
    queue.mark_done("T-1")
    queue.mark_done("T-2")

    removed = queue.purge_done(keep_last=1)
    assert removed == 2

    remaining = queue.list_all()
    assert len(remaining) == 3
    statuses = [t.status for t in remaining]
    assert statuses.count("PENDING") == 2
    assert statuses.count("DONE") == 1

def test_stats(tmp_path):
    queue_file = tmp_path / "task_queue.json"
    queue = TaskQueue(queue_file=queue_file)

    spec1 = TaskSpec(task_id="T1", title="T1", body="B1", priority="P1", tier="INFRA", source="manual", status="PENDING")
    spec2 = TaskSpec(task_id="T2", title="T2", body="B2", priority="P1", tier="INFRA", source="manual", status="PENDING")
    spec3 = TaskSpec(task_id="T3", title="T3", body="B3", priority="P2", tier="INFRA", source="manual", status="PENDING")

    queue.enqueue(spec1)
    queue.enqueue(spec2)
    queue.enqueue(spec3)

    queue.mark_done("T1")

    s = queue.stats()
    assert s["total"] == 3
    assert s["pending"] == 2
    assert s["done"] == 1
    assert s["skipped"] == 0

def test_cli_list(capsys, tmp_path, monkeypatch):
    queue_file = tmp_path / "task_queue.json"
    monkeypatch.setattr(TaskQueue, "QUEUE_FILE", queue_file)

    queue = TaskQueue(queue_file=queue_file)
    spec1 = TaskSpec(task_id="CLI-1", title="Cli Task 1", body="B1", priority="P1", tier="INFRA", source="manual", status="PENDING")
    spec2 = TaskSpec(task_id="CLI-2", title="Cli Task 2", body="B2", priority="P2", tier="INFRA", source="manual", status="PENDING")

    queue.enqueue(spec1)
    queue.enqueue(spec2)

    cli.main(["list"])
    captured = capsys.readouterr()
    assert "CLI-1" in captured.out
    assert "CLI-2" in captured.out
