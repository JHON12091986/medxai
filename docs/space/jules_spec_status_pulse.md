💓 MEGA-TASK: NF-STATUS High-Density Pulse (AG-M-08)
Assignee: Jules (Async Cloud Coder)
Objective: Minimize context bloat by providing a ultra-short project pulse.

🏗️ Domain 1: The Pulse Command
- nf status --pulse: Returns exactly 10 lines containing:
  1. Git SHA + Branch
  2. Venv Status
  3. Last Sync Timestamp
  4. Active Lock Status (jules_lock.txt summary)
  5. Backlog Tally (READY/DONE)
  6. Recent Errors (last 3 from nina_error_register.md)
  7. Thermal/VRAM Status

🧠 Domain 2: Zero-Token Log Parsing
- nf log find-id <task_id>: Return only the log entry associated with a specific task ID without reading the full log file.

📝 Acceptance Criteria:
- Pulse output must be under 1KB.
- Command must be registered as a primary `ninaflash` capability.
