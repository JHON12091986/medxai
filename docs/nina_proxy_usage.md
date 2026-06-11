# NINA Proxy & Gemini CLI Integration Guide

The NINA proxy provides an OpenAI-compatible FastAPI endpoint that routes your local IDE's AI requests through NINA's `HybridRouter`. This allows you to use your preferred BYOK model stack while leveraging NINA's fallback, health tracking, and model discovery logic.

## Non-Blocking Async Pipeline (v3.0)

NinaGate uses an asynchronous parallel pipeline. Every inbound request triggers a cloud connection immediately. In parallel, a local classification determines if the task is a simple/mechanical change. If classified as simple, the cloud request is cleanly cancelled and the response is generated locally via NinaFlash, saving token quotas without blocking or introducing double-hop latency.

## Bypass / Session Modes

To avoid proxy overhead entirely during interactive sessions with the Gemini CLI, use the environment-level toggle standard:

```bash
# FAST MODE — direct cloud, no proxy (use during active Gemini CLI sessions)
unset GOOGLE_GEMINI_BASE_URL

# ECONOMY MODE — route through NinaGate (use for Jules, agy batch tasks)
export GOOGLE_GEMINI_BASE_URL="http://localhost:8080/genai"
```

## Gemini CLI Extension (MCP)

NINA includes a native extension for Gemini CLI located at `.gemini/extensions/nina/`. When Gemini CLI starts, it automatically recognizes NINA's environment and loads specialized utilities.

### Custom Slash Commands
You can run NINA actions directly inside your Gemini CLI session:
- `/nf <args>` — Executes a `ninaflash` command line tool directly.
- `/status` — Displays the real-time status of `nina.service` along with the latest proxy logs.
- `/sync` — Triggers `./nina_sync.sh` post-task automation instantly.
