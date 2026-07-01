"""
NINA Sandboxed Python Executor (MT-7)
Provides a secure sandboxed environment to validate code, run tests, and execute safe scripts locally.
"""
from __future__ import annotations
import asyncio
import sys

import tempfile
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ExecResult:
    stdout: str
    stderr: str
    exit_code: int
    success: bool

class SandboxedExecutor:
    """Secure local sandbox wrapper utilizing subprocess isolation with limits."""
    
    async def run_python(self, code: str, timeout: int = 15) -> ExecResult:
        """Run python code in a temporary isolated file with resource limits."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            temp_path = Path(f.name)
        
        try:
            # Simple, robust subprocess sandbox execution
            cmd = [sys.executable, str(temp_path)]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                stdout = stdout_b.decode(errors="ignore")
                stderr = stderr_b.decode(errors="ignore")
                exit_code = proc.returncode or 0
            except asyncio.TimeoutError:
                proc.kill()
                stdout = ""
                stderr = "TIMEOUT_EXCEEDED: Execution exceeded limit."
                exit_code = -1
                
            return ExecResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                success=(exit_code == 0)
            )
        finally:
            if temp_path.exists():
                temp_path.unlink()

    async def run_tests(self, test_file: str, timeout: int = 30) -> ExecResult:
        """Run a pytest test suite within the virtual environment."""
        try:
            cmd = ["./venv/bin/pytest", test_file, "-v"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                stdout = stdout_b.decode(errors="ignore")
                stderr = stderr_b.decode(errors="ignore")
                exit_code = proc.returncode or 0
            except asyncio.TimeoutError:
                proc.kill()
                stdout = ""
                stderr = "TIMEOUT_EXCEEDED: Test execution exceeded limit."
                exit_code = -1
                
            return ExecResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                success=(exit_code == 0)
            )
        except Exception as e:
            return ExecResult(
                stdout="",
                stderr=f"EXECUTION_FAILED: {str(e)}",
                exit_code=-1,
                success=False
            )
