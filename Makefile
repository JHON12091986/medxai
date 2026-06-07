.PHONY: help check test

help:
	@echo "NINA Developer Helpers"
	@echo ""
	@echo "Usage:"
	@echo "  make check    Run py_compile and pyflakes on currently modified python files"
	@echo "  make test     Run pytest (if tests exist)"

check:
	@echo "Running py_compile on changed python files..."
	@git diff --name-only --diff-filter=d HEAD | grep '\.py$$' | xargs -r python3 -m py_compile
	@echo "Running pyflakes on changed python files..."
	@git diff --name-only --diff-filter=d HEAD | grep '\.py$$' | xargs -r pyflakes
	@echo "Checks passed!"

test:
	@echo "Running pytest..."
	@if [ -d "tests" ]; then \
		pytest tests/; \
	else \
		echo "No tests/ directory found."; \
	fi
