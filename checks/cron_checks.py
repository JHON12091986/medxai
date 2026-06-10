from checks.runner import record, NINA_DIR
import re
def check_cron_ids():
    mgr_path = NINA_DIR / "crons" / "manager.py"
    if not mgr_path.exists():
        record("INFO", "cron.manager.missing", "crons/manager.py not found — skipping cron ID check")
        return

    source = mgr_path.read_text(errors="replace")
    ids_found = re.findall(r"id\s*=\s*['\"]([^'\"]+)['\"]", source)
    seen = {}
    duplicates = []
    for job_id in ids_found:
        seen[job_id] = seen.get(job_id, 0) + 1
    for job_id, count in seen.items():
        if count > 1:
            duplicates.append(job_id)

    if duplicates:
        record(
            "BLOCKER", "cron.conflicting_id",
            f"Duplicate APScheduler job ID(s) found: {', '.join(duplicates)}",
            detail=f"Duplicate IDs in crons/manager.py: {duplicates}. Causes ConflictingIdError on startup.",
            fix="Remove or rename duplicate job registrations in ~/nina/crons/manager.py (R-23 fix).",
        )
    else:
        record("PASS", "cron.conflicting_id", "APScheduler job IDs — no duplicates — OK")

    # R-62: lambda coroutine drop
    if re.search(r"lambda\s*:\s*\w+\(", source) and not re.search(r"functools\.partial", source):
        record(
            "WARN", "cron.lambda_coroutine_drop",
            "APScheduler jobs may use lambda instead of functools.partial",
            detail="lambda: coroutine_fn(n) is sync; APScheduler will call it without awaiting.",
            fix="Replace lambda: fn(n) with functools.partial(fn, n) in crons/manager.py (R-62 fix).",
        )
    else:
        record("PASS", "cron.lambda_coroutine_drop", "APScheduler job callables — functools.partial in use — OK")
