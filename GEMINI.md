---
## ⚠️ TOOL OVERRIDE MANDATE
## Source: 27-session lifetime audit | 45,700+ tool calls analyzed
## Realistic optimization target: 66% of all calls → local nf (zero tokens)

### BANNED — Never use these for the listed operations:

#### run_shell_command — BAN these sub-commands only:
| Shell sub-command        | Frequency | Use instead                              |
|--------------------------|-----------|------------------------------------------|
| cat <file>               | 72x/life  | nf file read <file> --start 0 --end 60   |
| grep / grep -r           | 213x/life | nf file grep <pattern> --dir <dir>       |
| git log                  | 355x/life | nf git log --n 10                        |
| git diff <file>          | (subset)  | nf file diff <file>                      |
| git status          | (subset)  | nf git changed                           |
| git blame                | (subset)  | nf git blame <file> --start N --end N    |
| git stash                | (subset)  | nf git stash-quick --label "desc"        |
| ls / ls -la              | (subset)  | nf code index                            |
| find . -name "*.py"      | (subset)  | nf code index                            |
| head / tail / wc -l      | (subset)  | nf file read <file> --start N --end N    |
| git log --grep           | (subset)  | nf git search <keyword>                  |

#### read_file — BAN for these patterns (80% of calls):
| Pattern                  | Frequency  | Use instead                             |
|--------------------------|------------|-----------------------------------------|
| Reading whole file       | ~5,000x    | nf file read <file> --start N --end N   |
| Finding a function       | (subset)   | nf code symbol <file> <name>            |
| Getting file outline     | (subset)   | nf code outline <file>                  |
| Reading last N log lines | (subset)   | nf log tail N                           |
| Reading update log       | (subset)   | nf log tail 5                           |

#### replace — BAN for single-string edits (90% of calls):
| Pattern                  | Use instead                                         |
|--------------------------|-----------------------------------------------------|
| Single string replace    | nf file patch <file> --find "X" --replace "Y"       |
| Insert after anchor      | nf file insert <file> --after "ANCHOR" --text "..."  |

#### grep_search — BAN always (95% replaceable):
→ nf file grep <pattern> --dir <dir> --ext .py,.md,.sh
→ nf file smart-search <query> --context 5

#### list_directory / glob — BAN for code directories:
→ nf code index  (returns structured JSON map, zero shell)

---

### ALLOWED — These native tool calls are legitimate, never ban:

#### run_shell_command KEEP list:
- python3 -m py_compile <file>     ← validation
- python3 tools/ninaflash.py ...   ← nf execution
- python3 <any script>             ← legitimate execution
- ./nina_sync.sh                   ← mandatory sync
- sudo systemctl restart/status    ← service management
- git add / git commit             ← committing changes
- git push / git pull              ← remote sync
- git checkout / git merge         ← branch ops
- ollama serve / ollama pull       ← model management
- curl http://localhost:...        ← health checks
- sudo ln -sf                      ← system symlinks
- pip install / apt install        ← package management
- mkdir / cp / mv / rm             ← filesystem ops with no nf equiv

#### write_file — KEEP for:
- Creating new files from scratch  ← no nf equivalent exists
- Writing generated content        ← no nf equivalent exists

#### replace — KEEP for:
- Multi-block or multi-line edits  ← nf file patch is single-string only
- Structural rewrites              ← use native replace

#### Always KEEP — never substitute:
- update_topic                     ← Gemini CLI internal state
- invoke_agent                     ← Jules/agy workflow
- enter_plan_mode / exit_plan_mode ← planning UI
- google_web_search                ← external lookup
- web_fetch                        ← URL fetching
- list_background_processes        ← system monitoring
- read_background_output           ← async task output

---

### COMPLIANCE RULE:
Before every tool call, run this mental check:
  1. Is this cat/grep/git-log/ls/find/head/tail? → USE nf instead
  2. Is this read_file on an existing file?       → USE nf file read
  3. Is this replace for one string?              → USE nf file patch
  4. Is this grep_search?                         → USE nf file grep

At end of every task: self-audit.
If banned tool was used when nf equivalent existed → report:
"RULE0 VIOLATION: used [tool] [N]x — should have used [nf command]"
Target per session: < 20 banned tool calls total.

### REAL IMPACT (27-session audit):
- Substitutable calls: ~30,190 of 45,700 total (66%)
- Irreplaceable calls: ~15,510 (update_topic, invoke_agent, write_file new, etc.)
- Each nf call: <1s, zero tokens, zero quota
- Each banned call avoided: ~460 tokens saved on average
---
