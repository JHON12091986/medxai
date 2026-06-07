# Contributing to NINA

Welcome to the NINA (Neural Intelligence & Notification Agent) project! We appreciate your interest in contributing. This document provides the essential guidelines for developing, testing, and submitting your changes.

## General Guidelines

- **Read `AGENTS.md`**: Always read `AGENTS.md` before starting any development work. It contains the shared operating law for all agents and developers.
- **Understand Before Editing**: Read every file completely before making changes to it.
- **Workflow Protocol**: Follow the strictly enforced `verify -> log -> sync` workflow for all changes.

## Development Setup

To set up the NINA development environment locally, you must explicitly create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Lock File Protocols

NINA uses a lock file system to coordinate concurrent agent execution. Before modifying any file, you **must** interact with the lock system:

1. **Check Lock**: Check `jules_lock.txt` to ensure the files you intend to edit are not already locked. If a file is locked by another task/agent, **stop** and do not proceed.
2. **Acquire Lock**: When starting a task, update `jules_lock.txt` with your details. Assign the modified file path(s) to `LOCKED_FILES` and record the `JULES_TASK`, `JULES_PR`, and `LOCKED_SINCE` timestamp.
3. **Release Lock**: The lock file (`jules_lock.txt`) **must be cleared** after your PR is merged.

## Linting Requirements

- **PEP8**: Follow PEP8 standards for all Python code.
- **Exception Handling**: Avoid using bare `except:` or generic `except Exception:` blocks. Always use specific, typed exception handling (e.g., `OSError`, `ValueError`) to prevent swallowing critical logic errors or file parsing issues.
- **Logging**: Reuse existing logger instances and inject structured context (e.g., `tool_name`, `job_id`, `task_id`) into the `extra` argument. Avoid logging per iteration in tight loops. **Important**: Avoid using `'module'` as a key in the `extra` dictionary; use `'log_module'` instead.
- **Regex**: Use compiled regular expressions (`re.compile`) instead of Python generator expressions (e.g., `any(...)`) for string character matching in performance-critical paths.

## Testing Requirements

You must validate all changed files before committing your work.

1. **Syntax Checking**: Run `python3 -m py_compile <file>` and `pyflakes <file>` on every changed file.
2. **Helper Commands**: Alternatively, use the optional developer helper commands:
   ```bash
   make check
   make test
   ```
3. **Async Testing**: For async tests with `pytest`, ensure the `pytest-asyncio` plugin is installed. The `pytest.ini` must be configured with `asyncio_mode = auto` and `asyncio_default_fixture_loop_scope = function`. Always run tests using `python3 -m pytest` to avoid environment path issues.
4. **Test Failures**: It is acceptable to proceed with pre-existing test failures as long as your new code changes do not introduce new ones. Do not attempt to fix unrelated, out-of-scope broken tests.

## Pull Request (PR) Guidelines

When your changes are ready, follow these guidelines to open a PR:

- **Do Not Bundle**: One commit per logical fix. Never bundle unrelated changes in one commit.
- **Stage Specifically**: Strictly stage specific files only (never use `git add .`).
- **Conventional Commits**: Use conventional commits with task IDs: `fix:` | `feat:` | `docs:` | `chore:` | `ops:` followed by `(ID)`.
- **Sequential Execution**: Do not pause for confirmation; execute all tasks sequentially and open a PR when the task is done.

## Protected Files

Never modify the following protected files unless explicitly instructed:
- `.env`
- `core/router.py`
- `core/nina.py`
- `interfaces/telegram_interface.py`
- `data/memory/facts.json`
- `upgrades/guardian_baseline.json`

## Additional Project Structure Rules

- All new data files must go in the `data/` directory.
- All new tool files must go in the `tools/` directory.
- When adding new tools to the project, they must be exported in the `__all__` list of `tools/__init__.py` and registered in the `DEFAULT_CAPS` dictionary within `core/capabilities.py`.

Thank you for contributing to NINA!
