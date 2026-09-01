---
name: build-tdd
category: build
description: Red-Green-Refactor cycle for one step. Enforces L1 (RED before prod) and L5-R (non-overlap).
when_to_use:
  - Inside a role-owner's worktree, after the step's ## Role section is filled
allowed-tools: Read Write Bash Edit
model: sonnet
---

# /dev-kit-lite:build-tdd

## Workflow

Per-step TDD cycle with L5-R pre-flight.

## Step 1 — Pre-flight (L5-R non-overlap check)

1. Read `phases/<name>/step<N>.md` `## Role` section
2. Read `phases/<name>/owners.json`
3. Verify the Owner from `## Role` is not already in-flight on another step
4. Verify the `Owns:` paths do not intersect any active `path_locks`
5. If conflict → print error and refuse to start (use `/dev-kit-lite:reassign` to resolve)

## Step 2 — Create worktree (if not exists)

```bash
git worktree add -B feat/<scope>-<owner>-<slug> .worktrees/<scope>-<owner> origin/main
cd .worktrees/<scope>-<owner>
```

## Step 3 — RED phase

1. Write failing test in `tests/` or `*.test.*`
2. Run the test command — capture `exit_code != 0`
3. Write `.dev-kit/.tdd-cycle.json`:
   ```json
   {"phase": "red", "last_exit_code": 1, "test_command": "...", "started_at": "<iso>"}
   ```
4. `tdd-guard.sh` will now allow test-file edits but deny prod-code edits

## Step 4 — GREEN phase

1. Update `.dev-kit/.tdd-cycle.json` to `{"phase": "green", ...}`
2. Write minimum prod code to make the test pass
3. Run test — capture `exit_code == 0`
4. `tdd-guard.sh` now allows prod-code edits

## Step 5 — REFACTOR phase

1. Update `.dev-kit/.tdd-cycle.json` to `{"phase": "refactor", ...}`
2. Clean up code (no behavior change)
3. Run tests — must still pass

## Step 6 — Commit + Update owners.json

1. `git add . && git commit -m "feat(<scope>): <step title>"` with quoted exit code in body
2. Update `phases/<name>/owners.json`: release the lock (set `active_step: null`)

## Validation gates

- `.dev-kit/.tdd-cycle.json` shows completed cycle (red → green → refactor)
- `git log -1` shows commit with quoted exit code in body
- `owners.json` lock released for this owner

## Iron Laws

- L1 (RED before prod) — enforced by `tdd-guard.sh`
- L5-R (non-overlap) — enforced by Step 1 pre-flight

## Anti-patterns

- ❌ Skipping RED phase (writing prod code before failing test exists)
- ❌ Editing test file to make it pass instead of fixing prod code
- ❌ Working on a step whose Owner is already in-flight on another step

## Next step

```
/dev-kit-lite:build-verify <stepN>
```
