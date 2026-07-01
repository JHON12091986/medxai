# Perplexity Relay

This folder is the execution layer for tasks that Perplexity writes for you to run locally on Nina.

## How to run a task

1. Perplexity gives you a task JSON block. Save it to a file:

   ```
   perplexity/tasks/PRX-XXX.json
   ```

2. Run it with one command:

   ```
   python3 perplexity/relay.py --file perplexity/tasks/PRX-XXX.json
   ```

## What the status messages mean

- **DONE** — every step completed successfully, repo and/or git updated as described
- **PENDING** — task was submitted to Jules, waiting for a PR to appear
- **REFUSED** — safety checks blocked the task before anything ran; repo is unchanged
- **FAILED** — a step failed mid-task; all file changes were rolled back, repo is unchanged

If you see REFUSED or FAILED, paste the whole output back to Perplexity. Do not run anything else until Perplexity tells you what to do next.

Tasks involving a git push or a Jules submission require Perplexity to explicitly tell you to add `"confirmed": true` to the task file. Do not add this yourself unless Perplexity has told you to for that specific task.
