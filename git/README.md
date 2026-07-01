# NINA Git Governance

This folder is the **single source of truth** for all git hygiene rules, hooks, and automation in this repository.

Every agent (Jules, NINA, Perplexity, human) must read this before touching git operations.

---

## Folder Structure

```
git/
├── README.md                  ← You are here. Read this first.
├── RULES.md                   ← Git laws. Non-negotiable for all agents.
├── hooks/
│   ├── post-commit            ← Canonical hook source (copy to .git/hooks/)
│   ├── pre-commit             ← Canonical hook source
│   └── pre-push               ← Canonical hook source
├── scripts/
│   ├── install_hooks.sh       ← Run once after clone to install hooks
│   └── branch_cleanup.sh      ← Weekly cron — deletes orphaned Jules branches
└── docs/
    ├── dirty_file_register.md ← Files that are always regenerated (never manually edit)
    └── known_issues.md        ← Persistent WARNs and their status
```

---

## Quick Start (after clone)

```bash
bash git/scripts/install_hooks.sh
```

That's it. All hooks are installed, executable, and ready.

---

## Agent Contract

- **Jules**: Read `RULES.md` before creating any branch or PR. Delete your branch after PR merges.
- **NINA autonomy loop**: Never commit `data/router/provider_metrics.db`. Never commit `nina_context_graph.json`.
- **Perplexity/human**: Always read `dirty_file_register.md` before diagnosing a dirty working tree.
- **All agents**: If `git status` shows dirty files, check `dirty_file_register.md` first — it may be expected.
