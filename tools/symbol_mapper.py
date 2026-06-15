#!/usr/bin/env python3
import os
import ast
import json
from pathlib import Path

def generate_symbol_map(root_dir):
    symbol_map = {}
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".agent", ".jules", ".pytest_cache", ".mypy_cache", "upgrades/backups"}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            if not file.endswith(".py"):
                continue
                
            path = Path(root) / file
            rel_path = str(path.relative_to(root_dir))
            
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(path))
                
                file_symbols = {
                    "classes": {},
                    "functions": {}
                }
                
                # Walk the module AST body directly to extract class definitions and top-level functions
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        methods = []
                        for subnode in node.body:
                            if isinstance(subnode, ast.FunctionDef):
                                methods.append({
                                    "name": subnode.name,
                                    "line": subnode.lineno,
                                    "docstring": ast.get_docstring(subnode) or ""
                                })
                        
                        file_symbols["classes"][node.name] = {
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node) or "",
                            "methods": methods
                        }
                    elif isinstance(node, ast.FunctionDef):
                        file_symbols["functions"][node.name] = {
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node) or ""
                        }
                
                if file_symbols["classes"] or file_symbols["functions"]:
                    symbol_map[rel_path] = file_symbols
            except Exception:
                pass
                
    return symbol_map

if __name__ == "__main__":
    nina_root = Path(__file__).parent.parent.resolve()
    symbol_map = generate_symbol_map(nina_root)
    output_path = nina_root / "data" / "symbol_map.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(symbol_map, indent=2), encoding="utf-8")
    print(f"Semantic symbol map generated at {output_path}")
