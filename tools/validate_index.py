import json, os, sys
from pathlib import Path

def validate():
    repo_root = Path("/home/aibony/nina")
    index_path = repo_root / "docs/space/nina_index.json"
    
    if not index_path.exists():
        print("❌ Error: nina_index.json not found.")
        return False
        
    with open(index_path, "r") as f:
        data = json.load(f)
        
    indexed_paths = {f["path"] for f in data["files"]}
    
    errors = 0
    warnings = 0
    
    # 1. Check if index entries resolve to real files and validate schema
    for file_obj in data["files"]:
        path_str = file_obj["path"]
        if not (repo_root / path_str).exists():
            print(f"❌ Broken link: {path_str} in index does not exist on disk.")
            errors += 1
            
        # Schema validation
        required_keys = ["category", "role", "governed", "lifecycle", "retention_policy"]
        for key in required_keys:
            if key not in file_obj:
                print(f"❌ Schema error: '{key}' missing from entry {path_str}")
                errors += 1
                
    # 2. Check for "unmanaged but probably governed" files
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".agent", ".jules", ".pytest_cache", ".mypy_cache"}
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            rel_path = str((Path(root) / file).relative_to(repo_root))
            
            # If it's a doc, core logic, tool, or root script, it should be indexed
            if rel_path not in indexed_paths:
                if rel_path.endswith(".md") or rel_path.endswith(".py") or rel_path.endswith(".sh") or rel_path.startswith("docs/"):
                    print(f"⚠️ Unmanaged but probably governed: {rel_path} is missing from the index.")
                    warnings += 1

    if errors > 0:
        print(f"\n❌ Validation FAILED with {errors} errors and {warnings} warnings.")
        return False
        
    print(f"\n✅ Index validation PASSED ({warnings} warnings).")
    return True

if __name__ == "__main__":
    if not validate():
        sys.exit(1)
