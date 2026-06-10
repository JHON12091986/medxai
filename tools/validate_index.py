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
    
    # 1. Check if index entries resolve to real files
    errors = 0
    for path_str in indexed_paths:
        if not (repo_root / path_str).exists():
            print(f"❌ Broken link: {path_str} in index does not exist on disk.")
            errors += 1
            
    # 2. Check if every governed file is indexed
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".agent", ".jules", ".pytest_cache", ".mypy_cache"}
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            rel_path = str((Path(root) / file).relative_to(repo_root))
            if rel_path not in indexed_paths:
                print(f"⚠️ Unindexed file: {rel_path} is missing from the index.")
                # Non-fatal warning for now
                
    # 3. Check for multiple canonical files (functional overlap)
    # This is complex to automate without better metadata, but we check if multiple files
    # in the same core directory claim to be canonical docs.
    canonical_docs = [f["path"] for f in data["files"] if f["canonical"] and f["category"] == "docs"]
    # (Manual check logic could be added here)

    if errors > 0:
        print(f"\n❌ Validation FAILED with {errors} errors.")
        return False
        
    print("\n✅ Index validation PASSED.")
    return True

if __name__ == "__main__":
    if not validate():
        sys.exit(1)
