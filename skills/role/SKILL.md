---
name: role
category: plan
description: Manage role taxonomy (planner / frontend / backend / ai / design) with cleanly-separated responsibility areas. Source of truth for role defaults (owned directory, headcount, branch prefix, allowed tools) consumed by plan + plan-update + team-roster + build-tdd.
when_to_use:
  - Adding or modifying a role
  - Changing role defaults (headcount, owned directory, branch prefix, allowed tools)
  - Plan/plan-update needs to resolve role → defaults
  - Designing a monorepo or multi-repo layout where each role owns a clear responsibility area
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:role

## Role

You are the role taxonomy steward AND the **responsibility-area separator** for the repo layout. The 5 roles in this kit (`planner`, `frontend`, `backend`, `ai`, `design`) are not hardcoded — they live in `templates/roles-matrix.md` (human-readable) and `.dev-kit/role-config.json` (machine-readable). `plan` and `plan-update` consume the JSON. `team-roster` consumes both. Keep them in sync.

> **SRP here = "responsibility-area separation" (책임영역 분리)**, NOT "every file has exactly one owner". The principle is about giving each role a **clear, well-bounded responsibility area** that does not bleed into another's. Overlap at well-defined shared zones (build configs, root-level docs, generated artifacts) is allowed and expected — what is **not** allowed is *unclear* responsibility: a directory that two roles both feel they own, with no documented boundary.

Cold realism: if two roles reach for the same directory without a documented split, surface the ambiguity. Recommend either (a) assign the directory to one role, (b) split the directory, or (c) declare it a shared zone with explicit write rules.

## The responsibility-area model

Each role has:

| Field | Meaning | Example |
|-------|---------|---------|
| `owns_paths` | Directories/files this role **writes** exclusively. Other roles read but don't write. | `apps/`, `components/`, `prompts/`, `eval/` |
| `shared_read_paths` | (optional) Paths this role does NOT own but may read. Used for cross-role contracts. | `tools/` (AI owns, others read) |
| `shared_write_paths` | (optional, rare) Paths co-written by multiple roles with explicit co-edit rules. Used for cross-cutting config that genuinely needs two hands. | root `package.json` for full-stack features |
| `boundary_notes` | Free-text explaining where this role's responsibility ends and another's begins. | "frontend owns UI; backend owns `/api/*` they call. contracts/ is the bridge." |

The hard rule: **`owns_paths` between two roles MUST NOT overlap**. `shared_read_paths` is fine (a role reads what another owns). `shared_write_paths` requires explicit PM sign-off per role pair — print a loud warning.

## Inputs

Three input modes (L5: one answer at a time when in interactive mode):

1. **No-arg query** — list current roles, their defaults, and the responsibility-area map.
2. **Add role** — provide `{role_key, display_name, headcount_default, owns_paths, shared_read_paths?, shared_write_paths?, branch_prefix, default_tools, boundary_notes?}`.
3. **Modify role** — provide role_key + the fields to change.

## Built-in roles (defaults — do not hardcode, read from config)

| role_key | display_name | headcount | owns_paths (exclusively) | shared_read | branch_prefix | default_tools |
|----------|--------------|-----------|---------------------------|-------------|---------------|---------------|
| `planner` | PM / Coordinator | 1+ (mandatory) | `PRD.md`, `.dev-kit/**`, `phases/<name>/**` | all (read-only oversight) | — (no feature branches) | `AskUserQuestion`, `Read`, session-log append |
| `frontend` | Frontend | 2+ | `apps/`, `components/`, `hooks/`, `styles/`, `public/`, frontend-side `package.json`, `tsconfig.json`, `next.config.js` | `api/` (read for client types), `tokens/`, `tools/` | `feat/web-<owner>-<slug>` | `npm`, `npm test`, `npm run build`, `npm run lint`, Next.js |
| `backend` | Backend | 2+ | `api/`, `services/`, `models/`, backend-side `tests/` (pytest), `requirements.txt`, `pyproject.toml`, `alembic/` | `prompts/`, `tools/` | `feat/api-<owner>-<slug>` | `pytest`, `mypy`, `ruff`, FastAPI/Flask/Django |
| `ai` | AI Engineer | 1+ | `prompts/`, `eval/`, `retrieval/`, `lib/llm/`, `tests/test_prompts.py`, `tests/test_eval.py` | `tools/` | `feat/ai-<owner>-<slug>` | `pytest`, `ruff`, MiniMax/Anthropic API SDK, prompt-eval harness |
| `design` | Design (Figma MCP) | 1+ | `design/`, `tokens/`, `figma-export/`, `screenshots/` | `components/` (read for context) | `feat/design-<owner>-<slug>` | `mcp__figma__*` tools, JSON validators |

**Boundary notes:**
- `frontend` ↔ `backend` boundary: API contract lives in `api/` (backend writes, frontend reads for typing).
- `ai` ↔ `frontend` boundary: prompts consumed by frontend are exported from `prompts/` to `apps/<web>/prompts/` via a build step (read-only copy).
- `planner` owns the *registry* (`owners.json`) but not the *work* — every step belongs to its owner's role lane.

## Repo layouts

| Layout | When to use |
|--------|-------------|
| `monorepo` (default) | Single repo, role-owned subtrees. PR review sees cross-role changes. Speed > isolation. |
| `multi-repo` | One repo per role + shared `contracts/` repo for interfaces. Cross-role change requires multiple PRs + a contracts bump. |

The skill recommends `monorepo` for 4-hour sprints (speed > isolation). `multi-repo` is for projects that already have one repo per role.

## Workflow

### Step 1 — Resolve current role config

Read `.dev-kit/role-config.json` if it exists; otherwise fall back to parsing `templates/roles-matrix.md`. Print the active config so the user sees the source of truth, including `repo_layout`.

### Step 2 — Responsibility-area ambiguity check (NOT a per-file check)

The check is NOT "every file has exactly one owner". The check IS:

> **For every directory under the repo root, does the configuration unambiguously say which role owns it?**

For each top-level directory:
- If exactly one role's `owns_paths` matches → **clear** ✓
- If zero roles claim it → **default to planner** (root-level docs, configs) but flag for review
- If two or more roles claim it via `owns_paths` → **AMBIGUOUS** — must resolve (pick one owner, or split, or move to `shared_write_paths`)
- If a role's `owns_paths` overlaps another role's via `shared_read_paths` → **OK** (reads are non-exclusive); just print the read relationship

Print the responsibility-area map:

```
apps/                  → frontend (write), backend (read via API client), design (read for tokens)
api/                   → backend (write), frontend (read for types)
prompts/               → ai (write), backend (read for prompt catalog)
tools/                 → ai (write), all roles (read-only)
PRD.md                 → planner (write), all roles (read)
```

### Step 3 — Validate proposed change

For `add` or `modify`:
- `role_key` must match `^[a-z][a-z0-9-]{0,31}$` (kebab-case, ≤ 32 chars)
- `display_name` non-empty
- `headcount_default` is `1+`, `2+`, or a number
- `owns_paths` is a non-empty array of glob paths; reject if any `owns_paths` glob overlaps another role's `owns_paths` glob (responsibility-area conflict)
- `shared_read_paths` is fine to overlap (reads are non-exclusive)
- `shared_write_paths` requires an explicit `boundary_notes` justification — print a loud warning
- `branch_prefix` is `feat/<scope>-<owner>-<slug>` form OR empty (for `planner`)
- `default_tools` is an array of tool names
- For `modify`: changing `owns_paths` is a hard warning if plan data references the role (steps may now fall outside the lane)

For `planner`: cannot be deleted (mandatory).

### Step 4 — Write role config

Two files, written together:

**`.dev-kit/role-config.json`** (machine-readable, consumed by plan/plan-update/team-roster/build-tdd):

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
      "shared_read_paths": ["**"],
      "shared_write_paths": [],
      "branch_prefix": null,
      "default_tools": ["AskUserQuestion", "Read", "session-log append"],
      "boundary_notes": "Owns the registry (owners.json) and the cross-role hand-off cadence. Does not own product code.",
      "rules_file": "rules/role-pm-coordinator.md"
    },
    "frontend": {
      "display_name": "Frontend",
      "mandatory": false,
      "headcount_default": 2,
      "owns_paths": ["apps/**", "components/**", "hooks/**", "styles/**", "public/**", "package.json", "tsconfig.json", "next.config.js"],
      "shared_read_paths": ["api/**", "tokens/**", "tools/**"],
      "shared_write_paths": [],
      "branch_prefix": "feat/web-<owner>-<slug>",
      "default_tools": ["npm", "npm test", "npm run build", "npm run lint"],
      "boundary_notes": "Owns the UI surface. Reads API contracts (typed) and design tokens. Does not own server-side code or prompts.",
      "rules_file": "rules/role-frontend.md"
    },
    "ai": {
      "display_name": "AI Engineer",
      "mandatory": false,
      "headcount_default": 1,
      "owns_paths": ["prompts/**", "eval/**", "retrieval/**", "lib/llm/**", "tests/test_prompts.py", "tests/test_eval.py"],
      "shared_read_paths": ["tools/**"],
      "shared_write_paths": [],
      "branch_prefix": "feat/ai-<owner>-<slug>",
      "default_tools": ["pytest", "ruff", "minimax-sdk", "anthropic-sdk", "prompt-eval"],
      "boundary_notes": "Owns prompt catalog, eval harness, and retrieval plumbing. Other roles consume prompts as imports (never edit).",
      "rules_file": "rules/role-ai.md"
    }
  }
}
```

**`templates/roles-matrix.md`** (human-readable, regenerated from JSON).
**`templates/repo-layout.md`** (NEW, human-readable directory map showing which role owns each top-level dir, with read/write indicators).

### Step 5 — Generate per-role rules file

For any role that doesn't have a matching `rules/role-<key>.md`, write one using the JSON config (display_name, owns_paths, shared_read_paths, branch_prefix, default_tools, boundary_notes).

### Step 6 — Cross-reference with plan data (read-only check)

If `phases/<name>/owners.json` exists:
- For each step's owner, verify their role still exists in the new config
- If a role was removed and owners reference it, warn loudly
- If `owns_paths` was modified, list steps whose `Ows:` paths fall outside the new lane
- If two steps at the same dependency layer now share a `shared_write_paths` dir, that's a **co-edit conflict** — flag it

### Step 7 — Emit responsibility-area-driven plan design hints

Print a "Suggested plan partition" block the `plan` skill consumes. Each step lives in **one role's `owns_paths`** directory. Cross-role coordination happens via the handoff chain or `shared_read_paths`, never via shared `owns_paths`:

```markdown
## Suggested plan partition (from responsibility-area map)

| Layer | Step | Role | Owner identifier | Lane (dir) | Cross-role read | Depends on |
|-------|------|------|------------------|------------|-----------------|-----------|
| 0 | design-tokens | design | design-1 | design/, tokens/ | — | — |
| 0 | api-models | backend | be-1 | api/, models/ | — | — |
| 0 | prompts-baseline | ai | ai-1 | prompts/ | — | — |
| 1 | api-checkout | backend | be-1 | api/ | — | api-models |
| 1 | frontend-types | frontend | fe-1 | apps/, components/ | api/ (read types) | api-checkout |
| 2 | frontend-checkout | frontend | fe-1 | apps/, components/ | tokens/, prompts/ (read) | frontend-types, design-tokens |
| 3 | ai-prompt-iteration | ai | ai-1 | prompts/, eval/ | apps/ (read for context) | frontend-checkout |
```

Each row's `Lane` is the role's `owns_paths` slice. `Cross-role read` shows what the step pulls from other roles' lanes (read-only). The handoff chain at the bottom is just the `Depends on` column.

### Step 8 — Render change report

```markdown
# Role config update

## Responsibility-area check

- Top-level dirs: 18
- Clear ownership: 16
- Default-to-planner: 2 (README.md, .gitignore)
- AMBIGUOUS (must resolve): 0
- Read-only relationships: 12 (printed in map)

## Responsibility map

```
apps/                  → frontend (write), backend (read), design (read)
api/                   → backend (write), frontend (read)
prompts/               → ai (write), backend (read), frontend (read after build copy)
tools/                 → ai (write), all (read)
PRD.md                 → planner (write), all (read)
```

## Changes

- **ai**: ADDED
  - owns_paths: prompts/**, eval/**, retrieval/**, lib/llm/**, tests/test_prompts.py, tests/test_eval.py
  - shared_read_paths: tools/**
- **frontend**: MODIFIED
  - removed `styles/` from owns_paths (reassigned to design via shared_read_paths)

## Files written

- .dev-kit/role-config.json (5 roles)
- templates/roles-matrix.md (regenerated)
- templates/repo-layout.md (new)
- rules/role-ai.md (new per-role rules file)

## Cross-references with plan data

- phases/<name>/owners.json: 4 entries match new config
- 0 owners reference removed roles
- 0 steps have Ows paths outside new lanes
- 0 co-edit conflicts in shared_write_paths
```

## Validation gates

- `.dev-kit/role-config.json` parses as JSON, has `version: 1`, all 5 built-in roles present (planner mandatory)
- **Responsibility-area check** ran with status counts printed: every top-level dir has clear ownership OR is explicitly default-to-planner
- **No ambiguous ownership** (no top-level dir claimed by 2+ `owns_paths`)
- `templates/roles-matrix.md` regenerated from JSON (no drift)
- `templates/repo-layout.md` exists and matches JSON
- For each role, matching `rules/role-<key>.md` exists
- Cross-reference check ran

## Iron Laws

- **L2** (verification before completion) — regenerate matrix + repo-layout from JSON, verify they match before writing
- **L3** (evidence before claim) — every ambiguity finding cites the directory and which two roles claim it
- **L5** (one answer per question) — one role field at a time when collecting
- **L5-R** (non-overlap) — `owns_paths` MUST be disjoint; `shared_read_paths` is non-exclusive; `shared_write_paths` requires explicit `boundary_notes` + PM sign-off

## Anti-patterns

- ❌ Two roles claiming the same `owns_paths` directory — fix by splitting or reassigning
- ❌ Hardcoding role defaults in `plan` / `plan-update` skills — they MUST read from `.dev-kit/role-config.json`
- ❌ Editing `templates/roles-matrix.md` by hand and forgetting to regenerate the JSON (drift)
- ❌ Adding a role without a corresponding `rules/role-<key>.md`
- ❌ Removing `planner` (mandatory role)
- ❌ Writing to another role's `owns_paths` even "just to fix one line" — open a handoff instead, or escalate to `shared_write_paths` with PM sign-off
- ❌ Using `shared_write_paths` for more than root-level cross-cutting config (e.g., `package.json` with both frontend and backend deps) — anything deeper belongs in one role's lane
- ❌ Marking a role `mandatory: false` retroactively if owners reference it — would orphan steps

## Next step

- New role added → run `/dev-kit-lite:team-roster` to add members to it
- Role `owns_paths` changed → run `/dev-kit-lite:plan-update` to align existing step `Ows:` paths
- Role removed → run `/dev-kit-lite:reassign` to move affected steps to other roles
- Responsibility-area ambiguity detected → recommend a documented split, then re-run `plan`

## Downstream contracts

This skill is the **upstream** of four:

| Skill | Reads from `role` |
|-------|-------------------|
| `plan` | uses `headcount_default`, `owns_paths`, `shared_read_paths`, `branch_prefix`, `repo_layout` when generating steps; consumes the "Suggested plan partition" output |
| `plan-update` | validates that step owner role still exists + step's `Ows:` still falls within the role's `owns_paths` or `shared_write_paths` |
| `team-roster` | uses `headcount_default` to warn when a role has fewer members than recommended |
| `build-tdd` | reads `owns_paths` from the step's role to enforce write boundaries in the worktree |

If `role` is updated, those four skills must be re-invoked to pick up the new defaults.
