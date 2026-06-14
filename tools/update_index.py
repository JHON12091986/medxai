import json, os, hashlib, ast, sys, subprocess
from pathlib import Path
from datetime import datetime

def get_hash(path):
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except:
        return None

def scan():
    repo_root = Path(__file__).parent.parent.resolve()
    governed_files = []
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".agent", ".jules", ".pytest_cache", ".mypy_cache"}
    
    # Pre-fetch test filenames for faster lookup
    test_files = set()
    if (repo_root / "tests").exists():
        test_files = {f for f in os.listdir(repo_root / "tests") if f.startswith("test_")}

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
            elif category == "backup":
                role = "backup"
                
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
            
            # --- Reconciliation Logic (Exemptions) ---
            if requires_tests:
                # Check for existing test file
                has_test = f"test_{rel_path.stem}.py" in test_files or \
                           any(rel_path.stem in t for t in test_files)
                
                if not has_test:
                    # Apply exemptions for infra/tooling/entrypoints
                    try:
                        content = full_path.read_text(encoding="utf-8")
                        if any(path_str.startswith(d + "/") for d in ["crons", "tools", "scripts"]):
                            if 'if __name__ == "__main__":' in content:
                                tree = ast.parse(content)
                                funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                                if len(funcs) <= 3:
                                    requires_tests = False
                        
                        if path_str.startswith("interfaces/") and ("interface" in path_str.lower() or "api" in path_str.lower()):
                            if "class " not in content and "def " not in content:
                                requires_tests = False
                    except:
                        pass

            doc_required = False
            if category == "code" and lifecycle == "active":
                doc_required = True
                
            # Guardrails definition
            guardrails = []
            if category == "code" and path_str.startswith("core/"): guardrails.append("strict_typing")
            if path_str in ["core/router.py", "main.py", "guardian_engine.py"]: guardrails.append("high_risk_review")
            
            governed_files.append({
                "path": path_str,
                "category": category,
                "role": role,
                "governed": True,
                "lifecycle": lifecycle,
                "origin": origin,
                "retention_policy": retention_policy,
                "series_id": series_id,
                "series_type": series_type,
                "requires_tests": requires_tests,
                "doc_required": doc_required,
                "guardrails": guardrails,
                "summary": "Governed artifact.",
                "hash": get_hash(full_path),
                "tags": [category, lifecycle, role]
            })
            
    return governed_files

def generate_index():
    files = scan()
    index_data = {
        "version": "14.3",
        "generated_at": datetime.now().isoformat(),
        "repo": "NINA",
        "files": sorted(files, key=lambda x: x["path"])
    }
    
    with open("docs/space/nina_index.json", "w") as f:
        json.dump(index_data, f, indent=2)
        
    md_content = f"""# NINA Repository Index
_Single Source of Truth for File Inventory & Governance_

## 1. Overview & Scope
This index tracks all governed artifacts in the NINA repository.
- **Governed:** true. Includes docs, tools, scripts, configs, exports, and persistent logs.
- **Unmanaged:** Excludes `__pycache__`, `.venv`, `.git`, transient temp files.

## 2. File Inventory
| Path | Role | Lifecycle | Retention | Summary | Canonical |
|------|------|-----------|-----------|---------|-----------|
"""
    for f in index_data["files"]:
        md_content += f"| `{f['path']}` | {f['role']} | {f['lifecycle']} | {f['retention_policy']} | {f['summary']} | ✅ YES |\n"
        
    md_content += f"""
## 3. Core Document Inventory (v14.2)
| Path | Summary | Lifecycle |
|:-----|:--------|:----------|
| `README.md` | Human-facing project overview, agent model, and installation guide. | active |
| `ARCHITECTURE.md` | High-level system design and logic flow map. | active |
| `CHANGELOG.md` | User-friendly summary of major version releases. | active |
| `AGENTS.md` | Agent Operating Law (permissions and scopes for Jules, agy, etc). | active |
| `nina_context.md` | AI session grounding profile & architecture context. Attach to new threads. | active |
| `docs/nina_v14_blueprint.md` | Canonical v14.2 system blueprint and component map. | active |
| `docs/space/nina_state.md` | Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash). | active |
| `docs/space/nina_megatask_index.md` | Subsystem-level deep-dives (Guardian, Memory, Router, ninaflash). | active |

---
_Generated by NINA Indexer on {datetime.now().strftime('%Y-%m-%d')}_
"""
    with open("docs/space/nina_index.md", "w") as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_index()
    print("Index updated with full governance schema.")
