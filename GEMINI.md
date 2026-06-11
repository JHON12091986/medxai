---
## ⚠️ TOOL OVERRIDE MANDATE — MANDATORY BEFORE EVERY TOOL CALL
## Based on 27-session real usage audit: 45,700+ replaceable cloud calls identified.
## Target: reduce run_shell_command from 33,000 lifetime calls to near zero.

### BANNED — Never call these directly:

| Banned Tool         | Calls/session avg | Replace With                          |
|---------------------|-------------------|---------------------------------------|
| run_shell_command   | ~1,200x           | See shell dispatch table below        |
| read_file           | ~185x             | nf file read <f> --start N --end N    |
| write_file          | ~55x              | nf file patch / nf file insert        |
| replace             | ~185x             | nf file patch --find X --replace Y    |
| grep_search         | ~44x              | nf file grep <pattern> --dir <dir>    |
| list_directory      | ~18x              | nf code index                         |
| glob                | ~2x               | nf code index                         |

### SHELL DISPATCH TABLE — run_shell_command sub-commands:

| Shell command used  | Frequency | Use instead                           |
|---------------------|-----------|---------------------------------------|
| grep -r / grep      | 213x      | nf file grep <pattern> --dir <dir>    |
| git log             | 355x*     | nf git log --n 10                     |
| git diff            | (subset)  | nf file diff <file>                   |
| git status          | (subset)  | nf git changed                        |
| git blame           | (subset)  | nf git blame <file>                   |
| git stash           | (subset)  | nf git stash-quick                    |
| cat <file>          | 72x       | nf file read <file> --start 0 --end 60|
| ls / ls -la         | (subset)  | nf code index                         |
| python3 -m py_compile| 154x     | nf check code <file> ✅ KEEP          |
| python3 tools/nina* | (subset)  | KEEP — legitimate execution           |
| ./nina_sync.sh      | (subset)  | KEEP — mandatory sync                 |
| systemctl restart   | (subset)  | KEEP — service management             |
| sudo ln -sf         | (subset)  | KEEP — system ops                     |

### ALLOWED — these shell calls are legitimate:
- python3 -m py_compile <file>  ← validation
- python3 tools/ninaflash.py    ← nf execution itself
- ./nina_sync.sh                ← mandatory sync
- sudo systemctl                ← service ops
- git add / git commit / git push ← commits only
- ollama / curl (health checks) ← infra checks

### COMPLIANCE RULE:
Before ANY tool call, ask: "Is there an nf command for this?"
If yes → use nf. No exceptions.
If nf returns empty/error → fallback to shell, log as RULE0_FALLBACK.
At end of every task: count native shell/read_file calls.
If count > 5 for a full task → self-report: "RULE0 VIOLATION: X unnecessary cloud calls"

### WHY THIS MATTERS (real numbers):
- 33,000 run_shell_command calls × avg 460 tokens = 15.2M tokens wasted to date
- At Gemini Flash rates: ~$1.14 in pure tool overhead
- With nf replacement: same work costs ~0 tokens locally
- Each nf call: <1 second, zero quota, zero cost
---
