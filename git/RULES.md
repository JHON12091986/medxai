# NINA Git Rules — Non-Negotiable for All Agents

## Branch Rules

1. **Never commit directly to `main`** without going through a PR (exception: chore/infra fixes by human owner).
2. **Branch naming**: Jules branches use `jules-<id>-<hash>`. Feature branches use `feat/<name>`. Fixes use `fix/<name>`.
3. **Max open branches**: 3 at any time (1 main + 2 active work). More than 3 = run `git/scripts/branch_cleanup.sh`.
4. **Delete branch after PR merge**: GitHub auto-delete is enabled. Never reuse a merged branch.
5. **Orphaned branches** (no PR after 48h) must be deleted immediately.

## Commit Rules

6. **Conventional commits required**: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`.
7. **Never force-push to main**. Force-push only allowed on your own unmerged PR branch.
8. **Never commit these files** (they are runtime/generated — see `dirty_file_register.md`):
   - `data/router/provider_metrics.db`
   - `nina_context_graph.json`
   - `docs/generated/*`
9. **Hook-generated governed files** (`docs/space/nina_repo_hygiene_dashboard.md`, `docs/space/nina_index.md`, `docs/context/nina_session_log.md`) are auto-committed by the post-commit hook. Do not manually stage them.

## PR Rules

10. **Rebase onto latest main before opening PR**: `git fetch origin main && git rebase origin/main`.
11. **Run `python3 tools/update_index.py` on your branch** before pushing if any files were added/moved/deleted.
12. **Pre-push hook must pass** before PR is created. Never use `--no-verify` on a PR push.
13. **Squash merge only** — keeps main history linear.

## Rebase / Merge Rules

14. **Dirty working tree blocks rebase**. Before rebasing, always run:
    ```bash
    git checkout -- data/router/provider_metrics.db
    git checkout -- docs/space/nina_index.md docs/space/nina_repo_hygiene_dashboard.md
    ```
15. **Use `-X ours` for governance doc conflicts** during rebase — the branch version of `nina_index.json` is always more correct than main during a Jules PR rebase.

## Health Rules

16. `health=WARN` in post-commit output is acceptable during active development. `health=ERROR` blocks all PRs.
17. The persistent `top_priority=todo.tools_merge_resolver_py_184` wiring issue must be resolved before next major release.
