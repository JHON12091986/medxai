import subprocess
import httpx
import logging
from pathlib import Path

logger = logging.getLogger("nina.tools.git_ops")
WORKSPACE = Path("data/workspace").resolve()

def _safe(path: str) -> Path:
    p = (WORKSPACE / path).resolve()
    if not str(p).startswith(str(WORKSPACE)):
        raise PermissionError(f"Path traversal blocked: {path}")
    return p

async def status() -> str:
    try:
        r = subprocess.run(["git", "status"], capture_output=True, text=True, check=True, shell=False)
        return r.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Git status failed: {e}")
        return f"Error: {e.stderr}"

async def diff() -> str:
    try:
        r = subprocess.run(["git", "diff"], capture_output=True, text=True, check=True, shell=False)
        return r.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Git diff failed: {e}")
        return f"Error: {e.stderr}"

async def stage(path: str) -> str:
    try:
        p = _safe(path)
        subprocess.run(["git", "add", str(p)], capture_output=True, text=True, check=True, shell=False)
        return "Staged successfully"
    except PermissionError as e:
        return str(e)
    except subprocess.CalledProcessError as e:
        logger.error(f"Git add failed: {e}")
        return f"Error: {e.stderr}"

async def auto_commit() -> str:
    try:
        diff_output = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=True, shell=False).stdout
        if not diff_output.strip():
            return "No staged changes to commit."

        prompt = f"""
        Generate a conventional commit message for the following diff.
        Only output the commit message, no explanations.
        Format: <type>(<scope>): <subject>

        {diff_output[:2000]}
        """

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8765/v1/chat/completions",
                json={
                    "model": "qwen2.5-coder:7b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                },
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json()
            commit_msg = data['choices'][0]['message']['content'].strip()

        r = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True, check=True, shell=False)
        return f"Committed with message: '{commit_msg}'.\nOutput: {r.stdout}"
    except Exception as e:
        logger.error(f"Auto commit failed: {e}")
        return f"Error: {e}"
