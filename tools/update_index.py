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
            category = "other"
            if rel_path.suffix == ".md": category = "docs"
            elif rel_path.suffix == ".py": category = "code"
            elif rel_path.suffix == ".sh": category = "scripts"
            elif rel_path.suffix == ".json": category = "data/config"
            elif str(rel_path).startswith("logs/"): category = "logs"
            elif str(rel_path).startswith("exports/"): category = "exports"
            elif str(rel_path).startswith("upgrades/backups"): category = "backups"
            elif str(rel_path).startswith("upgrades/incidents"): category = "incidents"
            lifecycle = "active"
            if category in ["backups", "incidents"]: lifecycle = "archived"
            if category == "exports": lifecycle = "generated"
            if rel_path.name.endswith(".bak") or ".bak_" in rel_path.name: lifecycle = "deprecated"
            
            governed_files.append({
                "path": str(rel_path),
                "category": category,
                "lifecycle": lifecycle,
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
    "tools/update_index.py": "Utility to regenerate the repository index."
}

def generate_index():
    files = scan()
    hash_map = {}
    for f in files:
        h = f["hash"]
        if h:
            if h not in hash_map: hash_map[h] = []
            hash_map[h].append(f["path"])
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

    for f in files:
        f["summary"] = summaries.get(f["path"], summaries.get(f["path"].split("/")[0] + "/", "Governed artifact."))
        f["canonical"] = (f["lifecycle"] == "active")

    index_data = {
        "version": "1.0",
        "updated": "2026-06-10",
        "files": files,
        "duplicate_clusters": duplicates
    }

    with open("docs/space/nina_index.json", "w") as f:
        json.dump(index_data, f, indent=2)

    md_content = """# NINA Repository Index
_Single Source of Truth for File Inventory & Governance_

## 1. Overview
This index tracks all governed artifacts in the NINA repository. It is the primary discovery point for both humans and AI agents.

## 2. File Inventory
| Path | Category | Lifecycle | Summary | Canonical |
|------|----------|-----------|---------|-----------|
"""

    root_items = sorted([f for f in files if "/" not in f["path"]], key=lambda x: x["path"])
    for item in root_items:
        path = item["path"]
        summary = summaries.get(path, "Root artifact.")
        is_canonical = "✅ YES" if item["lifecycle"] == "active" else "NO"
        md_content += f"| `{path}` | {item['category']} | {item['lifecycle']} | {summary} | {is_canonical} |\n"

    dirs = sorted(list(set([f["path"].split("/")[0] for f in files if "/" in f["path"]])))
    for d in dirs:
        path = d + "/"
        summary = summaries.get(path, f"Subsystem directory containing {path[:-1]} logic/docs.")
        md_content += f"| `{path}` | directory | active | {summary} | ✅ YES |\n"

    md_content += """
## 3. Redundancy & Conflicts
The following clusters contain identical content. Consolidate to the canonical source where possible.

"""
    for h, paths in duplicates.items():
        if 1 < len(paths) < 10:
            md_content += f"- **Cluster `{h[:8]}`**: " + ", ".join([f"`{p}`" for p in paths]) + "\n"

    md_content += """
## 4. Governance Rules
1. **Creation:** Every new file must be added to this index.
2. **Move/Rename:** Update the path and lifecycle status.
3. **Deletion:** Mark as `archived` or remove from index if safe.
4. **Canonical:** Only one active canonical file should exist per functional role.

---
_Generated by NINA Indexer on 2026-06-10_
"""
    with open("docs/space/nina_index.md", "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_index()
    print("Index updated.")
