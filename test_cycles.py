import ast
from pathlib import Path

def get_module_name(file_path, root):
    rel_path = file_path.relative_to(root)
    if rel_path.name == "__init__.py":
        return ".".join(rel_path.parent.parts)
    else:
        return ".".join(rel_path.with_suffix("").parts)

p1 = Path("foo/bar/__init__.py")
p2 = Path("foo/bar/baz.py")

print("p1 name:", get_module_name(p1, Path(".")))
print("p2 name:", get_module_name(p2, Path(".")))
