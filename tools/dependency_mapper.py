import os
import re
import json
from pathlib import Path

def generate_dependency_graph(root_dir):
    graph = {}
    py_import_re = re.compile(r"^(?:from|import)\s+([\w\.]+)")
    md_link_re = re.compile(r"\[\[([^\]]+)\]\]|\[[^\]]+\]\(([^\)]+\.md)\)")

    for root, _, files in os.walk(root_dir):
        if any(x in root for x in [".git", ".venv", "__pycache__", "upgrades/backups"]):
            continue
        
        for file in files:
            path = Path(root) / file
            rel_path = path.relative_to(root_dir)
            deps = set()

            if file.endswith(".py"):
                try:
                    content = path.read_text(errors="ignore")
                    for line in content.splitlines():
                        match = py_import_re.match(line.strip())
                        if match:
                            # Convert module path to likely file path
                            mod = match.group(1).replace(".", "/")
                            # Simple heuristic: check if it matches a local file
                            possible_py = Path(root_dir) / f"{mod}.py"
                            if possible_py.exists():
                                deps.add(str(possible_py.relative_to(root_dir)))
                            possible_dir = Path(root_dir) / mod / "__init__.py"
                            if possible_dir.exists():
                                deps.add(str(possible_dir.relative_to(root_dir)))
                except Exception:
                    pass
            
            elif file.endswith(".md"):
                try:
                    content = path.read_text(errors="ignore")
                    for match in md_link_re.finditer(content):
                        ref = match.group(1) or match.group(2)
                        if ref:
                            # Normalize path
                            ref_path = (Path(root) / ref).resolve()
                            if str(ref_path).startswith(str(root_dir)) and ref_path.exists():
                                deps.add(str(ref_path.relative_to(root_dir)))
                except Exception:
                    pass
            
            if deps:
                graph[str(rel_path)] = list(deps)
    
    return graph

if __name__ == "__main__":
    nina_root = Path(__file__).parent.parent.resolve()
    graph = generate_dependency_graph(nina_root)
    output_path = nina_root / "data" / "dependency_graph.json"
    output_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Lightspeed dependency graph generated at {output_path}")
