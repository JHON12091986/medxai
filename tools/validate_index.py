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
    
    # Metrics for quality scoring
    total_files = 0
    total_score = 0
    missing_tests = 0
    
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
                
        # Test coverage validation
        if file_obj.get("requires_tests"):
            p = Path(path_str)
            # Try basic mappings like core/router.py -> tests/test_router.py
            test_path = repo_root / "tests" / f"test_{p.stem}.py"
            # Some tests are combined (e.g. test_finance_market.py) so we don't throw hard errors, just warnings
            if not test_path.exists() and not any(p.stem in t for t in os.listdir(repo_root / "tests")):
                warnings += 1
                missing_tests += 1
                print(f"⚠️ Test Coverage: {path_str} requires tests but no obvious test_{p.stem}.py found.")
                
        # Metadata Quality Score calculation
        score = 0
        if file_obj.get("summary") and file_obj["summary"] != "Governed artifact.": score += 1
        if file_obj.get("role"): score += 1
        if file_obj.get("origin"): score += 1
        if file_obj.get("retention_policy"): score += 1
        if file_obj.get("tags"): score += 1
        
        total_score += (score / 5.0)
        total_files += 1
                
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

    quality_pct = (total_score / total_files) * 100 if total_files else 0
    if quality_pct < 75.0:
        print(f"❌ Metadata Quality Score ({quality_pct:.1f}%) is below the required 75.0% threshold.")
        errors += 1

    if errors > 0:
        print(f"\n❌ Validation FAILED with {errors} errors and {warnings} warnings.")
        print(f"📊 Metadata Quality Score: {quality_pct:.1f}%")
        print(f"🧪 Missing Tests: {missing_tests}")
        return False
        
    print(f"\n✅ Index validation PASSED ({warnings} warnings).")
    print(f"📊 Metadata Quality Score: {quality_pct:.1f}%")
    print(f"🧪 Missing Tests: {missing_tests}")
    return True


if __name__ == "__main__":
    if not validate():
        sys.exit(1)
