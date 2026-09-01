---
name: team-roster
category: plan
description: Define the team roster (role + identifier + name, multiple per role) AND split steps by dependency graph. Sync to plan with coverage check so no one is left out.
when_to_use:
  - Right after bootstrap, before plan
  - When a team member joins or leaves mid-sprint
  - Coverage check: which roster members have zero step assignments?
  - When adding new steps and need to ensure dependency order is preserved
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:team-roster

## Role

You are the team's roster steward AND dependency-aware work splitter. Maintain a single source-of-truth list of every human on this sprint, and prove — before the first commit lands — that (a) nobody on the roster is unassigned AND (b) every step is split along a real dependency edge so parallel work doesn't collide on shared surfaces. Cold realism: if a member has zero steps, surface that. If a step spans two owners without an explicit handoff, surface that.

## Inputs

The skill takes **two coupled inputs**:

### Input 1 — Roster

JSON array of `{role, identifier, name}` objects. Collect via paste, CSV, or read of `.dev-kit/team-roster.json`. One `AskUserQuestion` per missing field (L5: one answer each), starting with PM (mandatory).

### Input 2 — Dependency graph

Either:
- A `dependencies` block in `PRD.md` §2 Scope (each step lists `depends_on: [stepN, ...]`)
- An inline paste: `step-name: [dep1, dep2, ...]`
- Auto-derive from path locks in `phases/<name>/owners.json` (steps touching the same path → likely sequential)

If neither, ask the user for step names + dependency list once at the start of the call.

## Roles

| Role key | Display name | Multi-person? | Mandatory? |
|----------|--------------|---------------|------------|
| `planner` | PM / Coordinator | yes (1+ recommended) | yes — warn if zero |
| `frontend` | Frontend | yes (2 recommended) | warn if zero |
| `backend` | Backend | yes (2 recommended) | warn if zero |
| `ai` | AI Engineer | yes (1+ recommended) | warn if zero |
| `design` | Design (Figma MCP) | yes (1 recommended) | warn if zero |

## Identifier rules

- **Scope**: identifier is unique **within its role** (not globally). `frontend` may have `fe-1`, `fe-2`; `backend` may also have `backend-1`; `frontend` and `backend` identifiers do not collide.
- **Format**: kebab-case ASCII, ≤ 32 chars, no spaces. Examples: `fe-1`, `be-alice`, `ai-rag-1`, `design-evil`.
- **Stable across the sprint**: once committed, the identifier is the addressable handle for that person. Renaming mid-sprint is allowed only via `/dev-kit-lite:reassign`.

## Dependency rules

- **DAG only**: dependency graph must be acyclic. A cycle is a hard error — print the cycle and refuse to proceed.
- **Self-dependency forbidden**: a step cannot depend on itself.
- **Edge = handoff**: an edge `A → B` means "B cannot start until A is merged into `main` (or at least reachable to B's owner)". If A and B share the same owner, the edge is a sequencing hint, not a hard block — note this in the report.
- **Cross-role edge**: edges that cross roles (design → frontend → backend → ai) are the norm. The skill should explicitly print the cross-role handoff chain.
- **Critical path**: longest path in the DAG by step count. Owners on the critical path get priority attention in the report.

## Workflow

### Step 1 — Collect roster

If `AskUserQuestion` mode, one field at a time. If paste/CSV mode, parse and validate.

### Step 2 — Validate roster

For each entry, check:
- `role` is one of the 5 supported values
- `identifier` matches `^[a-z0-9][a-z0-9-]{0,31}$`
- `identifier` is unique within its role
- `name` is non-empty (warn if missing)

Then check the roster as a whole:
- ≥ 1 planner (warn loudly — without PM the L5-R registry can't enforce non-overlap)
- ≥ 1 frontend, backend, ai, design recommended (warn but allow zero)
- No duplicate `(role, identifier)` pairs

### Step 3 — Collect + validate dependency graph

If the user did not provide dependencies, ask once: "Which steps depend on which? (e.g., `frontend-checkout: [api-checkout, design-tokens]`)" — then proceed.

Validate:
- All referenced step names exist (or will be created)
- No self-loops: `step: [step, ...]` is a hard error
- No cycles: run topological sort; if it fails, print the cycle and refuse to proceed
- Identify the **critical path** (longest chain) — print it for the report
- Identify **parallelizable layers** (steps with no in-edges at each layer) — these are the parallel work batches

### Step 4 — Write `.dev-kit/team-roster.json`

```json
{
  "version": 1,
  "updated_at": "<iso8601>",
  "members": [
    {"role": "planner", "identifier": "pm-1", "name": "Alice"},
    {"role": "frontend", "identifier": "fe-1", "name": "Bob"},
    {"role": "frontend", "identifier": "fe-2", "name": "Bea"},
    {"role": "backend", "identifier": "be-1", "name": "Carol"},
    {"role": "ai", "identifier": "ai-1", "name": "Dan"},
    {"role": "design", "identifier": "design-1", "name": "Eve"}
  ],
  "dependencies": {
    "design-tokens": [],
    "design-checkout-screen": ["design-tokens"],
    "api-models": [],
    "api-checkout": ["api-models"],
    "frontend-checkout": ["api-checkout", "design-checkout-screen"],
    "ai-prompt-iteration": ["frontend-checkout"]
  },
  "critical_path": ["api-models", "api-checkout", "frontend-checkout", "ai-prompt-iteration"]
}
```

### Step 5 — Split steps by dependency, assign to owners

This is the **dependency-aware division** step. For each step:

1. Determine its **dependency layer** (longest path from a root step to this one)
2. Determine its **role** (frontend step → frontend owner, backend step → backend owner, etc.)
3. Assign to an owner in that role:
   - First choice: a roster member with no other step at the same dependency layer (maximizes parallelism)
   - Second choice: a roster member whose other steps at this layer don't share path locks
   - Fallback: any roster member in the role (warn — single-person-role bottleneck)

If a step can't be assigned (no roster member in the required role), flag it as `UNASSIGNABLE` and block success.

### Step 6 — Sync to plan data

If `phases/<name>/owners.json` exists, augment each entry with an `identifier` field. Roster members not yet in `owners.json` are added with `active_step: null` and empty `owns_paths`.

For each step in `phases/<name>/step<N>.md`, update the `## Role` section:
- `Owner:` field is the roster `identifier` (not the name)
- New `Depends on:` line lists predecessor step identifiers (empty if root)
- New `Layer:` line with the dependency layer number
- New `Roster:` line with `identifier → name` mapping for that step's owner

### Step 7 — Coverage check (the "no one left out" gate)

For each roster member, determine assignment status:

| Status | Definition |
|--------|-----------|
| `assigned` | appears as `Owner` (by identifier) in ≥ 1 `phases/<name>/step<N>.md` `## Role` section |
| `pending` | exists in `owners.json` but no step references them |
| `orphan` | not in `owners.json` at all |

**Hard rule**: any roster member with status `pending` or `orphan` blocks the skill from returning success.

Also flag:
- Steps with `UNASSIGNABLE` status (no roster member in the required role)
- Steps with ambiguous role (matches multiple roles equally) — PM should clarify

### Step 8 — Render report

```markdown
# Team Roster: <project name>

## Members (N)

| Role | Identifier | Name | Status |
|------|------------|------|--------|
| planner | pm-1 | Alice | assigned |
| frontend | fe-1 | Bob | assigned (layer 3) |
| frontend | fe-2 | Bea | PENDING |
| backend | be-1 | Carol | assigned (layer 2) |
| ai | ai-1 | Dan | assigned (layer 4) |
| design | design-1 | Eve | assigned (layer 1) |

## Dependency graph (topological order)

Layer 0: api-models, design-tokens
Layer 1: api-checkout, design-checkout-screen
Layer 2: frontend-checkout
Layer 3: ai-prompt-iteration

## Critical path

`api-models → api-checkout → frontend-checkout → ai-prompt-iteration` (4 steps)

## Cross-role handoff chain

`design-1 (tokens) → design-1 (screen) → be-1 (api) → fe-1 (frontend) → ai-1 (prompt)`

## Coverage check

- **Assigned**: 5 / 6
- **Pending (no step)**: 1 — fe-2 (Bea)
- **Orphan**: 0
- **Unassignable steps**: 0

## Recommended next actions

1. Add a frontend step at layer 1+ for fe-2 (Bea) — e.g., `frontend-list` (depends on `api-models`)
2. After adding, re-run `/dev-kit-lite:plan-update` and then `/dev-kit-lite:team-roster` to re-verify

## Files written

- `.dev-kit/team-roster.json` (N members + dependency graph + critical path)
- `phases/<name>/owners.json` (M entries updated with `identifier`)
- `phases/<name>/step<N>.md` (K step Role sections updated with `Depends on:` + `Layer:`)
```

## Validation gates

- `.dev-kit/team-roster.json` parses as JSON, has `version: 1`, ≥ 1 member
- Every member has unique `(role, identifier)` pair
- ≥ 1 planner (warning allowed, hard block if zero)
- Dependency graph is a valid DAG (topological sort succeeds)
- Critical path computed and printed
- Coverage check ran with status counts printed
- All `pending` / `orphan` / `UNASSIGNABLE` items listed in the report

## Iron Laws

- **L2** (verification before completion) — count assigned/pending/orphan/unassignable, verify numbers before declaring success
- **L3** (evidence before claim) — every assignment status cites the file:line that justifies it
- **L5** (one answer per question) — ask one roster field at a time when collecting
- **L5-R** (non-overlap) — sync must not create duplicate `owners.json` entries; assignment must not put two owners on the same path lock at the same layer

## Anti-patterns

- ❌ Letting the user say "I'll add them later" without flagging them as `pending`
- ❌ Silently dropping roster members who have zero steps — surface them
- ❌ Using person name as identifier — identifier must be role-scoped and stable
- ❌ Auto-assigning arbitrary steps to fill unassigned members — let the PM decide
- ❌ Ignoring dependency order when assigning — owner of step X must not start before step X's deps are merged
- ❌ Assigning two owners to the same dependency layer if they share path locks — surfaces as a L5-R violation
- ❌ Treating cyclic dependencies as "we'll figure it out" — refuse and print the cycle

## Next step

- Coverage OK (all `assigned`, all steps `assignable`) → `/dev-kit-lite:plan` (if not yet run) or `/dev-kit-lite:build-tdd` (if plan exists)
- Coverage has `pending` members → `/dev-kit-lite:plan-update` to add missing steps, then re-run `team-roster` to re-verify
- Coverage has `UNASSIGNABLE` steps → add a roster member in that role, or change the step's role
- Cyclic dependency → restructure the dependency graph (likely means a step is too coarse-grained)

## Coverage re-check (idempotent)

Re-running `/dev-kit-lite:team-roster` with the same roster is safe — it re-syncs `owners.json` and re-runs the coverage check without overwriting existing `active_step` values. Use this after `/dev-kit-lite:plan-update` to confirm zero pending members.
