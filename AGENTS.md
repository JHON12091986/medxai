# NINA Agent Context — Prime Directive (v14.0)

## 1. Goal: Maximum Throughput & Zero-Token Logic
NINA is an autonomous engineering system. Every action must prioritize local hardware utilization over cloud API consumption. If a task can be done by a script, do not do it with your "brain."

## 2. Token-Surgical Protocols (Mandatory)
- **Zero-Turn Context:** Use `nf status --pulse` and `nf task active` on Turn 1 to understand repo state without reading full files.
- **Surgical Retrieval:** NEVER `read_file` on files >100 lines. Use:
  - `nf code symbol --file <f> --name <n>` to extract exact logic.
  - `nf code sigs --dir <d>` to see directory outlines.
  - `grep_search` with strict context limits.
- **Log Management:** Never read the entire `nina_update_log.md`. Use `nf log tail` to find the last entry ID.

## 3. Maintenance & CPU Offloading
Repetitive workflows must be offloaded to the local CPU via `ninaflash` (nf):
- **PR Merging:** Use `nf maintain pr <pr_id> --task <id> --title <t> --summary <s>`.
- **Conflict Resolution:** `ninaflash` contains local logic to pre-resolve documentation regressions and re-apply v13+ headers automatically.
- **Verification:** Use `nf check code <file>` and `nf hw gate` for zero-token quality and safety checks.

## 4. NinaGate & Prompt Engineering
- **Context Injection:** Trust the system prompts provided by NinaGate; they contain compressed pulse data.
- **Local Routing:** Small tasks (formatting, simple tests) should be routed to **Local Ollama** (Qwen-2.5-Coder) via NinaGate to save tokens for high-level reasoning.

## 5. Tool Routing Matrix
| Tool | Core Strength | Optimization Role |
| :--- | :--- | :--- |
| **Perplexity** | Planning & Specs | Offloads research turns. |
| **Gemini CLI** | Surgical Implementation | Heavy reasoning, complex refactors. |
| **ninaflash** | Kernel Automation | **Token reduction**, CPU offloading. |
| **NinaGate** | Proxy & Gatekeeper | Context caching & local routing. |
| **Local CPU** | Text & AST Processing | Surgical retrieval & conflict resolution. |

## 6. Pre-Code Reasoning Scaffold
1. RESTATE task + OPTIMIZATION PATH (e.g. "Merging PR #X using nf maintain").
2. LOCATE patterns locally (`nf code symbol`).
3. HARDWARE CHECK (`nf hw gate`).
4. ACTION: Call the most automated tool available.
5. SELF-CHECK & LOG.
