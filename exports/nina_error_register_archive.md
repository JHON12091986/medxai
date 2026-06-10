# NINA Error Register Archive

| ID | Severity | Component | Issue (short) | Status | Assignee | Fixed In | File(s) |
|----|----------|-----------|---------------|--------|----------|----------|---------|
| config.missing_env.apisecretkey | 🔴 BLOCKER | core.config | APISECRETKEY missing or empty in .env | ✅ FIXED | unassigned | v12.2.0 | .env, core/config.py |
| config.missing_env.authorizeduserid | 🔴 BLOCKER | core.config | AUTHORIZEDUSERID missing from .env | ✅ FIXED | unassigned | v12.2.0 | .env, core/config.py |
| config.missing_env.telegrambottoken | 🔴 BLOCKER | core.config | TELEGRAMBOTTOKEN missing from .env | ✅ FIXED | unassigned | v12.2.0 | .env, core/config.py |
| cron.conflicting_id | 🔴 BLOCKER | crons.manager | APScheduler ConflictingIdError — duplicate job ID | ✅ FIXED | unassigned | R-23 | crons/manager.py |
| process.ghost_instance | 🔴 BLOCKER | process | Ghost NINA process still running | ✅ FIXED | unassigned | v12.0.0 | data/nina.pid, main.py |
| process.lock_conflict | 🔴 BLOCKER | process | BlockingIOError on nina.lock — concurrent process conflict | ✅ FIXED | unassigned | v12.0.0 | data/nina.lock, main.py |
| router.attr.forcelocal | 🔴 BLOCKER | core.router | NameError: forcelocal not defined (should be force_local) | ✅ FIXED | unassigned | R-70 | core/router.py, core/agent.py |
| router.attr.orderedproviders | 🔴 BLOCKER | core.router | HybridRouter AttributeError: ordered_providers vs _ordere... | ✅ FIXED | unassigned | R-69 | core/router.py |
| router.attr.self_http | 🔴 BLOCKER | core.router | HybridRouter AttributeError: self._http vs self.http | ✅ FIXED | unassigned | R-72 | core/router.py |
| startup.attributeError | 🔴 BLOCKER | startup | AttributeError at startup/import | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.importError | 🔴 BLOCKER | startup | ImportError or ModuleNotFoundError at startup | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.nameError | 🔴 BLOCKER | startup | NameError at startup/import | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.syntaxError | 🔴 BLOCKER | startup | SyntaxError in Python source file | ✅ FIXED | unassigned | v12.2.0 | main.py |
| startup.typeError | 🔴 BLOCKER | startup | TypeError at startup/import | ✅ FIXED | unassigned | v12.2.0 | main.py |
| capabilities.race_condition | 🟠 WARN | core.capabilities | Race condition on capabilities.json writes | ✅ FIXED | unassigned | D-22 | core/capabilities.py |
| cron.lambda_coroutine_drop | 🟠 WARN | crons.manager | APScheduler lambda returning coroutine without await | ✅ FIXED | unassigned | D-23 | crons/manager.py |
| hotreload.deleted_key_revert | 🟠 WARN | core.hotreload | Hot-reload silently ignores deleted .env keys | ✅ FIXED | unassigned | R-44 | core/hotreload.py |
| logger.duplicate_handler | 🟠 WARN | core.nina | Duplicate log handler added on every restart | ✅ FIXED | unassigned | D-21 | core/nina.py |
