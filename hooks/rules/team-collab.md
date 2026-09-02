# Team collab — 4-hour MVP cadence

The PM/coordinator owns the loop. Everyone else owns one step at a time.

## The 4-hour cadence

| Block | Time | PM action | Team action |
|-------|------|-----------|-------------|
| Hour 0 — Plan | 0:00–0:30 | Run `/dev-kit-lite:plan`, write PRD.md + phases/ | Review PRD, claim steps |
| Hour 0 — Build | 0:30–2:30 | `/dev-kit-lite:build-verify` per step | `/dev-kit-lite:build-tdd` in own worktree |
| Hour 2 — Review | 2:30–3:30 | Run `/dev-kit-lite:review` per PR | Address review comments |
| Hour 3 — Verify | 3:30–4:00 | Final `/dev-kit-lite:build-verify`, merge | Clean up worktrees, retro |

## PM check-in cadence

Every 30 minutes, PM appends to `.dev-kit/session-log.md`:
- What got done
- What's blocked
- Owner reassignments (uses `/dev-kit-lite:reassign <stepN> <new-owner>`)
- Scope changes (uses `/dev-kit-lite:plan-update <reason>`)

## Hand-off protocol

When Owner A finishes a step and Owner B's step depends on it:
1. Owner A runs `/dev-kit-lite:build-verify` → status: completed → ownership lock released
2. PM updates `.dev-kit/session-log.md` with hand-off note
3. Owner B's `Owns:` paths must NOT overlap with any in-flight step
4. Owner B runs `/dev-kit-lite:build-tdd` → ownership lock acquired

## Conflict resolution

- **Same person, two in-flight steps**: PM runs `/dev-kit-lite:reassign` to move one to another owner
- **Overlapping paths**: same as above; path_locks in `phases/<name>/owners.json` are the source of truth
- **Scope change mid-sprint**: PM runs `/dev-kit-lite:plan-update <reason>`; this may trigger reassign
- **Build broken on red CI**: CI is advisory-only (see `.github/workflows/review.yml`); do NOT block merge — fix forward in next worktree

## Anti-patterns (forbidden)

- ❌ Two Alices working in parallel without separate worktrees
- ❌ Same directory edited in two worktrees simultaneously
- ❌ Merging to main without PM sign-off in session-log
- ❌ "We'll fix the failing test later" (L4 violation)
- ❌ "Just push to main, it's only one line" (L2 violation)
