📡 MEGA-TASK: GATE-PROMPT System Prompt Templating (AG-M-10)
Assignee: Jules (Async Cloud Coder)
Objective: Shift instruction overhead from every turn's prompt to a cached system template in NinaGate.

🏗️ Domain 1: NinaGate Template Engine
- Update `ninagate/main.py` to support "System Templates." 
- Move the core `AGENTS.md` operating laws into a static JSON template.
- Implement a `/v1/chat/completions` wrapper that injects these templates based on a `X-NINA-ROLE` header.

🧠 Domain 2: Prompt Stripping
- Modify `nina.py` and `agent.py` to strip redundant instructions from the `AgentLoop` prompt if it detects it is running through NinaGate.

📝 Acceptance Criteria:
- Measured reduction in "Input Tokens" per turn.
- Compatibility with all BYOK tools (Aider, Cursor, etc.).
