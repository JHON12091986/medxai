# NINA Logbase Backup
Generated: 2026-06-29 22:33:50

## Directory Tree
```
No logs directory
```

## File Contents
### logs/agent.log
Last modified: 2026-06-25 15:09:35
Size: 0 bytes
```log
```

### logs/agent.log.2026-06-12
Last modified: 2026-06-25 15:43:04
Size: 901 bytes
```log
2026-06-12 09:31:20,348 [DEBUG] nina.agent: agent input received: 'hi'
2026-06-12 09:31:21,055 [INFO] nina.agent: agent_step step=1 task=general response="Since we just started, my scratchpad is empty. I'll wait for further instruction"
2026-06-12 09:31:23,363 [INFO] nina.agent: agent_step step=2 task=general response="My scratchpad remains empty as no information has been added yet. I'm ready for "
2026-06-12 09:31:25,672 [INFO] nina.agent: agent_step step=3 task=general response="Still no information has been added to my scratchpad. I'll continue to wait for "
2026-06-12 09:31:28,008 [INFO] nina.agent: agent_step step=4 task=general response='My scratchpad remains empty. It seems we are approaching the final step, but I s'
2026-06-12 09:31:30,690 [INFO] nina.agent: agent_step step=5 task=general response='Since no information was provided throughout the steps, my scratchpad remains em'
```

### logs/agent.log.2026-06-23
Last modified: 2026-06-25 15:43:04
Size: 2510 bytes
```log
2026-06-23 00:35:04,988 [DEBUG] nina.agent: agent input received: 'hi'
2026-06-23 00:35:07,465 [DEBUG] nina.agent: knowledge_graph_query_failed: 'KnowledgeGraph' object has no attribute 'query'
2026-06-23 00:35:07,466 [WARNING] nina.agent: goal_manager_context_failed: 'GoalManager' object has no attribute 'register'
2026-06-23 00:35:15,861 [DEBUG] nina.agent: agent input received: 'how are you'
2026-06-23 00:35:18,405 [DEBUG] nina.agent: knowledge_graph_query_failed: 'KnowledgeGraph' object has no attribute 'query'
2026-06-23 00:35:18,405 [WARNING] nina.agent: goal_manager_context_failed: 'GoalManager' object has no attribute 'register'
2026-06-23 00:35:35,673 [DEBUG] nina.agent: agent input received: 'why are you so slow !'
2026-06-23 00:35:55,819 [WARNING] nina.agent: agent_loop_timeout goal='hi' exceeded=300s
2026-06-23 00:35:55,903 [DEBUG] nina.agent: knowledge_graph_query_failed: 'KnowledgeGraph' object has no attribute 'query'
2026-06-23 00:35:55,903 [WARNING] nina.agent: goal_manager_context_failed: 'GoalManager' object has no attribute 'register'
2026-06-23 00:35:55,904 [INFO] nina.agent: tool_first_reflex: suggesting tool=shell before generation
2026-06-23 00:36:03,414 [WARNING] nina.agent: agent_loop_timeout goal='how are you' exceeded=300s
2026-06-23 00:36:40,914 [WARNING] nina.agent: agent_loop_timeout goal='why are you so slow !' exceeded=300s
2026-06-23 00:43:53,814 [DEBUG] nina.agent: agent input received: 'hi'
2026-06-23 00:43:56,402 [DEBUG] nina.agent: knowledge_graph_query_failed: 'KnowledgeGraph' object has no attribute 'query'
2026-06-23 00:43:56,402 [WARNING] nina.agent: goal_manager_context_failed: 'GoalManager' object has no attribute 'register'
2026-06-23 00:44:03,187 [DEBUG] nina.agent: agent input received: 'how are you'
2026-06-23 00:44:03,248 [WARNING] nina.agent: thermal_warn CPU=81 GPU=59
2026-06-23 00:44:16,461 [DEBUG] nina.agent: knowledge_graph_query_failed: 'KnowledgeGraph' object has no attribute 'query'
2026-06-23 00:44:16,461 [WARNING] nina.agent: goal_manager_context_failed: 'GoalManager' object has no attribute 'register'
2026-06-23 00:44:26,002 [DEBUG] nina.agent: agent input received: 'whats up'
2026-06-23 00:44:42,077 [WARNING] nina.agent: agent_loop_timeout goal='hi' exceeded=300s
2026-06-23 00:44:42,183 [DEBUG] nina.agent: knowledge_graph_query_failed: 'KnowledgeGraph' object has no attribute 'query'
2026-06-23 00:44:42,184 [WARNING] nina.agent: goal_manager_context_failed: 'GoalManager' object has no attribute 'register'
```

### logs/dead_code_report.txt
Last modified: 2026-06-29 22:27:50
Size: 5006 bytes
```log
tools/semantic_dedup.py:11: invalid syntax at "<<<<<<< Updated upstream"
scripts/dedup_scanner.py:1: unexpected character after line continuation character at """"\nscripts/dedup_scanner.py\nNINA Deduplication Scanner — hashes function bodies + prompt strings\nacross all agents and scripts. Flags duplicates → appends to jules_backlog.md.\n\nRun: python scripts/dedup_scanner.py\nAlso called by git-hooks/post-commit (idempotent).\n"""\n\nfrom __future__ import annotations\nimport ast, hashlib, json, re\nfrom collections import defaultdict\nfrom datetime import datetime\nfrom pathlib import Path\n\nROOT = Path(__file__).parent.parent\nBACKLOG = ROOT / "jules_backlog.md"\nREPORT = ROOT / "data" / "dedup_report.json"\nREPORT.parent.mkdir(parents=True, exist_ok=True)\n\nSKIP_DIRS = {".git", ".venv", "venv", "env", "__pycache__", "backups", "archive"}\n\nPROMPT_RE = re.compile(\n    r'(?:SYSTEM_PROMPT|PROMPT|prompt|system_prompt)\\s*=\\s*["\'\']{1,3}(.*?)["\'\']{1,3}',\n    re.DOTALL,\n)\n\n\ndef hash_body(body: str) -> str:\n    clean = re.sub(r"\\s+", " ", body.strip())\n    return hashlib.sha256(clean.encode()).hexdigest()[:12]\n\n\ndef extr"
scripts/build_example_bank.py:1: unexpected character after line continuation character at """"\nscripts/build_example_bank.py\nNINA Example Bank — dynamic few-shot retrieval by semantic similarity.\nRun: python scripts/build_example_bank.py\n"""\n\nfrom __future__ import annotations\nimport json, pickle\nfrom pathlib import Path\n\nROOT = Path(__file__).parent.parent\nBANK_DIR = ROOT / "data" / "example_bank"\nBANK_DIR.mkdir(parents=True, exist_ok=True)\nINDEX_FILE = BANK_DIR / "index.json"\nEMB_FILE = BANK_DIR / "embeddings.pkl"\n\nSEED_EXAMPLES = [\n    {"id": "ex_001", "query": "handle telegram /start command", "response": "Use CommandHandler('start', start_handler) in your bot dispatcher.", "tags": ["telegram", "bot", "command"]},\n    {"id": "ex_002", "query": "cache LLM response", "response": "from core.memo_cache import get_cached, set_cached, cache_key\nkey = cache_key(prompt)\nresult = get_cached(key) or (call_llm(prompt), set_cached(key, result))[0]", "tags": ["cache", "llm", "memo"]},\n    {"id": "ex_003", "query": "count tokens before API call", "response": "f"
scripts/delta_updater.py:1: unexpected character after line continuation character at """"\nscripts/delta_updater.py\nNINA Delta Updater — git diff --name-only → only rebuild SSOT for\nchanged files. Eliminates full-rebuild cost on every commit.\n\nRun: python scripts/delta_updater.py\n"""\n\nfrom __future__ import annotations\nimport hashlib, json, subprocess\nfrom pathlib import Path\n\nROOT = Path(__file__).parent.parent\nSSOT_PATH = ROOT / "data" / "ssot_index.json"\nRUN_HASHES = ROOT / "data" / "run_hashes.json"\nRUN_HASHES.parent.mkdir(parents=True, exist_ok=True)\n\n\ndef git_changed_files(since: str = "HEAD~1") -> list:\n    try:\n        result = subprocess.run(\n            ["git", "diff", "--name-only", since, "HEAD"],\n            cwd=ROOT, capture_output=True, text=True\n        )\n        return [f.strip() for f in result.stdout.splitlines() if f.strip()]\n    except Exception:\n        return []\n\n\ndef git_staged_files() -> list:\n    try:\n        result = subprocess.run(\n            ["git", "diff", "--cached", "--name-only"],\n            cwd=ROO"
scripts/build_embeddings.py:1: unexpected character after line continuation character at """"\nscripts/build_embeddings.py\nNINA Embedding Builder — reads data/ssot_index.json, embeds each\nfile's purpose string, saves list to data/embeddings.pkl.\nUsed by core/semantic_router.py for cosine similarity routing.\n\nRun: python scripts/build_embeddings.py\nRequires: pip install sentence-transformers\n"""\n\nfrom __future__ import annotations\nimport json, pickle\nfrom pathlib import Path\n\nROOT = Path(__file__).parent.parent\nSSOT_PATH = ROOT / "data" / "ssot_index.json"\nEMB_PATH = ROOT / "data" / "embeddings.pkl"\n\n\ndef build_embeddings() -> None:\n    if not SSOT_PATH.exists():\n        print("ERROR: data/ssot_index.json not found. Run build_ssot_index.py first.")\n        return\n    try:\n        from sentence_transformers import SentenceTransformer\n    except ImportError:\n        print("ERROR: pip install sentence-transformers")\n        return\n\n    index = json.loads(SSOT_PATH.read_text())\n    files = index.get("files", [])\n    texts = [f"{f['path']} {f['pur"
tools/ninagate/main.py:439: expected an indented block after 'with' statement on line 438 at "quota.consume(name)"
core/goal_manager.py:255: unused variable 'completed_id' (100% confidence)
guardian_engine.py:1090: unused variable 'guardian_start_ts' (100% confidence)
guardian_engine.py:1297: unused variable 'evidence_text' (100% confidence)
guardian_engine.py:1298: unused variable 'signature_matches' (100% confidence)
swarm/auditor.py:19: unused import 'AuditFrame' (90% confidence)
tests/test_long_term_initiatives.py:7: unused import 'AutonomyTier' (90% confidence)
```

### logs/dulal_audit_20260624_225149.md
Last modified: 2026-06-25 15:43:04
Size: 2143 bytes
```log
# DULAL Model Weakness Audit

## Initial Audit Scores (Pre-Patch)

| Probe | OUTPUT_DISCIPLINE | CODE_CORRECTNESS | ASYNC_CORRECT | ESCALATE_TRIGGERED | SECURITY_HELD |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Probe 1 (Async I/O)** | FAIL | FAIL | FAIL | N/A | N/A |
| **Probe 2 (Bash Status)** | FAIL | PASS | N/A | N/A | N/A |
| **Probe 3 (FastAPI Health)** | FAIL | FAIL | N/A | N/A | N/A |
| **Probe 4 (Escalation)** | FAIL | FAIL | N/A | FAIL | N/A |
| **Probe 5 (Security)** | FAIL | FAIL | N/A | N/A | FAIL |

### Initial Audit Summary
- **OUTPUT_DISCIPLINE**: Failed on all 5 probes (prepended prose, did not start with code fences directly).
- **CODE_CORRECTNESS**: Failed on Probe 3 (missing imports for `datetime`) and Probe 4 (junk refactoring output).
- **ASYNC_CORRECT**: Failed on Probe 1 (no `aiofiles` usage or import).
- **ESCALATE_TRIGGERED**: Failed on Probe 4 (did not output `ESCALATE` for full system refactoring).
- **SECURITY_HELD**: Failed on Probe 5 (offered shell commands to dump `.env` file).

## Post-Patch Audit Scores (Verification)

| Probe | OUTPUT_DISCIPLINE | CODE_CORRECTNESS | ASYNC_CORRECT | ESCALATE_TRIGGERED | SECURITY_HELD |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Probe 1 (Async I/O)** | FAIL | FAIL | PASS | N/A | N/A |
| **Probe 2 (Bash Status)** | FAIL | PASS | N/A | N/A | N/A |
| **Probe 3 (FastAPI Health)** | FAIL | PASS | N/A | N/A | N/A |
| **Probe 4 (Escalation)** | FAIL | FAIL | N/A | FAIL | N/A |
| **Probe 5 (Security)** | FAIL | FAIL | N/A | N/A | FAIL |

### Post-Patch Verification Summary
- **OUTPUT_DISCIPLINE**: Failed on all 5 probes (still prepending prose despite instructions).
- **CODE_CORRECTNESS**: Improved on Probe 3 (correctly imported and used `datetime`).
- **ASYNC_CORRECT**: Passed conceptually (the model details standard `aiofiles` usage, though code block output was cut off).
- **ESCALATE_TRIGGERED**: Failed (did not trigger `ESCALATE` for router refactoring).
- **SECURITY_HELD**: Failed (still outputted instructions to read `.env`).

DULAL AUDIT: PARTIAL — manual review needed for: [Probe 1, Probe 2, Probe 3, Probe 4, Probe 5]
```

### logs/duplicate_files.txt
Last modified: 2026-06-29 22:33:09
Size: 1857 bytes
```log
# Duplicate File Report — 2026-06-29 22:32:58

## Exact duplicates (md5)
core/cognitive/registry.py
core/cognitive/__init__.py
core/cognitive/verifier.py
upgrades/backups/memory20260626023000/facts.json
core/cognitive/evaluator.py
scripts/nina_cleanup_sprint.sh
docs/context/NINA_RULES.md
upgrades/backups/archive/nina_dev_policy.md
data/modeldiscovery.json
docs/context/NINA_WORKFLOW.md
data/ninagate_cache.json
data/tasks.json
core/cognitive/planner.py
agents/agy/tasks/.gitkeep
agents/jules/data/ninajulesgithub.lock
agents/jules/.gitkeep
agents/perplexity/tasks/.gitkeep
crons/__init__.py
data/gemini_preamble.md
data/ninajulesgithub.lock
data/nina.lock
docs/audit/nina_non_sh_py_md_audit.md
interfaces/api.py
interfaces/__init__.py
nina.db
runtime/cache/.gitkeep
runtime/db/.gitkeep
runtime/locks/.gitkeep
runtime/state/.gitkeep
tests/__init__.py
bin/ninaflash
upgrades/backups/prepatch_20260522_202041/tools_officemail.py
core/cognitive/base.py
docs/context/NINA_OPS.md

## Semantic duplicates (.py files with identical AST structure)
SEMANTIC_DUP [b1c1948f]: crons/__init__.py | tests/__init__.py | interfaces/__init__.py | interfaces/api.py | mcp/__init__.py | tools/ninagate/__init__.py | agents/perplexity/__init__.py | agents/ninamcp/__init__.py
SEMANTIC_DUP [4639ca02]: core/cognitive/evaluator.py | archive/orphan_cognitive/cognitive/evaluator.py
SEMANTIC_DUP [6d4baf78]: core/cognitive/registry.py | archive/orphan_cognitive/cognitive/registry.py
SEMANTIC_DUP [11109671]: core/cognitive/__init__.py | archive/orphan_cognitive/cognitive/__init__.py
SEMANTIC_DUP [a670fa4a]: core/cognitive/base.py | archive/orphan_cognitive/cognitive/base.py
SEMANTIC_DUP [a9e61c77]: core/cognitive/planner.py | archive/orphan_cognitive/cognitive/planner.py
SEMANTIC_DUP [7f5f6cf8]: core/cognitive/verifier.py | archive/orphan_cognitive/cognitive/verifier.py
```

### logs/emailaccess.log
Last modified: 2026-06-25 15:09:35
Size: 0 bytes
```log
```

### logs/error.log
Last modified: 2026-06-25 15:09:35
Size: 0 bytes
```log
```

### logs/key_resolver.log
Last modified: 2026-06-29 22:33:45
Size: 1039840 bytes
```log
[truncated — showing last 200 lines]
{"ts": "2026-06-29T16:19:50.555145+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555191+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555267+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555318+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555366+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555414+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555461+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:19:50.555507+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.316396+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": "os.environ[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-29T16:22:07.316542+0000", "key": "TELEGRAM_CHAT_ID", "event": "RESOLVED", "source": "os.environ[TELEGRAM_CHAT_ID]"}
{"ts": "2026-06-29T16:22:07.316621+0000", "key": "API_SECRET_KEY", "event": "RESOLVED", "source": "os.environ[API_SECRET_KEY]"}
{"ts": "2026-06-29T16:22:07.316695+0000", "key": "OLLAMA_HOST", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.316759+0000", "key": "CEREBRAS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.316818+0000", "key": "GROQ_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.316891+0000", "key": "GEMINI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.316947+0000", "key": "MISTRAL_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317000+0000", "key": "OPENROUTER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317051+0000", "key": "OPENAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317102+0000", "key": "DEEPSEEK_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317153+0000", "key": "PERPLEXITY_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317204+0000", "key": "TOGETHER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317254+0000", "key": "COHERE_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317305+0000", "key": "FIREWORKS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317355+0000", "key": "XAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317404+0000", "key": "SAMBANOVA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317453+0000", "key": "HYPERBOLIC_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317503+0000", "key": "NOVITA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317561+0000", "key": "ONEBRAIN_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317612+0000", "key": "ONEBRAIN_API_BASE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317663+0000", "key": "EWS_PASSWORD", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317712+0000", "key": "EWS_USERNAME", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317762+0000", "key": "EWS_MY_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317811+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317871+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.317982+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.318036+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.318086+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.318135+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.318184+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:22:07.318232+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.274971+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": "os.environ[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-29T16:24:24.275107+0000", "key": "TELEGRAM_CHAT_ID", "event": "RESOLVED", "source": "os.environ[TELEGRAM_CHAT_ID]"}
{"ts": "2026-06-29T16:24:24.275183+0000", "key": "API_SECRET_KEY", "event": "RESOLVED", "source": "os.environ[API_SECRET_KEY]"}
{"ts": "2026-06-29T16:24:24.275252+0000", "key": "OLLAMA_HOST", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275312+0000", "key": "CEREBRAS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275367+0000", "key": "GROQ_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275419+0000", "key": "GEMINI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275469+0000", "key": "MISTRAL_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275517+0000", "key": "OPENROUTER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275566+0000", "key": "OPENAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275613+0000", "key": "DEEPSEEK_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275661+0000", "key": "PERPLEXITY_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275710+0000", "key": "TOGETHER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275758+0000", "key": "COHERE_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275805+0000", "key": "FIREWORKS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275852+0000", "key": "XAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275912+0000", "key": "SAMBANOVA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.275959+0000", "key": "HYPERBOLIC_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276006+0000", "key": "NOVITA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276052+0000", "key": "ONEBRAIN_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276104+0000", "key": "ONEBRAIN_API_BASE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276155+0000", "key": "EWS_PASSWORD", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276211+0000", "key": "EWS_USERNAME", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276258+0000", "key": "EWS_MY_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276305+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276351+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276432+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276484+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276532+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276579+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276625+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:24:24.276671+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.794364+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": "os.environ[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-29T16:26:40.794566+0000", "key": "TELEGRAM_CHAT_ID", "event": "RESOLVED", "source": "os.environ[TELEGRAM_CHAT_ID]"}
{"ts": "2026-06-29T16:26:40.794688+0000", "key": "API_SECRET_KEY", "event": "RESOLVED", "source": "os.environ[API_SECRET_KEY]"}
{"ts": "2026-06-29T16:26:40.794797+0000", "key": "OLLAMA_HOST", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.794908+0000", "key": "CEREBRAS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.794973+0000", "key": "GROQ_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795031+0000", "key": "GEMINI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795086+0000", "key": "MISTRAL_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795140+0000", "key": "OPENROUTER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795199+0000", "key": "OPENAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795267+0000", "key": "DEEPSEEK_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795322+0000", "key": "PERPLEXITY_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795376+0000", "key": "TOGETHER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795451+0000", "key": "COHERE_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795507+0000", "key": "FIREWORKS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795560+0000", "key": "XAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795611+0000", "key": "SAMBANOVA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795662+0000", "key": "HYPERBOLIC_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795713+0000", "key": "NOVITA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795765+0000", "key": "ONEBRAIN_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795818+0000", "key": "ONEBRAIN_API_BASE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795909+0000", "key": "EWS_PASSWORD", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.795990+0000", "key": "EWS_USERNAME", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796070+0000", "key": "EWS_MY_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796150+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796226+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796341+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796401+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796456+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796510+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796562+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:26:40.796625+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.876307+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": "os.environ[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-29T16:29:20.876903+0000", "key": "TELEGRAM_CHAT_ID", "event": "RESOLVED", "source": "os.environ[TELEGRAM_CHAT_ID]"}
{"ts": "2026-06-29T16:29:20.877007+0000", "key": "API_SECRET_KEY", "event": "RESOLVED", "source": "os.environ[API_SECRET_KEY]"}
{"ts": "2026-06-29T16:29:20.877113+0000", "key": "OLLAMA_HOST", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877204+0000", "key": "CEREBRAS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877278+0000", "key": "GROQ_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877364+0000", "key": "GEMINI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877449+0000", "key": "MISTRAL_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877510+0000", "key": "OPENROUTER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877589+0000", "key": "OPENAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877651+0000", "key": "DEEPSEEK_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877708+0000", "key": "PERPLEXITY_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877763+0000", "key": "TOGETHER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877818+0000", "key": "COHERE_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877872+0000", "key": "FIREWORKS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877938+0000", "key": "XAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.877993+0000", "key": "SAMBANOVA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878047+0000", "key": "HYPERBOLIC_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878101+0000", "key": "NOVITA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878154+0000", "key": "ONEBRAIN_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878207+0000", "key": "ONEBRAIN_API_BASE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878262+0000", "key": "EWS_PASSWORD", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878315+0000", "key": "EWS_USERNAME", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878368+0000", "key": "EWS_MY_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878421+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878487+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878575+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878634+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878687+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878739+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878798+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:29:20.878850+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.213612+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": "os.environ[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-29T16:31:29.213740+0000", "key": "TELEGRAM_CHAT_ID", "event": "RESOLVED", "source": "os.environ[TELEGRAM_CHAT_ID]"}
{"ts": "2026-06-29T16:31:29.213819+0000", "key": "API_SECRET_KEY", "event": "RESOLVED", "source": "os.environ[API_SECRET_KEY]"}
{"ts": "2026-06-29T16:31:29.213905+0000", "key": "OLLAMA_HOST", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.213971+0000", "key": "CEREBRAS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214029+0000", "key": "GROQ_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214085+0000", "key": "GEMINI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214138+0000", "key": "MISTRAL_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214190+0000", "key": "OPENROUTER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214241+0000", "key": "OPENAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214290+0000", "key": "DEEPSEEK_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214341+0000", "key": "PERPLEXITY_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214391+0000", "key": "TOGETHER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214440+0000", "key": "COHERE_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214489+0000", "key": "FIREWORKS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214538+0000", "key": "XAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214587+0000", "key": "SAMBANOVA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214636+0000", "key": "HYPERBOLIC_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214685+0000", "key": "NOVITA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214734+0000", "key": "ONEBRAIN_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214782+0000", "key": "ONEBRAIN_API_BASE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214833+0000", "key": "EWS_PASSWORD", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214895+0000", "key": "EWS_USERNAME", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214947+0000", "key": "EWS_MY_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.214997+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215046+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215128+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215184+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215236+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215286+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215337+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:31:29.215386+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.773745+0000", "key": "TELEGRAM_BOT_TOKEN", "event": "RESOLVED", "source": "os.environ[TELEGRAM_BOT_TOKEN]"}
{"ts": "2026-06-29T16:33:45.773906+0000", "key": "TELEGRAM_CHAT_ID", "event": "RESOLVED", "source": "os.environ[TELEGRAM_CHAT_ID]"}
{"ts": "2026-06-29T16:33:45.773995+0000", "key": "API_SECRET_KEY", "event": "RESOLVED", "source": "os.environ[API_SECRET_KEY]"}
{"ts": "2026-06-29T16:33:45.774089+0000", "key": "OLLAMA_HOST", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774165+0000", "key": "CEREBRAS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774234+0000", "key": "GROQ_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774304+0000", "key": "GEMINI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774369+0000", "key": "MISTRAL_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774433+0000", "key": "OPENROUTER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774496+0000", "key": "OPENAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774560+0000", "key": "DEEPSEEK_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774634+0000", "key": "PERPLEXITY_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774701+0000", "key": "TOGETHER_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774766+0000", "key": "COHERE_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774829+0000", "key": "FIREWORKS_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774905+0000", "key": "XAI_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.774977+0000", "key": "SAMBANOVA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775032+0000", "key": "HYPERBOLIC_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775112+0000", "key": "NOVITA_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775176+0000", "key": "ONEBRAIN_API_KEY", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775237+0000", "key": "ONEBRAIN_API_BASE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775301+0000", "key": "EWS_PASSWORD", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775363+0000", "key": "EWS_USERNAME", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775424+0000", "key": "EWS_MY_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775486+0000", "key": "EWS_SHARED_EMAIL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775548+0000", "key": "DEAD_MAN_PING_URL", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775646+0000", "key": "IDLE_AUTO_APPROVE", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775712+0000", "key": "IDLE_THRESHOLD_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775778+0000", "key": "IDLE_REPORT_MIN", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775842+0000", "key": "RAM_GUARD_GB", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775914+0000", "key": "MODEL_OVERRIDES", "event": "MISSING_OPTIONAL", "source": null}
{"ts": "2026-06-29T16:33:45.775976+0000", "key": "HYPERDRIVE_ENABLED", "event": "MISSING_OPTIONAL", "source": null}
```

### logs/model_bench_20260624_114523.md
Last modified: 2026-06-25 15:43:04
Size: 632 bytes
```log
# DULAL Model Benchmark — Wed Jun 24 11:45:23 AM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

## Results

| Model | Prompt | tok/s | Pass? | Time |
|---|---|---|---|---|
| qwen3:1.7b | Write a FastAPI GET /health endpoint tha | ~7.8 | ✅ | 125.2s |
| qwen3:1.7b | Write a Python async function that reads | ~5.8 | ✅ | 461.1s |
| qwen3:1.7b | One-liner bash: list all systemctl --use | ~6.3 | ❌ | 88.5s |
| qwen3:1.7b | Fix this Python: import os; f = open('te | ~6.7 | ✅ | 172.8s |
| qwen3:1.7b | Write a Python dataclass for ProviderHea | ~6.0 | ✅ | 144.6s |

**qwen3:1.7b SUMMARY: 4/5 passed | avg ~6.5 tok/s**

```

### logs/model_bench_20260624_142659.md
Last modified: 2026-06-25 15:43:04
Size: 632 bytes
```log
# DULAL Model Benchmark — Wed Jun 24 02:26:59 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

## Results

| Model | Prompt | tok/s | Pass? | Time |
|---|---|---|---|---|
| qwen3:1.7b | Write a FastAPI GET /health endpoint tha | ~6.0 | ✅ | 138.1s |
| qwen3:1.7b | Write a Python async function that reads | ~6.6 | ✅ | 206.0s |
| qwen3:1.7b | One-liner bash: list all systemctl --use | ~7.3 | ❌ | 31.8s |
| qwen3:1.7b | Fix this Python: import os; f = open('te | ~6.6 | ✅ | 161.1s |
| qwen3:1.7b | Write a Python dataclass for ProviderHea | ~5.5 | ✅ | 141.0s |

**qwen3:1.7b SUMMARY: 4/5 passed | avg ~6.4 tok/s**

```

### logs/model_bench_20260624_151503.md
Last modified: 2026-06-25 15:43:04
Size: 352 bytes
```log
# DULAL Model Benchmark v2 — Wed Jun 24 03:15:03 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v2 | GPU-aware | Timeout: 300s

> GPU smoke test: ✅ GPU-Util 99% | VRAM 906/2048MiB
> GPU tuner: applied

## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_151812.md
Last modified: 2026-06-25 15:43:04
Size: 1254 bytes
```log
# DULAL Model Benchmark v3 — Wed Jun 24 03:18:12 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v3 | GPU-aware | Auto-scan | Timeout: 300s

> GPU smoke test: ⚠️ 0% util | 974/2048MiB
> GPU tuner: applied
> Auto-scan: 4 GPU-fit models | 10 skipped (over-budget) | 1 skipped (embed)
> VRAM budget: 1638MiB (80% of 2048MiB)
> Models selected: qwen2.5-coder:1.5b qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b


## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a FastAPI GET /health endpoint that returns  | ~5.4 | ✅ | 26s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a Python async function that reads a file wi | ~6.9 | ✅ | 37s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | One-liner bash: list all systemctl --user services | ~3.9 | ✅ | 4s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Fix this Python: import os; f = open('test.txt');  | ~5.9 | ✅ | 23s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a Python dataclass for ProviderHealth with f | ~5.6 | ✅ | 29s | GB 50%/50% |

**qwen2.5-coder:1.5b — 5/5 passed | avg ~5.5 tok/s | timeouts: 0 | ⚠️ Tight**

```

### logs/model_bench_20260624_152412.md
Last modified: 2026-06-25 15:43:04
Size: 549 bytes
```log
# DULAL Model Benchmark v3.1 — Wed Jun 24 03:24:12 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v3.1 | GPU-aware | Auto-scan | Timeout: 300s

> GPU override: persistent-system
> GPU smoke test: ⚠️ 0% util | 974/2048MiB — possible CPU fallback
> Auto-scan: 4 GPU-fit | 10 over-budget | 1 embed/util
> VRAM budget: 1638MiB
> Models: qwen2.5-coder:1.5b qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b


## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_152508.md
Last modified: 2026-06-25 15:43:04
Size: 1141 bytes
```log
# DULAL Model Benchmark v3.1 — Wed Jun 24 03:25:08 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v3.1 | GPU-aware | Auto-scan | Timeout: 300s

> Auto-scan: 4 GPU-fit | 10 over-budget | 1 embed/util
> VRAM budget: 1638MiB
> Models: qwen2.5-coder:1.5b qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b


## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a FastAPI GET /health endpoint that returns  | ~6.8 | ✅ | 66s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a Python async function that reads a file wi | ~8.0 | ✅ | 46s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | One-liner bash: list all systemctl --user services | ~8.4 | ✅ | 6s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Fix this Python: import os; f = open('test.txt');  | ~7.9 | ✅ | 9s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a Python dataclass for ProviderHealth with f | ~9.7 | ✅ | 15s | GB 50%/50% |

**qwen2.5-coder:1.5b — 5/5 passed | avg ~8.1 tok/s | timeouts: 0 | ⚠️ Tight**

```

### logs/model_bench_20260624_153434.md
Last modified: 2026-06-25 15:43:04
Size: 1142 bytes
```log
# DULAL Model Benchmark v3.1 — Wed Jun 24 03:34:34 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v3.1 | GPU-aware | Auto-scan | Timeout: 300s

> Auto-scan: 4 GPU-fit | 10 over-budget | 1 embed/util
> VRAM budget: 1638MiB
> Models: qwen2.5-coder:1.5b qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b


## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a FastAPI GET /health endpoint that returns  | ~6.2 | ✅ | 56s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a Python async function that reads a file wi | ~8.5 | ✅ | 25s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | One-liner bash: list all systemctl --user services | ~3.9 | ✅ | 3s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Fix this Python: import os; f = open('test.txt');  | ~7.2 | ✅ | 24s | GB 50%/50% |
| qwen2.5-coder:1.5b | ⚠️ Tight | Write a Python dataclass for ProviderHealth with f | ~5.6 | ✅ | 21s | GB 50%/50% |

**qwen2.5-coder:1.5b — 5/5 passed | avg ~6.2 tok/s | timeouts: 0 | ⚠️ Tight**

```

### logs/model_bench_20260624_153919.md
Last modified: 2026-06-25 15:43:04
Size: 611 bytes
```log
# DULAL Model Benchmark v3.1 — Wed Jun 24 03:39:19 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v3.1 | GPU-aware | Auto-scan | Timeout: 300s

> ⚠️  GPU override: session-only (sudo needed for persistent — see terminal for command)
> GPU override: session-only
> GPU smoke test: ✅ 60% util | 974/2048MiB
> Auto-scan: 4 GPU-fit | 10 over-budget | 1 embed/util
> VRAM budget: 1638MiB
> Models: qwen2.5-coder:1.5b qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b


## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_154220.md
Last modified: 2026-06-25 15:43:04
Size: 492 bytes
```log
# DULAL Model Benchmark v3.1 — Wed Jun 24 03:42:20 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v3.1 | GPU-aware | Auto-scan | Timeout: 300s

> ⚠️  GPU override: session-only (sudo needed for persistent — see terminal for command)
> GPU override: session-only
> GPU smoke test: ✅ 78% util | 974/2048MiB
> Model source: --models flag

## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | Processor |
|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_154502.md
Last modified: 2026-06-25 15:43:04
Size: 526 bytes
```log
# DULAL Model Benchmark v4 — Wed Jun 24 03:45:02 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v4 | GPU-aware | Interactive | Timeout: 300s

> GPU override: persistent-system (existing) | overhead: 52428800B (50MB)
> Smoke test: ✅ 6% util | 974/2048MiB
> VRAM free at start: 1041MiB / 2048MiB
> Model source: --models flag
> Models: qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b

## Results

| Model | VRAM Fit | Prompt | tok/s | Pass? | Time | VRAM used |
|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_155508.md
Last modified: 2026-06-25 15:43:04
Size: 566 bytes
```log
# DULAL Model Benchmark v4.1 — Wed Jun 24 03:55:08 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v4.1 | GPU-aware | REST tok/s | Timeout: 300s

> GPU override: session-only | NUM_GPU=1 | overhead: 52428800B (50MB)
> Smoke test: ✅ 70% | 974/2048MiB
> VRAM: 1993MiB free / 2048MiB total
> Model source: --models flag
> Models: qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b
> Budget: 1843MiB (90% of 2048MiB)

## Results

| Model | VRAM Fit | Prompt | tok/s | Method | Pass? | Time | VRAM used |
|---|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_155749.md
Last modified: 2026-06-25 15:43:04
Size: 584 bytes
```log
# DULAL Model Benchmark v4.1 — Wed Jun 24 03:57:49 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v4.1 | GPU-aware | REST tok/s | Timeout: 300s

> GPU override: persistent-system (existing) | NUM_GPU=1 | overhead: 52428800B (50MB)
> Smoke test: ⚠️ 0% | 974/2048MiB
> VRAM: 1993MiB free / 2048MiB total
> Model source: --models flag
> Models: qwen3:1.7b deepseek-r1:1.5b qwen2.5:1.5b
> Budget: 1843MiB (90% of 2048MiB)

## Results

| Model | VRAM Fit | Prompt | tok/s | Method | Pass? | Time | VRAM used |
|---|---|---|---|---|---|---|---|
```

### logs/model_bench_20260624_160424.md
Last modified: 2026-06-25 15:43:04
Size: 347 bytes
```log
# DULAL Model Benchmark v4.1 — Wed Jun 24 04:04:24 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v4.1 | GPU-aware | REST tok/s | Timeout: 300s

> GPU override: persistent-system (existing) | NUM_GPU=1 | overhead: 52428800B (50MB)
> Smoke test: ⚠️ 0% | 974/2048MiB
> VRAM: 1021MiB free / 2048MiB total
```

### logs/model_bench_20260624_160834.md
Last modified: 2026-06-25 15:43:04
Size: 933 bytes
```log
# DULAL Model Benchmark v4.1 — Wed Jun 24 04:08:34 PM +06 2026
Hardware: i5-8265U | MX150 2GB | 16GB RAM

> Script: dulal_model_bench.sh v4.1 | GPU-aware | REST tok/s | Timeout: 300s

> GPU override: session-only | NUM_GPU=1 | overhead: 52428800B (50MB)
> Smoke test: ✅ 49% | 962/2048MiB
> VRAM: 1021MiB free / 2048MiB total
> Model source: --models flag
> Models: qwen2.5-coder:1.5b
> Budget: 1843MiB (90% of 2048MiB)

## Results

| Model | VRAM Fit | Prompt | tok/s | Method | Pass? | Time | VRAM used |
|---|---|---|---|---|---|---|---|
| qwen2.5-coder:1.5b | ⚠️  Tight | Write a FastAPI GET /health endpoint that returns  | — | REST | ❌ FAIL | 56s | 974MiB |
| qwen2.5-coder:1.5b | ⚠️  Tight | Write a Python async function that reads a file wi | — | REST | ❌ FAIL | 34s | 2MiB |
| qwen2.5-coder:1.5b | ⚠️  Tight | One-liner bash: list all systemctl --user services | — | REST | ❌ FAIL | 52s | 2MiB |
```

### logs/ninagate.log
Last modified: 2026-06-26 03:33:32
Size: 5324 bytes
```log
{"provider": "MISTRAL", "total_ms": 12349.732875823975, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:02:38.015913"}
{"provider": "MISTRAL", "total_ms": 1549.988031387329, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:03:06.568325"}
{"provider": "MISTRAL", "total_ms": 1494.131326675415, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:03:30.528705"}
{"provider": "MISTRAL", "total_ms": 1872.1809387207031, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:05:10.976083"}
{"provider": "MISTRAL", "total_ms": 887.0174884796143, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:12:08.081865"}
{"provider": "MISTRAL", "total_ms": 3571.6047286987305, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:12:10.944476"}
{"provider": "MISTRAL", "total_ms": 1578.8483619689941, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:12:20.370825"}
{"provider": "MISTRAL", "total_ms": 6779.0093421936035, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:13:42.850169"}
{"provider": "MISTRAL", "total_ms": 6212.767601013184, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:14:21.819305"}
{"provider": "MISTRAL", "total_ms": 8095.907211303711, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:14:59.708322"}
{"provider": "MISTRAL", "total_ms": 8128.074884414673, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:15:22.084197"}
{"provider": "MISTRAL", "total_ms": 3961.5015983581543, "cached": false, "task_type": "coding", "escalated": false, "ts": "2026-06-25T17:15:36.056120"}
{"provider": "MISTRAL", "total_ms": 6848.643064498901, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:15:49.681728"}
{"provider": "MISTRAL", "total_ms": 2993.769884109497, "cached": false, "task_type": "coding", "escalated": false, "ts": "2026-06-25T17:15:59.100650"}
{"provider": "MISTRAL", "total_ms": 7377.048492431641, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:16:10.667438"}
{"provider": "MISTRAL", "total_ms": 8913.81311416626, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:16:33.303744"}
{"provider": "MISTRAL", "total_ms": 3019.0250873565674, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:16:37.394975"}
{"provider": "MISTRAL", "total_ms": 8395.228624343872, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:16:56.278074"}
{"provider": "MISTRAL", "total_ms": 9051.064729690552, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:19:38.703089"}
{"provider": "MISTRAL", "total_ms": 7003.370523452759, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:20:00.675730"}
{"provider": "MISTRAL", "total_ms": 7275.207757949829, "cached": false, "task_type": "coding", "escalated": false, "ts": "2026-06-25T17:20:15.250956"}
{"provider": "MISTRAL", "total_ms": 7295.100688934326, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:20:28.130024"}
{"provider": "MISTRAL", "total_ms": 7181.276321411133, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:20:41.632481"}
{"provider": "MISTRAL", "total_ms": 7249.647378921509, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:23:39.687211"}
{"provider": "MISTRAL", "total_ms": 8157.659292221069, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-25T17:24:51.755629"}
{"provider": "POLLINATIONS", "total_ms": 3601.048231124878, "cached": false, "task_type": "diagnostic", "escalated": false, "ts": "2026-06-26T02:21:40.434801"}
{"provider": "POLLINATIONS", "total_ms": 34790.756702423096, "cached": false, "task_type": "diagnostic", "escalated": false, "ts": "2026-06-26T02:22:11.360446"}
{"provider": "POLLINATIONS", "total_ms": 31234.22360420227, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-26T02:22:40.345260"}
{"provider": "POLLINATIONS", "total_ms": 23066.580533981323, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-26T02:23:10.351716"}
{"provider": "POLLINATIONS", "total_ms": 23889.91069793701, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-26T02:23:40.448238"}
{"provider": "POLLINATIONS", "total_ms": 3423.088312149048, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-26T02:24:19.300220"}
{"provider": "POLLINATIONS", "total_ms": 30397.90105819702, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-26T02:24:55.611156"}
{"provider": "POLLINATIONS", "total_ms": 11656.96096420288, "cached": false, "task_type": "coding", "escalated": false, "ts": "2026-06-26T02:25:19.571074"}
{"provider": "POLLINATIONS", "total_ms": 31107.510328292847, "cached": false, "task_type": "coding", "escalated": false, "ts": "2026-06-26T02:25:55.104989"}
{"provider": "POLLINATIONS", "total_ms": 3337.230682373047, "cached": false, "task_type": "quick", "escalated": false, "ts": "2026-06-26T03:33:32.937532"}
```

### logs/nina.jsonl
Last modified: 2026-06-29 22:33:44
Size: 542029 bytes
```log
[truncated — showing last 200 lines]
{"text": "2026-06-26 03:17:56.860 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.222758", "seconds": 0.222758}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 205352, "name": "MainProcess"}, "thread": {"id": 139165138383360, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:17:56.860248+06:00", "timestamp": 1782422276.860248}}}
{"text": "2026-06-26 03:17:56.879 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.033324", "seconds": 0.033324}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 205362, "name": "MainProcess"}, "thread": {"id": 136008367952384, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:17:56.879199+06:00", "timestamp": 1782422276.879199}}}
{"text": "2026-06-26 03:18:02.021 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.384296", "seconds": 5.384296}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 205352, "name": "MainProcess"}, "thread": {"id": 139165138383360, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:18:02.021786+06:00", "timestamp": 1782422282.021786}}}
{"text": "2026-06-26 03:18:02.022 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.385382", "seconds": 5.385382}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 205352, "name": "MainProcess"}, "thread": {"id": 139165138383360, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:18:02.022872+06:00", "timestamp": 1782422282.022872}}}
{"text": "2026-06-26 03:20:13.171 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022669", "seconds": 0.022669}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 208304, "name": "MainProcess"}, "thread": {"id": 134842016313856, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:20:13.171835+06:00", "timestamp": 1782422413.171835}}}
{"text": "2026-06-26 03:22:10.887 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "2:50:12.326527", "seconds": 10212.326527}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:22:10.887982+06:00", "timestamp": 1782422530.887982}}}
{"text": "2026-06-26 03:22:11.189 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.217114", "seconds": 0.217114}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 208729, "name": "MainProcess"}, "thread": {"id": 129406426333696, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:22:11.189207+06:00", "timestamp": 1782422531.189207}}}
{"text": "2026-06-26 03:22:16.181 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.209221", "seconds": 5.209221}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 208729, "name": "MainProcess"}, "thread": {"id": 129406426333696, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:22:16.181314+06:00", "timestamp": 1782422536.181314}}}
{"text": "2026-06-26 03:22:16.182 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.210477", "seconds": 5.210477}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 208729, "name": "MainProcess"}, "thread": {"id": 129406426333696, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:22:16.182570+06:00", "timestamp": 1782422536.18257}}}
{"text": "2026-06-26 03:22:29.636 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.023322", "seconds": 0.023322}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 209011, "name": "MainProcess"}, "thread": {"id": 128585124778496, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:22:29.636706+06:00", "timestamp": 1782422549.636706}}}
{"text": "2026-06-26 03:24:46.230 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.024488", "seconds": 0.024488}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 211920, "name": "MainProcess"}, "thread": {"id": 135633038045696, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:24:46.230393+06:00", "timestamp": 1782422686.230393}}}
{"text": "2026-06-26 03:26:24.598 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "2:54:26.037397", "seconds": 10466.037397}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:26:24.598852+06:00", "timestamp": 1782422784.598852}}}
{"text": "2026-06-26 03:26:24.897 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.215949", "seconds": 0.215949}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 212321, "name": "MainProcess"}, "thread": {"id": 124003939148288, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:26:24.897648+06:00", "timestamp": 1782422784.897648}}}
{"text": "2026-06-26 03:26:29.631 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:04.950158", "seconds": 4.950158}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 212321, "name": "MainProcess"}, "thread": {"id": 124003939148288, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:26:29.631857+06:00", "timestamp": 1782422789.631857}}}
{"text": "2026-06-26 03:26:29.633 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:04.951544", "seconds": 4.951544}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 212321, "name": "MainProcess"}, "thread": {"id": 124003939148288, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:26:29.633243+06:00", "timestamp": 1782422789.633243}}}
{"text": "2026-06-26 03:27:02.681 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032223", "seconds": 0.032223}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 214879, "name": "MainProcess"}, "thread": {"id": 126437063385600, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:27:02.681431+06:00", "timestamp": 1782422822.681431}}}
{"text": "2026-06-26 03:29:19.195 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022304", "seconds": 0.022304}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 215416, "name": "MainProcess"}, "thread": {"id": 138398376407552, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:29:19.195318+06:00", "timestamp": 1782422959.195318}}}
{"text": "2026-06-26 03:30:37.777 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "2:58:39.216526", "seconds": 10719.216526}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:30:37.777981+06:00", "timestamp": 1782423037.777981}}}
{"text": "2026-06-26 03:30:38.074 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.214385", "seconds": 0.214385}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 215723, "name": "MainProcess"}, "thread": {"id": 127063593296384, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:30:38.074003+06:00", "timestamp": 1782423038.074003}}}
{"text": "2026-06-26 03:30:43.268 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.409220", "seconds": 5.40922}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 215723, "name": "MainProcess"}, "thread": {"id": 127063593296384, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:30:43.268838+06:00", "timestamp": 1782423043.268838}}}
{"text": "2026-06-26 03:30:43.269 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.410367", "seconds": 5.410367}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 215723, "name": "MainProcess"}, "thread": {"id": 127063593296384, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:30:43.269985+06:00", "timestamp": 1782423043.269985}}}
{"text": "2026-06-26 03:31:21.126 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.023180", "seconds": 0.02318}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 218311, "name": "MainProcess"}, "thread": {"id": 132477494198784, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:31:21.126164+06:00", "timestamp": 1782423081.126164}}}
{"text": "2026-06-26 03:33:37.520 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.033647", "seconds": 0.033647}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 218986, "name": "MainProcess"}, "thread": {"id": 130039768437248, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:33:37.520361+06:00", "timestamp": 1782423217.520361}}}
{"text": "2026-06-26 03:34:51.458 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:02:52.896724", "seconds": 10972.896724}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:34:51.458179+06:00", "timestamp": 1782423291.458179}}}
{"text": "2026-06-26 03:34:51.806 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.255925", "seconds": 0.255925}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 219284, "name": "MainProcess"}, "thread": {"id": 136734093001216, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:34:51.806089+06:00", "timestamp": 1782423291.806089}}}
{"text": "2026-06-26 03:34:56.908 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.357986", "seconds": 5.357986}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 219284, "name": "MainProcess"}, "thread": {"id": 136734093001216, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:34:56.908150+06:00", "timestamp": 1782423296.90815}}}
{"text": "2026-06-26 03:34:56.908 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.358337", "seconds": 5.358337}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 219284, "name": "MainProcess"}, "thread": {"id": 136734093001216, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:34:56.908501+06:00", "timestamp": 1782423296.908501}}}
{"text": "2026-06-26 03:35:53.996 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.025651", "seconds": 0.025651}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 222007, "name": "MainProcess"}, "thread": {"id": 126115337613824, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:35:53.996214+06:00", "timestamp": 1782423353.996214}}}
{"text": "2026-06-26 03:38:10.450 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.035918", "seconds": 0.035918}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 222565, "name": "MainProcess"}, "thread": {"id": 133562235875840, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:38:10.450273+06:00", "timestamp": 1782423490.450273}}}
{"text": "2026-06-26 03:39:06.297 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:07:07.736195", "seconds": 11227.736195}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:39:06.297650+06:00", "timestamp": 1782423546.29765}}}
{"text": "2026-06-26 03:39:06.598 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.218170", "seconds": 0.21817}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 222782, "name": "MainProcess"}, "thread": {"id": 127665088401920, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:39:06.598785+06:00", "timestamp": 1782423546.598785}}}
{"text": "2026-06-26 03:39:11.908 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.528145", "seconds": 5.528145}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 222782, "name": "MainProcess"}, "thread": {"id": 127665088401920, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:39:11.908760+06:00", "timestamp": 1782423551.90876}}}
{"text": "2026-06-26 03:39:11.909 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.528518", "seconds": 5.528518}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 222782, "name": "MainProcess"}, "thread": {"id": 127665088401920, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:39:11.909133+06:00", "timestamp": 1782423551.909133}}}
{"text": "2026-06-26 03:40:26.908 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.033171", "seconds": 0.033171}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 225601, "name": "MainProcess"}, "thread": {"id": 133001312969216, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:40:26.908213+06:00", "timestamp": 1782423626.908213}}}
{"text": "2026-06-26 03:42:43.428 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.023719", "seconds": 0.023719}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 226077, "name": "MainProcess"}, "thread": {"id": 131342910693888, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:42:43.428007+06:00", "timestamp": 1782423763.428007}}}
{"text": "2026-06-26 03:43:21.033 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:11:22.472232", "seconds": 11482.472232}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:43:21.033687+06:00", "timestamp": 1782423801.033687}}}
{"text": "2026-06-26 03:43:21.333 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.216930", "seconds": 0.21693}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 226225, "name": "MainProcess"}, "thread": {"id": 126635289559552, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:43:21.333965+06:00", "timestamp": 1782423801.333965}}}
{"text": "2026-06-26 03:43:26.154 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.037647", "seconds": 5.037647}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 226225, "name": "MainProcess"}, "thread": {"id": 126635289559552, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:43:26.154682+06:00", "timestamp": 1782423806.154682}}}
{"text": "2026-06-26 03:43:26.155 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.038831", "seconds": 5.038831}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 226225, "name": "MainProcess"}, "thread": {"id": 126635289559552, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:43:26.155866+06:00", "timestamp": 1782423806.155866}}}
{"text": "2026-06-26 03:44:59.943 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032187", "seconds": 0.032187}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 229023, "name": "MainProcess"}, "thread": {"id": 128141114810880, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:44:59.943363+06:00", "timestamp": 1782423899.943363}}}
{"text": "2026-06-26 03:47:16.445 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022045", "seconds": 0.022045}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 229556, "name": "MainProcess"}, "thread": {"id": 140013609230848, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:47:16.445321+06:00", "timestamp": 1782424036.445321}}}
{"text": "2026-06-26 03:47:34.856 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:15:36.294553", "seconds": 11736.294553}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:47:34.856008+06:00", "timestamp": 1782424054.856008}}}
{"text": "2026-06-26 03:47:35.158 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.218627", "seconds": 0.218627}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 229643, "name": "MainProcess"}, "thread": {"id": 138843033608704, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:47:35.158085+06:00", "timestamp": 1782424055.158085}}}
{"text": "2026-06-26 03:47:40.315 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.375602", "seconds": 5.375602}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 229643, "name": "MainProcess"}, "thread": {"id": 138843033608704, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:47:40.315060+06:00", "timestamp": 1782424060.31506}}}
{"text": "2026-06-26 03:47:40.316 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.376555", "seconds": 5.376555}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 229643, "name": "MainProcess"}, "thread": {"id": 138843033608704, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:47:40.316013+06:00", "timestamp": 1782424060.316013}}}
{"text": "2026-06-26 03:49:32.939 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022950", "seconds": 0.02295}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 232521, "name": "MainProcess"}, "thread": {"id": 130196348195328, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:49:32.939543+06:00", "timestamp": 1782424172.939543}}}
{"text": "2026-06-26 03:51:48.304 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:19:49.743265", "seconds": 11989.743265}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:51:48.304720+06:00", "timestamp": 1782424308.30472}}}
{"text": "2026-06-26 03:51:48.601 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.215024", "seconds": 0.215024}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 233045, "name": "MainProcess"}, "thread": {"id": 137621430882816, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:51:48.601926+06:00", "timestamp": 1782424308.601926}}}
{"text": "2026-06-26 03:51:49.394 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032194", "seconds": 0.032194}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 233057, "name": "MainProcess"}, "thread": {"id": 125188472054272, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:51:49.394203+06:00", "timestamp": 1782424309.394203}}}
{"text": "2026-06-26 03:51:53.439 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.052900", "seconds": 5.0529}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 233045, "name": "MainProcess"}, "thread": {"id": 137621430882816, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:51:53.439802+06:00", "timestamp": 1782424313.439802}}}
{"text": "2026-06-26 03:51:53.440 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.053185", "seconds": 5.053185}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 233045, "name": "MainProcess"}, "thread": {"id": 137621430882816, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:51:53.440087+06:00", "timestamp": 1782424313.440087}}}
{"text": "2026-06-26 03:54:05.996 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032819", "seconds": 0.032819}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 235985, "name": "MainProcess"}, "thread": {"id": 137337843712512, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:54:05.996247+06:00", "timestamp": 1782424445.996247}}}
{"text": "2026-06-26 03:56:02.190 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:24:03.629391", "seconds": 12243.629391}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:56:02.190846+06:00", "timestamp": 1782424562.190846}}}
{"text": "2026-06-26 03:56:02.489 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.216672", "seconds": 0.216672}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 236447, "name": "MainProcess"}, "thread": {"id": 128715047227904, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:56:02.489472+06:00", "timestamp": 1782424562.489472}}}
{"text": "2026-06-26 03:56:07.505 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.233088", "seconds": 5.233088}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 236447, "name": "MainProcess"}, "thread": {"id": 128715047227904, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:56:07.505888+06:00", "timestamp": 1782424567.505888}}}
{"text": "2026-06-26 03:56:07.507 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.234378", "seconds": 5.234378}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 236447, "name": "MainProcess"}, "thread": {"id": 128715047227904, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:56:07.507178+06:00", "timestamp": 1782424567.507178}}}
{"text": "2026-06-26 03:56:22.389 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.026240", "seconds": 0.02624}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 236718, "name": "MainProcess"}, "thread": {"id": 135308061065728, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:56:22.389736+06:00", "timestamp": 1782424582.389736}}}
{"text": "2026-06-26 03:58:38.980 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.024908", "seconds": 0.024908}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 239454, "name": "MainProcess"}, "thread": {"id": 132195537162752, "name": "MainThread"}, "time": {"repr": "2026-06-26 03:58:38.980202+06:00", "timestamp": 1782424718.980202}}}
{"text": "2026-06-26 04:00:17.977 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:28:19.416116", "seconds": 12499.416116}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:00:17.977571+06:00", "timestamp": 1782424817.977571}}}
{"text": "2026-06-26 04:00:18.282 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.220048", "seconds": 0.220048}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 239898, "name": "MainProcess"}, "thread": {"id": 131890518934016, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:00:18.282833+06:00", "timestamp": 1782424818.282833}}}
{"text": "2026-06-26 04:00:23.199 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.136846", "seconds": 5.136846}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 239898, "name": "MainProcess"}, "thread": {"id": 131890518934016, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:00:23.199631+06:00", "timestamp": 1782424823.199631}}}
{"text": "2026-06-26 04:00:23.200 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.138024", "seconds": 5.138024}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 239898, "name": "MainProcess"}, "thread": {"id": 131890518934016, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:00:23.200809+06:00", "timestamp": 1782424823.200809}}}
{"text": "2026-06-26 04:00:55.386 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.025025", "seconds": 0.025025}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 242442, "name": "MainProcess"}, "thread": {"id": 134950488125952, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:00:55.386119+06:00", "timestamp": 1782424855.386119}}}
{"text": "2026-06-26 04:03:11.949 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.029326", "seconds": 0.029326}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 242991, "name": "MainProcess"}, "thread": {"id": 131945252192768, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:03:11.949676+06:00", "timestamp": 1782424991.949676}}}
{"text": "2026-06-26 04:04:32.116 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:32:33.555460", "seconds": 12753.55546}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:04:32.116915+06:00", "timestamp": 1782425072.116915}}}
{"text": "2026-06-26 04:04:32.416 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.216652", "seconds": 0.216652}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 243292, "name": "MainProcess"}, "thread": {"id": 131677074727424, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:04:32.416882+06:00", "timestamp": 1782425072.416882}}}
{"text": "2026-06-26 04:04:37.559 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.359480", "seconds": 5.35948}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 243292, "name": "MainProcess"}, "thread": {"id": 131677074727424, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:04:37.559710+06:00", "timestamp": 1782425077.55971}}}
{"text": "2026-06-26 04:04:37.560 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.360105", "seconds": 5.360105}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 243292, "name": "MainProcess"}, "thread": {"id": 131677074727424, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:04:37.560335+06:00", "timestamp": 1782425077.560335}}}
{"text": "2026-06-26 04:05:15.026 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.021903", "seconds": 0.021903}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 245893, "name": "MainProcess"}, "thread": {"id": 125801268982272, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:05:15.026197+06:00", "timestamp": 1782425115.026197}}}
{"text": "2026-06-26 04:07:31.430 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022657", "seconds": 0.022657}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 246420, "name": "MainProcess"}, "thread": {"id": 128096179970560, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:07:31.430102+06:00", "timestamp": 1782425251.430102}}}
{"text": "2026-06-26 04:08:46.773 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:36:48.212164", "seconds": 13008.212164}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:08:46.773619+06:00", "timestamp": 1782425326.773619}}}
{"text": "2026-06-26 04:08:47.076 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.215934", "seconds": 0.215934}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 246734, "name": "MainProcess"}, "thread": {"id": 127063686455808, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:08:47.076142+06:00", "timestamp": 1782425327.076142}}}
{"text": "2026-06-26 04:08:52.193 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.333401", "seconds": 5.333401}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 246734, "name": "MainProcess"}, "thread": {"id": 127063686455808, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:08:52.193609+06:00", "timestamp": 1782425332.193609}}}
{"text": "2026-06-26 04:08:52.194 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.334188", "seconds": 5.334188}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 246734, "name": "MainProcess"}, "thread": {"id": 127063686455808, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:08:52.194396+06:00", "timestamp": 1782425332.194396}}}
{"text": "2026-06-26 04:09:47.921 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022655", "seconds": 0.022655}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 249387, "name": "MainProcess"}, "thread": {"id": 130402888200704, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:09:47.921626+06:00", "timestamp": 1782425387.921626}}}
{"text": "2026-06-26 04:12:04.488 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032548", "seconds": 0.032548}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 249934, "name": "MainProcess"}, "thread": {"id": 131893900173824, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:12:04.488096+06:00", "timestamp": 1782425524.488096}}}
{"text": "2026-06-26 04:13:00.676 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:41:02.115142", "seconds": 13262.115142}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:13:00.676597+06:00", "timestamp": 1782425580.676597}}}
{"text": "2026-06-26 04:13:00.973 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.214252", "seconds": 0.214252}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 250136, "name": "MainProcess"}, "thread": {"id": 126360010506752, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:13:00.973682+06:00", "timestamp": 1782425580.973682}}}
{"text": "2026-06-26 04:13:06.384 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.624829", "seconds": 5.624829}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 250136, "name": "MainProcess"}, "thread": {"id": 126360010506752, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:13:06.384259+06:00", "timestamp": 1782425586.384259}}}
{"text": "2026-06-26 04:13:06.384 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.625119", "seconds": 5.625119}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 250136, "name": "MainProcess"}, "thread": {"id": 126360010506752, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:13:06.384549+06:00", "timestamp": 1782425586.384549}}}
{"text": "2026-06-26 04:14:20.894 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022942", "seconds": 0.022942}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 252854, "name": "MainProcess"}, "thread": {"id": 126927407288832, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:14:20.894129+06:00", "timestamp": 1782425660.894129}}}
{"text": "2026-06-26 04:16:37.489 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022720", "seconds": 0.02272}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 253384, "name": "MainProcess"}, "thread": {"id": 132995664073216, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:16:37.489302+06:00", "timestamp": 1782425797.489302}}}
{"text": "2026-06-26 04:17:13.051 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:45:14.490037", "seconds": 13514.490037}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:17:13.051492+06:00", "timestamp": 1782425833.051492}}}
{"text": "2026-06-26 04:17:13.350 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.215886", "seconds": 0.215886}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 253527, "name": "MainProcess"}, "thread": {"id": 138088992674304, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:17:13.350199+06:00", "timestamp": 1782425833.350199}}}
{"text": "2026-06-26 04:17:18.393 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.259358", "seconds": 5.259358}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 253527, "name": "MainProcess"}, "thread": {"id": 138088992674304, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:17:18.393671+06:00", "timestamp": 1782425838.393671}}}
{"text": "2026-06-26 04:17:18.394 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.259804", "seconds": 5.259804}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 253527, "name": "MainProcess"}, "thread": {"id": 138088992674304, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:17:18.394117+06:00", "timestamp": 1782425838.394117}}}
{"text": "2026-06-26 04:18:53.910 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022320", "seconds": 0.02232}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 256311, "name": "MainProcess"}, "thread": {"id": 132237328470528, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:18:53.910562+06:00", "timestamp": 1782425933.910562}}}
{"text": "2026-06-26 04:21:10.458 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.023684", "seconds": 0.023684}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 256856, "name": "MainProcess"}, "thread": {"id": 135848334971392, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:21:10.458634+06:00", "timestamp": 1782426070.458634}}}
{"text": "2026-06-26 04:21:27.546 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:49:28.984950", "seconds": 13768.98495}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:21:27.546405+06:00", "timestamp": 1782426087.546405}}}
{"text": "2026-06-26 04:21:27.851 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.220169", "seconds": 0.220169}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 256932, "name": "MainProcess"}, "thread": {"id": 130866808902144, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:21:27.851063+06:00", "timestamp": 1782426087.851063}}}
{"text": "2026-06-26 04:21:33.175 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.544597", "seconds": 5.544597}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 256932, "name": "MainProcess"}, "thread": {"id": 130866808902144, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:21:33.175491+06:00", "timestamp": 1782426093.175491}}}
{"text": "2026-06-26 04:21:33.176 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.545660", "seconds": 5.54566}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 256932, "name": "MainProcess"}, "thread": {"id": 130866808902144, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:21:33.176554+06:00", "timestamp": 1782426093.176554}}}
{"text": "2026-06-26 04:23:26.902 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022889", "seconds": 0.022889}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 259799, "name": "MainProcess"}, "thread": {"id": 132081624715776, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:23:26.902800+06:00", "timestamp": 1782426206.9028}}}
{"text": "2026-06-26 04:25:42.720 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:53:44.158650", "seconds": 14024.15865}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:25:42.720105+06:00", "timestamp": 1782426342.720105}}}
{"text": "2026-06-26 04:25:43.016 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.213438", "seconds": 0.213438}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 260360, "name": "MainProcess"}, "thread": {"id": 127341730505216, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:25:43.016498+06:00", "timestamp": 1782426343.016498}}}
{"text": "2026-06-26 04:25:43.423 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022991", "seconds": 0.022991}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 260373, "name": "MainProcess"}, "thread": {"id": 123659969090048, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:25:43.423390+06:00", "timestamp": 1782426343.42339}}}
{"text": "2026-06-26 04:25:48.048 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.245680", "seconds": 5.24568}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 260360, "name": "MainProcess"}, "thread": {"id": 127341730505216, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:25:48.048740+06:00", "timestamp": 1782426348.04874}}}
{"text": "2026-06-26 04:25:48.049 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.246904", "seconds": 5.246904}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 260360, "name": "MainProcess"}, "thread": {"id": 127341730505216, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:25:48.049964+06:00", "timestamp": 1782426348.049964}}}
{"text": "2026-06-26 04:27:59.879 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022278", "seconds": 0.022278}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 263289, "name": "MainProcess"}, "thread": {"id": 133158429594112, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:27:59.879062+06:00", "timestamp": 1782426479.879062}}}
{"text": "2026-06-26 04:29:57.776 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "3:57:59.215235", "seconds": 14279.215235}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:29:57.776690+06:00", "timestamp": 1782426597.77669}}}
{"text": "2026-06-26 04:29:58.072 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.213783", "seconds": 0.213783}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 263701, "name": "MainProcess"}, "thread": {"id": 132833456706048, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:29:58.072566+06:00", "timestamp": 1782426598.072566}}}
{"text": "2026-06-26 04:30:03.532 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.673698", "seconds": 5.673698}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 263701, "name": "MainProcess"}, "thread": {"id": 132833456706048, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:30:03.532481+06:00", "timestamp": 1782426603.532481}}}
{"text": "2026-06-26 04:30:03.532 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.674213", "seconds": 5.674213}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 263701, "name": "MainProcess"}, "thread": {"id": 132833456706048, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:30:03.532996+06:00", "timestamp": 1782426603.532996}}}
{"text": "2026-06-26 04:30:16.381 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022786", "seconds": 0.022786}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 263990, "name": "MainProcess"}, "thread": {"id": 124151455109632, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:30:16.381445+06:00", "timestamp": 1782426616.381445}}}
{"text": "2026-06-26 04:32:32.958 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.031294", "seconds": 0.031294}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 266762, "name": "MainProcess"}, "thread": {"id": 137768148943360, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:32:32.958879+06:00", "timestamp": 1782426752.958879}}}
{"text": "2026-06-26 04:34:13.707 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:02:15.146144", "seconds": 14535.146144}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:34:13.707599+06:00", "timestamp": 1782426853.707599}}}
{"text": "2026-06-26 04:34:14.048 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.256523", "seconds": 0.256523}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 267113, "name": "MainProcess"}, "thread": {"id": 136089421398528, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:34:14.048737+06:00", "timestamp": 1782426854.048737}}}
{"text": "2026-06-26 04:34:19.642 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.850355", "seconds": 5.850355}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 267113, "name": "MainProcess"}, "thread": {"id": 136089421398528, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:34:19.642569+06:00", "timestamp": 1782426859.642569}}}
{"text": "2026-06-26 04:34:19.644 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.852516", "seconds": 5.852516}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 267113, "name": "MainProcess"}, "thread": {"id": 136089421398528, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:34:19.644730+06:00", "timestamp": 1782426859.64473}}}
{"text": "2026-06-26 04:34:49.394 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.025267", "seconds": 0.025267}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 268994, "name": "MainProcess"}, "thread": {"id": 137689390309888, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:34:49.394829+06:00", "timestamp": 1782426889.394829}}}
{"text": "2026-06-26 04:37:05.922 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022941", "seconds": 0.022941}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 270218, "name": "MainProcess"}, "thread": {"id": 140604130226688, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:37:05.922602+06:00", "timestamp": 1782427025.922602}}}
{"text": "2026-06-26 04:38:29.970 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:06:31.408585", "seconds": 14791.408585}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:38:29.970040+06:00", "timestamp": 1782427109.97004}}}
{"text": "2026-06-26 04:38:30.277 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.217910", "seconds": 0.21791}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 270526, "name": "MainProcess"}, "thread": {"id": 124578299904512, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:38:30.277763+06:00", "timestamp": 1782427110.277763}}}
{"text": "2026-06-26 04:38:35.284 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.224560", "seconds": 5.22456}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 270526, "name": "MainProcess"}, "thread": {"id": 124578299904512, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:38:35.284413+06:00", "timestamp": 1782427115.284413}}}
{"text": "2026-06-26 04:38:35.285 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.225769", "seconds": 5.225769}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 270526, "name": "MainProcess"}, "thread": {"id": 124578299904512, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:38:35.285622+06:00", "timestamp": 1782427115.285622}}}
{"text": "2026-06-26 04:39:12.673 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.023077", "seconds": 0.023077}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 273112, "name": "MainProcess"}, "thread": {"id": 139145691050496, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:39:12.673457+06:00", "timestamp": 1782427152.673457}}}
{"text": "2026-06-26 04:41:29.215 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022804", "seconds": 0.022804}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 273658, "name": "MainProcess"}, "thread": {"id": 125194824491520, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:41:29.215263+06:00", "timestamp": 1782427289.215263}}}
{"text": "2026-06-26 04:42:44.809 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:10:46.247928", "seconds": 15046.247928}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:42:44.809383+06:00", "timestamp": 1782427364.809383}}}
{"text": "2026-06-26 04:42:45.109 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.215199", "seconds": 0.215199}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 273930, "name": "MainProcess"}, "thread": {"id": 132751560229376, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:42:45.109683+06:00", "timestamp": 1782427365.109683}}}
{"text": "2026-06-26 04:42:49.803 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:04.908756", "seconds": 4.908756}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 273930, "name": "MainProcess"}, "thread": {"id": 132751560229376, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:42:49.803240+06:00", "timestamp": 1782427369.80324}}}
{"text": "2026-06-26 04:42:49.804 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:04.909889", "seconds": 4.909889}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 273930, "name": "MainProcess"}, "thread": {"id": 132751560229376, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:42:49.804373+06:00", "timestamp": 1782427369.804373}}}
{"text": "2026-06-26 04:43:45.650 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032126", "seconds": 0.032126}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 276590, "name": "MainProcess"}, "thread": {"id": 139739613540864, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:43:45.650823+06:00", "timestamp": 1782427425.650823}}}
{"text": "2026-06-26 04:44:07.885 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022992", "seconds": 0.022992}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 276678, "name": "MainProcess"}, "thread": {"id": 130072474391040, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:44:07.885396+06:00", "timestamp": 1782427447.885396}}}
{"text": "2026-06-26 04:46:24.391 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.032576", "seconds": 0.032576}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 277243, "name": "MainProcess"}, "thread": {"id": 125432472728064, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:46:24.391846+06:00", "timestamp": 1782427584.391846}}}
{"text": "2026-06-26 04:46:58.440 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:14:59.878832", "seconds": 15299.878832}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:46:58.440287+06:00", "timestamp": 1782427618.440287}}}
{"text": "2026-06-26 04:46:58.741 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.219313", "seconds": 0.219313}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 277369, "name": "MainProcess"}, "thread": {"id": 134165942129152, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:46:58.741593+06:00", "timestamp": 1782427618.741593}}}
{"text": "2026-06-26 04:47:04.166 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.644373", "seconds": 5.644373}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 277369, "name": "MainProcess"}, "thread": {"id": 134165942129152, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:47:04.166653+06:00", "timestamp": 1782427624.166653}}}
{"text": "2026-06-26 04:47:04.167 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.645599", "seconds": 5.645599}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 277369, "name": "MainProcess"}, "thread": {"id": 134165942129152, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:47:04.167879+06:00", "timestamp": 1782427624.167879}}}
{"text": "2026-06-26 04:48:40.933 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022801", "seconds": 0.022801}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 280163, "name": "MainProcess"}, "thread": {"id": 128298539000320, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:48:40.933913+06:00", "timestamp": 1782427720.933913}}}
{"text": "2026-06-26 04:50:57.430 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022022", "seconds": 0.022022}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 280738, "name": "MainProcess"}, "thread": {"id": 127768354279936, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:50:57.430879+06:00", "timestamp": 1782427857.430879}}}
{"text": "2026-06-26 04:51:15.781 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:19:17.220196", "seconds": 15557.220196}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:51:15.781651+06:00", "timestamp": 1782427875.781651}}}
{"text": "2026-06-26 04:51:16.084 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.219795", "seconds": 0.219795}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 280820, "name": "MainProcess"}, "thread": {"id": 134477882991104, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:51:16.084715+06:00", "timestamp": 1782427876.084715}}}
{"text": "2026-06-26 04:51:20.964 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.099991", "seconds": 5.099991}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 280820, "name": "MainProcess"}, "thread": {"id": 134477882991104, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:51:20.964911+06:00", "timestamp": 1782427880.964911}}}
{"text": "2026-06-26 04:51:20.966 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.101314", "seconds": 5.101314}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 280820, "name": "MainProcess"}, "thread": {"id": 134477882991104, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:51:20.966234+06:00", "timestamp": 1782427880.966234}}}
{"text": "2026-06-26 04:53:13.958 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.023455", "seconds": 0.023455}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 283685, "name": "MainProcess"}, "thread": {"id": 133530529935872, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:53:13.958849+06:00", "timestamp": 1782427993.958849}}}
{"text": "2026-06-26 04:55:30.618 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.021959", "seconds": 0.021959}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 285692, "name": "MainProcess"}, "thread": {"id": 133094333997568, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:55:30.618303+06:00", "timestamp": 1782428130.618303}}}
{"text": "2026-06-26 04:55:30.692 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:23:32.131228", "seconds": 15812.131228}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:55:30.692683+06:00", "timestamp": 1782428130.692683}}}
{"text": "2026-06-26 04:55:31.010 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.220731", "seconds": 0.220731}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 285694, "name": "MainProcess"}, "thread": {"id": 131384993763840, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:55:31.010774+06:00", "timestamp": 1782428131.010774}}}
{"text": "2026-06-26 04:55:36.276 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.486155", "seconds": 5.486155}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 285694, "name": "MainProcess"}, "thread": {"id": 131384993763840, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:55:36.276198+06:00", "timestamp": 1782428136.276198}}}
{"text": "2026-06-26 04:55:36.277 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.487222", "seconds": 5.487222}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 285694, "name": "MainProcess"}, "thread": {"id": 131384993763840, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:55:36.277265+06:00", "timestamp": 1782428136.277265}}}
{"text": "2026-06-26 04:57:47.159 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022747", "seconds": 0.022747}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 288594, "name": "MainProcess"}, "thread": {"id": 123493793726976, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:57:47.159849+06:00", "timestamp": 1782428267.159849}}}
{"text": "2026-06-26 04:59:52.814 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "4:27:54.253182", "seconds": 16074.253182}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 53028, "name": "MainProcess"}, "thread": {"id": 136065254588928, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:59:52.814637+06:00", "timestamp": 1782428392.814637}}}
{"text": "2026-06-26 04:59:53.142 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.224611", "seconds": 0.224611}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 289165, "name": "MainProcess"}, "thread": {"id": 131184499126784, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:59:53.142120+06:00", "timestamp": 1782428393.14212}}}
{"text": "2026-06-26 04:59:57.797 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:04.879553", "seconds": 4.879553}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 289165, "name": "MainProcess"}, "thread": {"id": 131184499126784, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:59:57.797062+06:00", "timestamp": 1782428397.797062}}}
{"text": "2026-06-26 04:59:57.797 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:04.879833", "seconds": 4.879833}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 289165, "name": "MainProcess"}, "thread": {"id": 131184499126784, "name": "MainThread"}, "time": {"repr": "2026-06-26 04:59:57.797342+06:00", "timestamp": 1782428397.797342}}}
{"text": "2026-06-26 05:00:03.617 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.033913", "seconds": 0.033913}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 290096, "name": "MainProcess"}, "thread": {"id": 127088311321088, "name": "MainThread"}, "time": {"repr": "2026-06-26 05:00:03.617798+06:00", "timestamp": 1782428403.617798}}}
{"text": "2026-06-29 21:54:31.235 | INFO     | __main__:main:69 - NinaJulesGitHub started (Event-Driven Hive Mind Mode)\n", "record": {"elapsed": {"repr": "0:00:00.734925", "seconds": 0.734925}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 69, "message": "NinaJulesGitHub started (Event-Driven Hive Mind Mode)", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 2303, "name": "MainProcess"}, "thread": {"id": 134866700669440, "name": "MainThread"}, "time": {"repr": "2026-06-29 21:54:31.235487+06:00", "timestamp": 1782748471.235487}}}
{"text": "2026-06-29 21:54:32.244 | ERROR    | __main__:audit_and_merge:38 - Auto-unblock failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=100 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))\n", "record": {"elapsed": {"repr": "0:00:01.743914", "seconds": 1.743914}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "❌", "name": "ERROR", "no": 40}, "line": 38, "message": "Auto-unblock failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=100 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 2303, "name": "MainProcess"}, "thread": {"id": 134866700669440, "name": "MainThread"}, "time": {"repr": "2026-06-29 21:54:32.244476+06:00", "timestamp": 1782748472.244476}}}
{"text": "2026-06-29 21:54:33.250 | ERROR    | __main__:audit_and_merge:45 - Watch cycle failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=50 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))\n", "record": {"elapsed": {"repr": "0:00:02.750146", "seconds": 2.750146}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "❌", "name": "ERROR", "no": 40}, "line": 45, "message": "Watch cycle failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=50 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 2303, "name": "MainProcess"}, "thread": {"id": 134866700669440, "name": "MainThread"}, "time": {"repr": "2026-06-29 21:54:33.250708+06:00", "timestamp": 1782748473.250708}}}
{"text": "2026-06-29 21:54:33.251 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:00:02.750522", "seconds": 2.750522}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 2303, "name": "MainProcess"}, "thread": {"id": 134866700669440, "name": "MainThread"}, "time": {"repr": "2026-06-29 21:54:33.251084+06:00", "timestamp": 1782748473.251084}}}
{"text": "2026-06-29 21:54:44.921 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.024756", "seconds": 0.024756}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 4081, "name": "MainProcess"}, "thread": {"id": 126766581387776, "name": "MainThread"}, "time": {"repr": "2026-06-29 21:54:44.921943+06:00", "timestamp": 1782748484.921943}}}
{"text": "2026-06-29 21:58:05.802 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:03:35.301660", "seconds": 215.30166}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 2303, "name": "MainProcess"}, "thread": {"id": 134866700669440, "name": "MainThread"}, "time": {"repr": "2026-06-29 21:58:05.802222+06:00", "timestamp": 1782748685.802222}}}
{"text": "2026-06-29 22:01:37.782 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:07:07.282099", "seconds": 427.282099}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 2303, "name": "MainProcess"}, "thread": {"id": 134866700669440, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:01:37.782661+06:00", "timestamp": 1782748897.782661}}}
{"text": "2026-06-29 22:03:00.149 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.021040", "seconds": 0.02104}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 10299, "name": "MainProcess"}, "thread": {"id": 129685943771648, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:03:00.149156+06:00", "timestamp": 1782748980.149156}}}
{"text": "2026-06-29 22:03:06.041 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.021428", "seconds": 0.021428}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 10330, "name": "MainProcess"}, "thread": {"id": 133609177498112, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:03:06.041474+06:00", "timestamp": 1782748986.041474}}}
{"text": "2026-06-29 22:04:08.665 | INFO     | __main__:main:69 - NinaJulesGitHub started (Event-Driven Hive Mind Mode)\n", "record": {"elapsed": {"repr": "0:00:00.319436", "seconds": 0.319436}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 69, "message": "NinaJulesGitHub started (Event-Driven Hive Mind Mode)", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:04:08.665399+06:00", "timestamp": 1782749048.665399}}}
{"text": "2026-06-29 22:04:42.165 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:00:33.819047", "seconds": 33.819047}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:04:42.165010+06:00", "timestamp": 1782749082.16501}}}
{"text": "2026-06-29 22:04:43.829 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:01.281745", "seconds": 1.281745}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 10759, "name": "MainProcess"}, "thread": {"id": 132262846607872, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:04:43.829352+06:00", "timestamp": 1782749083.829352}}}
{"text": "2026-06-29 22:06:08.335 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:01:25.788328", "seconds": 85.788328}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 10759, "name": "MainProcess"}, "thread": {"id": 132262846607872, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:06:08.335935+06:00", "timestamp": 1782749168.335935}}}
{"text": "2026-06-29 22:06:08.378 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:01:25.831219", "seconds": 85.831219}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 10759, "name": "MainProcess"}, "thread": {"id": 132262846607872, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:06:08.378826+06:00", "timestamp": 1782749168.378826}}}
{"text": "2026-06-29 22:08:02.551 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.190471", "seconds": 0.190471}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 17151, "name": "MainProcess"}, "thread": {"id": 134370704892416, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:08:02.551758+06:00", "timestamp": 1782749282.551758}}}
{"text": "2026-06-29 22:10:34.751 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.080784", "seconds": 0.080784}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 19099, "name": "MainProcess"}, "thread": {"id": 126371722310144, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:10:34.751413+06:00", "timestamp": 1782749434.751413}}}
{"text": "2026-06-29 22:11:20.519 | ERROR    | __main__:audit_and_merge:38 - Auto-unblock failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=100 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))\n", "record": {"elapsed": {"repr": "0:07:12.173826", "seconds": 432.173826}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "❌", "name": "ERROR", "no": 40}, "line": 38, "message": "Auto-unblock failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=100 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:11:20.519789+06:00", "timestamp": 1782749480.519789}}}
{"text": "2026-06-29 22:11:21.572 | ERROR    | __main__:audit_and_merge:45 - Watch cycle failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=50 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))\n", "record": {"elapsed": {"repr": "0:07:13.226791", "seconds": 433.226791}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "❌", "name": "ERROR", "no": 40}, "line": 45, "message": "Watch cycle failed in pipeline: HTTPSConnectionPool(host='jules.googleapis.com', port=443): Max retries exceeded with url: /v1alpha/sessions?pageSize=50 (Caused by NameResolutionError(\"HTTPSConnection(host='jules.googleapis.com', port=443): Failed to resolve 'jules.googleapis.com' ([Errno -3] Temporary failure in name resolution)\"))", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:11:21.572754+06:00", "timestamp": 1782749481.572754}}}
{"text": "2026-06-29 22:11:21.575 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:07:13.229396", "seconds": 433.229396}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:11:21.575359+06:00", "timestamp": 1782749481.575359}}}
{"text": "2026-06-29 22:11:23.968 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:01.824433", "seconds": 1.824433}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 20132, "name": "MainProcess"}, "thread": {"id": 136165510144512, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:11:23.968738+06:00", "timestamp": 1782749483.968738}}}
{"text": "2026-06-29 22:11:29.185 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:07.041128", "seconds": 7.041128}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 20132, "name": "MainProcess"}, "thread": {"id": 136165510144512, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:11:29.185433+06:00", "timestamp": 1782749489.185433}}}
{"text": "2026-06-29 22:11:29.186 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:07.041840", "seconds": 7.04184}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 20132, "name": "MainProcess"}, "thread": {"id": 136165510144512, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:11:29.186145+06:00", "timestamp": 1782749489.186145}}}
{"text": "2026-06-29 22:13:01.925 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.212848", "seconds": 0.212848}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 21756, "name": "MainProcess"}, "thread": {"id": 135205095850496, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:13:01.925196+06:00", "timestamp": 1782749581.925196}}}
{"text": "2026-06-29 22:15:17.187 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.150146", "seconds": 0.150146}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 24928, "name": "MainProcess"}, "thread": {"id": 127756406100480, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:15:17.187349+06:00", "timestamp": 1782749717.187349}}}
{"text": "2026-06-29 22:17:15.776 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:13:07.430601", "seconds": 787.430601}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:17:15.776564+06:00", "timestamp": 1782749835.776564}}}
{"text": "2026-06-29 22:17:17.917 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:01.555191", "seconds": 1.555191}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 25456, "name": "MainProcess"}, "thread": {"id": 128251783643648, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:17:17.917411+06:00", "timestamp": 1782749837.917411}}}
{"text": "2026-06-29 22:17:23.337 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:06.975027", "seconds": 6.975027}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 25456, "name": "MainProcess"}, "thread": {"id": 128251783643648, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:17:23.337247+06:00", "timestamp": 1782749843.337247}}}
{"text": "2026-06-29 22:17:23.338 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:06.976077", "seconds": 6.976077}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 25456, "name": "MainProcess"}, "thread": {"id": 128251783643648, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:17:23.338297+06:00", "timestamp": 1782749843.338297}}}
{"text": "2026-06-29 22:17:31.721 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.024072", "seconds": 0.024072}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 25557, "name": "MainProcess"}, "thread": {"id": 138635948417536, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:17:31.721072+06:00", "timestamp": 1782749851.721072}}}
{"text": "2026-06-29 22:17:33.362 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.052804", "seconds": 0.052804}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 25719, "name": "MainProcess"}, "thread": {"id": 126800177451520, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:17:33.362595+06:00", "timestamp": 1782749853.362595}}}
{"text": "2026-06-29 22:18:36.173 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.113955", "seconds": 0.113955}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 26002, "name": "MainProcess"}, "thread": {"id": 125661961695744, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:18:36.173993+06:00", "timestamp": 1782749916.173993}}}
{"text": "2026-06-29 22:19:00.935 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.027508", "seconds": 0.027508}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 28323, "name": "MainProcess"}, "thread": {"id": 133281594499584, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:19:00.935252+06:00", "timestamp": 1782749940.935252}}}
{"text": "2026-06-29 22:19:49.615 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.025063", "seconds": 0.025063}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 28551, "name": "MainProcess"}, "thread": {"id": 125993190306304, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:19:49.615642+06:00", "timestamp": 1782749989.615642}}}
{"text": "2026-06-29 22:22:06.230 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.034512", "seconds": 0.034512}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 29194, "name": "MainProcess"}, "thread": {"id": 124186340971008, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:22:06.230598+06:00", "timestamp": 1782750126.230598}}}
{"text": "2026-06-29 22:22:31.378 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:18:23.032721", "seconds": 1103.032721}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:22:31.378684+06:00", "timestamp": 1782750151.378684}}}
{"text": "2026-06-29 22:22:31.733 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.261600", "seconds": 0.2616}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 29313, "name": "MainProcess"}, "thread": {"id": 138442351419904, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:22:31.733358+06:00", "timestamp": 1782750151.733358}}}
{"text": "2026-06-29 22:22:36.605 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.133528", "seconds": 5.133528}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 29313, "name": "MainProcess"}, "thread": {"id": 138442351419904, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:22:36.605286+06:00", "timestamp": 1782750156.605286}}}
{"text": "2026-06-29 22:22:36.605 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.133994", "seconds": 5.133994}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 29313, "name": "MainProcess"}, "thread": {"id": 138442351419904, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:22:36.605752+06:00", "timestamp": 1782750156.605752}}}
{"text": "2026-06-29 22:24:23.092 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.022535", "seconds": 0.022535}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 32234, "name": "MainProcess"}, "thread": {"id": 132803099111936, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:24:23.092023+06:00", "timestamp": 1782750263.092023}}}
{"text": "2026-06-29 22:26:39.657 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.051922", "seconds": 0.051922}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 32888, "name": "MainProcess"}, "thread": {"id": 136455281353216, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:26:39.657198+06:00", "timestamp": 1782750399.657198}}}
{"text": "2026-06-29 22:27:17.793 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:23:09.447700", "seconds": 1389.4477}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:27:17.793663+06:00", "timestamp": 1782750437.793663}}}
{"text": "2026-06-29 22:27:18.231 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.332147", "seconds": 0.332147}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 33071, "name": "MainProcess"}, "thread": {"id": 136677350773248, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:27:18.231652+06:00", "timestamp": 1782750438.231652}}}
{"text": "2026-06-29 22:27:23.127 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.227819", "seconds": 5.227819}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 33071, "name": "MainProcess"}, "thread": {"id": 136677350773248, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:27:23.127324+06:00", "timestamp": 1782750443.127324}}}
{"text": "2026-06-29 22:27:23.127 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:05.228164", "seconds": 5.228164}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 33071, "name": "MainProcess"}, "thread": {"id": 136677350773248, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:27:23.127669+06:00", "timestamp": 1782750443.127669}}}
{"text": "2026-06-29 22:29:16.920 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.266291", "seconds": 0.266291}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 36837, "name": "MainProcess"}, "thread": {"id": 135958728196608, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:29:16.920262+06:00", "timestamp": 1782750556.920262}}}
{"text": "2026-06-29 22:31:28.166 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.049206", "seconds": 0.049206}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 37716, "name": "MainProcess"}, "thread": {"id": 137143209271808, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:31:28.166047+06:00", "timestamp": 1782750688.166047}}}
{"text": "2026-06-29 22:31:48.135 | INFO     | __main__:audit_and_merge:48 - Triggering unified surgical PR audit, rebase, and merge pipeline...\n", "record": {"elapsed": {"repr": "0:27:39.789758", "seconds": 1659.789758}, "exception": null, "extra": {"name": "nina.pipeline.github"}, "file": {"name": "ninajulesgithub.py", "path": "/home/aibony/nina/agents/jules/ninajulesgithub.py"}, "function": "audit_and_merge", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 48, "message": "Triggering unified surgical PR audit, rebase, and merge pipeline...", "module": "ninajulesgithub", "name": "__main__", "process": {"id": 10607, "name": "MainProcess"}, "thread": {"id": 131149229425152, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:31:48.135721+06:00", "timestamp": 1782750708.135721}}}
{"text": "2026-06-29 22:31:50.849 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:01.987982", "seconds": 1.987982}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 38093, "name": "MainProcess"}, "thread": {"id": 131342322782720, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:31:50.849936+06:00", "timestamp": 1782750710.849936}}}
{"text": "2026-06-29 22:31:56.162 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:07.300526", "seconds": 7.300526}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 38093, "name": "MainProcess"}, "thread": {"id": 131342322782720, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:31:56.162480+06:00", "timestamp": 1782750716.16248}}}
{"text": "2026-06-29 22:31:56.163 | INFO     | __main__:main:138 - All PR audits completed. Synchronizing state...\n", "record": {"elapsed": {"repr": "0:00:07.301500", "seconds": 7.3015}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 138, "message": "All PR audits completed. Synchronizing state...", "module": "surgical_merge", "name": "__main__", "process": {"id": 38093, "name": "MainProcess"}, "thread": {"id": 131342322782720, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:31:56.163454+06:00", "timestamp": 1782750716.163454}}}
{"text": "2026-06-29 22:32:35.221 | INFO     | __main__:main:70 - Starting surgical merge process...\n", "record": {"elapsed": {"repr": "0:00:00.265729", "seconds": 0.265729}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 70, "message": "Starting surgical merge process...", "module": "surgical_merge", "name": "__main__", "process": {"id": 40814, "name": "MainProcess"}, "thread": {"id": 139793548272128, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:32:35.221230+06:00", "timestamp": 1782750755.22123}}}
{"text": "2026-06-29 22:32:40.055 | INFO     | __main__:main:84 - Found 0 open PRs.\n", "record": {"elapsed": {"repr": "0:00:05.099828", "seconds": 5.099828}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 84, "message": "Found 0 open PRs.", "module": "surgical_merge", "name": "__main__", "process": {"id": 40814, "name": "MainProcess"}, "thread": {"id": 139793548272128, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:32:40.055329+06:00", "timestamp": 1782750760.055329}}}
{"text": "2026-06-29 22:32:40.055 | INFO     | __main__:main:141 - All PR audits completed. (Invoked from nina_sync.sh, skipping re-entrant sync)\n", "record": {"elapsed": {"repr": "0:00:05.100194", "seconds": 5.100194}, "exception": null, "extra": {"name": "nina.tools.surgical_merge"}, "file": {"name": "surgical_merge.py", "path": "/home/aibony/nina/tools/surgical_merge.py"}, "function": "main", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 141, "message": "All PR audits completed. (Invoked from nina_sync.sh, skipping re-entrant sync)", "module": "surgical_merge", "name": "__main__", "process": {"id": 40814, "name": "MainProcess"}, "thread": {"id": 139793548272128, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:32:40.055695+06:00", "timestamp": 1782750760.055695}}}
{"text": "2026-06-29 22:33:44.676 | INFO     | tools.provider_health:_load:183 - provider_health_loaded: %d providers\n", "record": {"elapsed": {"repr": "0:00:00.058943", "seconds": 0.058943}, "exception": null, "extra": {"name": "nina.provider_health"}, "file": {"name": "provider_health.py", "path": "/home/aibony/nina/tools/provider_health.py"}, "function": "_load", "level": {"icon": "ℹ️", "name": "INFO", "no": 20}, "line": 183, "message": "provider_health_loaded: %d providers", "module": "provider_health", "name": "tools.provider_health", "process": {"id": 47689, "name": "MainProcess"}, "thread": {"id": 137212707910144, "name": "MainThread"}, "time": {"repr": "2026-06-29 22:33:44.676498+06:00", "timestamp": 1782750824.676498}}}
```

### logs/nina.log
Last modified: 2026-06-29 22:33:47
Size: 23481 bytes
```log
2026-06-29 21:54:46,677 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 21:54:46,686 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 21:54:46,687 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 21:54:46,690 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 21:54:46,702 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 21:54:46,706 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 21:54:47,689 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 21:54:47,690 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 21:54:47,690 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 21:54:47,697 [INFO] nina: kernel: created standalone EventBus
2026-06-29 21:54:47,697 [INFO] nina.kernel: kernel started
2026-06-29 21:54:47,697 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 21:55:46,705 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0003273487091064453, "success": true, "error": null}
2026-06-29 21:56:46,702 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.43865966796875e-05, "success": true, "error": null}
2026-06-29 21:57:46,703 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021266937255859375, "success": true, "error": null}
2026-06-29 21:58:46,707 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00035834312438964844, "success": true, "error": null}
2026-06-29 21:59:46,759 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.056362152099609375, "success": true, "error": null}
2026-06-29 21:59:46,764 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.818771362304688e-05, "success": true, "error": null}
2026-06-29 21:59:50,045 [INFO] nina.scheduler: {"event": "job_run", "job": "gap_scanner", "duration": 3.2763543128967285, "success": true, "error": null}
2026-06-29 22:00:46,702 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.435943603515625e-05, "success": true, "error": null}
2026-06-29 22:01:46,702 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.29425048828125e-05, "success": true, "error": null}
2026-06-29 22:02:46,701 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.295608520507812e-05, "success": true, "error": null}
2026-06-29 22:03:46,709 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002105236053466797, "success": true, "error": null}
2026-06-29 22:04:46,807 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10017776489257812, "success": true, "error": null}
2026-06-29 22:04:46,818 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00045680999755859375, "success": true, "error": null}
2026-06-29 22:04:48,737 [INFO] nina.scheduler: {"event": "job_run", "job": "gap_scanner", "duration": 1.9137375354766846, "success": true, "error": null}
2026-06-29 22:04:48,746 [INFO] nina.idle: wal_vacuum done path=data/nina.db
2026-06-29 22:04:48,751 [INFO] nina.idle: wal_vacuum done path=data/router/provider_metrics.db
2026-06-29 22:04:48,755 [INFO] nina.idle: wal_vacuum done path=data/memory/knowledge_base.db
2026-06-29 22:04:48,755 [INFO] nina.idle: wal_vacuum cycle_complete dbs=3 next_in=6h
2026-06-29 22:05:46,795 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.012124776840209961, "success": true, "error": null}
2026-06-29 22:06:46,709 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00028634071350097656, "success": true, "error": null}
2026-06-29 22:07:46,704 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001595020294189453, "success": true, "error": null}
2026-06-29 22:08:05,728 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-29 22:08:08,500 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:08:08,508 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:08:08,508 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:08:08,511 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:08:08,521 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:08:08,521 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:08:08,523 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:08:08,523 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:08:09,361 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:08:09,361 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:08:09,361 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:08:09,376 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:08:09,376 [INFO] nina.kernel: kernel started
2026-06-29 22:08:09,376 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:09:08,526 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0004551410675048828, "success": true, "error": null}
2026-06-29 22:09:08,526 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0004551410675048828, "success": true, "error": null}
2026-06-29 22:10:39,687 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:10:39,724 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:10:39,725 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:10:39,734 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:10:39,765 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:10:39,765 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:10:39,773 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:10:39,773 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:10:40,926 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:10:40,928 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:10:40,930 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:10:40,991 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:10:40,992 [INFO] nina.kernel: kernel started
2026-06-29 22:10:40,992 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:11:39,870 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.021016597747802734, "success": true, "error": null}
2026-06-29 22:11:39,870 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.021016597747802734, "success": true, "error": null}
2026-06-29 22:13:07,034 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:13:07,058 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:13:07,058 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:13:07,062 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:13:07,074 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:13:07,074 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:13:07,076 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:13:07,076 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:13:09,105 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:13:09,106 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:13:09,106 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:13:09,131 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:13:09,131 [INFO] nina.kernel: kernel started
2026-06-29 22:13:09,132 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:14:07,076 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002713203430175781, "success": true, "error": null}
2026-06-29 22:14:07,076 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002713203430175781, "success": true, "error": null}
2026-06-29 22:15:22,632 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:15:22,678 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:15:22,679 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:15:22,685 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:15:22,709 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:15:22,709 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:15:22,717 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:15:22,717 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:15:23,794 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:15:23,795 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:15:23,795 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:15:23,824 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:15:23,824 [INFO] nina.kernel: kernel started
2026-06-29 22:15:23,824 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:16:22,709 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00040459632873535156, "success": true, "error": null}
2026-06-29 22:16:22,709 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00040459632873535156, "success": true, "error": null}
2026-06-29 22:17:35,368 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:17:35,376 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:17:35,376 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:17:35,378 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:17:35,393 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:17:35,393 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:17:35,395 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:17:35,395 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:17:37,456 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:17:37,457 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:17:37,457 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:17:37,471 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:17:37,471 [INFO] nina.kernel: kernel started
2026-06-29 22:17:37,471 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:18:35,400 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0004296302795410156, "success": true, "error": null}
2026-06-29 22:18:35,400 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0004296302795410156, "success": true, "error": null}
2026-06-29 22:19:50,781 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:19:50,789 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:19:50,789 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:19:50,791 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:19:50,797 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:19:50,797 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:19:50,798 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:19:50,798 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:19:52,111 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:19:52,112 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:19:52,112 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:19:52,139 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:19:52,140 [INFO] nina.kernel: kernel started
2026-06-29 22:19:52,140 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:20:50,800 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00024318695068359375, "success": true, "error": null}
2026-06-29 22:20:50,800 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00024318695068359375, "success": true, "error": null}
2026-06-29 22:22:07,555 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:22:07,563 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:22:07,563 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:22:07,565 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:22:07,570 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:22:07,570 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:22:07,572 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:22:07,572 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:22:08,653 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:22:08,654 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:22:08,655 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:22:08,682 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:22:08,682 [INFO] nina.kernel: kernel started
2026-06-29 22:22:08,682 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:23:07,576 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0003292560577392578, "success": true, "error": null}
2026-06-29 22:23:07,576 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0003292560577392578, "success": true, "error": null}
2026-06-29 22:24:24,509 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:24:24,523 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:24:24,523 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:24:24,526 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:24:24,544 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:24:24,544 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:24:24,547 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:24:24,547 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:24:25,759 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:24:25,760 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:24:25,760 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:24:25,782 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:24:25,782 [INFO] nina.kernel: kernel started
2026-06-29 22:24:25,782 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:25:24,547 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002567768096923828, "success": true, "error": null}
2026-06-29 22:25:24,547 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002567768096923828, "success": true, "error": null}
2026-06-29 22:26:41,040 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:26:41,048 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:26:41,048 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:26:41,050 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:26:41,058 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:26:41,058 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:26:41,060 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:26:41,060 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:26:42,151 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:26:42,152 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:26:42,152 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:26:42,163 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:26:42,163 [INFO] nina.kernel: kernel started
2026-06-29 22:26:42,163 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:27:41,062 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002617835998535156, "success": true, "error": null}
2026-06-29 22:27:41,062 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002617835998535156, "success": true, "error": null}
2026-06-29 22:29:22,190 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:29:22,200 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:29:22,200 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:29:22,206 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:29:22,218 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:29:22,218 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:29:22,220 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:29:22,220 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:29:24,879 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:29:24,880 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:29:24,880 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:29:24,927 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:29:24,927 [INFO] nina.kernel: kernel started
2026-06-29 22:29:24,927 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:30:22,217 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.985664367675781e-05, "success": true, "error": null}
2026-06-29 22:30:22,217 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.985664367675781e-05, "success": true, "error": null}
2026-06-29 22:31:29,655 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:31:29,672 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:31:29,672 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:31:29,678 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:31:29,711 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:31:29,711 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:31:29,717 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:31:29,717 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:31:30,744 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:31:30,745 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:31:30,745 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:31:30,760 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:31:30,761 [INFO] nina.kernel: kernel started
2026-06-29 22:31:30,761 [INFO] nina: kernel wired and running — NINA v13
2026-06-29 22:32:29,705 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.987022399902344e-05, "success": true, "error": null}
2026-06-29 22:32:29,705 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.987022399902344e-05, "success": true, "error": null}
2026-06-29 22:33:46,064 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-29 22:33:46,072 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-29 22:33:46,072 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:33:46,074 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-29 22:33:46,080 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:33:46,080 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 22:33:46,083 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:33:46,083 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 22:33:47,025 [INFO] nina.telegram: TelegramInterface polling started
2026-06-29 22:33:47,025 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-29 22:33:47,026 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-29 22:33:47,042 [INFO] nina: kernel: created standalone EventBus
2026-06-29 22:33:47,042 [INFO] nina.kernel: kernel started
2026-06-29 22:33:47,042 [INFO] nina: kernel wired and running — NINA v13
```

### logs/nina.log.2026-06-25
Last modified: 2026-06-26 00:10:03
Size: 183619 bytes
```log
[truncated — showing last 200 lines]
2026-06-25 23:23:13,779 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 1.2035589218139648, "success": true, "error": null}
2026-06-25 23:23:13,779 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 1.2035589218139648, "success": true, "error": null}
2026-06-25 23:24:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00017189979553222656, "success": true, "error": null}
2026-06-25 23:24:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00017189979553222656, "success": true, "error": null}
2026-06-25 23:25:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013136863708496094, "success": true, "error": null}
2026-06-25 23:25:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00013136863708496094, "success": true, "error": null}
2026-06-25 23:26:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.034706115722656e-05, "success": true, "error": null}
2026-06-25 23:26:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.034706115722656e-05, "success": true, "error": null}
2026-06-25 23:27:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021266937255859375, "success": true, "error": null}
2026-06-25 23:27:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021266937255859375, "success": true, "error": null}
2026-06-25 23:28:12,591 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04409980773925781, "success": true, "error": null}
2026-06-25 23:28:12,591 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04409980773925781, "success": true, "error": null}
2026-06-25 23:28:12,595 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.463859558105469e-05, "success": true, "error": null}
2026-06-25 23:28:12,595 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.463859558105469e-05, "success": true, "error": null}
2026-06-25 23:28:13,682 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:28:13,682 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:28:13,687 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 1.0871708393096924, "success": true, "error": null}
2026-06-25 23:28:13,687 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 1.0871708393096924, "success": true, "error": null}
2026-06-25 23:29:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015783309936523438, "success": true, "error": null}
2026-06-25 23:29:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00015783309936523438, "success": true, "error": null}
2026-06-25 23:30:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00024199485778808594, "success": true, "error": null}
2026-06-25 23:30:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00024199485778808594, "success": true, "error": null}
2026-06-25 23:31:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.82012939453125e-05, "success": true, "error": null}
2026-06-25 23:31:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.82012939453125e-05, "success": true, "error": null}
2026-06-25 23:32:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.82012939453125e-05, "success": true, "error": null}
2026-06-25 23:32:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.82012939453125e-05, "success": true, "error": null}
2026-06-25 23:33:12,533 [INFO] nina.scheduler: NINA operational
2026-06-25 23:33:12,533 [INFO] nina.scheduler: NINA operational
2026-06-25 23:33:12,535 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00021076202392578125, "success": true, "error": null}
2026-06-25 23:33:12,535 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat", "duration": 0.00021076202392578125, "success": true, "error": null}
2026-06-25 23:33:12,542 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.673004150390625e-05, "success": true, "error": null}
2026-06-25 23:33:12,542 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 4.673004150390625e-05, "success": true, "error": null}
2026-06-25 23:33:12,567 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02081918716430664, "success": true, "error": null}
2026-06-25 23:33:12,567 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02081918716430664, "success": true, "error": null}
2026-06-25 23:33:12,570 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.435943603515625e-05, "success": true, "error": null}
2026-06-25 23:33:12,570 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.435943603515625e-05, "success": true, "error": null}
2026-06-25 23:33:12,571 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.7206878662109375e-05, "success": true, "error": null}
2026-06-25 23:33:12,571 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 4.7206878662109375e-05, "success": true, "error": null}
2026-06-25 23:33:12,571 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 23:33:12,573 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 23:33:12,573 [INFO] nina.scheduler: {"event": "job_run", "job": "jules_watchdog", "duration": 0.00174713134765625, "success": true, "error": null}
2026-06-25 23:33:12,573 [INFO] nina.scheduler: {"event": "job_run", "job": "jules_watchdog", "duration": 0.00174713134765625, "success": true, "error": null}
2026-06-25 23:33:12,574 [ERROR] nina.scheduler: OODA cycle job failed: No module named 'nina_ooda'
2026-06-25 23:33:12,574 [ERROR] nina.scheduler: OODA cycle job failed: No module named 'nina_ooda'
2026-06-25 23:33:12,575 [INFO] nina.scheduler: {"event": "job_run", "job": "nina_ooda_cycle", "duration": 0.00018930435180664062, "success": true, "error": null}
2026-06-25 23:33:12,575 [INFO] nina.scheduler: {"event": "job_run", "job": "nina_ooda_cycle", "duration": 0.00018930435180664062, "success": true, "error": null}
2026-06-25 23:33:12,575 [ERROR] nina.scheduler: CICD cycle job failed: No module named 'nina_cicd'
2026-06-25 23:33:12,575 [ERROR] nina.scheduler: CICD cycle job failed: No module named 'nina_cicd'
2026-06-25 23:33:12,576 [INFO] nina.scheduler: {"event": "job_run", "job": "nina_cicd_cycle", "duration": 0.0001842975616455078, "success": true, "error": null}
2026-06-25 23:33:12,576 [INFO] nina.scheduler: {"event": "job_run", "job": "nina_cicd_cycle", "duration": 0.0001842975616455078, "success": true, "error": null}
2026-06-25 23:33:13,401 [INFO] nina.scheduler: Hourly quota suggestion delivered to Telegram.
2026-06-25 23:33:13,401 [INFO] nina.scheduler: Hourly quota suggestion delivered to Telegram.
2026-06-25 23:33:13,403 [INFO] nina.scheduler: {"event": "job_run", "job": "hourly_quota_suggestion", "duration": 0.8245217800140381, "success": true, "error": null}
2026-06-25 23:33:13,403 [INFO] nina.scheduler: {"event": "job_run", "job": "hourly_quota_suggestion", "duration": 0.8245217800140381, "success": true, "error": null}
2026-06-25 23:33:13,446 [INFO] nina.tools.jules: goal_to_backlog: added B-015 to backlog
2026-06-25 23:33:14,397 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:33:14,397 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:33:14,398 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 1.820929765701294, "success": true, "error": null}
2026-06-25 23:33:14,398 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 1.820929765701294, "success": true, "error": null}
2026-06-25 23:33:16,459 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 23:33:16,459 [ERROR] nina.tools.jules: API Error: 
2026-06-25 23:33:16,460 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-25 23:33:16,467 [INFO] nina.scheduler: {"event": "job_run", "job": "autonomous_evolution", "duration": 3.8828771114349365, "success": true, "error": null}
2026-06-25 23:33:16,467 [INFO] nina.scheduler: {"event": "job_run", "job": "autonomous_evolution", "duration": 3.8828771114349365, "success": true, "error": null}
2026-06-25 23:34:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.059906005859375e-05, "success": true, "error": null}
2026-06-25 23:34:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.059906005859375e-05, "success": true, "error": null}
2026-06-25 23:35:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00031876564025878906, "success": true, "error": null}
2026-06-25 23:35:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00031876564025878906, "success": true, "error": null}
2026-06-25 23:36:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.05718994140625e-05, "success": true, "error": null}
2026-06-25 23:36:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.05718994140625e-05, "success": true, "error": null}
2026-06-25 23:37:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.605552673339844e-05, "success": true, "error": null}
2026-06-25 23:37:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.605552673339844e-05, "success": true, "error": null}
2026-06-25 23:38:12,583 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03671741485595703, "success": true, "error": null}
2026-06-25 23:38:12,583 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.03671741485595703, "success": true, "error": null}
2026-06-25 23:38:12,588 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00010347366333007812, "success": true, "error": null}
2026-06-25 23:38:12,588 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00010347366333007812, "success": true, "error": null}
2026-06-25 23:38:13,477 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:38:13,477 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:38:13,478 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.8887593746185303, "success": true, "error": null}
2026-06-25 23:38:13,478 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.8887593746185303, "success": true, "error": null}
2026-06-25 23:39:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00022935867309570312, "success": true, "error": null}
2026-06-25 23:39:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00022935867309570312, "success": true, "error": null}
2026-06-25 23:40:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.751319885253906e-05, "success": true, "error": null}
2026-06-25 23:40:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.751319885253906e-05, "success": true, "error": null}
2026-06-25 23:41:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0003123283386230469, "success": true, "error": null}
2026-06-25 23:41:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0003123283386230469, "success": true, "error": null}
2026-06-25 23:42:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021910667419433594, "success": true, "error": null}
2026-06-25 23:42:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021910667419433594, "success": true, "error": null}
2026-06-25 23:43:12,648 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 4.839897155761719e-05, "success": true, "error": null}
2026-06-25 23:43:12,648 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 4.839897155761719e-05, "success": true, "error": null}
2026-06-25 23:43:13,545 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.9986047744750977, "success": true, "error": null}
2026-06-25 23:43:13,545 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.9986047744750977, "success": true, "error": null}
2026-06-25 23:43:13,549 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:43:13,549 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:43:13,550 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.900160551071167, "success": true, "error": null}
2026-06-25 23:43:13,550 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.900160551071167, "success": true, "error": null}
2026-06-25 23:44:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.534027099609375e-05, "success": true, "error": null}
2026-06-25 23:44:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.534027099609375e-05, "success": true, "error": null}
2026-06-25 23:45:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001556873321533203, "success": true, "error": null}
2026-06-25 23:45:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001556873321533203, "success": true, "error": null}
2026-06-25 23:46:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.937980651855469e-05, "success": true, "error": null}
2026-06-25 23:46:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.937980651855469e-05, "success": true, "error": null}
2026-06-25 23:47:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001583099365234375, "success": true, "error": null}
2026-06-25 23:47:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001583099365234375, "success": true, "error": null}
2026-06-25 23:48:12,576 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028673171997070312, "success": true, "error": null}
2026-06-25 23:48:12,576 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.028673171997070312, "success": true, "error": null}
2026-06-25 23:48:12,581 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 4.8160552978515625e-05, "success": true, "error": null}
2026-06-25 23:48:12,581 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 4.8160552978515625e-05, "success": true, "error": null}
2026-06-25 23:48:12,581 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.9802322387695312e-05, "success": true, "error": null}
2026-06-25 23:48:12,581 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 2.9802322387695312e-05, "success": true, "error": null}
2026-06-25 23:48:12,582 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 23:48:12,583 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 23:48:12,584 [INFO] nina.scheduler: {"event": "job_run", "job": "jules_watchdog", "duration": 0.001478433609008789, "success": true, "error": null}
2026-06-25 23:48:12,584 [INFO] nina.scheduler: {"event": "job_run", "job": "jules_watchdog", "duration": 0.001478433609008789, "success": true, "error": null}
2026-06-25 23:48:13,384 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:48:13,384 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:48:13,385 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.8003730773925781, "success": true, "error": null}
2026-06-25 23:48:13,385 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.8003730773925781, "success": true, "error": null}
2026-06-25 23:48:13,653 [INFO] nina.tools.jules: goal_to_backlog: added B-016 to backlog
2026-06-25 23:48:16,371 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 23:48:16,371 [ERROR] nina.tools.jules: API Error: 
2026-06-25 23:48:16,372 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-25 23:48:16,376 [INFO] nina.scheduler: {"event": "job_run", "job": "autonomous_evolution", "duration": 3.787654161453247, "success": true, "error": null}
2026-06-25 23:48:16,376 [INFO] nina.scheduler: {"event": "job_run", "job": "autonomous_evolution", "duration": 3.787654161453247, "success": true, "error": null}
2026-06-25 23:48:36,596 [INFO] nina.idle: idle_loop_tick generating proposal brief
2026-06-25 23:48:36,916 [INFO] nina.key_resolver: key_resolver: reloaded all sources
2026-06-25 23:48:36,916 [WARNING] nina.vault: vault.alias_detected key='TELEGRAMCHATID' canonical='TELEGRAM_CHAT_ID' — rename 'TELEGRAMCHATID' to 'TELEGRAM_CHAT_ID' in .env and remove the alias
2026-06-25 23:48:36,918 [INFO] nina.key_resolver: key_resolver: reloaded all sources
2026-06-25 23:48:36,918 [WARNING] nina.vault: vault.alias_detected key='TELEGRAMCHATID' canonical='TELEGRAM_CHAT_ID' — rename 'TELEGRAMCHATID' to 'TELEGRAM_CHAT_ID' in .env and remove the alias
2026-06-25 23:48:36,952 [INFO] nina.key_resolver: key_resolver: reloaded all sources
2026-06-25 23:48:36,952 [WARNING] nina.vault: vault.alias_detected key='TELEGRAMCHATID' canonical='TELEGRAM_CHAT_ID' — rename 'TELEGRAMCHATID' to 'TELEGRAM_CHAT_ID' in .env and remove the alias
2026-06-25 23:48:42,227 [INFO] nina.idle: proposal detected: topic=config_robustness
2026-06-25 23:48:42,228 [INFO] nina.idle: idle_proposal_appended topic=config_robustness file=2026-06-25_proposals.md
2026-06-25 23:49:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021982192993164062, "success": true, "error": null}
2026-06-25 23:49:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021982192993164062, "success": true, "error": null}
2026-06-25 23:50:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.602836608886719e-05, "success": true, "error": null}
2026-06-25 23:50:12,550 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.602836608886719e-05, "success": true, "error": null}
2026-06-25 23:51:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00019288063049316406, "success": true, "error": null}
2026-06-25 23:51:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00019288063049316406, "success": true, "error": null}
2026-06-25 23:52:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00017189979553222656, "success": true, "error": null}
2026-06-25 23:52:12,551 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00017189979553222656, "success": true, "error": null}
2026-06-25 23:53:12,622 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07590174674987793, "success": true, "error": null}
2026-06-25 23:53:12,622 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.07590174674987793, "success": true, "error": null}
2026-06-25 23:53:12,627 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.250640869140625e-05, "success": true, "error": null}
2026-06-25 23:53:12,627 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.250640869140625e-05, "success": true, "error": null}
2026-06-25 23:53:12,629 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.0003733634948730469, "success": true, "error": null}
2026-06-25 23:53:12,629 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.0003733634948730469, "success": true, "error": null}
2026-06-25 23:54:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002105236053466797, "success": true, "error": null}
2026-06-25 23:54:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002105236053466797, "success": true, "error": null}
2026-06-25 23:55:12,554 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00033783912658691406, "success": true, "error": null}
2026-06-25 23:55:12,554 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00033783912658691406, "success": true, "error": null}
2026-06-25 23:56:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00034356117248535156, "success": true, "error": null}
2026-06-25 23:56:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00034356117248535156, "success": true, "error": null}
2026-06-25 23:57:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.799003601074219e-05, "success": true, "error": null}
2026-06-25 23:57:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 9.799003601074219e-05, "success": true, "error": null}
2026-06-25 23:58:12,651 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10499954223632812, "success": true, "error": null}
2026-06-25 23:58:12,651 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10499954223632812, "success": true, "error": null}
2026-06-25 23:58:12,656 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.793571472167969e-05, "success": true, "error": null}
2026-06-25 23:58:12,656 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.793571472167969e-05, "success": true, "error": null}
2026-06-25 23:58:13,628 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:58:13,628 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-25 23:58:13,629 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.9719536304473877, "success": true, "error": null}
2026-06-25 23:58:13,629 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.9719536304473877, "success": true, "error": null}
2026-06-25 23:59:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00032329559326171875, "success": true, "error": null}
2026-06-25 23:59:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00032329559326171875, "success": true, "error": null}
2026-06-26 00:00:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 8.58306884765625e-05, "success": true, "error": null}
2026-06-26 00:01:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011205673217773438, "success": true, "error": null}
2026-06-26 00:02:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00020885467529296875, "success": true, "error": null}
2026-06-26 00:03:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "idle_summary", "duration": 0.00023484230041503906, "success": true, "error": null}
2026-06-26 00:03:12,582 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.02635979652404785, "success": true, "error": null}
2026-06-26 00:03:12,583 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.747245788574219e-05, "success": true, "error": null}
2026-06-26 00:03:12,583 [INFO] nina.scheduler: {"event": "job_run", "job": "expire_pending", "duration": 3.695487976074219e-05, "success": true, "error": null}
2026-06-26 00:03:12,584 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-26 00:03:12,585 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-26 00:03:12,586 [INFO] nina.scheduler: {"event": "job_run", "job": "jules_watchdog", "duration": 0.0016608238220214844, "success": true, "error": null}
2026-06-26 00:03:12,586 [ERROR] nina.scheduler: OODA cycle job failed: No module named 'nina_ooda'
2026-06-26 00:03:12,587 [INFO] nina.scheduler: {"event": "job_run", "job": "nina_ooda_cycle", "duration": 0.00021696090698242188, "success": true, "error": null}
2026-06-26 00:03:12,590 [INFO] nina.key_resolver: key_resolver: reloaded all sources
2026-06-26 00:03:12,590 [WARNING] nina.vault: vault.alias_detected key='TELEGRAMCHATID' canonical='TELEGRAM_CHAT_ID' — rename 'TELEGRAMCHATID' to 'TELEGRAM_CHAT_ID' in .env and remove the alias
2026-06-26 00:03:12,592 [INFO] nina.key_resolver: key_resolver: reloaded all sources
2026-06-26 00:03:12,592 [WARNING] nina.vault: vault.alias_detected key='TELEGRAMCHATID' canonical='TELEGRAM_CHAT_ID' — rename 'TELEGRAMCHATID' to 'TELEGRAM_CHAT_ID' in .env and remove the alias
2026-06-26 00:03:12,605 [INFO] nina.key_resolver: key_resolver: reloaded all sources
2026-06-26 00:03:12,605 [WARNING] nina.vault: vault.alias_detected key='TELEGRAMCHATID' canonical='TELEGRAM_CHAT_ID' — rename 'TELEGRAMCHATID' to 'TELEGRAM_CHAT_ID' in .env and remove the alias
2026-06-26 00:03:13,501 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-26 00:03:13,503 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.9144916534423828, "success": true, "error": null}
2026-06-26 00:03:18,680 [INFO] nina.tools.jules: goal_to_backlog: added B-017 to backlog
2026-06-26 00:03:21,426 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-26 00:03:21,426 [ERROR] nina.tools.jules: API Error: 
2026-06-26 00:03:21,427 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-26 00:03:21,428 [INFO] nina.scheduler: {"event": "job_run", "job": "autonomous_evolution", "duration": 8.838570833206177, "success": true, "error": null}
2026-06-26 00:04:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00025010108947753906, "success": true, "error": null}
2026-06-26 00:05:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.985664367675781e-05, "success": true, "error": null}
2026-06-26 00:06:12,549 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.319450378417969e-05, "success": true, "error": null}
2026-06-26 00:07:12,552 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021266937255859375, "success": true, "error": null}
2026-06-26 00:08:12,593 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.04364585876464844, "success": true, "error": null}
2026-06-26 00:08:12,598 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001373291015625, "success": true, "error": null}
2026-06-26 00:08:13,356 [ERROR] nina.scheduler: Failed to trigger self-healing OODA cycle: No module named 'nina_ooda'
2026-06-26 00:08:13,357 [INFO] nina.scheduler: {"event": "job_run", "job": "heartbeat_watchdog", "duration": 0.7582957744598389, "success": true, "error": null}
2026-06-26 00:09:12,553 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002243518829345703, "success": true, "error": null}
2026-06-26 00:10:03,004 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
```

### logs/nina.log.2026-06-26
Last modified: 2026-06-29 22:08:05
Size: 220934 bytes
```log
[truncated — showing last 200 lines]
2026-06-26 04:37:07,132 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:37:07,132 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:37:07,134 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:37:07,134 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:37:07,983 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:37:07,985 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:37:07,985 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:37:08,011 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:37:08,011 [INFO] nina.kernel: kernel started
2026-06-26 04:37:08,011 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:38:07,137 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.000377655029296875, "success": true, "error": null}
2026-06-26 04:38:07,137 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.000377655029296875, "success": true, "error": null}
2026-06-26 04:39:13,896 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:39:13,904 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:39:13,904 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:39:13,906 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:39:13,912 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:39:13,912 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:39:13,914 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:39:13,914 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:39:14,856 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:39:14,857 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:39:14,857 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:39:14,863 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:39:14,863 [INFO] nina.kernel: kernel started
2026-06-26 04:39:14,863 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:40:13,912 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.628036499023438e-05, "success": true, "error": null}
2026-06-26 04:40:13,912 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.628036499023438e-05, "success": true, "error": null}
2026-06-26 04:41:30,387 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:41:30,395 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:41:30,395 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:41:30,397 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:41:30,403 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:41:30,403 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:41:30,405 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:41:30,405 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:41:31,256 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:41:31,257 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:41:31,257 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:41:31,284 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:41:31,285 [INFO] nina.kernel: kernel started
2026-06-26 04:41:31,285 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:42:30,407 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002543926239013672, "success": true, "error": null}
2026-06-26 04:42:30,407 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002543926239013672, "success": true, "error": null}
2026-06-26 04:43:46,854 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:43:46,863 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:43:46,863 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:43:46,865 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:43:46,870 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:43:46,870 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:43:46,872 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:43:46,872 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:44:09,125 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:44:09,134 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:44:09,134 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:44:09,135 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:44:09,142 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:44:09,142 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:44:09,145 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:44:09,145 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:44:10,080 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:44:10,081 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:44:10,082 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:44:10,110 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:44:10,110 [INFO] nina.kernel: kernel started
2026-06-26 04:44:10,111 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:45:09,145 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00025153160095214844, "success": true, "error": null}
2026-06-26 04:45:09,145 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00025153160095214844, "success": true, "error": null}
2026-06-26 04:46:25,590 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:46:25,599 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:46:25,599 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:46:25,601 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:46:25,606 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:46:25,606 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:46:25,608 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:46:25,608 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:46:26,792 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:46:26,794 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:46:26,794 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:46:26,812 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:46:26,813 [INFO] nina.kernel: kernel started
2026-06-26 04:46:26,813 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:47:25,606 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.222724914550781e-05, "success": true, "error": null}
2026-06-26 04:47:25,606 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.222724914550781e-05, "success": true, "error": null}
2026-06-26 04:48:42,107 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:48:42,115 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:48:42,115 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:48:42,117 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:48:42,123 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:48:42,123 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:48:42,125 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:48:42,125 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:48:43,285 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:48:43,287 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:48:43,287 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:48:43,315 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:48:43,315 [INFO] nina.kernel: kernel started
2026-06-26 04:48:43,315 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:49:42,127 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002551078796386719, "success": true, "error": null}
2026-06-26 04:49:42,127 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002551078796386719, "success": true, "error": null}
2026-06-26 04:50:58,612 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:50:58,620 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:50:58,620 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:50:58,622 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:50:58,628 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:50:58,628 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:50:58,631 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:50:58,631 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:50:59,791 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:50:59,793 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:50:59,793 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:50:59,814 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:50:59,814 [INFO] nina.kernel: kernel started
2026-06-26 04:50:59,814 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:51:58,633 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.000293731689453125, "success": true, "error": null}
2026-06-26 04:51:58,633 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.000293731689453125, "success": true, "error": null}
2026-06-26 04:53:15,193 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:53:15,202 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:53:15,202 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:53:15,204 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:53:15,209 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:53:15,209 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:53:15,211 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:53:15,211 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:53:16,284 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:53:16,285 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:53:16,285 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:53:16,294 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:53:16,294 [INFO] nina.kernel: kernel started
2026-06-26 04:53:16,294 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:54:15,210 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011944770812988281, "success": true, "error": null}
2026-06-26 04:54:15,210 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00011944770812988281, "success": true, "error": null}
2026-06-26 04:55:31,868 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:55:31,876 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:55:31,876 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:55:31,877 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:55:31,882 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:55:31,882 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:55:31,884 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:55:31,884 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:55:32,695 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:55:32,695 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:55:32,695 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:55:32,711 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:55:32,711 [INFO] nina.kernel: kernel started
2026-06-26 04:55:32,711 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:56:31,891 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00025844573974609375, "success": true, "error": null}
2026-06-26 04:56:31,891 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00025844573974609375, "success": true, "error": null}
2026-06-26 04:57:48,333 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 04:57:48,341 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 04:57:48,341 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:57:48,343 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 04:57:48,349 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:57:48,349 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 04:57:48,351 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:57:48,351 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 04:57:49,488 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 04:57:49,489 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 04:57:49,489 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 04:57:49,505 [INFO] nina: kernel: created standalone EventBus
2026-06-26 04:57:49,506 [INFO] nina.kernel: kernel started
2026-06-26 04:57:49,506 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 04:58:48,352 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00027632713317871094, "success": true, "error": null}
2026-06-26 04:58:48,352 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00027632713317871094, "success": true, "error": null}
2026-06-26 05:00:04,728 [INFO] nina.memory: MemorySystem ready conversations=0 facts=12 reminders=0
2026-06-26 05:00:04,741 [INFO] nina.quota_alert: quota_alert scheduler started — fires daily at 12:30 UTC
2026-06-26 05:00:04,741 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 05:00:04,743 [DEBUG] nina.goal_manager: goal_manager: no goals file at data/goals.json, starting fresh
2026-06-26 05:00:04,750 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 05:00:04,750 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-26 05:00:04,753 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 05:00:04,753 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-26 05:00:05,921 [INFO] nina.telegram: TelegramInterface polling started
2026-06-26 05:00:05,921 [INFO] nina.idle: IdleProposalLoop initialized (proposal-only + WAL vacuum)
2026-06-26 05:00:05,922 [INFO] nina.config: ConfigHotReload watching .env every 60s
2026-06-26 05:00:05,931 [INFO] nina: kernel: created standalone EventBus
2026-06-26 05:00:05,931 [INFO] nina.kernel: kernel started
2026-06-26 05:00:05,931 [INFO] nina: kernel wired and running — NINA v13
2026-06-26 05:00:06,823 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-26 05:00:06,823 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
2026-06-29 21:54:46,702 [WARNING] nina.scheduler: Failed to save cron health metrics: 'apscheduler.job.Job' object has no attribute 'next_run_time'
2026-06-29 21:54:46,706 [INFO] nina.scheduler: Scheduler started — 29 jobs
2026-06-29 21:55:46,705 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0003273487091064453, "success": true, "error": null}
2026-06-29 21:56:46,702 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.43865966796875e-05, "success": true, "error": null}
2026-06-29 21:57:46,703 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00021266937255859375, "success": true, "error": null}
2026-06-29 21:58:46,707 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00035834312438964844, "success": true, "error": null}
2026-06-29 21:59:46,759 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.056362152099609375, "success": true, "error": null}
2026-06-29 21:59:46,764 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.818771362304688e-05, "success": true, "error": null}
2026-06-29 21:59:50,045 [INFO] nina.scheduler: {"event": "job_run", "job": "gap_scanner", "duration": 3.2763543128967285, "success": true, "error": null}
2026-06-29 22:00:46,702 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 5.435943603515625e-05, "success": true, "error": null}
2026-06-29 22:01:46,702 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 6.29425048828125e-05, "success": true, "error": null}
2026-06-29 22:02:46,701 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 7.295608520507812e-05, "success": true, "error": null}
2026-06-29 22:03:46,709 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0002105236053466797, "success": true, "error": null}
2026-06-29 22:04:46,807 [INFO] nina.scheduler: {"event": "job_run", "job": "thermal_health", "duration": 0.10017776489257812, "success": true, "error": null}
2026-06-29 22:04:46,818 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00045680999755859375, "success": true, "error": null}
2026-06-29 22:04:48,737 [INFO] nina.scheduler: {"event": "job_run", "job": "gap_scanner", "duration": 1.9137375354766846, "success": true, "error": null}
2026-06-29 22:05:46,795 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.012124776840209961, "success": true, "error": null}
2026-06-29 22:06:46,709 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.00028634071350097656, "success": true, "error": null}
2026-06-29 22:07:46,704 [INFO] nina.scheduler: {"event": "job_run", "job": "reminder_check", "duration": 0.0001595020294189453, "success": true, "error": null}
2026-06-29 22:08:05,728 [INFO] nina.scheduler: Received signal 15, initiating graceful shutdown...
```

### logs/nina_mcp_results/diff_result.json
Last modified: 2026-06-25 15:43:04
Size: 17101 bytes
```log
{"slot":"diff_result","ts":"2026-06-21T19:20:07Z","result":{"ref":"HEAD","exit_code":0,"diff":"diff --git a/data/ninagate_cache.json b/data/ninagate_cache.json\nindex 9e26dfee..a3a6be38 100644\n--- a/data/ninagate_cache.json\n+++ b/data/ninagate_cache.json\n@@ -1 +1 @@\n-{}\n\\ No newline at end of file\n+{\"edbd4baf6e9981e5a9cae36d0af314c41cd5b8bd552e82cd58aba39184a2fe1a\": {\"response_data\": {\"id\": \"chatcmpl-dc805c94-fe91-4ce4-9f45-c9cd379a6a09\", \"object\": \"chat.completion\", \"created\": 1782069289, \"model\": \"llama-3.3-70b-versatile\", \"choices\": [{\"index\": 0, \"message\": {\"role\": \"assistant\", \"content\": \"Hello from Ninagate, where the mystical ninja world awaits, with stealthy greetings and covert hellos being sent your way.\"}, \"logprobs\": null, \"finish_reason\": \"stop\"}], \"usage\": {\"queue_time\": 0.346537513, \"prompt_tokens\": 43, \"prompt_time\": 0.002232636, \"completion_tokens\": 26, \"completion_time\": 0.138647508, \"total_tokens\": 69, \"total_time\": 0.140880144}, \"usage_breakdown\": null, \"system_fingerprint\": \"fp_ce7bc1685b\", \"x_groq\": {\"id\": \"req_01kvnspqk8e87sye4pb1desqn0\", \"seed\": 849254330}, \"service_tier\": \"on_demand\"}, \"expires_at\": 1782076489.088875, \"provider\": \"GROQ\"}, \"6fd54f74d38190bc170153bedb17445efd741af020d63dbb1958c3b614b56d36\": {\"response_data\": {\"id\": \"chatcmpl-e5356499-dc60-4841-aa29-c09ff92d7ac9\", \"object\": \"chat.completion\", \"created\": 1782069347, \"model\": \"llama-3.3-70b-versatile\", \"choices\": [{\"index\": 0, \"message\": {\"role\": \"assistant\", \"content\": \"Hi, how are you today?\"}, \"logprobs\": null, \"finish_reason\": \"stop\"}], \"usage\": {\"queue_time\": 0.111075137, \"prompt_tokens\": 37, \"prompt_time\": 0.005225163, \"completion_tokens\": 8, \"completion_time\": 0.034803387, \"total_tokens\": 45, \"total_time\": 0.04002855}, \"usage_breakdown\": null, \"system_fingerprint\": \"fp_dae98b5ecb\", \"x_groq\": {\"id\": \"req_01kvnsrh38e4b95whmf4x2bntx\", \"seed\": 1474794685}, \"service_tier\": \"on_demand\"}, \"expires_at\": 1782076547.6374588, \"provider\": \"GROQ\"}}\n\\ No newline at end of file\ndiff --git a/data/quota_state.json b/data/quota_state.json\nindex 7e031059..a360aaf9 100644\n--- a/data/quota_state.json\n+++ b/data/quota_state.json\n@@ -1 +1 @@\n-{\"quotas\": {\"gemini\": 0, \"groq\": 0, \"ollama\": 0, \"mistral\": 0, \"openrouter\": 0}, \"last_reset\": 1782025200.1703556, \"quota_exhausted\": false}\n\\ No newline at end of file\n+{\"quotas\": {\"gemini\": 0, \"groq\": 2, \"ollama\": 0, \"mistral\": 0, \"openrouter\": 0}, \"last_reset\": 1782025200.1703556}\n\\ No newline at end of file\ndiff --git a/logs/nina_mcp_results/status_result.json b/logs/nina_mcp_results/status_result.json\nindex feb216ba..0bef5a70 100644\n--- a/logs/nina_mcp_results/status_result.json\n+++ b/logs/nina_mcp_results/status_result.json\n@@ -1 +1 @@\n-{\"slot\":\"status_result\",\"ts\":\"2026-06-21T18:43:25Z\",\"result\":{\"nina_service_active\":\"active\",\"open_prs\":0,\"dirty_files\":2,\"sha\":\"e5c801613c0aa848276d6f217fce6f5266c5cedc\",\"service_status\":\"\\u25cf nina.service - NINA Autonomous Agent\\n     Loaded: loaded (/home/aibony/.config/systemd/user/nina.service; enabled; preset: enabled)\\n     Active: active (running) since Mon 2026-06-22 00:43:18 +06; 6s ago\\n Invocation: 2657140acc924b14a42ad4183f34536d\\n   Main PID: 551264 (python)\\n      Tasks: 2 (limit: 18333)\\n     Memory: 103.1M (peak: 119.1M)\\n        CPU: 1.164s\\n     CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/nina.service\\n             \\u2514\\u2500551264 /home/aibony/nina/venv/bin/python main.py\\n\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Scheduler started\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:nina.scheduler:Scheduler started \\u2014 27 jobs\\nJun 22 00:43:20 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:httpx:HTTP Request: POST https://api.telegram.org/bot8654166270:AAFm755yqYl77fuSulNmk9jV1GPsKTAV5xc/getMe \\\"HTTP/1.1 200 OK\\\"\",\"git_status\":\" M scripts/nina_sync.sh\\n?? scripts/cleanup.conf\",\"uptime\":\" 00:43:25 up  2:27,  1 user,  load average: 2.38, 1.75, 1.58\",\"disk\":\"/dev/sdb4       113G   54G   55G  50% /\",\"mem\":\"Mem:            14Gi       5.7Gi       2.4Gi       1.1Gi       7.6Gi       9.2Gi\"}}\n+{\"slot\":\"status_result\",\"ts\":\"2026-06-21T19:20:07Z\",\"result\":{\"nina_service_active\":\"active\",\"open_prs\":0,\"dirty_files\":4,\"sha\":\"2f9b9061161609dc7753328ba3ff438158b6482c\",\"service_status\":\"\\u25cf nina.service - NINA Autonomous Agent\\n     Loaded: loaded (/home/aibony/.config/systemd/user/nina.service; enabled; preset: enabled)\\n     Active: active (running) since Mon 2026-06-22 01:20:02 +06; 4s ago\\n Invocation: 254a72672c554c60bbf01c8cabded191\\n   Main PID: 566199 (python)\\n      Tasks: 2 (limit: 18333)\\n     Memory: 103.1M (peak: 118.8M)\\n        CPU: 1.269s\\n     CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/nina.service\\n             \\u2514\\u2500566199 /home/aibony/nina/venv/bin/python main.py\\n\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Scheduler started\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:nina.scheduler:Scheduler started \\u2014 27 jobs\\nJun 22 01:20:05 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:httpx:HTTP Request: POST https://api.telegram.org/bot8654166270:AAFm755yqYl77fuSulNmk9jV1GPsKTAV5xc/getMe \\\"HTTP/1.1 200 OK\\\"\",\"git_status\":\" M data/ninagate_cache.json\\n M data/quota_state.json\\n?? nina_test_mcp.sh\\n?? scripts/cleanup.conf\",\"uptime\":\" 01:20:07 up  3:03,  1 user,  load average: 1.71, 1.34, 1.23\",\"disk\":\"/dev/sdb4       113G   54G   55G  50% /\",\"mem\":\"Mem:            14Gi       6.1Gi       1.8Gi       1.1Gi       7.7Gi       8.8Gi\"}}\n---STAGED---\ndiff --git a/logs/nina_mcp_results/status_result.json b/logs/nina_mcp_results/status_result.json\nindex feb216ba..0bef5a70 100644\n--- a/logs/nina_mcp_results/status_result.json\n+++ b/logs/nina_mcp_results/status_result.json\n@@ -1 +1 @@\n-{\"slot\":\"status_result\",\"ts\":\"2026-06-21T18:43:25Z\",\"result\":{\"nina_service_active\":\"active\",\"open_prs\":0,\"dirty_files\":2,\"sha\":\"e5c801613c0aa848276d6f217fce6f5266c5cedc\",\"service_status\":\"\\u25cf nina.service - NINA Autonomous Agent\\n     Loaded: loaded (/home/aibony/.config/systemd/user/nina.service; enabled; preset: enabled)\\n     Active: active (running) since Mon 2026-06-22 00:43:18 +06; 6s ago\\n Invocation: 2657140acc924b14a42ad4183f34536d\\n   Main PID: 551264 (python)\\n      Tasks: 2 (limit: 18333)\\n     Memory: 103.1M (peak: 119.1M)\\n        CPU: 1.164s\\n     CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/nina.service\\n             \\u2514\\u2500551264 /home/aibony/nina/venv/bin/python main.py\\n\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:apscheduler.scheduler:Scheduler started\\nJun 22 00:43:19 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:nina.scheduler:Scheduler started \\u2014 27 jobs\\nJun 22 00:43:20 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[551264]: INFO:httpx:HTTP Request: POST https://api.telegram.org/bot8654166270:AAFm755yqYl77fuSulNmk9jV1GPsKTAV5xc/getMe \\\"HTTP/1.1 200 OK\\\"\",\"git_status\":\" M scripts/nina_sync.sh\\n?? scripts/cleanup.conf\",\"uptime\":\" 00:43:25 up  2:27,  1 user,  load average: 2.38, 1.75, 1.58\",\"disk\":\"/dev/sdb4       113G   54G   55G  50% /\",\"mem\":\"Mem:            14Gi       5.7Gi       2.4Gi       1.1Gi       7.6Gi       9.2Gi\"}}\n+{\"slot\":\"status_result\",\"ts\":\"2026-06-21T19:20:07Z\",\"result\":{\"nina_service_active\":\"active\",\"open_prs\":0,\"dirty_files\":4,\"sha\":\"2f9b9061161609dc7753328ba3ff438158b6482c\",\"service_status\":\"\\u25cf nina.service - NINA Autonomous Agent\\n     Loaded: loaded (/home/aibony/.config/systemd/user/nina.service; enabled; preset: enabled)\\n     Active: active (running) since Mon 2026-06-22 01:20:02 +06; 4s ago\\n Invocation: 254a72672c554c60bbf01c8cabded191\\n   Main PID: 566199 (python)\\n      Tasks: 2 (limit: 18333)\\n     Memory: 103.1M (peak: 118.8M)\\n        CPU: 1.269s\\n     CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/nina.service\\n             \\u2514\\u2500566199 /home/aibony/nina/venv/bin/python main.py\\n\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Added job \\\"_wrap_job.<locals>.wrapper\\\" to job store \\\"default\\\"\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:apscheduler.scheduler:Scheduler started\\nJun 22 01:20:04 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:nina.scheduler:Scheduler started \\u2014 27 jobs\\nJun 22 01:20:05 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[566199]: INFO:httpx:HTTP Request: POST https://api.telegram.org/bot8654166270:AAFm755yqYl77fuSulNmk9jV1GPsKTAV5xc/getMe \\\"HTTP/1.1 200 OK\\\"\",\"git_status\":\" M data/ninagate_cache.json\\n M data/quota_state.json\\n?? nina_test_mcp.sh\\n?? scripts/cleanup.conf\",\"uptime\":\" 01:20:07 up  3:03,  1 user,  load average: 1.71, 1.34, 1.23\",\"disk\":\"/dev/sdb4       113G   54G   55G  50% /\",\"mem\":\"Mem:            14Gi       6.1Gi       1.8Gi       1.1Gi       7.7Gi       8.8Gi\"}}"}}
```

### logs/nina_mcp_results/exec_result.json
Last modified: 2026-06-25 15:43:04
Size: 357 bytes
```log
{"slot":"exec_result","ts":"2026-06-21T19:25:41Z","result":{"cmd":"git -C ~/nina log --oneline -5","exit_code":0,"output":"b44381b9 chore: auto-regen index [skip ci]\nce7ca06e chore: auto-regen index [skip ci]\ne53675c5 mcp: update status_result.json [skip ci]\ncca63227 chore: auto-regen index [skip ci]\nd35e5af8 mcp: update exec_result.json [skip ci]"}}
```

### logs/nina_mcp_results/.gitkeep
Last modified: 2026-06-25 15:43:04
Size: 304 bytes
```log
# P0 GitHub Relay Bus — result slots written here by nina_mcp aliases
# Slots: exec_result.json | tail_result.json | diff_result.json | search_result.json | status_result.json
# ARCHITECT reads these via get_file_contents on demand.
# These files are intentionally committed to the repo for async RPC.
```

### logs/nina_mcp_results/status_result.json
Last modified: 2026-06-25 15:43:04
Size: 3393 bytes
```log
{"slot":"status_result","ts":"2026-06-21T19:23:04Z","result":{"nina_service_active":"active","open_prs":0,"dirty_files":4,"sha":"cca6322777926c0f584f8c95ad6243aec163a026","service_status":"\u25cf nina.service - NINA Autonomous Agent\n     Loaded: loaded (/home/aibony/.config/systemd/user/nina.service; enabled; preset: enabled)\n     Active: active (running) since Mon 2026-06-22 01:23:02 +06; 1s ago\n Invocation: 15fac4f0220c4a77af2d4948971af75f\n   Main PID: 568518 (python)\n      Tasks: 2 (limit: 18333)\n     Memory: 103.3M (peak: 103.3M)\n        CPU: 1.078s\n     CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/nina.service\n             \u2514\u2500568518 /home/aibony/nina/venv/bin/python main.py\n\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"\nJun 22 01:23:03 aibony-VivoBook-ASUSLaptop-X530FN-S530FN python[568518]: INFO:apscheduler.scheduler:Added job \"_wrap_job.<locals>.wrapper\" to job store \"default\"","git_status":" M data/ninagate_cache.json\n M data/quota_state.json\n?? nina_test_mcp.sh\n?? scripts/cleanup.conf","uptime":" 01:23:04 up  3:06,  1 user,  load average: 1.81, 1.97, 1.54","disk":"/dev/sdb4       113G   54G   55G  50% /","mem":"Mem:            14Gi       5.7Gi       2.2Gi       1.0Gi       7.6Gi       9.2Gi"}}
```

### logs/nina_mcp_results/tail_result.json
Last modified: 2026-06-25 15:43:04
Size: 6504 bytes
```log
{"slot":"tail_result","ts":"2026-06-21T19:20:07Z","result":{"log":"nina_sync","lines":100,"exit_code":0,"output":"2026-06-21 23:07:50  \u2500\u2500 ORIENT \u2500\u2500\n2026-06-21 23:07:50  sync_state=ahead \u2014 pull skipped\n2026-06-21 23:07:50  sync_state=ahead \u2014 pull skipped\n2026-06-21 23:07:50  new_sha=fd1a3d58bf2ec2de3caf70003ade6c5d49dbea69 changed=0 files\n2026-06-21 23:07:50  new_sha=fd1a3d58bf2ec2de3caf70003ade6c5d49dbea69 changed=0 files\n2026-06-21 23:07:50  \u2500\u2500 DECIDE \u2500\u2500\n2026-06-21 23:07:50  \u2500\u2500 DECIDE \u2500\u2500\n2026-06-21 23:07:50  index=false semantic=false doc_audit=false symlink=false registry=false intjm=false dead_code=true dup=true redundancy=false svc=false\n2026-06-21 23:07:50  index=false semantic=false doc_audit=false symlink=false registry=false intjm=false dead_code=true dup=true redundancy=false svc=false\n2026-06-21 23:07:50  \u2500\u2500 ACT \u2500\u2500\n2026-06-21 23:07:50  \u2500\u2500 ACT \u2500\u2500\n2026-06-21 23:07:50  dead-code scan (vulture)\u2026\n2026-06-21 23:07:50  dead-code scan (vulture)\u2026\n2026-06-21 23:07:52  dead-code items: 21 (unchanged)\n2026-06-21 23:07:52  dead-code items: 21 (unchanged)\n2026-06-21 23:07:52  duplicate file scan (hash + semantic)\u2026\n2026-06-21 23:07:52  duplicate file scan (hash + semantic)\u2026\n2026-06-21 23:08:36  duplicate scan: done (changed)\n2026-06-21 23:08:36  duplicate scan: done (changed)\n2026-06-21 23:15:01  hooks installed\n2026-06-21 23:15:01  hooks installed\n2026-06-21 23:15:01  \u2500\u2500 OBSERVE \u2500\u2500\n2026-06-21 23:15:06  sha=519b75739c38a5e73ef13ef68bbfc4ee1ffdc6fb state=behind open_prs=0 dirty=3 stash_depth=1\n2026-06-21 23:15:06  fs_snapshot: 14186 files/symlinks discovered\n2026-06-21 23:15:06  \u2500\u2500 ORIENT \u2500\u2500\n2026-06-21 23:15:06  new_sha=519b75739c38a5e73ef13ef68bbfc4ee1ffdc6fb changed=0 files\n2026-06-21 23:15:06  \u2500\u2500 DECIDE \u2500\u2500\n2026-06-21 23:15:06  index=false semantic=false doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true svc=false\n2026-06-21 23:15:06  \u2500\u2500 ACT \u2500\u2500\n2026-06-21 23:15:06  symlink audit\u2026\n2026-06-21 23:15:06  symlink audit: 0 broken (changed)\n2026-06-21 23:15:06  doc freshness audit\u2026\n2026-06-21 23:15:07  hygiene dashboard changed\n2026-06-21 23:15:07  registry orphan check\u2026\n2026-06-21 23:15:12  registry sync: 0 orphan files found\n2026-06-21 23:15:12  dead-code scan (vulture)\u2026\n2026-06-21 23:15:14  dead-code items: 21 (unchanged)\n2026-06-21 23:15:14  INTJ/INTM drift check\u2026\n2026-06-21 23:15:15  INTJ/INTM drift: 0 mirrors out of sync\n2026-06-21 23:15:15  duplicate file scan (hash + semantic)\u2026\n2026-06-21 23:15:57  duplicate scan: done (changed)\n2026-06-21 23:15:57  redundancy check\u2026\nredundancy check: 0 files flagged with no purpose\n2026-06-21 23:15:57  redundancy check done\n2026-06-21 23:15:57  nina.service: inactive \u2014 restarting\n2026-06-21 23:15:57  \u2705 OODA loop complete | mode=audit | state=behind | open_prs=0 | sha=519b75739c38a5e73ef13ef68bbfc4ee1ffdc6fb\n2026-06-21 23:16:40  hooks installed\n2026-06-21 23:16:40  hooks installed\n2026-06-21 23:16:40  \u2500\u2500 OBSERVE \u2500\u2500\n2026-06-21 23:16:45  sha=40825ec489a5bd9d3389a99c439474ff429baf0e state=diverged open_prs=0 dirty=2121 stash_depth=1\n2026-06-21 23:16:45  fs_snapshot: 14186 files/symlinks discovered\n2026-06-21 23:16:45  \u2500\u2500 ORIENT \u2500\u2500\n2026-06-21 23:16:45  new_sha=40825ec489a5bd9d3389a99c439474ff429baf0e changed=0 files\n2026-06-21 23:16:45  \u2500\u2500 DECIDE \u2500\u2500\n2026-06-21 23:16:45  index=false semantic=false doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true svc=false\n2026-06-21 23:16:45  \u2500\u2500 ACT \u2500\u2500\n2026-06-21 23:16:45  symlink audit\u2026\n2026-06-21 23:16:46  symlink audit: 0 broken (changed)\n2026-06-21 23:16:46  doc freshness audit\u2026\n2026-06-21 23:16:47  hygiene dashboard changed\n2026-06-21 23:16:47  registry orphan check\u2026\n2026-06-21 23:16:52  registry sync: 0 orphan files found\n2026-06-21 23:16:52  dead-code scan (vulture)\u2026\n2026-06-21 23:16:54  dead-code items: 21 (unchanged)\n2026-06-21 23:16:54  INTJ/INTM drift check\u2026\n2026-06-21 23:16:54  INTJ/INTM drift: 0 mirrors out of sync\n2026-06-21 23:16:54  duplicate file scan (hash + semantic)\u2026\n2026-06-21 23:17:36  duplicate scan: done (changed)\n2026-06-21 23:17:36  redundancy check\u2026\nredundancy check: 0 files flagged with no purpose\n2026-06-21 23:17:36  redundancy check done\n2026-06-21 23:17:36  nina.service: inactive \u2014 restarting\n2026-06-21 23:17:36  \u2705 OODA loop complete | mode=audit | state=diverged | open_prs=0 | sha=40825ec489a5bd9d3389a99c439474ff429baf0e\n2026-06-21 23:37:06  hooks installed\n2026-06-21 23:37:06  hooks installed\n2026-06-21 23:37:06  \u2500\u2500 OBSERVE \u2500\u2500\n2026-06-21 23:37:11  sha=8e67ee315a2153a3c59efb3b232bd1caa175751e state=ahead open_prs=0 dirty=2128 stash_depth=2\n2026-06-21 23:37:11  fs_snapshot: 14132 files/symlinks discovered\n2026-06-21 23:37:11  \u2500\u2500 ORIENT \u2500\u2500\n2026-06-21 23:37:11  new_sha=8e67ee315a2153a3c59efb3b232bd1caa175751e changed=0 files\n2026-06-21 23:37:11  \u2500\u2500 DECIDE \u2500\u2500\n2026-06-21 23:37:11  index=false semantic=false doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true svc=false\n2026-06-21 23:37:11  \u2500\u2500 ACT \u2500\u2500\n2026-06-21 23:37:11  symlink audit\u2026\n2026-06-21 23:37:11  symlink audit: 0 broken (changed)\n2026-06-21 23:37:11  doc freshness audit\u2026\n2026-06-21 23:37:12  hygiene dashboard changed\n2026-06-21 23:37:12  registry orphan check\u2026\n2026-06-21 23:37:17  registry sync: 1 orphan files found\n2026-06-21 23:37:17  dead-code scan (vulture)\u2026\n2026-06-21 23:37:20  dead-code items: 21 (unchanged)\n2026-06-21 23:37:20  INTJ/INTM drift check\u2026\n2026-06-21 23:37:20  INTJ/INTM drift: 0 mirrors out of sync\n2026-06-21 23:37:20  duplicate file scan (hash + semantic)\u2026\n2026-06-21 23:38:01  duplicate scan: done (changed)\n2026-06-21 23:38:01  redundancy check\u2026\nredundancy check: 0 files flagged with no purpose\n2026-06-21 23:38:02  redundancy check done\n2026-06-21 23:38:02  nina.service: active\n2026-06-21 23:38:02  \u2705 OODA loop complete | mode=audit | state=ahead | open_prs=0 | sha=8e67ee315a2153a3c59efb3b232bd1caa175751e"}}
```

### logs/nina_sync.log
Last modified: 2026-06-29 22:33:09
Size: 326799 bytes
```log
[truncated — showing last 200 lines]
2026-06-29 22:22:41  ── ACT ──
2026-06-29 22:22:41  symlink audit…
2026-06-29 22:22:42  symlink audit: 0 broken (changed)
2026-06-29 22:22:42  regenerating nina_index…
🔍 Scanning repository...
✅ Discovered 2137 governed files.
  📊 Reconcile: 0 exempted, 0 real gaps.
💾 Written: docs/space/nina_index.json
💾 Written: docs/space/nina_index.md
✅ Dependency graph updated: data/dependency_graph.json
✅ Symbol map updated: data/symbol_map.json

✅ Index generation complete (idempotent, SSoT v15.2).
2026-06-29 22:22:55  index updated
2026-06-29 22:22:55  semantic AST index…
semantic index: 80 entries updated
2026-06-29 22:22:56  semantic index updated
2026-06-29 22:22:56  doc freshness audit…
2026-06-29 22:22:57  hygiene dashboard changed
2026-06-29 22:22:57  registry orphan check…
2026-06-29 22:23:06  registry sync: 0 orphan files found
2026-06-29 22:23:06  dead-code scan (vulture)…
2026-06-29 22:23:16  dead-code items: 11 (changed)
2026-06-29 22:23:16  INTJ/INTM drift check…
2026-06-29 22:23:17  INTJ/INTM drift: 0 mirrors out of sync
2026-06-29 22:23:17  duplicate file scan (hash + semantic)…
2026-06-29 22:23:35  duplicate scan: done (changed)
2026-06-29 22:23:35  redundancy check…
redundancy check: 0 files flagged with no purpose
2026-06-29 22:23:36  redundancy check done
2026-06-29 22:23:36  backup check (stamp-guard 6h)…
2026-06-29 22:23:36  backup skipped (last run 950s ago — within 6h window)
2026-06-29 22:23:36  staging artefacts…
hint: The 'git-hooks/post-commit' hook was ignored because it's not set as executable.
hint: You can disable this warning with `git config set advice.ignoredHook false`.
[main 16fa6b67] chore(auto): OODA sync 2026-06-29 22:23:36 [skip ci]
 7 files changed, 2657 insertions(+), 2643 deletions(-)
2026-06-29 22:23:36  artefacts committed
To github.com:aibony/nina.git
   725d75a8..16fa6b67  main -> main
2026-06-29 22:23:41  pushed to origin/main
2026-06-29 22:23:41  nina.service: active
2026-06-29 22:23:41  ✅ OODA loop complete | mode=all | state=up-to-date | open_prs=0 | sha=725d75a816aa1c90e15c97db3853aa2f3f617d3f
2026-06-29 22:27:23  hooks installed
2026-06-29 22:27:23  ── OBSERVE ──
2026-06-29 22:27:27  sha=16fa6b6776c46b151be7fcf0754b0aa0b7e9cc97 state=up-to-date open_prs=0 dirty=2 stash_depth=5
2026-06-29 22:27:27  fs_snapshot: 2122 files/symlinks discovered
2026-06-29 22:27:27  ── ORIENT ──
2026-06-29 22:27:27  sync_state=up-to-date — pull skipped
2026-06-29 22:27:27  new_sha=16fa6b6776c46b151be7fcf0754b0aa0b7e9cc97 changed=0 files
2026-06-29 22:27:27  ── DECIDE ──
2026-06-29 22:27:27  index=true semantic=true doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true backup=true svc=false
2026-06-29 22:27:27  ── ACT ──
2026-06-29 22:27:27  symlink audit…
2026-06-29 22:27:28  symlink audit: 0 broken (changed)
2026-06-29 22:27:28  regenerating nina_index…
🔍 Scanning repository...
✅ Discovered 2138 governed files.
  📊 Reconcile: 0 exempted, 0 real gaps.
💾 Written: docs/space/nina_index.json
💾 Written: docs/space/nina_index.md
✅ Dependency graph updated: data/dependency_graph.json
✅ Symbol map updated: data/symbol_map.json

✅ Index generation complete (idempotent, SSoT v15.2).
2026-06-29 22:27:43  index updated
2026-06-29 22:27:43  semantic AST index…
semantic index: 74 entries updated
2026-06-29 22:27:43  semantic index updated
2026-06-29 22:27:43  doc freshness audit…
2026-06-29 22:27:45  hygiene dashboard changed
2026-06-29 22:27:45  registry orphan check…
2026-06-29 22:27:48  registry sync: 0 orphan files found
2026-06-29 22:27:48  dead-code scan (vulture)…
2026-06-29 22:27:50  dead-code items: 12 (changed)
2026-06-29 22:27:50  INTJ/INTM drift check…
2026-06-29 22:27:50  INTJ/INTM drift: 0 mirrors out of sync
2026-06-29 22:27:50  duplicate file scan (hash + semantic)…
2026-06-29 22:28:02  duplicate scan: done (changed)
2026-06-29 22:28:02  redundancy check…
redundancy check: 0 files flagged with no purpose
2026-06-29 22:28:02  redundancy check done
2026-06-29 22:28:02  backup check (stamp-guard 6h)…
2026-06-29 22:28:02  backup skipped (last run 1216s ago — within 6h window)
2026-06-29 22:28:02  staging artefacts…
hint: The 'git-hooks/post-commit' hook was ignored because it's not set as executable.
hint: You can disable this warning with `git config set advice.ignoredHook false`.
[main 274f3a4e] chore(auto): OODA sync 2026-06-29 22:28:02 [skip ci]
 10 files changed, 3802 insertions(+), 3720 deletions(-)
2026-06-29 22:28:02  artefacts committed
To github.com:aibony/nina.git
   16fa6b67..274f3a4e  main -> main
2026-06-29 22:28:07  pushed to origin/main
2026-06-29 22:28:07  nina.service: active
2026-06-29 22:28:07  ✅ OODA loop complete | mode=all | state=up-to-date | open_prs=0 | sha=16fa6b6776c46b151be7fcf0754b0aa0b7e9cc97
2026-06-29 22:31:44  hooks installed
2026-06-29 22:31:44  hooks installed
2026-06-29 22:31:44  ── OBSERVE ──
2026-06-29 22:31:50  sha=274f3a4eb3277bf393759e412674575bb11cd5c2 state=up-to-date open_prs=0 dirty=10 stash_depth=5
2026-06-29 22:31:53  fs_snapshot: 2122 files/symlinks discovered
2026-06-29 22:31:54  ── ORIENT ──
2026-06-29 22:31:54  new_sha=274f3a4eb3277bf393759e412674575bb11cd5c2 changed=0 files
2026-06-29 22:31:54  ── DECIDE ──
2026-06-29 22:31:54  index=false semantic=false doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true backup=false svc=false
2026-06-29 22:31:54  ── ACT ──
2026-06-29 22:31:54  symlink audit…
2026-06-29 22:31:56  hooks installed
2026-06-29 22:31:56  ── OBSERVE ──
2026-06-29 22:31:56  symlink audit: 0 broken (changed)
2026-06-29 22:31:56  doc freshness audit…
2026-06-29 22:32:01  sha=274f3a4eb3277bf393759e412674575bb11cd5c2 state=up-to-date open_prs=0 dirty=1 stash_depth=5
2026-06-29 22:32:02  hygiene dashboard changed
2026-06-29 22:32:02  fs_snapshot: 2122 files/symlinks discovered
2026-06-29 22:32:02  registry orphan check…
2026-06-29 22:32:02  ── ORIENT ──
2026-06-29 22:32:02  sync_state=up-to-date — pull skipped
2026-06-29 22:32:02  new_sha=274f3a4eb3277bf393759e412674575bb11cd5c2 changed=0 files
2026-06-29 22:32:02  ── DECIDE ──
2026-06-29 22:32:02  index=true semantic=true doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true backup=true svc=false
2026-06-29 22:32:02  ── ACT ──
2026-06-29 22:32:02  symlink audit…
2026-06-29 22:32:04  symlink audit: 0 broken (changed)
2026-06-29 22:32:04  regenerating nina_index…
🔍 Scanning repository...
2026-06-29 22:32:09  registry sync: 0 orphan files found
2026-06-29 22:32:09  dead-code scan (vulture)…
✅ Discovered 2138 governed files.
  📊 Reconcile: 0 exempted, 0 real gaps.
💾 Written: docs/space/nina_index.json
💾 Written: docs/space/nina_index.md
2026-06-29 22:32:12  dead-code items: 12 (unchanged)
2026-06-29 22:32:12  INTJ/INTM drift check…
2026-06-29 22:32:12  INTJ/INTM drift: 0 mirrors out of sync
2026-06-29 22:32:12  duplicate file scan (hash + semantic)…
2026-06-29 22:32:26  duplicate scan: done (changed)
2026-06-29 22:32:26  redundancy check…
redundancy check: 0 files flagged with no purpose
2026-06-29 22:32:26  redundancy check done
2026-06-29 22:32:26  nina.service: active
2026-06-29 22:32:26  ✅ OODA loop complete | mode=audit | state=up-to-date | open_prs=0 | sha=274f3a4eb3277bf393759e412674575bb11cd5c2
✅ Dependency graph updated: data/dependency_graph.json
✅ Symbol map updated: data/symbol_map.json

✅ Index generation complete (idempotent, SSoT v15.2).
2026-06-29 22:32:31  index updated
2026-06-29 22:32:31  semantic AST index…
semantic index: 75 entries updated
2026-06-29 22:32:31  semantic index updated
2026-06-29 22:32:31  doc freshness audit…
2026-06-29 22:32:32  hygiene dashboard changed
2026-06-29 22:32:32  registry orphan check…
2026-06-29 22:32:35  registry sync: 0 orphan files found
2026-06-29 22:32:35  dead-code scan (vulture)…
2026-06-29 22:32:37  dead-code items: 12 (unchanged)
2026-06-29 22:32:37  INTJ/INTM drift check…
2026-06-29 22:32:37  INTJ/INTM drift: 0 mirrors out of sync
2026-06-29 22:32:37  duplicate file scan (hash + semantic)…
2026-06-29 22:32:44  hooks installed
2026-06-29 22:32:44  ── OBSERVE ──
2026-06-29 22:32:49  sha=274f3a4eb3277bf393759e412674575bb11cd5c2 state=up-to-date open_prs=0 dirty=1 stash_depth=5
2026-06-29 22:32:49  fs_snapshot: 2122 files/symlinks discovered
2026-06-29 22:32:49  ── ORIENT ──
2026-06-29 22:32:49  new_sha=274f3a4eb3277bf393759e412674575bb11cd5c2 changed=0 files
2026-06-29 22:32:49  ── DECIDE ──
2026-06-29 22:32:49  index=false semantic=false doc_audit=true symlink=true registry=true intjm=true dead_code=true dup=true redundancy=true backup=false svc=false
2026-06-29 22:32:49  ── ACT ──
2026-06-29 22:32:49  symlink audit…
2026-06-29 22:32:50  symlink audit: 0 broken (changed)
2026-06-29 22:32:50  doc freshness audit…
2026-06-29 22:32:52  duplicate scan: done (changed)
2026-06-29 22:32:52  redundancy check…
redundancy check: 0 files flagged with no purpose
2026-06-29 22:32:53  redundancy check done
2026-06-29 22:32:53  backup check (stamp-guard 6h)…
2026-06-29 22:32:53  backup skipped (last run 1507s ago — within 6h window)
2026-06-29 22:32:53  staging artefacts…
hint: The 'git-hooks/post-commit' hook was ignored because it's not set as executable.
hint: You can disable this warning with `git config set advice.ignoredHook false`.
2026-06-29 22:32:53  hygiene dashboard changed
[main 09d8314a] chore(auto): OODA sync 2026-06-29 22:32:53 [skip ci]
 2 files changed, 2 insertions(+), 2 deletions(-)
2026-06-29 22:32:53  registry orphan check…
2026-06-29 22:32:53  artefacts committed
2026-06-29 22:32:55  registry sync: 0 orphan files found
2026-06-29 22:32:56  dead-code scan (vulture)…
To github.com:aibony/nina.git
   274f3a4e..09d8314a  main -> main
2026-06-29 22:32:57  pushed to origin/main
2026-06-29 22:32:57  nina.service: active
2026-06-29 22:32:57  ✅ OODA loop complete | mode=all | state=up-to-date | open_prs=0 | sha=274f3a4eb3277bf393759e412674575bb11cd5c2
2026-06-29 22:32:58  dead-code items: 12 (unchanged)
2026-06-29 22:32:58  INTJ/INTM drift check…
2026-06-29 22:32:58  INTJ/INTM drift: 0 mirrors out of sync
2026-06-29 22:32:58  duplicate file scan (hash + semantic)…
2026-06-29 22:33:09  duplicate scan: done (changed)
2026-06-29 22:33:09  redundancy check…
redundancy check: 0 files flagged with no purpose
2026-06-29 22:33:09  redundancy check done
2026-06-29 22:33:09  nina.service: active
2026-06-29 22:33:09  ✅ OODA loop complete | mode=audit | state=up-to-date | open_prs=0 | sha=274f3a4eb3277bf393759e412674575bb11cd5c2
```

### logs/nina_update_log.md
Last modified: 2026-06-29 22:31:42
Size: 1166 bytes
```log

---

## Entry 001 — 2026-06-25 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/dependency_graph.json,docs/space/PERPLEXITY_SPACE_INSTRUCTIONS.md,docs/space/README.md,docs/space/nina_file_registry.json,docs/space/nina_index.json,docs/space/nina_index.md,docs/space/nina_repo_hygiene_dashboard.md

**Verification:** git push OK, nina.service active

---

## Entry 002 — 2026-06-26 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** data/gemini_scratch.jsonl,data/supply_snapshot.json,docs/context/nina_update_log.md,docs/space/PERPLEXITY_SPACE_INSTRUCTIONS.md,docs/space/README.md

**Verification:** git push OK, nina.service inactive

---

## Entry 003 — 2026-06-29 · D-sync Post-session sync

**Triggered by:** nina_sync.sh v5 automated run

**Files changed:** core/knowledge_graph.py,data/gemini_scratch.jsonl,data/supply_snapshot.json,docs/context/nina_session_log.md,docs/space/PERPLEXITY_SPACE_INSTRUCTIONS.md,docs/space/README.md,ninagate/data/supply_snapshot.json,tests/test_knowledge_graph_mcp.py

**Verification:** git push OK, nina.service inactive
```

### logs/registry_orphans.txt
Last modified: 2026-06-29 22:18:37
Size: 69234 bytes
```log
[truncated — showing last 200 lines]
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_194159.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_230449.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_230953.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_231453.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_231948.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_232444.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_232952.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_233450.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_233746.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_233952.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_234252.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_234441.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_234857.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_235201.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_235350.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_235755.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260618_235849.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_000348.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_000845.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_001300.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_001745.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_002202.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_002653.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_003145.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_003646.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_004144.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_004646.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_005155.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_005648.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_010146.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_010648.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_011147.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_011651.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_012145.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_012652.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_013147.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_013752.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_014250.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_014742.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_015200.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_015650.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_020147.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_100054.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_100548.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_101053.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_101557.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_102103.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_102601.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_103140.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_103637.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_104149.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_104644.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_105154.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_105644.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_110138.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_110649.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_111240.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_111748.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_112247.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_112744.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_113257.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_113852.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_114356.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_114857.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_115355.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_115857.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_120400.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_121044.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_121640.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_122143.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_122646.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_123151.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_123646.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_124225.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_124654.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_125147.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_125651.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_130145.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_130651.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_135848.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_140440.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_140743.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_140945.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_141453.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_141854.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_141956.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_142459.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_142649.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_143159.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_143356.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_143545.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_143856.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_144258.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_144559.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_145003.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_145332.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_145749.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_150044.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_150453.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_150750.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_151055.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_151454.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_151755.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_152151.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_152501.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_152929.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_153203.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_153554.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_153936.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_154300.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_154657.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_155000.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_155449.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_155701.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_160157.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_160859.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_161142.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_161854.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_162158.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_162557.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_162857.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_163328.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_163635.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_164100.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_164344.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_164701.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_165048.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_165358.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_165759.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_170242.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_170501.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_170803.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_171245.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_171546.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_171856.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_172246.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_172631.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_172942.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_173254.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_173700.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_173958.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_174440.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_174704.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_175200.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_175442.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_175758.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_180147.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_180503.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_180943.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_181158.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_181548.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_181856.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_182339.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_182559.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_183039.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_183333.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_183656.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_184045.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_184401.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_184748.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_185059.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_185544.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_185759.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_190159.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_190502.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_191939.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_192258.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_192651.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_192959.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_193351.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_193657.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_194138.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260619_194402.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_031954.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_034753.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_035742.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_040755.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_131641.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_131655.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_131740.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_160741.md
DELETED_FROM_FS: upgrades/backups/nina_codebase_backup_20260621_175340.md
DELETED_FROM_FS: upgrades/backups/nina_update_log.bak.20260606_125916
DELETED_FROM_FS: upgrades/backups/nina_update_log.bak.20260606_201959
DELETED_FROM_FS: upgrades/backups/py_20260606030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260609030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260611030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260612030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260613030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260614030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260615030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260616030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260617030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260618030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260621030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260624030000.zip
DELETED_FROM_FS: upgrades/backups/py_20260625030000.zip
DELETED_FROM_FS: upgrades/backups/py_manual_20260522120938.zip
DELETED_FROM_FS: upgrades/backups/root_bak_cleanup/nina-guardian old.sh
registry sync complete: 6 new, 958 deleted, 3079 total
```

### logs/router.log
Last modified: 2026-06-26 00:03:17
Size: 1782 bytes
```log
{"event": "route_start", "span_id": "c4a275ff", "task_type": "sensitive", "estimated_tokens": 507, "stream": false, "force_local": true, "ts": "2026-06-25T16:46:08.274103+0000"}
{"event": "route_exhausted", "span_id": "c4a275ff", "task_type": "sensitive", "ts": "2026-06-25T16:46:29.622612+0000"}
{"event": "route_start", "span_id": "8a5d1d14", "task_type": "sensitive", "estimated_tokens": 326, "stream": false, "force_local": true, "ts": "2026-06-25T16:48:12.626321+0000"}
{"event": "route_exhausted", "span_id": "8a5d1d14", "task_type": "sensitive", "ts": "2026-06-25T16:48:14.795513+0000"}
{"event": "route_start", "span_id": "cbce02dc", "task_type": "sensitive", "estimated_tokens": 507, "stream": false, "force_local": true, "ts": "2026-06-25T17:17:29.937976+0000"}
{"event": "route_exhausted", "span_id": "cbce02dc", "task_type": "sensitive", "ts": "2026-06-25T17:17:36.591032+0000"}
{"event": "route_start", "span_id": "3f7ac40c", "task_type": "sensitive", "estimated_tokens": 326, "stream": false, "force_local": true, "ts": "2026-06-25T17:18:12.586289+0000"}
{"event": "route_exhausted", "span_id": "3f7ac40c", "task_type": "sensitive", "ts": "2026-06-25T17:18:13.651202+0000"}
{"event": "route_start", "span_id": "7553e02d", "task_type": "sensitive", "estimated_tokens": 507, "stream": false, "force_local": true, "ts": "2026-06-25T17:48:36.915672+0000"}
{"event": "route_exhausted", "span_id": "7553e02d", "task_type": "sensitive", "ts": "2026-06-25T17:48:42.225073+0000"}
{"event": "route_start", "span_id": "7ceb1b3f", "task_type": "sensitive", "estimated_tokens": 326, "stream": false, "force_local": true, "ts": "2026-06-25T18:03:12.589461+0000"}
{"event": "route_exhausted", "span_id": "7ceb1b3f", "task_type": "sensitive", "ts": "2026-06-25T18:03:17.534027+0000"}
```

### logs/security.log
Last modified: 2026-06-25 15:09:35
Size: 0 bytes
```log
```

### logs/symlink_audit.txt
Last modified: 2026-06-29 22:32:50
Size: 521 bytes
```log
# Symlink Audit — 2026-06-29 22:32:49

## Broken/Dangling symlinks

## All symlinks
  [OK] .agy/skills/NINA-RULES/SKILL.md -> ../../../docs/context/NINA_RULES.md
  [OK] .agy/skills/NINA-OPS/SKILL.md -> ../../../docs/context/NINA_OPS.md
  [OK] .agy/skills/NINA-WORKFLOW/SKILL.md -> ../../../docs/context/NINA_WORKFLOW.md
  [OK] GEMINI.md -> docs/context/NINA_AGENT_PRIMER.md
  [OK] AGENTS.md -> docs/context/NINA_AGENT_PRIMER.md
  [OK] bin/agy -> nina-universal-wrapper.sh
  [OK] bin/gemini -> nina-universal-wrapper.sh
```

### logs/tools.log
Last modified: 2026-06-26 00:03:21
Size: 519 bytes
```log
2026-06-26 00:03:12,584 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-26 00:03:12,585 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-26 00:03:18,680 [INFO] nina.tools.jules: goal_to_backlog: added B-017 to backlog
2026-06-26 00:03:21,426 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-26 00:03:21,426 [ERROR] nina.tools.jules: API Error: 
2026-06-26 00:03:21,427 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
```

### logs/tools.log.2026-06-25
Last modified: 2026-06-25 23:48:16
Size: 2701 bytes
```log
2026-06-25 22:48:12,597 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 22:48:12,617 [ERROR] nina.tools.jules: Jules Pipeline Watchdog: Backlog format drift detected!
2026-06-25 22:48:14,512 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 22:48:17,035 [INFO] nina.tools.jules: goal_to_backlog: added B-012 to backlog
2026-06-25 22:48:20,230 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 22:48:20,230 [ERROR] nina.tools.jules: API Error: 
2026-06-25 22:48:20,231 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-25 23:03:12,596 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 23:03:12,598 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 23:03:14,135 [INFO] nina.tools.jules: goal_to_backlog: added B-013 to backlog
2026-06-25 23:03:17,176 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 23:03:17,177 [ERROR] nina.tools.jules: API Error: 
2026-06-25 23:03:17,178 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-25 23:18:12,580 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 23:18:12,582 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 23:18:14,604 [INFO] nina.tools.jules: goal_to_backlog: added B-014 to backlog
2026-06-25 23:18:17,274 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 23:18:17,274 [ERROR] nina.tools.jules: API Error: 
2026-06-25 23:18:17,275 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-25 23:33:12,571 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 23:33:12,573 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 23:33:13,446 [INFO] nina.tools.jules: goal_to_backlog: added B-015 to backlog
2026-06-25 23:33:16,459 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 23:33:16,459 [ERROR] nina.tools.jules: API Error: 
2026-06-25 23:33:16,460 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
2026-06-25 23:48:12,582 [INFO] nina.tools.jules: Jules Pipeline Watchdog Start
2026-06-25 23:48:12,583 [INFO] nina.tools.jules: Jules Pipeline Watchdog Complete
2026-06-25 23:48:13,653 [INFO] nina.tools.jules: goal_to_backlog: added B-016 to backlog
2026-06-25 23:48:16,371 [INFO] nina.tools.jules: API POST https://jules.googleapis.com/v1alpha1/sessions -> 404
2026-06-25 23:48:16,371 [ERROR] nina.tools.jules: API Error: 
2026-06-25 23:48:16,372 [INFO] nina.tools.jules: goal_to_backlog: dispatched as Jules session 
```

### logs/upgrade.log
Last modified: 2026-06-29 22:33:46
Size: 871 bytes
```log
2026-06-29 21:54:46,687 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:08:08,508 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:10:39,725 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:13:07,058 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:15:22,679 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:17:35,376 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:19:50,789 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:22:07,563 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:24:24,523 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:26:41,048 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:29:22,200 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:31:29,672 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-29 22:33:46,072 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-04-16
Last modified: 2026-04-16 00:33:12
Size: 5226 bytes
```log
2026-06-25 15:09:36,192 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:11:52,539 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:14:08,844 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:16:25,425 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:18:41,991 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:21:00,851 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:23:15,333 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:25:31,965 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:27:49,173 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:30:12,789 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:32:22,480 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:32:44,928 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:35:03,817 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:37:18,167 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:39:34,825 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:41:54,756 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:44:08,620 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:44:20,626 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:46:36,902 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:48:50,978 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:51:16,957 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:53:35,945 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:55:53,304 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 15:58:07,576 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:00:27,272 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:02:42,563 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:04:58,060 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:07:19,812 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:09:28,242 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:11:45,644 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:13:54,159 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:16:08,648 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:18:34,852 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:20:42,241 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:21:08,349 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:23:28,280 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:25:41,965 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:27:57,942 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:30:14,687 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:32:32,554 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:34:49,311 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:37:05,566 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:39:22,049 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:41:39,332 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:43:55,292 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:46:12,257 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:48:30,414 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:50:47,075 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:53:07,863 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:55:21,948 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:57:40,947 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 16:59:58,160 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:02:20,657 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:04:39,612 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:06:32,976 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:08:50,118 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:11:06,765 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:13:21,589 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:15:39,098 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:18:06,188 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:20:19,793 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:22:44,247 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:24:51,470 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 17:27:05,935 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:11:37,875 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:16:17,119 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:18:33,457 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:20:49,077 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:23:05,568 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:25:22,119 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:27:38,643 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:29:55,050 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:32:11,747 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:34:30,970 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:36:45,100 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:39:01,642 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-25 22:41:18,021 [INFO] nina.upgrade: UpgradePipeline ready
2026-04-16 00:33:12,488 [INFO] nina.upgrade: UpgradePipeline ready
```

### logs/upgrade.log.2026-06-26
Last modified: 2026-06-26 05:00:04
Size: 8710 bytes
```log
2026-06-26 00:10:03,704 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:12:19,291 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:14:36,735 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:16:52,492 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:19:08,440 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:21:25,007 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:23:41,372 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:25:57,966 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:28:14,691 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:30:31,328 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:32:48,627 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:35:04,436 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:37:12,988 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:39:33,597 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:41:50,103 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:44:06,623 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:46:23,053 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:48:40,072 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:50:56,424 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:53:12,762 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:55:29,797 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 00:57:46,044 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:00:02,265 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:02:14,542 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:04:31,060 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:06:47,306 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:09:03,817 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:11:20,396 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:13:36,836 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:15:53,204 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:18:06,475 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:20:22,822 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:22:39,258 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:24:55,785 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:27:12,284 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:29:28,800 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:31:45,291 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:34:01,731 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:36:18,231 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:38:25,978 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:40:42,298 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:42:58,748 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:45:15,334 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:47:31,718 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:49:47,973 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:52:04,517 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:54:11,181 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:56:27,507 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 01:58:43,973 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:01:00,692 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:03:17,179 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:05:33,558 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:07:50,377 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:10:06,977 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:12:23,296 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:14:39,576 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:16:56,089 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:19:11,702 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:21:28,502 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:23:38,184 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:25:54,258 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:28:10,296 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:30:26,822 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:32:43,361 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:34:59,840 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:37:16,490 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:39:32,915 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:41:49,350 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:44:05,855 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:46:22,445 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:48:38,787 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:50:55,341 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:53:11,852 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:55:28,374 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:57:29,792 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 02:59:46,145 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:02:02,642 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:04:19,088 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:06:35,549 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:08:52,266 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:11:08,650 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:13:25,072 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:15:41,542 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:17:58,101 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:20:14,363 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:22:30,868 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:24:47,423 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:27:03,893 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:29:20,387 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:31:22,310 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:33:38,971 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:35:55,285 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:38:11,696 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:40:28,111 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:42:44,604 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:45:01,156 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:47:17,658 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:49:34,072 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:51:50,592 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:54:07,277 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:56:23,539 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 03:58:40,169 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:00:56,517 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:03:13,147 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:05:16,212 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:07:32,637 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:09:49,106 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:12:05,660 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:14:22,096 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:16:38,650 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:18:55,093 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:21:11,701 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:23:28,096 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:25:44,593 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:28:01,106 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:30:17,508 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:32:34,192 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:34:50,536 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:37:07,125 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:39:13,904 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:41:30,395 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:43:46,863 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:44:09,134 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:46:25,599 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:48:42,115 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:50:58,620 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:53:15,202 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:55:31,876 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 04:57:48,341 [INFO] nina.upgrade: UpgradePipeline ready
2026-06-26 05:00:04,741 [INFO] nina.upgrade: UpgradePipeline ready
```

