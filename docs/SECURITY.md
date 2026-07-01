# Security Policy

## Reporting a Vulnerability

Please email onlybony@gmail.com — do not open a public issue for security bugs. NINA handles sensitive personal and banking infrastructure; disclosures should be coordinated privately.

## Local-Only Data Philosophy

NINA is designed fundamentally around data sovereignty. Under no circumstances should banking data, credentials, or sensitive personal information leave the local machine. All processing of such data is strictly mandated to occur via local Ollama models (`qwen2.5:1.5b` or `qwen2.5:7b`).

## Authentication & Access Control

- **Telegram Interface:** The primary gateway for remote operation is secured through Telegram. It strictly validates the sender against an `authorized_user_id`. No commands are accepted from unrecognized IDs.
- **Secrets Management:** There are absolutely no secrets, API keys, or credentials committed to the codebase. All sensitive tokens exist exclusively within the ignored `.env` file.

## Shell Execution Allowlist

Arbitrary code execution is a critical vulnerability for an autonomous agent. Therefore, `tools/shell.py` employs a strict command allowlist. Shell commands attempted by NINA or its sub-agents that are not explicitly pre-approved on this list will be rejected by the system. Furthermore, `subprocess` calls must never use `shell=True`.

## Guardian Gate Enforcement

The Guardian Gate (`guardian_engine.py`) serves as the active security enforcement mechanism for self-patching. It runs AST scans on all incoming patches to ensure no rogue code (such as injecting unauthorized shell executions or bypassing the allowlist) is deployed into the runtime environment.

## High-Risk Files

The following files control the core security, routing, and identity of NINA. They must default to manual local handling or `ninaflash` review, and are restricted from blind automated cloud edits (e.g., by Jules):
- `main.py`
- `core/router.py`
- `interfaces/telegram_interface.py`
- `guardian_engine.py`
- `tools/shell.py`
- `.env`

## Immutable Agent Files

To prevent context drift and ensure NINA cannot rewrite its own identity or baseline ruleset, two specific files are considered strictly immutable by automated agents:
- `data/memory/facts.json` (Identity Anchor)
- `upgrades/guardian_baseline.json` (Structural Baseline Map)
