#!/usr/bin/env python3
"""
ninatestrunner.py — Unified Test & Audit Orchestrator for NINA.
Supports targeted file testing, predefined suites, and structured JSON output.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).parent.parent.resolve()
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path("python3")

class NinaTestSuite:
    def __init__(self, json_output=False, strict=False):
        self.json_output = json_output
        self.strict = strict
        self.results = []
        self.start_time = time.time()

    def run_cmd(self, cmd, cwd=str(REPO_ROOT), timeout=60):
        try:
            res = subprocess.run(
                cmd, shell=False, capture_output=True, text=True, cwd=cwd, timeout=timeout
            )
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def add_result(self, category, name, status, detail="", fix="", files=None):
        self.results.append({
            "category": category,
            "name": name,
            "status": status,  # PASS, FAIL, WARN
            "detail": detail,
            "fix": fix,
            "files": files or []
        })

    def check_syntax(self, file_path):
        """Run py_compile and pyflakes."""
        p = Path(file_path)
        if not p.exists():
            self.add_result("syntax", str(p), "FAIL", "File not found")
            return False

        # py_compile
        rc, out, err = self.run_cmd(["python3", "-m", "py_compile", str(p)])
        if rc != 0:
            self.add_result("syntax", f"py_compile:{p.name}", "FAIL", err, files=[str(p)])
            return False

        # pyflakes
        rc, out, err = self.run_cmd([str(VENV_PYTHON), "-m", "pyflakes", str(p)])
        if rc != 0:
            self.add_result("syntax", f"pyflakes:{p.name}", "FAIL", out or err, files=[str(p)])
            return False

        self.add_result("syntax", p.name, "PASS", files=[str(p)])
        return True

    def run_pytest(self, target=None, markers=None):
        """Run pytest with optional target and markers."""
        cmd = [str(VENV_PYTHON), "-m", "pytest", "--ignore=upgrades", "-q", "--no-header"]
        if target:
            cmd.append(target)
        if markers:
            cmd.extend(["-m", markers])
        else:
            # Default: exclude monkeytype
            cmd.extend(["-m", "not monkeytype"])

        rc, out, err = self.run_cmd(cmd)
        
        # Parse short summary
        summary = "Passed"
        if rc != 0:
            summary = out.splitlines()[-1] if out.splitlines() else "Failed"
        
        status = "PASS" if rc == 0 else "FAIL"
        self.add_result("unit", "pytest" if not target else f"pytest:{target}", status, out if rc != 0 else summary)
        return rc == 0

    def run_hygiene(self, strict=False):
        """Run audit_repo_hygiene.py."""
        cmd = [str(VENV_PYTHON), "tools/audit_repo_hygiene.py"]
        if strict:
            cmd.append("--strict")
        
        rc, out, err = self.run_cmd(cmd)
        status = "PASS" if rc == 0 else "FAIL"
        # Parse dashboard for highlights if failed
        detail = out
        if rc != 0:
            dashboard = REPO_ROOT / "docs/space/nina_repo_hygiene_dashboard.md"
            if dashboard.exists():
                detail = dashboard.read_text()

        self.add_result("governance", "hygiene", status, detail)
        return rc == 0

    def run_index_validation(self):
        """Run validate_index.py."""
        cmd = [str(VENV_PYTHON), "tools/validate_index.py"]
        rc, out, err = self.run_cmd(cmd)
        status = "PASS" if rc == 0 else "FAIL"
        self.add_result("governance", "index", status, out or err)
        return rc == 0

    def run_rule0(self):
        """Run rule0_audit.py."""
        cmd = [str(VENV_PYTHON), "tools/rule0_audit.py", "--hours", "24", "--json"]
        rc, out, err = self.run_cmd(cmd)
        if rc == 0:
            try:
                data = json.loads(out)
                detail = data.get("summary", "")
                status = "PASS" if data.get("target_met") else "WARN"
            except:
                detail = out
                status = "PASS"
        else:
            detail = out or err
            status = "FAIL"
        
        self.add_result("compliance", "rule0", status, detail)
        return status != "FAIL"

    def emit_report(self):
        duration = time.time() - self.start_time
        overall_status = "PASS"
        if any(r["status"] == "FAIL" for r in self.results):
            overall_status = "FAIL"
        elif any(r["status"] == "WARN" for r in self.results):
            overall_status = "WARN"

        new_failures = [r["name"] for r in self.results if r["status"] == "FAIL"]
        report = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "overall_status": overall_status,
            "agent_directive": "PASS" if overall_status == "PASS" else "FAIL",
            "new_failures": new_failures,
            "duration_s": round(duration, 2),
            "results": self.results
        }

        # Save to data/ninatestrunner_report.json
        report_path = REPO_ROOT / "data" / "ninatestrunner_report.json"
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2))
        except Exception as e:
            print(f"⚠️ Warning: Could not save report to {report_path}: {e}", file=sys.stderr)

        if self.json_output:
            print(json.dumps(report, indent=2))
        else:
            self.print_terminal_report(report)

        return 0 if overall_status == "PASS" or (overall_status == "WARN" and not self.strict) else 1

    def print_terminal_report(self, report):
        print(f"\n{'='*60}")
        print(f" NINA TEST SUITE REPORT — {report['overall_status']}")
        print(f"{'='*60}")
        for r in self.results:
            icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else "⚠️")
            print(f"{icon} [{r['category']}] {r['name']}")
            if r["status"] != "PASS":
                lines = str(r["detail"]).splitlines()
                for line in lines[:5]:
                    print(f"   | {line}")
                if len(lines) > 5:
                    print(f"   | ... ({len(lines)-5} more lines)")
        print(f"{'='*60}")
        print(f"Overall: {report['overall_status']} ({report['duration_s']}s)")
        print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="NINA Unified Test Runner")
    parser.add_argument("--file", help="Target specific file for syntax and related tests")
    parser.add_argument("--suite", choices=["sync", "full", "fast"], help="Run a predefined suite")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--strict", action="store_true", help="Fail on WARN status")
    args = parser.parse_args()

    runner = NinaTestSuite(json_output=args.json, strict=args.strict)

    if args.file:
        if args.file.endswith(".py"):
            runner.check_syntax(args.file)
            p = Path(args.file)
            test_path = REPO_ROOT / "tests" / f"test_{p.stem}.py"
            if test_path.exists():
                runner.run_pytest(target=str(test_path))
        else:
            runner.add_result("error", args.file, "FAIL", "Unsupported file type")
    
    elif args.suite == "sync":
        runner.run_hygiene(strict=args.strict)
        runner.run_index_validation()
        runner.run_rule0()
    
    elif args.suite == "full":
        runner.run_hygiene(strict=args.strict)
        runner.run_index_validation()
        runner.run_rule0()
        runner.run_pytest()
    
    elif args.suite == "fast":
        runner.run_pytest(markers="smoke")
    
    else:
        runner.run_pytest(markers="smoke")

    sys.exit(runner.emit_report())

if __name__ == "__main__":
    main()
