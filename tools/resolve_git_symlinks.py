#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def resolve_symlinks():
    print("Checking git-tracked symlinks...")
    try:
        res = subprocess.run(
            ["git", "ls-files", "--stage"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running git ls-files: {e.stderr}", file=sys.stderr)
        return False

    repo_root = Path(__file__).resolve().parent.parent
    lines = res.stdout.strip().split("\n")
    resolved_count = 0
    failed_count = 0

    for line in lines:
        if not line.strip():
            continue
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        mode, sha, stage, filepath = parts
        if mode != "120000":
            continue

        link_path = repo_root / filepath
        if not link_path.exists() and not link_path.is_symlink():
            print(f"Symlink file {filepath} not found on disk, skipping.")
            continue

        # If it's a symlink already, check if it resolves correctly
        if link_path.is_symlink():
            try:
                target = os.readlink(link_path)
                real_target = (link_path.parent / target).resolve(strict=True)
                if real_target.exists():
                    # Symlink exists and is valid
                    continue
            except (FileNotFoundError, OSError):
                pass

        # Read the target path stored in the placeholder file
        try:
            with open(link_path, "r") as f:
                target_str = f.read().strip()
        except Exception as e:
            print(f"Error reading placeholder {filepath}: {e}", file=sys.stderr)
            failed_count += 1
            continue

        if not target_str:
            print(f"Placeholder {filepath} is empty, skipping.")
            continue

        target_path = (link_path.parent / target_str).resolve()
        if not target_path.exists():
            print(f"Target path {target_str} resolved to non-existent {target_path} for {filepath}")
            failed_count += 1
            continue

        # Recreate the symlink or copy target content
        try:
            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()
            
            # Attempt filesystem symlink creation
            try:
                os.symlink(target_str, link_path)
                print(f"Resolved symlink: {filepath} -> {target_str}")
            except OSError:
                # Fallback to hard copy if symlinks are not supported on this host/OS
                import shutil
                if target_path.is_dir():
                    shutil.copytree(target_path, link_path)
                else:
                    shutil.copy2(target_path, link_path)
                print(f"Resolved copy (fallback): {filepath} <- content of {target_str}")
            resolved_count += 1
        except Exception as e:
            print(f"Failed to resolve symlink {filepath}: {e}", file=sys.stderr)
            failed_count += 1

    print(f"Done. Resolved: {resolved_count}, Failed: {failed_count}")
    return failed_count == 0

if __name__ == "__main__":
    success = resolve_symlinks()
    sys.exit(0 if success else 1)
