---

# NINA Context

## Logging Shape

For NINA, logging in non-core modules (tools and crons) should include structured context to make logs easily searchable. Instead of modifying core logger configurations, we reuse existing logger instances and inject contextual fields such as `tool_name`, `job_id`, or `task_id` into the `extra` argument of the logger calls (e.g. `logger.info("message", extra={"log":"tools.log", "tool_name": "search"})`). It's also important to maintain a reasonable log volume by avoiding tight loops that log per iteration.

---

# NINA Proactive Reminder Engine

The NINA proactive reminder engine is an internal API designed to store and surface reminders, fulfilling requirement F-06.

## Architecture

The reminder engine is integrated directly into the `MemorySystem` (`core/memory.py`). It uses a simple file-based JSON persistence strategy, writing to `data/reminders.json`.

### Features
* **Storage:** Reminders are stored with a unique `id`, `text`, `due_time` (Unix timestamp), `status` (either "pending" or "done"), and `created_at`.
* **Async IO:** Persistence is handled asynchronously, offloaded to a thread using `asyncio.to_thread()`, to prevent blocking the main NINA event loop.
* **Cron Integration:** A scheduler job runs every 15 minutes to check for due reminders (`core/nina.py:run_reminder_check`). When due reminders are found, they are dispatched via the Telegram interface and marked as "done".

## Internal API Methods

The API is exposed via the NINA `MemorySystem`:

* `await nina.memory.add_reminder(text: str, due_time: float) -> str`
  Adds a new reminder and returns its unique ID.

* `await nina.memory.get_due_reminders(now: float) -> list`
  Returns a list of reminder dictionaries that are pending and whose `due_time` is less than or equal to `now`.

* `await nina.memory.mark_reminder_done(rem_id: str)`
  Updates the status of the specified reminder to "done" and persists the change.

## Future Telegram UI Wiring

In the future, Telegram UI commands (e.g., `/remind`) can be wired up by simply calling `await self.memory.add_reminder(text, due_time)` within `interfaces/telegram_interface.py` or agent actions, without needing to implement the persistence or timing logic.

---

# NINA Context
Note: Groundwork for F-07 "Email triage improvement" exists in tools/office_mail.py. This provides a clear separation of connection, fetch, and triage concerns, along with soft-failing for unconfigured EWS.
