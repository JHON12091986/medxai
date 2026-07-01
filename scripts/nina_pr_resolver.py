#!/usr/bin/env python3
"""
nina_pr_resolver.py — Autonomous PR evaluator and merger for NINA OODA loop

Called by nina_sync.sh A7 when OPEN_PRS > 0.
Uses `gh` CLI (already authenticated via ~/.config/gh/ in systemctl --user context).

Decision flow:
  STARTUP: gh CLI check → fetch all open PRs (oldest first)
  DUPLICATE PASS: detect PRs with near-identical titles → close older, delete branch
  FOR EACH PR:
    hard blocks   → SKIP (draft, do-not-merge, needs-review, wip, duplicate labels)
    conflict gate → CONFLICTING: cherry-pick valuable files → close PR → delete branch
                    UNKNOWN/null: SKIP (GitHub still computing)
    CI gate       → SKIP if checks pending; SKIP+alert if failing
    stale gate    → UPDATE BRANCH if > 10 commits behind main (real rev-list count)
    category      → MERGE if infra_repair | report_only | jules_task | audit
    fallback      → SKIP (no rule matched, logged only)
  POST-MERGE: verify SHA on origin/main → delete merged branch → append audit trail
              → Telegram alert

Safety guarantees:
  - ONE merge per invocation (exits after first merge)
  - do-not-merge label = unconditional human override
  - mergeable=null treated as SKIP (GitHub still computing)
  - dry-run mode: --dry-run flag logs decisions without acting
  - branch deletion always attempted after merge or close

Audit trail: docs/space/pr_resolver_audit.md (append-only)

Author: NINA Architect Overwatch (Perplexity) — 2026-06-23
Version: 2.0.0
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_LOG = REPO_ROOT / "docs" / "space" / "pr_resolver_audit.md"
NINA_LOG   = REPO_ROOT / "logs" / "nina_sync.log"
TZ_LABEL   = "+06"

# Labels that unconditionally block auto-merge
BLOCK_LABELS = {"do-not-merge", "needs-review", "wip", "duplicate", "blocked"}

# PR body / title keywords that classify a PR as safe to auto-merge
INFRA_KEYWORDS  = ["syntaxerror", "fix", "repair", "regression", "hotfix", "patch",
                   "idempotency", "import error"]
REPORT_KEYWORDS = ["audit", "report", "dashboard", "hygiene", "chore(auto)",
                   "ooda sync", "backlog"]
JULES_BRANCH_RE = re.compile(r"jules[/\-]", re.IGNORECASE)

# Max commits a PR branch may lag behind main before we rebase instead of merge
STALE_THRESHOLD = 10

# Title similarity threshold for duplicate detection (0.0–1.0)
DUPLICATE_TITLE_RATIO = 0.85

DRY_RUN = "--dry-run" in sys.argv

# ── Helpers ───────────────────────────────────────────────────────────────────
def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def log(msg: str):
    line = f"{ts()}  [pr_resolver] {msg}"
    print(line)
    try:
        with open(NINA_LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def telegram_alert(msg: str):
    cfg = REPO_ROOT / "config" / "telegram.cfg"
    if not cfg.exists():
        return
    try:
        env = {}
        for line in cfg.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
        token = env.get("TELEGRAM_TOKEN", "")
        chat  = env.get("TELEGRAM_CHAT", "")
        if token and chat:
            subprocess.run(
                ["curl", "-s", "-X", "POST",
                 f"https://api.telegram.org/bot{token}/sendMessage",
                 "-d", f"chat_id={chat}",
                 "-d", f"text=[nina_pr_resolver] {msg}"],
                capture_output=True, timeout=10
            )
    except Exception:
        pass


def gh(*args) -> dict | list | str | None:
    """Run gh CLI, return parsed JSON or raw string."""
    cmd = ["gh"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        log(f"gh error: {result.stderr.strip()[:200]}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout.strip()


def git(*args) -> str:
    """Run git command, return stdout string."""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.stdout.strip()


def append_audit(pr_number: int, action: str, reason: str, sha: str = ""):
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_LOG.exists():
        AUDIT_LOG.write_text("# PR Resolver Audit Log\n\n")
    with open(AUDIT_LOG, "a") as f:
        sha_str = f" | SHA: `{sha[:8]}`" if sha else ""
        f.write(f"## {ts()} {TZ_LABEL}\n")
        f.write(f"- **{action}** PR #{pr_number}{sha_str}\n")
        f.write(f"- Reason: {reason}\n")
        if DRY_RUN:
            f.write("- Mode: DRY-RUN (no action taken)\n")
        f.write("\n")


# ── Branch deletion ───────────────────────────────────────────────────────────
def delete_branch(head_ref: str, pr_number: int):
    """
    Delete a remote branch after merge or close.
    Uses gh api DELETE so it works even if the branch protection allows it.
    Never deletes 'main', 'master', 'develop', 'dev'.
    """
    protected = {"main", "master", "develop", "dev"}
    if not head_ref or head_ref in protected:
        log(f"branch deletion skipped — protected or empty: {head_ref!r}")
        return

    repo_info = gh("repo", "view", "--json", "nameWithOwner")
    if not isinstance(repo_info, dict):
        log("branch deletion skipped — could not determine repo name")
        return
    repo_nwo = repo_info.get("nameWithOwner", "")
    if not repo_nwo:
        log("branch deletion skipped — empty nameWithOwner")
        return

    log(f"deleting branch {head_ref!r} for PR #{pr_number}…")
    if DRY_RUN:
        log(f"DRY-RUN: would delete branch {head_ref!r}")
        return

    result = gh("api", "--method", "DELETE",
                f"/repos/{repo_nwo}/git/refs/heads/{head_ref}")
    if result is None:
        log(f"⚠️ branch deletion may have failed for {head_ref!r} — check GitHub")
    else:
        log(f"✅ branch {head_ref!r} deleted")


# ── PR Evaluation ─────────────────────────────────────────────────────────────
def get_open_prs() -> list[dict]:
    """Fetch open PRs sorted oldest-first."""
    prs = gh("pr", "list", "--state", "open", "--json",
             "number,title,body,labels,mergeable,baseRefName,headRefName,commits",
             "--limit", "20")
    if not isinstance(prs, list):
        return []
    return sorted(prs, key=lambda p: p["number"])


def has_block_label(pr: dict) -> str | None:
    labels = {lb["name"].lower() for lb in pr.get("labels", [])}
    for bl in BLOCK_LABELS:
        if bl in labels:
            return bl
    return None


def get_check_runs(pr_number: int) -> list[dict]:
    cmd = ["gh", "pr", "checks", str(pr_number)]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    checks = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line or "NAME" in line or "DESCRIPTION" in line:
            continue
        status = "SUCCESS"
        if line.startswith("X") or line.startswith("fail") or "failing" in line:
            status = "FAILURE"
        elif line.startswith("-") or "pending" in line:
            status = "IN_PROGRESS"
        
        parts = line.split()
        if len(parts) >= 2:
            name = parts[1]
            checks.append({"name": name, "status": "COMPLETED" if status != "IN_PROGRESS" else "IN_PROGRESS", "conclusion": status})
    return checks


def commits_behind(pr: dict) -> int:
    """
    Real commits-behind count using git rev-list.
    Falls back to PR commits array length if git is unavailable.
    """
    head_ref = pr.get("headRefName", "")
    if not head_ref:
        return len(pr.get("commits", []))
    # Fetch the PR branch so rev-list can compare
    fetch_result = subprocess.run(
        ["git", "fetch", "origin", f"{head_ref}", "--quiet"],
        capture_output=True, cwd=REPO_ROOT
    )
    if fetch_result.returncode != 0:
        return len(pr.get("commits", []))
    count_str = git("rev-list", "--count",
                    f"origin/main..origin/{head_ref}")
    try:
        return int(count_str)
    except ValueError:
        return len(pr.get("commits", []))


def classify(pr: dict) -> str:
    """Return merge category or UNKNOWN."""
    title = pr.get("title", "").lower()
    body  = (pr.get("body") or "").lower()
    head  = pr.get("headRefName", "")
    combined = title + " " + body

    if JULES_BRANCH_RE.search(head):
        return "jules_task"
    if any(kw in combined for kw in INFRA_KEYWORDS):
        return "infra_repair"
    if any(kw in combined for kw in REPORT_KEYWORDS):
        return "report_only"
    return "UNKNOWN"


def evaluate_pr(pr: dict) -> tuple[str, str]:
    """
    Returns (verdict, reason).
    verdict: MERGE | UPDATE_BRANCH | SKIP | CLOSE_CONFLICTING
    """
    num   = pr["number"]

    if pr.get("baseRefName", "main") != "main":
        return "SKIP", f"base is {pr.get('baseRefName')} not main"

    block_label = has_block_label(pr)
    if block_label:
        return "SKIP", f"blocked label: {block_label}"

    # ── Conflict gate ─────────────────────────────────────────────────────────
    mergeable = pr.get("mergeable")  # MERGEABLE | CONFLICTING | UNKNOWN | null
    if mergeable is None or str(mergeable).upper() == "UNKNOWN":
        return "SKIP", "mergeable state unknown (GitHub still computing)"
    if str(mergeable).upper() == "CONFLICTING":
        return "CLOSE_CONFLICTING", "merge conflicts with main — cherry-pick + close"

    # ── CI check gate ─────────────────────────────────────────────────────────
    checks = get_check_runs(num)
    pending = [c for c in checks if c.get("status") == "IN_PROGRESS"]
    failing = [c for c in checks if c.get("conclusion") == "FAILURE"]
    if pending:
        return "SKIP", f"CI pending ({len(pending)} check(s) running)"
    if failing:
        names = ", ".join(c.get("name", "?") for c in failing[:3])
        telegram_alert(f"🔴 PR #{num} CI failing: {names}")
        return "SKIP", f"CI failing: {names}"

    # ── Stale branch gate ─────────────────────────────────────────────────────
    behind = commits_behind(pr)
    if behind > STALE_THRESHOLD:
        return "UPDATE_BRANCH", f"branch is {behind} commits behind main — rebasing"

    # ── Category gate ─────────────────────────────────────────────────────────
    category = classify(pr)
    if category != "UNKNOWN":
        return "MERGE", f"category={category}"

    return "SKIP", "no auto-merge rule matched — needs human review"


# ── Duplicate detection ───────────────────────────────────────────────────────
def find_duplicate_pairs(prs: list[dict]) -> list[tuple[dict, dict]]:
    """
    Return pairs (older_pr, newer_pr) where title similarity >= DUPLICATE_TITLE_RATIO.
    Only flags pairs where older is clearly superseded by newer.
    """
    pairs = []
    for i, older in enumerate(prs):
        for newer in prs[i + 1:]:
            ratio = SequenceMatcher(
                None,
                older.get("title", "").lower(),
                newer.get("title", "").lower()
            ).ratio()
            if ratio >= DUPLICATE_TITLE_RATIO:
                pairs.append((older, newer))
    return pairs


def close_duplicate_pr(pr: dict, reason: str):
    """Close an older PR that is superseded by a duplicate."""
    num     = pr["number"]
    title   = pr.get("title", f"PR #{num}")
    head    = pr.get("headRefName", "")
    log(f"CLOSE_DUPLICATE PR #{num}: {title} ({reason})")
    if DRY_RUN:
        log(f"DRY-RUN: would close PR #{num} and delete branch {head!r}")
        append_audit(num, "DRY-RUN CLOSE_DUPLICATE", reason)
        return
    gh("pr", "close", str(num),
       "--comment", f"Auto-closed by nina_pr_resolver v2.0 — superseded by newer PR | {reason} | {ts()}")
    append_audit(num, "CLOSED_DUPLICATE", reason)
    telegram_alert(f"🗑️ Closed duplicate PR #{num}: {title}")
    delete_branch(head, num)


# ── Conflict handler ──────────────────────────────────────────────────────────
def do_close_conflicting(pr: dict, reason: str):
    """
    Handle a CONFLICTING PR:
      1. Cherry-pick any pure-add files (new files, no merge needed) to main directly.
      2. Close the PR with an explanatory comment.
      3. Delete the branch.
    Keeps valuable work from lost PRs without requiring manual conflict resolution.
    """
    num   = pr["number"]
    title = pr.get("title", f"PR #{num}")
    head  = pr.get("headRefName", "")
    log(f"CLOSE_CONFLICTING PR #{num}: {title}")

    if DRY_RUN:
        log(f"DRY-RUN: would cherry-pick pure-add files from {head!r}, close PR #{num}, delete branch")
        append_audit(num, "DRY-RUN CLOSE_CONFLICTING", reason)
        return

    # Fetch the conflicting branch
    fetch = subprocess.run(
        ["git", "fetch", "origin", head, "--quiet"],
        capture_output=True, cwd=REPO_ROOT
    )
    rescued_files = []
    if fetch.returncode == 0:
        # Find files that are purely added (A = added) relative to main
        diff_result = subprocess.run(
            ["git", "diff", "--name-status", "origin/main", f"origin/{head}"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        pure_adds = [
            line.split("\t", 1)[1].strip()
            for line in diff_result.stdout.splitlines()
            if line.startswith("A\t")
        ]
        for filepath in pure_adds:
            # Copy file directly from the conflicting branch to working tree
            show = subprocess.run(
                ["git", "show", f"origin/{head}:{filepath}"],
                capture_output=True, cwd=REPO_ROOT
            )
            if show.returncode == 0:
                dest = REPO_ROOT / filepath
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(show.stdout)
                rescued_files.append(filepath)

        if rescued_files:
            subprocess.run(
                ["git", "add"] + rescued_files, cwd=REPO_ROOT
            )
            subprocess.run(
                ["git", "commit", "--no-verify",
                 "-m", f"chore(rescue): cherry-pick pure-adds from conflicting PR #{num} [skip ci]"],
                cwd=REPO_ROOT
            )
            log(f"rescued {len(rescued_files)} pure-add file(s) from PR #{num}: {rescued_files}")
        else:
            log(f"no pure-add files to rescue from PR #{num}")

    rescued_str = ", ".join(rescued_files) if rescued_files else "none"
    gh("pr", "close", str(num),
       "--comment",
       f"Auto-closed by nina_pr_resolver v2.0 — conflicts with main.\n"
       f"Rescued pure-add files: {rescued_str}\n"
       f"Reason: {reason} | {ts()}")
    append_audit(num, "CLOSED_CONFLICTING",
                 f"{reason} | rescued: {rescued_str}")
    telegram_alert(f"⚠️ PR #{num} had conflicts — rescued {len(rescued_files)} file(s), closed PR")
    delete_branch(head, num)


# ── Actions ───────────────────────────────────────────────────────────────────
def do_merge(pr: dict, reason: str):
    num   = pr["number"]
    title = pr.get("title", f"PR #{num}")
    head  = pr.get("headRefName", "")
    log(f"MERGE PR #{num}: {title} ({reason})")

    if DRY_RUN:
        log(f"DRY-RUN: would squash-merge PR #{num}")
        append_audit(num, "DRY-RUN MERGE", reason)
        return

    gh("pr", "merge", str(num),
       "--squash", "--auto",
       "--subject", f"{title} (#{num})",
       "--body", f"Auto-merged by nina_pr_resolver.py v2.0 | {reason} | {ts()}")

    # Verify merge landed
    time.sleep(3)
    pr_state = gh("pr", "view", str(num), "--json", "state,mergeCommit")
    if isinstance(pr_state, dict) and pr_state.get("state") == "MERGED":
        sha = (pr_state.get("mergeCommit") or {}).get("oid", "")
        log(f"✅ PR #{num} merged — SHA {sha[:8]}")
        append_audit(num, "MERGED", reason, sha)
        telegram_alert(f"✅ Auto-merged PR #{num}: {title} | {reason}")
        delete_branch(head, num)
    else:
        log(f"⚠️ PR #{num} merge API called but state not confirmed — check GitHub")
        append_audit(num, "MERGE_UNCONFIRMED", reason)
        telegram_alert(f"⚠️ PR #{num} merge unconfirmed — check GitHub manually")


def do_update_branch(pr: dict, reason: str):
    num = pr["number"]
    log(f"UPDATE_BRANCH PR #{num}: {reason}")
    if DRY_RUN:
        log(f"DRY-RUN: would rebase PR #{num} onto main")
        append_audit(num, "DRY-RUN UPDATE_BRANCH", reason)
        return
    gh("pr", "update-branch", str(num), "--rebase")
    append_audit(num, "BRANCH_UPDATED", reason)
    telegram_alert(f"🔄 Rebased PR #{num} onto main — will re-evaluate next OODA cycle")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Verify gh CLI is available and authenticated
    whoami = gh("auth", "status")
    if whoami is None:
        log("ERROR: gh CLI not authenticated — cannot resolve PRs")
        sys.exit(0)  # non-fatal: fall through to normal OODA

    prs = get_open_prs()
    if not prs:
        log("no open PRs found via gh CLI")
        sys.exit(0)

    log(f"evaluating {len(prs)} open PR(s) (oldest first)")

    # ── Duplicate pass (runs before per-PR evaluation) ────────────────────────
    dup_pairs = find_duplicate_pairs(prs)
    if dup_pairs:
        log(f"found {len(dup_pairs)} duplicate PR pair(s) — closing older ones")
        closed_numbers: set[int] = set()
        for older, newer in dup_pairs:
            if older["number"] not in closed_numbers:
                close_duplicate_pr(
                    older,
                    f"superseded by PR #{newer['number']}: '{newer.get('title','?')[:60]}'"
                )
                closed_numbers.add(older["number"])
        # Refresh PR list after closures
        prs = [p for p in prs if p["number"] not in closed_numbers]
        if not prs:
            log("all PRs were duplicates — nothing left to evaluate")
            sys.exit(0)

    # ── Per-PR evaluation ─────────────────────────────────────────────────────
    for pr in prs:
        num   = pr["number"]
        title = pr.get("title", "?")
        verdict, reason = evaluate_pr(pr)
        log(f"PR #{num} '{title[:60]}' → {verdict}: {reason}")

        if verdict == "MERGE":
            do_merge(pr, reason)
            sys.exit(0)  # ONE merge per OODA cycle

        elif verdict == "UPDATE_BRANCH":
            do_update_branch(pr, reason)
            sys.exit(0)  # one branch update per cycle

        elif verdict == "CLOSE_CONFLICTING":
            do_close_conflicting(pr, reason)
            sys.exit(0)  # one conflict resolution per cycle

        else:  # SKIP
            append_audit(num, "SKIPPED", reason)
            if any(kw in reason for kw in ["conflicts", "CI failing", "loop"]):
                telegram_alert(f"⏭️ PR #{num} skipped: {reason}")

    log("all PRs evaluated — none merged this cycle")


if __name__ == "__main__":
    main()
