#!/usr/bin/env python3
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
REGISTER_PATH = REPO_ROOT / "docs/space/nina_error_register.md"

PATTERNS = [
    re.compile(r'#\s*(TODO|FIXME|HACK|BUG|BROKEN)\s*:\s*(.*)', re.IGNORECASE),
    re.compile(r'#\s*(TODO|FIXME|HACK|BUG|BROKEN)\s+(.*)', re.IGNORECASE)
]

def scan_codebase():
    todos = []
    # Scan all .py files recursively, excluding ignore directories
    for path in REPO_ROOT.rglob("*.py"):
        parts = path.relative_to(REPO_ROOT).parts
        if any(p in parts for p in (".venv", "venv", "env", ".git", ".pytest_cache", "__pycache__", "upgrades", "node_modules", "dist", "build")):
            continue
            
        rel_path = str(path.relative_to(REPO_ROOT))
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
            
        for idx, line in enumerate(content.splitlines(), 1):
            for pat in PATTERNS:
                m = pat.search(line)
                if m:
                    tag = m.group(1).upper()
                    text = m.group(2).strip()
                    # Clean text to avoid breaking markdown table
                    text = text.replace("|", "\\|")
                    todos.append({
                        "file": rel_path,
                        "line": idx,
                        "tag": tag,
                        "text": f"[{tag}] {text}",
                        "id": f"todo.{rel_path.replace('/', '_').replace('.', '_')}_{idx}"
                    })
                    break
    return todos

def sync_register():
    if not REGISTER_PATH.exists():
        print(f"Error Register not found at {REGISTER_PATH}")
        return
        
    current_todos = scan_codebase()
    todo_ids = {t["id"]: t for t in current_todos}
    
    lines = REGISTER_PATH.read_text(encoding="utf-8").splitlines()
    new_lines = []
    
    updated_ids = set()
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 9:
                entry_id = parts[1]
                if entry_id.startswith("todo."):
                    updated_ids.add(entry_id)
                    if entry_id in todo_ids:
                        if "FIXED" in parts[5] or "✅" in parts[5]:
                            line = line.replace("✅ FIXED", "🔵 OPEN/PENDING")
                        new_lines.append(line)
                    else:
                        if "🔵 OPEN/PENDING" in line or "OPEN" in parts[5]:
                            line = line.replace("🔵 OPEN/PENDING", "✅ FIXED")
                        new_lines.append(line)
                    continue
        new_lines.append(line)
        
    new_todos_added = 0
    last_table_idx = -1
    for i, line in enumerate(new_lines):
        if "|" in line:
            last_table_idx = i
            
    for t in current_todos:
        if t["id"] not in updated_ids:
            component = t["file"].split("/")[0] if "/" in t["file"] else "core"
            new_row = f"| {t['id']} | 🟡 DEBT | {component} | {t['text']} | 🔵 OPEN/PENDING | unassigned | — | {t['file']} |"
            if last_table_idx != -1:
                new_lines.insert(last_table_idx + 1, new_row)
                last_table_idx += 1
            else:
                new_lines.append(new_row)
            new_todos_added += 1
            
    # Fix trailing status column: FIXED rows -> CLOSED, OPEN rows -> OPEN
    fixed_lines = []
    for line in new_lines:
        if line.startswith('|') and '|' in line:
            cols = line.split('|')
            if len(cols) >= 12:
                severity_col = cols[2].strip()
                status_col   = cols[6].strip()
                is_fixed = ('✅ FIXED' in severity_col or 'CLOSED' in status_col or '✅ FIXED' in status_col)
                cols[-2] = ' CLOSED ' if is_fixed else ' OPEN '
                line = '|'.join(cols)
        fixed_lines.append(line)
    REGISTER_PATH.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")
    print(f"Sync complete. Added {new_todos_added} new TODOs.")

if __name__ == "__main__":
    sync_register()

# ── Auto-close reconciliation (appended by NINA enhancement patch) ────────────
# NINA_FEATURE: error-register-autoclose v1.0

import re as _re
from datetime import datetime as _dt

def autoclose_resolved_errors(register_path, guardian_findings: list):
    """
    Walk nina_error_register.md; mark any open error as [RESOLVED] if its
    signature ID is no longer in the current guardian findings list.
    Only closes entries that have a matching <!-- sig:ID --> HTML comment marker.
    """
    path = Path(register_path)
    if not path.exists():
        return 0

    text = path.read_text()
    finding_ids = {f["id"] for f in guardian_findings}
    lines = text.splitlines()
    new_lines = []
    closed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        sig_match = _re.search(r'<!-- sig:([\w.]+) -->', line)
        if sig_match:
            sig_id = sig_match.group(1)
            # Look for open status marker in next 5 lines
            for j in range(i, min(i + 6, len(lines))):
                if '**Status:** OPEN' in lines[j] and sig_id not in finding_ids:
                    lines[j] = lines[j].replace(
                        '**Status:** OPEN',
                        f'**Status:** RESOLVED <!-- auto-closed {_dt.now().strftime("%Y-%m-%d %H:%M")} -->'
                    )
                    closed += 1
                    break
        new_lines.append(line)
        i += 1

    if closed:
        path.write_text('\n'.join(new_lines))
        print(f"[error_register_sync] Auto-closed {closed} resolved error(s).")
    return closed

# ── Auto-close reconciliation (appended by NINA enhancement patch) ────────────
# NINA_FEATURE: error-register-autoclose v1.0

import re as _re
from datetime import datetime as _dt

def autoclose_resolved_errors(register_path, guardian_findings: list):
    """
    Walk nina_error_register.md; mark any open error as [RESOLVED] if its
    signature ID is no longer in the current guardian findings list.
    Only closes entries that have a matching <!-- sig:ID --> HTML comment marker.
    """
    path = Path(register_path)
    if not path.exists():
        return 0

    text = path.read_text()
    finding_ids = {f["id"] for f in guardian_findings}
    lines = text.splitlines()
    new_lines = []
    closed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        sig_match = _re.search(r'<!-- sig:([\w.]+) -->', line)
        if sig_match:
            sig_id = sig_match.group(1)
            # Look for open status marker in next 5 lines
            for j in range(i, min(i + 6, len(lines))):
                if '**Status:** OPEN' in lines[j] and sig_id not in finding_ids:
                    lines[j] = lines[j].replace(
                        '**Status:** OPEN',
                        f'**Status:** RESOLVED <!-- auto-closed {_dt.now().strftime("%Y-%m-%d %H:%M")} -->'
                    )
                    closed += 1
                    break
        new_lines.append(line)
        i += 1

    if closed:
        path.write_text('\n'.join(new_lines))
        print(f"[error_register_sync] Auto-closed {closed} resolved error(s).")
    return closed

# ── Auto-close reconciliation (appended by NINA enhancement patch) ────────────
# NINA_FEATURE: error-register-autoclose v1.0

import re as _re
from datetime import datetime as _dt

def autoclose_resolved_errors(register_path, guardian_findings: list):
    """
    Walk nina_error_register.md; mark any open error as [RESOLVED] if its
    signature ID is no longer in the current guardian findings list.
    Only closes entries that have a matching <!-- sig:ID --> HTML comment marker.
    """
    path = Path(register_path)
    if not path.exists():
        return 0

    text = path.read_text()
    finding_ids = {f["id"] for f in guardian_findings}
    lines = text.splitlines()
    new_lines = []
    closed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        sig_match = _re.search(r'<!-- sig:([\w.]+) -->', line)
        if sig_match:
            sig_id = sig_match.group(1)
            # Look for open status marker in next 5 lines
            for j in range(i, min(i + 6, len(lines))):
                if '**Status:** OPEN' in lines[j] and sig_id not in finding_ids:
                    lines[j] = lines[j].replace(
                        '**Status:** OPEN',
                        f'**Status:** RESOLVED <!-- auto-closed {_dt.now().strftime("%Y-%m-%d %H:%M")} -->'
                    )
                    closed += 1
                    break
        new_lines.append(line)
        i += 1

    if closed:
        path.write_text('\n'.join(new_lines))
        print(f"[error_register_sync] Auto-closed {closed} resolved error(s).")
    return closed
