# Gemini CLI Flash-Speed Guide

## What this does
Five-layer performance stack that cuts Gemini CLI token usage by 60-80% per call
and achieves near-Flash latency on single-file tasks.

## Quick start

# 1. Audit what Gemini will see
nf gemini context

# 2. Generate optimized prompt + get recommended command
nf gemini prompt --task 'fix the import error in tools/local_inference.py'

# 3. Check daily quota
nf gemini status

# 4. Full auto-run (prompt + model select + quota check + exec)
nf gemini run --task 'add type hints to core/agent.py'

# 5. Dry-run to preview without executing
nf gemini run --task 'refactor core/router.py' --dry-run

## Why it's faster

| Problem | Solution | Speedup |
|---|---|---|
| Fat context (all files) | .geminiignore prunes logs/cache/venv/data | 40-70% fewer tokens |
| Bloated GEMINI.md | Rewritten to <400 bytes | ~200 tokens saved/call |
| No cache hits | Stable prefix always first | Implicit cache hit after 2nd call |
| Pro model for tiny tasks | Flash auto-selected for <4k token tasks | 2-3x faster TTFT |
| Quota blind-spending | Budget guard warns at 800/1000 req | Prevents daily exhaustion |

## Per-call token budget
Set NINA_GEMINI_TOKEN_BUDGET in .env (default: 8000 tokens per call).
Set NINA_GEMINI_WARN_AT for quota warning threshold (default: 800 requests).

## Cache hit tips (from Google API docs)
- Stable context (GEMINI.md) must be IDENTICAL and at the START of every prompt
- Send similar requests within a short time window for implicit cache hit
- nf gemini prompt ensures this automatically

## Quota fallback cascade
Gemini Flash (1000/day) → Qwen Code CLI (2000/day) → Jules (async, 100/day)
