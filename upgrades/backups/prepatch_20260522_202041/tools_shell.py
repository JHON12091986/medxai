import asyncio, logging, shlex, subprocess
from pathlib import Path

logger = logging.getLogger("nina.tools.shell")

ALLOWED = [
    "df","ls","pwd","whoami","free","ps","uptime","cat","top","du","date",
    "systemctl status nina","journalctl -n 50 -u nina",
    "nvidia-smi","ollama ps","ollama list",
]

async def run(cmd: str) -> str:
    cmd = cmd.strip()
    if not any(cmd.startswith(a) for a in ALLOWED):
        base = cmd.split()[0] if cmd else ""
        logger.warning(f"shell_blocked cmd={cmd!r}", extra={"log":"tools.log"})
        return f"Blocked: '{base}' not in allowlist."

    # Prevent chaining attacks (;, &&, ||, |, backtick, $())
    for evil in (";", "&&", "||", "|", "`", "$("):
        if evil in cmd:
            logger.warning(f"shell_injection_blocked cmd={cmd!r}", extra={"log":"tools.log"})
            return f"Blocked: shell operators not allowed in command."

    try:
        loop = asyncio.get_running_loop()
        r = await asyncio.wait_for(
            loop.run_in_executor(None,
                lambda: subprocess.run(
                    shlex.split(cmd),   # no shell=True — safer
                    capture_output=True, text=True, timeout=10)),
            timeout=12)

        out = (r.stdout + r.stderr).strip()[:2000]

        if r.returncode != 0:
            logger.warning(f"shell_nonzero cmd={cmd!r} rc={r.returncode} err={r.stderr[:80]!r}",
                           extra={"log":"tools.log"})
            return f"Exit {r.returncode}: {out or '(no output)'}"

        logger.info(f"shell_ok cmd={cmd!r} out={out[:80]!r}", extra={"log":"tools.log"})
        return out or "(no output)"

    except asyncio.TimeoutError:
        return "Command timed out (10s)."
    except FileNotFoundError:
        return f"Command not found: {cmd.split()[0]}"
    except Exception as e:
        return f"Error: {e}"
