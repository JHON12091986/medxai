import re
from pathlib import Path
from datetime import datetime
from core.task_manager.task_spec import TaskSpec
from core.task_manager.queue import TaskQueue

def seed():
    """
    Reads all slot files from .jules/tasks/scheduled/slot-*.md,
    parses task details, and enqueues them into TaskQueue.
    """
    scheduled_dir = Path(".jules/tasks/scheduled")
    if not scheduled_dir.exists():
        print(f"Scheduled directory {scheduled_dir} does not exist. Skipping seed.")
        return

    queue = TaskQueue()
    slot_files = sorted(scheduled_dir.glob("slot-*.md"))

    print(f"Found {len(slot_files)} slot files to process.")
    enqueued_count = 0

    for file_path in slot_files:
        content = file_path.read_text(encoding="utf-8")
        first_line = content.splitlines()[0] if content.splitlines() else ""

        # Extract Task ID
        # 1. Check first line for [A-Z]+-\d+
        task_id_match = re.search(r"\b([A-Z]+-\d+)\b", first_line)
        if task_id_match:
            task_id = task_id_match.group(1)
        else:
            # 2. Check filename fallback, e.g. slot-01-vault-001.md -> VAULT-001
            fn_match = re.search(r"slot-\d+-([a-z]+-\d+)", file_path.name, re.IGNORECASE)
            if fn_match:
                task_id = fn_match.group(1).upper()
            else:
                task_id = f"SLOT-{file_path.stem.upper()}"

        # Extract Priority
        priority_match = re.search(r"Priority:\*\*?\s*(P[1-3])", content, re.IGNORECASE)
        priority = priority_match.group(1).upper() if priority_match else "P3"

        # Extract Tier
        tier_match = re.search(r"Tier:\*\*?\s*([A-Z]+)", content, re.IGNORECASE)
        tier = tier_match.group(1).upper() if tier_match else "BACKLOG"
        # Validate tier against choices: "INFRA" | "OMNI" | "PERF" | "OBS" | "GOVERN" | "BACKLOG"
        valid_tiers = {"INFRA", "OMNI", "PERF", "OBS", "GOVERN", "BACKLOG"}
        if tier not in valid_tiers:
            tier = "BACKLOG"

        # Extract Title
        title = ""
        # 1. Try **PR title:** or PR title:
        title_match = re.search(r"PR title:\*\*?\s*[`\"']?([^`\n\"']+)`?\"'?", content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # 2. Fall back to cleaning first line
            # E.g. "# Slot 01 — VAULT-001: Scoped Credential Vault Engine" -> "Scoped Credential Vault Engine"
            cleaned_first_line = re.sub(r"^#\s*Slot\s*\d+\s*[—\-]\s*[A-Z]+-\d+:\s*", "", first_line, flags=re.IGNORECASE)
            cleaned_first_line = re.sub(r"^#\s*", "", cleaned_first_line).strip()
            title = cleaned_first_line if cleaned_first_line else f"Scheduled task {task_id}"

        # Build TaskSpec
        spec = TaskSpec(
            task_id=task_id,
            title=title,
            body=content,
            priority=priority,
            tier=tier,
            source="scheduler",
            status="PENDING",
            created_at=datetime.now().isoformat(),
            tags=["scheduled", file_path.name],
            target_files=[],
            depends_on=[]
        )

        success = queue.enqueue(spec)
        if success:
            enqueued_count += 1
            print(f"Enqueued: {task_id} - {title} ({priority}, {tier})")
        else:
            print(f"Skipped (already exists): {task_id}")

    print(f"Seeding completed. Enqueued {enqueued_count} new tasks.")

if __name__ == "__main__":
    seed()
