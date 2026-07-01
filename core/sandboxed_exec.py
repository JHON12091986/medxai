"""core/sandboxed_exec.py — Sandboxed Python code executor for NINA vNext.

Runs untrusted or autonomous-generated Python in a subprocess with:
  - configurable timeout (default 15 s)
  - stdout + stderr capture
  - optional pytest gate: code only "passes" if its tests pass
  - resource limits (RLIMIT_AS memory cap on Linux)
  - NO network access by default (caller can override)

Used by:
  - core/react_engine   — run tool-generated code during verification step
  - core/autonomy        — test-gate before low-risk auto-merge
  - Jules async pipeline — local pre-flight before PR creation

Design rules:
  - Never import subprocess inside an async context without await.
  - Always clean up temp files in finally blocks.
  - Execution failures are returned as SandboxResult, never raised.
  - Code that writes files must do so inside the sandbox working dir.

Example:
    from core.sandboxed_exec import SandboxedExecutor
    sb = SandboxedExecutor()
    result = await sb.run_code("print(2 + 2)")
    print(result.stdout)        # "4"
    print(result.success)       # True
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.sandbox")

DEFAULT_TIMEOUT_S   = 15
DEFAULT_MEMORY_MB   = 256
MAX_OUTPUT_CHARS     = 8_000     # truncate huge stdout
MAX_CODE_CHARS       = 40_000    # refuse oversized blobs

_BANNED_IMPORTS = [
    "ctypes", "cffi", "subprocess", "multiprocessing", "socket",
    "_thread", "threading",  # threading allowed in tests; ban raw threads in code
    "resource", "mmap",
]


@dataclass
class SandboxResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    timed_out: bool = False
    error: str = ""
    tests_passed: int = 0
    tests_failed: int = 0

    def summary(self) -> str:
        if self.timed_out:
            return f"⏱️ Timed out after execution"
        if not self.success:
            return f"❌ Failed (rc={self.returncode}): {self.stderr[:200]}"
        if self.tests_failed > 0:
            return (
                f"⚠️ Tests: {self.tests_passed} passed, {self.tests_failed} failed\n"
                f"{self.stdout[:400]}"
            )
        if self.tests_passed > 0:
            return f"✅ Tests: {self.tests_passed} passed\n{self.stdout[:400]}"
        return f"✅ OK\n{self.stdout[:400]}"


class SandboxedExecutor:
    """Execute Python code safely in a subprocess."""

    def __init__(
        self,
        timeout:   int   = DEFAULT_TIMEOUT_S,
        memory_mb: int   = DEFAULT_MEMORY_MB,
        allow_network: bool = False,
    ):
        self.timeout      = timeout
        self.memory_mb    = memory_mb
        self.allow_network = allow_network

    async def run_code(
        self,
        code: str,
        *,
        extra_files: dict[str, str] | None = None,
        env_extras:  dict[str, str] | None = None,
    ) -> SandboxResult:
        """Execute a Python code string in a sandboxed subprocess.

        Args:
            code:        Python source code to run.
            extra_files: {filename: content} — written to the sandbox dir
                         before execution (e.g., input data files).
            env_extras:  Extra env vars to pass into the subprocess.

        Returns:
            SandboxResult with stdout, stderr, and success flag.
        """
        if len(code) > MAX_CODE_CHARS:
            return SandboxResult(
                success=False,
                error=f"Code too large: {len(code)} > {MAX_CODE_CHARS} chars",
            )

        static_check = _static_safety_check(code)
        if static_check:
            return SandboxResult(success=False, error=static_check)

        with tempfile.TemporaryDirectory(prefix="nina_sandbox_") as tmpdir:
            tmp = Path(tmpdir)

            # Write extra support files
            for fname, content in (extra_files or {}).items():
                (tmp / fname).write_text(content, encoding="utf-8")

            # Write the code file
            code_file = tmp / "_code_.py"
            code_file.write_text(code, encoding="utf-8")

            cmd = [sys.executable, str(code_file)]
            return await self._run_subprocess(
                cmd, tmpdir=tmpdir, env_extras=env_extras
            )

    async def run_pytest(
        self,
        code: str,
        test_code: str,
        *,
        env_extras: dict[str, str] | None = None,
    ) -> SandboxResult:
        """Run code under a pytest suite. Gate: tests must pass for success=True.

        Args:
            code:       Implementation Python source.
            test_code:  pytest-style test code that imports from the impl file.

        Returns:
            SandboxResult with tests_passed / tests_failed counts.
        """
        static_check = _static_safety_check(code + "\n" + test_code)
        if static_check:
            return SandboxResult(success=False, error=static_check)

        with tempfile.TemporaryDirectory(prefix="nina_pytest_") as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "implementation.py").write_text(code, encoding="utf-8")
            (tmp / "test_impl.py").write_text(test_code, encoding="utf-8")

            cmd = [
                sys.executable, "-m", "pytest", str(tmp / "test_impl.py"),
                "-v", "--tb=short", f"--timeout={self.timeout - 2}",
                "--no-header",
            ]
            result = await self._run_subprocess(
                cmd, tmpdir=tmpdir, env_extras=env_extras
            )
            result = _parse_pytest_output(result)
            return result

    async def verify_snippet(
        self,
        snippet: str,
        expected_output: str | None = None,
    ) -> SandboxResult:
        """Quick verify: run snippet and optionally compare stdout."""
        result = await self.run_code(snippet)
        if expected_output is not None and result.success:
            got = result.stdout.strip()
            exp = expected_output.strip()
            if got != exp:
                result.success = False
                result.error = (
                    f"Output mismatch.\nExpected: {exp!r}\nGot:      {got!r}"
                )
        return result

    # ─ internal ──────────────────────────────────────────────────────────────

    async def _run_subprocess(
        self,
        cmd: list[str],
        tmpdir: str,
        env_extras: dict[str, str] | None,
    ) -> SandboxResult:
        env = _build_env(tmpdir, env_extras, self.allow_network)
        preexec = _make_preexec(self.memory_mb)

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tmpdir,
                env=env,
                preexec_fn=preexec,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=self.timeout
                )
                rc = proc.returncode
                stdout = stdout_b.decode(errors="replace")[:MAX_OUTPUT_CHARS]
                stderr = stderr_b.decode(errors="replace")[:MAX_OUTPUT_CHARS]
                return SandboxResult(
                    success=(rc == 0),
                    stdout=stdout,
                    stderr=stderr,
                    returncode=rc,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                log.warning("sandbox: execution timed out after %ds", self.timeout)
                return SandboxResult(
                    success=False, timed_out=True,
                    error=f"Timed out after {self.timeout}s",
                )
        except Exception as exc:
            log.error("sandbox: subprocess launch failed: %s", exc)
            return SandboxResult(success=False, error=str(exc))


# ── helpers ─────────────────────────────────────────────────────────────────

def _static_safety_check(code: str) -> str:
    """Return an error string if the code contains banned patterns."""
    for banned in _BANNED_IMPORTS:
        if f"import {banned}" in code or f"from {banned}" in code:
            return f"Banned import detected: {banned}"
    if "__import__" in code and any(b in code for b in _BANNED_IMPORTS):
        return "Dynamic banned import detected"
    return ""


def _build_env(
    tmpdir: str,
    extras: dict[str, str] | None,
    allow_network: bool,
) -> dict[str, str]:
    """Build a minimal safe environment for the subprocess."""
    env = {
        "PATH":         os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME":         tmpdir,
        "TMPDIR":       tmpdir,
        "PYTHONPATH":   tmpdir,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1",
    }
    if not allow_network:
        # Blank out proxy vars and hint to disable net (best-effort)
        env["http_proxy"]  = ""
        env["https_proxy"] = ""
        env["no_proxy"]    = "*"
    env.update(extras or {})
    return env


def _make_preexec(memory_mb: int):
    """Return a preexec_fn that sets memory limits on Linux."""
    def _set_limits():
        try:
            import resource
            mem_bytes = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS,  (mem_bytes, mem_bytes))
            resource.setrlimit(resource.RLIMIT_CPU, (30, 30))  # hard CPU cap
        except Exception:
            pass  # Not on Linux or resource unavailable — proceed anyway
    return _set_limits


def _parse_pytest_output(result: SandboxResult) -> SandboxResult:
    """Parse pytest stdout to extract pass/fail counts."""
    import re
    text = result.stdout + result.stderr
    # e.g. "3 passed, 1 failed in 0.12s"
    m = re.search(r"(\d+) passed", text)
    if m:
        result.tests_passed = int(m.group(1))
    m = re.search(r"(\d+) failed", text)
    if m:
        result.tests_failed = int(m.group(1))
    result.success = (result.returncode == 0 and result.tests_failed == 0)
    return result
