"""
tools/post_task_hook.py
Post-task documentation auto-update hook.
Parses logs from data/gemini_scratch.jsonl since the last 'action=start' entry,
generates a routing history block, appends it to AGENTS.md, and notifies via Telegram.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Banned tool patterns to check for Rule 0 compliance
BANNED_PATTERNS = [
    ("run_shell_command: cat ", "nf file read"),
    ("run_shell_command: grep", "nf file grep"),
    ("run_shell_command: git log", "nf git log"),
    ("run_shell_command: git diff", "nf file diff"),
    ("run_shell_command: git status", "nf git changed"),
    ("run_shell_command: ls", "nf code index"),
    ("run_shell_command: find", "nf code index"),
    ("run_shell_command: head", "nf file read"),
    ("run_shell_command: tail", "nf file read"),
    ("run_shell_command: wc", "nf file read"),
]

# ── SPEC-01: Protected space files ────────────────────────────────────────────
# These files must NEVER be blanked or deleted by any hook operation.
# Any attempt to write empty content to them will abort with an error.
PROTECTED_SPACE_FILES = {
    "nexus_discoveries.md",
    "nina_session_log.md",
    "nina_error_register.md",
    "jules_backlog.md",
    "nina_contract.md",
}
# ──────────────────────────────────────────────────────────────────────────────


def _guard_protected_write(path: Path, content: str) -> None:
    """
    Raise RuntimeError if writing `content` to `path` would blank a protected file.
    Call this before any write that touches docs/space/.
    """
    if path.name in PROTECTED_SPACE_FILES:
        if not content.strip():
            raise RuntimeError(
                f"SPEC-01 GUARD: Refusing to blank protected file {path.name}. "
                "Aborting hook to preserve integrity."
            )


def main():
    parser = argparse.ArgumentParser(description="Post-task doc auto-update hook")
    parser.add_argument("--summary", help="One-line summary override for the Telegram notification")
    parser.add_argument("--dry-run", action="store_true", help="Print the generated block without writing/sending")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent.resolve()
    scratch_path = repo_root / "data" / "gemini_scratch.jsonl"
    agents_path = repo_root / "AGENTS.md"

    if not scratch_path.exists():
        print(f"❌ Error: {scratch_path} not found.")
        sys.exit(1)

    with open(scratch_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the last "action": "start"
    start_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        try:
            entry = json.loads(lines[i])
            if entry.get("action") == "start":
                start_idx = i
                break
        except Exception:
            continue

    if start_idx == -1:
        print("⚠️ Warning: No 'start' action found in logs. Using all logs.")
        start_idx = 0

    session_entries = []
    for line in lines[start_idx:]:
        try:
            session_entries.append(json.loads(line))
        except Exception:
            continue

    if not session_entries:
        print("❌ Error: No valid JSON entries found in session log.")
        sys.exit(1)

    start_entry = session_entries[0]
    done_entry = None
    for entry in reversed(session_entries):
        if entry.get("action") == "done":
            done_entry = entry
            break

    # 1. Parse fields
    date_str = datetime.now().strftime("%Y-%m-%d")
    tool_used = "Antigravity (Gemini 2.5 Flash)"

    # Check if we ran tasks that are mechanical
    offload_suggestions = []
    touched_files = set()
    banned_violations = []

    for entry in session_entries:
        detail = entry.get("detail", "")
        file_path = entry.get("file", "")
        if file_path:
            touched_files.add(Path(file_path).name)

        # Check for Rule 0 violations in this session
        for pattern, alt in BANNED_PATTERNS:
            if pattern.lower() in detail.lower():
                banned_violations.append(f"{pattern.strip()} (use {alt} instead)")

        # Offload opportunities
        if "compile" in detail.lower() or "pyflakes" in detail.lower():
            offload_suggestions.append("python compile and syntax validation")
        if "update_index" in detail.lower() or "validate_index" in detail.lower():
            offload_suggestions.append("index updates and governance checks")
        if "git status" in detail.lower() or "git changed" in detail.lower():
            offload_suggestions.append("git status checks")

    if offload_suggestions:
        offload_suggestion = f"Mechanical tasks ({', '.join(sorted(list(set(offload_suggestions)))[:3])}) → 100% NinaFlash next time."
    else:
        offload_suggestion = "Mechanical tasks (formatting, simple verification) → route to NinaFlash next time."

    # Escalation triggers: any high-risk files edited?
    escalation_files = []
    high_risk_stems = {"router", "telegram_interface", "main", "guardian_engine"}
    for f in touched_files:
        stem = Path(f).stem
        if stem in high_risk_stems:
            escalation_files.append(f)
    if escalation_files:
        escalation_trigger = f"Modifications to high-risk files ({', '.join(escalation_files)}) → Cloud LLM review required."
    else:
        escalation_trigger = "None."

    # Routing win
    if done_entry:
        routing_win = done_entry.get("detail", "")
    else:
        routing_win = start_entry.get("detail", "")
    if routing_win.lower().startswith("task summary:"):
        routing_win = routing_win[len("task summary:"):].strip()
    # Capitalize first letter
    if routing_win:
        routing_win = routing_win[0].upper() + routing_win[1:]

    # Context hint
    context_hint = "Ensure validate_index.py is run to update governance index metadata before final sync."
    if "validate_index.py" in touched_files:
        context_hint = "Keep validate_index.py updated to maintain test exemption rules for new modules."
    elif "quota_alert.py" in touched_files or "bench_runner.py" in touched_files:
        context_hint = "Ensure background schedulers and engines are registered in test exemption lists to prevent warning build-up."

    # Rule 0 violation
    if banned_violations:
        rule0_violation = f"Violations detected: {'; '.join(banned_violations)}"
    else:
        rule0_violation = "None. All file operations compliant."

    # Format output block
    history_block = f"""### [{date_str}] Session Update — {tool_used}
- OFFLOAD_OPPORTUNITY: {offload_suggestion}
- ESCALATION_TRIGGER: {escalation_trigger}
- ROUTING_WIN: {routing_win}
- CONTEXT_HINT: {context_hint}
- RULE0_VIOLATION: {rule0_violation}
"""

    if args.dry_run:
        print("=== DRY RUN: ROUTING HISTORY BLOCK ===")
        print(history_block)
        print("======================================")
        sys.exit(0)

    # 2. Append to AGENTS.md under "## NinaGate Routing History"
    if not agents_path.exists():
        print(f"❌ Error: {agents_path} not found.")
        sys.exit(1)

    agents_content = agents_path.read_text(encoding="utf-8")
    header_str = "## NinaGate Routing History"

    if header_str not in agents_content:
        print(f"❌ Error: Heading '{header_str}' not found in AGENTS.md.")
        sys.exit(1)

    # Insert right after the header line (plus an empty line)
    target_pos = agents_content.find(header_str) + len(header_str)

    # Find next newline
    insert_pos = agents_content.find("\n", target_pos)
    if insert_pos == -1:
        insert_pos = len(agents_content)
    else:
        insert_pos += 1  # Insert after the newline character

    updated_content = (
        agents_content[:insert_pos]
        + "\n"
        + history_block.strip()
        + "\n"
        + agents_content[insert_pos:]
    )

    # ── SPEC-01 guard before writing AGENTS.md ────────────────────────────────
    _guard_protected_write(agents_path, updated_content)
    # ─────────────────────────────────────────────────────────────────────────
    agents_path.write_text(updated_content, encoding="utf-8")
    print(f"✅ Successfully updated AGENTS.md routing history.")

    # 3. Send Telegram notification
    summary_text = args.summary if args.summary else routing_win
    iso_ts = datetime.now().isoformat()
    tele_msg = f"✅ NINA docs updated — {summary_text} — {iso_ts}"

    try:
        from telegram_notify import send_message
        success = send_message(tele_msg)
        if success:
            print("✅ Telegram notification sent.")
        else:
            print("⚠️ Telegram notification failed (check environment credentials).")
    except Exception as e:
        print(f"⚠️ Telegram notification import/send failed: {e}")

if __name__ == "__main__":
    main()
