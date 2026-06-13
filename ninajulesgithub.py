"""
NinaJulesGitHub — Autonomous Jules/GitHub Pipeline Daemon v1.0
==============================================================
Self-sustaining 3-minute loop managing the Jules→PR→merge pipeline
independently of NINA. Never blindly merges — every PR passes a
Surgical Gate before merge.

Phases every cycle:
  0  — Safety / global-pause check
  1  — Jules session health: auto-unblock AWAITING via NinaGate LLM
  2  — PR triage + Surgical Gate (py_compile, pyflakes, security scan,
        high-risk file block) → merge/close/defer
  3  — Backlog status sync
  4  — Duplicate session cleanup
  5  — Telegram cycle report
"""
from __future__ import annotations

import fcntl
import json
import logging
import logging.handlers
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import dotenv

dotenv.load_dotenv(Path(__file__).parent / ".env")

# ── Constants ──────────────────────────────────────────────────────────────────
REPO_ROOT      = Path(__file__).parent.resolve()
BACKLOG_PATH   = REPO_ROOT / "docs" / "space" / "jules_backlog.md"
REGISTRY_PATH  = REPO_ROOT / "data" / "jules_registry.json"
LOCK_PATH      = REPO_ROOT / "data" / "ninajulesgithub.lock"
LOG_PATH       = REPO_ROOT / "logs" / "ninajulesgithub.log"
RESPONDED_PATH = REPO_ROOT / "data" / "jules_auto_responded.json"
LOOP_INTERVAL  = 180  # seconds

JULES_BASE_URL   = "https://jules.googleapis.com/v1alpha"
NINAGATE_URL     = "http://localhost:8080/v1/chat/completions"
NINAGATE_TIMEOUT = 45

# High-risk files — blocked from auto-merge
HIGH_RISK = {
    "core/nina.py", "core/router.py", "core/agent.py",
    "guardian_engine.py", "interfaces/telegram_interface.py",
    "core/config.py", ".env", "tools/shell.py",
}

# Security patterns — any added diff line matching these fails the gate
SECURITY_PATTERNS = [
    (re.compile(r"\beval\s*\("),       "eval() call"),
    (re.compile(r"\bexec\s*\("),       "exec() call"),
    (re.compile(r"shell\s*=\s*True"),  "shell=True subprocess risk"),
    (re.compile(r"os\.system\s*\("),   "os.system() call"),
    (re.compile(r"__import__\s*\("),   "__import__() dynamic import"),
    (re.compile(r"ALLOWED\s*=.*cat"),  "cat in shell allowlist (R-48 regression)"),
]

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_fh  = logging.handlers.TimedRotatingFileHandler(
    LOG_PATH, when="midnight", backupCount=7, encoding="utf-8")
_fh.setFormatter(_fmt)
_sh  = logging.StreamHandler(sys.stdout)
_sh.setFormatter(_fmt)
logging.basicConfig(level=logging.INFO, handlers=[_fh, _sh])
logger = logging.getLogger("nina.ninajulesgithub")

# ── Helpers ────────────────────────────────────────────────────────────────────
def _run(cmd: list, *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or REPO_ROOT))

def _git(*args: str) -> subprocess.CompletedProcess:
    return _run(["git", *args])

def _gh(*args: str) -> subprocess.CompletedProcess:
    return _run(["gh", *args])

def _telegram(msg: str) -> None:
    token   = os.environ.get("TELEGRAMBOTTOKEN")
    chat_id = os.environ.get("AUTHORIZEDUSERID")
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
            timeout=10)
    except Exception as exc:
        logger.warning(f"Telegram failed: {exc}")

def _jules(method: str, path: str, **kwargs) -> dict:
    key = os.environ.get("JULES_API_KEY", "")
    if not key:
        raise RuntimeError("JULES_API_KEY not set")
    resp = requests.request(
        method, f"{JULES_BASE_URL}/{path.lstrip('/')}",
        headers={"X-Goog-Api-Key": key, "Content-Type": "application/json"},
        timeout=30, **kwargs)
    if resp.status_code == 404:
        return {"error": "not_found"}
    resp.raise_for_status()
    return resp.json() if method.upper() != "DELETE" else {"status": "ok"}

def _load_reg() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text())
    except Exception:
        return {}

def _save_reg(data: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2))

# ── Phase 0 — Safety ───────────────────────────────────────────────────────────
def phase0_safety() -> bool:
    if BACKLOG_PATH.exists() and "GLOBAL PAUSE ACTIVE" in BACKLOG_PATH.read_text():
        logger.info("GLOBAL PAUSE active — new dispatch suppressed")
        return True
    return False

# ── Phase 1 — Jules session health ────────────────────────────────────────────
_SYS_PROMPT = """\
You are an autonomous pipeline manager for the NINA AI OS codebase (Python/AsyncIO).
Responding to a Jules AI coding agent blocked waiting for feedback.
HARD RULES:
- Never approve modifying core/router.py, interfaces/telegram_interface.py,
  guardian_engine.py, .env, tools/shell.py without explicit human approval.
- Always require: python3 -m py_compile <file> && python3 -m pyflakes <file>.
- Conventional commits: fix(scope): | feat(scope): | docs(scope):
- Prefer minimal, surgical changes. Never restructure unrelated code.
- If task cannot be completed safely: say exactly "Close this session. Mark task NEEDS_REVIEW."
- End every response with a clear, specific next action for Jules.
Be concise. Jules acts immediately on your reply."""

def _ninagate(question: str, title: str = "") -> str:
    chunks: list[str] = []
    for m in re.findall(r"[\w./][\w/.-]+\.py", question):
        p = REPO_ROOT / m
        if p.exists():
            chunks.append(f"### {m}\n```python\n{p.read_text()[:800]}\n```")
    task_ids = re.findall(r"AG-[A-Z]-\d+|B-\d{3}", question + " " + title)
    if task_ids and BACKLOG_PATH.exists():
        text = BACKLOG_PATH.read_text()
        for tid in task_ids[:2]:
            idx = text.find(tid)
            if idx != -1:
                line = text[max(0, text.rfind("\n", 0, idx)):text.find("\n", idx)+1].strip()
                chunks.append(f"### Backlog: {tid}\n{line}")
    user = f"Session: {title}\n\n"
    if chunks:
        user += "Context:\n" + "\n\n".join(chunks) + "\n\n"
    user += f"Jules asks:\n{question}"
    try:
        resp = requests.post(NINAGATE_URL, json={
            "model": "auto", "stream": False,
            "messages": [{"role": "system", "content": _SYS_PROMPT},
                         {"role": "user", "content": user}],
            "max_tokens": 500, "temperature": 0.2,
        }, timeout=NINAGATE_TIMEOUT)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning(f"NinaGate unreachable ({exc}) — pattern fallback")
        ql = question.lower()
        if any(kw in ql for kw in ("shall i", "should i", "proceed", "open a pr", "ready")):
            return ("LGTM. Please open a PR with your completed changes now. "
                    "Run python3 -m py_compile on all modified files first.")
        if any(kw in ql for kw in ("accidentally removed", "regression", "reverted")):
            return ("Open a PR with only verified, clean changes. "
                    "Do not include accidentally removed code or unresolved regressions.")
        return "Proceed with the most conservative implementation. Do not modify unrelated code."

def phase1_session_health() -> dict:
    result = {"responded": 0, "redispatched": 0, "blocked": []}
    responded: set = set()
    if RESPONDED_PATH.exists():
        try:
            responded = set(json.loads(RESPONDED_PATH.read_text()))
        except Exception:
            pass
    try:
        data = _jules("GET", "sessions", params={"pageSize": 100})
    except Exception as exc:
        logger.warning(f"Phase 1: Jules API error: {exc}")
        return result
    registry = _load_reg()
    newly: list[str] = []
    for s in data.get("sessions", []):
        sid   = s.get("name", "").split("/")[-1] or s.get("id", "")
        state = s.get("state", "UNKNOWN")
        title = s.get("title", "Untitled")
        if sid in registry:
            registry[sid].update({"status": state,
                                   "last_updated": datetime.utcnow().isoformat() + "Z"})
        if state == "AWAITING_USER_FEEDBACK" and sid not in responded:
            try:
                acts = _jules("GET", f"sessions/{sid}/activities", params={"pageSize": 100})
                for act in reversed(acts.get("activities", [])):
                    if "agentMessaged" in act:
                        q = act["agentMessaged"].get("agentMessage", "")
                        if not q:
                            continue
                        answer = _ninagate(q, title)
                        _jules("POST", f"sessions/{sid}:sendMessage", json={"prompt": answer})
                        logger.info(f"Phase 1: responded to {sid[:14]}…")
                        newly.append(sid)
                        result["responded"] += 1
                        break
            except Exception as exc:
                logger.warning(f"Phase 1: failed responding to {sid}: {exc}")
        elif state == "FAILED":
            entry   = registry.get(sid, {})
            retries = entry.get("retry_count", 0)
            if retries < 1:
                try:
                    task_ids   = entry.get("tasks", [])
                    task_title = entry.get("title", title)
                    new_data   = _jules("POST", "sessions", json={
                        "prompt": f"Re-dispatch of failed task: {task_title}. Tasks: {', '.join(task_ids)}",
                        "sourceContext": {"source": "sources/github/aibony/nina",
                                          "githubRepoContext": {"startingBranch": "main"}},
                        "automationMode": "AUTO_CREATE_PR",
                        "title": f"[RETRY] {task_title}",
                    })
                    new_sid = new_data.get("id", new_data.get("name", "").split("/")[-1])
                    if new_sid:
                        registry[new_sid] = {"tasks": task_ids, "title": task_title,
                                              "status": "IN_PROGRESS", "retry_count": 1,
                                              "created_at": datetime.utcnow().isoformat() + "Z",
                                              "last_updated": datetime.utcnow().isoformat() + "Z"}
                        result["redispatched"] += 1
                    if sid in registry:
                        registry[sid]["retry_count"] = 1
                except Exception as exc:
                    logger.warning(f"Phase 1: re-dispatch failed for {sid}: {exc}")
                    if sid in registry:
                        registry[sid]["status"] = "BLOCKED"
                    result["blocked"].append(sid)
            else:
                if sid in registry:
                    registry[sid]["status"] = "BLOCKED"
                result["blocked"].append(sid)
    _save_reg(registry)
    if newly:
        RESPONDED_PATH.write_text(json.dumps(list(responded | set(newly)), indent=2))
    return result

# ── Surgical Gate ──────────────────────────────────────────────────────────────
def _changed_files(branch: str) -> list[str]:
    res = _git("diff", "--name-only", f"origin/main...origin/{branch}")
    return [l.strip() for l in res.stdout.splitlines() if l.strip()]

def _diff_added(branch: str) -> list[str]:
    diff = _git("diff", f"origin/main...origin/{branch}").stdout
    return [l[1:] for l in diff.splitlines()
            if l.startswith("+") and not l.startswith("+++")]

def surgical_gate(pr: dict) -> tuple[bool, str]:
    """Returns (pass, reason). Checks high-risk → security → py_compile → pyflakes."""
    branch  = pr.get("headRefName", "")
    changed = _changed_files(branch)
    if not changed:
        return True, "no changed files"

    # 1. High-risk file block
    hits = [f for f in changed if f in HIGH_RISK]
    if hits:
        return False, f"high-risk files modified: {hits}"

    # 2. Security pattern scan on added lines only
    for pattern, label in SECURITY_PATTERNS:
        for line in _diff_added(branch):
            if pattern.search(line):
                return False, f"security [{label}] in: {line.strip()[:120]}"

    # 3. py_compile + pyflakes via temp checkout
    py_files = [f for f in changed if f.endswith(".py")]
    if py_files:
        if _git("fetch", "origin", branch).returncode != 0:
            return False, "git fetch failed"
        _git("stash", "--include-untracked", "-q")
        _git("checkout", "-B", f"_gate_{branch[:38]}", f"origin/{branch}")
        failures: list[str] = []
        for f in py_files:
            if not (REPO_ROOT / f).exists():
                continue
            comp = _run(["python3", "-m", "py_compile", f])
            if comp.returncode != 0:
                failures.append(f"py_compile FAIL {f}: {comp.stderr.strip()[:150]}")
                continue
            flakes = _run(["python3", "-m", "pyflakes", f])
            errors = [l for l in flakes.stdout.splitlines()
                      if any(kw in l.lower() for kw in
                             ("undefined name", "redefinition", "syntax error"))]
            if errors:
                failures.append(f"pyflakes {f}: {'; '.join(errors[:3])}")
        _git("checkout", "main", "-q")
        _git("stash", "pop", "-q")
        if failures:
            return False, " | ".join(failures)

    return True, "all checks passed"

# ── Phase 2 — PR triage ────────────────────────────────────────────────────────
def _detect_dups(prs: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for pr in prs:
        m = re.search(r"(AG-[A-Z]-\d+|\d{15,})",
                      pr.get("headRefName", "") + pr.get("title", ""))
        if m:
            groups.setdefault(m.group(1), []).append(pr)
    return {k: v for k, v in groups.items() if len(v) > 1}

def _try_rebase(pr: dict) -> tuple[bool, str]:
    branch  = pr["headRefName"]
    hits    = [f for f in _changed_files(branch) if f in HIGH_RISK]
    if hits:
        return False, f"high-risk conflict: {hits}"
    if _git("fetch", "origin", branch).returncode != 0:
        return False, "fetch failed"
    _git("checkout", "-B", branch, f"origin/{branch}")
    rebase = _git("rebase", "origin/main")
    if rebase.returncode != 0:
        _git("rebase", "--abort")
        _git("checkout", "main")
        return False, f"rebase conflict: {rebase.stderr[:200]}"
    push = _git("push", "origin", branch, "--force-with-lease")
    _git("checkout", "main")
    if push.returncode != 0:
        return False, f"force-push failed: {push.stderr[:200]}"
    return True, "rebased"

def _merge(num: int) -> bool:
    r = _gh("pr", "merge", str(num), "--squash", "--delete-branch", "--yes")
    if r.returncode == 0:
        return True
    r2 = _gh("pr", "merge", str(num), "--merge", "--admin", "-d",
              "-b", "Automerged via NinaJulesGitHub after surgical gate.")
    return r2.returncode == 0

def phase2_pr_triage() -> dict:
    result = {"merged": [], "gate_passed": [], "gate_failed": [],
              "closed_duplicate": [], "closed_stale": [],
              "closed_high_risk": [], "deferred": [], "failed": []}

    res = _gh("pr", "list", "--json",
              "number,title,headRefName,mergeable,mergeStateStatus,state,createdAt",
              "--limit", "200")
    if res.returncode != 0:
        logger.error(f"Phase 2: gh pr list failed: {res.stderr}")
        return result

    prs: list[dict] = json.loads(res.stdout or "[]")
    if not prs:
        return result

    # 1. Close duplicates — keep newest
    for task_id, dup_prs in _detect_dups(prs).items():
        dup_prs.sort(key=lambda p: p.get("createdAt", ""), reverse=True)
        for old in dup_prs[1:]:
            _gh("pr", "close", str(old["number"]), "--comment",
                f"Auto-closed: duplicate — superseded by PR #{dup_prs[0]['number']} (task {task_id}).")
            result["closed_duplicate"].append(old["number"])
            logger.info(f"Phase 2: closed duplicate PR #{old['number']}")

    # Refresh after closing duplicates
    res = _gh("pr", "list", "--json",
              "number,title,headRefName,mergeable,mergeStateStatus,state,createdAt",
              "--limit", "200")
    prs = json.loads(res.stdout or "[]")

    # 2. Close stale conflicting PRs (>72h, task already in main)
    now     = datetime.now(timezone.utc)
    git_log = _git("log", "--oneline", "-100").stdout
    for pr in list(prs):
        try:
            age = now - datetime.fromisoformat(
                pr.get("createdAt", "").replace("Z", "+00:00"))
        except Exception:
            age = timedelta(0)
        if age > timedelta(hours=72) and pr.get("mergeable") == "CONFLICTING":
            branch = pr.get("headRefName", "")
            if any(w in git_log for w in re.findall(r"\d{10,}", branch)):
                _gh("pr", "close", str(pr["number"]), "--comment",
                    "Auto-closed: stale — task already merged in main.")
                result["closed_stale"].append(pr["number"])
                prs.remove(pr)

    # 3. Process each PR
    for pr in prs:
        num         = pr["number"]
        mergeable   = pr.get("mergeable", "UNKNOWN")
        merge_state = pr.get("mergeStateStatus", "UNKNOWN")

        if mergeable == "UNKNOWN" or merge_state == "UNKNOWN":
            result["deferred"].append(num)
            logger.info(f"Phase 2: PR #{num} UNKNOWN — deferred to next cycle")
            continue

        if mergeable == "CONFLICTING" or merge_state == "DIRTY":
            ok, reason = _try_rebase(pr)
            if not ok:
                if "high-risk" in reason:
                    _gh("pr", "close", str(num), "--comment",
                        f"Auto-closed: high-risk file conflict — needs human review. {reason}")
                    result["closed_high_risk"].append(num)
                    logger.warning(f"Phase 2: closed high-risk PR #{num}: {reason}")
                else:
                    result["failed"].append(num)
                    logger.warning(f"Phase 2: rebase failed PR #{num}: {reason}")
                continue

        # ── Surgical Gate ──
        gate_ok, gate_reason = surgical_gate(pr)
        if not gate_ok:
            result["gate_failed"].append(num)
            logger.warning(f"Phase 2: PR #{num} GATE FAILED — {gate_reason}")
            _gh("pr", "comment", str(num), "--body",
                f"🚫 **NinaJulesGitHub Surgical Gate FAILED**\n\n"
                f"```\n{gate_reason}\n```\n\n"
                f"This PR will not auto-merge until the above is fixed.\n"
                f"Jules: please fix and push a new commit to this branch.")
            continue

        result["gate_passed"].append(num)
        logger.info(f"Phase 2: PR #{num} passed gate — merging")
        if _merge(num):
            result["merged"].append(num)
            logger.info(f"Phase 2: ✅ merged PR #{num}: {pr['title'][:60]}")
        else:
            result["failed"].append(num)
            logger.warning(f"Phase 2: merge failed PR #{num}")

    # Push if local main ahead from rebase commits
    ahead = _git("rev-list", "origin/main..HEAD", "--count").stdout.strip()
    if ahead.isdigit() and int(ahead) > 0:
        push = _git("push", "origin", "main")
        if push.returncode != 0:
            logger.warning(f"Phase 2: push blocked: {push.stderr[:200]}")

    logger.info(f"Phase 2: merged={result['merged']} gate_failed={result['gate_failed']} "
                f"deferred={len(result['deferred'])}")
    return result

# ── Phase 3 — Backlog sync ─────────────────────────────────────────────────────
_STATUS_MAP = {
    "MERGED": "MERGED", "PR_OPEN": "IN_REVIEW", "IN_PROGRESS": "IN_PROGRESS",
    "AWAITING_USER_FEEDBACK": "AWAITING_RESPONSE", "AWAITING_RESPONSE": "AWAITING_RESPONSE",
    "COMPLETED": "DONE", "DONE": "DONE", "FAILED": "FAILED",
    "BLOCKED": "BLOCKED", "READY": "READY",
}

def phase3_backlog_sync() -> int:
    registry = _load_reg()
    git_log  = _git("log", "--oneline", "-200").stdout
    open_prs: list[dict] = json.loads(
        _gh("pr", "list", "--json", "number,title,headRefName,state",
            "--limit", "200").stdout or "[]")
    if not BACKLOG_PATH.exists():
        return 0
    content = BACKLOG_PATH.read_text()
    updated = 0
    for sid, entry in registry.items():
        for task_id in entry.get("tasks", []):
            if any(task_id in line for line in git_log.splitlines()):
                ts = "MERGED"
            elif any(task_id in (p.get("title", "") + p.get("headRefName", ""))
                     for p in open_prs):
                ts = "PR_OPEN"
            else:
                ts = entry.get("status", "UNKNOWN")
            ws = _STATUS_MAP.get(ts, ts)
            pat = rf'(\|\s*{re.escape(task_id)}\s*\|[^|]*\|[^|]*\|)\s*`?[A-Z_]+`?\s*(\|)'
            new_content, n = re.subn(pat, rf'\1 `{ws}` \2', content)
            if n:
                content = new_content
                updated += n
    if updated:
        BACKLOG_PATH.write_text(content)
        _git("add", str(BACKLOG_PATH.relative_to(REPO_ROOT)))
        _git("add", str(REGISTRY_PATH.relative_to(REPO_ROOT)))
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit = _git("commit", "-m",
                      f"chore(backlog): auto-sync task status {ts} [skip-jules]")
        if commit.returncode == 0 and _git("push", "origin", "main").returncode != 0:
            logger.warning("Phase 3: push blocked — committed locally")
        logger.info(f"Phase 3: updated {updated} backlog rows")
    return updated

# ── Phase 4 — Cleanup ──────────────────────────────────────────────────────────
def phase4_cleanup() -> int:
    registry = _load_reg()
    task_to_sids: dict[str, list[str]] = {}
    for sid, entry in registry.items():
        for tid in entry.get("tasks", []):
            task_to_sids.setdefault(tid, []).append(sid)
    removed = 0
    for tid, sids in task_to_sids.items():
        active = [s for s in sids if registry.get(s, {}).get("status")
                  not in ("FAILED", "BLOCKED", "MERGED", "DUPLICATE")]
        if len(active) > 1:
            active.sort(key=lambda s: registry.get(s, {}).get("created_at", ""), reverse=True)
            for old_sid in active[1:]:
                registry[old_sid]["status"] = "DUPLICATE"
                removed += 1
    _save_reg(registry)
    return removed

# ── Phase 5 — Report ───────────────────────────────────────────────────────────
def phase5_report(p1: dict, p2: dict, p3: int, p4: int, duration: float) -> None:
    gate_line = ""
    if p2.get("gate_failed"):
        gate_line = f"\n⚠️ Gate failures: PR#{', #'.join(str(n) for n in p2['gate_failed'])}"
    msg = (
        f"🤖 *NinaJulesGitHub*\n"
        f"PRs merged: {len(p2.get('merged', []))} | "
        f"Gate passed: {len(p2.get('gate_passed', []))} | "
        f"Deferred: {len(p2.get('deferred', []))}\n"
        f"Sessions unblocked: {p1.get('responded', 0)} | "
        f"Re-dispatched: {p1.get('redispatched', 0)}\n"
        f"Backlog synced: {p3} rows | Dupes cleaned: {p4}"
        f"{gate_line}\n⏱ {duration:.1f}s"
    )
    _telegram(msg)
    logger.info(f"Cycle complete in {duration:.1f}s")

# ── Main cycle ─────────────────────────────────────────────────────────────────
def run_cycle() -> None:
    start = time.monotonic()
    logger.info("═══ NinaJulesGitHub cycle start ═══")
    global_pause = phase0_safety()
    p1 = phase1_session_health()
    p2 = phase2_pr_triage()
    p3 = phase3_backlog_sync() if not global_pause else 0
    p4 = phase4_cleanup()
    phase5_report(p1, p2, p3, p4, time.monotonic() - start)

def main() -> None:
    logger.info("NinaJulesGitHub daemon starting")
    _telegram("🟢 *NinaJulesGitHub* daemon started")
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_PATH, "w") as lf:
        try:
            fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            logger.error("Another instance already running — exiting")
            sys.exit(1)
        try:
            while True:
                try:
                    run_cycle()
                except Exception as exc:
                    logger.exception(f"Cycle error: {exc}")
                logger.info(f"Sleeping {LOOP_INTERVAL}s")
                time.sleep(LOOP_INTERVAL)
        except KeyboardInterrupt:
            logger.info("NinaJulesGitHub stopped by signal")
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)

if __name__ == "__main__":
    main()
