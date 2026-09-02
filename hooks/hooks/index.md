# Hook matrix — dev-harness-kit-lite

6 hooks wired across 3 events. **fail_closed = true** means non-zero exit denies the tool call.

| Event | Matcher | Hook | fail_closed | Enforces |
|-------|---------|------|-------------|----------|
| PreToolUse | Write\|Edit\|MultiEdit | worktree-guard.sh | true | L2 (no edit on main) |
| PreToolUse | Write\|Edit\|MultiEdit | tdd-guard.sh | true | L1 (RED before prod) |
| PreToolUse | Write\|Edit\|MultiEdit | destructive-confirm.sh | true | (confirm .env/.pem writes) |
| PreToolUse | Bash | git-guard.sh | true | L2 (no push to main, no --force) |
| PreToolUse | Bash | destructive-confirm.sh | true | (confirm dangerous bash) |
| PostToolUse | Write\|Edit\|MultiEdit | secret-scan.sh | true | (block credential patterns) |
| Stop | (all) | stop-verify.sh | true | L3 (no done without verify) |

**fail_closed=true**: 7 hooks (deny on non-zero exit). The destructive-confirm.sh script is registered for both Write and Bash events.

Full-kit comparison: 32 hooks → 6 hooks (81% reduction).
