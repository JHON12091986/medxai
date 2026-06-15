import json, os, sys, argparse, subprocess
from pathlib import Path

def check_doc_deltas(data, repo_root):
    try:
        # Check against HEAD~1 for push, or origin/main for PR. 
        base = os.environ.get("GITHUB_BASE_REF")
        if base:
            cmd = ["git", "diff", "--name-only", f"origin/{base}...HEAD"]
        else:
            cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
        
        result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  Skipping doc delta check (git diff failed - likely no previous commit).")
            return True
            
        changed_files = result.stdout.strip().split("\n")
        changed_files = [f for f in changed_files if f]
    except Exception as e:
        print(f"⚠️  Skipping doc delta check (error: {e})")
        return True

    doc_targets_changed = set()
    requires_delta = []
    
    indexed_files = {f["path"]: f for f in data["files"]}
    
    for f in changed_files:
        if f in indexed_files:
            file_obj = indexed_files[f]
            if file_obj.get("doc_delta_required"):
                requires_delta.append(file_obj)
            # Check if this changed file is a target for anything
            if f in ["nina_update_log.md", "CHANGELOG.md", "docs/space/jules_backlog.md", "docs/space/nina_error_register.md", "docs/space/nina_state.md"]:
                doc_targets_changed.add(f)
                
    if requires_delta and not doc_targets_changed:
        print(f"\n❌ Governance Violation: Code/architecture changed but no documentation delta was found.")
        print("The following files require a doc delta:")
        for file_obj in requires_delta:
            print(f"  - {file_obj['path']} (Targets: {', '.join(file_obj.get('doc_targets', []))})")
        print("\nPlease add an entry to nina_update_log.md (or equivalent) before merging.")
        return False
        
    return True

def notify_telegram(message, repo_root):
    from dotenv import load_dotenv
    load_dotenv(repo_root / ".env")
    bot_token = os.environ.get("TELEGRAMBOTTOKEN")
    chat_id = os.environ.get("TELEGRAMCHATID")
    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not found in environment. Skipping notification.")
        return
        
    import urllib.request
    import urllib.parse
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ Telegram notification sent successfully.")
            else:
                print(f"❌ Failed to send Telegram notification: {response.status}")
    except Exception as e:
        print(f"❌ Exception sending Telegram notification: {e}")

def reconcile_tests(data, repo_root):
    import ast

    # Directories where CLI-entrypoint scripts live and don't need unit tests
    EXEMPT_DIRS = ["crons", "tools", "scripts", "bin", "checks"]
    # Filename patterns that are always infra, never logic-bearing
    EXEMPT_STEMS = {
        "update_index", "validate_index", "query_index", "cleanup_by_index",
        "rule0_audit", "gemini_watch", "telegram_notify", "nina_sync",
        "ninagate_info", "session_ledger", "provider_health", "quota_alert",
        "bench_runner", "ninaflash_bench", "post_task_hook",
    }
    # Pure adapter interface patterns
    EXEMPT_INTERFACE_PATTERNS = ["interface", "api", "webhook", "bridge", "shim"]

    updated = 0
    real_gaps = 0

    for file_obj in data["files"]:
        path_str = file_obj["path"]
        if not file_obj.get("requires_tests"):
            continue

        p = repo_root / path_str
        if not p.exists():
            continue

        # Already has a test — skip
        test_filename = f"test_{p.stem}.py"
        tests_dir = repo_root / "tests"
        has_test = (tests_dir / test_filename).exists() or (
            tests_dir.exists()
            and any(p.stem in t for t in os.listdir(tests_dir) if t.startswith("test_"))
        )
        if has_test:
            continue

        exempt = False
        reason = ""

        try:
            content = p.read_text(encoding="utf-8", errors="ignore")

            # Rule 1: Known infra stems — always exempt
            if p.stem in EXEMPT_STEMS:
                exempt = True
                reason = "known-infra-stem"

            # Rule 2: Crons/tools/scripts/bin/checks + has CLI entrypoint
            elif any(path_str.startswith(d + "/") for d in EXEMPT_DIRS):
                if 'if __name__ == "__main__":' in content:
                    try:
                        tree = ast.parse(content)
                        funcs = [
                            n for n in ast.walk(tree)
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        ]
                        # Exempt if mostly CLI glue: ≤6 functions or no class definitions
                        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                        if len(funcs) <= 6 or not classes:
                            exempt = True
                            reason = f"cli-entrypoint ({len(funcs)} funcs, {len(classes)} classes)"
                    except SyntaxError:
                        exempt = True
                        reason = "cli-entrypoint (parse failed)"

            # Rule 3: Pure adapter interfaces — no business logic
            elif path_str.startswith("interfaces/"):
                stem_lower = p.stem.lower()
                if any(pat in stem_lower for pat in EXEMPT_INTERFACE_PATTERNS):
                    try:
                        tree = ast.parse(content)
                        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                        funcs = [
                            n for n in ast.walk(tree)
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        ]
                        # Adapter: has at most 1 class and ≤4 methods
                        if len(classes) <= 1 and len(funcs) <= 4:
                            exempt = True
                            reason = "pure-adapter-interface"
                    except SyntaxError:
                        pass

            # Rule 4: __init__.py files — namespace only, no test needed
            elif p.name == "__init__.py":
                try:
                    tree = ast.parse(content)
                    funcs = [
                        n for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    if len(funcs) == 0:
                        exempt = True
                        reason = "empty-init"
                except SyntaxError:
                    exempt = True
                    reason = "empty-init (parse failed)"

        except Exception:
            pass

        if exempt:
            file_obj["requires_tests"] = False
            file_obj["test_exempt_reason"] = reason
            updated += 1
            print(f"  ✅ Exempted: {path_str}  ({reason})")
        else:
            real_gaps += 1

    print(f"\n  📊 Reconcile result: {updated} exempted, {real_gaps} real gaps remain.")
    return updated

def validate(check_deltas=False, notify=False, reconcile=False):
    repo_root = Path(__file__).parent.parent.resolve()
    index_path = repo_root / "docs/space/nina_index.json"
    
    if not index_path.exists():
        print("❌ Error: nina_index.json not found.")
        return False
        
    with open(index_path, "r") as f:
        data = json.load(f)
        
    if reconcile:
        count = reconcile_tests(data, repo_root)
        if count > 0:
            with open(index_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"💾 Updated {index_path} with {count} reconciliations.")
            # Regenerate markdown index
            try:
                subprocess.run([sys.executable, "tools/update_index.py"], check=True)
            except:
                pass

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

        # Don't throw a hard error for missing backups, logs, or dynamically generated files
        skip_existence_check = any(p in path_str for p in ["upgrades/backups", "upgrades/incidents", "upgrades/deploy.log", "logs/", "data/", "exports/", ".env", ".aider", ".log", ".lock", ".save", "history"])

        if not (repo_root / path_str).exists() and not skip_existence_check:
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
    ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".agent", ".jules", "node_modules"}
    governed_roots = ["core", "tools", "interfaces", "docs", "crons", "agent", "ninagate", "checks"]
    
    for root, dirs, files in os.walk(repo_root):
        # Prune high-volume automated dirs and hidden dirs
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        
        # Don't warn about missing index entries for high-volume automated artifacts
        if "upgrades/backups" in root or "upgrades/incidents" in root:
            continue
            
        for file in files:
            rel_path = str((Path(root) / file).relative_to(repo_root))
            
            # If it's a doc, core logic, tool, or root script, it should be indexed
            if rel_path not in indexed_paths:
                is_governed_path = any(rel_path.startswith(gr + "/") for gr in governed_roots)
                is_script_or_doc = rel_path.endswith(".md") or rel_path.endswith(".py") or rel_path.endswith(".sh")
                
                if is_governed_path or is_script_or_doc:
                    print(f"⚠️ Unmanaged but probably governed: {rel_path} is missing from the index.")
                    warnings += 1

    quality_pct = (total_score / total_files) * 100 if total_files else 0
    if quality_pct < 75.0:
        print(f"❌ Metadata Quality Score ({quality_pct:.1f}%) is below the required 75.0% threshold.")
        errors += 1

    if check_deltas:
        if not check_doc_deltas(data, repo_root):
            errors += 1

    if errors > 0:
        print(f"\n❌ Validation FAILED with {errors} errors and {warnings} warnings.")
        print(f"📊 Metadata Quality Score: {quality_pct:.1f}%")
        print(f"🧪 Missing Tests: {missing_tests}")
        if notify:
            msg = f"🚨 *NINA Governance Alert*\n\nValidation FAILED with *{errors}* errors.\nMetadata Quality Score: {quality_pct:.1f}%\nCheck CI logs or run validation locally."
            notify_telegram(msg, repo_root)
        return False
        
    print(f"\n✅ Index validation PASSED ({warnings} warnings).")
    print(f"📊 Metadata Quality Score: {quality_pct:.1f}%")
    print(f"🧪 Missing Tests: {missing_tests}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-deltas", action="store_true", help="Check that code changes are accompanied by doc deltas.")
    parser.add_argument("--notify", action="store_true", help="Send Telegram alerts on violations or low score")
    parser.add_argument("--reconcile", action="store_true", help="Auto-reconcile test requirements for infra/tooling scripts")
    args = parser.parse_args()
    if not validate(args.check_deltas, args.notify, args.reconcile):
        sys.exit(1)
