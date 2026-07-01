"""NINA v12 — IdleProposalLoop (Stage 6.4)
Proposal-only mode: Nina analyses, logs a markdown brief, pings Telegram.
No code generation. No pipeline. Human reviews via Perplexity, injects patch manually.
"""
import asyncio, json, logging, time
from pathlib import Path
from datetime import datetime

logger     = logging.getLogger("nina.idle")
PROPOSALS_DIR = Path("data/proposals")

ANALYSIS_PROMPTS = [
    ("tool_error_handling",
     "Analyse NINA's tool error handling (tools/*.py). Identify the single weakest point. "
     "Describe: 1) exact file + function, 2) what can go wrong, 3) suggested fix in plain English. "
     "No code. Be specific and concise."),
    ("morning_report",
     "Analyse NINA's morning report (core/nina.py → run_morning_report). Identify one concrete improvement. "
     "Describe: 1) what is missing or fragile, 2) why it matters, 3) suggested fix in plain English. No code."),
    ("provider_routing",
     "Analyse NINA's HybridRouter fallback logic (core/router.py). Identify one failure mode. "
     "Describe: 1) exact scenario where routing silently fails, 2) impact, 3) suggested fix in plain English. No code."),
    ("memory_context",
     "Analyse NINA's memory context building (core/memory.py → build_context). Identify one weakness. "
     "Describe: 1) what context is missed or stale, 2) impact on response quality, 3) suggested fix in plain English. No code."),
    ("scheduler_errors",
     "Analyse NINA's scheduler job error handling (crons/manager.py). Identify one gap. "
     "Describe: 1) which job type can fail silently, 2) what the consequence is, 3) suggested fix in plain English. No code."),
    ("telegram_interface",
     "Analyse NINA's Telegram interface (interfaces/telegram_interface.py). Identify one UX or reliability issue. "
     "Describe: 1) exact command or flow, 2) what breaks or feels rough, 3) suggested fix in plain English. No code."),
    ("config_robustness",
     "Analyse NINA's config loading (core/config.py + core/hotreload.py). Identify one fragility. "
     "Describe: 1) what env var or edge case is unhandled, 2) impact, 3) suggested fix in plain English. No code."),
]

class IdleProposalLoop:
    def __init__(self, config, router, telegram, pipeline=None):
        self.config        = config
        self.router        = router
        self.telegram      = telegram
        # pipeline retained in signature for compat but never used
        self._last_user_ts: float = time.time()
        self._task: asyncio.Task | None = None
        _idx_file = Path("data/proposal_index.txt")
        try:
            self._prompt_index = int(_idx_file.read_text().strip())
        except Exception:
            self._prompt_index = 0
        PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        self._task = asyncio.create_task(self._loop())
        logger.info("IdleProposalLoop initialized (proposal-only mode)")

    def record_user_message(self):
        self._last_user_ts = time.time()

    def _is_idle(self) -> bool:
        return (time.time() - self._last_user_ts) / 60 >= self.config.idle_threshold_min

    async def _loop(self):
        while True:
            try:
                await asyncio.sleep(60)
                if not self._is_idle():
                    continue
                import psutil
                ram_gb = psutil.virtual_memory().used / (1024 ** 3)
                if ram_gb >= self.config.ram_guard_gb:
                    logger.warning(f"idle_loop_skipped RAM={ram_gb:.1f}GB")
                    continue
                logger.info("idle_loop_tick generating proposal brief")
                await self._generate_proposal()
                await asyncio.sleep(self.config.idle_report_min * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"idle_loop_error {e}")
                await asyncio.sleep(300)

    async def _generate_proposal(self):
        topic, prompt = ANALYSIS_PROMPTS[self._prompt_index % len(ANALYSIS_PROMPTS)]
        self._prompt_index += 1
        try:
            Path("data/proposal_index.txt").write_text(str(self._prompt_index))
        except Exception:
            pass
        try:
            from core.router import ClassifiedTask
            from pathlib import Path
            # Ground the LLM with actual file list to prevent hallucination
            real_files = sorted(str(p.relative_to(Path("."))) for p in Path(".").rglob("*.py")
                if not any(x in str(p) for x in ["venv", ".venv", "__pycache__", "archive"]))
            file_list = "\n".join(real_files[:40])
            grounded_prompt = f"{prompt}\n\nIMPORTANT: NINA's actual Python files are:\n{file_list}\nOnly reference files from this list."
            task = ClassifiedTask("research", 400, False, False)
            msgs = [{"role": "user", "content": grounded_prompt}]
            analysis = await self.router.route(grounded_prompt, msgs, task)

            # Append to single rolling daily file
            today = datetime.now().strftime("%Y-%m-%d")
            out   = PROPOSALS_DIR / f"{today}_proposals.md"
            ts    = datetime.now().strftime("%H:%M:%S")
            entry = f"""
---

## [{ts}] {topic.replace('_', ' ').title()}

{analysis.strip()}

**Status:** pending
"""
            with open(out, "a") as f:
                if out.stat().st_size == 0 if out.exists() else True:
                    f.write(f"# NINA Daily Proposals — {today}\n")
                f.write(entry)
            logger.info(f"idle_proposal_appended topic={topic} file={out.name}")

        except Exception as e:
            logger.warning(f"idle_proposal_failed {e}")

    async def show_idle_queue(self) -> str:
        files = sorted(PROPOSALS_DIR.glob("*.md"), reverse=True)[:10]
        if not files:
            return "No proposals yet."
        lines = [f"📋 Last {len(files)} proposals:"]
        for f in files:
            lines.append(f"• `{f.name}`")
        return "\n".join(lines)

# Alias so core/nina.py import stays unchanged
IdleUpgradeLoop = IdleProposalLoop
