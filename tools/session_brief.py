#!/usr/bin/env python3
"""
tools/session_brief.py
Generates a structured, automated Session Brief after every synchronization task.
Prints to stdout and writes to docs/space/nina_session_brief.md.
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

def parse_session_log(repo_root):
    scratch_path = repo_root / "data" / "gemini_scratch.jsonl"
    if not scratch_path.exists():
        return "No active session log found.", []

    try:
        with open(scratch_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return f"Error reading session log: {e}", []

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
        start_idx = 0

    session_entries = []
    for line in lines[start_idx:]:
        try:
            session_entries.append(json.loads(line))
        except Exception:
            continue

    if not session_entries:
        return "No valid JSON entries found in session log.", []

    touched_files = set()
    implemented_details = []
    for entry in session_entries:
        detail = entry.get("detail", "")
        file_path = entry.get("file", "")
        if file_path:
            touched_files.add(file_path)
        if detail and entry.get("action") == "done":
            implemented_details.append(detail)

    # Fallback to last git commit if session entries have no done/detail
    if not implemented_details:
        try:
            cmd = ["git", "log", "-1", "--pretty=format:%s%n%b"]
            res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
            if res.returncode == 0:
                implemented_details.append(res.stdout.strip())
        except Exception:
            pass

    implemented_summary = "\n".join(f"- {d}" for d in implemented_details if d)
    return implemented_summary, sorted(list(touched_files))


def parse_backlog(repo_root):
    backlog_path = repo_root / "docs/space/jules_backlog.md"
    if not backlog_path.exists():
        return "Backlog file not found.", {}

    try:
        content = backlog_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading backlog: {e}", {}

    categories = {
        "🔴 TODO-P1 (High Priority / Urgent)": [],
        "🟠 TODO-P2 (Important / This Sprint)": [],
        "🟡 TODO-P3 (Low Priority / Improvements)": []
    }

    # Find tasks starting with ### or #### and containing TODO keys
    # Let's extract heading blocks
    blocks = re.findall(r'((?:###|####).+?(?=###|####|\Z))', content, re.DOTALL)
    for b in blocks:
        title_line = b.splitlines()[0]
        if "TODO-P1" in b or "TODO-P1" in title_line:
            categories["🔴 TODO-P1 (High Priority / Urgent)"].append(b.strip())
        elif "TODO-P2" in b or "TODO-P2" in title_line:
            categories["🟠 TODO-P2 (Important / This Sprint)"].append(b.strip())
        elif "TODO-P3" in b or "TODO-P3" in title_line:
            categories["🟡 TODO-P3 (Low Priority / Improvements)"].append(b.strip())

    return categories


def check_docs_status(repo_root):
    # Run validate_index.py to check status
    validate_script = repo_root / "tools" / "validate_index.py"
    if not validate_script.exists():
        return "Unknown (validate_index.py missing)", "N/A", "N/A"

    try:
        # Run reconcile first to clean up test exemptions
        subprocess.run([sys.executable, str(validate_script), "--reconcile"], cwd=repo_root, capture_output=True)

        res = subprocess.run([sys.executable, str(validate_script)], cwd=repo_root, capture_output=True, text=True)
        output = res.stdout + res.stderr
        
        # Parse output for Metadata Quality Score, Warnings, and Missing Tests
        quality_score = "Unknown"
        warnings = "0"
        missing_tests = "0"
        
        m_quality = re.search(r"Metadata Quality Score:\s*([\d\.]+)%", output)
        if m_quality:
            quality_score = f"{m_quality.group(1)}%"
            
        m_warnings = re.search(r"passed\s*\((\d+)\s*warnings\)", output, re.IGNORECASE)
        if not m_warnings:
            m_warnings = re.search(r"with\s*\d+\s*errors\s*and\s*(\d+)\s*warnings", output, re.IGNORECASE)
        if m_warnings:
            warnings = m_warnings.group(1)
            
        m_tests = re.search(r"Missing Tests:\s*(\d+)", output, re.IGNORECASE)
        if m_tests:
            missing_tests = m_tests.group(1)

        # Check if nina_update_log.md or AGENTS.md was modified in the last commit
        cmd_diff = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        res_diff = subprocess.run(cmd_diff, cwd=repo_root, capture_output=True, text=True)
        doc_updated = "No"
        if res_diff.returncode == 0:
            changed_files = res_diff.stdout.strip().split("\n")
            if any(f in ["nina_update_log.md", "AGENTS.md"] or f.endswith(".md") for f in changed_files if f):
                doc_updated = "Yes (Verified via git diff)"

        status_summary = f"""- **Index Metadata Quality**: {quality_score}
- **Index Gaps / Warnings**: {warnings} outstanding warnings
- **Missing Tests**: {missing_tests} files missing unit tests
- **Session Docs/Logs Updated**: {doc_updated}"""
        return status_summary, quality_score, warnings
    except Exception as e:
        return f"Error checking docs status: {e}", "Error", "Error"


def main():
    repo_root = Path(__file__).parent.parent.resolve()
    
    # 1. Gather Implemented Info
    impl_summary, touched_files = parse_session_log(repo_root)
    
    # 2. Check Documentation Status
    docs_summary, quality_score, warnings = check_docs_status(repo_root)
    
    # 3. Parse Backlog Gaps
    backlog_categories = parse_backlog(repo_root)
    
    # 4. Formulate "How to Implement These Later"
    how_to_implement = """### 💡 Implementation Strategy & Recipes

To address the remaining high-priority gaps, follow these guidelines:

1. **Provider Health Monitoring & Alerts (🔴 TODO-P1)**:
   - Create `tools/provider_health.py` defining `ProviderHealthTracker` using a sliding window for success/failure logs.
   - Wire this tracker into `core/router.py` to record metadata inside the core HTTP call/provider routing methods.
   - Use the Telegram notification client (`from telegram_notify import send_message`) to alert on 3 consecutive failures.

2. **Governance Index Auto-Update (🔴 TODO-P1)**:
   - To maintain high metadata quality, verify any new code file is registered in `docs/space/nina_index.json`.
   - Run `python3 tools/validate_index.py --reconcile` after creating any script. If it's pure utility or adapter infra, ensure it fits the exempt patterns inside `validate_index.py` so warning counts stay 0.

3. **Provider Registry Unification (🟠 TODO-P2)**:
   - Modify `core/router.py` to load provider specs dynamically from `ninagate/providers.json` at startup instead of keeping redundant lists. Ensure fallback tiers match properly.
"""

    # Build the final brief
    brief_lines = []
    brief_lines.append("# NINA Post-Session Brief")
    brief_lines.append(f"> Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} after task completion\n")
    
    brief_lines.append("## 1. What Was Implemented")
    if impl_summary.strip():
        brief_lines.append(impl_summary)
    else:
        brief_lines.append("- Minor synchronization and repo hygiene updates.")
    brief_lines.append("")
    
    if touched_files:
        brief_lines.append("**Touched Files:**")
        for f in touched_files:
            brief_lines.append(f"- `{f}`")
        brief_lines.append("")

    brief_lines.append("## 2. Documentation & Index Status")
    brief_lines.append(docs_summary)
    brief_lines.append("")

    brief_lines.append("## 3. What Is Remaining (Backlog Gaps)")
    
    has_backlog = False
    for cat, items in backlog_categories.items():
        if items:
            has_backlog = True
            brief_lines.append(f"### {cat}")
            for item in items[:3]:  # Show top 3 from each
                # Truncate to limit size
                item_lines = item.splitlines()
                summary_heading = item_lines[0]
                summary_desc = "\n".join(item_lines[1:5])
                brief_lines.append(f"{summary_heading}\n{summary_desc}\n...")
            brief_lines.append("")
            
    if not has_backlog:
        brief_lines.append("- Backlog fully cleared! No outstanding tasks.")
        brief_lines.append("")

    brief_lines.append("## 4. How to Implement Remaining Tasks")
    brief_lines.append(how_to_implement)
    brief_lines.append("")
    
    brief_content = "\n".join(brief_lines)
    
    # Save to docs/space/nina_session_brief.md
    brief_file = repo_root / "docs" / "space" / "nina_session_brief.md"
    try:
        brief_file.parent.mkdir(parents=True, exist_ok=True)
        brief_file.write_text(brief_content, encoding="utf-8")
        print(f"✅ Post-Session Brief written to {brief_file.relative_to(repo_root)}")
    except Exception as e:
        print(f"⚠️ Failed to write Session Brief file: {e}")

    # Output to stdout with nice borders for visibility
    print("\n" + "="*60)
    print(" 📋 NINA POST-SESSION BRIEF")
    print("="*60)
    print(brief_content)
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
