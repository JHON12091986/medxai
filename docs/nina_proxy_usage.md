# NINA Proxy Usage Guide

The NINA proxy provides an OpenAI-compatible FastAPI endpoint that routes your local IDE's AI requests through NINA's `HybridRouter`. This allows you to use your preferred BYOK model stack while leveraging NINA's fallback, health tracking, and model discovery logic.

## How to start

To manually start the proxy:

```bash
python3 tools/nina_proxy.py
```

By default, the proxy runs on `http://127.0.0.1:8080`.

## How to add as a systemd service

You can run `nina_proxy` alongside the main `nina.service`. Here is a unit file snippet (`/etc/systemd/system/nina_proxy.service`):

```ini
[Unit]
Description=NINA Proxy Service
After=network.target nina.service

[Service]
Type=simple
User=aibony
WorkingDirectory=/home/aibony/nina
ExecStart=/home/aibony/nina/venv/bin/python tools/nina_proxy.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Reload and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nina_proxy.service
```

## Setup Guides

### Cursor Setup
- **Base URL**: `http://localhost:8080/v1`
- **API Key**: `any-string` (Authentication is not validated for localhost connections)
- **Model Name**: `nina-auto` (Type it into the box and press Add Model)

### Continue.dev Setup
In your `~/.continue/config.json`, add the local NINA proxy to your models array:

```json
{
  "models": [
    {
      "title": "NINA Auto",
      "provider": "openai",
      "model": "nina-auto",
      "apiBase": "http://localhost:8080/v1",
      "apiKey": "nina"
    }
  ]
}
```

### aider Setup
Run Aider via the command line, pointing to the proxy:

```bash
aider --openai-api-base http://localhost:8080/v1 --openai-api-key nina --model nina-auto
```

### LM Studio Compatibility
**Compatible:** Yes
Any application that allows for an **OpenAI base URL override** will work with NINA proxy. Just set the URL to `http://localhost:8080/v1` and ensure the model string is `nina-auto`.
