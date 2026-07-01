"""
NINA — Pipeline Autopilot (AGY Autonomous Mode v1.1)
Zero-human-intervention Jules/Git pipeline maintenance daemon.

Phases:
  0 — Safety check (GLOBAL PAUSE flag)
  1 — PR triage and merge
  1.5 — Post-merge documentation update
  2 — Jules session health check & response
  3 — Backlog status sync
  4 — Poll loop for new PRs from in-flight sessions
  5 — Duplicate session cleanup
  6 — Final pipeline report + Telegram notification

Designed to run every 5 minutes via APScheduler (crons/manager.py).
File-lock enforced — only one instance runs at a time.
"""

from __future__ import annotations

import ast
import asyncio
import fcntl
import json
import logging
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from core.constants import (ENV_TELEGRAM_BOT_TOKEN, ENV_TELEGRAM_CHAT_ID, ENV_API_SECRET_KEY, ENV_OPENAI_API_KEY, ENV_CEREBRAS_API_KEY, ENV_GROQ_API_KEY, ENV_GEMINI_API_KEY, ENV_MISTRAL_API_KEY, ENV_OPENROUTER_API_KEY, ENV_DEEPSEEK_API_KEY, ENV_PERPLEXITY_API_KEY, ENV_TOGETHER_API_KEY, ENV_COHERE_API_KEY, ENV_FIREWORKS_API_KEY, ENV_XAI_API_KEY, ENV_SAMBANOVA_API_KEY, ENV_HYPERBOLIC_API_KEY, ENV_NOVITA_API_KEY, ENV_OLLAMA_HOST, ENV_EWS_USERNAME, ENV_EWS_MY_EMAIL, ENV_EWS_SHARED_EMAIL)

from core.constants import (
    ENV_TELEGRAM_BOT_TOKEN,
    ENV_TELEGRAM_CHAT_ID,
    ENV_AUTHORIZED_USER_ID,
    ENV_JULES_API_KEY,
)

# Lazy import to avoid circular load — jules imports happen at call-site
_jules = None

def _get_jules():
    global _jules
    if _jules is None:
        from tools import jules as _j
        _jules = _j
    return _jules

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT     = Path(__file__).parent.parent.resolve()
BACKLOG_PATH  = REPO_ROOT / "docs" / "space" / "jules_backlog.md"
REGISTRY_PATH = REPO_ROOT / "data" / "jules_registry.json"
AGENTS_PATH   = REPO_ROOT / "AGENTS.md"
LOCK_PATH     = REPO_ROOT / "data" / "pipeline.lock"
LOG_PATH      = REPO_ROOT / "logs" / "pipeline_autopilot.log"

JULES_BASE_URL = "https://jules.googleapis.com/v1alpha"

# High-risk files — never attempt auto-resolve; close PR instead
HIGH_RISK = {
    "core/nina.py", "core/router.py", "core/agent.py",
    "guardian_engine.py", "interfaces/telegram_interface.py", "core/config.py",
}

logger = logging.getLogger("nina.pipeline_autopilot")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(cmd: list[str], *, cwd: Path | None = None, check: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess and return the CompletedProcess."""
    cwd = cwd or REPO_ROOT
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), check=check)


def _git(*args: str) -> subprocess.CompletedProcess:
    return _run(["git", *args])


def _gh(*args: str) -> subprocess.CompletedProcess:
    return _run(["gh", *args])


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except Exception:
        backup = REGISTRY_PATH.with_suffix(f".bak.{int(time.time())}.json")
        REGISTRY_PATH.rename(backup)
        logger.error(f"Registry malformed — backed up to {backup}, reinitialised as empty")
        return {}


def _save_registry(data: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2))


def _send_telegram(message: str) -> None:
    import os
    token = os.environ.get(ENV_TELEGRAM_BOT_TOKEN)
    chat_id = os.environ.get(ENV_TELEGRAM_CHAT_ID) or os.environ.get(ENV_AUTHORIZED_USER_ID)
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
    except Exception as exc:
        logger.warning(f"Telegram send failed: {exc}")


def _jules_api(method: str, path: str, **kwargs) -> dict:
    import os
    key = os.environ.get(ENV_JULES_API_KEY, "")
    if not key:
        raise RuntimeError("JULES_API_KEY not set")
    headers = {"X-Goog-Api-Key": key, "Content-Type": "application/json"}
    url = f"{JULES_BASE_URL}/{path.lstrip('/')}"
    resp = requests.request(method, url, headers=headers, timeout=30, **kwargs)
    if resp.status_code == 404:
        return {"error": "not_found"}
    resp.raise_for_status()
    return resp.json() if method.upper() != "DELETE" else {"status": "ok"}


# ── Phase 0 — Safety check ─────────────────────────────────────────────────────

def phase0_safety() -> dict:
    global_pause = False
    if BACKLOG_PATH.exists():
        text = BACKLOG_PATH.read_text()
        if "GLOBAL PAUSE ACTIVE" in text:
            global_pause = True
            logger.info("GLOBAL PAUSE active — dispatch suppressed, all other phases running")
    return {"global_pause": global_pause}


# ── Phase 1 — PR triage and merge ─────────────────────────────────────────────

_PRIORITY_KEYWORDS = {
    "security": 0, "sec-": 0, "fix(": 0, "fix:": 0,
}


def _pr_priority(pr: dict) -> int:
    title = (pr.get("title") or "").lower()
    branch = (pr.get("headRefName") or "").lower()
    for kw, prio in _PRIORITY_KEYWORDS.items():
        if kw in title or kw in branch:
            return prio
    if "ag-m-" in title or "ag-m-" in branch:
        return 5  # MEGA tasks — last
    if any(p in branch for p in ("tools/", "ninaflash", "data/")):
        return 2
    if any(p in branch for p in ("core/memory", "core/task_store", "crons/")):
        return 3
    if any(p in branch for p in ("core/", "guardian", "interfaces/")):
        return 4
    return 2  # default: low-risk


def _detect_duplicates(prs: list[dict]) -> dict[str, list[dict]]:
    """Group PRs by AG-*/task ID extracted from branch or title."""
    groups: dict[str, list[dict]] = {}
    for pr in prs:
        key_match = re.search(r"(AG-[A-Z]-\d+|\d{15,})", pr.get("headRefName", "") + pr.get("title", ""))
        key = key_match.group(1) if key_match else None
        if key:
            groups.setdefault(key, []).append(pr)
    return {k: v for k, v in groups.items() if len(v) > 1}


def _pr_changed_files(branch: str) -> list[str]:
    res = _git("diff", "--name-only", f"origin/main...origin/{branch}")
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def _try_rebase_and_merge(pr: dict) -> tuple[bool, str]:
    """Attempt rebase of a conflicting branch onto main. Return (success, reason)."""
    branch = pr["headRefName"]
    pr["number"]

    # Check for high-risk file conflicts
    changed = _pr_changed_files(branch)
    high_risk_hits = [f for f in changed if f in HIGH_RISK]
    if high_risk_hits:
        return False, f"High-risk conflict: {high_risk_hits}"

    # Checkout and rebase
    res_fetch = _git("fetch", "origin", branch)
    if res_fetch.returncode != 0:
        return False, f"fetch failed: {res_fetch.stderr[:200]}"

    _git("checkout", "-B", branch, f"origin/{branch}")
    res_rebase = _git("rebase", "origin/main")
    if res_rebase.returncode != 0:
        _git("rebase", "--abort")
        return False, f"rebase conflict: {res_rebase.stderr[:200]}"

    # Validate changed .py files compile
    for f in changed:
        if f.endswith(".py") and (REPO_ROOT / f).exists():
            r = _run(["python3", "-m", "py_compile", f])
            if r.returncode != 0:
                _git("rebase", "--abort")
                return False, f"compile error in {f}: {r.stderr[:200]}"

    res_push = _git("push", "origin", branch, "--force-with-lease")
    if res_push.returncode != 0:
        return False, f"force-push failed: {res_push.stderr[:200]}"

    return True, "rebased"


def _merge_pr(num: int) -> bool:
    res = _gh("pr", "merge", str(num), "--squash", "--delete-branch", "--yes")
    if res.returncode == 0:
        return True
    # Fallback: plain merge
    res2 = _gh("pr", "merge", str(num), "--merge", "--delete-branch", "--yes")
    return res2.returncode == 0


def phase1_pr_triage() -> dict:
    result = {
        "merged": [], "closed_duplicate": [], "closed_stale": [],
        "closed_high_risk": [], "failed": [], "remaining": 0,
    }

    res = _gh("pr", "list", "--json",
              "number,title,headRefName,mergeable,state,createdAt",
              "--limit", "50")
    if res.returncode != 0:
        logger.error(f"gh pr list failed: {res.stderr}")
        return result

    prs: list[dict] = json.loads(res.stdout or "[]")
    if not prs:
        logger.info("Phase 1: No open PRs.")
        return result

    # 1. Close duplicates first (keep newest)
    dups = _detect_duplicates(prs)
    for task_id, dup_prs in dups.items():
        dup_prs.sort(key=lambda p: p.get("createdAt", ""), reverse=True)
        for old_pr in dup_prs[1:]:
            _gh("pr", "close", str(old_pr["number"]),
                "--comment", f"Closing duplicate — superseded by PR #{dup_prs[0]['number']} for task {task_id}.")
            result["closed_duplicate"].append(old_pr["number"])
            logger.info(f"Closed duplicate PR #{old_pr['number']}")

    # Refresh after closing duplicates
    res = _gh("pr", "list", "--json",
              "number,title,headRefName,mergeable,state,createdAt",
              "--limit", "50")
    prs = json.loads(res.stdout or "[]")

    # 2. Check staleness (>72h, task already DONE elsewhere)
    now = datetime.now(timezone.utc)
    for pr in list(prs):
        created = pr.get("createdAt", "")
        try:
            age = now - datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            age = timedelta(0)
        if age > timedelta(hours=72) and pr["mergeable"] == "CONFLICTING":
            branch = pr.get("headRefName", "")
            git_log = _git("log", "--oneline", "-100").stdout
            if any(word in git_log for word in re.findall(r"\d{10,}", branch)):
                _gh("pr", "close", str(pr["number"]),
                    "--comment", "Closing stale PR — task appears already merged in main.")
                result["closed_stale"].append(pr["number"])
                prs.remove(pr)
                logger.info(f"Closed stale PR #{pr['number']}")

    # 3. Sort remaining by priority and merge
    prs.sort(key=_pr_priority)

    for pr in prs:
        num = pr["number"]
        mergeable = pr.get("mergeable", "UNKNOWN")

        if mergeable == "MERGEABLE":
            success = _merge_pr(num)
            if success:
                result["merged"].append(num)
                logger.info(f"Merged PR #{num}: {pr['title']}")
            else:
                result["failed"].append(num)
                logger.warning(f"Merge failed for PR #{num}")

        elif mergeable == "CONFLICTING":
            success, reason = _try_rebase_and_merge(pr)
            if success:
                success2 = _merge_pr(num)
                if success2:
                    result["merged"].append(num)
                    logger.info(f"Rebased+merged PR #{num}")
                else:
                    result["failed"].append(num)
            else:
                if "High-risk" in reason:
                    _gh("pr", "close", str(num),
                        "--comment", f"Rebase conflict in high-risk file — task marked NEEDS_REVIEW. {reason}")
                    result["closed_high_risk"].append(num)
                    logger.warning(f"Closed high-risk PR #{num}: {reason}")
                else:
                    result["failed"].append(num)
                    logger.warning(f"Rebase failed for PR #{num}: {reason}")

        else:  # UNKNOWN — skip, will retry next cycle
            logger.info(f"PR #{num} mergeable=UNKNOWN — will retry next cycle")

    # 4. Push local main if ahead
    ahead = int(_git("rev-list", "origin/main..HEAD", "--count").stdout.strip() or 0)
    if ahead > 0:
        push_res = _git("push", "origin", "main")
        if push_res.returncode != 0:
            logger.warning(f"Push blocked: {push_res.stderr[:200]}")

    # 5. Count remaining
    final_res = _gh("pr", "list", "--json", "number")
    result["remaining"] = len(json.loads(final_res.stdout or "[]"))
    logger.info(f"Phase 1 complete: merged={result['merged']} remaining={result['remaining']}")
    return result


# ── Phase 1.5 — Post-merge documentation update ────────────────────────────────

def _extract_module_public_api(filepath: Path) -> dict:
    try:
        source = filepath.read_text()
        tree = ast.parse(source)
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        funcs = [n.name for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
        doc = ast.get_docstring(tree) or ""
        return {"classes": classes, "functions": funcs[:10],
                "description": doc.split("\n")[0] if doc else "No docstring"}
    except Exception:
        return {"classes": [], "functions": [], "description": "Parse error"}


def _upsert_agents_section(header: str, body: str) -> None:
    """Append or replace a named section at end of AGENTS.md."""
    if not AGENTS_PATH.exists():
        logger.warning("AGENTS.md not found — skipping doc update")
        return
    content = AGENTS_PATH.read_text()
    marker_start = f"<!-- AUTO:{header} START -->"
    marker_end = f"<!-- AUTO:{header} END -->"
    block = f"{marker_start}\n{body}\n{marker_end}"
    if marker_start in content:
        content = re.sub(
            rf"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
            block, content, flags=re.DOTALL)
    else:
        content = content.rstrip() + f"\n\n{block}\n"
    AGENTS_PATH.write_text(content)


def phase1_5_doc_update(merged_count: int, merged_prs: list[int]) -> None:
    if merged_count == 0:
        return
    if not AGENTS_PATH.exists():
        return

    changed: list[str] = []
    try:
        log_res = _git("log", "--name-only", "--pretty=format:",
                       f"origin/main~{merged_count}..origin/main")
        changed = sorted(set(line.strip() for line in log_res.stdout.splitlines() if line.strip()))
    except Exception as exc:
        logger.warning(f"Could not list changed files: {exc}")
        return

    if all(re.match(r"(data/|logs/|.*\.jsonl|.*\.lock)", f) for f in changed):
        return

    doc_lines: list[str] = []

    for path in changed:
        full = REPO_ROOT / path

        if path.startswith("tools/") and path.endswith(".py") and full.exists():
            info = _extract_module_public_api(full)
            doc_lines.append(
                f"### `{path}`\n"
                f"- **Description**: {info['description']}\n"
                f"- **Public API**: {', '.join(info['functions'][:6]) or 'none'}\n"
                f"- **Last updated**: {datetime.now().strftime('%Y-%m-%d')}"
            )

        elif path.startswith("core/") and path.endswith(".py") and full.exists():
            info = _extract_module_public_api(full)
            try:
                src = full.read_text()
                tree = ast.parse(src)
                existing_doc = ast.get_docstring(tree) or ""
                if not existing_doc or "Auto-generated summary" in existing_doc:
                    new_doc = (
                        f'"""NINA — {path}\n'
                        f'Auto-generated summary | Last updated: {datetime.now().strftime("%Y-%m-%d")}\n\n'
                        f'Classes  : {", ".join(info["classes"]) or "none"}\n'
                        f'Functions: {", ".join(info["functions"][:8]) or "none"}\n'
                        f'"""\n'
                    )
                    if existing_doc:
                        src = src.replace(f'"""{existing_doc}"""', new_doc.strip(), 1)
                        src = src.replace(f"'''{existing_doc}'''", new_doc.strip(), 1)
                    else:
                        src = new_doc + src
                    full.write_text(src)
                    _git("add", path)
            except Exception as exc:
                logger.warning(f"Docstring update failed for {path}: {exc}")

        elif "crons/manager.py" in path and full.exists():
            try:
                src = full.read_text()
                jobs = re.findall(r'id=["\']([^"\']+)["\']', src)
                rows = "\n".join(f"| `{j}` | managed by APScheduler |" for j in jobs)
                table = f"| Job ID | Schedule |\n|--------|----------|\n{rows}"
                _upsert_agents_section("CRON_JOBS", table)
            except Exception as exc:
                logger.warning(f"Cron registry update failed: {exc}")

    if doc_lines:
        summary = f"## Auto-updated tool summaries — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        summary += "\n\n".join(doc_lines)
        _upsert_agents_section("TOOL_SUMMARIES", summary)

    diff = _git("diff", "--name-only", "AGENTS.md")
    staged = _git("diff", "--cached", "--name-only")
    if diff.stdout.strip() or staged.stdout.strip():
        _git("add", "AGENTS.md")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        _git("commit", "-m", f"docs: auto-update post-merge {ts} [skip-jules]")
        logger.info("Phase 1.5: documentation committed")
    else:
        logger.info("Phase 1.5: no documentation changes")


# ── Phase 2 — Jules session health check ──────────────────────────────────────

def _read_file_section(filepath: str, keyword: str, lines: int = 30) -> str:
    """Read around a keyword in a local file."""
    path = REPO_ROOT / filepath
    if not path.exists():
        return f"File not found: {filepath}"
    text = path.read_text()
    idx = text.find(keyword)
    if idx == -1:
        return text[:500]
    start = max(0, text.rfind("\n", 0, idx - 1) - 200)
    snippet = text[start:idx + 800]
    return snippet[:1500]


_NINAGATE_URL = "http://localhost:8080/v1/chat/completions"
_NINAGATE_TIMEOUT = 45

_SYSTEM_PROMPT = """\
You are an autonomous pipeline manager for the NINA AI OS codebase (Python, FastAPI, APScheduler).
You are responding to a Jules AI coding agent that is blocked and waiting for feedback.

CONSTRAINTS you must enforce in every response:
- Never approve touching: core/router.py, interfaces/telegram_interface.py, guardian_engine.py, .env
- Always require: python3 -m py_compile <file> after every edit
- Always use conventional commits: fix(scope): | feat(scope): | docs(scope):
- Prefer minimal, surgical changes — never restructure unrelated code
- If the task cannot be completed safely, say: "Close this session. Mark task NEEDS_REVIEW."
- If global pause was active and is now lifted, explicitly say: "Global pause is lifted. You may proceed."
- End every response with a clear next action for Jules to take.

Be concise and specific. Jules acts immediately on your reply."""


def _build_context(question: str, session_title: str) -> str:
    """Assemble file snippets and backlog context relevant to the question."""
    chunks: list[str] = []

    for match in re.findall(r"[\w./][\w/.-]+\.py", question):
        snippet = _read_file_section(match, "def ")
        if "not found" not in snippet and snippet.strip():
            chunks.append(f"### {match} (relevant excerpt)\n```python\n{snippet[:800]}\n```")

    task_ids = re.findall(r"AG-[A-Z]-\d+|B-\d{3}", question + " " + session_title)
    if task_ids and BACKLOG_PATH.exists():
        text = BACKLOG_PATH.read_text()
        for tid in task_ids[:3]:
            idx = text.find(tid)
            if idx != -1:
                line = text[max(0, text.rfind("\n", 0, idx)):text.find("\n", idx) + 1].strip()
                chunks.append(f"### Backlog entry: {tid}\n{line}")

    return "\n\n".join(chunks) if chunks else ""


def _auto_answer_fallback(question: str) -> str:
    """Original pattern-matcher — used when NinaGate is unreachable."""
    q = question.lower()
    if any(kw in q for kw in ("what does", "read", "content of", "show me")):
        m = re.search(r"[\w/]+\.py", question)
        if m:
            return _read_file_section(m.group(0), "def ")
        return "Read the file locally and use minimal targeted changes."
    if any(kw in q for kw in ("function", "def ", "signature", "api")):
        m = re.search(r"[\w/]+\.py", question)
        if m:
            return _read_file_section(m.group(0), "def ")
        return "Look up the function definition in the referenced file."
    if "overwrite or append" in q or "replace" in q:
        return "Append unless the task description explicitly says 'replace' or 'overwrite'."
    if "import" in q or "module" in q or "path" in q:
        return "Use the canonical module path from docs/space/nina_index.md."
    if any(kw in q for kw in HIGH_RISK):
        return "Read the file and make a minimal targeted change. Do not restructure."
    return "Proceed with the most conservative implementation. Do not modify unrelated code."


def _auto_answer(question: str, session_title: str = "") -> str:
    """Route Jules question through NinaGate for intelligent response."""
    context = _build_context(question, session_title)

    user_content = f"Session title: {session_title}\n\n"
    if context:
        user_content += f"Relevant codebase context:\n{context}\n\n"
    user_content += f"Jules is asking:\n{question}"

    try:
        resp = requests.post(
            _NINAGATE_URL,
            json={
                "model": "auto",
                "stream": False,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": user_content},
                ],
                "max_tokens": 600,
                "temperature": 0.2,
            },
            timeout=_NINAGATE_TIMEOUT,
        )
        resp.raise_for_status()
        answer = resp.json()["choices"][0]["message"]["content"].strip()
        logger.info(f"_auto_answer: NinaGate response ({len(answer)} chars)")
        return answer

    except Exception as exc:
        logger.warning(f"_auto_answer: NinaGate unreachable ({exc}) — using fallback")
        return _auto_answer_fallback(question)


def phase2_session_health() -> dict:
    result = {"responded": 0, "redispatched": 0, "blocked": []}

    try:
        sessions_data = _jules_api("GET", "sessions", params={"pageSize": 100})
    except Exception as exc:
        logger.warning(f"Jules API unreachable in Phase 2: {exc}")
        return result

    sessions = sessions_data.get("sessions", [])
    registry = _load_registry()

    for s in sessions:
        sid = s.get("name", "").split("/")[-1] or s.get("id", "")
        state = s.get("state", "UNKNOWN")
        title = s.get("title", "Untitled")

        if sid in registry:
            registry[sid]["status"] = state
            registry[sid]["last_updated"] = datetime.utcnow().isoformat() + "Z"

        if state == "AWAITING_USER_FEEDBACK":
            try:
                acts = _jules_api("GET", f"sessions/{sid}/activities", params={"pageSize": 100})
                for act in reversed(acts.get("activities", [])):
                    if "agentMessaged" in act:
                        question = act["agentMessaged"].get("agentMessage", "")
                        answer = _auto_answer(question, session_title=title)
                        _jules_api("POST", f"sessions/{sid}/activities",
                                   json={"userMessage": answer})
                        result["responded"] += 1
                        logger.info(f"Responded to session {sid}: {question[:80]}")
                        break
            except Exception as exc:
                logger.warning(f"Could not respond to session {sid}: {exc}")

        elif state == "FAILED":
            entry = registry.get(sid, {})
            retries = entry.get("retry_count", 0)
            if retries < 1:
                try:
                    task_ids = entry.get("tasks", [])
                    task_title = entry.get("title", title)
                    prompt = f"Re-dispatch of failed task: {task_title}. Tasks: {', '.join(task_ids)}"
                    new_data = _jules_api("POST", "sessions", json={
                        "prompt": prompt,
                        "sourceContext": {
                            "source": "sources/github/aibony/nina",
                            "githubRepoContext": {"startingBranch": "main"}
                        },
                        "automationMode": "AUTO_CREATE_PR",
                        "title": f"[RETRY] {task_title}"
                    })
                    new_sid = new_data.get("id", new_data.get("name", "").split("/")[-1])
                    if new_sid:
                        registry[new_sid] = {
                            "tasks": task_ids, "title": task_title,
                            "status": "IN_PROGRESS", "retry_count": 1,
                            "created_at": datetime.utcnow().isoformat() + "Z",
                            "last_updated": datetime.utcnow().isoformat() + "Z",
                        }
                        result["redispatched"] += 1
                        logger.info(f"Re-dispatched failed session {sid} → {new_sid}")
                    if sid in registry:
                        registry[sid]["retry_count"] = 1
                except Exception as exc:
                    logger.warning(f"Re-dispatch failed for {sid}: {exc}")
                    if sid in registry:
                        registry[sid]["status"] = "BLOCKED"
                    result["blocked"].append(sid)
            else:
                if sid in registry:
                    registry[sid]["status"] = "BLOCKED"
                result["blocked"].append(sid)
                logger.warning(f"Session {sid} marked BLOCKED (exhausted retries)")

    _save_registry(registry)
    return result


# ── Phase 3 — Backlog status sync ─────────────────────────────────────────────

_STATUS_MAP = {
    "MERGED": "MERGED",
    "PR_OPEN": "IN_REVIEW",
    "IN_PROGRESS": "IN_PROGRESS",
    "AWAITING_USER_FEEDBACK": "AWAITING_RESPONSE",
    "AWAITING_RESPONSE": "AWAITING_RESPONSE",
    "COMPLETED": "DONE",
    "DONE": "DONE",
    "FAILED": "FAILED",
    "BLOCKED": "BLOCKED",
    "READY": "READY",
}


def phase3_backlog_sync() -> int:
    registry = _load_registry()
    git_log = _git("log", "--oneline", "-200").stdout

    pr_res = _gh("pr", "list", "--json", "number,title,headRefName,state", "--limit", "50")
    open_prs: list[dict] = json.loads(pr_res.stdout or "[]")

    if not BACKLOG_PATH.exists():
        return 0

    content = BACKLOG_PATH.read_text()
    updated = 0

    for sid, entry in registry.items():
        task_ids = entry.get("tasks", [])
        reg_status = entry.get("status", "UNKNOWN")

        for task_id in task_ids:
            if any(task_id in line for line in git_log.splitlines()):
                true_status = "MERGED"
            elif any(task_id in (p.get("title", "") + p.get("headRefName", "")) for p in open_prs):
                true_status = "PR_OPEN"
            else:
                true_status = reg_status

            write_status = _STATUS_MAP.get(true_status, true_status)

            pattern = rf'(\|\s*{re.escape(task_id)}\s*\|[^|]*\|[^|]*\|)\s*`?[A-Z_]+`?\s*(\|)'
            replacement = rf'\1 `{write_status}` \2'
            new_content, n = re.subn(pattern, replacement, content)
            if n:
                content = new_content
                updated += n

    if updated:
        BACKLOG_PATH.write_text(content)
        _git("add", str(BACKLOG_PATH.relative_to(REPO_ROOT)))
        _git("add", str(REGISTRY_PATH.relative_to(REPO_ROOT)))
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_res = _git("commit", "-m", f"chore(backlog): auto-sync task status {ts}")
        if commit_res.returncode == 0:
            push_res = _git("push", "origin", "main")
            if push_res.returncode != 0:
                logger.warning("Phase 3: push blocked — committed locally")
        logger.info(f"Phase 3: updated {updated} rows in backlog")
    else:
        logger.info("Phase 3: backlog already up to date")

    if not BACKLOG_PATH.exists():
        return updated

    active_task_ids: set[str] = set()
    for entry in registry.values():
        if entry.get("status") in ("IN_PROGRESS", "AWAITING_RESPONSE", "PR_OPEN"):
            active_task_ids.update(entry.get("tasks", []))

    ready_rows = re.findall(r"\|\s*([A-Z]{1,3}-[A-Z\d-]+|\d{8,})\s*\|([^|]+)\|[^|]*\|\s*`READY`", content)
    for task_id, title_raw in ready_rows:
        if task_id in active_task_ids:
            continue
        title = title_raw.strip()
        try:
            asyncio.get_event_loop().run_until_complete(
                _get_jules().goal_to_backlog(title, auto_dispatch=True)
            )
            logger.info(f"Phase 3: auto-dispatched READY task {task_id}: {title[:60]}")
        except Exception as exc:
            logger.warning(f"Phase 3: auto-dispatch failed for {task_id}: {exc}")

    return updated


# ── Phase 4 — Poll loop ────────────────────────────────────────────────────────

async def phase4_poll(p2_result: dict) -> None:
    if p2_result["responded"] == 0:
        return

    for attempt in range(3):
        await asyncio.sleep(120)
        logger.info(f"Phase 4: poll attempt {attempt + 1}/3")

        pr_res = _gh("pr", "list", "--json", "number,mergeable")
        prs = json.loads(pr_res.stdout or "[]")
        if prs:
            phase1_pr_triage()
            phase3_backlog_sync()

        try:
            sd = _jules_api("GET", "sessions", params={"pageSize": 100})
            in_flight = sum(
                1 for s in sd.get("sessions", [])
                if s.get("state") in ("IN_PROGRESS", "AWAITING_USER_FEEDBACK")
            )
            if in_flight == 0:
                break
        except Exception:
            break
