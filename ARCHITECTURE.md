# NINA Architecture

## Overview
A high-level blueprint of the NINA ecosystem, detailing the interactions between the strategic, cloud-based, and local execution layers.

## Purpose
To define the structural boundaries, security protocols, and optimization strategies that ensure NINA remains stable, secure, and cost-effective during autonomous expansion.

## Usage
Consult this document when designing new core modules or agents to ensure they align with the three-tier agent model and the Prime Directive.

## System Overview

NINA is a three-tier autonomous agentic OS. It is not a chatbot. It is an action-first system that relies on a multi-layered approach involving a strategic Architect, an asynchronous Cloud Coder, and a dedicated Local Executor for maximum local security and robust performance.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    NINA Ecosystem                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Perplexity  │    │    Jules     │    │   ninaflash    │  │
│  │  Enterprise  │    │  (Cloud VM)  │    │(Antigravity) │  │
│  │    Pro       │    │Gemini 3.1 Pro│    │Gemini Flash  │  │
│  │              │    │              │    │              │  │
│  │  ARCHITECT   │    │ASYNC BUILDER │    │LOCAL MUSCLE  │  │
│  │  + OVERWATCH │    │              │    │              │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │ specs             │ PRs               │ merges   │
│         │                  ▼                   │          │
│         │           ┌──────────────┐           │          │
│         │           │   GitHub     │◄──────────┘          │
│         │           │  (PR Gate)   │                      │
│         │           └──────┬───────┘                      │
│         │                  │ merged                       │
│         │                  ▼                              │
│         │         ┌────────────────┐                      │
│         └────────►│  NINA (Live)   │                      │
│          review   │  systemd svc   │                      │
│                   └────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Deep-Dives

**ninaflash (nf):**
The "Local Muscle" of NINA. A high-performance CLI executor (v6.0+) that offloads research, validation, and project management from the cloud. It features a "Surgical Code Intelligence" engine that uses local AST parsing to extract function signatures and symbols, avoiding expensive full-file reads. ninaflash maintains a strict 100-function core Nucleus to ensure high "attention" and reliability during autonomous execution.

**NinaGate:**
A lightweight OpenAI-compatible API proxy (`ninagate/main.py`) running on port 8765. It implements a "Fast-Path" routing strategy, directing boilerplate and low-complexity reasoning to local Ollama models (Qwen2.5-Coder, DeepSeek-Coder). It features a **Live Quota Tracker** that automatically monitors Gemini Flash usage and downgrades to local models when limits (>900 req/day) are reached, resetting at 1PM BD daily. NinaGate manages a priority cascade across 19+ providers, ensuring NINA always has a path to a model even during high-latency or rate-limit events.

**Token-Surgical Architecture (v2.1):**
A cross-cutting optimization layer designed to reduce cloud token consumption by 50-90%. It utilizes:
- **Local RAG:** Semantic chunk-searching via ChromaDB to provide precise context.
- **Reasoning Offloading:** Moving the 7-step planning scaffold to local models.
- **Differential Context:** Prioritizing git diffs and symbol skeletons over full file contents in cloud prompts.
- **Cached Templating:** Moving project-wide instructions (AGENTS.md) into NinaGate's system prompt cache.

**HybridRouter V4:**
NINA's model routing engine located in `core/router.py`. It intelligently routes queries across 19+ cloud AI providers and local Ollama instances based on a weighted scoring mechanism (success rate × latency × rate limits). The router integrates a CircuitBreaker to prevent cascading failures when a provider drops, prioritizing free-tier options first while safeguarding performance.

**AgentLoop (THINK-PLAN-ACT):**
The core processing loop that transforms intent into execution. It runs continuously, receiving input (e.g., from Telegram) and breaking tasks down using a THINK-PLAN-ACT cadence. It ensures state is maintained during complex tasks and provides a thermal guard to prevent runaway loops or resource exhaustion.

**Guardian Gate:**
The forensic safety layer for autonomous self-patching. Residing in `guardian_engine.py` and `guardian` script, it runs AST scans and baseline drift analysis on every patch applied. It ensures no code runs without py_compile and pyflakes validation, logging all updates locally to provide safety, accountability, and preventing agent conflicts via file locking.

**Memory System:**
NINA's dual-tier memory orchestrator. It uses ChromaDB as a semantic vector store for episodic recall of past events, enabling NINA to "remember" history. It also relies on a hardcoded, unmodifiable `facts.json` to anchor NINA's identity and core knowledge, preventing long-term context drift or personality alteration.

## Data Flow

A typical operation begins when a command is received via Telegram. It passes through the `telegram_interface.py` which acts as the authenticated gateway. The request enters the `AgentLoop`, which synthesizes intent and coordinates action. The loop utilizes the `HybridRouter` to select an appropriate LLM provider for the reasoning. The generated response/action is executed—often utilizing local op-codes if handled by ninaflash—and the result is returned back through the interface to the user.

## Safety Architecture

NINA relies on multiple safeguards to ensure security:
- **Guardian Gate:** Checks logic against an immutable baseline.
- **jules_lock.txt:** Prevents concurrent access issues between Jules and ninaflash.
- **Shell Allowlist:** Prevents arbitrary and dangerous command execution.
- **Local-only Routing:** Ensures highly sensitive pathways, such as banking operations, always remain locally processed and never touch cloud providers.

## Deployment Architecture

NINA runs as a persistently managed background service via `systemd` (`nina.service` and `nina-dashboard.service`). It heavily relies on local Ollama models for localized processing capability to maintain uptime during connectivity outages or rate-limit saturation. The workflow leverages a strictly isolated worktree branching strategy, allowing autonomous agents to operate parallelly without destabilizing the primary `main` branch.

## THE OPTIMIZATION OFFENSIVE (v14.0 - NINA-OPT-001)
NINA prioritizes local hardware. Every subtask is routed through the **NinaGate** classification tree.
1. **Local-First:** NinaFlash (Qwen-2.5-Coder:7B) handles mechanical tasks and small edits for $0.
2. **Surgical Retrieval:** Files >100 lines are surgically retrieved via AST (Abstract Syntax Tree) primitives in `ninaflash`.
3. **Unified Directive:** A single source of truth (`AGENTS.md`) governs all coders, ensuring zero context drift.
