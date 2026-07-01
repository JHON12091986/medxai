# opencode/

NINA's **autonomous code editing interface** — OpenCode CLI wired through NinaGate, NinaMCP, and the full Nina capability stack.

---

## How It Works

```
Nina (Telegram / Perplexity)
        │
        ▼
 opencode/tools/opencode_tool.py
        │  dispatch(task)
        ▼
 opencode run "<task>"          ← subprocess in ~/nina
        │
        ▼
 NinaGate (localhost:8080)      ← OpenAI-compatible proxy
        │  routes to Devstral / cloud cascade
        ▼
 OpenCode agent executes        ← reads files, runs git, edits code
        │
        ▼
 runtime/logs/opencode/         ← output captured here
        │
        ▼
 Returns {success, output, error, duration_s} to caller
```

OpenCode calls `http://localhost:8080` — NinaGate's OpenAI-compatible endpoint — and automatically gets the full HybridRouter V4 routing stack (circuit breaker, quota management, 19-provider cascade).

---

## Structure

```
opencode/
├── README.md              ← this file
├── tools/
│   ├── opencode_tool.py   ← Nina dispatcher: calls opencode run
│   └── __init__.py
├── tasks/
│   └── TASK_TEMPLATE.md   ← task spec format
├── prompts/
│   └── system_prompt.md   ← full Nina context injected into OpenCode
└── logs/                  ← symlink → runtime/logs/opencode/
```

---

## Configuration

**Project-level** (`~/nina/opencode.json`):
- MCP: NinaMCP tools wired in
- Write-deny rules: protects critical files
- Provider: `http://localhost:8080` (NinaGate)

**Global** (`~/.config/opencode/config.json`):
```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "MISTRAL/devstral-latest",
  "autoshare": false
}
```

---

## Usage

### Direct CLI
```bash
cd ~/nina
opencode run "<task description>"
```

### Via Nina dispatcher
```python
from opencode.tools.opencode_tool import dispatch
result = dispatch("add docstrings to core/router.py")
print(result['output'])
```

### Via Telegram
```
opencode: implement memory_indexer.py
```

---

## Task Spec Format

See `tasks/TASK_TEMPLATE.md`. Tasks should include:
- **Goal** — one sentence
- **Files to touch** — explicit list
- **Files NOT to touch** — from juleslock + critical list
- **Acceptance criteria** — verifiable

---

## Logs

All OpenCode run output goes to `runtime/logs/opencode/last_run.log`.

```bash
cat runtime/logs/opencode/last_run.log
# or tail live:
tail -f runtime/logs/opencode/last_run.log
```

---

*Part of NINA v14.4+ — OpenCode replaces aider as the primary autonomous local code editor.*
