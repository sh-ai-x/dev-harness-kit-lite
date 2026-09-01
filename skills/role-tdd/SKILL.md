---
name: role-tdd
category: build
description: TDD workflow scoped to the calling role-owner's identifier. Reads the role's plan doc, filters steps to only the ones they own, runs Red-Green-Refactor per step in dependency order, and updates the role-plan status as it goes. Same discipline as build-tdd but auto-scoped — no PM intervention needed.
when_to_use:
  - Inside a role-owner's worktree, after reading their role-plan
  - Each role runs this independently — FE / BE / AI / Design can all be running it in parallel
  - When you want a "TDD on my slice, not the whole project" mode
allowed-tools: Read Write Bash Edit AskUserQuestion
model: sonnet
---

# /dev-kit-lite:role-tdd

## Role

You are the role-scoped TDD runner. The PM finished `role-plan`, which wrote `phases/<name>/role-plans/<your-identifier>.md` — a focused doc listing only your assigned steps, your deps, and your tech-stack-specific tooling. Your job is to drive Red-Green-Refactor on those steps in dependency order, **without** touching steps owned by other roles. Cold realism: if a step's dependency isn't merged yet, you block — you don't silently reach across roles.

## Inputs

| Source | What you read | Where |
|--------|---------------|-------|
| Your role-identifier | who you are | `phases/<name>/role-plans/<your-role-key>-N.md` filename |
| Your role plan | your steps, deps, tooling | `phases/<name>/role-plans/<your-role-key>.md` (or the per-owner variant) |
| Step detail | AC + branch + worktree path | `phases/<name>/step<N>.md` |
| Team roster | confirms your identifier | `.dev-kit/team-roster.json` |
| Role config | your `owns_paths`, `tech_stack`, `shared_read_paths` | `.dev-kit/role-config.json` |

If you don't know your role-identifier, ask the user via `AskUserQuestion` (L5: one answer). Common values: `fe-1`, `be-2`, `ai-1`, `design-1`, `pm-1`.

## How role-scoping works

The skill walks `phases/<name>/index.json` and keeps ONLY steps where `owner == <your-identifier>`. Everything else is **invisible to this skill**. If you find yourself reading another role's step file, you've stepped outside your lane — abort and propose a reassignment via `/dev-kit-lite:reassign`.

## Workflow

### Step 1 — Pre-flight (L5-R non-overlap)

1. Read `phases/<name>/role-plans/<your-identifier>.md`. Confirm:
   - Your identifier matches an entry in `.dev-kit/team-roster.json`
   - Your role's `active_step` is either `null` or the current step (not someone else's)
   - The step's `Ows:` paths don't intersect any other active role's path locks
2. If any check fails, print the conflict and refuse to start. Use `/dev-kit-lite:reassign` to resolve.

### Step 2 — Pick the next step in dependency order

From your filtered steps, pick the lowest-layer one whose dependencies are all `status: done` (in `phases/<name>/index.json`). If none, stop — your work is done for this round.

If the next step's dependencies are owned by other roles and not yet `done`, **wait**. Print what you're waiting on. Do not silently reach across roles.

### Step 3 — RED phase (per step)

1. Open a worktree (if not already in one):
   ```bash
   git worktree add -b feat/<scope>-<your-identifier>-<step-id> \
     .worktrees/<your-identifier> origin/main
   cd .worktrees/<your-identifier>
   ```
2. Write a failing test in `tests/` (or `*.test.*`) that exercises the AC for this step.
3. Run the test command — capture `exit_code != 0`.
4. Write `.dev-kit/.tdd-cycle.json`:
   ```json
   {"phase": "red", "step": "<step-id>", "test_command": "...", "last_exit_code": 1, "started_at": "<iso>"}
   ```
5. `tdd-guard.sh` will now allow test-file edits but deny prod-code edits.

### Step 4 — GREEN phase

1. Update `.dev-kit/.tdd-cycle.json` to `{"phase": "green", ...}`.
2. Write minimum prod code in **your `owns_paths`** to make the test pass. Do NOT write to another role's `owns_paths`.
3. If you find yourself needing to touch a foreign path, ABORT and propose a hand-off via `/dev-kit-lite:plan-update` — don't paper over with a quick fix.
4. Run test — capture `exit_code == 0`.
5. `tdd-guard.sh` now allows prod-code edits.

### Step 5 — REFACTOR phase

1. Update `.dev-kit/.tdd-cycle.json` to `{"phase": "refactor", ...}`.
2. Clean up code (no behavior change).
3. Run tests — must still pass.

### Step 6 — Commit + update role-plan

1. `git add . && git commit -m "feat(<scope>): <step title>"` with quoted exit code in body.
2. Update `phases/<name>/role-plans/<your-identifier>.md` — flip the step's `Status:` from `pending` to `in-progress` (or `done` if you want a tight feedback loop).
3. Update `phases/<name>/index.json` — set the step's `status` to `in-progress`.
4. Push to your feature branch. Open a PR.
5. Run `/dev-kit-lite:review` (advisory).
6. After PR merge, set the step's `status: done` in `index.json` and your role-plan.

### Step 7 — Loop

Go back to Step 2, pick the next dependency-ready step.

## Validation gates

- `.dev-kit/.tdd-cycle.json` shows completed cycle (red → green → refactor)
- `git log -1` shows commit with quoted exit code in body (L3 evidence)
- Your role-plan's `Status:` flipped correctly
- `phases/<name>/index.json` updated
- No files written outside your `owns_paths` (verifiable by `git diff origin/main --stat`)

## Iron Laws

- **L1** (no prod code without a failing test) — enforced by `tdd-guard.sh`
- **L2** (no Edit/Write on main checkout) — enforced by `worktree-guard.sh`; you're in your own worktree
- **L3** (no "done" without quoted exit code + test count) — commit body must carry it
- **L4** (no TODO / FIXME in committed code) — `hooks/secret-scan.sh` and the L4 check in `review`
- **L5** (one answer per question) — single AskUserQuestion at a time when role-identifier is unknown
- **L5-R** (non-overlap) — verified at pre-flight; checked again at Step 6 via `git diff --stat` outside `owns_paths`

## Anti-patterns

- ❌ Starting a step before its cross-role dependency is merged (use `/dev-kit-lite:reassign` if you really need to start earlier)
- ❌ Writing to another role's `owns_paths` even for "just one line" — open a hand-off via `plan-update`
- ❌ Touching steps in your role-plan that aren't in your filter (e.g., "while I'm here, let me also fix this other step") — out of scope
- ❌ Skipping RED because "the prod code is obvious" — `tdd-guard.sh` will block anyway; better to write the test
- ❌ Marking a step `done` without running tests + L3 commit evidence
- ❌ Re-running build-tdd at the project level when this skill would do — this skill is the scoped variant for role-owners

## Next step

- All your steps done → run `/dev-kit-lite:build-verify` (PM-level gate) which verifies role-contract + releases path locks
- New step added to your lane (via `plan-update` + re-running `role-plan`) → re-invoke this skill
- Cross-role dependency appears unmerged → message the owning role in your team's channel, or escalate via `/dev-kit-lite:reassign` if it's blocking you
