🧹 MEGA-TASK: NF-CLEAN Automated Hygiene (AG-M-07)
Assignee: Jules (Async Cloud Coder)
Objective: Offload code linting and document formatting from the cloud agent to local ninaflash commands.

🏗️ Domain 1: Code Auto-Fixing
- nf check code --fix: Automatically run `ruff --fix` and `black` (if available) on the target file.
- Implement pre-commit hooks in `ninaflash` that prevent committing code with syntax errors.

🧠 Domain 2: Document Auto-Formatting
- nf doc check --fix: Automatically format the `nina_update_log.md` entry headers and tables to maintain repository standards.
- nf doc consolidate: Automatically move log entries older than 30 days into `exports/nina_update_log_archive.md`.

📝 Acceptance Criteria:
- No human intervention required for common linting/formatting fixes.
- `ninaflash.py` hard cap of 100 functions must be maintained (consolidate where possible).
