# AGY Prompts — Batch 5

***

### AGY-B5-01 — Wire `run()` stub in `crons/manager.py`
**Source:** `todo.crons_manager_py_735` | **Risk:** Low

> 1. Read `crons/manager.py` in full.
> 2. Find the `run()` function at the bottom (currently `pass  # TODO: wire existing logic here`).
> 3. Replace the body with a standalone async runner that creates a `_MinimalNinaOS` shim (stub methods for router, telegram, pipeline, and all `run_*` callables) and calls `TaskScheduler(nina_stub).start()` inside `asyncio.run()`. The shim only needs to prevent AttributeError — no real logic needed.
> 4. Do NOT change any other function, import, or constant in the file.
> 5. Verify: `python3 -c "from crons.manager import run; print('OK')"` prints `OK`.

***

### AGY-B5-02 — Wire `run()` stub in `crons/backup_jobs.py`
**Source:** `todo.crons_backup_jobs_py_41` | **Risk:** Low

> 1. Read `crons/backup_jobs.py` in full.
> 2. Find `run()` at the bottom (currently `pass  # TODO: wire existing logic here`).
> 3. Replace the body with `asyncio.run(_main())` where `_main()` creates a minimal `nina_stub` with a `memory.backup()` that writes an empty zip, then calls `await run_memory_backup(nina_stub)` and `await run_py_backup(nina_stub)`.
> 4. Do NOT touch `run_memory_backup`, `run_py_backup`, `BACKUP_ROOT`, `CRON_JOB`, or any import.
> 5. Verify: `python3 -c "from crons.backup_jobs import run; print('OK')"` prints `OK`.

***

### AGY-B5-03 — Convert `classify_task` from async to sync (AG-69)
**Source:** `todo.core_task_classifier_py_205` | **Risk:** Medium

> 1. Read `core/task_classifier.py` in full. Note: `classify_task` is `async def` but has zero `await` expressions — it's a sync function mislabelled.
> 2. Read `ninagate/main.py` in full — find every `await classify_task(`.
> 3. Read `core/router.py` in full — find every `await classify_task(` if present.
> 4. In `core/task_classifier.py`: change `async def classify_task` → `def classify_task`. Remove the `# TODO AG-69` comment line above it. All `return ClassifiedTask(...)` lines stay exactly as-is.
> 5. In `ninagate/main.py`: replace every `await classify_task(` with `classify_task(`. Touch nothing else.
> 6. In `core/router.py`: same — remove `await` from `classify_task` calls only if present.
> 7. Verify: `python3 -c "from core.task_classifier import classify_task; import inspect; assert not inspect.iscoroutinefunction(classify_task); print(classify_task('fix typo', []).complexity)"` prints `SIMPLE`.
> 8. Also run: `python3 -m py_compile core/task_classifier.py ninagate/main.py core/router.py` — must pass clean.

***

### AGY-B5-04 — Fix `_jules_audit_job`: `--limit` integer bug in subprocess call
**Source:** `todo.tools_merge_resolver_py_184` (re-targeted after code read) | **Risk:** Low

> 1. Read `crons/manager.py` — find `_jules_audit_job`.
> 2. Locate this line inside the function: `["gh", "pr", "list", "--state", "all", "--limit", 100, "--json", ...]`
> 3. Change the integer `100` → string `"100"`. `subprocess.run` requires all list elements to be strings; an integer causes `TypeError` at runtime when this job fires.
> 4. Do NOT change any other argument, function, or file.
> 5. Verify: `python3 -c "src=open('crons/manager.py').read(); assert '\"--limit\", 100,' not in src; assert '\"--limit\", \"100\",' in src; print('OK')"` prints `OK`.

***

### AGY-B5-05 — Add `TELEGRAM_CHAT_ID` validation to `core/config.py`
**Source:** `config.missing_env.telegramchatid` | **Risk:** Low

> 1. Read `core/config.py` in full.
> 2. Find where `TELEGRAM_BOT_TOKEN` (or equivalent) is validated/declared.
> 3. Immediately adjacent to it, add validation for `TELEGRAM_CHAT_ID`:
>    - If the file uses **Pydantic BaseSettings**: add `telegram_chat_id: str` as a required field (no default) next to the token field.
>    - If the file uses **manual env reads**: add `self.telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]` with a clear `KeyError`/`ValueError` fallback that says: `"TELEGRAM_CHAT_ID is required but not set. Add it to .env."`.
> 4. Match the exact naming convention used for `TELEGRAM_BOT_TOKEN` in the file — do not invent new patterns.
> 5. Do NOT change any other field, routing logic, or any other file. Do NOT add anything to `.env`.
> 6. Verify: unset `TELEGRAM_CHAT_ID` in env, then run `python3 -c "from core.config import Config; Config()"` — must raise an error that names `TELEGRAM_CHAT_ID`. With the var set, must succeed silently.
