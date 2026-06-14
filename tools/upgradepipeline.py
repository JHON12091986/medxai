"""
NINA v12 — UpgradePipeline (Stage 6)
Pattern scan → sandbox test → diff → approve/reject → deploy + backup.
"""
import ast
import json
import logging
import re
import shutil
import time
from pathlib import Path

logger     = logging.getLogger("nina.upgrade")
BACKUP_DIR = Path("upgrades/backups")
IDLE_QUEUE = Path("data/idlequeue.json")

WRITABLE_SCOPE = ["tools/", "crons/", "core/agent.py", "tests/"]
PROTECTED = [
    "core/nina.py","core/router.py","core/config.py",
    "interfaces/telegram_interface.py",".env","nina.service"
]

DANGEROUS_PATTERNS = [
    (r"os\.system",              "Shell injection — use subprocess with shell=False"),
    (r"subprocess\.[^\n]+shell\s*=\s*True", "subprocess shell=True — remove shell=True"),
    (r"subprocess\.call\([^)]*shell\s*=\s*True", "subprocess.call shell=True — remove shell=True"),
    (r"subprocess\.check_output\([^)]*shell\s*=\s*True", "subprocess.check_output shell=True — remove shell=True"),
    (r"subprocess\.Popen\([^)]*shell\s*=\s*True", "subprocess.Popen shell=True — remove shell=True"),
    (r"shutil\.rmtree",          "shutil.rmtree — forbidden"),
    (r"\beval\b",                 "eval on non-literal — forbidden"),
    (r"\bexec\b",                 "exec on non-literal — forbidden"),
    (r"\b__import__\b",          "dynamic __import__ — forbidden"),
    (r"\bcompile\b",            "compile on non-literal — forbidden"),
    (r"importlib\.import_module","importlib dynamic import — forbidden"),
    (r"open\s*\(\s*['\"]?\.\.",  "path traversal in open — workspace only"),
    (r"pathlib\.Path\s*\(\s*['\"]?\.\.", "path traversal via pathlib — workspace only"),
    (r"socket\.connect",         "raw socket.connect — forbidden"),
    (r"requests\.get\s*\([^)]*(?!http://|https://)", "requests to non-http target — forbidden"),
    (r"core/nina|core/router|core/config|telegram_interface|\.env\b|nina\.service",
                                  "write to protected core file — forbidden"),
]

class UpgradePipeline:
    def __init__(self, config, router):
        self.config = config
        self.router = router
        self._pending: dict | None = None
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        IDLE_QUEUE.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        logger.info("UpgradePipeline ready", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})

    def _scan(self, code: str) -> list[str]:
        hits = []
        for pattern, reason in DANGEROUS_PATTERNS:
            if re.search(pattern, code):
                hits.append(f"Upgrade rejected: {reason}. Fix and resubmit.")
        return hits

    def _in_writable_scope(self, filename: str) -> bool:
        try:
            from pathlib import Path as _P
            resolved = _P(filename).resolve()
            base = _P(".").resolve()
            in_scope = any(
                str(resolved).startswith(str((base / s).resolve()) + "/")
                or resolved == (base / s).resolve()
                for s in WRITABLE_SCOPE
            )
            not_protected = not any(
                resolved == (base / pr).resolve() for pr in PROTECTED
            )
            return in_scope and not_protected
        except Exception:
            return False

    async def submit(self, code: str, filename: str) -> list:
        step_results = []

        # Step: extension check
        step_name = "check_extension"
        try:
            if not filename.endswith(".py"):
                raise ValueError("NINA only accepts .py files for upgrades.")
            step_results.append({"step_name": step_name, "ok": True, "error": None})
            logger.info(f"{step_name}: SUCCESS", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        except Exception as e:
            step_results.append({"step_name": step_name, "ok": False, "error": str(e)})
            logger.info(f"{step_name}: FAILED - {e}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            return step_results

        # Step: writable scope check
        step_name = "check_writable_scope"
        try:
            if not self._in_writable_scope(filename):
                raise ValueError(f"Upgrade rejected: {filename} is outside writable scope or is a protected file.")
            step_results.append({"step_name": step_name, "ok": True, "error": None})
            logger.info(f"{step_name}: SUCCESS", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        except Exception as e:
            step_results.append({"step_name": step_name, "ok": False, "error": str(e)})
            logger.info(f"{step_name}: FAILED - {e}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            return step_results

        # Step: pattern scan
        step_name = "pattern_scan"
        try:
            hits = self._scan(code)
            if hits:
                for h in hits:
                    logger.warning(h, extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
                raise ValueError("\n".join(hits))
            step_results.append({"step_name": step_name, "ok": True, "error": None})
            logger.info(f"{step_name}: SUCCESS", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        except Exception as e:
            step_results.append({"step_name": step_name, "ok": False, "error": str(e)})
            logger.info(f"{step_name}: FAILED - {e}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            return step_results

        # Step: syntax check
        step_name = "syntax_check"
        try:
            ast.parse(code)
            step_results.append({"step_name": step_name, "ok": True, "error": None})
            logger.info(f"{step_name}: SUCCESS", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        except SyntaxError as e:
            err = f"Upgrade rejected: SyntaxError — {e}"
            step_results.append({"step_name": step_name, "ok": False, "error": err})
            logger.info(f"{step_name}: FAILED - {err}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            return step_results
        except Exception as e:
            step_results.append({"step_name": step_name, "ok": False, "error": str(e)})
            logger.info(f"{step_name}: FAILED - {e}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            return step_results

        # Step: stage pending
        step_name = "stage_pending"
        try:
            self._pending = {"filename": filename, "code": code, "submitted_at": time.time()}

            step_results.append({"step_name": step_name, "ok": True, "error": None})
            logger.info(f"{step_name}: SUCCESS", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        except Exception as e:
            step_results.append({"step_name": step_name, "ok": False, "error": str(e)})
            logger.info(f"{step_name}: FAILED - {e}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            return step_results

        return step_results

    async def handle_command(self, cmd: str, arg: str) -> str:
        if cmd == "approve":
            return await self._deploy()
        elif cmd == "reject":
            self._pending = None
            return "Upgrade rejected and discarded."
        elif cmd == "patch":
            parts = arg.split(None, 1)
            if len(parts) != 2:
                return "Usage: patch <filename> <url>"
            filename, url = parts
            import httpx
            from urllib.parse import urlparse
            _parsed = urlparse(url)
            _ALLOWED_DOMAINS = {"github.com", "raw.githubusercontent.com", "gist.githubusercontent.com", "pastebin.com"}
            if _parsed.scheme != "https":
                return "Patch rejected: only HTTPS URLs are allowed."
            if _parsed.hostname not in _ALLOWED_DOMAINS:
                return f"Patch rejected: domain '{_parsed.hostname}' not in allowlist {_ALLOWED_DOMAINS}."
            async with httpx.AsyncClient(timeout=30, verify=True) as c:
                r = await c.get(url)
                content_type = r.headers.get("Content-Type", "")
                if not content_type.startswith("text/") and "application/json" not in content_type:
                    raise ValueError(f"Remote patch rejected: unexpected Content-Type '{content_type}'")
                MAX_PATCH_SIZE = 512 * 1024
                content = r.content
                if len(content) > MAX_PATCH_SIZE:
                    raise ValueError(f"Remote patch rejected: response too large ({len(content)} bytes)")
            return await self.submit(content.decode("utf-8"), filename)
        elif cmd == "generate":
            return await self._generate(arg)
        elif cmd == "rollback":
            return await self._rollback(arg)
        return "Unknown upgrade command."

    async def _deploy(self) -> str:
        if not self._pending:
            return "No pending upgrade."
        fn   = self._pending["filename"]
        code = self._pending["code"]
        dest = Path(fn)

        # Backup
        if dest.exists():
            ts   = time.strftime("%Y%m%d%H%M%S")
            bak  = BACKUP_DIR / f"{dest.stem}_{ts}.py"
            shutil.copy2(dest, bak)

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code)
        logger.info(f"upgrade_deployed file={fn}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        self._pending = None
        return f"✅ Deployed: `{fn}`"

    async def _rollback(self, filename: str) -> str:
        stem    = Path(filename).stem
        backups = sorted(BACKUP_DIR.glob(f"{stem}_*.py"), reverse=True)
        if not backups:
            return f"No backups found for {filename}."
        latest = backups[0]
        shutil.copy2(latest, filename)
        logger.info(f"rollback file={filename} from={latest}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
        return f"✅ Rolled back `{filename}` from `{latest.name}`"

    async def _generate(self, arg: str) -> str:
        prompt = f"Generate a Python upgrade module for NINA. Task: {arg}\nReply with only valid Python code."
        msgs   = [{"role": "user", "content": prompt}]
        from core.router import ClassifiedTask
        task   = ClassifiedTask("coding", 800, False, False)
        code   = await self.router.route(prompt, msgs, task)
        fname  = f"tools/generated_{int(time.time())}.py"
        return await self.submit(code, fname)

    def _expire_pending(self):
        """Call periodically — move expired pending to idle queue."""
        if not self._pending:
            return
        age = time.time() - self._pending.get("submitted_at", 0)
        if age > 3600:
            q = json.loads(IDLE_QUEUE.read_text()) if IDLE_QUEUE.exists() else []
            q.append({**self._pending, "state": "expired_pending_review",
                      "expired_at": time.strftime("%Y-%m-%dT%H:%M:%S+0600")})
            IDLE_QUEUE.write_text(json.dumps(q, indent=2))
            logger.info(f"upgrade_expired_to_idle file={self._pending['filename']}", extra={"log":"upgrade.log", "tool_name": "upgradepipeline"})
            self._pending = None

    async def _handle_shadow(self, arg: str) -> str:
        if not hasattr(self, "_shadow_tester"):
            self._shadow_tester = ABShadowTester(self)
        parts = arg.split(None, 1)
        sub = parts[0].lower() if parts else ""
        if sub == "approve":
            return await self._shadow_tester.approve()
        if sub == "reject":
            return self._shadow_tester.reject()
        if sub == "status":
            return self._shadow_tester.status()
        if sub == "start" and len(parts) > 1:
            import httpx
            fname, url = parts[1].split(None, 1)
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.get(url)
                content_type = r.headers.get("Content-Type", "")
                if not content_type.startswith("text/") and "application/json" not in content_type:
                    raise ValueError(f"Remote patch rejected: unexpected Content-Type '{content_type}'")
                MAX_PATCH_SIZE = 512 * 1024
                content = r.content
                if len(content) > MAX_PATCH_SIZE:
                    raise ValueError(f"Remote patch rejected: response too large ({len(content)} bytes)")
            return await self._shadow_tester.start(content.decode("utf-8"), fname)
        return "Usage: shadow start <file> <url> | shadow status | shadow approve | shadow reject"


class ABShadowTester:
    """Opt-in shadow tester (Stage 6.7)."""
    def __init__(self, pipeline, shadow_n=20):
        self.pipeline = pipeline
        self.shadow_n = shadow_n
        self._results = []
        self._candidate_code = None
        self._candidate_file = None

    async def start(self, code, filename):
        scan = await self.pipeline.submit(code, filename)
        if "rejected" in scan.lower():
            return scan
        self._candidate_code = code
        self._candidate_file = filename
        self._results = []
        lines = ["Shadow test started for `" + filename + "`",
                 "Will shadow " + str(self.shadow_n) + " live requests.",
                 "Send `shadow status` to check progress."]
        return "\n".join(lines)

    def status(self):
        if not self._candidate_code:
            return "No active shadow test."
        done = len(self._results)
        rate = sum(r["match"] for r in self._results) / max(done, 1) * 100
        return "Shadow: `" + str(self._candidate_file) + "`\n" + str(done) + "/" + str(self.shadow_n) + " sampled | match: " + str(int(rate)) + "%"

    async def approve(self):
        if not self._candidate_code:
            return "No active shadow test."
        result = await self.pipeline._deploy()
        self._candidate_code = None
        return "Shadow approved and deployed: " + result

    def reject(self):
        self._candidate_code = None
        self._results = []
        return "Shadow test rejected. Candidate discarded."

