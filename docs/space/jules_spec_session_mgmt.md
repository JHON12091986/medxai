📦 MEGA-TASK: NF-SESSIONS Checkpoint & Resume (AG-M-12)
Assignee: Jules (Async Cloud Coder)
Objective: Ensure NINA's task state survives Gemini CLI session resets and crashes.

🏗️ Domain 1: Session Checkpointing
- nf session checkpoint: Save the current git branch, changed files, and the active "Goal" to `data/session_checkpoint.json`.
- nf session resume: Read the checkpoint and automatically restore the environment (git branch, re-verify changes).

🧠 Domain 2: Transient Memory
- nf memory stash <text>: Save a snippet of "Working Memory" (e.g., a specific line number or a temporary variable name) to a local JSON stash that persists across CLI restarts.

📝 Acceptance Criteria:
- Checkpoint file must be excluded from `.geminiignore` (it's for me to read).
- `ninaflash.py` implementation must handle JSON serialization errors gracefully.
