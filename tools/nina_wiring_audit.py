"""NINA Wiring Integrity Auditor (OBS-001)"""
import os
import sys
import ast
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("nina.wiring_audit")
REPO_ROOT = Path(__file__).resolve().parent.parent

# Mapping of Symlink File -> Target (relative to REPO_ROOT)
SYMLINKS = {
    ".agy/skills/NINA-RULES/SKILL.md": "docs/context/NINA_RULES.md",
    ".agy/skills/NINA-WORKFLOW/SKILL.md": "docs/context/NINA_WORKFLOW.md",
    ".agy/skills/NINA-OPS/SKILL.md": "docs/context/NINA_OPS.md",
    "GEMINI.md": "docs/context/NINA_AGENT_PRIMER.md",
    "AGENTS.md": "docs/context/NINA_AGENT_PRIMER.md"
}

# Mapping of Copy File -> Source File (relative to REPO_ROOT)
COPIES = {
    ".cursor/rules/nina-rules.mdc": "docs/context/NINA_RULES.md",
    ".cursor/rules/nina-workflow.mdc": "docs/context/NINA_WORKFLOW.md",
    ".cursor/rules/nina-ops.mdc": "docs/context/NINA_OPS.md"
}

def symlink_resolves(link_rel_path: str, target_rel_path: str) -> tuple[bool, bool]:
    """Returns (ok, repaired)."""
    link_path = REPO_ROOT / link_rel_path
    target_path = REPO_ROOT / target_rel_path

    if not target_path.exists():
        logger.warning("wiring_audit: symlink target does not exist — %s", target_rel_path)
        return False, False

    if link_path.is_symlink():
        try:
            resolved = link_path.resolve(strict=True)
            if resolved == target_path.resolve():
                return True, False
        except (FileNotFoundError, OSError):
            pass

    logger.warning("wiring_audit: dangling symlink — %s", link_rel_path)
    try:
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.relpath(target_path, link_path.parent), link_path)
        logger.info("wiring_audit: repaired symlink — %s", link_rel_path)
        return True, True
    except Exception as e:
        logger.error("wiring_audit: failed to repair symlink %s: %s", link_rel_path, e)
        return False, False

def get_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def file_in_sync(copy_rel_path: str, source_rel_path: str) -> tuple[bool, bool]:
    """Returns (ok, repaired)."""
    copy_path = REPO_ROOT / copy_rel_path
    source_path = REPO_ROOT / source_rel_path

    if not source_path.exists():
        logger.warning("wiring_audit: copy source does not exist — %s", source_rel_path)
        return False, False

    if copy_path.exists():
        if get_md5(copy_path) == get_md5(source_path):
            return True, False

    logger.warning("wiring_audit: stale copy — %s", copy_rel_path)
    try:
        copy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(source_path, "rb") as src, open(copy_path, "wb") as dst:
            dst.write(src.read())
        logger.info("wiring_audit: refreshed copy — %s", copy_rel_path)
        return True, True
    except Exception as e:
        logger.error("wiring_audit: failed to refresh copy %s: %s", copy_rel_path, e)
        return False, False

def context_graph_age_ok(graph_rel_path: str, max_hours: int = 24) -> bool:
    graph_path = REPO_ROOT / graph_rel_path
    if not graph_path.exists():
        logger.warning("wiring_audit: context graph missing — regenerate with python3 nina_context_graph.py")
        return False

    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        gen_str = data.get("meta", {}).get("generated_at")
        if not gen_str:
            logger.warning("wiring_audit: context graph metadata missing generated_at")
            return False

        gen_str = gen_str.replace("Z", "+00:00")
        gen_dt = datetime.fromisoformat(gen_str)
        now = datetime.now(timezone.utc) if gen_dt.tzinfo else datetime.now()
        age_hours = (now - gen_dt).total_seconds() / 3600.0
        if age_hours > max_hours:
            logger.warning("wiring_audit: context graph stale — %.1fh old", age_hours)
            return False
        return True
    except Exception as e:
        logger.warning("wiring_audit: failed to read context graph: %s", e)
        return False

def session_log_has_recent_entry(log_rel_path: str, max_hours: int = 48) -> bool:
    log_path = REPO_ROOT / log_rel_path
    if not log_path.exists():
        logger.warning("wiring_audit: session log missing — %s", log_rel_path)
        return False

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("## Session"):
                    parts = line.split("|")
                    session_part = parts[0].replace("## Session", "").strip()
                    try:
                        if "T" in session_part:
                            gen_dt = datetime.fromisoformat(session_part.replace("Z", "+00:00"))
                        else:
                            gen_dt = datetime.strptime(session_part[:10], "%Y-%m-%d")
                    except ValueError:
                        continue

                    now = datetime.now(timezone.utc) if gen_dt.tzinfo else datetime.now()
                    age_hours = (now - gen_dt).total_seconds() / 3600.0
                    if age_hours > max_hours:
                        logger.warning("wiring_audit: session log stale — last entry %.1fh ago", age_hours)
                        return False
                    return True
        logger.warning("wiring_audit: no session entries found in session log")
        return False
    except Exception as e:
        logger.warning("wiring_audit: failed to read session log: %s", e)
        return False


def build_symbol_registry() -> dict[str, set[str]]:
    """Build a map of local module paths -> set of exported symbols (functions/classes/globals)."""
    registry = {}
    for root, _, files in os.walk(str(REPO_ROOT)):
        if any(p in root for p in ["/venv", "/.venv", "/.git", "/__pycache__", "/build", "/dist", "/data", "/upgrades", "/archive", "/backups", "/tests", "/memory", "/mcp", "/swarm"]):
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            full_path = Path(root) / f
            try:
                rel_path = full_path.relative_to(REPO_ROOT)
                parts = list(rel_path.parts)
                parts[-1] = parts[-1][:-3]  # Remove .py
                if parts[-1] == "__init__":
                    parts.pop()
                module_name = ".".join(parts)

                content = full_path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(full_path))

                exports = set()
                has_all = False
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "__all__":
                                if isinstance(node.value, (ast.List, ast.Tuple)):
                                    for elt in node.value.elts:
                                        if isinstance(elt, ast.Constant):
                                            exports.add(elt.value)
                                    has_all = True

                if not has_all:
                    for node in tree.body:
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            exports.add(node.name)
                        elif isinstance(node, ast.ClassDef):
                            exports.add(node.name)
                        elif isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    exports.add(target.id)
                                elif isinstance(target, (ast.Tuple, ast.List)):
                                    for elt in target.elts:
                                        if isinstance(elt, ast.Name):
                                            exports.add(elt.id)
                        elif isinstance(node, ast.AnnAssign):
                            if isinstance(node.target, ast.Name):
                                exports.add(node.target.id)

                registry[module_name] = exports
            except Exception as e:
                logger.warning(f"wiring_audit: failed to parse symbols in {f}: {e}")
    return registry


def audit_imports_and_calls(registry: dict[str, set[str]]) -> list[str]:
    """Verify that all local import statements and attribute calls exist in the registry."""
    warnings = []
    LOGGER_METHODS = {
        "debug", "info", "warning", "warn", "error", "critical", "exception",
        "log", "success", "trace", "bind", "opt", "add", "remove", "configure",
        "level", "disable", "enable", "catch"
    }

    for root, _, files in os.walk(str(REPO_ROOT)):
        if any(p in root for p in ["/venv", "/.venv", "/.git", "/__pycache__", "/build", "/dist", "/data", "/upgrades", "/archive", "/backups", "/tests", "/memory", "/mcp", "/swarm"]):
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            full_path = Path(root) / f
            try:
                rel_path = full_path.relative_to(REPO_ROOT)
                content = full_path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(full_path))

                # Step 1: scan imports to see which local names bind to modules in the registry
                module_bindings = {}  # local name -> full module name
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            local_name = alias.asname or alias.name
                            if alias.name in registry:
                                module_bindings[local_name] = alias.name
                    elif isinstance(node, ast.ImportFrom):
                        if not node.module:
                            continue
                        for alias in node.names:
                            full_mod = f"{node.module}.{alias.name}"
                            if full_mod in registry:
                                local_name = alias.asname or alias.name
                                module_bindings[local_name] = full_mod

                # Step 2: audit imports and attribute calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if not node.module:
                            continue
                        module_name = node.module
                        if module_name in registry:
                            for alias in node.names:
                                if alias.name != "*":
                                    full_submodule = f"{module_name}.{alias.name}"
                                    if full_submodule in registry:
                                        continue
                                    if alias.name not in registry[module_name]:
                                        if module_name == "core.logger" and alias.name == "logger":
                                            continue
                                        warnings.append(
                                            f"Import error in {rel_path}: '{alias.name}' not found in '{module_name}'"
                                        )
                    elif isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name):
                            local_name = node.value.id
                            if local_name == "logger" and node.attr in LOGGER_METHODS:
                                continue
                            if local_name in module_bindings:
                                mod_name = module_bindings[local_name]
                                if node.attr not in registry[mod_name]:
                                    if node.attr not in ["__class__", "__name__", "__doc__", "__file__"]:
                                        warnings.append(
                                            f"Interface drift in {rel_path}: '{node.attr}' not in '{mod_name}' (called as '{local_name}.{node.attr}')"
                                        )
            except Exception:
                pass
    return warnings


def run_all_checks() -> dict:
    passed = 0
    failed = 0
    repaired = 0
    warnings = []

    for link, target in SYMLINKS.items():
        ok, rep = symlink_resolves(link, target)
        if ok:
            passed += 1
            if rep:
                repaired += 1
        else:
            failed += 1
            warnings.append(f"Symlink {link} is broken")

    for copy_file, source in COPIES.items():
        ok, rep = file_in_sync(copy_file, source)
        if ok:
            passed += 1
            if rep:
                repaired += 1
        else:
            failed += 1
            warnings.append(f"Copy {copy_file} is stale")

    if context_graph_age_ok("data/graphs/nina_context_graph.json", max_hours=24):
        passed += 1
    else:
        failed += 1
        warnings.append("Context graph is stale or missing")

    if session_log_has_recent_entry("docs/context/nina_session_log.md", max_hours=48):
        passed += 1
    else:
        failed += 1
        warnings.append("Session log is stale or missing")

    # Run Python interface and import audits
    try:
        registry = build_symbol_registry()
        interface_warnings = audit_imports_and_calls(registry)
        if interface_warnings:
            failed += len(interface_warnings)
            warnings.extend(interface_warnings)
            logger.warning("wiring_audit: found %d local interface import/drift issue(s)", len(interface_warnings))
        else:
            passed += 1
            logger.info("wiring_audit: local python imports and interfaces passed verification")
    except Exception as e:
        failed += 1
        warnings.append(f"Interface audit failed with exception: {e}")

    return {
        "passed": passed,
        "failed": failed,
        "repaired": repaired,
        "warnings": warnings,
        "healthy": (failed == 0)
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s wiring_audit: %(message)s")
    result = run_all_checks()
    if not result["healthy"]:
        print(f"WIRING AUDIT FAILED: {result['failed']} issue(s)")
        for w in result["warnings"]:
            print(f"  - {w}")
        sys.exit(1)
    else:
        print(f"WIRING AUDIT PASSED: {result['passed']} checks, {result['repaired']} repaired")
        sys.exit(0)
