"""Async shell executor — non-blocking subprocess wrapper with semaphore concurrency control. Max 4 concurrent shell tasks."""
import asyncio
import logging
import shlex
import os

logger = logging.getLogger("nina.executor.async_shell")

# Hard limit: 4 concurrent shell tasks. Raise only after benchmarking.
SHELL_SEMAPHORE = asyncio.Semaphore(4)

async def run_shell(cmd: str | list, *, cwd: str | None = None, timeout: float = 120.0, env_extra: dict | None = None) -> tuple[int, str, str]:
    """Run a shell command asynchronously. Returns (returncode, stdout, stderr). Raises asyncio.TimeoutError if timeout exceeded. Raises ValueError if cmd is empty."""
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd)
    else:
        cmd_list = list(cmd)

    if not cmd_list:
        raise ValueError("cmd must not be empty")

    env = os.environ.copy()
    if env_extra is not None:
        env.update(env_extra)

    async with SHELL_SEMAPHORE:
        proc = await asyncio.create_subprocess_exec(
            *cmd_list,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise

    stdout_str = stdout_bytes.decode("utf-8", errors="replace").strip()
    stderr_str = stderr_bytes.decode("utf-8", errors="replace").strip()

    logger.debug(f"[async_shell] rc={proc.returncode} cmd={cmd_list}")
    return proc.returncode, stdout_str, stderr_str

async def run_shell_checked(cmd: str | list, *, cwd: str | None = None, timeout: float = 120.0) -> str:
    """Like run_shell but raises RuntimeError on non-zero returncode. Returns stdout."""
    rc, stdout, stderr = await run_shell(cmd, cwd=cwd, timeout=timeout)
    if rc != 0:
        raise RuntimeError(f"Command failed (rc={rc}): {stderr}")
    return stdout
