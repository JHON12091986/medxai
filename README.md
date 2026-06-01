# NINA — Personal AI Assistant

NINA (Neural Intelligence & Notification Agent) is a self-hosted, Telegram-based personal AI assistant that runs on your local machine. It routes tasks intelligently across 20+ free and paid AI providers, manages your email, monitors system health, and upgrades itself — all from a single Telegram chat.

---

## Features

- **Multi-provider AI routing** — Automatically selects the best available model from Groq, Gemini, Cerebras, DeepSeek, Mistral, OpenRouter, Together, Cohere, Fireworks, xAI, SambaNova, Hyperbolic, Novita, Perplexity, OpenAI, and more
- **Rate-limit aware** — Built-in per-provider rate limit tracking (RPM, RPD, TPD) with automatic fallback
- **Telegram interface** — Fully controlled via Telegram bot; flood protection and authorized-user-only access
- **Email integration** — Reads and summarizes office email via EWS (Exchange Web Services / NTLM auth)
- **Web browsing & search** — Autonomous web search and page reading
- **Shell & file tools** — Execute shell commands, read/write files, manage workspace
- **GPU tuner** — Monitors and adjusts GPU settings dynamically
- **System health monitoring** — CPU/RAM/disk/thermal guards with configurable thresholds
- **Guardian process** — Watchdog that auto-restarts NINA on failure and logs incidents
- **Hot reload** — Reload configuration without restarting
- **Idle loop** — Background proposals and self-improvement tasks during idle time
- **Upgrade pipeline** — Structured self-upgrade system with guardian handoff

---

## Requirements

- Python 3.10+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- At least one AI provider API key (Groq free tier is enough to start)

---

## Installation

```bash
git clone https://github.com/aibony/nina.git
cd nina
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
```

---

## Configuration

All configuration is done via `.env`. Create a `.env` file in the project root:

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_USER_ID=your_telegram_user_id

# At least one AI provider
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# Optional — EWS email integration
EWS_PASSWORD=your_exchange_password
EWS_USERNAME=your_username
EWS_MY_EMAIL=your@email.com
EWS_SHARED_EMAIL=shared@email.com
```

Full list of supported environment variables: see `core/config.py`.

---

## Running NINA

```bash
# Start NINA directly
python main.py

# Start with Guardian watchdog (recommended)
./guardian
```

To run as a systemd service:

```bash
sudo cp nina.service /etc/systemd/system/
sudo systemctl enable nina
sudo systemctl start nina
```

---

## Project Structure

```
nina/
├── main.py                  # Entry point
├── guardian                 # Guardian watchdog script
├── guardian_engine.py       # Guardian logic
├── core/
│   ├── agent.py             # Main agent loop
│   ├── config.py            # NinaConfig + rate limits
│   ├── memory.py            # Memory management
│   ├── router.py            # Provider routing
│   ├── nina.py              # Core NINA class
│   ├── capabilities.py      # Capability registry
│   └── hotreload.py         # Live config reload
├── tools/
│   ├── browser.py           # Web browsing
│   ├── search.py            # Web search
│   ├── shell.py             # Shell execution
│   ├── files.py             # File operations
│   ├── system.py            # System monitoring
│   ├── gputuner.py          # GPU management
│   ├── officemail.py        # EWS email
│   └── upgradepipeline.py   # Self-upgrade system
├── interfaces/
│   ├── api.py               # REST API
│   └── telegram_interface.py# Telegram bot
├── crons/
│   ├── manager.py           # Cron job manager
│   └── backup_jobs.py       # Scheduled backups
├── dashboard/
│   └── nina-guardian.html   # Web dashboard
├── requirements.txt
└── nina.service             # systemd unit file
```

---

## Supported AI Providers

| Provider | Free Tier | Notes |
|---|---|---|
| Groq | ✅ | Fast inference, recommended default |
| Gemini | ✅ | Large context window |
| Cerebras | ✅ | High TPD allowance |
| DeepSeek | ✅ | Strong reasoning |
| Mistral | ✅ | 1 RPM on free tier |
| Together | ✅ | Many open models |
| Cohere | ✅ | Good for long context |
| Fireworks | ✅ | Fast open models |
| Perplexity | ✅ | Search-augmented |
| SambaNova | ✅ | High throughput |
| Hyperbolic | ✅ | Open model hosting |
| Novita | ✅ | Affordable inference |
| OpenRouter | ✅ | Multi-model gateway |
| xAI (Grok) | Paid | — |
| OpenAI | Paid | — |
| Pollinations | ✅ | Image generation |
| Chutes | ✅ | — |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**M. Baizid Alam** · [onlybony@gmail.com](mailto:onlybony@gmail.com) · [github.com/aibony](https://github.com/aibony)
