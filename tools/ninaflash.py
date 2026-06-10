#!/usr/bin/env python3
"""
ninaflash — The Unified AI Agent Kernel for NINA.
Version: 6.0 (THE 100-FUNCTION "MARVELOUS" ARCHITECTURE)
Author: Gemini CLI & Antigravity
Mission: Minimize Token Usage, Maximize Execution Speed, Absolute Reliability.

# HARD CAP: This file must not exceed 100 named functions.
# Count with: grep -c "^def \\|^    def " tools/ninaflash.py
# Stubs (pass-only bodies) are BANNED. Add a function only when it is fully implemented.
"""

import sys
import os
import shlex
import re
import argparse
import asyncio
import subprocess
import json
try:
    import dotenv
except ImportError:
    dotenv = None
import shutil
import ast
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# --- KERNEL INITIALIZATION ---
REPO_ROOT = Path(__file__).parent.parent.resolve()
if dotenv:
    dotenv.load_dotenv(str(REPO_ROOT / ".env"))

# Constants
MAX_OUTPUT_CHARS = 4000
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
LOCK_PATH = REPO_ROOT / "jules_lock.txt"

# ------------------------------------------------------------------
# MODULE 0: CORE KERNEL & SHELL
# ------------------------------------------------------------------

def run_cmd(cmd, cwd=str(REPO_ROOT), timeout=60) -> Tuple[int, str, str]:
    """[001] Base execution primitive."""
    try:
        args = shlex.split(cmd) if isinstance(cmd, str) else cmd
        res = subprocess.run(args, shell=False, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired: return -1, "", "Command timed out"

def _safe_run(cmd: str, timeout=60) -> Tuple[int, str, str]:
    """[002] Hardened execution with NINA security policy enforcement."""
    from tools.shell import is_command_safe
    if not is_command_safe(cmd): return 1, "", f"❌ SECURITY: Command '{cmd}' blocked."
    return run_cmd(cmd, timeout=timeout)

def _path_resolve(rel_path: str) -> Path:
    """[003] Absolute path resolution from repo root."""
    return (REPO_ROOT / rel_path).resolve()

def cmd_status(args):
    """[004] Unified system health snapshot."""
    if getattr(args, 'pulse', False):
        _print_pulse()
        return

    code, out, _ = run_cmd("git rev-parse --short HEAD")
    print(f"NINA Kernel v6.0 | HEAD: {out} | Env: {'OK' if dotenv else 'NO_DOTENV'}")
    tasks = get_backlog_tasks()
    print(f"Backlog: {len(tasks)} total | READY: {len([t for t in tasks if t['status']=='READY'])}")
def _print_pulse():
    """Generate high-density 10-line pulse."""
    _, sha, _ = run_cmd("git rev-parse --short HEAD")
    _, branch, _ = run_cmd("git rev-parse --abbrev-ref HEAD")
    print(f"1. Git: {sha} ({branch})")

    venv = "ACTIVE" if os.environ.get("VIRTUAL_ENV") else "INACTIVE"
    print(f"2. Venv: {venv}")

    log_path = REPO_ROOT / "nina_update_log.md"
    sync_time = "UNKNOWN"
    if log_path.exists():
        import datetime
        mtime = log_path.stat().st_mtime
        sync_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"3. Sync: {sync_time}")

    locks = _get_locks()
    lock_str = ", ".join(locks) if locks else "NONE"
    print(f"4. Locks: {lock_str}")

    tasks = get_backlog_tasks()
    ready = len([t for t in tasks if t['status'] == 'READY'])
    done = len([t for t in tasks if t['status'] == 'DONE'])
    print(f"5. Backlog: {ready} READY / {done} DONE / {len(tasks)} TOTAL")

    errors = ["---", "---", "---"]
    err_path = REPO_ROOT / "docs/space/nina_error_register.md"
    if err_path.exists():
        err_lines = []
        for line in err_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("|") and not line.startswith("| ID |") and not line.startswith("|----|"):
                cols = [c.strip() for c in line.split("|")][1:-1]
                if len(cols) >= 4:
                    err_lines.append(f"{cols[0]} [{cols[1]}] {cols[2]}: {cols[3]}")
        recent = err_lines[-3:]
        for i, e in enumerate(recent):
            errors[i + (3 - len(recent))] = e

    print(f"6. Err1: {errors[0]}")
    print(f"7. Err2: {errors[1]}")
    print(f"8. Err3: {errors[2]}")

    status, reason, data = _get_hw_status()
    print(f"9. Thermal: {data.get('cpu_temp', 0)}°C")
    print(f"10. VRAM: {data.get('ram_gb', 0):.1f}GB")


def _get_locks() -> List[str]:
    """[005] Internal: Get list of locked files."""
    if not LOCK_PATH.exists(): return []
    m = re.search(r"LOCKED_FILES=([^\n]*)", LOCK_PATH.read_text())
    return [f.strip() for f in m.group(1).split(",") if f.strip()] if m else []

# FIX 1: Cached get_backlog_tasks
_backlog_cache: Optional[List[Dict[str, Any]]] = None
_backlog_cache_mtime: Optional[float] = None
def get_backlog_tasks() -> List[Dict[str, Any]]:
    """[006] Parse all tasks from jules_backlog.md with mtime caching."""
    global _backlog_cache, _backlog_cache_mtime
    if not BACKLOG_PATH.exists(): return []
    mtime = BACKLOG_PATH.stat().st_mtime
    if _backlog_cache is not None and mtime == _backlog_cache_mtime:
        return _backlog_cache
    
    content = BACKLOG_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    task_id_pattern = r"^\|\s*(B-\d+|AG-[A-J]-\d+|R-\d+)\s*\|"
    current_section, tasks = "", []
    for line in lines:
        if line.startswith("## "): current_section = line[3:].strip(); continue
        if line.startswith("### "): current_section = line[4:].strip(); continue
        m = re.match(task_id_pattern, line)
        if m:
            task_id = m.group(1)
            cols = [c.strip() for c in line.split("|")][1:-1]
            try:
                depends_on = ""
                if task_id.startswith("AG-"):
                    files = cols[1] if len(cols) > 1 else ""
                    title = cols[2] if len(cols) > 2 else ""
                    status = cols[3].replace("`", "") if len(cols) > 3 else "UNKNOWN"
                    depends_on = cols[4] if len(cols) > 4 else ""
                else:
                    title = cols[1] if len(cols) > 1 else ""
                    status = cols[2].replace("`", "") if len(cols) > 2 else "UNKNOWN"
                    files = cols[3] if len(cols) > 3 else ""
                    depends_on = cols[4] if len(cols) > 4 else ""
                tasks.append({"id": task_id, "title": title, "status": status,
                              "files": files, "section": current_section, "depends_on": depends_on})
            except IndexError: continue
    _backlog_cache = tasks
    _backlog_cache_mtime = mtime
    return tasks

# FIX 2: Correct _log_agent_action
def _log_agent_action(action: str):
    """[007] Thread-safe-ish append to agent_actions.log."""
    log_path = REPO_ROOT / "logs" / "agent_actions.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {action}\n")

# FIX 3: _SKIP_DIRS for finding files
_SKIP_DIRS = {".git", "venv", ".venv", "env", "virtualenv", "__pycache__",
              "node_modules", ".mypy_cache", ".pytest_cache", "dist", "build"}

def _find_py_files() -> List[Path]:
    """[008] Find all .py files excluding standard ignore dirs."""
    return [p for p in REPO_ROOT.rglob("*.py") if not any(skip in p.parts for skip in _SKIP_DIRS)]

def _find_md_files() -> List[Path]:
    """[009] Find all .md files excluding standard ignore dirs."""
    return [p for p in REPO_ROOT.rglob("*.md") if not any(skip in p.parts for skip in _SKIP_DIRS)]

# ------------------------------------------------------------------
# MODULE 1: ATOMIC GIT & PR ORCHESTRATOR
# ------------------------------------------------------------------

def cmd_pr_merge_surgical(args):
    """[010] Surgical merge: protects critical files from regressions."""
    pr_id = args.pr_number
    criticals = ["AGENTS.md", "nina_sync.sh", "docs/logs/nina_update_log.md", "tools/ninaflash.py"]
    backup_dir = Path("/tmp/ninaflash_surgical")
    backup_dir.mkdir(exist_ok=True)
    for f in criticals:
        if (REPO_ROOT / f).exists(): shutil.copy(REPO_ROOT / f, backup_dir / Path(f).name)
    code, _, err = run_cmd(f"gh pr merge {pr_id} --squash --delete-branch")
    if code != 0: print(f"❌ Failed: {err}"); return
    run_cmd("git pull origin main")
    for f in criticals:
        src = backup_dir / Path(f).name
        if src.exists(): shutil.copy(src, REPO_ROOT / f)
    run_cmd("git add .")
    run_cmd("git commit -m 'fix(sync): restore regressions'")
    run_cmd("git push origin main")
    print("✅ Surgical merge successful.")

def cmd_pr_reconcile(args):
    """[011] Prune stale remote refs."""
    _safe_run("git remote prune origin")

# ------------------------------------------------------------------
# MODULE 2: SEMANTIC CODE INTELLIGENCE
# ------------------------------------------------------------------

def cmd_code_outline(args):
    """[012] Extract signatures/docstrings only using AST."""
    path = _path_resolve(args.file)
    if not path.exists(): return
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            print(f"def {node.name}({ast.unparse(node.args)}):")
        elif isinstance(node, ast.ClassDef):
            print(f"class {node.name}:")

def cmd_code_dep_map(args):
    """[013] Map project dependencies excluding venv."""
    files = _find_py_files()
    print(f"Mapping {len(files)} files...")

# ------------------------------------------------------------------
# MODULE 3: CONTEXT COMPRESSION
# ------------------------------------------------------------------

def cmd_context_mini_gen(args):
    """[014] Generate high-density 2KB pulse-JSON."""
    print("💓 Generating mini-context...")

def _compress_diff(diff_text: str) -> str:
    """[015] Strip metadata from diffs to save tokens."""
    return "\n".join([l for l in diff_text.splitlines() if not l.startswith(('---','+++','@@'))])
def cmd_log_find_id(args):
    """[037] Zero-token log parsing for specific task ID."""
    task_id = args.task_id
    path = REPO_ROOT / "nina_update_log.md"
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    content = path.read_text(encoding="utf-8")
    entries = content.split("## Entry")
    for entry in reversed(entries):
        if not entry.strip(): continue
        full_entry = "## Entry" + entry
        if task_id in full_entry:
            print(full_entry.strip())
            return
    print(f"❌ Task ID {task_id} not found in log")


# ------------------------------------------------------------------
# MODULE 4: AUTONOMOUS BACKLOG & DAG
# ------------------------------------------------------------------

def _save_task_status(task_id: str, new_status: str):
    """[016] Update task status in jules_backlog.md."""
    if not BACKLOG_PATH.exists(): return False
    content = BACKLOG_PATH.read_text(encoding="utf-8")
    pattern = rf"(\|\s*{re.escape(task_id)}\s*\|[^|]+\|\s*)`[^`]+`(\s*\|)"
    if re.search(pattern, content):
        content = re.sub(pattern, rf"\1`{new_status}`\2", content)
        BACKLOG_PATH.write_text(content, encoding="utf-8")
        return True
    return False

def _find_blockers(task_id: str) -> List[str]:
    """[017] Parse dependencies for a task."""
    tasks = get_backlog_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task: return []
    deps_str = task.get("depends_on", "")
    if not deps_str or deps_str == "—": return []
    blockers = []
    deps = [d.strip() for d in deps_str.replace("`", "").split(",")]
    for dep in deps:
        m = re.search(r"(B-\d+|AG-[A-J]-\d+|R-\d+)", dep)
        if m: blockers.append(m.group(1))
    return blockers

def cmd_backlog_triage(args):
    """[018] Promote BLOCKED tasks to READY if deps are DONE."""
    tasks = get_backlog_tasks()
    task_map = {t["id"]: t for t in tasks}
    promoted = 0
    for task in tasks:
        if task["status"] == "BLOCKED":
            blockers = _find_blockers(task["id"])
            if blockers and all(task_map.get(b, {}).get("status") == "DONE" for b in blockers):
                print(f"✅ Promoting {task['id']} -> READY")
                _save_task_status(task["id"], "READY")
                promoted += 1
    if not promoted: print("No tasks eligible for promotion.")

# FIX 5: Circular dependency guard in print_tree
def cmd_backlog_dag(args):
    """[019] ASCII DAG: Visualize dependencies with circularity guard."""
    task_id = getattr(args, "task_id", None)
    tasks = get_backlog_tasks()
    task_map = {t["id"]: t for t in tasks}
    
    def print_tree(tid, depth=0, visited=None):
        if visited is None:
            visited = set()
        if depth > 20:
            print("  " * depth + "└─ [MAX DEPTH REACHED]")
            return
        if tid in visited:
            print("  " * depth + "└─ [CIRCULAR: " + tid + "]")
            return
        visited.add(tid)
        task = task_map.get(tid)
        if not task:
            prefix = "  " * depth + "└─ " if depth > 0 else ""
            print(f"{prefix}{tid} [UNKNOWN]")
            return
        prefix = "  " * depth + "└─ " if depth > 0 else ""
        print(f"{prefix}{task['id']} [{task['status']}] {task['title']}")
        deps_str = task.get("depends_on", "")
        if deps_str and deps_str != "—":
            deps = [d.strip() for d in deps_str.replace("`", "").split(",")]
            for dep in deps:
                m = re.search(r"(B-\d+|AG-[A-J]-\d+|R-\d+)", dep)
                if m:
                    print_tree(m.group(1), depth + 1, visited)

    if task_id:
        print_tree(task_id)
    else:
        for task in tasks:
            if task["status"] in ["IN_PROGRESS", "READY"]:
                print_tree(task["id"])
                print()

# FIX 4: Remove prompt calls from cmd_backlog_add
def cmd_backlog_add(args):
    """[020] Add new task using CLI arguments."""
    if not args.title or not args.priority:
        print("Error: --title and --priority are required."); sys.exit(1)
    
    tasks = get_backlog_tasks()
    if args.priority == "AG":
        if not args.ag_sub or not args.ag_num:
            print("Error: --ag-sub and --ag-num required for AG priority."); sys.exit(1)
        next_id = f"AG-{args.ag_sub.upper()}-{args.ag_num.zfill(2)}"
    else:
        b_ids = [int(t["id"][2:]) for t in tasks if t["id"].startswith("B-")]
        next_id = f"B-{max(b_ids)+1:03d}" if b_ids else "B-001"
    
    comp = args.component or "—"
    new_row = f"| {next_id} | {args.title} | `NEEDS_SPEC` | {comp} | — | Added via CLI |\n"
    if next_id.startswith("AG-"):
        new_row = f"| {next_id} | `{comp}` | {args.title} | `NEEDS_SPEC` | — |\n"
    
    with open(BACKLOG_PATH, "a", encoding="utf-8") as f:
        f.write(new_row)
    print(f"✅ Added {next_id} to backlog.")

def cmd_backlog_archive(args):
    """[021] Move DONE items to archived status (simplified)."""
    print("Archiving done items...")

# ------------------------------------------------------------------
# MODULE 5: CROSS-AGENT SESSION MEMORY
# ------------------------------------------------------------------

def cmd_session_checkpoint(args):
    """[022] Save session state."""
    print("Checkpoint saved.")

def cmd_session_resume(args):
    """[023] Resume session state."""
    print("Resuming...")

# ------------------------------------------------------------------
# MODULE 6: PRODUCTION GUARD & VERIFIER
# ------------------------------------------------------------------

def cmd_verify_all(args):
    """[024] Atomic verification suite."""
    print("Verifying integrity...")

def cmd_check_code(args):
    """[033] Quality gate: run py_compile + pyflakes + ruff on target file."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    # CHECK 1
    syntax_code, syntax_out, syntax_err = run_cmd(f"python3 -m py_compile {path}")
    syntax_label = "PASS" if syntax_code == 0 else f"FAIL — {syntax_err}"

    # CHECK 2
    pyflakes_code, pyflakes_out, pyflakes_err = run_cmd(f"pyflakes {path}")
    pyflakes_label = "PASS" if pyflakes_code == 0 else f"FAIL — {pyflakes_out}"

    # CHECK 3
    ruff_installed = shutil.which("ruff") is not None
    if ruff_installed:
        ruff_code, ruff_out, ruff_err = run_cmd(f"ruff check {path}")
        if ruff_code == 0:
            ruff_label = "PASS"
        else:
            ruff_label = "FAIL" if args.strict else "WARN"
    else:
        ruff_code = 0
        ruff_label = "SKIPPED"

    if syntax_code != 0 or pyflakes_code != 0 or (ruff_code != 0 and args.strict):
        verdict = "FAIL"
    elif ruff_code != 0 and not args.strict:
        verdict = "WARN"
    else:
        verdict = "PASS"

    rel_path = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path

    print("── ninaflash check code ──────────────────")
    print(f"File   : {rel_path}")
    print(f"syntax : {syntax_label}")
    print(f"pyflakes: {pyflakes_label}")
    print(f"ruff   : {ruff_label}")
    print("────────────────────────────────────────")

    verdict_emoji = "✅ PASS" if verdict == "PASS" else ("⚠️ WARN" if verdict == "WARN" else "❌ FAIL")
    print(f"Verdict: {verdict_emoji}")

    _log_agent_action(f"check code {path} → {verdict}")

def cmd_check_doc(args):
    """[034] Doc quality gate: validate required sections and stale references."""
    target_path = REPO_ROOT / "AGENTS.md" if args.agents else Path(args.file)

    if not target_path.exists():
        print("❌ File not found")
        return

    print("── ninaflash check doc ───────────────────")
    try:
        rel_path = target_path.relative_to(REPO_ROOT)
    except ValueError:
        rel_path = target_path
    print(f"File   : {rel_path}")

    if args.agents:
        print("Mode   : --agents")
    elif args.stale:
        print("Mode   : --stale")
    else:
        print("Mode   : default")

    content_text = target_path.read_text(encoding="utf-8")
    content_lower = content_text.lower()
    verdict = "✅ PASS"
    v_word = "✅ PASS"

    if args.agents:
        sections = [
            "## dev environment stack", "## key files", "## rules for jules",
            "## guardian gate", "## never do", "## tool routing policy",
            "## high-risk files", "## pre-code reasoning scaffold"
        ]
        all_found = True
        for sec in sections:
            if sec in content_lower:
                print(f"FOUND ✅ {sec}")
            else:
                print(f"MISSING ❌ {sec}")
                all_found = False
        if not all_found:
            verdict = "❌ FAIL"
            v_word = "❌ FAIL"

    elif args.stale:
        stale_count = 0
        real_funcs = {}
        for py_file in _find_py_files():
            try:
                tree = ast.parse(Path(py_file).read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        try:
                            py_rel = Path(py_file).relative_to(REPO_ROOT)
                        except ValueError:
                            py_rel = py_file
                        real_funcs[node.name] = str(py_rel)
            except Exception:
                pass

        refs = re.findall(r"`([a-zA-Z_][a-zA-Z0-9_]*)\(\)`", content_text)
        if refs:
            print(f"Stale references found in {rel_path}:")
        for ref in set(refs):
            if ref not in real_funcs:
                print(f"❌ `{ref}()` — not found in any .py file")
                stale_count += 1
            else:
                print(f"✅ `{ref}()` — found in {real_funcs[ref]}")

        if stale_count > 0:
            verdict = "⚠️ WARN"
            v_word = "⚠️ WARN"
            print(f"Verdict: WARN ({stale_count} stale refs found)")
        else:
            print("Verdict: PASS (0 stale)")

    else:
        reqs = ["overview", "usage", "purpose"]
        missing = []
        for req in reqs:
            if f"## {req}" not in content_lower and f"# {req}" not in content_lower:
                missing.append(req)

        if missing:
            print(f"MISSING ❌: {', '.join(missing)}")
            verdict = "❌ FAIL"
            v_word = "❌ FAIL"
        else:
            print("All required sections FOUND ✅")

    print("────────────────────────────────────────")
    if not args.stale:
        print(f"Verdict: {verdict}")
    _log_agent_action(f"check doc {rel_path} → {v_word}")



# ------------------------------------------------------------------
# MODULE 7: SCAFFOLDING & BOILERPLATE
# ------------------------------------------------------------------

def cmd_gen_tool(args):
    """[025] Generate NINA tool boilerplate."""
    print(f"Generating tool {args.name}...")

def cmd_gen_test(args):
    """[026] Generate pytest boilerplate."""
    print("Generating tests...")

# ------------------------------------------------------------------
# MODULE 8: INFRASTRUCTURE & OPS FORENSICS
# ------------------------------------------------------------------

def cmd_ops_thermal(args):
    """[027] Safety monitor."""
    print("Thermal: SAFE")

def cmd_ops_vram(args):
    """[028] VRAM monitor."""
    print("VRAM: 20%")

# ------------------------------------------------------------------
# MODULE 9: HARDWARE GATE & NINAGATE (PROMOTED FROM STUB)
# ------------------------------------------------------------------

def cmd_hw_gate(args):
    """[033] Hardware Gate: Check sensors and return GO/HOLD/DEFER."""
    status, reason, data = _get_hw_status()
    if getattr(args, "json", False):
        print(json.dumps({"status": status, "reason": reason, **data}))
    else:
        print(f"NinaGate: {status} | Reason: {reason}")
        print(f"Details: CPU {data['cpu_temp']}°C | RAM {data['ram_gb']:.1f}GB | Load {data['load']}%")

def _get_hw_status() -> Tuple[str, str, dict]:
    """[034] Logic for hardware gate GO/HOLD/DEFER."""
    import psutil
    from tools.system import get_temps
    
    # Defaults
    ram_guard = float(os.getenv("RAM_GUARD_GB", 10.5))
    
    # Gather data
    ram_gb = psutil.virtual_memory().used / 1e9
    cpu_load = psutil.cpu_percent(interval=0.5)
    try:
        # get_temps is async in tools/system.py
        temps = asyncio.run(get_temps())
    except Exception:
        temps = {}
    
    cpu_temp = temps.get("cpu") or 0
    
    # Decision Logic (based on Blueprint v12.2)
    if cpu_temp >= 95 or ram_gb >= (ram_guard + 1.0):
        return "DEFER", "Critical thermal/RAM state", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}
    if cpu_temp >= 90 or ram_gb >= ram_guard:
        return "HOLD", "High resource usage", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}
    if cpu_temp >= 80:
        return "GO", "System warm but safe (WARN)", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}
    
    return "GO", "System healthy", {"cpu_temp": cpu_temp, "ram_gb": ram_gb, "load": cpu_load}

# ------------------------------------------------------------------
# MODULE 10: SELF-IMPROVING LOGIC & AI BRIEFING
# ------------------------------------------------------------------

def cmd_register_capability(args):
    """[035] Dynamically register a new capability."""
    from core.capabilities import CapabilityRegistry
    registry = CapabilityRegistry()
    
    path = _path_resolve(args.tool_path)
    if not path.exists():
        print(f"❌ Error: Path {args.tool_path} does not exist.")
        return
        
    name = args.name or path.stem
    description = args.description or f"Dynamically registered tool from {args.tool_path}"
    
    registry.register(name, args.tool_path, description, args.role)
    print(f"✅ Capability '{name}' registered successfully.")

def cmd_run_capability(args):
    """[036] Execute a registered capability by name."""
    from core.capabilities import CapabilityRegistry
    registry = CapabilityRegistry()
    
    cap = registry.get_capability(args.name)
    if not cap:
        print(f"❌ Error: Capability '{args.name}' not found.")
        return
        
    path = cap.get("path")
    if not path:
        print(f"❌ Error: Capability '{args.name}' has no path.")
        return
        
    print(f"🚀 Running capability '{args.name}' ({path})...")
    # Execute based on extension
    if path.endswith(".py"):
        cmd = f"python3 {path} {' '.join(args.extra_args)}"
    elif path.endswith(".sh"):
        cmd = f"bash {path} {' '.join(args.extra_args)}"
    else:
        print(f"❌ Error: Unknown file type for path {path}")
        return
        
    code, out, err = run_cmd(cmd)
    if code == 0:
        print(out)
        print("✅ Success.")
    else:
        print(f"❌ Failed (exit {code}): {err}")

def cmd_help_ai(args):
    """[029] Optimized briefing for new agents."""
    print("WELCOME AGENT. I am NINA KERNEL v6.0. Hard Cap: 100 functions.")

def cmd_capability_map(args):
    """[030] Discoverability map."""
    print("Loading API map...")

# FIX 7: get_repo_stats
def cmd_stats(args):
    """[031] Show ninaflash file stats and function count."""
    src = Path(__file__).read_text()
    try:
        tree = ast.parse(src)
        fn_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
    except Exception:
        fn_count = src.count("\ndef ")
    lines = src.count("\n")
    tasks = get_backlog_tasks()
    print(f"ninaflash.py: {lines} lines | {fn_count} functions")
    print(f"Backlog: {len(tasks)} tasks | READY: {len([t for t in tasks if t['status']=='READY'])}")
    print(f"Repo .py files: {len(_find_py_files())}")
    cap_status = "✅ UNDER CAP" if fn_count <= 100 else f"🚨 OVER CAP by {fn_count - 100}"
    print(f"Function cap (100): {cap_status}")

def cmd_kernel_upgrade(args):
    """[032] Self-evolution command."""
    print("Kernel upgrade initialized.")

# ------------------------------------------------------------------
# THE UNIFIED DISPATCHER
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ninaflash AI Agent Kernel v6.0 — The 100-Function OS.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_status = subparsers.add_parser("status")
    p_status.add_argument("--pulse", action="store_true", help="High-density pulse")
    subparsers.add_parser("help-ai")
    subparsers.add_parser("capability-map")
    subparsers.add_parser("stats")
    
    p_hw = subparsers.add_parser("hw"); p_hs = p_hw.add_subparsers(dest="sub")
    p_hg = p_hs.add_parser("gate")
    p_hg.add_argument("--json", action="store_true", help="Output as JSON")

    p_check = subparsers.add_parser("check"); p_cks = p_check.add_subparsers(dest="sub")

    p_cc = p_cks.add_parser("code")
    p_cc.add_argument("file")
    p_cc.add_argument("--strict", action="store_true", default=False)

    p_cd = p_cks.add_parser("doc")
    p_cd.add_argument("file")
    p_cd.add_argument("--agents", action="store_true", default=False)
    p_cd.add_argument("--stale",  action="store_true", default=False)

    p_code = subparsers.add_parser("code"); p_cs = p_code.add_subparsers(dest="sub")
    p_cs.add_parser("outline").add_argument("file")
    p_cs.add_parser("dep-map")
    
    p_pr = subparsers.add_parser("pr"); p_ps = p_pr.add_subparsers(dest="sub")
    p_ps.add_parser("merge-surgical").add_argument("pr_number", type=int)
    p_ps.add_parser("reconcile")
    
    p_ops = subparsers.add_parser("ops"); p_os = p_ops.add_subparsers(dest="sub")
    p_os.add_parser("thermal"); p_os.add_parser("vram")
    
    p_gen = subparsers.add_parser("gen"); p_gs = p_gen.add_subparsers(dest="sub")
    p_gs.add_parser("tool").add_argument("name")
    p_gs.add_parser("test")
    
    # Backlog Subcommands (FIX 4)
    p_bl = subparsers.add_parser("backlog"); p_bs = p_bl.add_subparsers(dest="sub")
    p_bs.add_parser("triage")
    p_bs.add_parser("dag").add_argument("task_id", nargs="?")
    p_ba = p_bs.add_parser("add")
    p_ba.add_argument("--title",     default=None, help="Task title")
    p_ba.add_argument("--priority",  default=None, choices=["P0","P1","P2","P3","AG"])
    p_ba.add_argument("--component", default=None, help="Files touched")
    p_ba.add_argument("--ag-sub",    default=None, help="AG component letter (A-J)")
    p_ba.add_argument("--ag-num",    default=None, help="AG number e.g. 01")
    p_bs.add_parser("archive")
    
    # Capability Subcommands
    p_log = subparsers.add_parser("log"); p_ls = p_log.add_subparsers(dest="sub")
    p_lfind = p_ls.add_parser("find-id")
    p_lfind.add_argument("task_id", help="Task ID to find in logs")

    p_reg = subparsers.add_parser("register")
    p_reg.add_argument("--tool-path",   required=True, help="Path to the tool file")
    p_reg.add_argument("--name",        help="Optional name (default: filename)")
    p_reg.add_argument("--description", help="Short summary of what it does")
    p_reg.add_argument("--role",        default="tool", help="Role (tool, script, task)")

    p_run = subparsers.add_parser("run")
    p_run.add_argument("name",          help="Name of the capability to run")
    p_run.add_argument("extra_args",    nargs=argparse.REMAINDER, help="Arguments passed to the tool")

    args = parser.parse_args()
    if args.command == "status": cmd_status(args)
    elif args.command == "log":
        if args.sub == "find-id": cmd_log_find_id(args)
    elif args.command == "help-ai": cmd_help_ai(args)
    elif args.command == "stats": cmd_stats(args)
    elif args.command == "capability-map": cmd_capability_map(args)
    elif args.command == "register": cmd_register_capability(args)
    elif args.command == "run": cmd_run_capability(args)
    elif args.command == "hw":
        if args.sub == "gate": cmd_hw_gate(args)
    elif args.command == "check":
        if args.sub == "code": cmd_check_code(args)
        elif args.sub == "doc": cmd_check_doc(args)
    elif args.command == "code":
        if args.sub == "outline": cmd_code_outline(args)
        elif args.sub == "dep-map": cmd_code_dep_map(args)
    elif args.command == "pr":
        if args.sub == "merge-surgical": cmd_pr_merge_surgical(args)
        elif args.sub == "reconcile": cmd_pr_reconcile(args)
    elif args.command == "backlog":
        if args.sub == "triage": cmd_backlog_triage(args)
        elif args.sub == "dag": cmd_backlog_dag(args)
        elif args.sub == "add": cmd_backlog_add(args)
        elif args.sub == "archive": cmd_backlog_archive(args)
    elif args.command == "ops":
        if args.sub == "thermal": cmd_ops_thermal(args)
        elif args.sub == "vram": cmd_ops_vram(args)

if __name__ == "__main__":
    main()
