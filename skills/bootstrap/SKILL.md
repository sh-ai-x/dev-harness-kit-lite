---
name: bootstrap
category: bootstrap
description: Scaffold CLAUDE.md + AGENTS.md + .active-hooks.json + first commit (idempotent).
when_to_use:
  - First time running dev-kit-lite in this repo
  - After pulling a fresh clone
allowed-tools: Read Write Bash
model: sonnet
---

# /dev-kit-lite:bootstrap

## Workflow

Idempotent. Safe to re-run. Verifies the lite kit is wired correctly.

## Step 1 — Verify kit

```bash
test -f CLAUDE.md && test -L AGENTS.md && test -d hooks/ && test -d skills/ && test -d rules/ && test -d iron-laws/
```

Exit 0 = wired. Exit 1 = missing file.

## Step 2 — Write `.dev-kit/.active-hooks.json`

```json
{
  "schema_version": "1.0.0",
  "phase": "bootstrap",
  "hooks": {
    "PreToolUse:Write|Edit|MultiEdit": ["worktree-guard.sh", "tdd-guard.sh", "destructive-confirm.sh"],
    "PreToolUse:Bash": ["git-guard.sh", "destructive-confirm.sh"],
    "PostToolUse:Write|Edit|MultiEdit": ["secret-scan.sh"],
    "SessionStart": ["session-start-check.sh"],
    "Stop": ["stop-verify.sh"]
  },
  "wrote_at": "<iso-8601>"
}
```

## Step 3 — Write `.gitignore` (if missing)

See `.gitignore` in repo root. Idempotent — does not overwrite.

## Validation gates

- `CLAUDE.md` exists
- `AGENTS.md` symlinks to `CLAUDE.md`
- `.dev-kit/.active-hooks.json` has 5 hook entries (PreToolUse Write+Edit, PreToolUse Bash, PostToolUse, SessionStart, Stop)
- `git status` clean on main checkout

## Iron Laws

- L2 (no edit on main) — bootstrap writes config files; subsequent code edits must be in worktree
- L5-R (non-overlap) — bootstrap is PM-only

## Next step

```
/dev-kit-lite:plan "<your 1-line MVP goal>"
```
