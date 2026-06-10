🛡️ MEGA-TASK: SEC-IGNORE Global Context Filtering (AG-M-06)
Assignee: Jules (Async Cloud Coder)
Objective: Automatically prune the agent's context window using project-wide exclusion rules.

🏗️ Domain 1: .geminiignore Implementation
- Create a canonical `.geminiignore` in the repo root.
- Exclusion list: `logs/`, `data/plans/`, `upgrades/backups/`, `*.pyc`, `__pycache__/`, `venv/`.

🧠 Domain 2: Tool-Level Compliance
- Update `ninaflash.py` and `tools/files.py` to respect `.geminiignore` patterns when listing or reading files.
- nf check ignore: A diagnostic command that shows which files are currently being hidden from the agent.

📝 Acceptance Criteria:
- Reduced "noise" in global searches (`grep_search`).
- No sensitive logs or large data files leaked into the cloud context.
