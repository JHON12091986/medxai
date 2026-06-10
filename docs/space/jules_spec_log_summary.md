📉 MEGA-TASK: NF-LOG Sliding Window Summarizer (AG-M-11)
Assignee: Jules (Async Cloud Coder)
Objective: Prevent context overflow from noisy logs and long markdown files.

🏗️ Domain 1: Log Compression
- nf log summarize: Use a local tiny-model (via NinaGate) or regex patterns to collapse repeating log patterns.
- Implement a sliding window for `nina_update_log.md` where the agent only sees the "Relevant Window" (last 10 entries + task-specific entries).

🧠 Domain 2: Tool Log Rotation
- nf ops rotate-logs: Automatically compress and archive `logs/*.log` into `logs/archive/` using gzip.

📝 Acceptance Criteria:
- Log summarization must preserve all Entry IDs and Dates.
- Integration with `compact_exporter.py` to ensure `nina_latest.md` stays under 64KB.
