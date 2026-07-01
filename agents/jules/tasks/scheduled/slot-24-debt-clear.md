# Slot 24 — DEBT-CLEAR: Tech Debt TODO/FIXME Resolution
**Tier:** BACKLOG | **Priority:** P3 | **Interval:** Every 12h (offset :30)
**Backlog ref:** `docs/space/jules_backlog.md` → READY items: `todo.crons_manager_py_735`, `todo.tools_merge_resolver_py_184`, `todo.core_task_classifier_py_205`, `todo.crons_backup_jobs_py_41`

---

## Idempotency Scan (RUN FIRST)

```bash
# SCAN 1: Find all TODO/FIXME in target files
grep -n 'TODO\|FIXME\|HACK\|XXX' crons/manager.py crons/backup_jobs.py core/task_classifier.py 2>/dev/null | head -20

# SCAN 2: Check which READY debt items have been resolved
grep -n 'todo.crons_manager\|todo.tools_merge\|todo.core_task_class\|todo.crons_backup' docs/space/jules_backlog.md | grep -i 'DONE\|CLOSED'

# SCAN 3: Prior debt-clearing commits?
git log --oneline --all | grep -i 'debt\|todo.*fix\|fixme\|cleanup.*todo' | head -10
```

**SKIP IF:** All 4 READY debt items show status DONE in backlog.

**PARTIAL:** Fix only items not yet marked DONE.

---

## Task Execution

For each unresolved debt item, read the target file FIRST, then resolve the specific TODO/FIXME:

**`todo.crons_manager_py_735`** — Read `crons/manager.py` line ~735. Resolve the TODO comment there.
**`todo.crons_backup_jobs_py_41`** — Read `crons/backup_jobs.py` line ~41. Resolve the TODO comment there.
**`todo.core_task_classifier_py_205`** — Read `core/task_classifier.py` line ~205. Resolve the TODO comment there.
**`todo.tools_merge_resolver_py_184`** — Read `tools/merge_resolver.py` line ~184 (if exists). Resolve the TODO comment there.

**Rules:**
- Each fix must be the MINIMAL change that resolves the TODO — do not refactor surrounding code.
- Each fixed TODO must be replaced with the actual implementation OR a clear comment explaining why it is deferred (`# DEFERRED: <reason>`).
- Do NOT introduce new TODOs.

**Target files:** the specific files listed above only.

**Validation:**
```bash
for f in crons/manager.py crons/backup_jobs.py core/task_classifier.py; do
  python3 -m py_compile "$f" && echo "$f OK"
done
./guardian
```

**PR title:** `chore(debt): resolve TODO items in crons/manager, backup_jobs, task_classifier`
