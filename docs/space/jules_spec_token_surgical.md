📉 MEGA-TASK: Token-Surgical Architecture (v2.1)
Assignee: Jules (Async Cloud Coder)
Objective: Reduce NINA's total cloud token consumption by an additional 50% (on top of v2.0) by moving context management from "Dumb Truncation" to "Surgical Selection."

🏗️ Domain 1: Semantic Context Selection (Local-First RAG)
- nf context-map: Automatically generate a semantic map of the codebase using local models (qwen2.5:1.5b).
- nf chunk-search: Replace full-file reading with a RAG-based chunk search. Use ChromaDB locally. When an agent requests a file, nf returns only the relevant semantic chunks (e.g., "router's circuit breaker") across multiple files instead of entire large files.

🧠 Domain 2: Local Reasoning Offloading (Thinking-on-the-Edge)
- nf plan-local: Move the 7-step code scaffold reasoning (from AGENTS.md) to a local model (Ollama). The cloud agent only receives the final verified plan.
- Local Error Pre-Verification: Before the cloud agent attempts to "fix" a file, nf runs pyflakes and compile locally and provides a one-line error summary: "Fix IndentationError at line 45" instead of the whole file.

📉 Domain 3: Differential Context Injector (Git-Diff Primary)
- nf diff-context: Modify the primary agent prompt to prioritize git diff over file content. For files >500 lines, nf sends only the changed blocks + symbol outline (function signatures).
- Skeleton Outlining: Use the Python `ast` module to generate a "Skeleton" of large files. The cloud agent sees class/function signatures and docstrings but no bodies, unless specifically requested via `nf read --full`.

🛡️ Domain 4: Token-Aware Tooling (Surgical Read/Write)
- Surgical Read: Update tools/files.py to support line-range reads (`--lines 40-80`) and symbol-based reads (`--symbol HybridRouter`).
- Log Compression: Implement a sliding-window log summarizer in tools/ninaflash.py that collapses identical repeating log lines (e.g., "Heartbeat..." x 100) into a single summary line.

📡 Domain 5: NinaGate Prompt Optimization
- System Prompt Templating: Move the heavy AGENTS.md instructions into a cached system prompt in NinaGate. 
- Tool Definition Stripping: Dynamically strip unused tool definitions from the cloud agent's context based on the current task classification (e.g., remove "market" tools from a "coding" task).

📝 Acceptance Criteria for Jules:
1. Token Reduction: Demonstrate (via mocks or logs) that a standard coding task uses 30-50% fewer tokens.
2. Stability: Surgical reads must include enough context (at least 5 lines above/below) to prevent hallucination.
3. Documentation: Update nina_update_log.md for every module completed.
4. Testing: Provide unit tests for the RAG chunking and Skeleton outlining logic.

Jules, you are cleared to proceed with AG-M-02. Start with Domain 4 (Surgical Tooling) to enable the infrastructure for surgical reading.
