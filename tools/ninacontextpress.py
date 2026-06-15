#!/usr/bin/env python3
"""
ninacontextpress.py — Zero-token rule-based context compressor for NINA.
Parses data/gemini_scratch.jsonl and produces data/session_checkpoint.md.
Detects session stalls and summarizes progress.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).parent.parent.resolve()
SCRATCH_LOG = REPO_ROOT / "data" / "gemini_scratch.jsonl"
CHECKPOINT_OUT = REPO_ROOT / "data" / "session_checkpoint.md"
TEST_REPORT = REPO_ROOT / "data" / "ninatestrunner_report.json"

class ContextCompressor:
    def __init__(self, task_file=None, cp_num=0):
        self.task_file = task_file
        self.cp_num = cp_num
        self.entries = self._load_entries()

    def _load_entries(self):
        if not SCRATCH_LOG.exists():
            return []
        entries = []
        with open(SCRATCH_LOG, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except:
                    continue
        return entries

    def detect_stall(self):
        if not self.entries:
            return None
        
        last_10 = self.entries[-10:]
        file_counts = {}
        for e in last_10:
            f = e.get("file")
            if f and not f.startswith("logs/"):
                file_counts[f] = file_counts.get(f, 0) + 1
                if file_counts[f] >= 3:
                    return f"STALL: File '{f}' accessed {file_counts[f]}x in last 10 steps."

        consecutive_errors = 0
        last_err = ""
        for e in self.entries:
            if e.get("action") == "error":
                curr_err = e.get("detail", "")
                if curr_err == last_err and curr_err:
                    consecutive_errors += 1
                else:
                    consecutive_errors = 1
                    last_err = curr_err
                if consecutive_errors >= 5:
                    return f"STALL: Same error repeated 5x: {last_err[:100]}"
            else:
                consecutive_errors = 0
                last_err = ""

        last_cp_idx = -1
        for i, e in enumerate(self.entries):
            if e.get("action") == "checkpoint":
                last_cp_idx = i
        
        steps_since_cp = len(self.entries) - (last_cp_idx + 1)
        if steps_since_cp > 30:
            return f"STALL: {steps_since_cp} steps since last checkpoint (limit: 30)."

        return None

    def _get_git_info(self):
        def run(cmd):
            try:
                import shlex
                if isinstance(cmd, str):
                    if "|" in cmd:
                        cmd = ["sh", "-c", cmd]
                    else:
                        cmd = shlex.split(cmd)
                return subprocess.check_output(cmd, shell=False, text=True, cwd=REPO_ROOT).strip()
            except:
                return "Unknown"
        
        branch = run("git branch --show-current")
        last_commit = run("git log -1 --oneline")
        changed = run("git diff --name-only HEAD")
        return branch, last_commit, changed

    def _parse_pytest_detail(self, detail):
        m = re.search(r"(\d+) passed", str(detail))
        passed = m.group(1) if m else "?"
        m = re.search(r"(\d+) failed", str(detail))
        failed = m.group(1) if m else "0"
        
        failed_ids = []
        if failed != "0":
            for line in str(detail).splitlines():
                if line.startswith("FAILED "):
                    failed_ids.append(line.split("::")[-1].split()[0])

        return f"pytest: {passed} passed, {failed} failed: {failed_ids[:3]}"

    def compress(self):
        if not self.entries:
            return "No scratch log found."

        mission = "Unknown"
        completed = []
        critical_context = []
        
        for e in self.entries:
            action = e.get("action")
            file = e.get("file")
            detail = str(e.get("detail", ""))
            
            if action == "start":
                mission = detail
            elif action == "done":
                completed.append(f"✅ step: {detail}")
            elif action == "read" and file:
                critical_context.append(f"read {file}: {detail[:50]}...")
            elif "pytest" in detail.lower():
                summary = self._parse_pytest_detail(detail)
                critical_context.append(summary)

        remaining = "Check task file for remaining items."
        if self.task_file:
            p = Path(self.task_file)
            if p.exists():
                lines = p.read_text().splitlines()
                rem_lines = [l.strip() for l in lines if "[ ]" in l or "- [ ]" in l]
                if rem_lines:
                    remaining = "\n".join(rem_lines)

        branch, last_commit, changed = self._get_git_info()
        
        test_report_str = "None"
        if TEST_REPORT.exists():
            try:
                tr = json.loads(TEST_REPORT.read_text())
                test_report_str = f"{tr.get('agent_directive', 'FAIL')} | New Failures: {tr.get('new_failures', [])}"
            except:
                pass

        stall = self.detect_stall() or "None"

        checkpoint = f"""## Session Resume [CP{self.cp_num} of 5] — {datetime.now(tz=timezone.utc).isoformat()}

### MISSION (verbatim)
{mission}

### Completed
{chr(10).join(completed[-10:])}

### Current State
- Branch: {branch}
- Last commit: {last_commit}
- Uncommitted changes: 
{changed}

### Remaining Work
{remaining}

### Critical Context (verified — do not re-derive)
{chr(10).join(critical_context[-10:])}

### Last NinaTestSuite Report
{test_report_str}

### ⚠ STALL ALERT
{stall}
"""
        CHECKPOINT_OUT.write_text(checkpoint)
        
        try:
            with open(SCRATCH_LOG, "a") as f:
                f.write(json.dumps({
                    "t": datetime.now(tz=timezone.utc).isoformat(),
                    "step": -99,
                    "action": "checkpoint",
                    "file": "",
                    "detail": f"Checkpoint CP{self.cp_num} saved",
                    "status": "ok"
                }) + "\n")
        except:
            pass

        return checkpoint

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task")
    parser.add_argument("--cp", type=int, default=0)
    parser.add_argument("--stall-only", action="store_true")
    args = parser.parse_args()

    compressor = ContextCompressor(task_file=args.task, cp_num=args.cp)
    
    if args.stall_only:
        stall = compressor.detect_stall()
        if stall:
            print(stall)
            sys.exit(1)
        else:
            sys.exit(0)
    
    compressor.compress()
    print(f"Checkpoint saved → {CHECKPOINT_OUT}")

if __name__ == "__main__":
    main()
