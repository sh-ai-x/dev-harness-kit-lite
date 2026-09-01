---
name: role
category: plan
description: Manage role taxonomy (planner / frontend / backend / ai / design) with SRP-aware directory separation. Single source of truth for role defaults (owned directory, headcount, branch prefix, allowed tools) consumed by plan + plan-update + team-roster.
when_to_use:
  - Adding or modifying a role
  - Changing role defaults (headcount, owned directory, branch prefix, allowed tools)
  - Plan/plan-update needs to resolve role → defaults
  - Designing a monorepo or multi-repo layout where each role owns a clean surface
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:role

## Role

You are the role taxonomy steward AND the SRP (Single Responsibility Principle) enforcer for the repo layout. The 5 roles in this kit (`planner`, `frontend`, `backend`, `ai`, `design`) are not hardcoded — they live in `templates/roles-matrix.md` (human-readable) and `.dev-kit/role-config.json` (machine-readable). `plan` and `plan-update` consume the JSON. `team-roster` consumes both. Keep them in sync. Cold realism: if a role's owned directory overlaps with another role, surface the violation. If two roles touch the same file, that's a structural smell — recommend splitting or reassigning before plan generation.

## SRP rule (the hard constraint)

**Every file in the repo is owned by exactly one role.** Cross-role touching is a design defect, not a normal state.

To enforce this, every role's `owns_paths` must resolve to a **disjoint** set of directories. The top-level repo layout must be partitionable into role-owned slices without overlap:

```
<repo-root>/
├── apps/                      # → frontend
├── api/                       # → backend
├── services/                  # → backend
├── models/                    # → backend
├── prompts/                   # → ai
├── eval/                      # → ai
├── retrieval/                 # → ai
├── lib/llm/                   # → ai
├── tools/                     # → ai (shared tool plumbing)
├── design/                    # → design
├── tokens/                    # → design
├── figma-export/              # → design
├── tests/test_prompts.py      # → ai
├── tests/test_eval.py         # → ai
├── tests/test_*.py (other)    # → backend or frontend by language
├── PRD.md                     # → planner
├── .dev-kit/                  # → planner
└── phases/<name>/             # → planner (registry; steps belong to their owners)
```

Two structural layouts are supported (chosen at `bootstrap` time, recorded in `role-config.json` → `repo_layout`):

| Layout | When to use | Trade-off |
|--------|-------------|-----------|
| `monorepo` (default) | Single repo, role-owned subtrees. PR review sees cross-role changes. | Simpler ops. SRP violation visible in PR diff. |
| `multi-repo` | One repo per role + shared `contracts/` repo for interfaces. | Clean blast-radius. Cross-role change requires multiple PRs + a contracts bump. |

The skill recommends `monorepo` for 4-hour sprints (speed > isolation). `multi-repo` is for projects that already have one repo per role.

## Inputs

Three input modes (L5: one answer at a time when in interactive mode):

1. **No-arg query** — list current roles, their defaults, and SRP-overlap status.
2. **Add role** — provide `{role_key, display_name, headcount_default, owns_paths, branch_prefix, default_tools}`.
3. **Modify role** — provide role_key + the fields to change.

## Built-in roles (defaults — do not hardcode, read from config)

| role_key | display_name | headcount | owns_paths (SRP-disjoint) | branch_prefix | default_tools |
|----------|--------------|-----------|---------------------------|---------------|---------------|
| `planner` | PM / Coordinator | 1+ (mandatory) | `PRD.md`, `.dev-kit/**`, `phases/<name>/**` | — (no feature branches) | `AskUserQuestion`, `Read`, session-log append |
| `frontend` | Frontend | 2+ | `apps/`, `components/`, `hooks/`, `styles/`, `public/`, frontend-side `package.json`, `tsconfig.json`, `next.config.js` | `feat/web-<owner>-<slug>` | `npm`, `npm test`, `npm run build`, `npm run lint`, Next.js |
| `backend` | Backend | 2+ | `api/`, `services/`, `models/`, backend-side `tests/` (pytest), `requirements.txt`, `pyproject.toml`, `alembic/` | `feat/api-<owner>-<slug>` | `pytest`, `mypy`, `ruff`, FastAPI/Flask/Django |
| `ai` | AI Engineer | 1+ | `prompts/`, `eval/`, `retrieval/`, `lib/llm/`, `tools/` (shared, read-only for non-ai), `tests/test_prompts.py`, `tests/test_eval.py` | `feat/ai-<owner>-<slug>` | `pytest`, `ruff`, MiniMax/Anthropic API SDK, prompt-eval harness |
| `design` | Design (Figma MCP) | 1+ | `design/`, `tokens/`, `figma-export/`, `screenshots/` | `feat/design-<owner>-<slug>` | `mcp__figma__*` tools, JSON validators |

**SRP note**: `tools/` is owned by `ai` but exposed read-only to other roles (cross-role reads are allowed; cross-role writes are not). All other dirs are exclusive.

## Workflow

### Step 1 — Resolve current role config

Read `.dev-kit/role-config.json` if it exists; otherwise fall back to parsing `templates/roles-matrix.md`. Print the active config so the user sees the source of truth, including `repo_layout`.

### Step 2 — SRP-overlap check

Compute the union of all roles' `owns_paths` globs. For every file in the repo (git ls-files), verify exactly one role claims it. Files claimed by zero roles = "planner's lane by default" (config files, root-level docs). Files claimed by > 1 role = **SRP violation**, list them and refuse to declare success.

### Step 3 — Validate proposed change

For `add` or `modify`:
- `role_key` must match `^[a-z][a-z0-9-]{0,31}$` (kebab-case, ≤ 32 chars)
- `display_name` non-empty
- `headcount_default` is `1+`, `2+`, or a number
- `owns_paths` is a non-empty array of glob paths; reject if any path overlaps another role's `owns_paths` (SRP)
- `branch_prefix` is `feat/<scope>-<owner>-<slug>` form OR empty (for `planner`)
- `default_tools` is an array of tool names
- For `modify`: changing `owns_paths` is a hard warning if plan data references the role (steps may now fall outside the lane)

For `planner`: cannot be deleted (mandatory).

### Step 4 — Write role config

Two files, written together:

**`.dev-kit/role-config.json`** (machine-readable, consumed by plan/plan-update/team-roster):

```json
{
  "version": 1,
  "updated_at": "<iso8601>",
  "repo_layout": "monorepo",
  "roles": {
    "planner": {
      "display_name": "PM / Coordinator",
      "mandatory": true,
      "headcount_default": 1,
      "owns_paths": ["PRD.md", ".dev-kit/**", "phases/<name>/**"],
      "branch_prefix": null,
      "default_tools": ["AskUserQuestion", "Read", "session-log append"],
      "rules_file": "rules/role-pm-coordinator.md"
    },
    "frontend": { ... },
    "ai": {
      "display_name": "AI Engineer",
      "mandatory": false,
      "headcount_default": 1,
      "owns_paths": ["prompts/**", "eval/**", "retrieval/**", "lib/llm/**", "tests/test_prompts.py", "tests/test_eval.py"],
      "branch_prefix": "feat/ai-<owner>-<slug>",
      "default_tools": ["pytest", "ruff", "minimax-sdk", "anthropic-sdk", "prompt-eval"],
      "rules_file": "rules/role-ai.md",
      "shared_read_paths": ["tools/**"]
    }
  }
}
```

**`templates/roles-matrix.md`** (human-readable, regenerated from JSON).
**`templates/repo-layout.md`** (NEW, human-readable directory map showing which role owns each top-level dir).

### Step 5 — Generate per-role rules file

For any role that doesn't have a matching `rules/role-<key>.md`, write one using the JSON config (see Step 4 example for `ai`).

### Step 6 — Cross-reference with plan data (read-only check)

If `phases/<name>/owners.json` exists:
- For each step's owner, verify their role still exists in the new config
- If a role was removed and owners reference it, warn loudly
- If `owns_paths` was modified, list steps whose `Ows:` paths fall outside the new lane

### Step 7 — Emit SRP-driven plan design hints

Print a "Suggested step partition" block the `plan` skill consumes:

```markdown
## Suggested plan partition (from role SRP map)

| Layer | Step | Role | Owner identifier | Lane (dir) | Depends on |
|-------|------|------|------------------|------------|-----------|
| 0 | design-tokens | design | design-1 | design/, tokens/ | — |
| 0 | api-models | backend | be-1 | api/, models/ | — |
| 1 | api-checkout | backend | be-1 | api/ | api-models |
| 2 | frontend-checkout | frontend | fe-1 | apps/, components/ | api-checkout, design-tokens |
| 3 | ai-prompt-iteration | ai | ai-1 | prompts/, eval/ | frontend-checkout |
```

Each step lives in EXACTLY ONE role's directory. Cross-role coordination happens via the handoff chain, never via shared file ownership.

### Step 8 — Render change report

```markdown
# Role config update

## SRP check

- Total files in repo: 234
- Files owned by exactly one role: 234
- SRP violations: 0

## Changes

- **ai**: ADDED
  - owns_paths: prompts/**, eval/**, retrieval/**, lib/llm/**, tests/test_prompts.py, tests/test_eval.py
  - shared_read_paths: tools/**
- **frontend**: MODIFIED
  - owns_paths: removed `styles/` (reassigned to design)

## Files written

- .dev-kit/role-config.json (5 roles)
- templates/roles-matrix.md (regenerated)
- templates/repo-layout.md (new)
- rules/role-ai.md (new per-role rules file)

## Cross-references with plan data

- phases/<name>/owners.json: 4 entries match new config
- 0 owners reference removed roles
- 0 steps have Ows paths outside new lanes
```

## Validation gates

- `.dev-kit/role-config.json` parses as JSON, has `version: 1`, all 5 built-in roles present (planner mandatory)
- SRP check: 0 violations (no file claimed by > 1 role)
- `templates/roles-matrix.md` regenerated from JSON (no drift)
- `templates/repo-layout.md` exists and matches JSON
- For each role, matching `rules/role-<key>.md` exists
- Cross-reference check ran

## Iron Laws

- **L2** (verification before completion) — regenerate matrix + repo-layout from JSON, verify they match before writing
- **L3** (evidence before claim) — every SRP violation cites the file path and which two roles claim it
- **L5** (one answer per question) — one role field at a time when collecting
- **L5-R** (non-overlap) — role `owns_paths` MUST be disjoint (hard rule); `shared_read_paths` is the only escape hatch for cross-role reads

## Anti-patterns

- ❌ Two roles claiming the same `owns_paths` glob — fix by splitting the directory
- ❌ Hardcoding role defaults in `plan` / `plan-update` skills — they MUST read from `.dev-kit/role-config.json`
- ❌ Editing `templates/roles-matrix.md` by hand and forgetting to regenerate the JSON (drift)
- ❌ Adding a role without a corresponding `rules/role-<key>.md`
- ❌ Removing `planner` (mandatory role)
- ❌ Writing to another role's directory even "just to fix one line" — open a handoff instead
- ❌ Using `shared_read_paths` to bypass SRP — only allowed for code-generated artifacts and shared utilities
- ❌ Marking a role `mandatory: false` retroactively if owners reference it — would orphan steps

## Next step

- New role added → run `/dev-kit-lite:team-roster` to add members to it
- Role `owns_paths` changed → run `/dev-kit-lite:plan-update` to align existing step `Ows:` paths
- Role removed → run `/dev-kit-lite:reassign` to move affected steps to other roles
- SRP violation detected → recommend directory split, then re-run `plan`

## Downstream contracts

This skill is the **upstream** of four:

| Skill | Reads from `role` |
|-------|-------------------|
| `plan` | uses `headcount_default`, `owns_paths`, `branch_prefix`, `repo_layout` when generating steps; consumes the "Suggested plan partition" output |
| `plan-update` | validates that step owner role still exists + `owns_paths` still covers the step's `Ows:` |
| `team-roster` | uses `headcount_default` to warn when a role has fewer members than recommended |
| `build-tdd` | reads `owns_paths` from the step's role to enforce write boundaries in the worktree |

If `role` is updated, those four skills must be re-invoked to pick up the new defaults.
