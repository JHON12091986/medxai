"""
NINA v12 -- TelegramInterface (Stage 3)
Security gate, command handler, NLP fallback, streaming, flood protection, reset UX.
"""

import asyncio, logging, re, time
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from core.config import NinaConfig
from core.router import HybridRouter, ClassifiedTask, classify_task

logger  = logging.getLogger("nina.telegram")
sec_log = logging.getLogger("nina.security")

COMMANDS = {
    "task", "ask", "email", "shell", "remember", "forget",
    "patch", "generate", "approve", "reject", "rollback",
    "addkey", "status", "router", "logs", "abort", "start", "reset", "help"
}

HELP_TEXT = """*NINA v12 Commands*

`task <goal>` -- Multi-step autonomous task
`ask <question>` -- Quick single-turn question
`email` -- Fetch & analyze both mailboxes
`shell <cmd>` -- Allowlisted system command
`remember <text>` -- Save to permanent memory
`forget <key>` -- Delete a saved fact
`patch <file> <url>` -- Deploy a Python module upgrade
`generate <f> <d>` -- AI-generate a module upgrade
`approve` -- Confirm pending upgrade
`reject` -- Discard pending upgrade
`rollback <file>` -- Restore previous version
`addkey <P> <key>` -- Add a provider API key
`addkey list` -- Show provider status & signup links
`status` -- System health snapshot
`router` -- Provider routing table
`logs` -- Last 50 lines of nina.log
`abort` -- Kill active task immediately
`start` -- Reset session history
`reset` -- Full reinitialization (backs up memory first)

You can also just talk:
check my email, hunt for new providers, show idle queue
diagnose errors, run the morning report now, how much did I spend today
set EWS emails to 25, roll back web.py, what's using the most RAM"""


class TelegramInterface:

    def __init__(self, config: NinaConfig, nina_os):
        self.config          = config
        self.nina            = nina_os
        self.session_history: list[dict] = []
        self._flood_window:   list[float] = []
        self._active_task:    Optional[asyncio.Task] = None
        self._app:            Optional[Application]  = None

    async def start(self):
        self._app = Application.builder().token(self.config.telegram_bot_token).build()
        self._app.add_handler(MessageHandler(filters.ALL, self._handle_update))
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(drop_pending_updates=True)
        logger.info("TelegramInterface polling started")

    async def stop(self):
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    def _mask_secrets(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        for k, v in self.config.dict().items():
            if v and isinstance(v, str) and any(x in k.lower() for x in ['key', 'token', 'secret', 'password']):
                if v in text:
                    masked = v[:4] + "***" + v[-4:] if len(v) > 8 else "***"
                    text = text.replace(v, masked)
        return text

    async def _reply(self, update, text: str, **kwargs):
        text = self._mask_secrets(str(text))
        return await self._reply(update, text, **kwargs)


    # ---- Security gate -------------------------------------------------------

    async def _handle_update(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return
        uid = str(update.message.from_user.id)

        if uid != str(self.config.authorized_user_id):
            sec_log.warning(f"unauthorized_access uid={uid}", extra={"log": "security.log"})
            return

        text = (update.message.text or "").strip()
        if update.message.document and update.message.document.file_name.endswith(".py"):
            size = update.message.document.file_size or 0
            if size > 100_000:
                await self._reply(update, "File too large. Max 100KB.")
                return
            await self._reply(update, "Routing to upgrade pipeline...")
            await update.message.delete()
            asyncio.create_task(self._handle_upgrade_file(update, ctx))
            return

        if not text:
            return

        now = time.time()
        self._flood_window = [t for t in self._flood_window
                              if now - t < self.config.flood_window_s]
        if len(self._flood_window) >= self.config.flood_max_messages:
            queued = len(self._flood_window) - self.config.flood_max_messages + 1
            sec_log.warning(f"authorized_user_flood uid={uid}", extra={"log": "security.log"})
            await self._reply(update, f"Slow down -- {queued} message(s) queued.")
            return
        self._flood_window.append(now)

        if hasattr(self.nina, "idle_loop") and self.nina.idle_loop:
            self.nina.idle_loop.record_user_message()
        asyncio.create_task(self._dispatch(update, text))

    # ---- Dispatcher ----------------------------------------------------------

    async def _dispatch(self, update: Update, text: str):
        parts = text.split(None, 1)
        cmd   = parts[0].lstrip("/").lower()
        arg   = parts[1] if len(parts) > 1 else ""

        if cmd in COMMANDS:
            await self._handle_command(update, cmd, arg)
        else:
            await self._handle_nlp(update, text)

    async def _handle_command(self, update: Update, cmd: str, arg: str):
        router: HybridRouter = self.nina.router

        if cmd == "help":
            await self._reply(update, HELP_TEXT, parse_mode=None)

        elif cmd == "status":
            reply = await self.nina.get_status()
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
            await self._stream_reply(update, arg, ClassifiedTask("quick", 300, False, False))

        elif cmd == "task":
            task = await classify_task(arg, self._local_fast)
            await self._stream_reply(update, arg, task, use_agent=True)

        elif cmd == "email":
            await self._stream_reply(update, "fetch and analyze both mailboxes",
                                     ClassifiedTask("general", 500, False, False))

        elif cmd == "shell":
            result = await self.nina.tools["shell"].run(arg)
            await self._reply(update, result[:4000])

        elif cmd == "remember":
            await self.nina.memory.remember(arg)
            await self._reply(update, f"Remembered: {arg}")

        elif cmd == "forget":
            await self.nina.memory.forget(arg)
            await self._reply(update, f"Forgot: {arg}")

        elif cmd == "addkey":
            await self._handle_addkey(update, arg)

        elif cmd in ("approve", "reject", "patch", "generate", "rollback"):
            result = await self.nina.pipeline.handle_command(cmd, arg)
            await self._reply(update, result[:4000])

        else:
            await self._reply(update, "Unknown command. /help for the list.")

    # ---- NLP fallback --------------------------------------------------------

    async def _handle_nlp(self, update: Update, text: str):
        NLP_INTENTS = {
            "email":           ["check my email", "fetch email", "my emails"],
            "provider_hunt":   ["hunt for new providers", "find providers", "missing providers"],
            "provider_status": ["provider status", "addkey list", "show providers"],
            "config_update":   ["set ews", "config update", "change setting"],
            "rollback_request":["roll back", "rollback"],
            "upgrade_history": ["upgrade history", "upgrade log"],
            "cost_report":     ["how much did i spend", "cost report", "daily cost"],
            "diagnose":        ["diagnose errors", "auto-diagnose"],
            "run_schedule":    ["run the morning report", "run scheduled job", "morning report"],
            "gpu_config":      ["gpu config", "optimize gpu layers"],
            "clear_session":   ["clear my session", "clear session"],
            "show_idle_queue": ["show idle queue", "idle proposals"],
            "ram_status":      ["what's using the most ram", "ram usage"],
        }

        intent_map = {
            "email":           ("email",  ""),
            "provider_hunt":   ("shell",  "python -m tools.providerhunter"),
            "provider_status": ("router", ""),
            "cost_report":     ("status", ""),
            "diagnose":        ("logs",   ""),
            "run_schedule":    ("task",   "run morning report"),
            "clear_session":   ("start",  ""),
            "show_idle_queue": ("task",   "show idle queue"),
            "ram_status":      ("status", ""),
            "gpu_config":      ("task",   ""),
            "config_update":   ("task",   text),
            "rollback_request":("task",   text),
            "upgrade_history": ("task",   "show upgrade history"),
        }

        lower  = text.lower()
        intent = "general_task"
        for key, phrases in NLP_INTENTS.items():
            if any(p in lower for p in phrases):
                intent = key
                break

        if intent == "general_task":
            from tools.search import search
            search_keywords = ["search", "rate", "price", "news", "today", "current",
                               "latest", "fetch", "find", "what is", "how much"]
            if any(k in text.lower() for k in search_keywords):
                result = await search(text)
                await self._reply(update, result[:4000])
                return
            task = await classify_task(text, self._local_fast)
            await self._stream_reply(update, text, task, use_agent=True)
            return

        cmd, arg = intent_map.get(intent, ("task", text))
        await self._handle_command(update, cmd, arg)

    # ---- Streaming reply -----------------------------------------------------

    async def _stream_reply(self, update: Update, prompt: str,
                            task: ClassifiedTask, use_agent: bool = False):

        while len(self.session_history) > self.config.session_max_turns * 2:
            self.session_history.pop(0)
        self.session_history.append({"role": "user", "content": prompt})

        msgs = [{"role": "system", "content": self.nina.system_prompt}] + self.session_history
        sent = await self._reply(update, "...")

        try:
            if use_agent:
                coro = self.nina.agent.run(prompt, task, self.session_history)
            else:
                coro = self.nina.router.route(
                    prompt, msgs, task,
                    force_local=getattr(self.nina, "_force_local_fast", False))

            self._active_task = asyncio.create_task(coro)
            result = await self._active_task

            final = result[:4096]
            if final != "...":
                try:
                    await sent.edit_text(final)
                except Exception:
                    pass
            if len(result) > 4096:
                for chunk in [result[i:i+4096] for i in range(4096, len(result), 4096)]:
                    await self._reply(update, chunk)

            self.session_history.append({"role": "assistant", "content": result})

        except asyncio.CancelledError:
            await sent.edit_text("Task aborted.")
        except Exception as e:
            logger.exception("stream_reply_error")
            await sent.edit_text(
                f"Error {type(e).__name__}: {str(e)[:200]}\n"
                "Try /ask for a simpler route, or /status to check providers.",
                parse_mode=None)

    # ---- Reset UX ------------------------------------------------------------

    async def _handle_reset(self, update: Update):
        await self._reply(update, 
            "Reset will wipe all session memory. Creating backup first...")
        try:
            backup_path = await self.nina.memory.backup()
            await self.nina.memory.wipe_and_reinitialize()
            self.nina.router.cache.clear()
            self.session_history.clear()
            await self._reply(update, 
                f"Reset complete. Memory and cache cleared. Backup at: {backup_path}",
                parse_mode=None)
        except Exception as e:
            await self._reply(update, f"Reset failed: {e} -- untouched.")

    # ---- addkey flow ---------------------------------------------------------

    async def _handle_addkey(self, update: Update, arg: str):
        if arg.strip().lower() == "list":
            await self._reply(update, self.nina.router.get_status())
            return
        parts = arg.split(None, 1)
        if len(parts) != 2:
            await self._reply(update, "Usage: addkey PROVIDER key", parse_mode=None)
            return
        provider, key = parts
        result = await self.nina.router.activate_key(provider.upper(), key)
        masked = key[:4] + "..." + key[-2:] if len(key) > 6 else "***"
        try:
            await update.message.delete()
        except Exception:
            pass
        logger.info(f"addkey provider={provider.upper()} key set",
                    extra={"log": "nina.security"})
        await self._reply(update, f"{result} (key {masked}, message deleted)")

    # ---- Upgrade file handler ------------------------------------------------

    async def _handle_upgrade_file(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
            f       = await update.message.document.get_file()
            content = await f.download_as_bytearray()
            result  = await self.nina.pipeline.handle_command(
                "patch", content.decode(), update.message.document.file_name)
            await self._reply(update, result[:4000])
        except Exception as e:
            await self._reply(update, f"Upgrade file error: {e}")

    # ---- Local fast helper ---------------------------------------------------

    async def _local_fast(self, prompt: str) -> str:
        msgs = [{"role": "user", "content": prompt}]
        task = ClassifiedTask("quick", 300, False, False)
        try:
            text, _, _, _ = await self.nina.router._call_provider("LOCALFAST", msgs, task)
            return text
        except Exception as e:
            logger.warning(f"local_fast_failed err={e}")
            return ""

    # ---- send_message --------------------------------------------------------

    async def send_message(self, text: str):
        text = self._mask_secrets(text)
        def esc(t):
            return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', t)
        try:
            await self._app.bot.send_message(
                chat_id=self.config.authorized_user_id,
                text=esc(text)[:4096],
                parse_mode="MarkdownV2")
        except Exception:
            try:
                await self._app.bot.send_message(
                    chat_id=self.config.authorized_user_id,
                    text=text[:4096])
            except Exception as e:
                logger.warning(f"send_message_failed err={e}")
