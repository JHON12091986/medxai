import json, os, hashlib
from pathlib import Path

def get_hash(path):
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except:
        return None

def scan():
    repo_root = Path("/home/aibony/nina")
    governed_files = []
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".agent", ".jules", ".pytest_cache", ".mypy_cache"}
    
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(repo_root)
            path_str = str(rel_path)
            
            category = "other"
            if rel_path.suffix == ".md": category = "doc"
            elif rel_path.suffix == ".py": category = "code"
            elif rel_path.suffix == ".sh": category = "script"
            elif rel_path.suffix == ".json": category = "config"
            
            if path_str.startswith("logs/"): category = "log"
            elif path_str.startswith("exports/"): category = "export"
            elif path_str.startswith("upgrades/backups"): category = "backup"
            elif path_str.startswith("upgrades/incidents"): category = "incident"
            
            lifecycle = "active"
            if category in ["backup", "incident"]: lifecycle = "archived"
            if category == "export": lifecycle = "generated"
            if rel_path.name.endswith(".bak") or ".bak_" in rel_path.name: lifecycle = "deprecated"
            
            role = "source_of_truth"
            if path_str in ["nina_update_log.md", "docs/space/nina_error_register.md", "data/memory/facts.json", "jules_lock.txt"]:
                role = "system_of_record"
            elif lifecycle in ["archived", "deprecated"]:
                role = "archive"
            elif lifecycle == "generated" or category == "export":
                role = "generated"
            elif category == "log":
                role = "derived"
                
            origin = "manual"
            if category == "incident": origin = "guardian"
            elif category == "backup": origin = "script:backup"
            elif category == "export": origin = "script:sync"
            elif path_str in ["docs/space/nina_index.json", "docs/space/nina_index.md"]: origin = "script:update_index"
            
            retention_policy = "keep"
            if category == "log": retention_policy = "rotate"
            elif category == "backup": retention_policy = "keep_latest_n: 10"
            elif category == "incident": retention_policy = "purge_candidate"
            elif category == "export": retention_policy = "ephemeral"
            
            # Series tracking
            series_id = None
            series_type = None
            if category in ["backup", "incident"]:
                series_type = category
                parts = Path(path_str).parts
                if len(parts) >= 3:
                    series_id = parts[2]
            
            # Test & Doc Requirements
            requires_tests = False
            if category == "code" and lifecycle == "active" and not path_str.startswith("tests/") and not path_str.startswith("ninagate/"):
                if path_str.startswith("core/") or path_str.startswith("tools/") or path_str.startswith("crons/") or path_str.startswith("interfaces/"):
                    if not path_str.endswith("__init__.py"):
                        requires_tests = True
                        
            doc_required = False
            if category == "code" and lifecycle == "active":
                doc_required = True
            
            governed_files.append({
                "path": path_str,
                "category": category,
                "role": role,
                "governed": True,
                "canonical": True,
                "lifecycle": lifecycle,
                "retention_policy": retention_policy,
                "origin": origin,
                "owner": "system" if origin != "manual" else "engineering",
                "duplicate_cluster_id": None,
                "series_id": series_id,
                "series_type": series_type,
                "requires_tests": requires_tests,
                "doc_required": doc_required,
                "summary": "",
                "tags": [category, role, lifecycle],
                "hash": get_hash(full_path)
            })
    return governed_files

summaries = {
    "nina_update_log.md": "Canonical live activity log (Entry 001-167). Newest entries at top.",
    "nina_context.md": "AI session grounding profile & architecture context. Attach to new threads.",
    "README.md": "Human-facing project overview, agent model, and installation guide.",
    "ARCHITECTURE.md": "High-level system design and logic flow map.",
    "AGENTS.md": "Agent Operating Law (permissions and scopes for Jules, agy, etc).",
    "WORKFLOW.md": "Repository rules of engagement and development lifecycle.",
    "CHANGELOG.md": "User-friendly summary of major version releases.",
    "guardian_engine.py": "Forensic AST scanner and baseline drift analyzer (73KB).",
    "main.py": "Primary entry point for the NINA systemd service.",
    "healthcheck.py": "Pre-deployment health and dependency verification suite.",
    "nina_sync.sh": "Post-session synchronization and deployment script.",
    "core/": "System orchestrator, router, memory, and config modules.",
    "tools/": "Capability kernel and domain-specific action modules (agynina nucleus).",
    "interfaces/": "Telegram and REST API communication layers.",
    "docs/": "Subsystem-level deep-dives (Guardian, Memory, Router, agynina).",
    "docs/space/": "Active operational workspace (Backlog, Error Register, State).",
    "data/memory/facts.json": "Immutable personal identity anchor (Owner facts).",
    "upgrades/backups/": "Automated system snapshots and recovery artifacts.",
    "upgrades/incidents/": "Forensic logs and evidence from Guardian interventions.",
    "docs/space/nina_index.md": "Canonical repository index (this document).",
    "docs/space/nina_index.json": "Machine-readable repository index companion.",
    "tools/validate_index.py": "Automated validator for repository index consistency.",
    "tools/update_index.py": "Utility to regenerate the repository index.",
    "tools/query_index.py": "Agent API to query file governance status.",
    "tools/cleanup_by_index.py": "Safe dry-run cleanup planner based on retention policies.",
}

def generate_index():
    files = scan()
    
    hash_map = {}
    for f in files:
        h = f["hash"]
        if h:
            if h not in hash_map: hash_map[h] = []
            hash_map[h].append(f)
            
    duplicate_clusters = []
    cluster_counter = 1
    
    for h, members in hash_map.items():
        if len(members) > 1:
            cluster_id = f"dup-{cluster_counter:04d}"
            cluster_counter += 1
            
            active_members = sorted([m for m in members if m["lifecycle"] == "active"], key=lambda x: len(x["path"]))
            canonical_path = active_members[0]["path"] if active_members else members[0]["path"]
            
            for m in members:
                m["duplicate_cluster_id"] = cluster_id
                if m["path"] != canonical_path:
                    m["canonical"] = False
                    if m["lifecycle"] == "active":
                        m["lifecycle"] = "deprecated"
                        
            duplicate_clusters.append({
                "cluster_id": cluster_id,
                "canonical_path": canonical_path,
                "members": [m["path"] for m in members],
                "reason": "exact_md5_duplicate"
            })

    for f in files:
        del f["hash"] 
        f["summary"] = summaries.get(f["path"], summaries.get(f["path"].split("/")[0] + "/", "Governed artifact."))

    index_data = {
        "version": "1.2",
        "updated": "2026-06-10",
        "governed_scope": "All docs under docs/ and docs/space/, shims/scripts under tools/, configs (*.service, requirements.txt, .env.example), exported snapshots in exports/ and logs. Excludes temp data and cache.",
        "files": files,
        "duplicate_clusters": duplicate_clusters
    }

    with open("docs/space/nina_index.json", "w") as f:
        json.dump(index_data, f, indent=2)

    md_content = """# NINA Repository Index
_Single Source of Truth for File Inventory & Governance_

## 1. Overview & Scope
This index tracks all governed artifacts in the NINA repository.
- **Governed:** true. Includes docs, tools, scripts, configs, exports, and persistent logs.
- **Unmanaged:** Excludes `__pycache__`, `.venv`, `.git`, transient temp files.

## 2. File Inventory
| Path | Role | Lifecycle | Retention | Summary | Canonical |
|------|------|-----------|-----------|---------|-----------|
"""

    root_items = sorted([f for f in files if "/" not in f["path"]], key=lambda x: x["path"])
    for item in root_items:
        path = item["path"]
        summary = item["summary"]
        is_canonical = "✅ YES" if item["canonical"] else "NO"
        md_content += f"| `{path}` | {item['role']} | {item['lifecycle']} | {item['retention_policy']} | {summary} | {is_canonical} |\n"

    dirs = sorted(list(set([f["path"].split("/")[0] for f in files if "/" in f["path"]])))
    for d in dirs:
        path = d + "/"
        summary = summaries.get(path, f"Subsystem directory containing {path[:-1]} logic/docs.")
        md_content += f"| `{path}` | subsystem | active | keep | {summary} | ✅ YES |\n"

    md_content += """
## 3. Redundancy & Conflicts
The following clusters contain identical content. Consolidate to the canonical source where possible.

"""
    for cluster in duplicate_clusters:
        if 1 < len(cluster["members"]) < 10:
            md_content += f"- **Cluster `{cluster['cluster_id']}`**: Canonical is `{cluster['canonical_path']}`. Members: " + ", ".join([f"`{p}`" for p in cluster["members"]]) + "\n"

    md_content += """
## 4. Governance Rules & Index-First Workflow
1. **Check the Index:** `python3 tools/query_index.py --path <file>`
2. **Duplicate Clusters:** When writing to a path that belongs to a duplicate cluster, you MUST only write to the `canonical_path`.
3. **Index Modification:** If creating/moving a governed file:
   - Run `python3 tools/update_index.py`.
   - Run `python3 tools/validate_index.py`.
4. **Validation:** No PR touching governed paths is "Done" unless `validate_index.py` passes.
5. **Contract:** The index is the single enforceable contract for doc/log/code inventory.

---
_Generated by NINA Indexer on 2026-06-10_
"""
    with open("docs/space/nina_index.md", "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_index()
    print("Index updated with full governance schema.")
