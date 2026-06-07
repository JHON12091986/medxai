

---

# NINA Context

## Logging Shape

For NINA, logging in non-core modules (tools and crons) should include structured context to make logs easily searchable. Instead of modifying core logger configurations, we reuse existing logger instances and inject contextual fields such as `tool_name`, `job_id`, or `task_id` into the `extra` argument of the logger calls (e.g. `logger.info("message", extra={"log":"tools.log", "tool_name": "search"})`). It's also important to maintain a reasonable log volume by avoiding tight loops that log per iteration.
