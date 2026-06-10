📦 MEGA-TASK: NF-ARCHIVE Historical Offloading (AG-M-09)
Assignee: Jules (Async Cloud Coder)
Objective: Keep the main working documents lean by archiving historical data.

🏗️ Domain 1: Backlog Archiving
- nf backlog archive: Move all tasks with status `DONE` or `DEFERRED` from `docs/space/jules_backlog.md` to `docs/archive/jules_backlog_archive.md`.

🧠 Domain 2: Error Register Archiving
- nf error archive: Move `✅ FIXED` entries from `docs/space/nina_error_register.md` to `exports/nina_error_register_archive.md`.

📝 Acceptance Criteria:
- Archiving must be idempotent.
- Maintain a 10-entry "Recent History" in the main files for immediate context.
