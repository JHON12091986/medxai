# HybridRouter V4 Subsystem

## Overview

Located in `core/router.py`, the HybridRouter V4 is NINA's sophisticated model routing engine. NINA is not bound to a single LLM provider; instead, it leverages this router to dynamically select the optimal provider for every task, ensuring high availability, minimizing costs, and respecting API rate limits.

## Supported Providers

The router maintains connections to 19+ cloud providers and 2 local model variants:
- **Cloud Providers:** Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, Pollinations, Chutes, and more.
- **Local Models (via Ollama):**
  - `qwen2.5:1.5b` (For rapid, lightweight parsing and fast tasks)
  - `qwen2.5:7b` (For heavy reasoning and complex logic parsing)

## Routing Algorithm

HybridRouter V4 does not just pick a model at random; it employs a weighted scoring algorithm to determine the absolute best route for the current prompt. The scoring mechanism calculates the viability of a provider using the formula:
**`Success Rate × Latency × Rate Limits`**

This ensures that NINA routes heavily toward providers that are currently fast, reliable, and well below their quota limits.

## Live Quota Tracker (v14.0)

NinaGate features a **Live Quota Tracker** to protect cloud API limits and automate routing shifts:
- **Monitoring:** Tracks total requests per provider (e.g., Gemini Flash).
- **Auto-Downgrade:** When a limit (e.g., 900 req/day) is approached, NinaGate automatically skips that provider and routes to local NinaFlash (Ollama) or next-tier cloud models.
- **Daily Reset:** Quotas reset automatically at **1 PM BD** (Midnight PT), ensuring continuous operation without manual intervention.

## CircuitBreaker Pattern

To prevent NINA from hanging or cascading into total failure when a specific provider experiences an outage, HybridRouter V4 implements a strict CircuitBreaker pattern. If a provider fails multiple times in rapid succession, the CircuitBreaker trips, temporarily removing that provider from the active pool. The router will automatically fallback to the next highest-scoring provider, ensuring seamless user experience.

## Free-Tier Priority

NINA operates on a strict "free-tier first" philosophy. The router is explicitly configured to exhaust the quotas of high-quality free API tiers (like Groq, Together, or Gemini's free tiers) before gracefully degrading or shifting to paid APIs. This prevents runaway API costs during autonomous self-development loops.

## Rate Limit Tracking

The router rigorously tracks usage statistics internally to avoid HTTP 429 (Too Many Requests) errors. It monitors:
- **RPM:** Requests Per Minute
- **RPD:** Requests Per Day
- **TPD:** Tokens Per Day

If an impending rate limit is detected for the top-priority provider, the router preemptively shifts the load to the next available provider.

## Response Caching

To further minimize token usage and latency, HybridRouter V4 includes a persistent response caching layer.
- **Deduplication:** Identical prompts (including recent message history) are hashed and checked against the cache before any provider call is made.
- **Persistence:** Unlike standard in-memory caches, NINA's cache is persisted to `data/router_cache.json`. This ensures that cached responses survive service restarts and system reboots.
- **TTL Management:** Cache entries have specific Time-To-Live (TTL) values based on task type (e.g., `coding` tasks may be cached for 6 hours, while `quick` tasks are cached for 1 hour). Sensitive tasks are never cached.
- **Automatic Purging:** The cache periodically purges expired entries during idle periods to maintain a lean storage footprint.

## Performance Telemetry (v14.0)

Every routing decision and completion is logged to `logs/ninagate.log` in JSON format. This log includes:
- **provider**: The model provider used (local or cloud).
- **input_tokens / output_tokens**: Consumed token counts.
- **total_ms**: Round-trip latency.
- **cached**: Boolean indicating if the response was served from the cache.

This data is used by `nf monitor` to provide real-time efficiency reports.
