#!/usr/bin/env python3
"""
Syncs the keys required/optional by NinaConfig with .env and .env.example
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import NinaConfig

def main():
    required_keys = NinaConfig.REQUIRED_KEYS
    optional_keys = list(NinaConfig.OPTIONAL_KEYS.keys())
    all_config_keys = required_keys + optional_keys

    for file_path in [".env", ".env.example"]:
        existing_keys = set()
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key = line.split("=")[0]
                        existing_keys.add(key)

        missing_keys = [k for k in all_config_keys if k not in existing_keys]

        if missing_keys:
            mode = "a" if os.path.exists(file_path) else "w"
            with open(file_path, mode) as f:
                f.write("\n# Automatically added by tools/nina_env_sync.py\n")
                for key in missing_keys:
                    f.write(f'{key}=""\n')
            print(f"✅ Updated {file_path} with {len(missing_keys)} missing keys.")
        else:
            print(f"✅ {file_path} is up to date.")

if __name__ == "__main__":
    main()
