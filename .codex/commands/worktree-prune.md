---
description: Count worktrees, list them oldest-first, and remove the N oldest on demand.
argument-hint: '[N | --keep N | --dry-run | --yes]'
---

# /worktree-prune

Interactive worktree cleanup. Lists every registered worktree sorted
by branch-tip age, asks how many of the oldest to remove, and (after a
y/N gate) hands each one to `bin/worktree-remove-safe.sh`.

Pruned from dev-harness-kit's `/dev-kit:worktree-prune` — drops the
janitor-agent cross-link and the per-worktree log archive (lite has
no telemetry retention requirement).

## Args

`$ARGUMENTS` is the full arg string. Positional N and `--keep` are
mutually exclusive. See `/worktree-prune` (Claude Code) for the full
argument table — Codex forwards to the same `bin/worktree-prune.sh`.

## Examples

```
/worktree-prune                # interactive: "how many?"
/worktree-prune 5              # remove the 5 oldest, then confirm
/worktree-prune -y 10          # remove 10 oldest, no prompt
/worktree-prune --keep 3       # prune to 3 newest
/worktree-prune -n 5           # preview the 5 oldest, no changes
```

## Related

- `bin/worktree-prune.sh` — the script the command forwards to
- `lib/worktree_prune.py` — the data half (parses porcelain, builds
  the epoch map, sorts oldest-first)
- `bin/worktree-remove-safe.sh` — per-worktree safe-removal wrapper
  used by the removal loop
