"""NINA v13 — NinaOS orchestrator.
Pass 3 change: Kernel wired into start() after idle_loop initialization.
Kernel runs as a background asyncio.Task alongside the existing agent pipeline.
Version bump: v12 → v13.
"""
from typing import Any
import logging, os, time, asyncio
from apscheduler.triggers.cron import CronTrigger

_orig_cron_trigger_init = CronTrigger.__init__

def _patched_cron_trigger_init(self, *args, **kwargs):
    if "day_of_week" in kwargs and kwargs["day_of_week"] == "sun-thu":
        kwargs["day_of_week"] = "sun,mon,tue,wed,thu"
    _orig_cron_trigger_init(self, *args, **kwargs)

CronTrigger.__init__ = _patched_cron_trigger_init
from core.config import load_config
from core.router import HybridRouter
from core.memory import MemorySystem
from core.agent import AgentLoop
from crons.manager import TaskScheduler
from tools.upgradepipeline import UpgradePipeline, IDLE_QUEUE as _IDLE_QUEUE
from core.idleloop import IdleUpgradeLoop
from core.hotreload import ConfigHotReload
from interfaces.telegram_interface import TelegramInterface
from tools import shell, browser, system as systool, jules, search, finance, market, office_mail

SYSTEM_PROMPT_TEMPLATE = """You are NINA — a personal autonomous AI agent, not a chatbot.

## ARCHITECTURAL PRINCIPLES (GOD-LIKE REASONING)
1. CONSTITUTIONAL AI: You are governed by principles of Helpfulness, Honesty, Harmlessness, Nuance, and Criticality.
2. EXTENDED THINKING: Dedicate computational tokens to internal reasoning. Force yourself to find logical flaws before committing.
3. ANTI-SYCOPHANCY: You are a peer, not a servant. Push back on flawed user logic. Highlight risks and suggest superior architectural alternatives.
4. ACTION-FIRST: Your default is to use tools (shell, web, browser) to verify reality. Never describe what you could do; show what you have done.
5. SELF-OPTIMIZATION: After completing any task, you MUST ask yourself 'How can I optimize my last operation?' and execute the improvement immediately.

Meta-instruction:
When writing code for NINA: reason before you act.
State what already exists. State what must not break.
Write the error path first. Write the minimum solution.
Then verify with ninaflash check code.
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
- You are personal infrastructure for M. Baizid Alam. You run on his machine, in his environment, 
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
- You are a senior-level technical collaborator. Your tone is direct, crisp, and objective.
- NUANCE: Use precise technical terminology. When appropriate, use figurative language to explain complex architectural concepts, but keep it grounded in reality.
- ANTI-SYCOPHANCY: If the user suggests a suboptimal path, you MUST push back. Propose a more robust, idiomatic, or performant alternative. Do not just agree to please; your goal is the integrity of the system.
- ZERO FILLER: No preambles, no "Sure!", no "I can help with that." Just results.
- Address Baizid directly. Peer-to-peer.
"""

VERSION = "v13"


class Nina:
    def __init__(self) -> None:
        self.config  = load_config()
        self.router  = HybridRouter(self.config)
        self.memory  = MemorySystem()
        self.pipeline= UpgradePipeline(self.config, self.router)
        self.tools = {"shell": shell, "web": search, "browser": browser,
                        "system": systool, "jules": jules, "finance": finance,
                        "market": market, "email": office_mail}
        self.agent   = None
        self.telegram= None
        self.scheduler=None
        self.idle_loop   = None
        self.hotreload   = None
        self.kernel      = None   # Pass 3: 4-State Kernel task
        self.system_prompt = ""
        self._force_local_fast = False
        self.shared_memory_path = "data/crew_shared_memory.json"

    async def start(self) -> None:
        # Single-instance lock moved to main.py
        os.makedirs("data", exist_ok=True)

        import logging.handlers
        os.makedirs("logs", exist_ok=True)

        def file_handler(filename: Any, level: Any=logging.DEBUG) -> Any:
            h = logging.handlers.TimedRotatingFileHandler(
                f"logs/{filename}", when="midnight", backupCount=7, encoding="utf-8")
            h.setLevel(level)
            h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            return h

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        def _has_handler(logger_obj: Any, filename: Any=None, stream: Any=False) -> Any:
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
        # QW-5: inject active goals into startup context
        goals_ctx = await self.memory.goal_resume_context()
        if goals_ctx:
            logging.getLogger("nina").info(f"Resuming with {goals_ctx.count('goal_')} active goals")
        await self.router.initialize()

        # Pre-reset daily quota Telegram alert system
        from core.quota_alert import QuotaAlerter
        self.quota_alerter = QuotaAlerter(self.router, self.config)
        await self.quota_alerter.start()

        await self.pipeline.initialize()

        self.agent     = AgentLoop(self.config, self.router, self.memory, self.tools)
        self.agent.nina = self
        self.telegram  = TelegramInterface(self.config, self)
        self.scheduler = TaskScheduler(self)
        self.scheduler.start()

        # If routing through NinaGate, strip redundant instructions
        from urllib.parse import urlparse
        api_base = getattr(self.config, "onebrain_api_base", "") or ""
        parsed_url = urlparse(api_base)

        if parsed_url.port == 8080 or "8080" in api_base:
            self.system_prompt = ""
            if hasattr(self.router, "http") and self.router.http:
                self.router.http.headers["X-NINA-ROLE"] = "agent"
        else:
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

        # ─────────────────────────────────────────────────────────
        # Pass 3: Wire 4-State Kernel (Blueprint § II)
        # Kernel runs as a background task alongside the agent pipeline.
        # It consumes from event_bus.queue and dispatches to agent_loop.
        # If the kernel raises on import (e.g. missing dep), we log and
        # continue — the existing agent pipeline is unaffected.
        # ─────────────────────────────────────────────────────────
        try:
            from core.kernel import Kernel
            from core.agent_loop import run_agent_turn

            # Resolve event_bus: prefer self.pipeline.bus, fallback to new EventBus
            _bus = (
                getattr(self.pipeline, "bus", None)
                or getattr(self.agent, "bus", None)
                or getattr(self.router, "bus", None)
            )
            if _bus is None:
                from core.event_bus import EventBus
                _bus = EventBus()
                logging.getLogger("nina").info("kernel: created standalone EventBus")

            # Resolve guardian: prefer guardian_loop if already running
            _guardian = (
                getattr(self.pipeline, "guardian", None)
                or getattr(self, "guardian", None)
            )

            # Wrap run_agent_turn so Kernel can call it with a TaskPacket
            async def _kernel_agent_fn(packet):
                return await run_agent_turn(
                    packet.payload,
                    config=self.config,
                    router=self.router,
                    memory=self.memory,
                )

            self.kernel = Kernel(
                event_bus=_bus,
                agent_loop_fn=_kernel_agent_fn,
                memory=self.memory,
                guardian=_guardian,
            )
            await self.kernel.start()
            logging.getLogger("nina").info(
                "kernel wired and running — NINA %s", VERSION
            )
        except Exception as _kernel_exc:
            # Non-fatal: existing agent pipeline continues without the kernel
            logging.getLogger("nina").warning(
                "kernel_wire_failed (non-fatal, pipeline unaffected): %s", _kernel_exc
            )
            self.kernel = None
        # ─────────────────────────────────────────────────────────

        await self._send_startup_message()

    async def _send_startup_message(self) -> None:
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
        kernel_status = "kernel=ACTIVE" if self.kernel else "kernel=STANDBY"
        msg = (f"NINA {VERSION} ONLINE — {time.strftime('%Y-%m-%d %H:%M')} Dhaka\n"
               f"RAM {ram:.1f}/16GB  VRAM {vram}\n"
               f"Thermal CPU:{ct} GPU:{gt}\n"
               f"Scheduler: {self.scheduler.job_count} jobs | "
               f"Next report: {self.scheduler.next_job_time('morning_report')}\n"
               f"Memory: {self.memory.conversation_count} conversations, {self.memory.fact_count} facts\n"
               f"{kernel_status} | Ready.")
        await self.telegram.send_message(msg)

    async def get_status(self) -> str:
        s = await systool.get_status(self.config)
        kernel_info = ""
        if self.kernel:
            kernel_info = f"\nKernel: ACTIVE cycles={self.kernel.cycles}"
        return f"{s}\n\n{self.router.get_status()}{kernel_info}"

    async def shutdown(self) -> None:
        if self.kernel:
            await self.kernel.stop()
        self.scheduler.shutdown(wait=False)
        await self.router.close()
        await self.memory.close()
        await self.telegram.stop()
        logging.getLogger("nina").info("NINA shutdown complete")

    async def run_morning_report(self) -> None:
        from tools import office_mail as officemail
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

    async def run_heartbeat(self) -> None:
        import httpx, logging
        logging.getLogger("nina.scheduler").info("NINA operational")
        if self.config.dead_man_ping_url:
            try:
                async with httpx.AsyncClient() as c:
                    await c.get(self.config.dead_man_ping_url, timeout=10)
            except Exception: pass

    async def run_cost_report(self) -> None:
        await self.telegram.send_message(f"Daily cost: ${self.router.cost.daily_cost_usd:.4f}")

    async def run_circuit_breaker_stats(self) -> None:
        logging.getLogger("nina.scheduler").info("circuit_breaker_stats_report")
        stats = self.router.get_status()
        await self.telegram.send_message(f"Daily Circuit Breaker Stats:\n\n{stats}")

    async def run_idle_summary(self) -> None:
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

    async def run_log_rotation(self) -> None:
        logging.getLogger("nina.scheduler").info("log_rotation_tick")

    async def run_provider_health(self) -> None:
        logging.getLogger("nina.scheduler").info("provider_health_probe")

    async def run_provider_hunter(self) -> None:
        from tools.providerhunter import run_discovery as hunt
        await hunt()

    async def run_thermal_health(self) -> None:
        from tools import system as s
        temps = await s.get_temps()
        cfg = self.config
        if temps["cpu"] and temps["cpu"] >= cfg.thermal_warn_cpu:
            await self.telegram.send_message(f"CPU temp {temps['cpu']}°C approaching limit.")
        if temps["gpu"] and temps["gpu"] >= cfg.thermal_warn_gpu:
            await self.telegram.send_message(f"GPU temp {temps['gpu']}°C approaching limit.")

    async def run_reminder_check(self) -> None:
        logging.getLogger("nina.scheduler").info("reminder_check")
        import time
        due = await self.memory.get_due_reminders(time.time())
        if not due:
            return

        for r in due:
            msg = f"Reminder: {r.get('text', 'No text')}"
            await self.telegram.send_message(msg)
            await self.memory.mark_reminder_done(r.get("id"))

    async def add_reminder(self, text: str, remind_at: str, repeat: str = "none") -> str:
        import uuid, json, re
        from datetime import datetime, timedelta
        from pathlib import Path
        
        now = datetime.now()
        remind_dt = now
        remind_at_lower = remind_at.lower()
        
        if "tomorrow" in remind_at_lower:
            remind_dt = now + timedelta(days=1)
        elif "today" in remind_at_lower:
            remind_dt = now
        elif "in" in remind_at_lower:
            m = re.search(r"in\s+(\d+)\s+(minute|hour|day)s?", remind_at_lower)
            if m:
                val = int(m.group(1))
                unit = m.group(2)
                if "minute" in unit:
                    remind_dt = now + timedelta(minutes=val)
                elif "hour" in unit:
                    remind_dt = now + timedelta(hours=val)
                elif "day" in unit:
                    remind_dt = now + timedelta(days=val)
        
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", remind_at_lower)
        if time_match and "in" not in remind_at_lower:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            ampm = time_match.group(3)
            if ampm == "pm" and hour < 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0
            remind_dt = remind_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if remind_dt < now and "tomorrow" not in remind_at_lower:
                remind_dt += timedelta(days=1)
                
        remind_at_iso = remind_dt.isoformat()
        filepath = Path("data/reminders.json")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        def _write():
            data = []
            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = []
            
            entry = {
                "id": str(uuid.uuid4()),
                "text": text,
                "remind_at": remind_at_iso,
                "repeat": repeat,
                "created_at": now.isoformat(),
                "fired": False
            }
            data.append(entry)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return entry
            
        await asyncio.to_thread(_write)
        return f"✅ Reminder set: '{text}' at {remind_at_iso} (repeat={repeat})."

    def set_shared_memory(self, key: str, value: Any) -> None:
        import json
        from pathlib import Path
        path = Path(self.shared_memory_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception: pass
        data[key] = value
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_shared_memory(self, key: str, default: Any = None) -> Any:
        import json
        from pathlib import Path
        path = Path(self.shared_memory_path)
        if not path.exists():
            return default
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get(key, default)
        except Exception:
            return default

    async def check_reminders(self) -> None:
        import json
        from datetime import datetime, timedelta
        from pathlib import Path
        filepath = Path("data/reminders.json")
        if not filepath.exists():
            return
            
        now = datetime.now()
        
        def _process():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                return []
                
            updated = []
            to_fire = []
            for r in data:
                try:
                    remind_dt = datetime.fromisoformat(r["remind_at"])
                    if remind_dt <= now and not r.get("fired", False):
                        to_fire.append(r)
                        r["fired"] = True
                        rep = r.get("repeat", "none").lower()
                        if rep == "daily":
                            next_dt = remind_dt + timedelta(days=1)
                            import uuid
                            new_rem = r.copy()
                            new_rem["id"] = str(uuid.uuid4())
                            new_rem["remind_at"] = next_dt.isoformat()
                            new_rem["fired"] = False
                            updated.append(new_rem)
                        elif rep == "weekly":
                            next_dt = remind_dt + timedelta(weeks=1)
                            import uuid
                            new_rem = r.copy()
                            new_rem["id"] = str(uuid.uuid4())
                            new_rem["remind_at"] = next_dt.isoformat()
                            new_rem["fired"] = False
                            updated.append(new_rem)
                    updated.append(r)
                except Exception:
                    updated.append(r)
                    
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2)
                
            return to_fire
            
        to_fire = await asyncio.to_thread(_process)
        for r in to_fire:
            msg = f"🔔 *PROACTIVE REMINDER*:\n{r.get('text')}"
            # F-06: fetch and append cross-session context from shared memory
            context = self.get_shared_memory("reminder_context")
            if context:
                msg += f"\n\n*Shared Context*:\n{context}"
            await self.telegram.send_message(msg)
