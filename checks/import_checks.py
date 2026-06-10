from checks.runner import record, NINA_DIR, BLOCKER_EXCEPTIONS, log
import importlib.util
import sys

CORE_MODULES = [
    ("core.config",       "core/config.py"),
    ("core.logger",       "core/logger.py"),
    ("core.capabilities", "core/capabilities.py"),
    ("core.memory",       "core/memory.py"),
    ("core.router",       "core/router.py"),
    ("core.agent",        "core/agent.py"),
    ("core.nina",         "core/nina.py"),
    ("core.hotreload",    "core/hotreload.py"),
]
def check_core_imports():
    # Ensure nina dir is on sys.path
    nina_str = str(NINA_DIR)
    if nina_str not in sys.path:
        sys.path.insert(0, nina_str)

    for mod_name, rel_path in CORE_MODULES:
        full_path = NINA_DIR / rel_path
        if not full_path.exists():
            record(
                "INFO", f"import.missing.{mod_name.replace('.','_')}",
                f"Module file not found: {rel_path} — skipping import check",
            )
            continue
        try:
            # Use importlib to attempt the import in isolation
            spec = importlib.util.spec_from_file_location(mod_name, full_path)
            if spec is None or spec.loader is None:
                record("WARN", f"import.spec_none.{mod_name.replace('.','_')}",
                       f"Could not build import spec for {mod_name}")
                continue
            module = importlib.util.module_from_spec(spec)
            # Temporarily add to sys.modules to allow relative imports
            sys.modules[mod_name] = module
            try:
                spec.loader.exec_module(module)
                record("PASS", f"import.{mod_name.replace('.','_')}", f"Import OK: {mod_name}")
            except BLOCKER_EXCEPTIONS as e:
                exc_type = type(e).__name__
                sig_map = {
                    "NameError":      "startup.nameError",
                    "TypeError":      "startup.typeError",
                    "AttributeError": "startup.attributeError",
                    "ImportError":    "startup.importError",
                    "SyntaxError":    "startup.syntaxError",
                }
                sig_id = sig_map.get(exc_type, "startup.importError")
                record(
                    "BLOCKER", sig_id,
                    f"{exc_type} importing {mod_name}: {e}",
                    detail=(
                        f"Module: {mod_name}\n"
                        f"File:   {rel_path}\n"
                        f"Error:  {exc_type}: {e}"
                    ),
                    fix=f"Inspect ~/nina/{rel_path} for the symbol named in the error. "
                        f"Check recent patches via nina_update_log.md.",
                )
            except (RuntimeError, ValueError, OSError, LookupError, SystemError, ModuleNotFoundError) as e:
                log.warning(f"Runtime error importing {mod_name}: {e}")
                # Non-BLOCKER exception (e.g. missing .env at import time) — WARN only
                record(
                    "WARN", f"import.runtime_error.{mod_name.replace('.','_')}",
                    f"Runtime error importing {mod_name}: {type(e).__name__}: {e}",
                    detail=str(e),
                    fix=f"Check ~/nina/{rel_path} — may require .env to be fully populated.",
                )
            finally:
                # Remove from sys.modules to avoid polluting subsequent checks
                sys.modules.pop(mod_name, None)
        except (OSError, ValueError, ImportError) as outer:
            log.warning(f"Outer error testing import of {mod_name}: {outer}")
            record(
                "WARN", f"import.outer_error.{mod_name.replace('.','_')}",
                f"Outer error testing import of {mod_name}: {outer}",
                detail=str(outer),
                fix=f"Inspect ~/nina/{rel_path} manually.",
            )
