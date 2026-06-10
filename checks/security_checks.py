from checks.runner import record, NINA_DIR
import re
def check_shell_allowlist():
    shell_path = NINA_DIR / "tools" / "shell.py"
    if not shell_path.exists():
        record("INFO", "shell.allowlist.missing", "tools/shell.py not found — skipping allowlist check")
        return

    source = shell_path.read_text(errors="replace")

    # R-48: 'cat' must not be in ALLOWED
    if re.search(r"['\"]cat['\"]", source):
        record(
            "BLOCKER", "shell.allowlist.regression",
            "Security regression: 'cat' found in shell allowlist (tools/shell.py)",
            detail="'cat' in ALLOWED enables unrestricted file reads including .env and SSH keys.",
            fix="Remove 'cat' from the ALLOWED set in ~/nina/tools/shell.py (R-48 fix).",
        )
    else:
        record("PASS", "shell.allowlist.regression", "Shell allowlist — 'cat' not present — OK")

    # Check for shell=True without injection protection
    if re.search(r"shell\s*=\s*True", source) and not re.search(r"shlex\.split", source):
        record(
            "WARN", "shell.injection_risk",
            "tools/shell.py uses shell=True without shlex.split — injection risk",
            detail="shell=True without tokenisation can allow command injection.",
            fix="Add shlex.split() and a shell operator blocklist (R-40 fix).",
        )
    else:
        record("PASS", "shell.injection_risk", "Shell injection protection — OK")

def check_ssrf_guard():
    browser_path = NINA_DIR / "tools" / "browser.py"
    if not browser_path.exists():
        record("INFO", "browser.ssrf.missing", "tools/browser.py not found — skipping SSRF check")
        return

    source = browser_path.read_text(errors="replace")

    # R-64: substring SSRF checks are bad — ipaddress module must be used
    substring_ssrf = re.search(r'"10\." in url|"192\.168" in url|"172\." in url', source)
    ipaddress_used = re.search(r"import ipaddress|from ipaddress", source)

    if substring_ssrf and not ipaddress_used:
        record(
            "DEBT", "browser.ssrf.guard_regression",
            "SSRF guard uses substring matching — ipaddress module not used",
            detail="Substring SSRF checks are bypassable. Use ipaddress.ip_address() (R-64 fix).",
            fix="Replace substring checks with ipaddress.ip_address() range validation in tools/browser.py.",
        )
    else:
        record("PASS", "browser.ssrf.guard_regression", "SSRF guard — ipaddress module in use — OK")

def check_pipeline_security():
    pipeline_path = NINA_DIR / "tools" / "upgradepipeline.py"
    if not pipeline_path.exists():
        record("INFO", "pipeline.missing", "tools/upgradepipeline.py not found — skipping pipeline checks")
        return

    source = pipeline_path.read_text(errors="replace")

    # R-54: weak eval/exec regex (no word boundaries)
    has_word_boundary = re.search(r"\\b(eval|exec|compile)\\b", source)
    has_eval_pattern  = re.search(r"eval|exec|compile", source)
    if has_eval_pattern and not has_word_boundary:
        record(
            "DEBT", "pipeline.eval_regex_weak",
            "Upgrade pipeline eval/exec pattern may lack \\b word boundaries",
            detail="Without word boundaries, 'evaluate' or 'executor' could be falsely flagged.",
            fix="Use re.compile(r'\\b(eval|exec|compile)\\b') in tools/upgradepipeline.py (R-54 fix).",
        )
    else:
        record("PASS", "pipeline.eval_regex_weak", "Pipeline eval/exec regex — OK")

    # R-63: content-type and size guard
    has_content_type = re.search(r"content.type|Content-Type", source, re.IGNORECASE)
    has_size_guard   = re.search(r"100.*1024|max.*size|content.*length", source, re.IGNORECASE)
    if not has_content_type or not has_size_guard:
        record(
            "DEBT", "pipeline.no_content_type_guard",
            "Upgrade pipeline may be missing Content-Type or size guard on remote fetch",
            detail="Fetching patches without Content-Type/size guard allows binary or oversized data.",
            fix="Enforce text/plain + 100KB max on all patch downloads (R-63 fix).",
        )
    else:
        record("PASS", "pipeline.no_content_type_guard", "Pipeline content-type + size guard — OK")
