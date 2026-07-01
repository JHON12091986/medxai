import os
import subprocess
import py_compile
import time
from .models import GapItem

def scan_hygiene(repo_root: str = ".", max_files: int = 200) -> list[GapItem]:
    gaps = []

    py_files = []
    for root, _, files in os.walk(repo_root):
        if '.git' in root or 'venv' in root:
            continue
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))

    py_files.sort()
    py_files = py_files[:max_files]

    for py_file in py_files:
        try:
            py_compile.compile(py_file, doraise=True)
        except py_compile.PyCompileError:
            gaps.append(GapItem(
                source="hygiene",
                raw_text=f"SyntaxError: {py_file}",
                priority="P1"
            ))

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )

        if result.returncode == 0:
            modified_files = [f for f in result.stdout.split('\n') if f]
            current_time = time.time()

            for file in modified_files:
                file_path = os.path.join(repo_root, file)
                if os.path.exists(file_path):
                    mtime = os.path.getmtime(file_path)
                    if current_time - mtime > 172800:
                        gaps.append(GapItem(
                            source="hygiene",
                            raw_text=f"Uncommitted modified file > 48h old: {file}",
                            priority="P2"
                        ))

    except subprocess.TimeoutExpired:
        gaps.append(GapItem(
            source="hygiene",
            raw_text="git_diff_timeout",
            priority="P2"
        ))
    except Exception:
        pass

    return gaps
