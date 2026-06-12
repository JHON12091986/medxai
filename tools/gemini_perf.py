import os
import json
import logging
import fnmatch
from functools import lru_cache
from datetime import datetime

# Setup simple logger for our classes
logger = logging.getLogger("gemini_perf")
logger.setLevel(logging.INFO)
# Don't add handler if one exists to prevent duplicate logs in case of reload
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)

class ContextPruner:
    ALWAYS_EXCLUDE = [
        "__pycache__/", "*.pyc", "*.pyo",
        ".git/", ".github/",
        "*.egg-info/", "dist/", "build/", ".tox/",
        "venv/", ".venv/", "env/",
        "*.log",
        "data/session_ledger.json", "data/session_ledger.tmp",
        "data/gemini_preamble.md",
        "juleslock.txt",
        "docs/space/",
        "nina_master_backup*.md",
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg",
        "*.db", "*.sqlite", "*.sqlite3",
        "node_modules/",
        ".env",
        "upgrades/"
    ]

    def write_ignore_file(self) -> str:
        home_nina = os.path.expanduser("~/nina")
        extra_ignore_path = os.path.join(home_nina, ".geminiperfignore_extra")
        ignore_path = os.path.join(home_nina, ".geminiignore")
        tmp_path = ignore_path + ".tmp"

        patterns = self.ALWAYS_EXCLUDE.copy()

        try:
            if os.path.exists(extra_ignore_path):
                with open(extra_ignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
        except Exception:
            pass # Silently handle if we can't read extra

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write("\n".join(patterns) + "\n")
            os.replace(tmp_path, ignore_path)
        except Exception:
            pass

        return ignore_path

    def estimate_context_tokens(self, paths: list[str]) -> int:
        total_tokens = 0
        home_nina = os.path.expanduser("~/nina")
        for p in paths:
            full_path = os.path.join(home_nina, p)
            try:
                if os.path.isfile(full_path):
                    with open(full_path, "rb") as f:
                        data = f.read(8000)
                        # approximate tokens = chars / 4
                        total_tokens += len(data.decode('utf-8', errors='ignore')) // 4
            except Exception:
                pass
        return total_tokens

    def get_included_files(self, base_dir: str = '~/nina') -> list[str]:
        expanded_base = os.path.expanduser(base_dir)
        ignore_path = os.path.join(expanded_base, ".geminiignore")
        patterns = []
        try:
            with open(ignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception:
            patterns = self.ALWAYS_EXCLUDE.copy()

        included_files = []
        for root, dirs, files in os.walk(expanded_base):
            rel_root = os.path.relpath(root, expanded_base)
            if rel_root == ".":
                rel_root = ""

            # Prune dirs
            dirs_to_remove = []
            for d in dirs:
                rel_d = os.path.join(rel_root, d) + "/"
                if any(fnmatch.fnmatch(rel_d, p) or fnmatch.fnmatch(d + "/", p) or fnmatch.fnmatch(d, p) for p in patterns):
                    dirs_to_remove.append(d)
            for d in dirs_to_remove:
                dirs.remove(d)

            # Filter files
            for file in files:
                rel_f = os.path.join(rel_root, file) if rel_root else file
                excluded = False
                for p in patterns:
                    if fnmatch.fnmatch(rel_f, p) or fnmatch.fnmatch(file, p):
                        excluded = True
                        break
                if not excluded:
                    included_files.append(rel_f)

        return sorted(included_files)


class PrefixCacheWarmer:
    @lru_cache(maxsize=1)
    def get_stable_prefix(self) -> str:
        agents_path = os.path.expanduser("~/nina/AGENTS.md")
        try:
            with open(agents_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Strip trailing whitespace from every line
            return "\n".join(line.rstrip() for line in lines)
        except Exception:
            return ""

    def build_prompt(self, user_task: str, extra_context: str = '') -> str:
        prefix = self.get_stable_prefix()
        budget = int(os.environ.get("NINA_GEMINI_TOKEN_BUDGET", "8000"))

        # Estimate prefix and task tokens (rough)
        prefix_tokens = len(prefix) // 4
        task_tokens = len(user_task) // 4
        extra_tokens = len(extra_context) // 4

        total = prefix_tokens + task_tokens + extra_tokens

        if total > budget and extra_context:
            logger.warning(f"Estimated tokens ({total}) > NINA_GEMINI_TOKEN_BUDGET ({budget}). Truncating extra_context.")
            allowed_extra_tokens = max(0, budget - prefix_tokens - task_tokens)
            allowed_chars = allowed_extra_tokens * 4
            if allowed_chars > 0:
                half = allowed_chars // 2
                extra_context = extra_context[:half] + "\n\n...[TRUNCATED]...\n\n" + extra_context[-half:]
            else:
                extra_context = ""

        return prefix + '\n\n---\n\n' + extra_context + '\n\n' + user_task

    def write_prompt_file(self, user_task: str, extra_context: str = '') -> str:
        prompt = self.build_prompt(user_task, extra_context)
        prompt_path = os.path.expanduser("~/nina/data/gemini_prompt.md")
        try:
            os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(prompt)
        except Exception:
            pass
        return prompt_path


class ModelTierSelector:
    def select(self, task: str, context_tokens: int, target_files: list[str]) -> str:
        task_lower = task.lower()
        flash_triggers = ['fix typo', 'rename', 'add comment', 'docstring', 'format', 'lint', 'add type hint', 'add import', 'print', 'log statement']
        pro_triggers = ['refactor', 'architecture', 'mega', 'multi-file', 'migrate', 'security', 'audit', 'design', 'rewrite']

        # Flash triggers
        if context_tokens <= 4000:
            logger.debug("Selected gemini-2.5-flash (context <= 4000)")
            return 'gemini-2.5-flash'

        if any(trigger in task_lower for trigger in flash_triggers):
            logger.debug("Selected gemini-2.5-flash (keyword match)")
            return 'gemini-2.5-flash'

        if len(target_files) == 1:
            try:
                with open(os.path.expanduser(f"~/nina/{target_files[0]}"), "r", encoding="utf-8") as f:
                    if sum(1 for _ in f) < 200:
                        logger.debug("Selected gemini-2.5-flash (1 file < 200 lines)")
                        return 'gemini-2.5-flash'
            except Exception:
                pass

        # Pro triggers
        if context_tokens > 12000:
            logger.debug("Selected gemini-2.5-pro (context > 12000)")
            return 'gemini-2.5-pro'

        if any(trigger in task_lower for trigger in pro_triggers):
            logger.debug("Selected gemini-2.5-pro (keyword match)")
            return 'gemini-2.5-pro'

        if len(target_files) > 4:
            logger.debug("Selected gemini-2.5-pro (> 4 files)")
            return 'gemini-2.5-pro'

        logger.debug("Selected gemini-2.5-flash (default fallback)")
        return 'gemini-2.5-flash'

    def get_cli_flag(self, task: str, context_tokens: int, target_files: list[str]) -> str:
        model = self.select(task, context_tokens, target_files)
        return f"--model {model}"


class PromptBudgetGuard:
    def __init__(self):
        self.state_file = os.path.expanduser("~/nina/data/gemini_usage.json")
        self.daily_limit = int(os.environ.get("NINA_GEMINI_DAILY_REQ_LIMIT", "1000"))
        self.token_budget = int(os.environ.get("NINA_GEMINI_TOKEN_BUDGET", "8000"))
        self.warn_at = int(os.environ.get("NINA_GEMINI_WARN_AT", "800"))

    def _load_state(self) -> dict:
        today = datetime.now().strftime("%Y-%m-%d")
        default_state = {'date': today, 'requests': 0, 'estimated_tokens': 0}

        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                if state.get('date') != today:
                    return default_state
                return state
        except Exception:
            pass
        return default_state

    def _save_state(self, state: dict) -> None:
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            tmp_path = self.state_file + ".tmp"
            with open(tmp_path, "w") as f:
                json.dump(state, f)
            os.replace(tmp_path, self.state_file)
        except Exception:
            pass

    def record_request(self, estimated_tokens: int) -> None:
        try:
            state = self._load_state()
            state['requests'] += 1
            state['estimated_tokens'] += estimated_tokens
            self._save_state(state)

            if state['requests'] >= self.daily_limit:
                logger.error("Gemini quota exhausted — switch to Qwen Code CLI")
            elif state['requests'] >= self.warn_at:
                logger.warning(f"Gemini quota: {state['requests']} of {self.daily_limit} daily requests used")
        except Exception:
            pass

    def check_invocation(self, estimated_tokens: int) -> dict:
        state = self._load_state()

        ok = True
        reason = ""

        if state['requests'] >= self.daily_limit:
            ok = False
            reason = "Daily request limit reached"
        elif estimated_tokens > self.token_budget * 1.5:
            ok = False
            reason = "Estimated tokens significantly exceed per-invocation budget"

        return {
            'ok': ok,
            'reason': reason,
            'daily_used': state['requests'],
            'daily_limit': self.daily_limit,
            'token_estimate': estimated_tokens
        }

    def get_status(self) -> dict:
        state = self._load_state()
        state['daily_limit'] = self.daily_limit
        state['token_budget'] = self.token_budget
        return state
