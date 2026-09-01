---
name: plan
category: plan
description: 3-gate lite plan: Frame → Phase → AC. Writes PRD.md + phases/<name>/ + owners.json.
when_to_use:
  - At the start of every MVP sprint (after bootstrap)
  - When scope is well-known (no 5-field safety contract interview)
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:plan

## Workflow

3 gates (lite version; full kit has 5 + interview). PM runs this once per sprint.

## Gate 1 — Frame

Ask the user 3 questions (L5: one answer each):

1. **Goal** (1 sentence): What does the MVP do?
2. **Target user** (1 sentence): Who is this for?
3. **Situation** (1 sentence): Why now / what triggered this sprint?

Write to `PRD.md §1 Frame`.

## Gate 2 — Phase plan

Ask the user for the **role assignment** (see `rules/role-*.md`):

| Role | Default headcount |
|------|-------------------|
| PM / Coordinator | 1 |
| Frontend | 2 |
| Backend | 2 |
| Design (Figma MCP) | 1 |

User provides actual names. PM writes `PRD.md §4 Role assignment` table.

Then ask: "What are the 3-8 steps to ship this MVP?" Each step gets:
- Title
- Owner (one person from §4 table)
- Discipline (FE | BE | Design | PM)
- AC reference (1-2 ACs)

Write `PRD.md §5 Phase plan` table AND create:
- `phases/<name>/index.json` — step manifest
- `phases/<name>/step<N>.md` per step (with `## Role` section per `templates/step.md`)
- `phases/<name>/owners.json` — initial L5-R non-overlap registry (see `templates/owners.example.json`)

## Gate 3 — AC + Scope

Ask the user for the **Acceptance Criteria** (runnable commands):

```markdown
- AC-1: `pytest tests/test_x.py::test_y -v` → exit 0, 1 passed
- AC-2: `npm run build && npm run lint` → exit 0
- AC-3: `curl -X POST /api/...` → 200, JSON schema matches
```

Write `PRD.md §3 AC list` and `PRD.md §2 Scope` (in-scope vs out-of-scope).

## Output

```
PRD.md                                # 6-section
phases/<name>/index.json              # step manifest
phases/<name>/step1.md ... stepN.md   # per-step docs with ## Role
phases/<name>/owners.json             # L5-R non-overlap registry
```

## Validation gates

- `PRD.md` has all 6 sections (§1 Frame, §2 Scope, §3 AC, §4 Role, §5 Phase, §6 Hand-off)
- `phases/<name>/index.json` has `pending` status for every step
- Each `step<N>.md` has `## Role` section with Owner / Discipline / Branch / Worktree / Owns
- `owners.json` has unique Owner entries (no duplicates), unique path_locks entries

## Iron Laws

- L5 (one answer per question) — use AskUserQuestion with multiSelect=false
- L5-R (non-overlap) — owners.json enforces uniqueness

## Next step

```
/dev-kit-lite:ci-setup        # opt-in: install advisory review.yml
# or
/dev-kit-lite:build-tdd       # jump to TDD
```
