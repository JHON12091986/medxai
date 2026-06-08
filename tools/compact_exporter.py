#!/usr/bin/env python3
import os
import re
import sys
import subprocess
from datetime import datetime
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Define file paths
NINA_DIR = Path("/home/aibony/nina")
SPACE_DIR = NINA_DIR / "docs/space"
UPLOAD_DIR = Path("/home/aibony/Downloads/nina_space_upload")

def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_git_short_sha():
    try:
        return subprocess.check_output(["git", "-C", str(NINA_DIR), "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def get_git_long_sha():
    try:
        return subprocess.check_output(["git", "-C", str(NINA_DIR), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def get_git_branch():
    try:
        return subprocess.check_output(["git", "-C", str(NINA_DIR), "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"

def get_state_section(section_title, max_lines=None, bullets_only=False):
    state_path = SPACE_DIR / "nina_state.md"
    if not state_path.exists():
        return f"_Section {section_title} missing_"
    
    content = state_path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^## {section_title}\n(.*?)(?=\n## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(content)
    if not match:
        return f"_Section {section_title} not found_"
    
    lines = match.group(1).strip().split('\n')
    if bullets_only:
        lines = [l for l in lines if l.strip().startswith(('-', '*', '1.'))]
    
    if max_lines:
        lines = lines[:max_lines]
        
    return '\n'.join(lines)

def export_summary():
    """Produces nina_latest.md (BAREBONES SUMMARY)"""
    sha = get_git_short_sha()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output = []
    output.append(f"# NINA Latest State | {ts} | Git: {sha}")
    
    output.append("\n## Identity")
    output.append(get_state_section("Identity", max_lines=4))
    
    output.append("\n## Current Phase + Next Task")
    output.append(get_state_section("Current Phase & Next Task", bullets_only=True))
    
    output.append("\n## Open Error Register")
    reg_path = SPACE_DIR / "nina_error_register.md"
    open_errors = []
    if reg_path.exists():
        reg_content = reg_path.read_text(encoding="utf-8")
        for line in reg_content.split('\n'):
            if '|' in line and 'OPEN' in line.upper():
                open_errors.append(line)
    
    if open_errors:
        output.append("| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |")
        output.append("|----|----------|-----------|---------------|--------|----------|----------|---------|")
        output.extend(open_errors)
    else:
        output.append("✅ No open errors")
        
    output.append("\n## Tool Routing Policy")
    policy = get_state_section("NINA Tool Routing Policy v2 Summary")
    # Extract only the 4-row table if possible, or just the summary
    table_match = re.search(r'(\|.*\|.*\n\|.*\|.*\n\|.*\|.*\n\|.*\|.*\n\|.*\|.*)', policy)
    if table_match:
        output.append(table_match.group(1))
    else:
        output.append(policy)
        
    output.append("\n## Active Milestones")
    output.append(get_state_section("Open Milestones", max_lines=3))
    
    output.append("\n## Key Paths")
    output.append(get_state_section("Key File Paths", max_lines=5))
    
    output.append(f"\n_Last sync: {ts}_")
    
    dest = UPLOAD_DIR / "nina_latest.md"
    dest.write_text('\n'.join(output), encoding="utf-8")
    print(f"Exported: {dest} ({dest.stat().st_size} bytes)")

def export_diff():
    """Produces nina_diff.md (LOCAL vs GITHUB DELTA)"""
    sha = get_git_short_sha()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output = []
    output.append(f"# NINA Local vs GitHub Diff\nGenerated: {ts}\nGit HEAD: {sha}\n")
    
    commands = [
        ("## Git Status", ["git", "-C", str(NINA_DIR), "status", "--short"]),
        ("## Unpushed Commits", ["git", "-C", str(NINA_DIR), "log", "origin/main..HEAD", "--oneline"]),
        ("## facts.json diff", ["git", "-C", str(NINA_DIR), "diff", "HEAD", "--", "data/memory/facts.json"]),
        ("## puter_architect.html diff", ["git", "-C", str(NINA_DIR), "diff", "HEAD", "--", "dashboard/puter_architect.html"]),
        ("## nina_dashboard.py diff", ["git", "-C", str(NINA_DIR), "diff", "HEAD", "--", "tools/nina_dashboard.py"]),
        ("## Files Changed Since Last Git Fetch", ["find", str(NINA_DIR), "-maxdepth", "4", "-newer", str(NINA_DIR / ".git/FETCH_HEAD"), 
                                                   "-not", "-path", "*/.git/*", "-not", "-path", "*/venv/*", "-not", "-path", "*/ninavenv/*", 
                                                   "-not", "-path", "*/__pycache__/*", "-not", "-name", "*.pyc", 
                                                   "-not", "-path", "*/exports/*", "-not", "-name", "*.bak"])
    ]
    
    for header, cmd in commands:
        output.append(header)
        try:
            res = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
            if not res:
                res = "(no changes)"
        except Exception as e:
            res = f"(error running command: {e})"
        
        output.append(f"```\n{res}\n```\n")
        
    dest = UPLOAD_DIR / "nina_diff.md"
    dest.write_text('\n'.join(output), encoding="utf-8")
    print(f"Exported: {dest} ({dest.stat().st_size} bytes)")

def export_full_backup():
    """Produces nina_full_backup_<YYYYMMDD_HHMMSS>.md (COMPLETE SNAPSHOT)"""
    sha = get_git_long_sha()
    branch = get_git_branch()
    ts_now = datetime.now()
    ts_str = ts_now.strftime("%Y-%m-%d %H:%M:%S")
    ts_file = ts_now.strftime("%Y%m%d_%H%M%S")
    
    inc_ext = {'.py', '.sh', '.md', '.txt', '.json', '.yml', '.yaml', '.cfg', '.ini', '.conf', '.service', '.html', '.css', '.js', '.env.example'}
    exc_paths = {'venv', 'ninavenv', '.venv', '.git', '__pycache__', 'exports', 'upgrades/backups', 'upgrades/incidents', 'node_modules', 'logs', 'data', 'tests'}
    exc_ext = {'.bak', '.fix', '.save', '.pyc', '.pyo', '.log'}
    exc_files = {'.env'}
    
    files_to_backup = []
    total_size = 0
    
    for root, dirs, files in os.walk(str(NINA_DIR)):
        rel_root = os.path.relpath(root, str(NINA_DIR))
        
        # Prune excluded paths
        if any(rel_root == p or rel_root.startswith(p + os.sep) for p in exc_paths):
            dirs[:] = [] # skip this directory
            continue
            
        for file in files:
            rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
            
            # Skip excluded paths in file walk if any (redundant but safe)
            if any(rel_path.startswith(p + os.sep) for p in exc_paths):
                continue
                
            path = Path(root) / file
            ext = path.suffix
            
            if ext in inc_ext and ext not in exc_ext and file not in exc_files:
                files_to_backup.append(path)
                
    # Sort order: .py -> .sh -> .md -> .json -> others. Alphabetical within.
    def sort_key(p):
        ext = p.suffix
        if ext == '.py': group = 0
        elif ext == '.sh': group = 1
        elif ext == '.md': group = 2
        elif ext == '.json': group = 3
        else: group = 4
        return (group, str(p.relative_to(NINA_DIR)))
        
    files_to_backup.sort(key=sort_key)
    
    output = []
    output.append(f"# NINA Complete Local Snapshot\nGenerated: {ts_str}\nGit HEAD: {sha}\nGit branch: {branch}")
    output.append(f"Total files captured: {{count}}\nTotal size: {{size}} bytes\n")
    output.append("⚠️  CONFIDENTIAL — full disaster recovery backup\n⚠️  .env excluded — restore secrets manually from secure vault\n\n---\n")
    
    captured_count = 0
    captured_size = 0
    
    for path in files_to_backup:
        rel_path = path.relative_to(NINA_DIR)
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = path.stat().st_size
            content = path.read_text(encoding="utf-8", errors="replace")
            
            output.append(f"## [N] {rel_path}\nLast modified: {mtime}\nSize: {size} bytes\n```\n{content}\n```\n")
            captured_count += 1
            captured_size += size
        except Exception as e:
            output.append(f"## [N] {rel_path}\n❌ READ ERROR: {e}\n")
            
    # Update header counts
    full_output = '\n'.join(output).replace("{count}", str(captured_count)).replace("{size}", str(captured_size))
    
    dest = UPLOAD_DIR / f"nina_full_backup_{ts_file}.md"
    dest.write_text(full_output, encoding="utf-8")
    print(f"Exported: {dest} ({dest.stat().st_size} bytes)")

def main():
    ensure_upload_dir()
    export_summary()
    export_diff()
    export_full_backup()

if __name__ == "__main__":
    main()
