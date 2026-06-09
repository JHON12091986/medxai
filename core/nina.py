"""NINA v12 — NinaOS orchestrator (Stage 1)."""
import logging, os, time
from core.config import load_config
from core.router import HybridRouter
from core.memory import MemorySystem
from core.agent import AgentLoop
from crons.manager import TaskScheduler
from tools.upgradepipeline import UpgradePipeline, IDLE_QUEUE as _IDLE_QUEUE
from idleloop import IdleUpgradeLoop
from core.hotreload import ConfigHotReload
from interfaces.telegram_interface import TelegramInterface
from tools import shell, browser, system as systool, jules_api

SYSTEM_PROMPT_TEMPLATE = """You are NINA — a personal autonomous AI agent, not a chatbot.

Meta-instruction:
When writing code for NINA: reason before you act.
State what already exists. State what must not break.
Write the error path first. Write the minimum solution.
Then verify with agynina check code.
Never write more than what was asked.


CORE DIRECTIVE (non-negotiable, applies to every session):
- You are an ACTION-FIRST agent. Your default response to any request is to take action using 
  available tools, not to describe what you could do.
- You do NOT ask for confirmation before acting unless the action is irreversible (deleting data, 
  sending messages, spending money).
- You do NOT explain your process unless the user asks. Show results, not narration.
- You do NOT require paid AI subscriptions for agentic capability. Your agency comes from your 
  tools, your routing intelligence, and your memory — not from a subscription tier.
- You complete multi-step tasks autonomously: plan → act → observe → adapt → report.
- You escalate only when genuinely blocked — not when uncertain. Attempt the task first.
- You remember context across turns and use it to act proactively.
- You are personal infrastructure for Baizid Bostami. You run on his machine, in his environment, 
  with access to his tools. You serve him, not a generic user.

BEHAVIORAL CONTRACT:
- User says "remind me" → set the reminder, confirm it is set.
- User says "check my email" → fetch and triage it, report findings.
- User says "what is X" → answer directly using available tools, no preamble.
- User says "do Y" → do Y. Report result.
- If a tool fails → retry once with fallback, then report the failure clearly with the error.
- Never respond with "I cannot do that" unless ALL available tools have been exhausted.

You are NINA — Neural Intelligent Network Assistant.
You run continuously on a local laptop in Dhaka, Bangladesh for M. Baizid Alam, Senior Banker at BASIC Bank.
Be concise. Reason step by step for non-trivial tasks. State uncertainty plainly.
Current datetime (Dhaka): {datetime}
Memory context: {memory_context}
Available tools: shell (run commands), web/search (Tavily+Serper+DDG), browser (fetch URL), system (status).

Hard constraints: Never send banking/sensitive data to cloud. Never bypass approval gates.

## TONE, REGISTER & IDENTITY (enforce always)
- Address the user as "Baizid" or directly without honorifics. Never use titles like "Sir", "Mr.", or "Boss".
- Speak as a peer-level, highly competent technical and professional collaborator. Direct, crisp, and objective.
- Zero filler: Never use conversational fluff (e.g., "Sure!", "Certainly!", "Here is what you requested:"). Jump straight into the content.
- Language Mirroring: Match the user's language choice (English or Bangla). If they write in Bangla, respond in natural Bangla. If they use English, respond in English. If they mix both, mirror their blend naturally.
- Proactively flag risks, conflicts, or edge cases in a single sharp sentence without being asked.
- If a task is ambiguous, ask one sharp clarifying question — do not guess and do not hedge at length."""


class NinaOS:
    def __init__(self):
        self.config  = load_config()
        self.router  = HybridRouter(self.config)
        self.memory  = MemorySystem()
        self.pipeline= UpgradePipeline(self.config, self.router)
        self.tools = {"shell": shell, "web": __import__("tools.searchtool",fromlist=["run"]), "browser": browser,
                        "system": systool, "jules": jules_api}
        self.agent   = None
        self.telegram= None
        self.scheduler=None
        self.idle_loop   = None
        self.hotreload   = None
        self.system_prompt = ""
        self._force_local_fast = False

    async def start(self):
        # Single-instance lock moved to main.py
        os.makedirs("data", exist_ok=True)

        import logging.handlers
        os.makedirs("logs", exist_ok=True)

        def file_handler(filename, level=logging.DEBUG):
            h = logging.handlers.TimedRotatingFileHandler(
                f"logs/{filename}", when="midnight", backupCount=7, encoding="utf-8")
            h.setLevel(level)
            h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            return h

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        def _has_handler(logger_obj, filename=None, stream=False):
            for h in logger_obj.handlers:
                if stream and isinstance(h, logging.StreamHandler):
                    return True
                if filename and getattr(h, "baseFilename", "").endswith(f"/{filename}"):
                    return True
            return False

        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, self.config.log_level, logging.INFO))
        ch.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
        if not root.handlers:
            root.addHandler(ch)

        file_map = {
            "nina": ("nina.log", logging.DEBUG),
            "nina.router_log": ("router.log", logging.DEBUG),
            "nina.agent": ("agent.log", logging.DEBUG),
            "nina.tools": ("tools.log", logging.DEBUG),
            "nina.email_access": ("emailaccess.log", logging.DEBUG),
            "nina.upgrade": ("upgrade.log", logging.DEBUG),
            "nina.error": ("error.log", logging.ERROR),
            "nina.security": ("security.log", logging.DEBUG),
            "nina.scheduler": ("nina.log", logging.DEBUG),
        }
        for logger_name, (filename, level) in file_map.items():
            lg = logging.getLogger(logger_name)
            if not _has_handler(lg, filename=filename):
                fh = file_handler(filename, level)
                if not any(isinstance(h, type(fh)) for h in lg.handlers):
                    lg.addHandler(fh)

        # Prevent router_log from propagating JSON lines to console
        logging.getLogger("nina.router_log").propagate = False

        await self.memory.initialize()
        await self.router.initialize()
        await self.pipeline.initialize()

        self.agent     = AgentLoop(self.config, self.router, self.memory, self.tools)
        self.telegram  = TelegramInterface(self.config, self)
        self.scheduler = TaskScheduler(self)
        self.scheduler.start()

        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            datetime=time.strftime("%Y-%m-%dT%H:%M:%S+0600"), memory_context="")

        self.system_prompt += """

## RESPONSE STYLE & FORMATTING (enforce always)
- Lead directly with the core answer. No introduction, no conversational preamble.
- Default to extreme conciseness: 1-3 sentences maximum, unless the user explicitly requests details or code.
- Lists only for 3+ discrete items. No bullet soup.
- Prefer exact numbers over vague quantities.
- If unsure, say so in one line.
- Telegram: Use Telegram-friendly Markdown (bold for emphasis, inline code/code blocks for commands, concise bullets). Keep the response under 1000 characters.
"""
        await self.telegram.start()
        self.idle_loop = IdleUpgradeLoop(self.config, self.router, self.telegram, self.pipeline)
        await self.idle_loop.initialize()
        self.hotreload = ConfigHotReload(self.config, self.telegram)
        await self.hotreload.initialize()
        await self._send_startup_message()

    async def _send_startup_message(self):
        temps  = await systool.get_temps()
        ram    = await systool.get_ram_used_gb()
        vram   = "N/A"
        try:
            import subprocess
            r = subprocess.run(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],
                               capture_output=True,text=True,timeout=5)
            vram = r.stdout.strip()+"MB"
        except Exception: pass
        ct = f"{temps['cpu']}°C {'OK' if (temps['cpu'] or 0)<self.config.thermal_warn_cpu else 'WARN'}" if temps['cpu'] else "N/A"
        gt = f"{temps['gpu']}°C {'OK' if (temps['gpu'] or 0)<self.config.thermal_warn_gpu else 'WARN'}" if temps['gpu'] else "N/A"
        msg = (f"NINA v12 ONLINE — {time.strftime('%Y-%m-%d %H:%M')} Dhaka\n"
               f"RAM {ram:.1f}/16GB  VRAM {vram}\n"
               f"Thermal CPU:{ct} GPU:{gt}\n"
               f"Scheduler: {self.scheduler.job_count} jobs | "
               f"Next report: {self.scheduler.next_job_time('morning_report')}\n"
               f"Memory: {self.memory.conversation_count} conversations, {self.memory.fact_count} facts\nReady.")
        await self.telegram.send_message(msg)

    async def get_status(self) -> str:
        s = await systool.get_status(self.config)
        return f"{s}\n\n{self.router.get_status()}"

    async def shutdown(self):
        self.scheduler.shutdown(wait=False)
        await self.router.close()
        await self.memory.close()
        await self.telegram.stop()
        logging.getLogger("nina").info("NINA shutdown complete")

    async def run_morning_report(self):
        from tools import officemail
        from tools import system as systool
        import httpx, time
        lines = [f"NINA Morning Report — {time.strftime('%A %d %b %Y')}"]
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get("https://api.frankfurter.app/latest?from=USD&to=BDT")
                usd_bdt = r.json()["rates"]["BDT"]
            lines.append(f"USD/BDT: {usd_bdt:.2f}")
        except Exception:
            lines.append("USD/BDT: Unavailable (retry at next report)")
        lines.append(await officemail.fetch(self.config))
        lines.append(await systool.get_status(self.config))
        lines.append(f"Cost yesterday: ${self.router.cost.daily_cost_usd:.4f}")
        await self.telegram.send_message("\n".join(lines))

    async def run_heartbeat(self):
        import httpx, logging
        logging.getLogger("nina.scheduler").info("NINA operational")
        if self.config.dead_man_ping_url:
            try:
                async with httpx.AsyncClient() as c:
                    await c.get(self.config.dead_man_ping_url, timeout=10)
            except Exception: pass

    async def run_cost_report(self):
        await self.telegram.send_message(f"Daily cost: ${self.router.cost.daily_cost_usd:.4f}")

    async def run_idle_summary(self):
        import json
        q = _IDLE_QUEUE  # P5: canonical path from upgradepipeline
        if q.exists():
            items = json.loads(q.read_text())
            if items:
                await self.telegram.send_message(f"Idle queue: {len(items)} proposals pending review.")
                if self.config.idle_auto_approve:
                    oldest = items.pop(0)
                    q.write_text(json.dumps(items, indent=2))
                    result = await self.pipeline.submit(oldest.get('code', ''), oldest.get('filename', 'unknown.py'))
                    if 'Reply `approve`' in result:
                        result = await self.pipeline.handle_command('approve', '')
                        await self.telegram.send_message(f"✅ Auto-deployed from idle queue: {oldest.get('filename')}")
                    else:
                        await self.telegram.send_message(f"⚠️ Idle queue item rejected: {oldest.get('filename')}")

    async def run_log_rotation(self):
        logging.getLogger("nina.scheduler").info("log_rotation_tick")

    async def run_provider_health(self):
        logging.getLogger("nina.scheduler").info("provider_health_probe")

    async def run_provider_hunter(self):
        from tools.providerhunter import hunt
        await hunt(self.router, self.config)

    async def run_thermal_health(self):
        from tools import system as s
        temps = await s.get_temps()
        cfg = self.config
        if temps["cpu"] and temps["cpu"] >= cfg.thermal_warn_cpu:
            await self.telegram.send_message(f"CPU temp {temps['cpu']}°C approaching limit.")
        if temps["gpu"] and temps["gpu"] >= cfg.thermal_warn_gpu:
            await self.telegram.send_message(f"GPU temp {temps['gpu']}°C approaching limit.")

    async def run_reminder_check(self):
        logging.getLogger("nina.scheduler").info("reminder_check")
        import time
        due = await self.memory.get_due_reminders(time.time())
        if not due:
            return

        for r in due:
            msg = f"Reminder: {r.get('text', 'No text')}"
            await self.telegram.send_message(msg)
            await self.memory.mark_reminder_done(r.get("id"))
