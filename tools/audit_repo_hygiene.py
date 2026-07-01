import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL)

# Subdirectories whose untracked files are INTENTIONALLY gitignored (generated outputs).
# Files here are never hard violations — they are downgraded to warnings.
GENERATED_EXEMPT_PREFIXES = (
    "docs/generated/",
    "archive/",
    "data/graphs/",
    "data/reports/",
    "data/logs/",
    "logs/",
    "exports/",
    "upgrades/backups/",
)


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.splitlines()


def get_git_tracked():
    return set(run_cmd(["git", "ls-files"]))


def get_git_untracked_non_ignored():
    """Return only untracked files that are NOT covered by .gitignore.

    Uses `git ls-files --others --exclude-standard` which honours .gitignore,
    .git/info/exclude, and global gitignore — so intentionally-ignored files
    (tools/.cursor/, tools/.agy/, tools/AGENTS.md, etc.) never appear here.
    """
    lines = run_cmd(["git", "ls-files", "--others", "--exclude-standard"])
    return set(f.rstrip("/") for f in lines if f)


def get_stale_files(months=6):
    recent = set(run_cmd(["git", "log", f"--since={months} months ago", "--pretty=format:", "--name-only"]))
    recent = {f for f in recent if f}
    tracked = get_git_tracked()
    return tracked - recent


def get_fs_all(repo_root):
    fs_all = set()
    ignore_parts = {".git", "venv", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".agent", "node_modules", ".aider.tags.cache"}
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in ignore_parts and not d.startswith(".aider")]
        for file in files:
            if file.startswith(".aider"):
                continue
            full_path = Path(root) / file
            rel_path = full_path.relative_to(repo_root)
            fs_all.add(str(rel_path))
    return fs_all


def notify_telegram(message):
    bot_token = os.environ.get(ENV_TELEGRAM_BOT_TOKEN)
    chat_id = os.environ.get("TELEGRAMCHATID")
    if not bot_token or not chat_id:
        print("\u26a0\ufe0f  Telegram credentials not found in environment. Skipping notification.")
        return
    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("\u2705 Telegram notification sent successfully.")
            else:
                print(f"\u274c Failed to send Telegram notification: {response.status}")
    except Exception as e:
        print(f"\u274c Exception sending Telegram notification: {e}")


def audit(strict=False, notify=False):
    repo_root = Path(__file__).parent.parent.resolve()

    git_tracked = get_git_tracked()
    fs_all = get_fs_all(repo_root)
    stale_tracked = get_stale_files(months=6)

    index_path = repo_root / "docs/space/nina_index.json"
    governed_paths = set()
    if index_path.exists():
        with open(index_path) as f:
            idx_data = json.load(f)
            governed_paths = {f["path"] for f in idx_data.get("files", []) if f.get("governed")}

    # Use git's own ignore machinery — this respects .gitignore, .git/info/exclude,
    # and global gitignore.  Only files that git itself considers "should be tracked
    # but aren't" will appear here.  Intentionally-ignored files are excluded.
    stray_locals = get_git_untracked_non_ignored()

    # For dashboard stats we still want the raw filesystem count.
    all_untracked = fs_all - git_tracked

    missing_locally = git_tracked - fs_all

    hard_violations = []
    warnings = []

    # Missing locally — hard violation unless it's a known generated/log path
    for f in missing_locally:
        if any(f.startswith(p) for p in GENERATED_EXEMPT_PREFIXES):
            warnings.append(f"Missing generated/exempt file (expected \u2014 gitignored): {f}")
        else:
            hard_violations.append(f"Missing locally (corrupted worktree): {f}")

    # Untracked files in governed dirs (gitignored files already excluded above)
    GOVERNED_TOPS = {"core", "tools", "interfaces", "docs", "crons", "agent", "ninagate", "checks"}
    for f in stray_locals:
        p = Path(f)
        # Exempt: generated output directories — never a hard violation
        if any(f.startswith(prefix) for prefix in GENERATED_EXEMPT_PREFIXES):
            if p.name != ".gitignore":
                warnings.append(f"Generated/exempt untracked (OK \u2014 gitignored): {f}")
            continue
        if p.parts[0] in GOVERNED_TOPS:
            if not f.endswith(".bak") and not f.endswith(".pyc") and not f.endswith(".log"):
                hard_violations.append(f"Untracked file in governed directory: {f}")
            else:
                warnings.append(f"Transient local in governed directory: {f}")
        else:
            warnings.append(f"Stray local (untracked): {f}")

    stale_governed = []
    for f in stale_tracked:
        if f in governed_paths:
            stale_governed.append(f)
            warnings.append(f"Stale governed file (>6 months): {f}")

    # Dashboard
    md = f"""# NINA Repository Hygiene Dashboard
_Generated by `tools/audit_repo_hygiene.py` on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_

## 1. Hygiene Status
- **Git Tracked Files:** {len(git_tracked)}
- **Stray Locals (Untracked, incl. gitignored):** {len(all_untracked)}
- **Stray Locals (Non-ignored, actionable):** {len(stray_locals)}
- **Missing Locally:** {len(missing_locally)}
- **Stale Governed Files (>6 months):** {len(stale_governed)}
- **Generated/Exempt Dirs:** {', '.join(GENERATED_EXEMPT_PREFIXES)}

## 2. Hard Violations (Blocks CI)
"""
    if not hard_violations:
        md += "\u2705 None.\n"
    else:
        for v in hard_violations:
            md += f"- \u274c {v}\n"

    md += "\n## 3. Stale Governed Files (Action Required)\n"
    if not stale_governed:
        md += "\u2705 None.\n"
    else:
        for f in sorted(stale_governed):
            md += f"- \u26a0\ufe0f `{f}` (Consider archival or check if dead code)\n"

    md += "\n## 4. Stray Locals (Top 20, non-ignored)\n"
    if not stray_locals:
        md += "\u2705 None.\n"
    else:
        for f in sorted(list(stray_locals))[:20]:
            md += f"- \U0001f5d1\ufe0f `{f}`\n"
    if len(stray_locals) > 20:
        md += f"- ... and {len(stray_locals) - 20} more.\n"

    with open(repo_root / "docs/space/nina_repo_hygiene_dashboard.md", "w") as f_out:
        f_out.write(md)

    print("\u2705 Hygiene audit complete. Dashboard: docs/space/nina_repo_hygiene_dashboard.md")

    if notify and hard_violations:
        from dotenv import load_dotenv
        load_dotenv(repo_root / ".env")
        msg = f"\U0001f6a8 *NINA Governance Alert*\n\nHygiene audit detected *{len(hard_violations)}* hard violations.\nCheck `docs/space/nina_repo_hygiene_dashboard.md` for details."
        notify_telegram(msg)

    if strict and hard_violations:
        print("\n\u274c STRICT MODE: Hard violations detected. Failing pipeline.")
        for v in hard_violations:
            print(f"  - {v}")
        sys.exit(1)

    if hard_violations:
        print(f"\n\u26a0\ufe0f WARNING: {len(hard_violations)} hard violations detected. (Run with --strict to fail).")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail with non-zero exit code on hard violations")
    parser.add_argument("--notify", action="store_true", help="Send Telegram alerts on violations")
    args = parser.parse_args()
    audit(args.strict, args.notify)
