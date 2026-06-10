📝 MEGA-TASK: DOC-COMP Instruction Compression (AG-M-04)
Assignee: Jules (Async Cloud Coder)
Objective: Refactor `AGENTS.md` into a high-density, token-efficient directive list.

🏗️ Domain 1: Structural Compression
- Move verbose "Guides", "Tool Lists", and "Examples" from `AGENTS.md` to dedicated files in `docs/agent-memory/workflow.md` or `docs/agent-memory/patterns.md`.
- Replace these with one-line pointers (e.g., "See docs/patterns.md for log formatting").

🧠 Domain 2: Directive Mapping
- Rewrite the "Rules of Engagement" into high-density "Directive Lists" (Goal-Restraint-Action).
- Example: Replace "Please never use git add ." with "Directive: NEVER use 'git add .'; stage specific files only."

📝 Acceptance Criteria:
- `AGENTS.md` file size reduced by >40%.
- All core constraints preserved.
