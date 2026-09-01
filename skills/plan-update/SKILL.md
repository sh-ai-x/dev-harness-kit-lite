---
name: plan-update
category: plan
description: PM-only mid-sprint PRD/phases/owners.json mutation. Use when scope changes after plan emission.
when_to_use:
  - Adding/removing steps mid-sprint
  - Changing AC of an in-flight step
  - Reassigning role headcount (e.g. "we need a 3rd frontend dev")
  - Adjusting scope (in/out)
allowed-tools: Read Write Bash
model: opus
---

# /dev-kit-lite:plan-update

## Workflow

PM-only. Mutates existing PRD.md + phases/<name>/ + owners.json. **Never** called by role-owners.

## Step 1 — State the reason

Ask the user (1 question, L5):
> "Why is the plan changing? (1 sentence)"

Write reason to `.dev-kit/decision-log.md` with timestamp.

## Step 2 — Detect change type

Ask the user (multiSelect):

- [ ] Add new step
- [ ] Remove existing step
- [ ] Change AC of existing step
- [ ] Change scope (in/out)
- [ ] Reassign owner of a step (use `/dev-kit-lite:reassign` instead — this skill handles the plan side)
- [ ] Change role headcount (e.g. add a 3rd frontend dev)

## Step 3 — Apply change

For each selected change:

| Change | Action |
|--------|--------|
| Add step | Append `step<N+1>.md` to `phases/<name>/`, update `index.json` |
| Remove step | Delete `step<N>.md`, update `index.json`, release ownership locks in `owners.json` |
| Change AC | Edit `step<N>.md` AC section, update `PRD.md §3` |
| Change scope | Edit `PRD.md §2` |
| Reassign owner | Delegate to `/dev-kit-lite:reassign <stepN> <new-owner>` (do not edit owners.json directly) |
| Change headcount | Update `PRD.md §4` table + `owners.json` initial entries |

## Step 4 — Validate

- All changes written to `PRD.md` + `phases/<name>/` consistently (no orphaned steps)
- `owners.json` re-validated for L5-R non-overlap
- `decision-log.md` entry appended
- PM sign-off recorded

## Validation gates

- `phases/<name>/index.json` is valid JSON
- Every step in `index.json` has a corresponding `step<N>.md`
- `owners.json` owners are all unique
- `owners.json` path_locks are all unique
- For any in-flight step being changed: PM must explicitly approve the change (recorded in `decision-log.md`)

## Iron Laws

- L5 (one answer per question)
- L5-R (non-overlap) — must re-check owners.json after every change

## Anti-patterns

- ❌ Calling this skill without a reason — use `/dev-kit-lite:reassign` for pure ownership changes
- ❌ Role-owner calling this skill — PM-only
- ❌ Removing an in-flight step without releasing its ownership lock first

## Next step

```
/dev-kit-lite:build-tdd    # continue work
# or
/dev-kit-lite:reassign     # for pure ownership change
```
