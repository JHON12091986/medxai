#!/usr/bin/env python3
import os
import re
import sys
import subprocess
from datetime import datetime

# Define file paths
NINA_DIR = "/home/aibony/nina"
SPACE_DIR = os.path.join(NINA_DIR, "docs/space")
EXPORTS_DIR = os.path.join(NINA_DIR, "exports")
LOGS_DIR = os.path.join(NINA_DIR, "logs")
UPLOAD_DIR = "/home/aibony/Downloads/nina_space_upload"
OUTPUT_FILE = os.path.join(UPLOAD_DIR, "nina_latest.md")

os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_state_section(section_title):
    state_path = os.path.join(SPACE_DIR, "nina_state.md")
    if not os.path.exists(state_path):
        return f"_Section {section_title} missing from nina_state.md_"
    with open(state_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    pattern = re.compile(rf"^## {section_title}\n(.*?)(?=\n## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(content)
    if match:
        return match.group(1).strip()
    return f"_Section {section_title} not parsed._"

def get_service_status():
    try:
        status = subprocess.check_output(["systemctl", "--user", "is-active", "nina"], stderr=subprocess.DEVNULL).decode().strip()
        return status
    except Exception:
        try:
            status = subprocess.check_output(["systemctl", "is-active", "nina"], stderr=subprocess.DEVNULL).decode().strip()
            return status
        except Exception:
            return "unknown"

def get_header():
    branch = "main"
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=NINA_DIR).decode().strip()
    except Exception:
        pass
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    python_ver = sys.version.split()[0]
    
    header = f"""# NINA Operational AI Snapshot — {timestamp}
_Generated: {timestamp} | Repo: github.com/aibony/nina | Branch: {branch} | Python: {python_ver}_
_Purpose: AI context snapshot for Perplexity Space_
_Target size: Compact, low-noise context (~200KB-300KB)_

---

## SESSION START CHECKLIST (Perplexity)
Before opening a new Perplexity thread:
1. cd ~/nina && ./nina_sync.sh  (generates fresh nina_latest.md)
2. Attach: exports/nina_latest.md
3. Attach: the specific source file(s) to be discussed
4. State: task type — bug / feature / doc / security / review
5. Check: cat ~/nina/juleslock.txt — confirm no target files are locked

---
"""
    return header

def get_executive_snapshot():
    identity = get_state_section("Identity")
    arch = get_state_section("Architecture & Stack")
    providers = get_state_section("AI Providers & Quota")
    policy = get_state_section("NINA Tool Routing Policy v2 Summary")
    svc_status = get_service_status()
    
    snapshot = f"""## Executive Snapshot

### Identity & Deployment Summary
{identity}

### Core Architecture Summary
{arch}

### Tool Routing & Quota Strategy Summary
{providers}

### NINA Tool Routing Policy v2 Summary
{policy}

### High-Risk Files
- `interfaces/telegram_interface.py` (Telegram bot / security gate)
- `.env` (Secrets — NEVER commit, NEVER send to cloud)
- `core/router.py` (HybridRouter V4)
- `main.py` (Entry point)
- `guardian_engine.py` (Forensic engine)
- `tools/shell.py` (Allowlist-gated shell)

### Latest Verified Runtime Status
- **nina.service Status:** {svc_status}
"""
    return snapshot

def get_action_board():
    register_path = os.path.join(SPACE_DIR, "nina_error_register.md")
    if not os.path.exists(register_path):
        return "## Current Action Board\n\n_nina_error_register.md not found._\n"
        
    with open(register_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    blockers, warnings, debts, features = [], [], [], []
    
    # Parse markdown table
    for line in lines:
        if not line.startswith("|") or line.strip().startswith("|----") or line.strip().startswith("| ID "):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 5:
            continue
        
        severity = parts[1]
        status = parts[4]
        
        if status.upper() not in ["OPEN", "OPEN/PENDING", "IN-PROGRESS", "IN PROGRESS"]:
            continue
            
        if "BLOCKER" in severity.upper() or "🔴" in severity:
            blockers.append(line)
        elif "WARN" in severity.upper() or "🟠" in severity:
            warnings.append(line)
        elif "DEBT" in severity.upper() or "🟡" in severity:
            debts.append(line)
        else:
            features.append(line)
            
    header_row = "| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |\n|----|----------|-----------|---------------|--------|----------|----------|---------|\n"
    
    action_board = f"""## Current Action Board

### Summary Counts
- **🔴 BLOCKER:** {len(blockers)}
- **🟠 WARN:** {len(warnings)}
- **🟡 DEBT:** {len(debts)}
- **🔵 FEATURE/PENDING:** {len(features)}

"""
    if blockers:
        action_board += "#### 🔴 BLOCKER\n" + header_row + "".join(blockers) + "\n"
    if warnings:
        action_board += "#### 🟠 WARN\n" + header_row + "".join(warnings) + "\n"
    if debts:
        action_board += "#### 🟡 DEBT\n" + header_row + "".join(debts) + "\n"
    if features:
        action_board += "#### 🔵 FEATURE/PENDING\n" + header_row + "".join(features) + "\n"
        
    return action_board

def get_roadmap():
    phase = get_state_section("Current Phase & Next Task")
    milestones = get_state_section("Open Milestones")
    confidence = get_state_section("Action Board Confidence")
    
    content = f"""## Current Phase & Roadmap

### Current Stage & Next Task
{phase}

### Open Milestones
{milestones}

### Action Board Confidence
{confidence}
"""
    return content

def get_recent_changes():
    log_path = os.path.join(NINA_DIR, "nina_update_log.md")
    if not os.path.exists(log_path):
        return "## Recent Meaningful Changes\n\n_nina_update_log.md not found._\n"
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by Entry
    pattern = re.compile(r"^## Entry (\d+)", re.MULTILINE)
    matches = list(pattern.finditer(content))
    
    entries = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        entry_text = content[start:end].strip()
        if entry_text.endswith("---"):
            entry_text = entry_text[:-3].strip()
        entries.append(entry_text)
        
    meaningful_count = 0
    skipped_sync_count = 0
    recent_entries = []
    
    for entry in reversed(entries):
        first_line = entry.split("\n")[0]
        if "D-sync Post-session sync" in first_line:
            skipped_sync_count += 1
            continue
        
        if meaningful_count < 10:
            recent_entries.append(entry)
            meaningful_count += 1
        else:
            break
            
    recent_entries.reverse()
    
    changes = "## Recent Meaningful Changes\n\n"
    changes += "\n\n---\n\n".join(recent_entries)
    changes += f"\n\n---\n\n_Note: {skipped_sync_count} automated sync runs omitted; no material policy or architecture change._\n"
    return changes

def get_agents_rules():
    agents_path = os.path.join(NINA_DIR, "AGENTS.md")
    if not os.path.exists(agents_path):
        return "## Key Rules for Future Patches\n\n_AGENTS.md not found._\n"
    with open(agents_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    rules = "## Key Rules for Future Patches\n\n"
    match = re.search(r"## Rules for Jules.*", content, re.DOTALL)
    if match:
        rules += match.group(0)
    else:
        rules += content
    return rules

def get_file_summary(rel_path):
    abs_path = os.path.join(NINA_DIR, rel_path)
    if not os.path.exists(abs_path):
        return f"### `{rel_path}`\n_Status: File not found / does not exist yet._\n"
        
    with open(abs_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if len(lines) < 120 or rel_path.endswith(".sh") or rel_path.endswith(".txt") or rel_path.endswith(".json"):
        ext = rel_path.split(".")[-1]
        lang = "python" if ext == "py" else ("bash" if ext == "sh" else ext)
        code = "".join(lines)
        return f"### `{rel_path}`\n\n```{lang}\n{code}\n```\n"
        
    summary_lines = []
    
    # Extract docstring if present
    in_docstring = False
    docstring_lines = []
    for line in lines[:20]:
        strip_line = line.strip()
        if strip_line.startswith('"""') or strip_line.startswith("'''"):
            if in_docstring:
                docstring_lines.append(line)
                break
            else:
                in_docstring = True
                docstring_lines.append(line)
        elif in_docstring:
            docstring_lines.append(line)
            
    if docstring_lines:
        summary_lines.append("#### Docstring\n" + "".join(docstring_lines).strip() + "\n")
        
    # Extract imports
    imports = []
    for line in lines:
        if line.startswith("import ") or line.startswith("from "):
            imports.append(line.strip())
    if imports:
        summary_lines.append("#### Imports\n```python\n" + "\n".join(imports) + "\n```\n")
        
    # Extract classes and methods
    classes_and_methods = []
    for line in lines:
        strip_line = line.strip()
        if line.startswith("class "):
            classes_and_methods.append(line.rstrip())
        elif line.startswith("def "):
            classes_and_methods.append(line.rstrip())
        elif strip_line.startswith("def ") and (line.startswith("    ") or line.startswith("\t")):
            classes_and_methods.append("  " + strip_line)
            
    if classes_and_methods:
        summary_lines.append("#### Classes & Signatures\n```python\n" + "\n".join(classes_and_methods) + "\n```\n")
        
    summary = f"### `{rel_path}` (Compact Signatures Summary)\n\n"
    summary += "\n".join(summary_lines)
    return summary

def get_code_context():
    files_to_export = [
        "core/router.py",
        "core/agent.py",
        "core/nina.py",
        "core/config.py",
        "core/memory.py",
        "core/hotreload.py",
        "interfaces/telegram_interface.py",
        "tools/shell.py",
        "tools/browser.py",
        "tools/upgradepipeline.py",
        "tools/finance.py",
        "tools/market.py",
        "tools/officemail.py",
        "crons/manager.py",
        "guardian_engine.py",
        "main.py",
        "nina_sync.sh"
    ]
    
    context = "## Targeted Code Context\n\n"
    for rel in files_to_export:
        context += get_file_summary(rel) + "\n---\n\n"
    return context

def get_appendix():
    appendix = """## Appendix Pointers

- **Full Update Log Archive:** `exports/nina_update_log_archive_2026-05.md` (Contains the history of entries 001 to 093)
- **Full Error Register Archive:** `exports/nina_error_register_archive.md` (Contains all historically FIXED entries)
- **Exports Directory:** `exports/` (Contains backups and problem log archives)
- **Handoff/Baseline Configurations:** `upgrades/.guardian_handoff.json` and `upgrades/guardian_baseline.json`
"""
    return appendix

def main():
    parts = [
        get_header(),
        get_executive_snapshot(),
        get_action_board(),
        get_roadmap(),
        get_recent_changes(),
        get_agents_rules(),
        get_code_context(),
        get_appendix()
    ]
    
    full_output = "\n\n".join(parts)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_output)
        
    print(f"Compact snapshot created: {OUTPUT_FILE}")
    size = os.path.getsize(OUTPUT_FILE)
    print(f"File size: {size} bytes")
    
    # Validation block
    mandatory_strings = [
        "ARCHITECT",
        "ASYNC CLOUD CODER",
        "LOCAL MUSCLE",
        "Local Executor as Merge Executor",
        "The Full Parallel Loop",
        "BLOCKER",
        "Guardian Gate"
    ]
    for string in mandatory_strings:
        if string not in full_output:
            print(f"WARNING: nina_latest.md missing section: \"{string}\"")

if __name__ == "__main__":
    main()
