import asyncio, logging, shlex, subprocess, fnmatch
from pathlib import Path

# ---- Allowlists -------------------------------------------------------------
ALLOWED_BASES = {
    "df", "ls", "pwd", "whoami", "free", "ps", "uptime",
    "head", "tail", "grep", "find", "echo", "date",
    "ping", "curl", "wget", "python", "python3", "pip", "pip3",
    "git", "systemctl", "journalctl", "ollama", "nvidia-smi",
}
ALLOWED_SYSTEMCTL_SUBS = {
    "status", "start", "stop", "restart", "enable", "disable", "is-active",
}
ALLOWED_OLLAMA_SUBS = {
    "list", "show", "pull", "run", "stop", "ps", "serve",
}
# c@t removed in R-48, verified clean R-97.

ALLOWED = ALLOWED_BASES   # backward-compat alias

logger = logging.getLogger("nina.tools.shell")


async def run(cmd: str) -> str:
    cmd   = cmd.strip()
    parts = shlex.split(cmd) if cmd else []
    base  = parts[0] if parts else ""

    if base not in ALLOWED_BASES:
        logger.warning(f"shell:blocked cmd={cmd!r}", extra={"log": "tools.log", "tool_name": "shell"})
        return f"Blocked: {base!r} not in allowlist."

    # FIX: compare only parts[1] (the subcommand token), not the joined tail
    if base == "systemctl":
        sub = parts[1] if len(parts) > 1 else ""
        if sub not in ALLOWED_SYSTEMCTL_SUBS:
            return f"Blocked: systemctl subcommand {sub!r} not allowed."

    if base == "ollama":
        sub = parts[1] if len(parts) > 1 else ""
        if sub not in ALLOWED_OLLAMA_SUBS:
            return f"Blocked: ollama subcommand {sub!r} not allowed."

    for evil in (";", "&&", "||", "|", "`", "$("):
        if evil in cmd:
            logger.warning(f"shell_injection_blocked cmd={cmd!r}", extra={"log": "tools.log", "tool_name": "shell"})
            return "Blocked: shell operators not allowed in command."

    # SEC-IGNORE logic
    try:
        ignore_file = Path(".geminiignore")
        if ignore_file.exists():
            patterns = [p.strip() for p in ignore_file.read_text().splitlines() if p.strip() and not p.startswith("#")]
            dirs_to_exclude = [p[:-1] for p in patterns if p.endswith('/')]
            if base == "grep":
                for d in dirs_to_exclude:
                    parts.insert(1, f"--exclude-dir={d}")
                for d in patterns:
                    if not d.endswith('/'):
                        parts.insert(1, f"--exclude={d}")
            elif base in ["head", "tail", "less"]:
                import fnmatch
                for p in parts[1:]:
                    if not p.startswith('-'):
                        for d in patterns:
                            if d.endswith('/'):
                                d_clean = d[:-1]
                                if fnmatch.fnmatch(p, d_clean) or p.startswith(d) or fnmatch.fnmatch(p, f"*/{d_clean}") or f"/{d}" in f"/{p}":
                                    return f"Blocked: {base} access to {p} matches .geminiignore pattern {d}"
                            else:
                                if fnmatch.fnmatch(p, d) or fnmatch.fnmatch(p, f"*/{d}"):
                                    return f"Blocked: {base} access to {p} matches .geminiignore pattern {d}"
            elif base == "find":
                for d in dirs_to_exclude:
                    parts.extend(["-not", "-path", f"*/{d}/*"])
                for d in patterns:
                    if not d.endswith('/'):
                        parts.extend(["-not", "-name", d])
    except Exception as e:
        logger.error(f"shell_ignore_error err={e}")

    try:
        # Micro-Sandboxed Environment: Keep only essential execution variables, strip all custom secrets
        import os
        safe_env = {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "HOME": os.environ.get("HOME", "/home/aibony"),
            "USER": os.environ.get("USER", "aibony"),
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            "TERM": "xterm-256color",
        }
        if "VIRTUAL_ENV" in os.environ:
            safe_env["VIRTUAL_ENV"] = os.environ["VIRTUAL_ENV"]

        loop = asyncio.get_running_loop()
        r = await asyncio.wait_for(
            loop.run_in_executor(None,
                lambda: subprocess.run(
                    parts,
                    capture_output=True, text=True, timeout=10, shell=False, env=safe_env)),
            timeout=12)

        out = (r.stdout + r.stderr).strip()[:2000]

        if r.returncode != 0:
            logger.warning(
                f"shell_nonzero cmd={cmd!r} rc={r.returncode} err={r.stderr[:80]!r}",
                extra={"log": "tools.log", "tool_name": "shell"})
            return f"Exit {r.returncode}: {out or '(no output)'}"

        logger.info(f"shell_ok cmd={cmd!r} out={out[:80]!r}", extra={"log": "tools.log", "tool_name": "shell"})
        return out or "(no output)"

    except asyncio.TimeoutError:
        return "Command timed out (10s)."
    except FileNotFoundError:
        return f"Command not found: {cmd.split()[0]}"
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        logger.error(f"shell_error cmd={cmd!r} err={e}", extra={"log": "tools.log", "tool_name": "shell"})
        return f"Error: {e}"



def _load_geminiignore() -> list[str]:
    ignore_file = Path('.geminiignore')
    if not ignore_file.exists(): return []
    return [line.strip() for line in ignore_file.read_text().splitlines() if line.strip() and not line.startswith('#')]

def _is_ignored(path_str: str) -> bool:
    patterns = _load_geminiignore()
    for pattern in patterns:
        if pattern.startswith('!'): continue
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path_str, f"*/{pattern}") or fnmatch.fnmatch(path_str, f"{pattern}*"):
            return True
    return False

def is_command_safe(cmd: str) -> bool:
    """Minimal security stub for Rule 0 compliance."""
    blocked = ['rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:']
    if any(b in cmd for b in blocked):
        return False

    parts = shlex.split(cmd) if cmd else []
    base = parts[0] if parts else ""
    if base in ['grep', 'ls', 'find', 'head', 'tail']:
        for part in parts[1:]:
            if not part.startswith('-') and _is_ignored(part):
                return False
    return True
