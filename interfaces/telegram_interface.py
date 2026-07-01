"""
NINA v13 -- TelegramInterface (Stage 3 / Pass 4)
Security gate, command handler, NLP fallback, streaming, flood protection, reset UX.

Symbiosis commands added (2026-06-22):
  /opencode <task>  — full 5-step NDEV+OpenCode+NinaGate+NinaSuperCLI dispatch
  /ndev             — show last nina_debug_out.txt (NDEV feedback)
  /oclog [N]        — tail last opencode run log (default 40 lines)
  /sync             — nina-super sync audit
  /doctor           — nina-super doctor health check

Pass 3 additions (2026-06-24):
  /ratchet              — autonomy ratchet status
  /ratchet ceiling <N>  — set max rung at runtime
  /ratchet reset        — emergency reset to OBSERVE
  /ratchet patches      — last 10 self-patch entries
  /ratchet proposals    — pending proposals

Pass 4 additions (2026-06-25):
  Live status display via status_bus subscribe/unsubscribe pattern.
  - subscribe() / unsubscribe() imported from core.status_bus at module top.
  - _stream_reply(): registers _status_update callback before routing,
    unconditionally unsubscribes in a finally block after stream completes.
  - _handle_opencode(): same subscribe/finally-unsubscribe pattern wrapping
    the tools.opencode.run_async call, editing the sent message on each
    status event.
  - Both callbacks are per-request closures, keyed by sent.message_id to
    prevent cross-request bleed on concurrent Telegram messages.
  - Null-safe: if status_bus is unavailable (ImportError), both handlers
    fall back to silent no-op stubs.

NLP triggers added:
  "opencode <task>" / "run opencode <task>"  → opencode dispatch
  "ndev status" / "show ndev"                → ndev tail
  "super sync" / "nina sync"                 → sync
  "doctor" / "health check"                  → doctor
  "ratchet status" / "autonomy ratchet"      → ratchet
"""

import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler


from interfaces.middleware import RateLimiter
from core.config import NinaConfig
from core.router import HybridRouter, ClassifiedTask
from core.task_classifier import classify_task
from tools.session_ledger import audit_sessions
from core.reminders import add_reminder, list_reminders
from core.knowledge import forget
from tools.finance import add_expense, set_budget, get_summary, list_expenses
from tools.ratchet_cmd import handle_ratchet_command  # Pass 3

# ── Pass 4: status_bus import (null-safe) ────────────────────────────────────
try:
    from core.status_bus import subscribe as _sb_subscribe, unsubscribe as _sb_unsubscribe
except ImportError:
    def _sb_subscribe(cb): pass      # no-op fallback
    def _sb_unsubscribe(cb): pass    # no-op fallback

logger = logging.getLogger("nina.telegram")


# Bolt: Pre-compiled regexes for hot-path NLP intent matching

_rate_limiter = RateLimiter(max_calls=20, period_seconds=60)
_NLP_INTENTS_RE = {
    "email": re.compile(r"check my email|fetch email|my emails"),
    "provider_hunt": re.compile(
        r"hunt for new providers|find providers|missing providers"
    ),
    "provider_status": re.compile(r"provider status|addkey list|show providers"),
    "config_update": re.compile(r"set ews|config update|change setting"),
    "rollback_request": re.compile(r"roll back|rollback"),
    "upgrade_history": re.compile(r"upgrade history|upgrade log"),
    "cost_report": re.compile(r"how much did i spend|cost report|daily cost"),
    "diagnose": re.compile(r"diagnose errors|auto-diagnose"),
    "run_schedule": re.compile(
        r"run the morning report|run scheduled job|morning report"
    ),
    "gpu_config": re.compile(r"gpu config|optimize gpu layers"),
    "clear_session": re.compile(r"clear my session|clear session"),
    "show_idle_queue": re.compile(r"show idle queue|idle proposals"),
    "ram_status": re.compile(r"what's using the most ram|ram usage"),
    # ── Symbiosis NLP triggers ──────────────────────────────────────────────
    "opencode_dispatch": re.compile(
        r"^(?:run\s+)?opencode\s+(.+)", re.IGNORECASE
    ),
    "ndev_status": re.compile(
        r"ndev status|show ndev|ndev output|debug out", re.IGNORECASE
    ),
    "super_sync": re.compile(
        r"super sync|nina sync|sync audit|sync nina", re.IGNORECASE
    ),
    "doctor_check": re.compile(
        r"\bdoctor\b|health check|nina doctor|super doctor", re.IGNORECASE
    ),
    "oclog_tail": re.compile(
        r"oclog|opencode log|last opencode run|tail opencode", re.IGNORECASE
    ),
    # ── Pass 3: Ratchet NLP trigger ─────────────────────────────────────────
    "ratchet_status": re.compile(
        r"ratchet status|autonomy ratchet|autonomy level|ratchet rung", re.IGNORECASE
    ),
}

_SECRET_KEYS_RE = re.compile(r"key|token|secret|password", re.IGNORECASE)
_SEARCH_KEYWORDS_RE = re.compile(
    r"search|rate|price|news|today|current|latest|fetch|find|what is|how much"
)

sec_log = logging.getLogger("nina.security")

COMMANDS = {
    "task",
    "ask",
    "email",
    "shell",
    "remember",
    "recall",
    "forget",
    "patch",
    "generate",
    "approve",
    "reject",
    "rollback",
    "addkey",
    "status",
    "router",
    "models",
    "logs",
    "abort",
    "start",
    "reset",
    "help",
    "backlog",
    "errors",
    "jules",
    "session_audit",
    "cron_status",
    "remind",
    "reminders",
    "recall",
    "spend",
    "budget",
    "expenses",
    "goal",
    "goals",
    # ── Symbiosis commands ───────────────────────────────────────────────────
    "opencode",
    "ndev",
    "oclog",
    "sync",
    "doctor",
    # ── Pass 3: Autonomy ratchet ─────────────────────────────────────────────
    "ratchet",
}

HELP_TEXT = """*NINA v13 Commands*

`task <goal>` -- Multi-step autonomous task
`ask <question>` -- Quick single-turn question
`email` -- Fetch & analyze both mailboxes
`shell <cmd>` -- Allowlisted system command
`remember <text>` -- Save to permanent memory
`recall <query>` -- Search permanent memory
`forget <key>` -- Delete a saved fact
`patch <file> <url>` -- Deploy a Python module upgrade
`generate <f> <d>` -- AI-generate a module upgrade
`approve` -- Confirm pending upgrade
`reject` -- Discard pending upgrade
`rollback <file>` -- Restore previous version
`addkey <P> <key>` -- Add a provider API key
`addkey list` -- Show provider status & signup links
`models` -- Show current model per provider
`backlog` -- Show top 5 READY items
`status` -- System health snapshot
`errors` -- Show open error register items
`cron_status` -- Show background cron status & health
`router` -- Provider routing table
`jules <cmd>` -- Jules API (dispatch, status, feedback)
`logs` -- Last 50 lines of nina.log
`abort` -- Kill active task immediately
`start` -- Reset session history
`reset` -- Full reinitialization (backs up memory first)

*Symbiosis Commands*
`opencode <task>` -- Full NDEV+OpenCode+NinaGate dispatch (5-step loop)
`ndev` -- Show last nina_debug_out.txt (NDEV feedback layer)
`oclog [N]` -- Tail last OpenCode run log (default 40 lines)
`sync` -- Run nina-super sync audit (commit artifacts)
`doctor` -- Run nina-super doctor health check

*Autonomy Ratchet (Pass 3)*
`ratchet` -- Show autonomy ratchet status & rung
`ratchet ceiling <0-4>` -- Set max autonomy rung at runtime
`ratchet reset` -- Emergency reset to OBSERVE (all autonomy suspended)
`ratchet patches` -- Last 10 self-patch entries
`ratchet proposals` -- Pending unexecuted proposals

You can also just talk:
check my email, hunt for new providers, show idle queue
diagnose errors, run the morning report now, how much did I spend today
set EWS emails to 25, roll back web.py, what's using the most RAM
opencode add docstrings to tools/finance.py, ndev status, super sync
ratchet status, autonomy level, autonomy ratchet"""


class TelegramInterface:

    def __init__(self, config: NinaConfig, nina_os):
        self.config = config
        self.nina = nina_os
        self.session_history: list[dict] = []
        self._flood_window: list[float] = []
        self._active_task: Optional[asyncio.Task] = None
        self._app: Optional[Application] = None
        cfg_dict = self.config.model_dump() if hasattr(self.config, 'model_dump') else self.config.dict()
        # Pre-cache secret values to avoid dict serialization overhead on every message
        self._secret_values = []
        for k in cfg_dict.keys():
            if _SECRET_KEYS_RE.search(k):
                v = cfg_dict.get(k)
                if v and isinstance(v, str):
                    self._secret_values.append(v)
        # Gap analysis: engine + pending approval state
        from core.gap_analysis import GapAnalysisEngine
        self._gap_engine = GapAnalysisEngine(self.nina.router)
        self._pending_gap: Optional[tuple] = None  # (GapReport, original_goal, task)

    async def start(self):
        from telegram.request import HTTPXRequest
        
        # Aumentamos el tiempo de espera a 30 segundos para evitar los ReadTimeout
        request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
        
        self._app = Application.builder().token(self.config.telegram_bot_token).request(request).build()
        
        # Register document handler first to prevent catch-all swallowing
        self._app.add_handler(
            MessageHandler(filters.Document.ALL, self._handle_document_update)
        )
        self._app.add_handler(MessageHandler(filters.ALL, self._handle_update))
        self._app.add_handler(CallbackQueryHandler(self._handle_callback_query))
        await self._app.initialize()

        await self._app.start()
        await self._app.updater.start_polling(drop_pending_updates=True)
        logger.info("TelegramInterface polling started with 30s timeout")

    async def stop(self):
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    # Centrally defined last-mile parse_mode constants to prevent BadRequest crashes
    PARSE_MODE_DEFAULT = None
    PARSE_MODE_MARKDOWN_V2 = "MarkdownV2"

    def _mask_secrets(self, text: str) -> str:
        # Last-mile secret masking helper to prevent API keys and credentials leaking
        if not isinstance(text, str):
            return text
        # Use pre-cached secret values instead of dumping config dict on every call
        for v in self._secret_values:
            if v in text:
                masked = v[:4] + "***" + v[-4:] if len(v) > 8 else "***"
                text = text.replace(v, masked)
        return text

    async def _reply(self, update, text: str, **kwargs):
        # Mask secrets and reply to a message using safe parse_mode defaults
        text = self._mask_secrets(str(text))
        if "parse_mode" not in kwargs:
            kwargs["parse_mode"] = self.PARSE_MODE_DEFAULT
        # Call update.message.reply_text (resolving recursive infinite loop)
        return await update.message.reply_text(text, **kwargs)

    async def _edit_message(self, message, text: str, **kwargs):
        # Mask secrets and edit an existing message using safe parse_mode defaults
        text = self._mask_secrets(str(text))
        if "parse_mode" not in kwargs:
            kwargs["parse_mode"] = self.PARSE_MODE_DEFAULT
        return await message.edit_text(text, **kwargs)

    # ---- Document Handler ----------------------------------------------------
    async def _handle_document_update(
        self, update: Update, ctx: ContextTypes.DEFAULT_TYPE
    ):
        # Dedicated handler to ensure documents are processed first and never dropped
        if not update.message or not update.message.document:
            return
        uid = str(update.message.from_user.id)
        if uid != str(self.config.telegram_chat_id):
            sec_log.warning(
                f"unauthorized_access uid={uid}", extra={"log": "security.log"}
            )
            return

        doc = update.message.document
        if doc.file_name and doc.file_name.endswith(".py"):
            size = doc.file_size or 0
            if size > 100_000:
                await self._reply(update, "File too large. Max 100KB.")
                return
            await self._reply(update, "Routing to upgrade pipeline...")
            try:
                await update.message.delete()
            except Exception:
                pass
            asyncio.create_task(self._handle_upgrade_file(update, ctx))
        else:
            await self._reply(
                update, "Unsupported document format. Only .py files are allowed."
            )

    async def _handle_update(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            if not update.message:
                return
            
            # --- AGREGADO PARA DEBUG ---
            uid = str(update.message.from_user.id)
            print(f"DEBUG: Mensaje recibido de UID: {uid}")
            # ---------------------------

            if not _rate_limiter.is_allowed(update.effective_user.id):
                await update.message.reply_text("⚠️ Too many requests. Please wait.")
                return

<<<<<<< HEAD
            if uid != str(self.config.authorized_user_id):
                sec_log.warning(f"unauthorized_access uid={uid} (Expected: {self.config.authorized_user_id})")
                # Opcional: Descomenta la siguiente línea si quieres que te avise en Telegram aunque no seas el autorizado
                # await update.message.reply_text(f"Acceso denegado. Tu ID es: {uid}")
=======
            if uid != str(self.config.telegram_chat_id):
                sec_log.warning(
                    f"unauthorized_access uid={uid}", extra={"log": "security.log"}
                )
>>>>>>> cbb4b4dcd44382648448ba40737f237f25289730
                return

            text = (update.message.text or "").strip()
            if not text:
                return

            now = time.time()
            self._flood_window = [
                t for t in self._flood_window if now - t < self.config.flood_window_s
            ]
            if len(self._flood_window) >= self.config.flood_max_messages:
                queued = len(self._flood_window) - self.config.flood_max_messages + 1
                sec_log.warning(
                    f"authorized_user_flood uid={uid}", extra={"log": "security.log"}
                )
                await self._reply(update, f"Slow down -- {queued} message(s) queued.")
                return
            self._flood_window.append(now)

            if hasattr(self.nina, "idle_loop") and self.nina.idle_loop:
                self.nina.idle_loop.record_user_message()
            asyncio.create_task(self._dispatch(update, text))

        except Exception as e:
            import logging

            logging.getLogger("nina.telegram").error(
                f"Handler error: {e}", exc_info=True
            )
            try:
                await ctx.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ NINA encountered an error. The team has been notified.",
                )
            except Exception:
                pass

    # ---- Dispatcher ----------------------------------------------------------

    async def _dispatch(self, update: Update, text: str):
        parts = text.split(None, 1)
        cmd = parts[0].lstrip("/").lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in COMMANDS:
            await self._handle_command(update, cmd, arg)
        else:
            await self._handle_nlp(update, text)

    async def _handle_command(self, update: Update, cmd: str, arg: str):
        router: HybridRouter = self.nina.router

        if cmd == "help":
            await self._reply(update, HELP_TEXT, parse_mode=self.PARSE_MODE_DEFAULT)

        elif cmd == "status":
            s = await self.nina.get_status()
            reply = f"{s}\n\n{self.nina.router.get_health_summary()}"
            await self._reply(update, reply)

        elif cmd == "session_audit":
            report = audit_sessions()
            await update.message.reply_text(report)

        elif cmd == "cron_status":
            try:
                from crons.manager import get_job_metrics, _active_scheduler
                metrics = get_job_metrics()
                lines = ["⏰ *NINA Background Cron Status*"]
                
                for job_id in sorted(metrics.keys()):
                    m = metrics[job_id]
                    status = m.get("status", "PENDING")
                    status_emoji = "🟢" if status == "SUCCESS" else "🔴" if status == "FAILED" else "🟡"
                    
                    next_run = "None"
                    schedule_str = "None"
                    if _active_scheduler and _active_scheduler._sched:
                        job = _active_scheduler._sched.get_job(job_id)
                        if job:
                            next_run = str(job.next_run_time).split(".")[0] if job.next_run_time else "None"
                            schedule_str = str(job.trigger)
                            
                    if schedule_str == "None":
                        schedule_str = m.get("schedule", "None")
                    if next_run == "None":
                        next_run = m.get("next_run", "None")
                        
                    lines.append(f"{status_emoji} *{job_id}*:")
                    lines.append(f"  • Status: `{status}` (Fail count: {m.get('fail_count', 0)})")
                    lines.append(f"  • Last Run: `{m.get('last_run', 'Never')}`")
                    lines.append(f"  • Next Run: `{next_run}`")
                    lines.append(f"  • Trigger: `{schedule_str}`")
                    if m.get("last_error"):
                        lines.append(f"  • Error: `{m.get('last_error')}`")
                
                reply = "\n".join(lines)
                await self._reply(update, reply[:4000], parse_mode=self.PARSE_MODE_DEFAULT)
            except Exception as e:
                await self._reply(update, f"Error gathering cron status: {e}")

        elif cmd == "models":
            reply = await router.get_models_status()
            await self._reply(update, reply)

        elif cmd == "router":
            await self._reply(update, router.get_status())

        elif cmd == "logs":
            log_path = Path("logs/nina.log")
            if log_path.exists():
                lines = log_path.read_text().splitlines()[-50:]
                await self._reply(update, "\n".join(lines)[-4000:])
            else:
                await self._reply(update, "nina.log not found.")

        elif cmd == "backlog":
            backlog_path = Path("docs/space/jules_backlog.md")
            if not backlog_path.exists():
                await self._reply(update, "Backlog not found.")
                return

            try:
                backlog_content = backlog_path.read_text()
                ready_items = []
                for line in backlog_content.splitlines():
                    if line.strip().startswith("|") and "`READY`" in line:
                        parts_line = [p.strip() for p in line.split("|") if p.strip()]
                        if len(parts_line) >= 3:
                            tid = parts_line[0]
                            title = parts_line[1] if "`READY`" in parts_line[2] else parts_line[2]
                            ready_items.append(f"• {tid}: {title}")
                            if len(ready_items) >= 5: break
                
                reply = "*Top 5 READY Backlog Items:*\n" + "\n".join(ready_items) if ready_items else "No READY items found."
                await self._reply(update, reply, parse_mode=self.PARSE_MODE_DEFAULT)
            except Exception as e:
                await self._reply(update, f"Error: {e}")

        elif cmd == "errors":
            path = Path("docs/space/nina_error_register.md")
            if not path.exists():
                await self._reply(update, "Error register not found.")
            else:
                lines = path.read_text().splitlines()
                open_items = []
                in_table = False
                for line in lines:
                    if line.startswith("| ID"): in_table = True; continue
                    if in_table and line.startswith("|"):
                        parts_line = [p.strip() for p in line.split("|")]
                        if len(parts_line) >= 6:
                            if "OPEN" in parts_line[5] or "PENDING" in parts_line[5]:
                                open_items.append(f"• [{parts_line[1]}] {parts_line[4]}")
                reply = "Open Error Register Items:\n" + "\n".join(open_items) if open_items else "No open errors found."
                await self._reply(update, reply[:4000])

        elif cmd == "jules":
            from tools import jules
            result = await jules.run(arg)
            await self._reply(update, result[:4000])

        elif cmd == "start":
            self.session_history.clear()
            await self._reply(update, "Session cleared.")

        elif cmd == "reset":
            await self._handle_reset(update)

        elif cmd == "abort":
            if self._active_task and not self._active_task.done():
                self._active_task.cancel()
                await self._reply(update, "Task aborted.")
            else:
                await self._reply(update, "No active task.")

        elif cmd == "ask":
            await self._stream_reply(
                update, arg, ClassifiedTask("quick", 300, False, False)
            )

        elif cmd == "task":
            task = classify_task(arg, [])
            await self._stream_reply(update, arg, task, use_agent=True)

        elif cmd == "email":
            await self._stream_reply(
                update,
                "fetch and analyze both mailboxes",
                ClassifiedTask("general", 500, False, False),
            )

        elif cmd == "shell":
            result = await self.nina.tools["shell"].run(arg)
            await self._reply(update, result[:4000])

        elif cmd == "remind":
            if not arg.strip():
                reply = "Usage: /remind <message> at YYYY-MM-DD HH:MM [daily|weekly]"
            else:
                import re
                m = re.match(
                    r"(.+?) at (\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?: (daily|weekly))?",
                    arg.strip()
                )
                if not m:
                    reply = "Usage: /remind <message> at YYYY-MM-DD HH:MM [daily|weekly]"
                else:
                    msg, dt_str, repeat = m.group(1), m.group(2), m.group(3)
                    due_iso = dt_str.replace(" ", "T") + ":00"
                    reply = add_reminder(msg, due_iso, repeat)
            await self._reply(update, reply)

        elif cmd == "reminders":
            await self._reply(update, list_reminders())

        elif cmd == "goal":
            subparts = arg.strip().split(None, 1)
            if not subparts:
                await self._reply(update, "Usage: /goal add <text>  or  /goal done <id>")
                return
            subcmd = subparts[0].lower()
            subarg = subparts[1] if len(subparts) > 1 else ""
            if subcmd == "add" and subarg:
                goal_id = await self.nina.memory.goal_add(subarg)
                await self._reply(update, f"✅ Goal added: {subarg} (ID: {goal_id})")
            elif subcmd == "done" and subarg:
                await self.nina.memory.goal_done(subarg)
                await self._reply(update, f"✅ Goal {subarg} marked done")
            else:
                await self._reply(update, "Usage: /goal add <text>  or  /goal done <id>")

        elif cmd == "goals":
            goals = await self.nina.memory.goal_list()
            if not goals:
                await self._reply(update, "No active goals found.")
            else:
                lines = []
                for i, g in enumerate(goals, 1):
                    lines.append(f"{i}. [{g['id']}] (P{g['priority']}) {g['description']}")
                await self._reply(update, "\n".join(lines))

        elif cmd == "remember":
            await self.nina.memory.kb_add_entry(tags=["manual"], text=arg)
            await self._reply(update, f"Remembered: {arg}")

        elif cmd == "recall":
            results = await self.nina.memory.kb_search(query=arg)
            if results:
                lines = [f"• {r['text']}" for r in results]
                await self._reply(update, "🧠 KB matches:\n" + "\n".join(lines))
            else:
                await self._reply(update, f"Nothing found for '{arg}'.")

        elif cmd == "forget":
            await self._reply(update, forget(arg))

        elif cmd == "spend":
            parts = arg.strip().split(None, 2)
            if len(parts) < 2:
                reply = "Usage: /spend <amount> <category> [note]"
            else:
                try:
                    amount = float(parts[0])
                    category = parts[1]
                    note = parts[2] if len(parts) > 2 else ""
                    reply = add_expense(amount, category, note)
                except ValueError:
                    reply = "Amount must be a number. Usage: /spend <amount> <category>"
            await self._reply(update, reply)

        elif cmd == "budget":
            try:
                amount = float(arg.strip())
                reply = set_budget(amount)
            except ValueError:
                reply = "Usage: /budget <amount>  (in BDT)"
            await self._reply(update, reply)

        elif cmd == "expenses":
            if arg.strip().lower() == "list":
                await self._reply(update, list_expenses())
            else:
                await self._reply(update, get_summary())

        elif cmd == "addkey":
            await self._handle_addkey(update, arg)

        elif cmd in ("approve", "reject", "patch", "generate", "rollback"):
            result = await self.nina.pipeline.handle_command(cmd, arg)
            await self._reply(update, result[:4000])

        # ── Symbiosis commands ─────────────────────────────────────────────────

        elif cmd == "opencode":
            await self._handle_opencode(update, arg)

        elif cmd == "ndev":
            await self._handle_ndev(update)

        elif cmd == "oclog":
            try:
                n = int(arg.strip()) if arg.strip().isdigit() else 40
            except ValueError:
                n = 40
            await self._handle_oclog(update, n)

        elif cmd == "sync":
            await self._handle_sync(update)

        elif cmd == "doctor":
            await self._handle_doctor(update)

        # ── Pass 3: Autonomy Ratchet command ───────────────────────────────────

        elif cmd == "ratchet":
            try:
                # Resolve ratchet from pipeline or nina directly
                ratchet = (
                    getattr(self.nina.pipeline, "ratchet", None)
                    or getattr(self.nina, "ratchet", None)
                )
                if ratchet is None:
                    await self._reply(update, "⚠️ Ratchet not available — pipeline not initialised.")
                    return
                result = await handle_ratchet_command(arg, ratchet, self.nina)
                await self._reply(update, result)
            except Exception as e:
                await self._reply(update, f"❌ ratchet error: {e}")

        else:
            await self._reply(update, "Unknown command. /help for the list.")

    # ── Symbiosis handlers ─────────────────────────────────────────────────────

    async def _handle_opencode(self, update: Update, task: str):
        """Full 5-step NDEV+OpenCode+NinaGate+NinaSuperCLI dispatch.

        Pass-4: subscribes a _status_update closure to status_bus before
        dispatching, editing the sent message on each pipeline status event.
        Unconditionally unsubscribes in a finally block to prevent listener
        accumulation across concurrent requests.
        """
        if not task.strip():
            await self._reply(
                update,
                "Usage: /opencode <task>\nExample: /opencode add docstrings to tools/finance.py"
            )
            return

        sent = await self._reply(update, f"⚙️ OpenCode dispatching...\n`{task[:120]}`")

        # Pass-4: per-request status_bus subscriber keyed by message_id
        _msg_id = sent.message_id

        def _status_update(event: dict):
            """Edit the sent message with live pipeline status from status_bus."""
            stage = event.get("stage", "")
            msg   = event.get("message", "")
            if not msg:
                return
            status_line = f"⚙️ [{stage}] {msg}"
            try:
                asyncio.get_event_loop().call_soon_threadsafe(
                    asyncio.ensure_future,
                    self._edit_message(sent, status_line[:4096])
                )
            except Exception:
                pass

        _sb_subscribe(_status_update)
        try:
            from tools.opencode import run_async
            result = await run_async(task)

            status  = "✅" if result["success"] else "❌"
            dur     = result["duration_s"]
            out     = result["output"][:800] or "(no output)"
            err_snip = f"\n⚠️ {result['error'][:200]}" if result["error"] else ""
            ndev    = "📤 NDEV loop closed — output pushed to GitHub" if result.get("ndev_upload_ok") else ""
            sync_ok = "🔄 Sync: ✅" if result.get("super_sync_ok") else "🔄 Sync: ❌"

            reply = (
                f"{status} OpenCode done in {dur}s\n\n"
                f"```\n{out}\n```"
                f"{err_snip}\n\n"
                f"{sync_ok}  {ndev}"
            )
            try:
                await self._edit_message(sent, reply[:4096])
            except Exception:
                await self._reply(update, reply[:4096])
        except Exception as e:
            await self._reply(update, f"❌ opencode dispatch error: {e}")
        finally:
            _sb_unsubscribe(_status_update)

    async def _handle_ndev(self, update: Update):
        """Show last 60 lines of ~/nina_debug_out.txt (NDEV feedback layer)."""
        debug_out = Path.home() / "nina_debug_out.txt"
        if not debug_out.exists():
            await self._reply(update, "nina_debug_out.txt not found — no NDEV run yet.")
            return
        lines = debug_out.read_text(encoding="utf-8").splitlines()
        tail  = "\n".join(lines[-60:])
        await self._reply(update, f"📋 NDEV last output:\n```\n{tail[-3800:]}\n```")

    async def _handle_oclog(self, update: Update, n: int = 40):
        """Tail last opencode run log."""
        try:
            from tools.opencode import tail_last_log
            tail = tail_last_log(n)
            await self._reply(update, f"📜 Last OpenCode log ({n} lines):\n```\n{tail[-3800:]}\n```")
        except Exception as e:
            await self._reply(update, f"❌ oclog error: {e}")

    async def _handle_sync(self, update: Update):
        """Run nina-super sync audit."""
        sent = await self._reply(update, "🔄 Running nina-super sync audit...")
        try:
            import subprocess
            from pathlib import Path as _Path
            r = subprocess.run(
                ["nina-super", "sync", "audit"],
                cwd=str(_Path.home() / "nina"),
                capture_output=True, text=True, timeout=60
            )
            out = (r.stdout + r.stderr).strip()[-2000:]
            ok  = "✅" if r.returncode == 0 else "❌"
            try:
                await self._edit_message(sent, f"{ok} sync audit:\n```\n{out}\n```")
            except Exception:
                await self._reply(update, f"{ok} sync audit:\n```\n{out}\n```")
        except Exception as e:
            await self._reply(update, f"❌ sync error: {e}")

    async def _handle_doctor(self, update: Update):
        """Run nina-super doctor health check."""
        sent = await self._reply(update, "🩺 Running nina-super doctor...")
        try:
            from tools.opencode import doctor as oc_doctor
            import json as _json
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, oc_doctor)
            raw  = data.get("raw", _json.dumps(data, indent=2))
            ok   = "✅" if data.get("doctor_ok") else "❌"
            try:
                await self._edit_message(sent, f"{ok} Doctor:\n```\n{str(raw)[-3000:]}\n```")
            except Exception:
                await self._reply(update, f"{ok} Doctor:\n```\n{str(raw)[-3000:]}\n```")
        except Exception as e:
            await self._reply(update, f"❌ doctor error: {e}")

    # ---- NLP fallback --------------------------------------------------------

    async def _handle_nlp(self, update: Update, text: str):
        intent_map = {
            "email": ("email", ""),
            "provider_hunt": ("shell", "python -m tools.providerhunter"),
            "provider_status": ("router", ""),
            "cost_report": ("status", ""),
            "diagnose": ("logs", ""),
            "run_schedule": ("task", "run morning report"),
            "clear_session": ("start", ""),
            "show_idle_queue": ("task", "show idle queue"),
            "ram_status": ("status", ""),
            "gpu_config": ("task", ""),
            "config_update": ("task", text),
            "rollback_request": ("task", text),
            "upgrade_history": ("task", "show upgrade history"),
            # ── Symbiosis NLP → command routing ──────────────────────────────
            "ndev_status":    ("ndev",    ""),
            "super_sync":     ("sync",    ""),
            "doctor_check":   ("doctor",  ""),
            "oclog_tail":     ("oclog",   "40"),
            # ── Pass 3: Ratchet NLP → command routing ─────────────────────────
            "ratchet_status": ("ratchet", ""),
        }

        lower = text.lower()
        intent = "general_task"
        for key, regex in _NLP_INTENTS_RE.items():
            if key == "opencode_dispatch":
                m = regex.match(text)
                if m:
                    # Extract the task after "opencode" / "run opencode"
                    asyncio.create_task(self._handle_opencode(update, m.group(1).strip()))
                    return
            elif regex.search(lower):
                intent = key
                break

        if intent == "general_task":
            from tools.search import search

            if _SEARCH_KEYWORDS_RE.search(lower):
                result = await search(text)
                await self._reply(update, result[:4000])
                return

            # ── Gap analysis feedback loop ──────────────────────────────────────
            # If user is responding to a pending gap analysis, handle it first
            if self._pending_gap is not None:
                consumed = await self._handle_gap_response(update, text)
                if consumed:
                    return

            task = classify_task(text, [])

            # Intercept feature/upgrade requests for gap analysis
            if self._gap_engine.is_feature_request(text):
                report = await self._gap_engine.analyze(text, task)
                if report.auto_proceed:
                    # High confidence — note analysis and proceed immediately
                    await self._reply(update, report.to_auto_proceed_note())
                else:
                    # Hold execution — ask user to confirm
                    self._pending_gap = (report, text, task)
                    await self._reply(update, report.to_telegram())
                    return
            # ── End gap analysis ────────────────────────────────────────────────

            use_agent = (task.complexity in ("COMPLEX", "MASSIVE")) or (task.task_type in ("coding", "research", "diagnostic"))
            await self._stream_reply(update, text, task, use_agent=use_agent)
            return

        cmd, arg = intent_map.get(intent, ("task", text))
        await self._handle_command(update, cmd, arg)

    # ---- Gap analysis feedback handler --------------------------------------

    async def _handle_gap_response(self, update, text: str) -> bool:
        """
        Handle user's reply to a pending gap analysis report.
        Returns True if the message was consumed (yes/no/modify), False otherwise.
        """
        t = text.lower().strip()
        report, original_goal, task = self._pending_gap

        # User approves → proceed
        if t in {"yes", "y", "proceed", "ok", "go", "sure", "do it", "go ahead", "continue", "confirm"}:
            self._pending_gap = None
            await self._reply(update, "⚙️ Proceeding with implementation...")
            await self._stream_reply(update, original_goal, task, use_agent=True)
            return True

        # User cancels → discard
        if t in {"no", "n", "cancel", "abort", "stop", "reject", "skip", "nope", "nah"}:
            self._pending_gap = None
            await self._reply(update, "❌ Cancelled. Feature request discarded — nothing was changed.")
            return True

        # User sent a modified/refined request → re-run gap analysis on new text
        if len(text) > 10 and text != original_goal:
            self._pending_gap = None
            await self._reply(update, "🔄 Re-running gap analysis on your updated request...")
            await self._handle_nlp(update, text)
            return True

        return False

    # ---- Streaming reply -----------------------------------------------------

    async def _stream_reply(
        self, update: Update, prompt: str, task: ClassifiedTask, use_agent: bool = False
    ):
        """Route a prompt through HybridRouter with live status display.

        Pass-4: subscribes a _status_update closure to status_bus before
        routing begins, forwarding pipeline stage events to the sent Telegram
        message via _edit_message. Unconditionally unsubscribes in a finally
        block after the stream completes or errors, keyed by sent.message_id
        to prevent cross-request listener bleed on concurrent messages.
        """
        while len(self.session_history) > self.config.session_max_turns * 2:
            self.session_history.pop(0)
        self.session_history.append({"role": "user", "content": prompt})

        msgs = [
            {"role": "system", "content": self.nina.system_prompt}
        ] + self.session_history
        sent = await self._reply(update, "...")

        # Pass-4: per-request status_bus subscriber keyed by message_id
        _msg_id = sent.message_id

        def _status_update(event: dict):
            """Edit the sent message with live pipeline status from status_bus."""
            stage = event.get("stage", "")
            msg   = event.get("message", "")
            if not msg:
                return
            status_line = f"⏳ [{stage}] {msg}"
            try:
                asyncio.get_event_loop().call_soon_threadsafe(
                    asyncio.ensure_future,
                    self._edit_message(sent, status_line[:4096])
                )
            except Exception:
                pass

        _sb_subscribe(_status_update)
        try:
            use_stream = not use_agent
            if use_stream:
                try:
                    await self._edit_message(sent, "⏳ Thinking...")
                    coro = self.nina.router.route(
                        prompt,
                        msgs,
                        task,
                        force_local=getattr(self.nina, "_force_local_fast", False),
                        stream=True,
                    )
                    self._active_task = asyncio.create_task(coro)
                    stream_generator = await self._active_task
                    
                    accumulated = []
                    last_edit_time = time.time()
                    token_count = 0
                    
                    async for chunk in stream_generator:
                        accumulated.append(chunk)
                        token_count += 1
                        now = time.time()
                        if token_count >= 30 or (now - last_edit_time) >= 2.0:
                            current_text = "".join(accumulated)
                            if current_text.strip():
                                try:
                                    await self._edit_message(sent, current_text)
                                except Exception:
                                    pass
                            last_edit_time = now
                            token_count = 0
                            
                    final_text = "".join(accumulated)
                    if final_text.strip():
                        try:
                            await self._edit_message(sent, final_text)
                        except Exception:
                            pass
                    self.session_history.append({"role": "assistant", "content": final_text})
                    return
                except Exception as stream_err:
                    logger.warning(f"Streaming failed: {stream_err}. Falling back to standard non-streaming.")

            if use_agent:
                coro = self.nina.agent.run(prompt, task, self.session_history)
            else:
                coro = self.nina.router.route(
                    prompt,
                    msgs,
                    task,
                    force_local=getattr(self.nina, "_force_local_fast", False),
                )

            self._active_task = asyncio.create_task(coro)
            result = await self._active_task

            final = result[:4096]
            if final != "...":
                try:
                    await self._edit_message(sent, final)
                except Exception:
                    pass
            if len(result) > 4096:
                for chunk in [
                    result[i : i + 4096] for i in range(4096, len(result), 4096)
                ]:
                    await self._reply(update, chunk)

            self.session_history.append({"role": "assistant", "content": result})

        except asyncio.CancelledError:
            await self._edit_message(sent, "Task aborted.")
        except Exception as e:
            logger.exception("stream_reply_error")
            await self._edit_message(
                sent,
                f"Error {type(e).__name__}: {str(e)[:200]}\n"
                "Try /ask for a simpler route, or /status to check providers.",
                parse_mode=self.PARSE_MODE_DEFAULT,
            )
        finally:
            _sb_unsubscribe(_status_update)

    # ---- Reset UX ------------------------------------------------------------

    async def _handle_reset(self, update: Update):
        await self._reply(
            update, "Reset will wipe all session memory. Creating backup first..."
        )
        try:
            backup_path = await self.nina.memory.backup()
            await self.nina.memory.wipe_and_reinitialize()
            self.nina.router.cache.clear()
            self.session_history.clear()
            await self._reply(
                update,
                f"Reset complete. Memory and cache cleared. Backup at: {backup_path}",
                parse_mode=self.PARSE_MODE_DEFAULT,
            )
        except Exception as e:
            await self._reply(update, f"Reset failed: {e} -- untouched.")

    # ---- addkey flow ---------------------------------------------------------

    async def _handle_addkey(self, update: Update, arg: str):
        if arg.strip().lower() == "list":
            await self._reply(update, self.nina.router.get_status())
            return
        parts = arg.split(None, 1)
        if len(parts) != 2:
            await self._reply(
                update, "Usage: addkey PROVIDER key", parse_mode=self.PARSE_MODE_DEFAULT
            )
            return
        provider, key = parts
        result = await self.nina.router.activate_key(provider.upper(), key)
        masked = key[:4] + "..." + key[-2:] if len(key) > 6 else "***"
        try:
            await update.message.delete()
        except Exception:
            pass
        logger.info(
            f"addkey provider={provider.upper()} key set",
            extra={"log": "nina.security"},
        )
        await self._reply(update, f"{result} (key {masked}, message deleted)")

    async def _handle_callback_query(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        callback = update.callback_query
        await callback.answer()
        context = {}
        if len(self.session_history) >= 2:
            user_msgs = [m for m in self.session_history if m.get('role') == 'user']
            asst_msgs = [m for m in self.session_history if m.get('role') == 'assistant']
            if user_msgs:
                context['last_query'] = user_msgs[-1].get('content', '')
            if asst_msgs:
                context['last_response'] = asst_msgs[-1].get('content', '')

        if callback.data == 'feedback_negative' or '👎' in str(callback.data):
            from core.cognition.reflexion import log_negative_trace
            last_query = context.get('last_query', '') if hasattr(context, 'get') else ''
            last_response = context.get('last_response', '') if hasattr(context, 'get') else ''
            log_negative_trace(query=last_query, bad_response=last_response, model_used=context.get('last_model', 'unknown') if hasattr(context, 'get') else 'unknown')

    # ---- Upgrade file handler ------------------------------------------------

    async def _handle_upgrade_file(

        self, update: Update, ctx: ContextTypes.DEFAULT_TYPE
    ):
        try:
            f = await update.message.document.get_file()
            content = await f.download_as_bytearray()
            result = await self.nina.pipeline.handle_command(
                "patch", content.decode(), update.message.document.file_name
            )
            await self._reply(update, result[:4000])
        except Exception as e:
            await self._reply(update, f"Upgrade file error: {e}")

    # ---- Local fast helper ---------------------------------------------------

    async def _local_fast(self, prompt: str) -> str:
        msgs = [{"role": "user", "content": prompt}]
        task = ClassifiedTask("quick", 300, False, False)
        try:
            text, _, _, _ = await self.nina.router._call_provider(
                "LOCALFAST", msgs, task
            )
            return text
        except Exception as e:
            logger.warning(f"local_fast_failed err={e}")
            return ""

    # ---- send_message (bloqueado intencionalmente) --------------------------

    async def send_message(self, text: str):
        # ANULADO PARA EVITAR ERRORES DE CHAT_ID
        logger.info(f"Intento de envío bloqueado (Debug): {text}")
        return

        def esc(t):
            return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", t)

        try:
            await self._app.bot.send_message(
                chat_id=self.config.telegram_chat_id,
                text=esc(text)[:4096],
                parse_mode=self.PARSE_MODE_MARKDOWN_V2,
            )
        except Exception:
            try:
                await self._app.bot.send_message(
                    chat_id=self.config.telegram_chat_id,
                    text=text[:4096],
                    parse_mode=self.PARSE_MODE_DEFAULT,
                )
            except Exception as e:
                logger.warning(f"send_message_failed err={e}")
