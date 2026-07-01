#!/usr/bin/env python3
"""
Sync Environment Variables

Parses core/config.py for all expected environment variables and updates
.env and .env.example if any keys are missing.
"""

import ast
from pathlib import Path

def get_all_env_vars_from_config(config_path: str) -> list[str]:
    content = Path(config_path).read_text()
    tree = ast.parse(content)

    keys = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NinaConfig":
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    if isinstance(stmt.target, ast.Name):
                        if stmt.target.id == "REQUIRED_KEYS":
                            if isinstance(stmt.value, ast.List):
                                for elt in stmt.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        keys.add(elt.value)
                        elif stmt.target.id == "OPTIONAL_KEYS":
                            if isinstance(stmt.value, ast.Dict):
                                for key in stmt.value.keys:
                                    if isinstance(key, ast.Constant):
                                        keys.add(key.value)

        if isinstance(node, ast.FunctionDef) and node.name == "load_config":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "env_keys":
                            if isinstance(stmt.value, ast.Dict):
                                for v in stmt.value.values:
                                    if isinstance(v, ast.Constant):
                                        keys.add(v.value)
                if isinstance(stmt, ast.Call):
                    if isinstance(stmt.func, ast.Name) and stmt.func.id == "get_secret":
                        if stmt.args and isinstance(stmt.args[0], ast.Constant):
                            keys.add(stmt.args[0].value)

    return sorted(list(k for k in keys if isinstance(k, str) and k))

def update_env_file(env_path: str, all_keys: list[str]) -> None:
    env_file = Path(env_path)
    if not env_file.exists():
        lines = []
    else:
        lines = env_file.read_text().splitlines()

    existing_keys = set()
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                existing_keys.add(key)

    new_lines = list(lines)
    added_keys = []

    for key in all_keys:
        if key not in existing_keys:
            added_keys.append(key)

    if added_keys:
        new_lines.append("")
        new_lines.append("# Auto-added missing keys")
        for key in added_keys:
            new_lines.append(f'{key}=""')
        env_file.write_text("\n".join(new_lines) + "\n")
        print(f"Updated {env_path} (added {len(added_keys)} keys)")
    else:
        print(f"No new keys to add to {env_path}")

def main():
    config_path = "core/config.py"
    if not Path(config_path).exists():
        print(f"Error: {config_path} not found.")
        return

    keys = get_all_env_vars_from_config(config_path)
    if not keys:
        print("Warning: No keys found in config.")
        return

    print(f"Found {len(keys)} environment variables in config.")
    update_env_file(".env", keys)
    update_env_file(".env.example", keys)

if __name__ == "__main__":
    main()
