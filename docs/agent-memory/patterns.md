# NINA Agent Patterns

## Backlog Protocol
- **Goal:** Keep tracking docs accurate.
- **Restraint:** NEVER use bash echo; NEVER update tracker from inside Jules.
- **Action:** `ninaflash` runs Python script post-merge to change status (`IN_PROGRESS` -> `DONE`), add PR number and date, then runs `./nina_sync.sh`.

## Task Tracker Update Protocol Example
```python
from pathlib import Path
tracker_path = Path("/home/aibony/nina/docs/space/jules_task_tracker.md")
content = tracker_path.read_text()
content = content.replace("... ⏳ QUEUED ...", "... ✅ MERGED ... PR #123 ...")
tracker_path.write_text(content)
```

## Logging Pattern
- **Goal:** Maintain accurate, structured update logs.
- **Restraint:** NEVER use heredoc or direct `bash echo >>` to `nina_update_log.md`.
- **Action:** Append log entries using Python. Auto-detect entry number, include date, title, changes, verifications, and rollback path.

## Surgical Merge Protocol (For Jules PRs)
- **Goal:** Prevent Jules PRs from overwriting local truths.
- **Restraint:** Do NOT merge Jules PRs blindly if they touch critical files (AGENTS.md, nina_sync.sh, nina_update_log.md).
- **Action:** Backup critical files -> merge PR -> restore regressions -> commit fix -> run `nina_sync.sh`.
