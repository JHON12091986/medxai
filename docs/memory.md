# Memory Subsystem

## Overview

The NINA memory system, orchestrated by `core/memory.py`, is the foundation of the agent's persistence, personality, and operational continuity. It prevents NINA from acting as a stateless chatbot by utilizing a dual-memory approach that merges dynamic episodic recall with a hardcoded, immutable identity anchor.

## Dual-Memory Architecture

### 1. ChromaDB (Episodic Memory)
NINA utilizes ChromaDB as a semantic, local vector store to record the "what happened when."
- **Function:** It stores previous interactions, executed tasks, resolved errors, and ambient context.
- **Recall:** By utilizing semantic similarity search, `core/memory.py` can fetch highly relevant historical context to inform NINA's current decisions.

### 2. facts.json (Identity Anchor)
Located at `data/memory/facts.json`, this is the core of NINA's persistent personality.
- **Function:** It contains hardcoded, foundational truths about NINA's identity, the user (M. Baizid Alam), the operating environment, and core directives.
- **Why it matters:** The combination of ChromaDB (episodic) and `facts.json` (identity) prevents "context drift." Even after thousands of API calls or autonomous development loops, NINA will not hallucinate a new persona or forget its primary directives, because `facts.json` grounds every context window. (Fixed in v12.3: ensured deterministic injection at the top of every prompt).

## Protection Mechanisms

The `data/memory/facts.json` file is strictly protected. It is listed in the Guardian Gate's high-risk list. NINA's agents (like Jules) are explicitly forbidden from modifying this file autonomously. Any changes to the identity anchor must be performed manually or via highly scrutinized, locally executed `ninaflash` operations.

## Context Management

### Truncation & Budgeting
To prevent Context Window Overflow and ensure reliable model performance, `core/memory.py` implements character-based truncation:
- **Budget:** The total context injected by the memory system is capped (default: 4000 characters).
- **Prioritization:** The deterministic "Personal Context" (from `facts.json`) is always preserved in full. Episodic docs from ChromaDB are truncated to fit the remaining budget, ensuring NINA never loses its identity even when history is deep.

### [NEW] Session Memory (ninaflash)
For cross-agent and cross-session continuity, ninaflash provides standardized session capture:
- `nf memory session-save --summary "TEXT"` — Appends the current session summary and git state to `data/session_memory.jsonl`.
- `nf memory inject` — Generates a formatted context block of recent sessions to be pasted at the start of a new Gemini CLI session.
- `nf memory session-recall` — Recalls the last N session summaries for quick reference.

## Recommended Enhancements

- **Short-Term Working Memory / Scratchpad:** Currently, NINA relies heavily on the full memory orchestrator. A recommended enhancement is the implementation of a volatile, short-term scratchpad layer for the `AgentLoop`. This would allow NINA to hold in-flight state or intermediate logic steps during complex, multi-stage reasoning without permanently embedding that noise into the ChromaDB vector store.
