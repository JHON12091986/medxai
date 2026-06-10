import json, argparse, sys

def query(path):
    with open("docs/space/nina_index.json") as f:
        data = json.load(f)
        
    for file_obj in data["files"]:
        if file_obj["path"] == path:
            print(f"🔍 Governance Profile: {path}")
            print(f"  - Summary:    {file_obj.get('summary')}")
            print(f"  - Category:   {file_obj.get('category')} / {file_obj.get('lifecycle')}")
            print(f"  - Role:       {file_obj.get('role')} (Canonical: {file_obj.get('canonical')})")
            print(f"  - Governed:   {file_obj.get('governed')}")
            print(f"  - Retention:  {file_obj.get('retention_policy')}")
            print(f"  - Tests Req:  {file_obj.get('requires_tests', False)}")
            if file_obj.get("series_id"):
                print(f"  - Series ID:  {file_obj.get('series_id')} ({file_obj.get('series_type')})")
            if file_obj.get("duplicate_cluster_id"):
                print(f"  - Cluster ID: {file_obj.get('duplicate_cluster_id')}")
            return
            
    print(f"❌ Path '{path}' not found in index. It may be unmanaged.")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Path to query in the index")
    args = parser.parse_args()
    query(args.path)
