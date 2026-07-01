# Rollback Registry

> **Location**: `docs/ops/rollback_registry.md`  
> **Written by**: `ngit` post-push hook automatically  
> **Retention policy**: Last 20 checkpoints kept; older entries pruned each cycle  
> **Read by**: Perplexity ARCHITECT OVERWATCH, Jules — before any destructive operation

This registry tracks release and merge states for automatic recovery and rollback safety. To roll back to any checkpoint: `git checkout <commit_sha>`

---

## Last 20 Active Checkpoints

| Timestamp | Commit SHA | Tag | Status | Description |
|---|---|---|---|---|
| 2026-06-22T12:12:29Z | 40329c9584d1820a9d5e2f1bdc71513de0374812 | `rollback/pr-unknown/20260622-121229` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T12:17:20Z | 020391a2b469564172a54c6075b1ec2d0db686a2 | `rollback/pr-unknown/20260622-121720` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T12:25:56Z | 242826f17138b9f438a31c0cf2de581bba06d37d | `rollback/pr-unknown/20260622-122556` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T12:37:36Z | 203f8d746c61004e5e03358ea7f19ce6643228b0 | `rollback/pr-unknown/20260622-123736` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T12:47:29Z | 9f0dc3c9b943a1e4e29edbe941b89f729759aa58 | `rollback/pr-unknown/20260622-124729` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T13:51:16Z | 5e4e0776831bb199b6bae5598bf606c2fad0bb5d | `rollback/pr-unknown/20260622-135116` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T14:09:53Z | b88ca2a8f833a44cc72ed27b0510ebef5fd93905 | `rollback/pr-unknown/20260622-140953` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T14:52:19Z | 31e43a8863eeb295629ea648f2a1363a71f6c8e1 | `rollback/pr-unknown/20260622-145219` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T15:23:53Z | 36ca07f547ab11e7512ae8ee4fafeb0b60c37ffa | `rollback/pr-unknown/20260622-152353` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T16:54:46Z | b12610ca43f31f8e5f6d6a7381a0d8d88e04e6c8 | `rollback/pr-unknown/20260622-165446` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T17:13:23Z | 5d80f12a0b7705da7af12556b6ab69defb7c749d | `rollback/pr-unknown/20260622-171323` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T17:34:49Z | 47c6cc83e5d699038281ceebdefc06c5de93c7f8 | `rollback/pr-unknown/20260622-173449` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T17:57:39Z | 8d14596a0546dd04953eedbad0cc9deb60ea6be6 | `rollback/pr-unknown/20260622-175739` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T18:10:35Z | 85bc8bbc7022815a2565259cab5b7448aaa174d4 | `rollback/pr-unknown/20260622-181035` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T18:34:57Z | 1e27362fcca89ad50a384249a04fc336e21cf047 | `rollback/pr-unknown/20260622-183457` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T18:49:37Z | f670e565caa4a5086f87ee7c70cf351c1c8b54f6 | `rollback/pr-unknown/20260622-184937` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T19:13:28Z | f95f00f38e6943c015a552e1e5d2c6863f09a34c | `rollback/pr-unknown/20260622-191328` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T19:28:13Z | 1c153c0cb707a74f0b6a0ea865a25c9518f461e7 | `rollback/pr-unknown/20260622-192813` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T19:35:35Z | d31d9ab202b036ed97c1f72102c1aa5538b4160a | `rollback/pr-unknown/20260622-193535` | ACTIVE | Auto-generated rollback checkpoint |
| 2026-06-22T21:30:06Z | 7932a4435a0b386dbb8f4722f9923e38638369bb | `rollback/pr-unknown/20260622-213006` | ACTIVE | Auto-generated rollback checkpoint |

---

## How to Rollback

```bash
# List available checkpoints
git log --oneline --decorate | grep rollback

# Roll back to a specific checkpoint
git checkout <commit_sha>       # detached HEAD — inspect
git checkout -b recovery/2606xx # create recovery branch

# Hard reset main to checkpoint (DESTRUCTIVE — confirm first)
git reset --hard <commit_sha>
git push --force-with-lease
```

> **ngit automation**: The `post-push` hook in `.git/hooks/post-push` appends a new row here after every successful push. Pruning (keep last 20) runs as part of `nina_sync.sh`.
