---
name: reassign
category: plan
description: PM-only mid-sprint ownership transfer. Releases one owner's lock and grants it to another.
when_to_use:
  - When an Owner becomes blocked (sick, scope change, etc.)
  - When path ownership needs to shift mid-sprint
allowed-tools: Read Write Bash
model: sonnet
---

# /dev-kit-lite:reassign

## Workflow

PM-only. Single skill call: `/dev-kit-lite:reassign <stepN> <new-owner>`.

## Step 1 — Validate

- Caller must be PM (check `.dev-kit/session-log.md` for PM sign-off marker)
- `step<N>` must exist in `phases/<name>/index.json`
- `<new-owner>` must be in `PRD.md §4 Role assignment` table

## Step 2 — Release old lock

In `phases/<name>/owners.json`:
- `owners[<old-owner>].active_step = null`
- Remove `path_locks[<path>]` for paths this step owned

## Step 3 — Grant new lock

In `phases/<name>/owners.json`:
- Set `owners[<new-owner>].active_step = <N>`
- Set `owners[<new-owner>].branch = feat/<scope>-<new-owner>-<slug>`
- Set `owners[<new-owner>].worktree = .worktrees/<scope>-<new-owner>`
- Set `owners[<new-owner>].started_at = <iso>`
- Add `path_locks[<path>] = <new-owner>` for each `Owns:` path in the step's `## Role`

## Step 4 — Update step file

Edit `phases/<name>/step<N>.md` `## Role` section:
- `Owner: <new-owner>`
- `Branch: feat/<scope>-<new-owner>-<slug>`
- `Worktree: .worktrees/<scope>-<new-owner>`
- Append: `Reassigned from <old-owner> at <iso> by PM.`

## Step 5 — Append session-log

```
[HH:MM] PM reassign: step<N> from <old-owner> to <new-owner> (reason: <one-line>)
```

## Validation gates

- `owners.json` is valid JSON after the change
- Old owner's `active_step` is null
- New owner's `active_step == <N>`
- `step<N>.md` Role section updated
- Session-log entry appended

## Iron Laws

- L5-R (non-overlap) — release-then-grant; no transient overlap allowed
- L5 (one answer per question) — PM does not ask; PM decides

## Anti-patterns

- ❌ Calling this skill without being PM (role-owners must ask PM)
- ❌ Granting ownership without first releasing the old owner (transient overlap)
- ❌ Reassigning to a name not in PRD §4 Role table

## Next step

```
# New owner continues:
cd .worktrees/<scope>-<new-owner>
/dev-kit-lite:build-tdd
```
