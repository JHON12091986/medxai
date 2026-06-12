# NINA Dev Agent
## Identity
~/nina. Py 3.11.
## Rules
Read full|1 file/task|grep path|Atomic|NEEDS_CLARIFICATION:?
## High-Risk Files
interfaces/telegram_interface.py|core/router.py|core/agent.py|guardian_engine.py|tools/shell.py|.env
## Locked Files
tools/ninasync.py|tests/test_ninasync.py|.ninaignore|requirements.txt
## Commit format
feat|fix|docs: TASK-ID
## On failure
Log err. STUCK:?