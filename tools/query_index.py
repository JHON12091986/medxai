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
            if file_obj.get("guardrails"):
                print(f"  - Guardrails: {', '.join(file_obj.get('guardrails'))}")
                print("\n  ⚠️ AGENT UX TEMPLATES (ENFORCED RULES):")
                for gr in file_obj.get("guardrails"):
                    if gr == "high_risk_do_not_edit_directly":
                        print("    [high_risk_do_not_edit_directly]")
                        print("    - Reason: Core runtime logic or config. Direct edits risk system crash.")
                        print("    - Allowed: Read, analyze, propose changes via PR.")
                        print("    - Forbidden: Direct file edits via CLI/script.")
                        print("    - Human Next Step: Review proposed PR or apply manually.\n")
                    elif gr == "append_only":
                        print("    [append_only]")
                        print("    - Reason: Historical or sequential log.")
                        print("    - Allowed: Append new entries to the end of the file.")
                        print("    - Forbidden: Editing or deleting past entries.")
                        print("    - Human Next Step: N/A (Agent can append freely).\n")
                    elif gr == "read_only_for_agents":
                        print("    [read_only_for_agents]")
                        print("    - Reason: Immutable identity or critical architectural truth.")
                        print("    - Allowed: Read and use for context.")
                        print("    - Forbidden: Any write operations.")
                        print("    - Human Next Step: Edit manually if architecture or identity changes.\n")

            if not file_obj.get("canonical"):
                cluster_id = file_obj.get("duplicate_cluster_id")
                # find canonical path for this cluster
                canonical_path = "UNKNOWN"
                for c in data.get("duplicate_clusters", []):
                    if c["cluster_id"] == cluster_id:
                        canonical_path = c["canonical_path"]
                        break
                        
                print("\n  ⚠️ AGENT UX TEMPLATE (NON-CANONICAL):")
                print("    [non_canonical_duplicate]")
                print("    - Reason: This file belongs to a duplicate cluster but is NOT the canonical source.")
                print(f"    - Allowed: Read for context, OR write to the canonical path: {canonical_path}.")
                print("    - Forbidden: Writing to this specific non-canonical file.")
                print(f"    - Human Next Step: Consider running dedupe to remove {path}.\n")
                
            return
            
    print(f"❌ Path '{path}' not found in index. It may be unmanaged.")
    print("\n  ⚠️ AGENT UX TEMPLATE (UNMANAGED):")
    print("    [unmanaged_governed_file]")
    print("    - Reason: This file is missing from the governance index but appears to be a governed artifact.")
    print("    - Allowed: Update `tools/update_index.py` to track this file.")
    print("    - Forbidden: Proceeding with edits before the file is properly indexed.")
    print("    - Human Next Step: Ensure the file is added to the index and `validate_index.py` passes.\n")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Path to query in the index")
    args = parser.parse_args()
    query(args.path)
