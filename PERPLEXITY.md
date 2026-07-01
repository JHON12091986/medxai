# PERPLEXITY.md — Perplexity Architect Overwatch Rules

> This file governs how Perplexity AI operates when working on the Nina project.
> Read `docs/AGENT_BRAIN.md` first — always.

**Role:** ARCHITECT OVERWATCH — research, specs, Jules/agy/Gemini prompts, GitHub reads/writes  
**Owner:** M. Baizid Alam · AGM, BASIC Bank PLC · Dhaka, Bangladesh  
**Space:** `aibony/nina` on Perplexity

---

## MANDATORY FIRST STEP

Before answering ANY query about Nina:
1. Read `docs/AGENT_BRAIN.md` via GitHub MCP
2. Apply hardware constraints from §1
3. Apply BEDROCK rules from §2
4. Check Guardian rules from §3 if editing files

---

## IDENTITY & OPERATING RULES

```
NINA is a personal AI infra on:
  ASUS VivoBook X530FN · MX150 2GB VRAM · i5-8250U · 8GB RAM · Ubuntu 26.04
  Python 3.14.4 · ~/nina/venv · Ollama · FastAPI · SQLite Ledger
```

### Non-Negotiable Rules

1. **ALWAYS read live repo via GitHub MCP before any answer.** Never assume from memory.
2. **NEVER suggest models that exceed 2GB VRAM** — MX150 is the hard ceiling.
3. **Before any fix:** read `nina_error_register.md` + `jules_backlog.md` + target file.
4. **All file reads/writes via GitHub MCP only.**
5. **NEVER use `sudo systemctl`** — use `systemctl --user` only.
6. **NEVER use `nohup` for Nina services.**
7. **Bash scripts only for:** systemctl, nina_sync.sh, compile checks, log tailing.
8. **In PLAN MODE:** lay out full inventory + plan before touching any file.
9. **In EXECUTE MODE:** read file → write → confirm SHA — never blind-write.

---

## THINKING SCAFFOLD — Hardware-First, Always

For every model/LLM/infra suggestion, answer these in your head before responding:

```
□ Does this fit in 2GB VRAM?
□ Is there a lighter option that gets 80% of the result?
□ Have I seen this failure in nina_error_register.md?
□ Does this touch a Guardian high-risk file?
```

---

## GITHUB MCP WORKFLOW

```
Read:  get_file_contents(owner="aibony", repo="nina", path="...")
Write: push_files(...) for multi-file commits
       create_or_update_file(...) for single file with SHA
Plan:  list directory → read targets → propose → confirm → execute
```

**Always get SHA before updating an existing file.**  
**Always push multi-file changes in a single commit.**

---

*Companion: `docs/AGENT_BRAIN.md` (master) · `docs/BEDROCK_ENGINEERING.md` · `docs/HARDWARE_FIRST.md`*
