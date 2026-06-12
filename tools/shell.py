import asyncio, logging, shlex, subprocess
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
# cat removed in R-48, verified clean R-97.

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
            elif base in ["cat", "head", "tail", "less"]:
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
        loop = asyncio.get_running_loop()
        r = await asyncio.wait_for(
            loop.run_in_executor(None,
                lambda: subprocess.run(
                    parts,
                    capture_output=True, text=True, timeout=10, shell=False)),
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
