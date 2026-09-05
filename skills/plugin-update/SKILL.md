---
name: plugin-update
description: git fetch + reset --hard for every git repo under .claude/plugins/. No verb. No state.
allowed-tools: Bash
model: sonnet
---

# /dev-kit-lite:plugin-update

```bash
for d in .claude/plugins/*/; do
  [ -d "$d/.git" ] || continue
  git -C "$d" fetch --all --prune --quiet
  ref=$(git -C "$d" symbolic-ref --short HEAD 2>/dev/null || echo main)
  git -C "$d" reset --hard "origin/$ref" --quiet
  echo "updated: $d"
done
```

Install = `git clone <url> .claude/plugins/<name>/`.

L2 — caller in a worktree.