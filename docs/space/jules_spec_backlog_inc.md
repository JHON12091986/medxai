📊 MEGA-TASK: NF-BACKLOG Incremental State (AG-M-05)
Assignee: Jules (Async Cloud Coder)
Objective: Reduce token consumption by providing high-density summaries of project state instead of reading large markdown tables.

🏗️ Domain 1: Backlog Summarization
- nf backlog summary: Provide a 5-line summary of the backlog: count of READY, IN_PROGRESS, BLOCKED, and DONE tasks.
- nf task active: List only tasks currently in `IN_PROGRESS` or `IN_PR` along with the files they have locked in `jules_lock.txt`.

🧠 Domain 2: Incremental Logs
- nf log tail <n>: Read only the last <n> entries of `nina_update_log.md`.
- nf log next-id: Parse the update log to find the last entry number and return the next available ID (e.g., "173").

📝 Acceptance Criteria:
- Commands must be fast and zero-token in cloud (local execution).
- Update `ninaflash.py` help menu.
