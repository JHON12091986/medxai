import argparse
import sys
from datetime import datetime
from core.task_manager.task_spec import TaskSpec
from core.task_manager.queue import TaskQueue
from core.task_manager.dispatcher import TaskDispatcher

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="NINA Task Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # list
    subparsers.add_parser("list", help="List all pending tasks")

    # stats
    subparsers.add_parser("stats", help="Show queue stats")

    # dispatch
    subparsers.add_parser("dispatch", help="Dispatch next pending task")

    # add
    add_parser = subparsers.add_parser("add", help="Add a task to the queue")
    add_parser.add_argument("--id", required=True, help="Task ID, e.g. VAULT-001")
    add_parser.add_argument("--title", required=True, help="One-line task title")
    add_parser.add_argument("--body", required=True, help="Full prompt or task body")
    add_parser.add_argument("--priority", required=True, choices=["P1", "P2", "P3"], help="Priority")
    add_parser.add_argument("--tier", required=True, choices=["INFRA", "OMNI", "PERF", "OBS", "GOVERN", "BACKLOG"], help="Tier")
    add_parser.add_argument("--source", default="manual", help="Source")
    add_parser.add_argument("--depends-on", nargs="*", default=[], help="Dependencies (list of task IDs)")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a task as DONE")
    done_parser.add_argument("task_id", help="Task ID to mark DONE")
    done_parser.add_argument("--pr", type=int, default=0, help="PR number associated with task completion")

    # purge
    purge_parser = subparsers.add_parser("purge", help="Purge old done tasks")
    purge_parser.add_argument("--keep", type=int, default=50, help="Number of done tasks to keep")

    parsed = parser.parse_args(args)

    queue = TaskQueue()

    if parsed.command == "list":
        pending = queue.list_pending()
        if not pending:
            print("No pending tasks.")
            return
        print(f"{'Task ID':<15} | {'Priority':<8} | {'Title'}")
        print("-" * 60)
        for t in pending:
            print(f"{t.task_id:<15} | {t.priority:<8} | {t.title}")

    elif parsed.command == "stats":
        s = queue.stats()
        print("Queue Statistics:")
        for k, v in s.items():
            print(f"  {k.capitalize()}: {v}")

    elif parsed.command == "dispatch":
        dispatcher = TaskDispatcher(queue)
        res = dispatcher.dispatch_next()
        if res:
            print(f"Dispatch Result: {res}")
        else:
            print("Nothing to dispatch (queue empty or all tasks blocked/already done).")

    elif parsed.command == "add":
        spec = TaskSpec(
            task_id=parsed.id,
            title=parsed.title,
            body=parsed.body,
            priority=parsed.priority,
            tier=parsed.tier,
            source=parsed.source,
            status="PENDING",
            created_at=datetime.now().isoformat(),
            depends_on=parsed.depends_on
        )
        success = queue.enqueue(spec)
        if success:
            print(f"Successfully enqueued task: {parsed.id}")
        else:
            print(f"Failed to enqueue task (idempotency key / task already exists): {parsed.id}")

    elif parsed.command == "done":
        success = queue.mark_done(parsed.task_id, pr_number=parsed.pr)
        if success:
            print(f"Marked task {parsed.task_id} as DONE (PR {parsed.pr})")
        else:
            print(f"Task not found: {parsed.task_id}")

    elif parsed.command == "purge":
        removed = queue.purge_done(keep_last=parsed.keep)
        print(f"Purged {removed} old DONE/SKIPPED tasks from the queue.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
