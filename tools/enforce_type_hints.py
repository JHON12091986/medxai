import argparse
import os
import pathlib
import sys
import subprocess

def process_file(filepath: str, repo_root: str, fix: bool = False):
    rel_path = os.path.relpath(filepath, repo_root)
    # Convert path to module name
    if rel_path.endswith(".py"):
        rel_path = rel_path[:-3]
    module_name = rel_path.replace(os.sep, ".")

    if fix:
        print(f"Applying type hints to: {module_name}")
        # Apply the hints directly
        cmd = ["monkeytype", "apply", module_name]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error applying to {module_name}:\n{res.stderr}")
            return False
        return True
    else:
        # Just check if monkeytype has hints for it (or stub it out)
        print(f"Needs fixing: {filepath} (Run with --fix to apply changes)")
        return False

def main():
    parser = argparse.ArgumentParser(description="Enforce type hints in Python files using MonkeyType.")
    parser.add_argument("path", help="Path to file or directory")
    parser.add_argument("--fix", action="store_true", help="Apply fixes")
    args = parser.parse_args()

    target_path = pathlib.Path(args.path).absolute()
    repo_root = pathlib.Path.cwd().absolute()

    # Generate the traces by running tests with monkeytype
    if args.fix:
        print("Generating call traces with MonkeyType (running pytest)...")
        env = os.environ.copy()
        env["PYTHONPATH"] = f"./tools:{env.get('PYTHONPATH', '.')}"
        subprocess.run(["monkeytype", "run", "-m", "pytest", "tests/"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    all_passed = True
    if target_path.is_file() and target_path.suffix == '.py':
        all_passed = process_file(str(target_path), str(repo_root), args.fix)
    elif target_path.is_dir():
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith('.py'):
                    if not process_file(os.path.join(root, file), str(repo_root), args.fix):
                        all_passed = False
    else:
        print(f"Invalid path or no Python files found: {args.path}")
        sys.exit(1)

    if not all_passed and not args.fix:
        sys.exit(1)

if __name__ == "__main__":
    main()
