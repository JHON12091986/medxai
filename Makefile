# Nina Makefile — all runnable targets for tools, checks, and SSOT ops
# Run `make help` to see all available targets.
# NINA_FEATURE: makefile-enriched v1.0

PYTHON := ./venv/bin/python3
REPO   := $(shell pwd)

.PHONY: help install test lint audit sync dedup semantic-dedup telemetry \
        agent-context cron-status memory-update bench export ssot-diff \
        check-all warm-cache guardian clean

help: ## Show all available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*##"}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies into venv
	python3 -m venv venv && ./venv/bin/pip install -r requirements.txt

test: ## Run full pytest suite
	$(PYTHON) -m pytest

lint: ## Run pyflakes on all Python files
	@find . -name '*.py' -not -path './venv/*' -not -path './.cache/*' \
		| xargs $(PYTHON) -m pyflakes 2>&1 | grep -v '^$$' || true

audit: ## Run full OODA audit (nina_sync.sh audit)
	bash scripts/nina_sync.sh audit
	sync: ## Run nina_sync.sh (index regen + governance)
	bash scripts/nina_sync.sh

dedup: ## Incremental hash-cache duplicate scan
	$(PYTHON) tools/dedup_scan.py

semantic-dedup: ## GPU semantic near-duplicate scan via Ollama (needs nomic-embed-text)
	$(PYTHON) tools/semantic_dedup.py

telemetry: ## Digest telemetry.jsonl → report
	$(PYTHON) tools/telemetry_digest.py

telemetry-export: ## Digest + write to exports/telemetry_digest.json
	$(PYTHON) tools/telemetry_digest.py --export

agent-context: ## Write data/agent_context.json (post-OODA snapshot)
	$(PYTHON) tools/agent_context_writer.py

cron-status: ## Check cron job health stamps
	$(PYTHON) tools/cron_sentinel.py --check

memory-update: ## Auto-patch MEMORY.md from nina_update_log.md
	$(PYTHON) tools/update_memory.py

bench: ## Latency-benchmark NinaGate providers → rewrite providers.json
	$(PYTHON) tools/bench_providers.py

bench-dry: ## Benchmark providers without rewriting providers.json
	$(PYTHON) tools/bench_providers.py --dry-run

export: ## Snapshot full Nina state → exports/nina_state_YYYYMMDD.json
	$(PYTHON) tools/export_snapshot.py --pretty

ssot-diff: ## Show SSOT files changed since last push
	@git diff origin/main --name-only 2>/dev/null | grep -E '(nina_index|dependency_graph|nina_update_log|MEMORY|agent_context)' || echo 'No SSOT changes since last push'

check-all: ## Run all checks/ scripts in parallel
	@echo 'Running all checks in parallel...'; \
	pids=''; \
	for f in checks/*.sh checks/*.py; do \
		[ -f "$$f" ] || continue; \
		echo "  Starting $$f"; \
		case $$f in *.sh) bash $$f & ;; *.py) $(PYTHON) $$f & ;; esac; \
		pids="$$pids $$!"; \
	done; \
	failed=0; \
	for pid in $$pids; do wait $$pid || failed=1; done; \
	[ $$failed -eq 0 ] && echo '✓ All checks passed' || echo '⚠️  Some checks failed'

warm-cache: ## Rebuild .cache/ from scratch (run after fresh clone)
	@mkdir -p .cache
	$(PYTHON) tools/dedup_scan.py --full
	$(PYTHON) tools/agent_context_writer.py
	$(PYTHON) tools/cron_sentinel.py --check || true

guardian: ## Run guardian static analysis
	$(PYTHON) guardian_engine.py 2>/dev/null || bash guardian

clean: ## Remove .pyc files and __pycache__
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo '✓ Cleaned'
