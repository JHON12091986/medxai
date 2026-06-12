# NINA - Neural Interactive Network Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

NINA is a production-grade, autonomous AI engineering agent—not a conversational chatbot. She manages her own development lifecycle, from goal ingestion and architecture design to parallel PR resolution and repository governance.

## System Architecture

NINA orchestrates both local and cloud-based intelligence through a unified routing layer.

```text
+-----------+      +----------------+      +------------------+
| Telegram  | ---> | Router (NINA)  | ---> | NinaGate (Proxy) |
+-----------+      +----------------+      +------------------+
                           |                        |
                           |                        +--> [Local] NinaFlash (qwen2.5-coder)
                           |                        +--> [Cloud] Jules VM (x15 Parallel)
                           v
                   +-------------------+
                   | Guardian AST Scan |
                   +-------------------+
```

### Key Capabilities
- **Jules-Telegram Bridge:** NINA monitors 15 concurrent Google Jules cloud sessions and automatically forwards clarifying questions to your Telegram. Reply from your phone to unblock cloud compute.
- **Smart Routing:** NinaGate intercepts LLM calls, seamlessly falling back to local `qwen2.5-coder` inference for mechanical tasks to preserve cloud API quotas.
- **Guardian AST Scanner:** A strict forensic parser that blocks dangerous code (like `shell=True`) from ever merging.
- **3-Minute Autonomous Evolution:** NINA runs an orchestrator cycle every 3 minutes to auto-merge PRs, resolve conflicts, enforce index-based documentation updates, and self-optimize.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aibony/nina.git
   cd nina
   ```
2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Add your API keys and Telegram credentials
   ```
3. **Install as a Systemd Service:**
   ```bash
   sudo systemctl enable --now $(pwd)/nina.service
   ```
4. **Synchronize Workspace:**
   ```bash
   ./nina_sync.sh
   ```

## Tech Stack

| Component | Technology | Role |
|:---|:---|:---|
| **Core Engine** | Python 3.14 | Agent loop, orchestration, routing, memory |
| **Automation** | Playwright | Headless browser execution and interaction |
| **Interface** | Telegram Bot API | Remote command & control via mobile |
| **Cloud Intelligence**| Jules API | 15-node parallel task execution |
| **Local Intelligence**| Ollama / qwen2.5 | Token-free mechanical parsing and scaffolding |
| **Version Control** | GitHub API | PR creation, resolution, and merging |

For a deep dive into NINA's internal state machine, governance index, and sub-systems, read our [ARCHITECTURE.md](ARCHITECTURE.md).
