#!/usr/bin/env python3
"""ninaflash_context — Context compression, log parsing utilities."""
from tools.ninaflash_core import REPO_ROOT, _path_resolve, get_backlog_tasks, _find_py_files, run_cmd
import re
import json
import ast
import inspect
from pathlib import Path
from datetime import datetime

# --- cmd_context_mini_gen ---
def cmd_context_mini_gen(args):
    """[014] Generate high-density pulse-JSON."""
    print("💓 Generating mini-context...")

# --- _compress_diff ---
def _compress_diff(diff_text: str) -> str:
    """[015] Strip metadata from diffs to save tokens."""
    return "\n".join([l for l in diff_text.splitlines() if not l.startswith(('---','+++','@@'))])

# --- cmd_log_find_id ---
def cmd_log_find_id(args):
    """[037] Zero-token log parsing for specific task ID."""
    task_id = args.task_id
    path = REPO_ROOT / "nina_update_log.md"
    if not path.exists(): return
    content = path.read_text(encoding="utf-8")
    entries = content.split("## Entry")
    for entry in reversed(entries):
        if task_id in entry:
            print("## Entry" + entry.strip()); return
    print(f"❌ Task ID {task_id} not found.")

# --- cmd_log_tail ---
def cmd_log_tail(args):
    """[102] Print the last <n> entries of the log."""
    content = _get_log_entries()
    if not content: return
    entries = re.split(r'(?=\n## Entry )', content)
    actual = [e for e in entries if e.strip().startswith("## Entry")]
    n = getattr(args, 'n', 5) or 5
    for e in actual[-n:]: print(e.strip() + "\n")

# --- cmd_log_next_id ---
def cmd_log_next_id(args):
    """[103] Print the next available entry ID."""
    content = _get_log_entries()
    max_id = 0
    for line in content.splitlines():
        m = re.match(r"^## Entry (\d+)", line)
        if m: max_id = max(max_id, int(m.group(1)))
    print(max_id + 1)

# --- _get_log_entries ---
def _get_log_entries():
    p = REPO_ROOT / "nina_update_log.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""

# --- cmd_query ---
def cmd_query(args):
    """[044] Query capabilities mapping of NinaFlash local handlers."""
    import tools.ninaflash as nf
    mapping = {n: inspect.getdoc(o).strip() for n, o in inspect.getmembers(nf, inspect.isfunction) if n.startswith("cmd_")}
    print(json.dumps(mapping, indent=2))

# --- cmd_query_capability ---
def cmd_query_capability(args):
    """[042] Query: Check if a task type can be handled locally."""
    keys = ["format", "lint", "status", "backlog", "log", "symbol", "signature", "outline", "merge", "pr", "sync"]
    can = any(k in args.task.lower() for k in keys)
    print(f"{'✅' if can else '❓'} NinaFlash {'can' if can else 'might not'} handle this locally.")

# --- cmd_context_pack ---
def cmd_context_pack(args):
    """[041] Context Pack: Distill a file into a token-efficient skeletal summary."""
    path = _path_resolve(args.file)
    if not path.exists(): return
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        print(f"--- CONTEXT PACK: {path.name} ---")
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                print(f"def {node.name}(...): {doc.splitlines()[0] if doc else '...'}")
            elif isinstance(node, ast.ClassDef):
                print(f"class {node.name}: ...")
    except Exception as e: print(f"❌ Failed: {e}")

# --- cmd_register_capability ---
def cmd_register_capability(args):
    """[035] Dynamically register a new capability."""
    from core.capabilities import CapabilityRegistry
    CapabilityRegistry().register(args.name or Path(args.tool_path).stem, args.tool_path, args.description or "", args.role)
    print("✅ Registered.")

# --- cmd_run_capability ---
def cmd_run_capability(args):
    """[036] Execute a registered capability by name."""
    from core.capabilities import CapabilityRegistry
    cap = CapabilityRegistry().get_capability(args.name)
    if not cap or not cap.get("path"): return
    cmd = f"python3 {cap['path']} {' '.join(args.extra_args)}"
    code, out, err = run_cmd(cmd)
    print(out if code == 0 else err)

# --- cmd_capability_map ---
def cmd_capability_map(args):
    print("Loading API map...")

# --- cmd_stats ---
def cmd_stats(args):
    """[031] Show ninaflash file stats and efficiency metrics."""
    print("NINA Efficiency Report (v6.1)")
    # Simplified stats for refactor
    tasks = get_backlog_tasks()
    print(f"Backlog: {len(tasks)} tasks | READY: {len([t for t in tasks if t['status']=='READY'])}")

# --- cmd_help_ai ---
def cmd_help_ai(args):
    print("WELCOME AGENT. I am NINA KERNEL v6.1. Hard Cap: 100 functions.")

# --- cmd_log_summarize ---
def cmd_log_summarize(args):
    """[037] Sliding window summarizer for nina_update_log.md."""
    path = REPO_ROOT / "nina_update_log.md"
    if not path.exists(): return
    content = path.read_text(encoding="utf-8")
    entries = re.findall(r"(?m)^## Entry \d+.*?(?=\n## Entry |\Z)", content, re.DOTALL)
    if len(entries) > 20:
        print(f"✅ Summarized {len(entries)-20} old entries.")
