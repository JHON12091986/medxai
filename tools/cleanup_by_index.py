import json
from pathlib import Path

def run_cleanup_plan():
    with open("docs/space/nina_index.json") as f:
        data = json.load(f)
        
    print("🧹 NINA Cleanup Plan (DRY RUN)\n")
    
    purge = []
    dedupe = []
    
    for f in data["files"]:
        # Rule 1: Purge candidates and ephemerals
        if f.get("retention_policy") in ["purge_candidate", "ephemeral"]:
            purge.append(f["path"])
            
        # Rule 2: Duplicate members that are NOT canonical
        if f.get("duplicate_cluster_id") and not f.get("canonical"):
            dedupe.append(f["path"])
            
    if not purge and not dedupe:
        print("✨ System is clean! No files match purge or dedupe rules.")
        return

    print("### Commands to execute:\n")
    
    if purge:
        print("# 1. Purge candidates & ephemeral files")
        for p in purge:
            print(f"rm -rf {p}")
            
    if dedupe:
        print("\n# 2. Redundant duplicates (keep canonical only)")
        for p in dedupe:
            print(f"git rm {p}  # or rm if untracked")
            
    print("\n⚠️ Note: Review carefully before running. Some incidents might be needed for debugging.")

if __name__ == "__main__":
    run_cleanup_plan()
