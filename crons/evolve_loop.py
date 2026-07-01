import subprocess
import sys
import uuid
from pathlib import Path

# Add project root to PYTHONPATH for correct module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_evolution_cycle():
    import tools.monitor as monitor
    import tools.evolve as evolve

    print("SENSE: Generating efficiency report...")
    monitor.generate_efficiency_report()

    print("THINK: Checking bottlenecks and generating proposals...")
    action = evolve.check_bottlenecks()

    print("ACT: Implementing proposals...")
    if action and action != "NONE":
        import core.jules_guard as jules_guard
        import json
        open_prs = []
        try:
            state_path = Path(__file__).parent.parent / "docs/space/nina_state.json"
            if state_path.exists():
                with open(state_path, "r") as f:
                    open_prs = json.load(f).get("open_prs", [])
        except Exception:
            pass
        error_id = action
        if jules_guard.check_before_jules_submit(error_id, open_prs):
            print("EVOLVE: Skipping submission as it is already in open PRs.")
            return

        branch_name = f"evolve-optimization-{uuid.uuid4().hex[:8]}"
        print(f"Creating temporary branch {branch_name}...")
        subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True)

        tests_passed = evolve.act(action)

        if tests_passed:
            print("EVOLVE: Cycle complete, tests passed. Merging...")
            # Commit changes
            subprocess.run(["git", "add", "."], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"feat(autonomous): implemented {action}"], capture_output=True)
            # Switch back and merge
            subprocess.run(["git", "checkout", "main"], capture_output=True)
            subprocess.run(["git", "merge", branch_name], capture_output=True)
            # Cleanup branch
            subprocess.run(["git", "branch", "-d", branch_name], capture_output=True)
        else:
            print("EVOLVE: Tests failed, rolling back.")
            subprocess.run(["git", "reset", "--hard"], capture_output=True)
            subprocess.run(["git", "checkout", "main"], capture_output=True)
            subprocess.run(["git", "branch", "-D", branch_name], capture_output=True)
    else:
        print("EVOLVE: No action taken.")

if __name__ == "__main__":
    run_evolution_cycle()
