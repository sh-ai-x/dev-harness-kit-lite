# Hook matrix — dev-harness-kit-lite

6 hooks wired across 3 events. **fail_closed = true** means non-zero exit denies the tool call.

| Event | Matcher | Hook | fail_closed | Enforces | Toggleable |
|-------|---------|------|-------------|----------|------------|
| PreToolUse | Write\|Edit\|MultiEdit | worktree-guard.sh | true | L2 (no edit on main) | — |
| PreToolUse | Write\|Edit\|MultiEdit | tdd-guard.sh | true | L1 (RED before prod) | `tdd_guard_enabled` |
| PreToolUse | Write\|Edit\|MultiEdit | destructive-confirm.sh | true | (confirm .env/.pem writes) | — |
| PreToolUse | Bash | git-guard.sh | true | L2 (no push to main, no --force) | `main_push_block_enabled` |
| PreToolUse | Bash | destructive-confirm.sh | true | (confirm dangerous bash) | — |
| PostToolUse | Write\|Edit\|MultiEdit | secret-scan.sh | true | (block credential patterns) | — |
| Stop | (all) | stop-verify.sh | true | L3 (no done without verify) | — |

**fail_closed=true**: 7 hooks (deny on non-zero exit). The destructive-confirm.sh script is registered for both Write and Bash events.

**Toggleable**: TDD guard (L1) and the main-push / main-commit sections of git-guard (L2) read `.dev-kit/.guard-config.json` and exit 0 when their flag is `false`. Flip with `/dev-kit-lite:setup-guard`. Hook wiring is never changed — only the rule is bypassed.

Full-kit comparison: 32 hooks → 6 hooks (81% reduction).
