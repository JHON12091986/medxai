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

## Local Model Routing for Sensitive Data

A critical feature of the HybridRouter V4 is its ability to recognize sensitive data context. If the task context flags sensitive operations—such as processing local banking parameters, personal financial data, or core identity manipulation—the router absolutely bypasses all cloud providers. It strictly routes these prompts to the local Ollama models (`qwen2.5:1.5b` or `qwen2.5:7b`) to ensure sensitive data never leaves the local machine.
