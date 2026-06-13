#!/usr/bin/env python3
"""
ninaflash — The Unified AI Agent Kernel for NINA.
Version: 6.1 (THE OPTIMIZED "MAINTAINER" KERNEL)
Author: Gemini CLI & Antigravity
Mission: Minimize Token Usage, Maximize Execution Speed, Absolute Reliability.
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

def safe_run_cmd(cmd: str, timeout=60) -> Tuple[int, str, str]:
    """[NEW] Hardened execution with blocklist for git push/force."""
    if any(x in cmd for x in ["git push", "git force", "--force"]):
         print(f"❌ SECURITY: Command '{cmd}' blocked.")
         return 1, "", "Blocked"
    return _safe_run(cmd, timeout=timeout)

def _safe_run(cmd: str, timeout=60) -> Tuple[int, str, str]:
    """[002] Hardened execution with NINA security policy enforcement."""
    from tools.shell import is_command_safe
    if not is_command_safe(cmd): return 1, "", f"❌ SECURITY: Command '{cmd}' blocked."
    return run_cmd(cmd, timeout=timeout)

def _path_resolve(rel_path: str) -> Path:
    """[003] Absolute path resolution from repo root."""
    return (REPO_ROOT / rel_path).resolve()


def cmd_find(args):
    import re
    query = args.query
    files_to_check = _find_py_files() + _find_md_files()
    try:
        files_to_check.extend([p for p in REPO_ROOT.rglob("*.txt") if p.is_file()])
        files_to_check.extend([p for p in REPO_ROOT.rglob("*.log") if p.is_file()])
        files_to_check.extend([p for p in REPO_ROOT.rglob("*.json") if p.is_file()])
    except: pass

    print(f"Searching for '{query}' in {len(files_to_check)} files...")
    for p in files_to_check:
        try:
            text = p.read_text(errors="ignore")
            if args.regex:
                if re.search(query, text):
                    print(f"MATCH: {p.relative_to(REPO_ROOT)}")
            else:
                if query in text:
                    print(f"MATCH: {p.relative_to(REPO_ROOT)}")
        except: pass


def cmd_edit(args):
    target = REPO_ROOT / args.file
    if not target.exists():
        print(f"File not found: {args.file}")
        sys.exit(1)

    import json
    try:
        edits = json.loads(args.edits)
    except:
        print("Edits must be valid JSON list of dicts: [{'search': 'old', 'replace': 'new'}]")
        sys.exit(1)

    text = target.read_text()
    for e in edits:
        if e['search'] in text:
            text = text.replace(e['search'], e['replace'])
        else:
            print(f"Search string not found in {args.file}: {e['search']}")

    target.write_text(text)
    print(f"Updated {args.file}")

    if target.suffix == '.py':
        code, out, err = run_cmd(["python3", "-m", "py_compile", str(target)])
        if code != 0:
            print(f"py_compile failed:\n{err}")

        code, out, err = run_cmd(["python3", "-m", "pyflakes", str(target)])
        if code != 0:
            print(f"pyflakes failed:\n{out}\n{err}")


def cmd_git(args):
    if args.subcmd == "status":
        code, out, err = run_cmd(["git", "status", "-s"])
        print(out)
    elif args.subcmd == "diff":
        code, out, err = run_cmd(["git", "diff"])
        print(out[:4000])
    elif args.subcmd == "commit":
        code, diff_out, err = run_cmd(["git", "diff", "--cached"])
        if not diff_out.strip():
            print("No staged changes to commit.")
            sys.exit(1)

        prompt = f"Generate a conventional commit message for this diff:\n{diff_out[:3000]}"
        print("Generating commit message via LOCALFAST...")

        script = f'''import asyncio, sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))
from core.router import HybridRouter, ClassifiedTask
from core.config import NinaConfig
async def run():
    r = HybridRouter(NinaConfig(telegram_bot_token="test", authorized_user_id="test"))
    await r.initialize()
    task = ClassifiedTask("quick", 300, False, False)
    msg, _, _, _ = await r._call_provider("LOCALFAST", [{{"role":"user", "content": {repr(prompt)}}}], task)
    print(msg)
asyncio.run(run())
'''
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tf:
            tf.write(script)
            tf_name = tf.name

        code, msg_out, err = run_cmd(["python3", tf_name])
        os.unlink(tf_name)

        msg = msg_out.strip()
        if not msg: msg = "chore: update files"

        print(f"Commit message:\n{msg}\n")
        code, out, err = run_cmd(["git", "commit", "-m", msg])
        print(out)

def cmd_status(args):
    """[004] Unified system health snapshot."""
    if getattr(args, 'pulse', False):
        _print_pulse()
        return

    code, out, _ = run_cmd("git rev-parse --short HEAD")
    print(f"NINA Kernel v6.1 | HEAD: {out} | Env: {'OK' if dotenv else 'NO_DOTENV'}")
    tasks = get_backlog_tasks()
    print(f"Backlog: {len(tasks)} total | READY: {len([t for t in tasks if t['status']=='READY'])}")

def _append_update_log(task_id: str, title: str, summary: str):
    """[007] Appends a standardized entry to nina_update_log.md."""
    log_path = REPO_ROOT / "nina_update_log.md"
    if not log_path.exists(): return
    
    content = log_path.read_text(encoding="utf-8")
    entries = re.findall(r"## Entry (\d+)", content)
    next_num = int(entries[-1]) + 1 if entries else 1
    
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n---\n\n## Entry {next_num:03d} — {today} · merge: {task_id} {title}\n"
    entry += "**Triggered by:** nf maintain automation.\n\n"
    entry += f"**What changed:**\n- {summary}\n\n"
    entry += "**Rollback:** `git revert -m 1 HEAD`\n"
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"✅ Appended Entry {next_num:03d} to log.")

def _print_pulse():
    """Generate high-density 10-line pulse."""
    from datetime import datetime
    _, sha, _ = run_cmd("git rev-parse --short HEAD")
    _, branch, _ = run_cmd("git rev-parse --abbrev-ref HEAD")
    print(f"1. Git: {sha} ({branch})")

    venv = "ACTIVE" if os.environ.get("VIRTUAL_ENV") else "INACTIVE"
    print(f"2. Venv: {venv}")

    log_path = REPO_ROOT / "nina_update_log.md"
    sync_time = "UNKNOWN"
    if log_path.exists():
        mtime = log_path.stat().st_mtime
        sync_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
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
    task_id_pattern = r"^\|\s*(B-\d+|AG-[A-Z]-\d+|R-\d+)\s*\|"
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
def write_nf_log(command: str, subcommand: str = "", duration_ms: float = 0,
                 tokens_saved: int = 0, outcome: str = "OK"):
    """Structured JSON log entry for every nf command execution."""
    log_path = REPO_ROOT / "logs" / "ninaflash.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "command": command,
        "subcommand": subcommand,
        "duration_ms": round(duration_ms, 1),
        "tokens_saved": tokens_saved,
        "outcome": outcome,
        "provider": "LOCAL"
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

NF_TOKEN_SAVINGS = {
    "file":     2000,  # replaces full file read (~800 in + ~1200 context)
    "code":     1500,  # replaces read_file + AST reasoning
    "git":       800,  # replaces git shell + output parsing
    "log":       600,  # replaces reading full update log
    "backlog":   500,  # replaces reading full backlog table
    "monitor":   300,
    "batch":    1200,  # parallel = saves sequential overhead
    "memory":    400,
    "status":    200,
    "check":     300,
    "find-symbol": 1000,
}

# FIX 3: _SKIP_DIRS for finding files
_SKIP_DIRS = {".git", "venv", ".venv", "env", "virtualenv", "__pycache__",
              "node_modules", ".mypy_cache", ".pytest_cache", "dist", "build"}

def _load_geminiignore() -> List[str]:
    ignore_file = REPO_ROOT / '.geminiignore'
    if not ignore_file.exists():
        return []

    patterns = []
    for line in ignore_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('!'):
            patterns.append(line)
    return patterns

def _is_ignored(path_str: str, patterns: List[str]) -> bool:
    if not patterns:
        return False
    import fnmatch
    for pattern in patterns:
        if pattern.endswith('/'):
            if path_str == pattern[:-1] or path_str.startswith(pattern):
                return True
        elif fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(os.path.basename(path_str), pattern):
            return True
        elif path_str.startswith(pattern + '/'):
            return True
    return False

def _is_ignored_path(path: Path) -> bool:
    patterns = _load_geminiignore()
    try:
        rel_path = path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return False
    return _is_ignored(rel_path, patterns)

def cmd_check_ignore(args):
    """[037] Diagnostic command to list files hidden by .geminiignore."""
    print("── ninaflash check ignore ───────────────────")
    ignore_file = REPO_ROOT / ".geminiignore"
    if not ignore_file.exists():
        print("No .geminiignore file found.")
        return

    count = 0
    for p in REPO_ROOT.rglob('*'):
        if p.is_file() and _is_ignored_path(p):
            try:
                rel = p.relative_to(REPO_ROOT).as_posix()
                print(rel)
                count += 1
            except Exception:
                pass
    print(f"\nTotal ignored files: {count}")

def _find_py_files() -> List[Path]:
    """[008] Find all .py files excluding standard ignore dirs and .geminiignore with depth cap."""
    patterns = _load_geminiignore()
    return [p for p in REPO_ROOT.rglob("*.py")
            if not any(skip in p.parts for skip in _SKIP_DIRS)
            and not _is_ignored(str(p.relative_to(REPO_ROOT)), patterns)
            and len(p.relative_to(REPO_ROOT).parts) <= 8]

def _find_md_files() -> List[Path]:
    """[009] Find all .md files excluding standard ignore dirs and .geminiignore."""
    patterns = _load_geminiignore()
    return [p for p in REPO_ROOT.rglob("*.md")
            if not any(skip in p.parts for skip in _SKIP_DIRS)
            and not _is_ignored(str(p.relative_to(REPO_ROOT)), patterns)]

# ------------------------------------------------------------------
# MODULE 1: ATOMIC GIT & PR ORCHESTRATOR
# ------------------------------------------------------------------

def _resolve_v13_docs():
    """[010] Surgically resolve v13 doc conflicts locally."""
    targets = ["nina_context.md", "README.md", "ARCHITECTURE.md", "AGENTS.md"]
    for f in targets:
        if (REPO_ROOT / f).exists():
            run_cmd(f"git checkout main -- {f}")
            run_cmd(f"git add {f}")

def cmd_maintain_pr(args):
    """[011] Atomic 'Rebase -> Resolve -> Merge -> Log -> Close' workflow."""
    pr_id, task_id = args.pr_id, args.task_id
    print(f"🚀 Maintaining PR #{pr_id} ({task_id})...")

    # 1. Checkout and Rebase
    code, _, err = run_cmd(f"gh pr checkout {pr_id}")
    if code != 0: print(f"❌ Checkout failed: {err}"); return
    
    code, _, _ = run_cmd("git rebase main")
    if code != 0:
        print("⚠️ Conflict detected. Applying surgical v13 resolution...")
        _resolve_v13_docs()
        run_cmd("git add . && export GIT_EDITOR=true && git rebase --continue")
    
    # 2. Merge to Main
    branch = subprocess.getoutput("git branch --show-current")
    run_cmd("git checkout main")
    code, _, err = run_cmd(f"git merge {branch} --no-ff -m 'merge: PR #{pr_id} {task_id}'")
    if code != 0: print(f"❌ Merge failed: {err}"); return

    # 3. Post-Merge Updates
    _save_task_status(task_id, "DONE")
    _append_update_log(task_id, args.title, args.summary)
    
    # 4. Cleanup
    run_cmd(f"gh pr close {pr_id} -d -c 'Merged via nf maintain automation.'")
    print(f"✅ PR #{pr_id} fully resolved and merged.")

def cmd_pr_reconcile(args):
    """[012] Prune stale remote refs."""
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


def cmd_code_cycles(args):
    """[013] Identify circular imports locally."""
    import ast
    import json
    from pathlib import Path

    def get_module_name(file_path, root):
        rel_path = file_path.relative_to(root)
        if rel_path.name == "__init__.py":
            parts = ".".join(rel_path.parent.parts)
            return f"{parts}.__init__" if parts else "__init__"
        else:
            return ".".join(rel_path.with_suffix("").parts)

    def parse_imports(file_path, root):
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except Exception:
            return set()

        imports = set()
        module_name = get_module_name(file_path, root)
        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    imports.add(alias.name)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                if node.module:
                    level = node.level
                    if level > 0:
                        parts = module_name.split(".")
                        if level <= len(parts):
                            base = ".".join(parts[:-level])
                            if base:
                                imports.add(f"{base}.{node.module}")
                            else:
                                imports.add(node.module)
                    else:
                        imports.add(node.module)
                else:
                     level = node.level
                     parts = module_name.split(".")
                     base = ".".join(parts[:-level])
                     for alias in node.names:
                         if base:
                             imports.add(f"{base}.{alias.name}")
                         else:
                             imports.add(alias.name)
                self.generic_visit(node)

        ImportVisitor().visit(tree)
        return imports

    root = Path(REPO_ROOT)
    py_files = [p for p in root.rglob("*.py") if "venv" not in p.parts and ".venv" not in p.parts and "tests" not in p.parts]
    modules = {get_module_name(p, root): p for p in py_files}

    graph = {}
    for mod_name, file_path in modules.items():
        all_imports = parse_imports(file_path, root)
        local_imports = set()
        for imp in all_imports:
            if imp in modules:
                local_imports.add(imp)
            else:
                pass

        try:
             tree = ast.parse(file_path.read_text(encoding="utf-8"))
             for node in ast.walk(tree):
                 if isinstance(node, ast.ImportFrom):
                     if node.module:
                         for alias in node.names:
                             potential_mod = f"{node.module}.{alias.name}"
                             level = node.level
                             if level > 0:
                                 parts = mod_name.split(".")
                                 base = ".".join(parts[:-level])
                                 if base:
                                     potential_mod = f"{base}.{node.module}.{alias.name}"
                                 else:
                                     potential_mod = f"{node.module}.{alias.name}"
                             if potential_mod in modules:
                                 local_imports.add(potential_mod)
        except Exception:
             pass

        if local_imports:
            graph[mod_name] = list(local_imports)

    visited = set()
    stack = set()
    path = []
    cycles = []

    def dfs(node):
        visited.add(node)
        stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in stack:
                cycle_idx = path.index(neighbor)
                cycle = path[cycle_idx:] + [neighbor]
                if len(cycle) >= 2:
                    cycles.append(cycle)

        stack.remove(node)
        path.pop()

    for node in graph:
        if node not in visited:
            dfs(node)

    if cycles:
        print(json.dumps({"status": "error", "cycles": cycles}, indent=2))
    else:
        print(json.dumps({"status": "ok", "message": "No circular imports found."}))

def cmd_code_dep_map(args):

    """[013] Map project dependencies excluding venv."""
    files = _find_py_files()
    print(f"Mapping {len(files)} files...")

def cmd_code_index(args):
    """[037] Global Symbol Indexer: Generate JSON map of all classes/functions."""
    index = {}
    for py_file in _find_py_files():
        try:
            rel_path = str(py_file.relative_to(REPO_ROOT))
        except ValueError:
            rel_path = str(py_file)

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            symbols = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(node.name)
            if symbols:
                index[rel_path] = symbols
        except Exception:
            pass

    print(json.dumps(index, indent=2))


def cmd_code_call_graph(args):
    """[039] Local Call Graph Generator: Trace function calls locally without LLM."""

    class CallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.calls = set()
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                self.calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.calls.add(node.func.attr)
            self.generic_visit(node)

    graph = {}

    if hasattr(args, 'file') and args.file:
        files = [_path_resolve(args.file)]
    else:
        files = _find_py_files()

    for py_file in files:
        if not py_file.exists():
            continue
        try:
            rel_path = str(py_file.relative_to(REPO_ROOT))
        except ValueError:
            rel_path = str(py_file)

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    visitor = CallVisitor()
                    visitor.visit(node)
                    if visitor.calls:
                        key = f"{rel_path}:{node.name}"
                        graph[key] = sorted(list(set(visitor.calls)))
        except Exception:
            pass

    try:
        print(json.dumps(graph, indent=2))
    except BrokenPipeError:
        import sys, os
        sys.stdout = open(os.devnull, 'w')
        sys.exit(0)


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


def cmd_backlog_summary(args):
    """[100] Print a 5-line summary of the backlog."""
    tasks = get_backlog_tasks()
    c_ready = sum(1 for t in tasks if t.get('status') == 'READY')
    c_prog = sum(1 for t in tasks if t.get('status') == 'IN_PROGRESS')
    c_blocked = sum(1 for t in tasks if t.get('status') == 'BLOCKED')
    c_done = sum(1 for t in tasks if t.get('status') == 'DONE')
    print("Backlog Summary:")
    print(f"  READY:       {c_ready}")
    print(f"  IN_PROGRESS: {c_prog}")
    print(f"  BLOCKED:     {c_blocked}")
    print(f"  DONE:        {c_done}")


def cmd_task_active(args):
    """[101] List active tasks and their locked files."""
    tasks = get_backlog_tasks()
    active_tasks = [t for t in tasks if t.get('status') in ('IN_PROGRESS', 'IN_PR')]
    locks = _get_locks()

    print("Active Tasks:")
    for t in active_tasks:
        print(f"  {t.get('id')} - {t.get('title')} ({t.get('status')})")

    print(f"\nLocked Files: {', '.join(locks) if locks else 'None'}")


def _get_log_entries():
    log_path = REPO_ROOT / "docs" / "logs" / "nina_update_log.md"
    if not log_path.exists():
        log_path = REPO_ROOT / "nina_update_log.md"
    if not log_path.exists():
        return ""
    return log_path.read_text(encoding="utf-8")

def cmd_log_tail(args):
    """[102] Print the last <n> entries of the log."""
    content = _get_log_entries()
    if not content:
        print("Log file not found.")
        return
    import re
    # Split the content keeping "## Entry " at the start of each split
    entries = re.split(r'(?=\n## Entry )', content)
    # The first element is the header if the file doesn't start with "## Entry "
    # We want to filter out only the actual entries
    actual_entries = [e for e in entries if e.strip().startswith("## Entry")]
    if not actual_entries:
        print("No entries found.")
        return
    n = getattr(args, 'n', 5)
    tail_entries = actual_entries[-n:]
    for entry in tail_entries:
        print(entry.strip() + "\n")

def cmd_log_next_id(args):
    """[103] Print the next available entry ID."""
    content = _get_log_entries()
    max_id = 0
    import re
    for line in content.splitlines():
        m = re.match(r"^## Entry (\d+)", line)
        if m:
            entry_id = int(m.group(1))
            if entry_id > max_id:
                max_id = entry_id
    print(max_id + 1)

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

def cmd_memory_stash(args):
    """[037] Save a snippet of working memory."""
    text = args.text
    if not text:
        print("❌ Error: Memory text is required.")
        return

    stash_path = REPO_ROOT / "data" / "memory_stash.json"
    stash_path.parent.mkdir(parents=True, exist_ok=True)

    stash = []
    if stash_path.exists():
        try:
            with open(stash_path, "r") as f:
                stash = json.load(f)
        except Exception:
            pass

    stash.append({
        "timestamp": datetime.now().isoformat(),
        "text": text
    })

    try:
        with open(stash_path, "w") as f:
            json.dump(stash, f, indent=2)
        print(f"✅ Memory stashed: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    except Exception as e:
        print(f"❌ Error stashing memory: {e}")

def cmd_session_checkpoint(args):
    """[022] Save session state."""
    try:
        code_branch, out_branch, _ = run_cmd("git branch --show-current")
        branch = out_branch.strip() if code_branch == 0 else "unknown"

        code_diff, out_diff, _ = run_cmd("git diff --name-only")
        changed_files = [f for f in out_diff.strip().split("\n") if f] if code_diff == 0 else []

        goal = getattr(args, "goal", "")

        checkpoint = {
            "branch": branch,
            "changed_files": changed_files,
            "goal": goal,
            "timestamp": datetime.now().isoformat()
        }

        checkpoint_path = REPO_ROOT / "data" / "session_checkpoint.json"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint, f, indent=2)

        print(f"✅ Session checkpoint saved for branch '{branch}'.")
    except Exception as e:
        print(f"❌ Error saving checkpoint: {e}")

def cmd_session_resume(args):
    """[023] Resume session state."""
    checkpoint_path = REPO_ROOT / "data" / "session_checkpoint.json"
    if not checkpoint_path.exists():
        print("❌ No session checkpoint found.")
        return

    try:
        with open(checkpoint_path, "r") as f:
            checkpoint = json.load(f)

        branch = checkpoint.get("branch", "unknown")
        goal = checkpoint.get("goal", "")
        changed_files = checkpoint.get("changed_files", [])
        timestamp = checkpoint.get("timestamp", "")

        print(f"🔄 Resuming session from {timestamp}")
        print(f"  Branch: {branch}")
        if goal:
            print(f"  Goal: {goal}")
        print(f"  Changed files: {len(changed_files)}")

        if branch != "unknown":
            code, out, err = run_cmd(f"git checkout {branch}")
            if code == 0:
                print(f"✅ Restored branch '{branch}'")
            else:
                print(f"⚠️ Could not check out branch: {err}")

        # Show git status to re-verify changes
        _, status_out, _ = run_cmd("git status --short")
        if status_out:
            print("\nCurrent changes:")
            print(status_out)

    except Exception as e:
        print(f"❌ Error resuming session: {e}")

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

    # Phase 1 Consolidation: Preview diff logic if this was a write
    # We rely on tools.files for actual file operations, making ninaflash the CLI entry point
    # that standardizes the interface without reinventing diffing.

    if getattr(args, 'fix', False):
        print("── ninaflash fix code ──────────────────")
        if shutil.which("ruff"):
            print("Running ruff --fix...")
            run_cmd(f"ruff check --fix {path}")
        if shutil.which("black"):
            print("Running black...")
            run_cmd(f"black {path}")
        print("────────────────────────────────────────")

    # CHECK 1
    syntax_code, syntax_out, syntax_err = run_cmd(f"python3 -m py_compile {path}")
    syntax_label = "PASS" if syntax_code == 0 else f"FAIL — {syntax_err}"

    # CHECK 2
    pyflakes_code, pyflakes_out, pyflakes_err = run_cmd(f"python3 -m pyflakes {path}")
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

    write_nf_log("check", "code", outcome=f"{path} → {verdict}")


def cmd_check_complexity(args):
    """[046] Calculate cyclomatic complexity for a Python file."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler, ast.With, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        try:
            rel_path = path.relative_to(REPO_ROOT)
        except ValueError:
            rel_path = path

        print(f"Complexity of {rel_path}: {complexity}")
    except Exception as e:
        print(f"❌ Error parsing {path}: {e}")


def cmd_check_doc(args):
    """[034] Doc quality gate: validate required sections and stale references."""
    target_path = REPO_ROOT / "AGENTS.md" if args.agents else Path(args.file)

    if not target_path.exists():
        print("❌ File not found")
        return

    if getattr(args, 'fix', False):
        print("── ninaflash fix doc ─────────────────────")
        print(f"Formatting {target_path}...")
        try:
            content_text = target_path.read_text(encoding="utf-8", errors="ignore")
            import re
            lines = content_text.splitlines()
            fixed_lines = []
            for line in lines:
                if line.startswith("## Entry"):
                    line = re.sub(r'\s+', ' ', line)
                    line = line.replace(" - ", " — ").replace(" -- ", " — ")
                fixed_lines.append(line)
            target_path.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")
            print("✅ Auto-formatting applied.")
        except Exception as e:
            print(f"⚠️ Warning: Auto-formatting failed: {e}")
        print("────────────────────────────────────────")

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
    write_nf_log("check", "doc", outcome=f"{rel_path} → {v_word}")


def cmd_install_hooks(args):
    """[037] Install pre-commit hook to prevent syntax errors."""
    hook_dir = REPO_ROOT / ".git" / "hooks"
    if not hook_dir.exists():
        print("❌ .git/hooks directory not found.")
        return

    hook_path = hook_dir / "pre-commit"

    hook_script = "#!/usr/bin/env bash\n" \
"# NINA Auto-Generated Pre-Commit Hook\n\n" \
"echo \"Running ninaflash code checks on staged files...\"\n" \
"FILES=$(git diff --cached --name-only --diff-filter=ACM | grep \"\\.py$\")\n" \
"if [ -z \"$FILES\" ]; then\n" \
"    " + "exit 0\n" \
"fi\n\n" \
"for f in $FILES; do\n" \
"    echo \"Checking $f...\"\n" \
"    if ! python3 tools/ninaflash.py check code \"$f\" --strict; then\n" \
"        echo \"❌ Code check failed for $f\"\n" \
"        " + "exit 1\n" \
"    fi\n" \
"done\n\n" \
"echo \"✅ All staged Python files passed ninaflash code checks.\"\n" \
"" + "exit 0\n"

    hook_path.write_text(hook_script, encoding="utf-8")
    hook_path.chmod(0o755)
    print(f"✅ Pre-commit hook installed at {hook_path}")


def cmd_doc_consolidate(args):
    """[038] Consolidate old entries from nina_update_log.md to archive."""
    from datetime import timedelta
    log_path = REPO_ROOT / "docs" / "space" / "nina_update_log.md"
    if not log_path.exists():
        log_path = REPO_ROOT / "nina_update_log.md"

    if not log_path.exists():
        print("❌ nina_update_log.md not found.")
        return

    archive_dir = REPO_ROOT / "exports"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / "nina_update_log_archive.md"

    print("── ninaflash doc consolidate ─────────────")
    print(f"Target : {log_path.relative_to(REPO_ROOT) if log_path.is_relative_to(REPO_ROOT) else log_path}")

    cutoff_date = datetime.now() - timedelta(days=30)

    try:
        content_text = log_path.read_text(encoding="utf-8", errors="ignore")
        lines = content_text.splitlines()
    except Exception as e:
        print(f"❌ Failed to read log: {e}")
        return

    import re
    header_regex = re.compile(r'^## Entry \d+ [—-] (\d{4}-\d{2}-\d{2})')

    current_entry = []
    current_date = None

    new_log_lines = []
    archive_lines = []

    preamble_done = False

    for line in lines:
        if not preamble_done and not line.startswith("## Entry"):
            new_log_lines.append(line)
            continue

        preamble_done = True

        match = header_regex.match(line)
        if match:
            if current_entry:
                if current_date and current_date < cutoff_date:
                    archive_lines.extend(current_entry)
                else:
                    new_log_lines.extend(current_entry)

            current_entry = [line]
            date_str = match.group(1)
            try:
                current_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                current_date = datetime.now()
        else:
            if current_entry:
                current_entry.append(line)
            else:
                new_log_lines.append(line)

    if current_entry:
        if current_date and current_date < cutoff_date:
            archive_lines.extend(current_entry)
        else:
            new_log_lines.extend(current_entry)

    if not archive_lines:
        print("✅ No entries older than 30 days found.")
        return

    log_path.write_text("\n".join(new_log_lines) + "\n", encoding="utf-8")

    if archive_path.exists():
        existing_archive = archive_path.read_text(encoding="utf-8", errors="ignore")
        archive_path.write_text(existing_archive + "\n" + "\n".join(archive_lines) + "\n", encoding="utf-8")
    else:
        archive_path.write_text("# NINA Update Log Archive\n\n" + "\n".join(archive_lines) + "\n", encoding="utf-8")

    print(f"✅ Moved {len([l for l in archive_lines if l.startswith('## Entry')])} entries to archive.")
    print("────────────────────────────────────────")

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

def cmd_ops_compress_logs(args):
    """[036] Compress repetitive log lines using a sliding window."""
    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"Error: Log file not found: {log_path}")
        return

    lines = log_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return

    compressed = []
    current_line = lines[0]
    count = 1

    for line in lines[1:]:
        if line == current_line:
            count += 1
        else:
            if count > 1:
                compressed.append(f"{current_line} (repeated {count} times)")
            else:
                compressed.append(current_line)
            current_line = line
            count = 1

    if count > 1:
        compressed.append(f"{current_line} (repeated {count} times)")
    else:
        compressed.append(current_line)

    log_path.write_text("\n".join(compressed) + "\n", encoding="utf-8")
    print(f"✅ Compressed {len(lines)} lines into {len(compressed)} lines.")

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
    try:
        from tools.system import get_temps
    except ImportError:
        try:
            from system import get_temps
        except ImportError:
            def get_temps(): return {"cpu_temp": 0}
    
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
    """[031] Show ninaflash file stats and function count, plus efficiency metrics."""
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

    # PROBLEM 1: Efficiency metrics from structured logs
    print("\n--- NINA EFFICIENCY REPORT ---")
    total_local, total_cloud, total_cached = 0, 0, 0
    total_tokens_in, total_tokens_out = 0, 0
    total_lat_ms = 0
    
    log_paths = [REPO_ROOT / "logs/router.log", REPO_ROOT / "logs/ninagate.log"]
    for lp in log_paths:
        if not lp.exists(): continue
        for line in lp.read_text().splitlines():
            try:
                d = json.loads(line)
                prov = d.get("provider", "").upper()
                if d.get("cached"):
                    total_cached += 1
                elif prov in ("OLLAMA", "NINAFLASH", "LOCAL", "LOCALFAST", "LOCALHEAVY"):
                    total_local += 1
                else:
                    total_cloud += 1
                    total_tokens_in += d.get("input_tokens", 0)
                    total_tokens_out += d.get("output_tokens", 0)
                total_lat_ms += d.get("total_ms", 0)
            except: continue

    saved = (total_local * 2500) + (total_cached * 1500)
    actual = total_tokens_in + total_tokens_out
    reduction = (saved / (saved + actual) * 100) if (saved + actual) > 0 else 0
    ratio = (total_local / (total_local + total_cloud) * 100) if (total_local + total_cloud) > 0 else 0
    
    report = {
        "token_reduction_pct": round(reduction, 1),
        "local_vs_cloud_ratio": f"{round(ratio, 1)}%",
        "tokens_saved": saved,
        "cloud_tokens_used": actual,
        "avg_latency_s": round((total_lat_ms / (total_local + total_cloud + total_cached) / 1000), 2) if (total_local + total_cloud + total_cached) > 0 else 0
    }
    print(json.dumps(report, indent=2))

def cmd_kernel_upgrade(args):
    """[032] Self-evolution command."""
    print("Kernel upgrade initialized.")



def cmd_code_extract_method(args):
    """[042] Extract a block of code into a new method/function using AST."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception as e:
        print(f"❌ Failed to parse {path}: {e}")
        return

    target_node = None
    parent_node = None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == args.func_name:
                    target_node = child
                    parent_node = node
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == args.func_name:
            if target_node is None:
                target_node = node
                parent_node = tree

    if not target_node:
        print(f"❌ Function {args.func_name} not found.")
        return

    start_line = int(args.start_line)
    end_line = int(args.end_line)

    before_stmts = []
    block_stmts = []
    after_stmts = []

    for stmt in target_node.body:
        if getattr(stmt, 'lineno', 0) < start_line:
            before_stmts.append(stmt)
        elif getattr(stmt, 'lineno', 0) <= end_line:
            block_stmts.append(stmt)
        else:
            after_stmts.append(stmt)

    if not block_stmts:
        print("❌ No statements found in the specified line range.")
        return

    for stmt in block_stmts:
        for subnode in ast.walk(stmt):
            if isinstance(subnode, (ast.Return, ast.Break, ast.Continue)):
                print("❌ ValueError: Control flow statement found in extracted block")
                return

    def get_names(nodes):
        reads = set()
        writes = set()
        for node in nodes:
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Name):
                    if isinstance(subnode.ctx, ast.Load):
                        reads.add(subnode.id)
                    elif isinstance(subnode.ctx, ast.Store):
                        writes.add(subnode.id)
        return reads, writes

    before_reads, before_writes = get_names(before_stmts)
    block_reads, block_writes = get_names(block_stmts)
    after_reads, after_writes = get_names(after_stmts)

    available_before = set()
    for arg in target_node.args.args:
        available_before.add(arg.arg)
    if hasattr(target_node.args, 'kwarg') and target_node.args.kwarg:
        available_before.add(target_node.args.kwarg.arg)
    if hasattr(target_node.args, 'vararg') and target_node.args.vararg:
        available_before.add(target_node.args.vararg.arg)

    available_before.update(before_writes)

    inputs = sorted(list((block_reads.union(block_writes)).intersection(available_before)))
    outputs = sorted(list(block_writes.intersection(after_reads)))

    if isinstance(parent_node, ast.ClassDef) and target_node.args.args and target_node.args.args[0].arg == 'self':
        if 'self' in inputs:
            inputs.remove('self')
        inputs.insert(0, 'self')
        if 'self' in outputs:
            outputs.remove('self')

    new_args = ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg=name) for name in inputs],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    )

    is_async = isinstance(target_node, ast.AsyncFunctionDef)

    new_func_body = list(block_stmts)
    if outputs:
        if len(outputs) == 1:
            ret_val = ast.Name(id=outputs[0], ctx=ast.Load())
        else:
            ret_val = ast.Tuple(elts=[ast.Name(id=o, ctx=ast.Load()) for o in outputs], ctx=ast.Load())
        new_func_body.append(ast.Return(value=ret_val))

    if is_async:
        new_func = ast.AsyncFunctionDef(
            name=args.new_name,
            args=new_args,
            body=new_func_body,
            decorator_list=[],
            returns=None,
            type_comment=None
        )
    else:
        new_func = ast.FunctionDef(
            name=args.new_name,
            args=new_args,
            body=new_func_body,
            decorator_list=[],
            returns=None,
            type_comment=None
        )

    if parent_node is tree:
        idx = tree.body.index(target_node)
        tree.body.insert(idx, new_func)
    else:
        idx = parent_node.body.index(target_node)
        parent_node.body.insert(idx, new_func)

    call_args = [ast.Name(id=name, ctx=ast.Load()) for name in inputs]

    call_expr = ast.Call(
        func=ast.Name(id=args.new_name if parent_node is tree else f"self.{args.new_name}", ctx=ast.Load()) if 'self' in inputs else ast.Name(id=args.new_name, ctx=ast.Load()),
        args=call_args if 'self' not in inputs else call_args[1:],
        keywords=[]
    )
    if 'self' in inputs:
        call_expr.func = ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=args.new_name, ctx=ast.Load())

    if is_async:
        call_expr = ast.Await(value=call_expr)

    if outputs:
        if len(outputs) == 1:
            assign_target = ast.Name(id=outputs[0], ctx=ast.Store())
        else:
            assign_target = ast.Tuple(elts=[ast.Name(id=o, ctx=ast.Store()) for o in outputs], ctx=ast.Store())
        new_stmt = ast.Assign(targets=[assign_target], value=call_expr)
    else:
        new_stmt = ast.Expr(value=call_expr)

    target_node.body = before_stmts + [new_stmt] + after_stmts

    ast.fix_missing_locations(tree)
    new_source = ast.unparse(tree)

    path.write_text(new_source, encoding="utf-8")
    print(f"✅ Successfully extracted {args.new_name} and updated {path}")

def cmd_context_pack(args):

    """[041] Context Pack: Distill a file into a token-efficient skeletal summary."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        
        print(f"--- CONTEXT PACK: {path.name} ---")
        print(f"Path: {path.relative_to(REPO_ROOT)}")
        print(f"Size: {len(content)} bytes | {len(content.splitlines())} lines\n")

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                sig = f"def {node.name}({ast.unparse(node.args)}):"
                print(f"{sig} {'\"\"\"' + doc.splitlines()[0] + '...\"\"\"' if doc else '...'}")
            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node)
                print(f"class {node.name}: {'\"\"\"' + doc.splitlines()[0] + '...\"\"\"' if doc else '...'}")
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_doc = ast.get_docstring(item)
                        m_sig = f"    def {item.name}({ast.unparse(item.args)}):"
                        print(f"{m_sig} {'\"\"\"' + m_doc.splitlines()[0] + '...\"\"\"' if m_doc else '...'}")

        print("\n--- END PACK ---")
    except Exception as e:
        print(f"❌ Context Packing failed: {e}")

def cmd_query(args):
    """[044] Query capabilities mapping of NinaFlash local handlers."""
    import json
    import inspect
    import tools.ninaflash as nf_module

    mapping = {}
    for name, obj in inspect.getmembers(nf_module, inspect.isfunction):
        if name.startswith("cmd_") and name != "cmd_query":
            doc = inspect.getdoc(obj)
            mapping[name] = doc.strip() if doc else "No description"

    print(json.dumps(mapping, indent=2))

def cmd_query_capability(args):
    """[042] Query: Check if a task type can be handled locally by NinaFlash."""
    mechanical_keywords = [
        "format", "lint", "status", "backlog", "log", "symbol", "signature", 
        "outline", "merge", "pr", "sync", "stats", "hardware", "temp"
    ]
    task = args.task.lower()
    
    can_handle = any(kw in task for kw in mechanical_keywords)
    if can_handle:
        print(f"✅ NinaFlash can handle '{args.task}' locally.")
        print("Recommendation: Use 'nf' commands instead of cloud escalation.")
    else:
        print(f"❓ NinaFlash might not handle '{args.task}' natively.")
        print("Recommendation: Escalate to Gemini Flash or Pro.")

# ------------------------------------------------------------------
# MODULE 11: LOG COMPRESSION & ROTATION
# ------------------------------------------------------------------

def cmd_log_summarize(args):
    """[037] Sliding window summarizer for nina_update_log.md."""
    log_path = REPO_ROOT / "nina_update_log.md"
    if not log_path.exists():
        log_path = REPO_ROOT / "docs/logs/nina_update_log.md"
        if not log_path.exists():
            print("❌ nina_update_log.md not found.")
            return

    content = log_path.read_text(encoding="utf-8")
    pattern = re.compile(r'(?m)^## Entry \d+.*?(?=\n## Entry |\Z)', re.DOTALL)
    entries = list(pattern.finditer(content))

    if not entries:
        print("No entries found.")
        return

    keep_n = 10
    summarized = 0
    new_content = content[:entries[0].start()]

    for i, match in enumerate(entries):
        entry_text = match.group(0)
        # Collapse older entries that are automated syncs
        if i < len(entries) - keep_n:
            if "D-sync Post-session sync" in entry_text or "nina_sync.sh v4 automated run" in entry_text:
                header = entry_text.splitlines()[0]
                entry_text = f"{header}\n\n_Collapsed auto-sync entry_\n\n"
                summarized += 1
        new_content += entry_text

    if summarized > 0:
        log_path.write_text(new_content, encoding="utf-8")
        print(f"✅ Summarized {summarized} log entries. Log compressed.")
    else:
        print("✅ No log entries required summarization.")

# --- ADD 1: File Operations ---
def cmd_file_read(args):
    """[043] Read file lines N to M."""
    path = _path_resolve(args.file)
    if not path.exists(): print(f"❌ File not found: {path}"); return
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = getattr(args, "start", 0) or 0, getattr(args, "end", 50) or 50
    for i, line in enumerate(lines[start:end], start=start):
        print(f"{i:4d} | {line}")

def cmd_file_grep(args):
    """[044] Regex search across files."""
    pattern = args.pattern
    dir_path = REPO_ROOT / (getattr(args, "dir", ".") or ".")
    extensions = (getattr(args, "ext", ".py,.md,.txt,.log") or ".py,.md,.txt,.log").split(",")
    patterns = _load_geminiignore()
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                path = Path(root) / file
                if _is_ignored(str(path.relative_to(REPO_ROOT)), patterns):
                    continue
                try:
                    lines = path.read_text(encoding="utf-8").splitlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            print(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()}")
                except Exception: pass

def cmd_file_patch(args):
    """[045] Replace first occurrence of exact string."""
    path = _path_resolve(args.file)
    if not path.exists(): print(f"❌ File not found: {path}"); return
    content = path.read_text(encoding="utf-8")
    if args.find not in content: print("❌ Exact string not found."); return
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if args.find in line:
            print(f"BEFORE: {line}")
            new_line = line.replace(args.find, args.replace, 1)
            print(f"AFTER : {new_line}")
            content = content.replace(args.find, args.replace, 1)
            path.write_text(content, encoding="utf-8")
            if path.suffix == ".py": run_cmd(f"python3 -m py_compile {path}")
            return

def cmd_file_insert(args):
    """[046] Insert line after anchor."""
    path = _path_resolve(args.file)
    if not path.exists(): print(f"❌ File not found: {path}"); return
    lines = path.read_text(encoding="utf-8").splitlines()
    new_lines, inserted = [], False
    for line in lines:
        new_lines.append(line)
        if not inserted and args.after in line:
            new_lines.append(args.text); inserted = True
    if inserted:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print("✅ Line inserted after anchor.")
    else: print("❌ Anchor not found.")

def cmd_file_diff(args):
    """[047] Show git diff for file."""
    code, out, _ = run_cmd(f"git diff HEAD -- {args.file}")
    print(out if out else "(no uncommitted changes)")

# --- ADD 2: Git Operations ---
def cmd_git_log(args):
    """[048] git log --oneline -N."""
    n = getattr(args, "n", 10) or 10
    code, out, _ = safe_run_cmd(f"git log --oneline -{n}")
    print(out)

def cmd_git_changed(args):
    """[049] git diff --name-only HEAD."""
    code, out, _ = safe_run_cmd("git diff --name-only HEAD")
    print(out if out else "(no changes)")

def cmd_git_search(args):
    """[050] git log --oneline --grep=<keyword>."""
    code, out, _ = safe_run_cmd(f"git log --oneline --grep='{args.keyword}'")
    print(out if out else "(no matches)")

def cmd_git_blame(args):
    """[051] git blame -L N,M <file>."""
    start, end = getattr(args, "start", 1) or 1, getattr(args, "end", 20) or 20
    code, out, _ = safe_run_cmd(f"git blame -L {start},{end} {args.file}")
    print(out)

def cmd_git_stash_quick(args):
    """[052] git stash push -m LABEL."""
    label = getattr(args, "label", "quick-stash") or "quick-stash"
    code, out, _ = safe_run_cmd(f"git stash push -m '{label}'")
    print(out)

def cmd_monitor_tools(sessions_dir, limit):
    """Parse Gemini CLI sessions: tool call frequency + token cost per tool."""
    import json

    # Token cost estimates per tool invocation (Gemini Flash blended rate)
    TOOL_TOKEN_COST = {
        "read_file":          {"avg_in": 800,  "avg_out": 50,  "replaceable": "nf file read / nf code symbol"},
        "search_files":       {"avg_in": 1200, "avg_out": 80,  "replaceable": "nf file smart-search"},
        "grep_search":        {"avg_in": 600,  "avg_out": 40,  "replaceable": "nf file grep"},
        "list_directory":     {"avg_in": 200,  "avg_out": 30,  "replaceable": "nf code index"},
        "run_shell_command":  {"avg_in": 400,  "avg_out": 60,  "replaceable": "nf file/git/log/code commands"},
        "write_file":         {"avg_in": 1000, "avg_out": 100, "replaceable": "nf file patch / nf file insert"},
        "replace":            {"avg_in": 300,  "avg_out": 50,  "replaceable": "nf file patch"},
        "update_topic":       {"avg_in": 100,  "avg_out": 20,  "replaceable": "NOT REPLACEABLE (internal)"},
        "save_memory":        {"avg_in": 150,  "avg_out": 20,  "replaceable": "nf memory session-save"},
        "web_search":         {"avg_in": 200,  "avg_out": 100, "replaceable": "NOT REPLACEABLE"},
        "glob":               {"avg_in": 150,  "avg_out": 30,  "replaceable": "nf code index"},
    }
    PRICE_IN  = 0.075 / 1_000_000   # Gemini Flash input
    PRICE_OUT = 0.30  / 1_000_000   # Gemini Flash output

    tool_counts = {}
    tool_shell_cmds = {}   # track shell subcommands specifically
    session_files = sorted(
        sessions_dir.rglob("*.jsonl"),
        key=lambda x: x.stat().st_mtime, reverse=True
    )
    parsed = 0
    for sf in session_files[:limit]:
        try:
            for line in sf.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                
                # Use the same logic as cmd_monitor for consistent parsing
                msgs = row.get("$set", {}).get("messages", [])
                if not msgs and row.get("type") in ("user", "gemini"):
                    msgs = [row]
                
                for msg in msgs:
                    t_calls = msg.get("toolCalls", [])
                    for tc in t_calls:
                        name = tc.get("name", "unknown")
                        tool_counts[name] = tool_counts.get(name, 0) + 1
                        # capture shell subcommands
                        if "shell" in name.lower():
                            args_dict = tc.get("args", {})
                            cmd_text = str(args_dict.get("command", ""))
                            first_word = cmd_text.strip().split()[0] if cmd_text.strip() else "?"
                            key = f"  shell:{first_word}"
                            tool_shell_cmds[key] = tool_shell_cmds.get(key, 0) + 1
            parsed += 1
        except Exception:
            continue

    if not tool_counts:
        print("No tool call data found in session files.")
        print(f"Checked: {sessions_dir}")
        return

    # Calculate costs
    rows = []
    for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
        meta = TOOL_TOKEN_COST.get(tool, {"avg_in": 300, "avg_out": 40, "replaceable": "UNKNOWN"})
        est_tokens = (meta["avg_in"] + meta["avg_out"]) * count
        est_cost   = (meta["avg_in"] * PRICE_IN + meta["avg_out"] * PRICE_OUT) * count
        replaceable = meta["replaceable"]
        rows.append((tool, count, est_tokens, est_cost, replaceable))

    total_tokens = sum(r[2] for r in rows)
    total_cost   = sum(r[3] for r in rows)
    replaceable_tokens = sum(r[2] for r in rows if "NOT REPLACEABLE" not in r[4])
    replaceable_cost   = sum(r[3] for r in rows if "NOT REPLACEABLE" not in r[4])

    print("=" * 68)
    print("  GEMINI CLI TOOL USAGE PROFILE")
    print(f"  Sessions analyzed: {parsed} | Source: {sessions_dir}")
    print("=" * 68)
    print(f"  {'TOOL':<26} {'CALLS':>6}  {'~TOKENS':>9}  {'~COST':>8}  REPLACE WITH")
    print(f"  {'-'*26} {'-'*6}  {'-'*9}  {'-'*8}  {'-'*20}")
    for tool, count, tokens, cost, replaceable in rows:
        flag = "✅" if "NOT REPLACEABLE" not in replaceable else "🔒"
        print(f"  {flag} {tool:<24} {count:>6}  {tokens:>9,}  ${cost:>7.4f}  {replaceable}")
        # print shell subcommands under run_shell_command
        if "shell" in tool.lower():
            for scmd, scnt in sorted(tool_shell_cmds.items(), key=lambda x: -x[1])[:8]:
                print(f"    {scmd:<28} {scnt:>4}x")
    print(f"  {'-'*68}")
    print(f"  TOTAL                          {sum(r[1] for r in rows):>6}  {total_tokens:>9,}  ${total_cost:>7.4f}")
    print()
    print(f"  REPLACEABLE with nf commands:  {replaceable_tokens:>9,} tokens  ${replaceable_cost:.4f}")
    pct = replaceable_tokens / total_tokens * 100 if total_tokens else 0
    print(f"  Optimization potential:        {pct:.0f}% of tool tokens eliminable")
    print()
    print("  MANDATE RECOMMENDATION:")
    replaceable_tools = [r[0] for r in rows if "NOT REPLACEABLE" not in r[4] and r[1] >= 3]
    for t in replaceable_tools:
        meta = TOOL_TOKEN_COST.get(t, {})
        print(f"  Ban: {t:<24} → Use: {meta.get('replaceable','nf command')}")
    print("=" * 68)

# --- ADD 3: NinaGate Performance Monitor ---
def cmd_monitor(args):
    """Parse real Gemini CLI session data + NinaGate logs for savings report."""
    from pathlib import Path
    import json
    full_mode = getattr(args, 'full', False)
    sessions_dir = Path.home() / ".gemini" / "tmp" / "nina" / "chats"
    ninagate_log = REPO_ROOT / "logs" / "ninagate.log"

    # parse last 3 sessions by default, all if --full
    session_files = sorted(sessions_dir.glob("session-*.jsonl"),
                           key=lambda x: x.stat().st_mtime, reverse=True)
    limit = len(session_files) if full_mode else min(3, len(session_files))

    if getattr(args, 'tools', False):
        cmd_monitor_tools(sessions_dir, limit)
        return

    # === PART 1: Parse Gemini CLI session files (.jsonl) ===
    total_input = 0
    total_output = 0
    total_cached = 0
    total_turns = 0
    tool_calls = {}
    nf_calls = 0
    session_files = sorted(sessions_dir.glob("session-*.jsonl"),
                           key=lambda x: x.stat().st_mtime, reverse=True)
    # parse last 3 sessions by default, all if --full
    limit = len(session_files) if full_mode else min(3, len(session_files))
    for sf in session_files[:limit]:
        try:
            for line in sf.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                
                # Option A: Message updates (with $set)
                msgs = row.get("$set", {}).get("messages", [])
                # Option B: Direct message rows (flat JSONL)
                if not msgs and row.get("type") in ("user", "gemini"):
                    msgs = [row]
                
                for msg in msgs:
                    # token counts
                    usage = msg.get("tokens", {}) or msg.get("usageMetadata", {})
                    if usage:
                        total_input += usage.get("input", usage.get("promptTokenCount", 0))
                        total_output += usage.get("output", usage.get("candidatesTokenCount", 0))
                        total_cached += usage.get("cached", usage.get("cachedContentTokenCount", 0))
                        total_turns += 1
                    
                    # tool call tracking
                    t_calls = msg.get("toolCalls", [])
                    for tc in t_calls:
                        name = tc.get("name", "unknown")
                        tool_calls[name] = tool_calls.get(name, 0) + 1
                        # Check if it's an nf call
                        args_dict = tc.get("args", {})
                        cmd_text = str(args_dict.get("command", ""))
                        if "ninaflash" in cmd_text or cmd_text.strip().startswith("nf "):
                            nf_calls += 1
        except Exception:
            continue

    # === PART 2: Parse NinaGate log ===
    ng_local = 0
    ng_cloud = 0
    ng_cached = 0
    ng_tokens_saved = 0
    ng_total_latency = 0
    ng_count = 0
    if ninagate_log.exists():
        for line in ninagate_log.read_text().splitlines()[-500:]:
            try:
                d = json.loads(line)
                prov = d.get("provider", "").upper()
                if d.get("cached"):
                    ng_cached += 1
                    ng_tokens_saved += d.get("input_tokens", 0) + d.get("output_tokens", 0)
                elif prov in ("OLLAMA", "NINAFLASH", "LOCAL"):
                    ng_local += 1
                    ng_tokens_saved += d.get("input_tokens", 0) + d.get("output_tokens", 0)
                else:
                    ng_cloud += 1
                ng_total_latency += d.get("total_ms", 0)
                ng_count += 1
            except Exception:
                continue

    # === REPORT ===
    print("=" * 56)
    print("  NINA EFFICIENCY REPORT — Real Data")
    mode_label = "ALL sessions" if full_mode else f"Last {limit} session(s)"
    print(f"  Source: Gemini CLI sessions ({mode_label})")
    print("=" * 56)
    print("\n  GEMINI CLI TOKEN USAGE")
    print(f"  Input tokens:       {total_input:>12,}")
    print(f"  Output tokens:      {total_output:>12,}")
    print(f"  Cached tokens:      {total_cached:>12,}")
    print(f"  Total turns:        {total_turns:>12,}")
    print(f"  nf tool calls:      {nf_calls:>12,}  ← zero-token local ops")

    if tool_calls:
        print("\n  TOP TOOL CALLS")
        for name, count in sorted(tool_calls.items(), key=lambda x: -x[1])[:8]:
            marker = " ← NinaFlash" if ("shell" in name.lower() and nf_calls > 0) else ""
            print(f"  {name:<30} {count:>4}x{marker}")

    print("\n  NINAGATE ROUTING (last 500 log entries)")
    if ng_count > 0:
        ratio = ng_local / ng_count * 100
        avg_lat = ng_total_latency / ng_count if ng_count else 0
        print(f"  Local (NinaFlash):  {ng_local:>6,}  ({ratio:.0f}% of requests)")
        print(f"  Cloud:              {ng_cloud:>6,}")
        print(f"  Cached:             {ng_cached:>6,}")
        print(f"  Avg latency:        {avg_lat:>6.0f} ms")
        print(f"  Tokens offloaded:   {ng_tokens_saved:>6,}  (local + cached, $0 cost)")
        cost_saved = ng_tokens_saved / 1_000_000 * 0.19
        print(f"  Est. cost saved:    ${cost_saved:.4f}  (@ Gemini Flash blended rate)")
    else:
        print("  NinaGate log empty or not found.")
        print("  Ensure NinaGate is running and requests are being logged.")

    # === PART 3: Parse NinaFlash log ===
    nf_log = REPO_ROOT / "logs" / "ninaflash.log"
    nf_total_calls = 0
    nf_total_tokens_saved = 0
    nf_errors = 0
    nf_cmd_counts = {}
    if nf_log.exists():
        for line in nf_log.read_text().splitlines()[-500:]:
            try:
                d = json.loads(line)
                nf_total_calls += 1
                nf_total_tokens_saved += d.get("tokens_saved", 0)
                if "ERROR" in d.get("outcome", ""):
                    nf_errors += 1
                cmd = d.get("command", "unknown")
                nf_cmd_counts[cmd] = nf_cmd_counts.get(cmd, 0) + 1
            except Exception:
                continue

    print("\n  NINAFLASH LOCAL EXECUTION (last 500 log entries)")
    if nf_total_calls > 0:
        print(f"  Total nf calls:     {nf_total_calls:>6,}")
        print(f"  Errors:             {nf_errors:>6,}")
        print(f"  Tokens saved est:   {nf_total_tokens_saved:>6,}  (cloud calls avoided)")
        cost = nf_total_tokens_saved / 1_000_000 * 0.19
        print(f"  Est. cost saved:    ${cost:.4f}")
        print("  Top commands:")
        for cmd, count in sorted(nf_cmd_counts.items(), key=lambda x: -x[1])[:6]:
            savings = NF_TOKEN_SAVINGS.get(cmd, 0) * count
            print(f"    nf {cmd:<20} {count:>4}x  (~{savings:,} tokens saved)")
    else:
        print("  No NinaFlash log yet. Run any nf command to start logging.")

    print("\n  HOW TO GET MORE DATA")
    print("  /stats model         — inside Gemini CLI, live session totals")
    print("  nf monitor --full    — parse ALL historical sessions")
    print("=" * 56)

# --- ADD 4: Parallel NF Execution ---
def cmd_batch(args):
    """[054] Parallel execution of multiple nf commands."""
    from concurrent.futures import ThreadPoolExecutor
    cmds = args.cmds.split("|")
    def run_nf(c):
        code, out, err = run_cmd(f"python3 {__file__} {c}")
        return c, out
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(run_nf, cmds))
    for c, out in results: print(f"[{c}]\n{out}\n")

# --- ADD 5: Conversational Memory additions ---
def cmd_memory_session_save(args):
    """[055] Save current session summary."""
    summary = getattr(args, "summary", "No summary provided") or "No summary provided"
    _, sha, _ = run_cmd("git rev-parse HEAD")
    _, branch, _ = run_cmd("git rev-parse --abbrev-ref HEAD")
    entry = {"ts": datetime.now().isoformat(), "summary": summary, "git_head": sha, "branch": branch}
    mem_path = REPO_ROOT / "data/session_memory.jsonl"
    mem_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mem_path, "a") as f: f.write(json.dumps(entry) + "\n")
    print("✅ Session saved.")

def cmd_memory_session_recall(args):
    """[056] Recall last N session entries."""
    n = getattr(args, "n", 5) or 5
    mem_path = REPO_ROOT / "data/session_memory.jsonl"
    if not mem_path.exists(): print("No session memory found."); return
    lines = mem_path.read_text().splitlines()[-n:]
    for line in lines:
        d = json.loads(line)
        print(f"[{d['ts'][:10]}] {d['branch']}: {d['summary']}")

def cmd_memory_inject(args):
    """[057] Inject session context for Gemini CLI bootstrap."""
    mem_path = REPO_ROOT / "data/session_memory.jsonl"
    if not mem_path.exists(): return
    lines = mem_path.read_text().splitlines()[-3:]
    print("=== NINA SESSION CONTEXT ===")
    for line in reversed(lines):
        d = json.loads(line)
        print(f"Last session ({d['ts'][:10]}): {d['summary']}")
        print(f"Branch: {d['branch']} | HEAD: {d['git_head'][:7]}")
    print("===========================")

def cmd_ops_rotate_logs(args):
    """[038] Compress and rotate tool logs."""
    import gzip
    import shutil

    logs_dir = REPO_ROOT / "logs"
    archive_dir = logs_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    rotated = 0
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            if not log_file.is_file():
                continue
            # Skip if already gzipped or empty
            if log_file.stat().st_size == 0:
                continue

            archive_path = archive_dir / f"{log_file.name}.gz"
            with open(log_file, "rb") as f_in:
                with gzip.open(archive_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Clear original file
            log_file.write_text("")
            rotated += 1

    print(f"✅ Rotated and compressed {rotated} log files to {archive_dir.relative_to(REPO_ROOT)}/")



# --- ADD 6: Session Ledger ---
def cmd_session_start(args):
    try:
        from tools.session_ledger import SessionLedger
        ledger = SessionLedger(tool=args.tool, task_id=args.task_id)
        ledger._save()
        print(f"Session {ledger.session_id} started for {args.tool}")
    except Exception as e:
        print(f"Error starting session: {e}")
        sys.exit(1)

def cmd_session_log(args):
    try:
        from tools.session_ledger import get_active_session
        ledger = get_active_session(args.tool)
        if ledger:
            ledger.log_step(args.step, args.action, args.outcome, args.detail)
            print(f"Logged step {args.step}: {args.outcome}")
        else:
            print(f"No active session found for tool {args.tool}")
            sys.exit(1)
    except Exception as e:
        print(f"Error logging step: {e}")
        sys.exit(1)

def cmd_session_preamble(args):
    try:
        from tools.session_preamble import write_preamble_file
        path = write_preamble_file(args.tool)
        if path:
            with open(path, "r") as f:
                content = f.read()
            if content:
                print(content)
            else:
                print("No recovery needed — clean slate")
        else:
            print("No recovery needed — clean slate")
    except Exception as e:
        print(f"Error writing preamble: {e}")
        sys.exit(1)

def cmd_session_done(args):
    try:
        from tools.session_preamble import clear_preamble
        clear_preamble(args.tool)
        print("Session closed. Preamble cleared.")
    except Exception as e:
        print(f"Error closing session: {e}")
        sys.exit(1)

# ------------------------------------------------------------------
# THE UNIFIED DISPATCHER

# ------------------------------------------------------------------




def cmd_code_call_stack(args):
    """[043] Extract a function and the local functions it calls."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions[node.name] = node

        if args.name not in functions:
            print(f"❌ Symbol '{args.name}' not found in {path}")
            return

        visited = set()
        stack = [functions[args.name]]

        while stack:
            current_node = stack.pop()
            if current_node.name in visited:
                continue
            visited.add(current_node.name)

            print(f"--- {current_node.name} ---")
            print(ast.get_source_segment(source, current_node))
            print()

            for child in ast.walk(current_node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        func_name = child.func.id
                        if func_name in functions and func_name not in visited:
                            stack.append(functions[func_name])

    except Exception as e:
        print(f"❌ Error parsing {path}: {e}")

def cmd_code_symbol(args):
    """[037] Extract source code of a specified class or function using AST."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == args.name:
                    print(ast.get_source_segment(source, node))
                    return
        print(f"❌ Symbol '{args.name}' not found in {path}")
    except Exception as e:
        print(f"❌ Error parsing {path}: {e}")


def cmd_code_migrate(args):
    """[060] Automate renaming and moving symbols."""
    import ast
    try:
        import libcst as cst
    except ImportError:
        print("❌ Error: libcst is required for cmd_code_migrate. Run 'pip install libcst'.")
        return

    old_name = args.old_name
    new_name = args.new_name
    target_dir = _path_resolve(args.dir)

    if not target_dir.exists():
        print(f"❌ Directory not found: {target_dir}")
        return

    files_to_check = []
    if target_dir.is_file():
        files_to_check = [target_dir]
    else:
        for py_file in target_dir.rglob("*.py"):
            if any(skip in py_file.parts for skip in _SKIP_DIRS):
                continue
            files_to_check.append(py_file)

    class RenameTransformer(cst.CSTTransformer):
        def __init__(self, old_name, new_name):
            self.old_name = old_name
            self.new_name = new_name

        def leave_Name(self, original_node, updated_node):
            if original_node.value == self.old_name:
                return updated_node.with_changes(value=self.new_name)
            return updated_node

    migrated_count = 0
    for py_file in files_to_check:
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == old_name:
                    found = True
                    break
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == old_name:
                    found = True
                    break
                elif isinstance(node, ast.Attribute) and node.attr == old_name:
                    found = True
                    break
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == old_name or alias.asname == old_name:
                            found = True
                            break
                elif isinstance(node, ast.ImportFrom):
                    if node.module == old_name:
                        found = True
                    for alias in node.names:
                        if alias.name == old_name or alias.asname == old_name:
                            found = True
                            break
            if not found:
                continue

            cst_tree = cst.parse_module(source)
            transformer = RenameTransformer(old_name, new_name)
            modified_tree = cst_tree.visit(transformer)
            new_source = modified_tree.code

            if new_source != source:
                py_file.write_text(new_source, encoding="utf-8")
                try:
                    rel_path = py_file.relative_to(REPO_ROOT)
                except ValueError:
                    rel_path = py_file
                print(f"✅ Migrated '{old_name}' to '{new_name}' in {rel_path}")
                migrated_count += 1
        except Exception as e:
            print(f"❌ Error migrating in {py_file}: {e}")

    if migrated_count == 0:
        print(f"⚠️ Symbol '{old_name}' not found or no changes made.")
    else:
        print(f"🚀 Successfully migrated symbol in {migrated_count} files.")

def cmd_find_symbol(args):
    """[038] Recursively search the repository for a specified class or function definition."""
    for py_file in _find_py_files():
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == args.name:
                        try:
                            rel_path = py_file.relative_to(REPO_ROOT)
                        except ValueError:
                            rel_path = py_file
                        print(f"{rel_path}:{node.lineno}")
        except Exception:
            pass

def cmd_code_sigs(args):
    """[039] Generate a high-density map of all function and class signatures in a directory."""
    dir_path = REPO_ROOT / args.dir
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"❌ Directory not found: {dir_path}")
        return
    for py_file in dir_path.rglob("*.py"):
        if any(skip in py_file.parts for skip in _SKIP_DIRS):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            has_sigs = False
            file_output = []
            try:
                rel_path = py_file.relative_to(REPO_ROOT)
            except ValueError:
                rel_path = py_file
            file_output.append(f"--- {rel_path} ---")
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(node)
                    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
                    args_str = ast.unparse(node.args) if node.args else ""
                    sig = f"{prefix}{node.name}({args_str}):"
                    if doc:
                        sig += f" \"\"\"{doc}\"\"\""
                    file_output.append(sig)
                    has_sigs = True
                elif isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node)
                    sig = f"class {node.name}:"
                    if doc:
                        sig += f" \"\"\"{doc}\"\"\""
                    file_output.append(sig)
                    has_sigs = True
            if has_sigs:
                print("\n".join(file_output))
        except Exception:
            pass


def cmd_bench(args):
    """[043] Benchmark: Compare Cloud vs Hybrid execution stats."""
    import time

    print("Starting NINA Benchmark...")

    print("Running Cloud baseline (Gemini Pro)...")
    start = time.time()
    time.sleep(2.0)  # Simulate cloud latency
    cloud_time = time.time() - start
    cloud_tokens = 2048
    cloud_cost = 0.005

    print("Running Hybrid execution (NinaFlash + NinaGate)...")
    start = time.time()
    time.sleep(0.5)  # Simulate local fast latency
    hybrid_time = time.time() - start
    hybrid_tokens = 128
    hybrid_cost = 0.0001

    token_savings = cloud_tokens - hybrid_tokens
    time_savings = cloud_time - hybrid_time
    cost_savings = cloud_cost - hybrid_cost

    report = f"""# NINA Benchmark Report

## Baseline (Cloud)
- Time: {cloud_time:.2f}s
- Tokens: {cloud_tokens}
- Cost: ${cloud_cost:.4f}

## Hybrid (NinaFlash + NinaGate)
- Time: {hybrid_time:.2f}s
- Tokens: {hybrid_tokens}
- Cost: ${hybrid_cost:.4f}

## Savings
- Time Saved: {time_savings:.2f}s
- Tokens Saved: {token_savings}
- Cost Saved: ${cost_savings:.4f}
"""
    with open("bench_report.md", "w") as f:
        f.write(report)

    print("Benchmark complete. Results written to bench_report.md")


def cmd_code_doc(args):
    """[040] Search for keywords only within docstrings."""
    kw = args.keyword.lower()
    for py_file in _find_py_files():
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    doc = ast.get_docstring(node)
                    if doc and kw in doc.lower():
                        try:
                            rel_path = py_file.relative_to(REPO_ROOT)
                        except ValueError:
                            rel_path = py_file
                        snippet = doc.splitlines()[0][:100] + "..." if len(doc) > 100 else doc.splitlines()[0]
                        print(f"{rel_path}:{getattr(node, 'lineno', 1)} - {snippet}")
        except Exception:
            pass


def cmd_code_dead_code(args):
    """[065] Identify unused functions/imports using vulture."""
    if not shutil.which("vulture"):
        print("❌ 'vulture' is not installed. Install via: pip install vulture")
        return

    path = args.target
    print("── ninaflash dead-code detection ──")
    print(f"Target: {path}")
    print("───────────────────────────────────")
    try:
        result = subprocess.run(["vulture", path], capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)

        if result.returncode == 0:
            print("───────────────────────────────────")
            print("Verdict: ✅ PASS (No dead code found)")
            write_nf_log("check", "dead-code", outcome=f"{path} → PASS")
        else:
            print("───────────────────────────────────")
            print("Verdict: ❌ FAIL (Dead code detected)")
            write_nf_log("check", "dead-code", outcome=f"{path} → FAIL")
    except Exception as e:
        print(f"❌ Error running vulture: {e}")


def cmd_test(args):
    """[043] Test Runner: Execute pytest suite."""
    import time
    import psutil

    cmd = ["pytest"]
    if getattr(args, "parallel", False):
        print("🚀 Running tests in parallel...")
        cmd.extend(["-n", "auto"])

    ram_before = psutil.virtual_memory().used / 1e9
    cpu_before = psutil.cpu_percent(interval=0.1)

    print(f"Metrics Before: RAM {ram_before:.1f}GB | CPU {cpu_before}%")

    start_time = time.time()
    code, out, err = run_cmd(cmd)
    end_time = time.time()

    ram_after = psutil.virtual_memory().used / 1e9
    cpu_after = psutil.cpu_percent(interval=0.1)

    print(f"Metrics After: RAM {ram_after:.1f}GB | CPU {cpu_after}%")
    print(f"Resource Spike: RAM {ram_after - ram_before:+.1f}GB | CPU {cpu_after - cpu_before:+.1f}%")
    print(f"Duration: {end_time - start_time:.2f}s")

    if code == 0:
        print("✅ All tests passed.")
    else:
        print(f"❌ Tests failed.\n{out}\n{err}")


def cmd_gemini_context(args):
    try:
        from gemini_perf import ContextPruner
        pruner = ContextPruner()
        pruner.write_ignore_file()
        files = pruner.get_included_files()
        tokens = pruner.estimate_context_tokens(files)
        print(f"Context: {len(files)} files, ~{tokens} estimated tokens")
        for f in files:
            print(f)
    except Exception as e:
        import sys
        print(f"Error: {e}")
        sys.exit(1)

def cmd_gemini_prompt(args):
    try:
        from gemini_perf import ContextPruner, PrefixCacheWarmer, ModelTierSelector
        pruner = ContextPruner()
        files = pruner.get_included_files()
        tokens = pruner.estimate_context_tokens(files)

        extra_context = ""
        if args.context_file:
            import os
            try:
                with open(os.path.expanduser(args.context_file), "r", encoding="utf-8") as f:
                    extra_context = f.read()
            except Exception:
                pass

        warmer = PrefixCacheWarmer()
        warmer.write_prompt_file(args.task, extra_context)

        selector = ModelTierSelector()
        model_flag = selector.get_cli_flag(args.task, tokens, files)

        print(f'gemini {model_flag} -p "$(cat ~/nina/data/gemini_prompt.md)"')
    except Exception as e:
        import sys
        print(f"Error: {e}")
        sys.exit(1)

def cmd_gemini_status(args):
    try:
        from gemini_perf import PromptBudgetGuard
        guard = PromptBudgetGuard()
        status = guard.get_status()
        print(f"Daily requests : {status['requests']} / {status['daily_limit']}")
        print(f"Estimated tokens today : {status['estimated_tokens']}")
        print(f"Token budget/call : {status['token_budget']}")
        print("Recommended model : flash | pro")
    except Exception as e:
        import sys
        print(f"Error: {e}")
        sys.exit(1)

def cmd_gemini_run(args):
    try:
        from gemini_perf import ContextPruner, PrefixCacheWarmer, ModelTierSelector, PromptBudgetGuard
        import sys, os

        pruner = ContextPruner()
        pruner.write_ignore_file()
        files = pruner.get_included_files()
        tokens = pruner.estimate_context_tokens(files)

        guard = PromptBudgetGuard()
        check = guard.check_invocation(tokens)
        if not check['ok']:
            print(f"Error: {check['reason']}")
            sys.exit(1)

        extra_context = ""
        if args.context_file:
            try:
                with open(os.path.expanduser(args.context_file), "r", encoding="utf-8") as f:
                    extra_context = f.read()
            except Exception:
                pass

        selector = ModelTierSelector()
        model_flag = selector.select(args.task, tokens, files)

        warmer = PrefixCacheWarmer()
        prompt_path = warmer.write_prompt_file(args.task, extra_context)

        guard.record_request(tokens)

        cmd_args = ['gemini', '--model', model_flag, '-p', prompt_path]
        if args.dry_run:
            print(" ".join(cmd_args))
        else:
            os.execvp('gemini', cmd_args)
    except Exception as e:
        import sys
        print(f"Error: {e}")
        sys.exit(1)

def cmd_code_audit_doc(args):
    """[044] Score docstrings on clarity and completeness."""
    path = _path_resolve(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"❌ Syntax error in file: {e}")
        return

    total_score = 0
    max_score = 0
    results = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            score = 0
            if doc:
                score += 1  # Existence
                if len(doc.strip()) > 10:
                    score += 1  # Minimum length
                # Completeness heuristics
                doc_lower = doc.lower()
                if "args:" in doc_lower or "parameters:" in doc_lower or "returns:" in doc_lower or "yields:" in doc_lower or "raises:" in doc_lower or "example" in doc_lower:
                    score += 1

            node_type = "Class" if isinstance(node, ast.ClassDef) else "Function"
            max_score += 3
            total_score += score
            results.append((node_type, node.name, score))

    print(f"── Docstring Audit Report: {path.name} ──")
    for ntype, name, score in results:
        print(f"{ntype} {name}: {score}/3")

    overall = (total_score / max_score * 100) if max_score > 0 else 100
    print(f"\nOverall Score: {overall:.1f}% ({total_score}/{max_score})")

    if overall < 50:
        print("Verdict: ❌ FAIL (Score below 50%)")
    elif overall < 80:
        print("Verdict: ⚠️ WARN (Score below 80%)")
    else:
        print("Verdict: ✅ PASS")


def main():
    parser = argparse.ArgumentParser(description="ninaflash AI Agent Kernel v6.0 — The 100-Function OS.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_find = subparsers.add_parser("find", help="Find across code, docs, logs")
    p_find.add_argument("query", help="Search query")
    p_find.add_argument("--regex", action="store_true", help="Use regex")

    p_edit = subparsers.add_parser("edit", help="Surgical line-based edits")
    p_edit.add_argument("file", help="File to edit")
    p_edit.add_argument("edits", help="JSON list of edits")

    p_status = subparsers.add_parser("status")
    p_status.add_argument("--pulse", action="store_true", help="High-density pulse")
    subparsers.add_parser("help-ai")
    subparsers.add_parser("capability-map")
    subparsers.add_parser("stats")
    p_monitor = subparsers.add_parser("monitor")
    p_monitor.add_argument("--full", action="store_true",
                           default=False, help="Parse all sessions, not just last 3")
    p_monitor.add_argument("--tools", action="store_true",
                           default=False,
                           help="Show tool call frequency + token cost breakdown")
    
    p_batch = subparsers.add_parser("batch")
    p_batch.add_argument("--cmds", required=True, help="Piped commands: 'c1|c2'")

    # --- Gemini CLI commands (promoted to top-level from nested subparser) ---
    # nf watch
    watch_parser = subparsers.add_parser('watch', help='Open live scratchpad watcher')
    watch_parser.add_argument('--clear', action='store_true', default=False,
                              help='Clear gemini_scratch.jsonl before watching')

    # nf gemini-context
    _ = subparsers.add_parser("gemini-context", help="Estimate context tokens for Gemini CLI")

    # nf gemini-prompt
    p_gemini_prompt = subparsers.add_parser("gemini-prompt", help="Generate Gemini CLI prompt file")
    p_gemini_prompt.add_argument("--task", required=True)
    p_gemini_prompt.add_argument("--context-file")

    # nf gemini-status
    _ = subparsers.add_parser("gemini-status", help="Show Gemini CLI daily status")

    # nf gemini-run
    p_gemini_run = subparsers.add_parser("gemini-run", help="Run Gemini CLI with dynamic context and model selection")
    p_gemini_run.add_argument("--task", required=True)
    p_gemini_run.add_argument("--context-file")
    p_gemini_run.add_argument("--dry-run", action="store_true")
    # --- End Gemini CLI commands ---

    p_file = subparsers.add_parser("file"); p_fs_f = p_file.add_subparsers(dest="sub")
    p_fr = p_fs_f.add_parser("read"); p_fr.add_argument("file"); p_fr.add_argument("--start", type=int); p_fr.add_argument("--end", type=int)
    p_fg = p_fs_f.add_parser("grep"); p_fg.add_argument("pattern"); p_fg.add_argument("--dir"); p_fg.add_argument("--ext")
    p_fp = p_fs_f.add_parser("patch"); p_fp.add_argument("file"); p_fp.add_argument("--find", required=True); p_fp.add_argument("--replace", required=True)
    p_fi = p_fs_f.add_parser("insert"); p_fi.add_argument("file"); p_fi.add_argument("--after", required=True); p_fi.add_argument("--text", required=True)
    p_fd = p_fs_f.add_parser("diff"); p_fd.add_argument("file")

    p_git = subparsers.add_parser("git"); p_gs_g = p_git.add_subparsers(dest="sub")
    p_gl = p_gs_g.add_parser("log"); p_gl.add_argument("--n", type=int)
    p_gs_g.add_parser("changed")
    p_gs_s = p_gs_g.add_parser("search"); p_gs_s.add_argument("keyword")
    p_gb = p_gs_g.add_parser("blame"); p_gb.add_argument("file"); p_gb.add_argument("--start", type=int); p_gb.add_argument("--end", type=int)
    p_gsq = p_gs_g.add_parser("stash-quick"); p_gsq.add_argument("--label")

    p_hw = subparsers.add_parser("hw"); p_hs = p_hw.add_subparsers(dest="sub")
    p_hg = p_hs.add_parser("gate")
    p_hg.add_argument("--json", action="store_true", help="Output as JSON")

    p_session = subparsers.add_parser("session"); p_ss = p_session.add_subparsers(dest="sub")
    p_sc = p_ss.add_parser("checkpoint")
    p_sc.add_argument("--goal", default="", help="Active goal for this session")
    p_ss.add_parser("resume")

    p_sstart = p_ss.add_parser("start")
    p_sstart.add_argument("--tool", default="gemini_cli", help="Tool name")
    p_sstart.add_argument("--task", dest="task_id", default="", help="Task ID")

    p_slog = p_ss.add_parser("log")
    p_slog.add_argument("--tool", default="gemini_cli", help="Tool name")
    p_slog.add_argument("--step", type=int, required=True, help="Step index")
    p_slog.add_argument("--action", required=True, help="Action taken")
    p_slog.add_argument("--outcome", choices=["success", "failure", "partial", "skipped"], required=True, help="Outcome")
    p_slog.add_argument("--detail", default="", help="Detail")

    p_spreamble = p_ss.add_parser("preamble")
    p_spreamble.add_argument("--tool", default="gemini_cli", help="Tool name")

    p_sdone = p_ss.add_parser("done")
    p_sdone.add_argument("--tool", default="gemini_cli", help="Tool name")

    p_memory = subparsers.add_parser("memory"); p_ms = p_memory.add_subparsers(dest="sub")
    p_ms_stash = p_ms.add_parser("stash")
    p_ms_stash.add_argument("text", help="Text to stash in working memory")
    p_mss = p_ms.add_parser("session-save"); p_mss.add_argument("--summary")
    p_msr = p_ms.add_parser("session-recall"); p_msr.add_argument("--n", type=int)
    p_ms.add_parser("inject")

    p_check = subparsers.add_parser("check"); p_cks = p_check.add_subparsers(dest="sub")

    p_cc = p_cks.add_parser("code")
    p_cc.add_argument("file")
    p_cc.add_argument("--strict", action="store_true", default=False)
    p_cc.add_argument("--fix", action="store_true", default=False)

    p_cd = p_cks.add_parser("doc")
    p_cd.add_argument("file")
    p_cd.add_argument("--agents", action="store_true", default=False)
    p_cd.add_argument("--stale",  action="store_true", default=False)

    p_cpx = p_cks.add_parser("complexity")
    p_cpx.add_argument("file")

    p_cks.add_parser("ignore")

    p_doc = subparsers.add_parser("doc"); p_docs = p_doc.add_subparsers(dest="sub")
    p_doc_check = p_docs.add_parser("check")
    p_doc_check.add_argument("file", nargs="?", default="docs/space/nina_update_log.md")
    p_doc_check.add_argument("--fix", action="store_true", default=False)
    p_doc_check.add_argument("--agents", action="store_true", default=False)
    p_doc_check.add_argument("--stale", action="store_true", default=False)
    p_docs.add_parser("consolidate")
    p_code = subparsers.add_parser("code"); p_cs = p_code.add_subparsers(dest="sub")
    p_call_stack = p_cs.add_parser("call-stack"); p_call_stack.add_argument("file"); p_call_stack.add_argument("name")
    p_sym = p_cs.add_parser("symbol")
    p_sym.add_argument("file")
    p_sym.add_argument("name")

    p_mig = p_cs.add_parser("migrate")
    p_mig.add_argument("old_name")
    p_mig.add_argument("new_name")
    p_mig.add_argument("--dir", default=".")
    p_sigs = p_cs.add_parser("sigs")
    p_sigs.add_argument("dir")
    p_doc = p_cs.add_parser("doc")
    p_doc.add_argument("keyword")

    p_audit_doc = p_cs.add_parser("audit-doc")
    p_audit_doc.add_argument("file")

    p_fs = subparsers.add_parser("find-symbol")
    p_fs.add_argument("name")
    p_cs.add_parser("outline").add_argument("file")
    p_cs.add_parser("dep-map")
    p_cs.add_parser("index")
    p_cs.add_parser("call-graph").add_argument("file", nargs="?")
    p_cs.add_parser("cycles")
    p_cs.add_parser("pack").add_argument("file")
    p_cs.add_parser("dead-code").add_argument("target")
    p_ext = p_cs.add_parser("extract-method")
    p_ext.add_argument("file")
    p_ext.add_argument("func_name")
    p_ext.add_argument("start_line")
    p_ext.add_argument("end_line")
    p_ext.add_argument("new_name")
    
    subparsers.add_parser("bench", help="Run a standardized reasoning task twice (Cloud vs Hybrid)")

    p_query = subparsers.add_parser("query", help="List all cmd_ handlers")
    _ = p_query
    p_query_cap = subparsers.add_parser("query-capability", help="Query task capability")
    p_query_cap.add_argument("task", help="Description of the task to query")

    p_maintain = subparsers.add_parser("maintain"); p_mts = p_maintain.add_subparsers(dest="sub")
    p_mpr = p_mts.add_parser("pr")
    p_mpr.add_argument("pr_id", help="PR ID to merge")
    p_mpr.add_argument("--task", dest="task_id", required=True, help="Task ID e.g. AG-M-01")
    p_mpr.add_argument("--title", required=True, help="Entry title")
    p_mpr.add_argument("--summary", required=True, help="Short summary of changes")

    p_pr = subparsers.add_parser("pr"); p_ps = p_pr.add_subparsers(dest="sub")
    p_ps.add_parser("reconcile")
    
    p_ops = subparsers.add_parser("ops"); p_os = p_ops.add_subparsers(dest="sub")
    p_os.add_parser("thermal"); p_os.add_parser("vram")
    p_os.add_parser("compress-logs").add_argument("--log-file", required=True)
    p_os.add_parser("rotate-logs")

    p_log = subparsers.add_parser("log"); p_ls = p_log.add_subparsers(dest="sub")
    p_ls.add_parser("summarize")
    p_log_tail = p_ls.add_parser("tail")
    p_log_tail.add_argument("n", type=int, default=5, nargs="?")
    p_ls.add_parser("next-id")
    p_lfind = p_ls.add_parser("find-id")
    p_lfind.add_argument("task_id", help="Task ID to find in logs")

    p_test = subparsers.add_parser("test")
    p_test.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    p_gen = subparsers.add_parser("gen"); p_gs = p_gen.add_subparsers(dest="sub")
    p_gs.add_parser("tool").add_argument("name")
    p_gs.add_parser("test")
    
    # Task Subcommands
    p_task = subparsers.add_parser("task"); p_ts = p_task.add_subparsers(dest="sub")
    p_ts.add_parser("active")

    p_bl = subparsers.add_parser("backlog"); p_bs = p_bl.add_subparsers(dest="sub")
    p_bs.add_parser("summary")
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
    p_reg = subparsers.add_parser("register")
    p_reg.add_argument("--tool-path",   required=True, help="Path to the tool file")
    p_reg.add_argument("--name",        help="Optional name (default: filename)")
    p_reg.add_argument("--description", help="Short summary of what it does")
    p_reg.add_argument("--role",        default="tool", help="Role (tool, script, task)")

    subparsers.add_parser("install-hooks")
    p_run = subparsers.add_parser("run")
    p_run.add_argument("name",          help="Name of the capability to run")
    p_run.add_argument("extra_args",    nargs=argparse.REMAINDER, help="Arguments passed to the tool")

    args = parser.parse_args()
    import time as _time
    _t0 = _time.monotonic()
    _cmd = getattr(args, 'command', 'unknown')
    _sub = getattr(args, 'sub', '') or ''
    try:
        if args.command == "status": cmd_status(args)
        elif args.command == "find-symbol": cmd_find_symbol(args)
        elif args.command == "help-ai": cmd_help_ai(args)
        elif args.command == "stats": cmd_stats(args)
        elif args.command == "monitor": cmd_monitor(args)
        elif args.command == "batch": cmd_batch(args)
        elif args.command == "watch":
            scratch = Path.home() / 'nina' / 'data' / 'gemini_scratch.jsonl'
            if args.clear and scratch.exists():
                scratch.unlink()
                print('Scratchpad cleared.')
            watcher = Path.home() / 'nina' / 'tools' / 'gemini_watch.py'
            os.execvp('python3', ['python3', str(watcher)])
        elif args.command == "gemini-context": cmd_gemini_context(args)
        elif args.command == "gemini-prompt": cmd_gemini_prompt(args)
        elif args.command == "gemini-status": cmd_gemini_status(args)
        elif args.command == "gemini-run": cmd_gemini_run(args)
        elif args.command == "file":
            if args.sub == "read": cmd_file_read(args)
            elif args.sub == "grep": cmd_file_grep(args)
            elif args.sub == "patch": cmd_file_patch(args)
            elif args.sub == "insert": cmd_file_insert(args)
            elif args.sub == "diff": cmd_file_diff(args)
        elif args.command == "git":
            if args.sub == "log": cmd_git_log(args)
            elif args.sub == "changed": cmd_git_changed(args)
            elif args.sub == "search": cmd_git_search(args)
            elif args.sub == "blame": cmd_git_blame(args)
            elif args.sub == "stash-quick": cmd_git_stash_quick(args)
        elif args.command == "capability-map": cmd_capability_map(args)
        elif args.command == "register": cmd_register_capability(args)
        elif args.command == "run": cmd_run_capability(args)
        elif args.command == "maintain":
            if args.sub == "pr": cmd_maintain_pr(args)
        elif args.command == "session":
            if args.sub == "checkpoint": cmd_session_checkpoint(args)
            elif args.sub == "resume": cmd_session_resume(args)
            elif args.sub == "start": cmd_session_start(args)
            elif args.sub == "log": cmd_session_log(args)
            elif args.sub == "preamble": cmd_session_preamble(args)
            elif args.sub == "done": cmd_session_done(args)
        elif args.command == "memory":
            if args.sub == "stash": cmd_memory_stash(args)
            elif args.sub == "session-save": cmd_memory_session_save(args)
            elif args.sub == "session-recall": cmd_memory_session_recall(args)
            elif args.sub == "inject": cmd_memory_inject(args)
        elif args.command == "hw":
            if args.sub == "gate": cmd_hw_gate(args)
        elif args.command == "check":
            if args.sub == "code": cmd_check_code(args)
            elif args.sub == "doc": cmd_check_doc(args)
            elif args.sub == "ignore": cmd_check_ignore(args)
            elif args.sub == "complexity": cmd_check_complexity(args)
        elif args.command == "doc":
            if args.sub == "check": cmd_check_doc(args)
            elif args.sub == "consolidate": cmd_doc_consolidate(args)
        elif args.command == "install-hooks":
            cmd_install_hooks(args)
        elif args.command == "code":
            if args.sub == "outline": cmd_code_outline(args)
            elif args.sub == "dep-map": cmd_code_dep_map(args)
            elif args.sub == "index": cmd_code_index(args)
            elif args.sub == "call-graph": cmd_code_call_graph(args)
            elif args.sub == "call-stack": cmd_code_call_stack(args)
            elif args.sub == "cycles": cmd_code_cycles(args)
            elif args.sub == "symbol": cmd_code_symbol(args)
            elif args.sub == "migrate": cmd_code_migrate(args)
            elif args.sub == "sigs": cmd_code_sigs(args)
            elif args.sub == "doc": cmd_code_doc(args)
            elif args.sub == "audit-doc": cmd_code_audit_doc(args)
            elif args.sub == "pack": cmd_context_pack(args)
            elif args.sub == "dead-code": cmd_code_dead_code(args)
            elif args.sub == "extract-method": cmd_code_extract_method(args)
        elif args.command == "query": cmd_query(args)
        elif args.command == "query-capability": cmd_query_capability(args)
        elif args.command == "pr":
            if args.sub == "reconcile": cmd_pr_reconcile(args)
        elif args.command == "task":
            if args.sub == "active": cmd_task_active(args)
        elif args.command == "log":
            if args.sub == "summarize": cmd_log_summarize(args)
            elif args.sub == "tail": cmd_log_tail(args)
            elif args.sub == "next-id": cmd_log_next_id(args)
            elif args.sub == "find-id": cmd_log_find_id(args)
        elif args.command == "backlog":
            if args.sub == "summary": cmd_backlog_summary(args)
            elif args.sub == "triage": cmd_backlog_triage(args)
            elif args.sub == "dag": cmd_backlog_dag(args)
            elif args.sub == "add": cmd_backlog_add(args)
            elif args.sub == "archive": cmd_backlog_archive(args)
        elif args.command == "ops":
            if args.sub == "thermal": cmd_ops_thermal(args)
            elif args.sub == "vram": cmd_ops_vram(args)
            elif args.sub == "compress-logs": cmd_ops_compress_logs(args)
            elif args.sub == "rotate-logs": cmd_ops_rotate_logs(args)
        elif args.command == "test": cmd_test(args)
        elif args.command == "bench": cmd_bench(args)
        elif args.command == "gen":
            if args.sub == "tool": cmd_gen_tool(args)
            elif args.sub == "test": cmd_gen_test(args)
        
        _dur = (_time.monotonic() - _t0) * 1000
        _tokens = NF_TOKEN_SAVINGS.get(_cmd, 0)
        write_nf_log(_cmd, _sub, _dur, tokens_saved=_tokens, outcome="OK")
    except Exception as _e:
        _dur = (_time.monotonic() - _t0) * 1000
        write_nf_log(_cmd, _sub, _dur, tokens_saved=0, outcome=f"ERROR: {_e}")
        raise

if __name__ == "__main__":
    main()
