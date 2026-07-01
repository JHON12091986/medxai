#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shlex, subprocess, sys
from pathlib import Path

REPO_ROOT = Path.cwd()

def run(cmd: str, check: bool = True, capture: bool = False):
    return subprocess.run(cmd, shell=True, cwd=REPO_ROOT, text=True, check=check, capture_output=capture)

def exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()

def safe(cmd: str, default: str = "") -> str:
    try:
        out = run(cmd, check=False, capture=True).stdout.strip()
        return out or default
    except Exception:
        return default

def cmd_doctor(args):
    data = {
        "repo_root": str(REPO_ROOT),
        "head": safe("git rev-parse --short HEAD", "unknown"),
        "git_status": safe("git status -sb", "unknown"),
        "dirty_files": safe("git status --short | wc -l", "0"),
        "has_sync": exists("scripts/nina_sync.sh"),
        "has_registry": exists("docs/space/nina_file_registry.json"),
        "has_ssot_tool": exists("tools/ssot_registry.py"),
        "has_vulture": run("python3 -m vulture --version", check=False).returncode == 0,
        "service_active": run("systemctl --user is-active nina.service", check=False).returncode == 0,
    }
    print(json.dumps(data, indent=2))
    return 0

def cmd_sync(args):
    return run(f"bash scripts/nina_sync.sh {shlex.quote(args.mode)}", check=False).returncode

def cmd_fix(args):
    return run("python3 tools/ssot_registry.py semantic || true\nbash scripts/nina_sync.sh audit", check=False).returncode

def cmd_upgrade(args):
    script = """set -euo pipefail
git fetch origin
BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$BRANCH" = "main" ] || { echo "Not on main"; exit 2; }
if ! git diff --quiet || ! git diff --cached --quiet; then
  git stash push -u -m "nina-upgrade-auto" >/dev/null 2>&1 || true
fi
git pull --rebase origin main || true
python3 -m pip install --upgrade vulture >/dev/null 2>&1 || true
python3 tools/ssot_registry.py semantic || true
bash scripts/nina_sync.sh audit || true
"""
    return run(script, check=False).returncode

def cmd_ask(args):
    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("No prompt provided", file=sys.stderr)
        return 2
    if exists("bin/agy"):
        return run(f"./bin/agy {shlex.quote(prompt)}", check=False).returncode
    if exists("bin/gemini"):
        return run(f"./bin/gemini {shlex.quote(prompt)}", check=False).returncode
    print(prompt)
    return 0

def cmd_heal(args):
    script = """set -euo pipefail
python3 -m pip install --upgrade vulture >/dev/null 2>&1 || true
python3 tools/ssot_registry.py semantic || true
bash scripts/nina_sync.sh audit || true
systemctl --user is-active nina.service >/dev/null 2>&1 || systemctl --user restart nina.service || true
"""
    return run(script, check=False).returncode


def cmd_finalize(args):
    script = """set -euo pipefail
python3 tools/ssot_registry.py semantic || true
bash scripts/nina_sync.sh audit || true
git add README.md CHANGELOG.md docs/space/NINA_UPDATE_LOG.md \
        docs/space/nina_file_registry.json docs/space/nina_repo_hygiene_dashboard.md \
        tools/docs/generated/nina_commit_index.md data/graphs/nina_context_graph.json \
        git-hooks/pre-commit bin/nina bin/nina-super tools/nina_super_cli.py \
        interfaces/cli_interface.py core/router.py || true
git commit -m \"chore(nina): finalize super-ai docs, ssot state, and generated artifacts\" || true
"""
    return run(script, check=False).returncode

def cmd_evolve(args):
    print("Nina Super AI control plane active.")
    print("Use: nina-super doctor | sync audit | heal | upgrade | ask ...")
    return 0

def main():
    p = argparse.ArgumentParser(prog="nina-super", description="Nina Super AI CLI")
    sp = p.add_subparsers(dest="command", required=True)

    d = sp.add_parser("doctor"); d.set_defaults(func=cmd_doctor)
    s = sp.add_parser("sync"); s.add_argument("mode", nargs="?", default="audit", choices=["all","pull-only","push-only","hooks","audit"]); s.set_defaults(func=cmd_sync)
    f = sp.add_parser("fix"); f.set_defaults(func=cmd_fix)
    u = sp.add_parser("upgrade"); u.set_defaults(func=cmd_upgrade)
    a = sp.add_parser("ask"); a.add_argument("prompt", nargs=argparse.REMAINDER); a.set_defaults(func=cmd_ask)
    h = sp.add_parser("heal"); h.set_defaults(func=cmd_heal)
    e = sp.add_parser("evolve"); e.set_defaults(func=cmd_evolve)

    args = p.parse_args()
    raise SystemExit(args.func(args))

if __name__ == "__main__":
    main()
