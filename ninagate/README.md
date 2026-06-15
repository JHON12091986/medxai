# NinaGate

NinaGate is a tiny, always-alive OpenAI-compatible API proxy that routes requests from BYOK-capable CLI tools (Qwen Code, Aider, Cursor, etc.) through NINA's existing provider API keys in a priority cascade. It operates completely independently of `nina.service`, does not import from NINA, and requires zero dependency on NINA being active.

## Installation

```bash
pip install fastapi uvicorn httpx watchfiles python-dotenv
```

## Enable as a Service

```bash
systemctl enable --now ninagate
```

## Configuring BYOK Tools

Configure your BYOK tool (e.g. Cursor, Aider) with:
- **base_url:** `http://localhost:8080/v1`
- **api_key:** `ninagate`
- **model:** `auto` (or leave blank)

## Changing Provider Priority

Edit `providers.json` to modify the provider cascade priority. NinaGate will hot-reload the configuration instantly without needing a restart.

## Response Caching
NinaGate implements a response caching layer to store and serve previous LLM responses. This significantly reduces redundant calls to upstream providers and lowers latency.
- **Mechanism:** Cache keys are generated based on sorted payload representation, ensuring robustness across different request formats.
- **Persistence:** Cached responses are persisted to `data/router_cache.json` and survive service restarts.
- **Benefits:** Minimizes token usage and improves overall system responsiveness.
