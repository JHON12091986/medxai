# NINA Four Pillar Hardening Blueprint
## Date: 2026-06-16 | Role: ARCHITECT & EXECUTOR

This document outlines the architecture, specifications, and execution plan for implementing the **Four Strategic Hardening Pillars** to upgrade NINA's security, integration capability, performance, and execution autonomy.

---

## 1. Credential Vault Proxy (Security)
* **Goal:** Shield raw API keys and credentials from standard `os.environ` memory to prevent speculative Python code or shell processes from extracting sensitive environment data.
* **Component:** `core/vault.py` (New), integrated with `core/config.py`.
* **Mechanism:**
  1. Load `.env` into a private dictionary inside `core/vault.py` at bootstrap.
  2. Identify sensitive keys matching patterns: `*_API_KEY`, `*TOKEN*`, `*PASSWORD*`, `*SECRET*`.
  3. Delete these keys from `os.environ` so standard subprocesses and external tools cannot read them.
  4. Expose `get_secret(key: str, default: Optional[str] = None) -> Optional[str]` as the secure getter.
  5. Adjust config loading to request sensitive keys from the vault.

---

## 2. OmniBridge Abstract Channel Adapters (Integration)
* **Goal:** Abstract NINA's external message interface to allow swapping standard Telegram routing for other channels (TUI, Discord, Webhooks) without changing core logic.
* **Component:** `interfaces/base_adapter.py` (New)
* **Mechanism:**
  1. Define a generic `BaseChannelAdapter` class:
     - `send_message(target_id: str, text: str) -> bool`
     - `send_document(target_id: str, file_path: str, caption: str) -> bool`
     - `register_handler(command: str, handler_func: Callable)`
  2. Implement an abstract state model for representing standardized client/message objects.

---

## 3. Compiled High-Frequency Utilities (Performance)
* **Goal:** Accelerate performance-critical utility calls (e.g., regex matching, config lookup, AST traversal) using speed-optimized modules.
* **Component:** `tools/compile_extensions.py` (New)
* **Mechanism:**
  1. Write a speed-up utility containing pre-compiled regex pools, quick tokenization mechanisms, or pre-calculated static caches.
  2. Provide compile scripts that pre-compile python modules or byte-compile (`.pyc`) hotpaths.

---

## 4. Micro-Sandboxed Subshell Execution (Autonomy)
* **Goal:** Execute untrusted/speculative commands or user-generated scripts in a secure, resource-limited environment to prevent damage to the host system.
* **Component:** `tools/sandboxed_shell.py` (New)
* **Mechanism:**
  1. Use the Python `resource` module to set strict limits on CPU time, memory (RLIMIT_AS), and file size on the spawned subprocess.
  2. Strip environment variables down to the absolute bare minimum (e.g., PATH, clear of all keys).
  3. Run executions in an ephemeral subshell.

---

## Implementation Schedule
1. **Pillar 1:** Implement `core/vault.py` and connect it with `core/config.py`.
2. **Pillar 2:** Implement `interfaces/base_adapter.py`.
3. **Pillar 3:** Implement `tools/compile_extensions.py`.
4. **Pillar 4:** Implement `tools/sandboxed_shell.py` and hook into standard shell triggers.
5. **Validation:** Perform py_compile/pyflakes checks on all, run the test suite, and run `rule0_audit.py` + `nina_sync.sh`.
