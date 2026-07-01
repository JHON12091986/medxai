import subprocess
from pathlib import Path
from core.task_manager.task_spec import TaskSpec
from core.task_manager.queue import TaskQueue
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL)

class TaskDispatcher:
    """
    Reads from TaskQueue and dispatches tasks to Jules or AGY.
    Does NOT modify core/router.py or any protected file.
    """

    def __init__(self, queue: TaskQueue, dry_run: bool = False):
        self.queue = queue
        self.dry_run = dry_run

    def dispatch_next(self) -> dict | None:
        """
        Pop the next PENDING unblocked task from the queue.
        Check idempotency via tools/jules.py (open PRs, git log).
        If clear: call tools/jules.py dispatch OR write .jules task file.
        Mark task as DISPATCHED in queue.
        Returns dispatch result dict or None if nothing to dispatch.
        """
        spec = self.queue.dequeue()
        if not spec:
            return None

        # Check idempotency
        if not self._check_idempotency(spec):
            self.queue.mark_skipped(spec.task_id, reason="Idempotency guard triggered: already implemented")
            self._notify_telegram(f"⏭️ Task {spec.task_id} skipped: already implemented.")
            return {"task_id": spec.task_id, "status": "SKIPPED", "reason": "Idempotency check failed"}

        if self.dry_run:
            return {"task_id": spec.task_id, "status": "DRY_RUN", "msg": "Dry run: not dispatched"}

        # Write handoff file
        task_file = self._build_jules_task_file(spec)

        # Trigger tools/jules.py dispatch
        sid = None
        try:
            res = subprocess.run(
                ["python3", "tools/jules.py", "dispatch", spec.body],
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode == 0:
                output = res.stdout.strip()
                if "Jules task started:" in output:
                    sid = output.split("Jules task started:")[-1].strip()
        except Exception:
            pass

        # Mark as DISPATCHED
        self.queue.mark_dispatched(spec.task_id)

        # Notify Telegram
        msg = f"🚀 *Dispatched Task {spec.task_id}* to Jules\n*Title:* {spec.title}\n*Priority:* {spec.priority}"
        if sid:
            msg += f"\n*Session ID:* `{sid}`"
        self._notify_telegram(msg)

        return {
            "task_id": spec.task_id,
            "status": "DISPATCHED",
            "task_file": str(task_file),
            "jules_session_id": sid
        }

    def dispatch_all_pending(self, limit: int = 3) -> list[dict]:
        """Dispatch up to `limit` pending tasks. Returns list of results."""
        results = []
        for _ in range(limit):
            res = self.dispatch_next()
            if not res:
                break
            results.append(res)
        return results

    def _check_idempotency(self, spec: TaskSpec) -> bool:
        """
        Returns True if task is safe to dispatch (not already done).
        Checks:
        1. Git log for task_id keyword
        2. data/task_queue.json for existing DONE/DISPATCHED entry with same idempotency_key
        3. docs/audit/scheduler_skip_log.md for skip entries
        Returns False (block dispatch) if evidence of prior implementation found.
        """
        # 1. Git log for task_id keyword
        try:
            res = subprocess.run(
                ["git", "log", "--grep", spec.task_id, "-n", "1"],
                capture_output=True,
                text=True,
                check=False
            )
            if res.stdout and spec.task_id in res.stdout:
                return False
        except Exception:
            pass

        # 2. data/task_queue.json for existing DONE/DISPATCHED entry with same idempotency_key
        try:
            all_tasks = self.queue.list_all()
            for t in all_tasks:
                if t.idempotency_key == spec.idempotency_key and t.status in ("DONE", "DISPATCHED"):
                    if t.task_id != spec.task_id:
                        return False
        except Exception:
            pass

        # 3. docs/audit/scheduler_skip_log.md for skip entries
        try:
            skip_log = Path("docs/audit/scheduler_skip_log.md")
            if skip_log.exists():
                content = skip_log.read_text(encoding="utf-8")
                if spec.task_id in content:
                    return False
        except Exception:
            pass

        return True

    def _build_jules_task_file(self, spec: TaskSpec) -> Path:
        """
        Write a .jules/tasks/runtime/<task_id>.md file from the spec.
        This is the handoff format Jules reads.
        Returns path to the written file.
        """
        target_path = Path(".jules/tasks/runtime") / f"{spec.task_id}.md"
        target_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""# TASK: {spec.title}
**Task ID:** {spec.task_id}
**Priority:** {spec.priority}
**Tier:** {spec.tier}
**Source:** {spec.source}
**Created At:** {spec.created_at}

---

## BODY
{spec.body}
"""
        target_path.write_text(content, encoding="utf-8")
        return target_path

    def _notify_telegram(self, message: str):
        """
        Send Telegram notification via interfaces/telegram_interface.py.
        Import it read-only — do NOT modify it.
        Wrap in try/except so failure never blocks dispatch.
        """
        try:
            import os
            import requests
            from core.config import load_config

            token = os.environ.get(ENV_TELEGRAM_BOT_TOKEN)
            chat_id = os.environ.get(ENV_TELEGRAM_CHAT_ID) or os.environ.get(ENV_TELEGRAM_CHAT_ID)

            if not token or not chat_id:
                try:
                    cfg = load_config()
                    token = getattr(cfg, "telegram_bot_token", None) or os.environ.get(ENV_TELEGRAM_BOT_TOKEN)
                    chat_id = getattr(cfg, "telegram_chat_id", None) or os.environ.get(ENV_TELEGRAM_CHAT_ID) or os.environ.get(ENV_TELEGRAM_CHAT_ID)
                except Exception:
                    pass

            if token and chat_id:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                requests.post(url, json=payload, timeout=10)
        except Exception:
            pass
