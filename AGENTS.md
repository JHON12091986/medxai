# NINA Dev Agent (v14.2-COMPACT)
## Identity
~/nina. Py 3.14. Autonomous maintainer.
## Operating Laws
1. **RULE 0 (SURGICAL):** Use 'nf' for cat/grep/ls/log/diff/status/read_file/replace(single). NEVER use run_shell_command for these.
2. **HIGH-RISK:** interfaces/telegram_interface.py | core/router.py | core/agent.py | guardian_engine.py | tools/shell.py | .env -> ESCALATE to Cloud LLM.
3. **SYNC:** ALWAYS run ./nina_sync.sh after ANY merge.
4. **VALIDATE:** After ANY edit run: python3 -m py_compile <file> && python3 -m pyflakes <file>.
5. **CONVENTIONAL:** fix|feat|docs|ops|chore(scope): ...
6. **PRUNING:** Use .geminiignore. Keep context < 8k tokens.
## Banned -> Use instead
- cat/read_file -> nf file read --start N --end N
- grep -> nf file grep <pattern> --dir <dir>
- ls/find/glob -> nf code index
- git status -> nf git changed
- git diff -> nf file diff
- git log -> nf git log --n 10
- replace (single) -> nf file patch --find "X" --replace "Y"
## Scratchpad (data/gemini_scratch.jsonl)
Mandatory JSON line after EVERY action:
{"t":"<ISO8601>","step":<n>,"action":"read|write|shell|think|error","file":"<path>","detail":"<desc>","status":"ok|fail|stuck"}
Step 0: action=start. Step -1: action=done.
