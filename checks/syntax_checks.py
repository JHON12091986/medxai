from checks.runner import record, NINA_DIR, log
import ast

SYNTAX_CHECK_FILES = [
    "main.py",
    "core/config.py",
    "core/router.py",
    "core/nina.py",
    "core/agent.py",
    "core/memory.py",
    "core/logger.py",
    "core/hotreload.py",
    "core/capabilities.py",
    "interfaces/telegram_interface.py",
    "tools/shell.py",
    "tools/browser.py",
    "tools/upgradepipeline.py",
    "tools/officemail.py",
    "tools/system.py",
    "crons/manager.py",
    "idleloop.py",
]
def check_syntax():
    for rel in SYNTAX_CHECK_FILES:
        full = NINA_DIR / rel
        if not full.exists():
            record("INFO", f"syntax.missing.{rel.replace('/','.')}", f"File not found: {rel}")
            continue
        try:
            source = full.read_text(errors="replace")
            ast.parse(source, filename=rel)
            record("PASS", f"syntax.{rel.replace('/','.')}", f"Syntax OK: {rel}")
        except SyntaxError as e:
            record(
                "BLOCKER", "startup.syntaxError",
                f"SyntaxError in {rel}: {e.msg} (line {e.lineno})",
                detail=f"File: {rel}\nLine: {e.lineno}\nMessage: {e.msg}\nText: {e.text or ''}",
                fix=f"Open ~/nina/{rel} at line {e.lineno} and fix the syntax error.",
            )
        except (OSError, ValueError, UnicodeDecodeError) as e:
            log.warning(f"Parse error in {rel}: {e}")
            record(
                "WARN", f"syntax.parse_error.{rel.replace('/','.')}",
                f"Parse error in {rel}: {e}",
                detail=str(e),
                fix=f"Inspect ~/nina/{rel} for encoding or unusual syntax issues.",
            )
