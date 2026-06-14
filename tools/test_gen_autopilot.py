import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKLOG_PATH = REPO_ROOT / "docs/space/jules_backlog.md"
JULES_TOOL = REPO_ROOT / "tools" / "jules.py"

# Batches of missing tests (from validate_index.py findings)
TEST_BATCHES = [
    {
        "id": "BT-CORE-INFRA",
        "files": ["core/logger.py", "core/config.py", "core/hotreload.py"],
        "prompt": "Create new test files in tests/ for: core/logger.py, core/config.py, core/hotreload.py. Use unittest.mock for all I/O. Follow conftest.py patterns. PASS on PYTHONPATH=. .venv/bin/pytest tests/test_<module>.py."
    },
    {
        "id": "BT-TOOLS-SYNC",
        "files": ["tools/ninaflash_core.py", "tools/nina_sync.py", "tools/git_ops.py"],
        "prompt": "Create new test files in tests/ for: tools/ninaflash_core.py, tools/nina_sync.py, tools/git_ops.py. MOCK ALL shell commands and git calls. Do not execute real git commands."
    },
    {
        "id": "BT-INTERFACES",
        "files": ["interfaces/cli_interface.py", "interfaces/api.py"],
        "prompt": "Create new test files in tests/ for: interfaces/cli_interface.py, interfaces/api.py. Mock sys.stdin/stdout for CLI and use httpx.AsyncClient with mock for API."
    }
]

def run_jules_goal(batch):
    print(f"🚀 Dispatching Batch {batch['id']}...")
    prompt = f"[NINA TEST GENERATION MISSION]\n{batch['prompt']}\n\nCONSTRAINTS: NEW FILES IN tests/ ONLY. DO NOT TOUCH CORE FILES."
    
    cmd = [str(REPO_ROOT / ".venv" / "bin" / "python"), str(JULES_TOOL), "goal", prompt]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    
    try:
        subprocess.run(cmd, env=env, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to dispatch {batch['id']}: {e}")
        return False

def main():
    # Only dispatch if not already active (check backlog or status)
    if run_jules_goal(TEST_BATCHES[0]):
        print("✅ Batch 1 dispatched successfully.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
