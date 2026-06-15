# Status: IMPLEMENTED | Target: NINA Universal CLI Integration
# Replaces specific shims with a universal wrapper for all managed CLIs
# Implemented on: June 15, 2026

---

## What This Does

Replaces CLI binaries (e.g., `gemini`, `agy`) in the local `bin/` directory with symlinks to a single, thin `nina-universal-wrapper.sh`.

The universal wrapper:
1. Detects which CLI was invoked by checking its own `basename`.
2. Automatically configures the environment to route API requests (Gemini SDKs and OpenAI SDKs) to `NinaGate` (running locally on port 8080).
3. Provides fallback bypass keys (`nina-local-bypass`) to satisfy CLI SDK requirements when no key is explicitly configured.
4. Dynamically discovers the original target binary from the system `PATH` (using `which -a`), avoiding recursion loops.
5. Executes the original binary transparently, piping all output and input normally.
6. Implements a hardcoded Python fallback specifically for `gemini` if the original binary cannot be found.

## Deployment Details

- **Path**: `bin/nina-universal-wrapper.sh`
- **Managed Links**: 
  - `bin/gemini -> nina-universal-wrapper.sh`
  - `bin/agy -> nina-universal-wrapper.sh`

This configuration ensures that any CLI tool executed from the NINA workspace inherently routes its LLM requests through NINA's quota-aware routing logic, local inference fallbacks, and provider circuits—protecting cloud limits and increasing resilience automatically.
