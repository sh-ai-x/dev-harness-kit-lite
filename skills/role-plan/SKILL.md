---
name: role-plan
category: plan
description: Generate per-role plan docs from the project plan. Each role gets a focused doc with only their assigned steps, their dependencies, and their tech-stack-specific guidance. PM uses this to give each role-owner a clean starting point instead of pointing them at the full PRD + every step file.
when_to_use:
  - Right after /dev-kit-lite:plan writes PRD.md + phases/<name>/
  - After /dev-kit-lite:plan-update modifies the plan mid-sprint
  - After /dev-kit-lite:team-roster changes ownership
  - When a role-owner joins and wants to see only their work
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:role-plan

## Role

You are the role-doc generator. The PM just finished `/dev-kit-lite:plan` (or `/dev-kit-lite:plan-update`) and produced one PRD.md plus N step files in `phases/<name>/`. Now you slice that into **one focused doc per role** so each role-owner opens a single file and sees only their lane. Cold realism: a role-owner should never have to grep through 30 step files to find theirs. The output is the role's daily-driver doc.

## Inputs

Read these from `.dev-kit/` and `phases/<name>/`:

| File | What it provides |
|------|------------------|
| `.dev-kit/role-config.json` | role taxonomy + tech_stack + owns_paths per role |
| `.dev-kit/team-roster.json` | members with `{role, identifier, name}` |
| `PRD.md` | goal, scope, AC list |
| `phases/<name>/index.json` | step manifest with dependencies |
| `phases/<name>/owners.json` | step → owner identifier + active_step |
| `phases/<name>/step<N>.md` | per-step detail |

## Output layout

For each role that owns at least one step (and `planner` always), write:

```
phases/<name>/role-plans/<role-key>.md
```

Five files in a typical project: `planner.md`, `frontend.md`, `backend.md`, `ai.md`, `design.md`. Empty files for roles with zero assigned steps (the team-roster skill already blocks that — see L5-R — but defensively we emit a stub).

## Workflow

### Step 1 — Resolve role taxonomy

```bash
cat .dev-kit/role-config.json | jq '.roles | keys[]'
```

Print the 5 roles. For each, load `tech_stack`, `owns_paths`, `shared_read_paths`, `boundary_notes`.

### Step 2 — Filter steps per role

For each role `<key>`:

1. Find every step in `phases/<name>/index.json` where `owner` matches an identifier in `.dev-kit/team-roster.json` whose `role == <key>`.
2. Compute the **dependency closure** for that subset (every dependency the role's steps need, even if that dep is owned by another role — the role needs to *know* about the dep but doesn't *own* it).
3. Compute the **cross-role read paths** from `role-config.json[role].shared_read_paths`.
4. Compute the **critical path** filtered to layers this role touches.

### Step 3 — Write each role's plan doc

```markdown
# <Role display name> plan — <project name>

**Your identifier:** `<role-key>-1` (or whichever one this plan is for)
**Tech stack:** `<tech_stack>`
**Your lane (owns_paths):** `paths/...`, `paths/...`
**Cross-role reads:** `shared/path/`, `other/path/`
**Boundary notes:** <boundary_notes from role-config>

## Your steps

| Layer | Step | Depends on | Status | AC count |
|-------|------|-----------|--------|----------|
| 0 | <step-id> | — | pending | 3 |
| 1 | <step-id> | <upstream step> | blocked | 2 |

## Critical path (your slice)

`<step1> → <step2> → <step3>` (X layers)

## Dependencies you don't own (read-only awareness)

- `<upstream step>` (owned by `<other-role-key>-N`) — what you wait on
- `<downstream step>` (owned by `<other-role-key>-M`) — what they wait on you for

## Cross-role read paths

You may READ (not write):
- `path/A/` — owned by `<other-role-key>-1` (their contract with you)
- `path/B/` — owned by `<other-role-key>-2`

## Per-step detail

### <step-id>

- **Status:** pending | in-progress | done
- **Owner:** `<role-key>-N`
- **Branch convention:** `feat/<scope>-<your-identifier>-<slug>`
- **Worktree:** `.worktrees/<your-identifier>`
- **Acceptance Criteria:**
  - AC-1: <verbatim from PRD or step file>
  - AC-2: <verbatim>
- **TDD entry point:** `pytest tests/test_<x>.py -v` (or whichever test command your tech_stack implies)
- **Cross-role handoff at end:** push to PR, run `/dev-kit-lite:build-verify`, hand off to `<downstream role>` via PR merge

## Your TDD loop

For each step in order of dependency layer:

1. Open a worktree: `git worktree add -b feat/<scope>-<your-identifier>-<step-id> .worktrees/<your-identifier> origin/main`
2. Run `/dev-kit-lite:role-tdd` in that worktree — it scopes to your steps automatically
3. Run `/dev-kit-lite:review` after the PR is open
4. Run `/dev-kit-lite:build-verify` after merge

## Boundary reminders

- You write ONLY to your `owns_paths`. Writing to another role's lane opens a hand-off — propose it via `/dev-kit-lite:plan-update` instead of doing it silently.
- You READ freely from `shared_read_paths`. Don't write.
- If you find your assigned steps don't fit your `tech_stack`, run `/dev-kit-lite:role` to change the stack — don't paper over with mismatched tooling.
```

### Step 4 — Write the planner's overview

`phases/<name>/role-plans/planner.md` is special — it lists every role's plan and the cross-role handoff chain:

```markdown
# PM plan — <project name>

## Phase summary

| Step | Layer | Owner | Role | Status | Depends on |
|------|-------|-------|------|--------|-----------|
| design-tokens | 0 | design-1 | design | pending | — |
| api-models | 0 | be-1 | backend | pending | — |
| ... | | | | | |

## Cross-role handoff chain

```
design-1 (tokens) → design-1 (screen) → be-1 (api) → fe-1 (frontend) → ai-1 (prompts)
```

## Per-role plan docs

- [Frontend](./frontend.md) — owned by `<fe-identifier>`, `<fe-identifier>`
- [Backend](./backend.md) — owned by `<be-identifier>`, `<be-identifier>`
- [AI](./ai.md) — owned by `<ai-identifier>`
- [Design](./design.md) — owned by `<design-identifier>`

## Open issues

- <list of pending role-stack confirmations, unassigned steps, etc.>
```

### Step 5 — Update CHANGELOG

Append a one-line entry to `CHANGELOG.md` recording the role-plan generation timestamp.

## Validation gates

- `phases/<name>/role-plans/<role-key>.md` exists for every role in `role-config.json`
- Each role's plan lists ONLY their assigned steps (no foreign steps in their "Your steps" table)
- Each role's plan cites the step `## Acceptance Criteria` verbatim (no paraphrasing)
- The planner overview (`planner.md`) lists every step from `phases/<name>/index.json` exactly once
- Dependency edges in role plans match `phases/<name>/index.json` (no new edges, no dropped edges)
- `file:line` evidence per role for each "this is your step" claim (L3)

## Iron Laws

- **L2** (verification before completion) — count steps across all role-plans vs `index.json`; they MUST match
- **L3** (evidence before claim) — every "this is your step" attribution cites the file:line in `index.json` + `owners.json`
- **L5** (one answer per question) — one role field at a time when collecting inputs
- **L5-R** (non-overlap) — every step appears in EXACTLY ONE role's "Your steps" table

## Anti-patterns

- ❌ Putting a step in two roles' plans ("Frontend can also work on the API surface" — no, that's a SRP violation; reassign via plan-update)
- ❌ Paraphrasing the AC instead of quoting it verbatim (drift between role-doc and PRD causes "but my plan said..." disputes)
- ❌ Adding "future work" or "polish later" bullets to a role plan (that's the PM's job, not the role's)
- ❌ Empty role-plan files for roles with zero steps — emit a stub explaining the role is reserved but not yet assigned
- ❌ Forgetting the planner overview — without it, the PM has to re-read all role plans to know progress
- ❌ Embedding another role's detail in your role plan ("for context, here's what BE is doing") — link to their plan file instead

## Next step

- All role-plans written → role-owners open their assigned worktree, run `/dev-kit-lite:role-tdd` to start the first step
- Mid-sprint role changes → re-run `role-plan` (idempotent; regenerates all role-plan files from current state)
- New step added via `plan-update` → re-run `role-plan` to refresh the affected role's doc
