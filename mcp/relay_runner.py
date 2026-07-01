#!/usr/bin/env python3
"""
NinaMCP P2 — GitHub Actions relay runner.
Reads mcp/inbox/exec.json, validates against allowlist,
executes the command, writes result to mcp/outbox/exec_result.json.

Only runs inside GitHub Actions (NINA_MCP_RELAY=1).
"""
import os
import sys
import json
import subprocess
import pathlib
import datetime
import hashlib

if os.environ.get("NINA_MCP_RELAY") != "1":
    print("ERROR: This script only runs inside GitHub Actions (NINA_MCP_RELAY=1)")
    sys.exit(1)

REPO_ROOT = pathlib.Path(__file__).parent.parent
INBOX    = REPO_ROOT / "mcp" / "inbox" / "exec.json"
OUTBOX   = REPO_ROOT / "mcp" / "outbox" / "exec_result.json"
ALLOWLIST = REPO_ROOT / "mcp" / "allowlist.txt"
OUTBOX.parent.mkdir(parents=True, exist_ok=True)

def ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def load_allowlist() -> set[str]:
    if not ALLOWLIST.exists():
        return set()
    lines = ALLOWLIST.read_text().splitlines()
    return {l.strip() for l in lines if l.strip() and not l.startswith("#")}

def write_result(request_id: str, cmd: str, exit_code: int, output: str, error: str = "") -> None:
    result = {
        "request_id": request_id,
        "cmd": cmd,
        "ts": ts(),
        "exit_code": exit_code,
        "output": output[:50000],   # cap at 50KB
        "error": error
    }
    OUTBOX.write_text(json.dumps(result, indent=2))
    print(f"[relay] Written: mcp/outbox/exec_result.json (exit={exit_code})")

def main() -> None:
    if not INBOX.exists():
        print("[relay] No inbox file found. Nothing to execute.")
        write_result("none", "none", 0, "No command in inbox.")
        return

    try:
        payload = json.loads(INBOX.read_text())
    except json.JSONDecodeError as e:
        write_result("parse_error", "", 1, "", f"Invalid JSON in inbox: {e}")
        sys.exit(1)

    cmd       = payload.get("cmd", "").strip()
    req_id    = payload.get("request_id", hashlib.sha1(cmd.encode()).hexdigest()[:8])
    allowlist = load_allowlist()

    if not cmd:
        write_result(req_id, cmd, 1, "", "Empty command in inbox.")
        sys.exit(1)

    # Security: only allowlisted script prefixes
    cmd_base = cmd.split()[0] if cmd else ""
    allowed  = any(cmd.startswith(entry) or cmd_base == entry for entry in allowlist)
    if not allowed:
        msg = f"BLOCKED: '{cmd_base}' not in allowlist ({len(allowlist)} entries). Edit mcp/allowlist.txt."
        print(f"[relay] {msg}")
        write_result(req_id, cmd, 403, "", msg)
        sys.exit(0)  # non-fatal — don't fail the action

    print(f"[relay] Executing: {cmd}")
    try:
        proc = subprocess.run(
            ["bash", "-c", cmd],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "NINA_MCP_RELAY": "1"}
        )
        write_result(req_id, cmd, proc.returncode, proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired:
        write_result(req_id, cmd, 124, "", "Command timed out after 300s")
        sys.exit(1)
    except Exception as e:
        write_result(req_id, cmd, 1, "", f"Runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
