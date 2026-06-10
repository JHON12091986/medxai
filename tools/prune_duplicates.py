import json, os, argparse
from pathlib import Path

def prune(execute=False):
    repo_root = Path("/home/aibony/nina")
    index_path = repo_root / "docs/space/nina_index.json"
    
    if not index_path.exists():
        print("❌ Error: nina_index.json not found.")
        return
        
    with open(index_path, "r") as f:
        data = json.load(f)
        
    to_delete = []
    
    print("🔍 NINA Safe Duplicate Pruner")
    print("------------------------------------------------")
    
    for cluster in data.get("duplicate_clusters", []):
        canonical = cluster.get("canonical_path", "")
        
        # Rule 1: Canonical must be a live file (not an upgrade backup or incident)
        if canonical.startswith("upgrades/"):
            continue
            
        # Identify members that are safe to delete (must be in upgrades/)
        members_to_prune = []
        for member in cluster.get("members", []):
            if member != canonical and member.startswith("upgrades/"):
                members_to_prune.append(member)
                
        if members_to_prune:
            print(f"📦 Cluster {cluster['cluster_id']} (Canonical: {canonical})")
            for m in members_to_prune:
                print(f"   🗑️  Marked for deletion: {m}")
                to_delete.append(repo_root / m)
                
    print("------------------------------------------------")
    print(f"Total safe non-canonical duplicates identified: {len(to_delete)}")
    
    if not execute:
        print("\n⚠️  DRY RUN MODE. No files were deleted.")
        print("Run with --execute to perform the deletion.")
        return
        
    print("\n🚀 EXECUTING DELETION...")
    deleted_count = 0
    for file_path in to_delete:
        try:
            if file_path.exists():
                file_path.unlink()
                deleted_count += 1
        except Exception as e:
            print(f"❌ Failed to delete {file_path}: {e}")
            
    print(f"✅ Successfully deleted {deleted_count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune non-canonical backup/incident duplicates.")
    parser.add_argument("--execute", action="store_true", help="Actually delete the files.")
    args = parser.parse_args()
    prune(args.execute)
