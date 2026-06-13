#!/usr/bin/env python3
"""ninaflash_memory — Cross-session memory stash and checkpoint/resume."""
from tools.ninaflash_core import REPO_ROOT, run_cmd
import json
import sys
from datetime import datetime
from pathlib import Path

# --- cmd_memory_stash ---
def cmd_memory_stash(args):
    """[037] Save a snippet of working memory."""
    text = args.text
    stash_path = REPO_ROOT / "data" / "memory_stash.json"
    stash_path.parent.mkdir(parents=True, exist_ok=True)
    stash = []
    if stash_path.exists():
        try: stash = json.loads(stash_path.read_text())
        except: pass
    stash.append({"ts": datetime.now().isoformat(), "text": text})
    stash_path.write_text(json.dumps(stash, indent=2))
    print(f"✅ Memory stashed: '{text[:50]}...'")

# --- cmd_session_checkpoint ---
def cmd_session_checkpoint(args):
    """[022] Save session state."""
    _, branch, _ = run_cmd("git branch --show-current")
    _, diff, _ = run_cmd("git diff --name-only")
    checkpoint = {
        "branch": branch.strip(),
        "changed": [f for f in diff.strip().split("\n") if f],
        "goal": getattr(args, "goal", ""),
        "ts": datetime.now().isoformat()
    }
    path = REPO_ROOT / "data/session_checkpoint.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checkpoint, indent=2))
    print(f"✅ Checkpoint saved ({branch.strip()}).")

# --- cmd_session_resume ---
def cmd_session_resume(args):
    """[023] Resume session state."""
    path = REPO_ROOT / "data/session_checkpoint.json"
    if not path.exists(): return
    cp = json.loads(path.read_text())
    print(f"🔄 Resuming {cp['branch']} from {cp['ts']}")
    run_cmd(f"git checkout {cp['branch']}")
    _, status, _ = run_cmd("git status --short")
    if status: print(f"Current changes:\n{status}")

# --- cmd_memory_session_save ---
def cmd_memory_session_save(args):
    """[055] Save current session summary."""
    summary = getattr(args, "summary", "No summary") or "No summary"
    _, sha, _ = run_cmd("git rev-parse HEAD")
    _, branch, _ = run_cmd("git rev-parse --abbrev-ref HEAD")
    entry = {"ts": datetime.now().isoformat(), "summary": summary, "head": sha, "branch": branch}
    mem_path = REPO_ROOT / "data/session_memory.jsonl"
    mem_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mem_path, "a") as f: f.write(json.dumps(entry) + "\n")
    print("✅ Session saved.")

# --- cmd_memory_session_recall ---
def cmd_memory_session_recall(args):
    """[056] Recall last N session entries."""
    n = getattr(args, "n", 5) or 5
    path = REPO_ROOT / "data/session_memory.jsonl"
    if not path.exists(): return
    lines = path.read_text().splitlines()[-n:]
    for l in lines:
        d = json.loads(l)
        print(f"[{d['ts'][:10]}] {d['branch']}: {d['summary']}")

# --- cmd_memory_inject ---
def cmd_memory_inject(args):
    """[057] Inject session context for Gemini CLI bootstrap."""
    path = REPO_ROOT / "data/session_memory.jsonl"
    if not path.exists(): return
    lines = path.read_text().splitlines()[-3:]
    print("=== NINA SESSION CONTEXT ===")
    for l in reversed(lines):
        d = json.loads(l)
        print(f"Last session ({d['ts'][:10]}): {d['summary']}\nBranch: {d['branch']} | HEAD: {d['head'][:7]}")
    print("===========================")

# --- cmd_session_start ---
def cmd_session_start(args):
    from tools.session_ledger import SessionLedger
    ledger = SessionLedger(tool=args.tool, task_id=args.task_id)
    ledger._save()
    print(f"Session {ledger.session_id} started for {args.tool}")

# --- cmd_session_log ---
def cmd_session_log(args):
    from tools.session_ledger import get_active_session
    ledger = get_active_session(args.tool)
    if ledger:
        ledger.log_step(args.step, args.action, args.outcome, args.detail)
        print(f"Logged step {args.step}: {args.outcome}")

# --- cmd_session_preamble ---
def cmd_session_preamble(args):
    from tools.session_preamble import write_preamble_file
    path = write_preamble_file(args.tool)
    if path and path.exists(): print(path.read_text())
    else: print("No recovery needed.")

# --- cmd_session_done ---
def cmd_session_done(args):
    from tools.session_preamble import clear_preamble
    clear_preamble(args.tool)
    print("Session closed.")
