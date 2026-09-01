---
name: role
category: plan
description: Manage role taxonomy (planner / frontend / backend / ai / design) with responsibility-area separation. Tech-stack agnostic — every role declares its own owns_paths and tech_stack; no defaults that bake in Next.js / FastAPI / etc. SSOT for plan + plan-update + team-roster + build-tdd.
when_to_use:
  - At the start of every sprint, before plan (pick repo_layout + tech_stack per role)
  - Adding or modifying a role
  - Changing role defaults (headcount, owned directory, branch prefix, allowed tools)
  - Plan/plan-update needs to resolve role → defaults
  - Switching tech stack (Next.js → React Native, FastAPI → Express, etc.)
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:role

## Role

You are the role taxonomy steward AND the **responsibility-area separator** AND the **tech-stack-agnostic gatekeeper**. The 5 roles in this kit (`planner`, `frontend`, `backend`, `ai`, `design`) carry **no built-in assumptions about tech stack**. A frontend role can own a `src/screens/` tree (React Native), a `app/` tree (Next.js App Router), a `lib/components/` tree (Vue), or a custom layout — whatever the team picks.

> **SRP here = "responsibility-area separation" (책임영역 분리)**, NOT "every file has exactly one owner". The principle is about giving each role a **clear, well-bounded responsibility area** that does not bleed into another's. Overlap at well-defined shared zones (build configs, root-level docs, generated artifacts) is allowed and expected — what is **not** allowed is *unclear* responsibility: a directory that two roles both feel they own, with no documented boundary.

> **Tech-stack neutrality**: this skill does NOT default to Next.js / FastAPI / Figma / etc. The default `owns_paths` for every role is **empty**. The team MUST explicitly choose a tech stack (per role) and the paths it implies, or write custom paths. See the [Tech-stack presets](#tech-stack-presets) section for copy-paste templates.

## The two questions that gate every sprint

Before plan generation, the team must answer:

1. **Repo layout**: `monorepo` (one repo, role-owned subtrees) OR `multi-repo` (one repo per role + shared `contracts/` repo)?
2. **Tech stack per role**: for each of `frontend`, `backend`, `ai`, `design`, which tech stack + which paths does that stack imply?

These decisions are recorded in `.dev-kit/role-config.json` as `repo_layout` (top-level) and `roles.<key>.tech_stack` + `roles.<key>.owns_paths` (per-role).

## The responsibility-area model

Each role has:

| Field | Meaning | Example |
|-------|---------|---------|
| `tech_stack` | Free-form label of the chosen stack. NOT used for path inference; just a label for the team. | `"nextjs-app-router"`, `"react-native-cli"`, `"fastapi"`, `"express"`, `"sveltekit"`, `"none"` |
| `owns_paths` | Directories/files this role **writes** exclusively. Other roles read but don't write. | `apps/web/**`, `src/screens/**`, `api/**`, `services/**` |
| `shared_read_paths` | (optional) Paths this role does NOT own but may read. Used for cross-role contracts. | `tools/`, `tokens/`, `api/` (frontend reads for typing) |
| `shared_write_paths` | (optional, rare) Paths co-written by multiple roles with explicit co-edit rules. Used for cross-cutting config that genuinely needs two hands. | root `package.json` for full-stack features |
| `boundary_notes` | Free-text explaining where this role's responsibility ends and another's begins. | "frontend owns UI; backend owns `/api/*` they call. contracts/ is the bridge." |

The hard rule: **`owns_paths` between two roles MUST NOT overlap**. `shared_read_paths` is fine (a role reads what another owns). `shared_write_paths` requires explicit PM sign-off per role pair — print a loud warning.

## Inputs

Four input modes (L5: one answer at a time when in interactive mode):

1. **No-arg query** — list current roles, their defaults, and the responsibility-area map.
2. **Bootstrap sprint** — first-time setup: answer the two gating questions (repo_layout + tech_stack per role), then write the config.
3. **Add role** — provide `{role_key, display_name, headcount_default, tech_stack?, owns_paths, shared_read_paths?, shared_write_paths?, branch_prefix, default_tools, boundary_notes?}`.
4. **Modify role** — provide role_key + the fields to change.

## Built-in roles (degenerate defaults — paths are EMPTY until team picks a stack)

The 5 roles below are **structural**. Each role's `owns_paths` and `default_tools` default to **empty**. The team MUST fill these in (either by picking a tech_stack preset OR by writing custom paths) before plan generation runs.

| role_key | display_name | headcount | owns_paths (DEFAULT = empty) | branch_prefix | tech_stack examples |
|----------|--------------|-----------|------------------------------|---------------|---------------------|
| `planner` | PM / Coordinator | 1+ (mandatory) | `[]` (no defaults; add PRD.md, .dev-kit/**, phases/<name>/** by hand) | — (no feature branches) | `"none"` |
| `frontend` | Frontend | 2+ | `[]` | `feat/web-<owner>-<slug>` (also override per stack) | `"nextjs-app-router"`, `"nextjs-pages"`, `"react-vite"`, `"react-native-cli"`, `"expo"`, `"vue-nuxt"`, `"sveltekit"`, `"astro"`, `"remix"`, custom |
| `backend` | Backend | 2+ | `[]` | `feat/api-<owner>-<slug>` | `"fastapi"`, `"express"`, `"nestjs"`, `"django"`, `"flask"`, `"go-gin"`, `"go-echo"`, `"rust-axum"`, `"spring-boot"`, custom |
| `ai` | AI Engineer | 1+ | `[]` | `feat/ai-<owner>-<slug>` | `"minimax-only"`, `"anthropic-only"`, `"multi-provider"`, `"openai-only"`, custom |
| `design` | Design (Figma MCP) | 1+ | `[]` | `feat/design-<owner>-<slug>` | `"figma-mcp"`, `"sketch-export"`, `"penpot-export"`, custom |

The `planner` role always owns `PRD.md`, `.dev-kit/**`, `phases/<name>/**` regardless of repo layout — those are the kit's own files. (This is the one hardcoded set of paths.)

## Tech-stack presets

The role skill ships with **copy-paste presets** at `templates/tech-stacks/<stack>.json`. The user picks one per role; the skill copies the preset into `roles.<key>.owns_paths` + `roles.<key>.default_tools`. Examples (not exhaustive — user can define their own):

### Frontend presets

| Stack | `owns_paths` | `default_tools` |
|-------|--------------|-----------------|
| `nextjs-app-router` | `app/**`, `components/**`, `lib/client/**`, `public/**`, `next.config.js`, `package.json`, `tsconfig.json` | `npm`, `npm test`, `npm run build`, `npm run lint`, `next` |
| `nextjs-pages` | `pages/**`, `components/**`, `lib/client/**`, `public/**`, `next.config.js`, `package.json`, `tsconfig.json` | `npm`, `npm test`, `npm run build`, `npm run lint`, `next` |
| `react-vite` | `src/**`, `public/**`, `vite.config.ts`, `package.json`, `tsconfig.json` | `npm`, `npm test`, `vite` |
| `react-native-cli` | `src/screens/**`, `src/components/**`, `src/navigation/**`, `ios/**`, `android/**`, `metro.config.js`, `package.json`, `tsconfig.json` | `npm`, `npm test`, `metro`, `react-native` |
| `expo` | `app/**`, `components/**`, `assets/**`, `app.json`, `package.json`, `tsconfig.json` | `npx expo`, `eas`, `npm test` |
| `vue-nuxt` | `pages/**`, `components/**`, `composables/**`, `nuxt.config.ts`, `package.json` | `npm`, `npm test`, `nuxt` |
| `sveltekit` | `src/routes/**`, `src/lib/**`, `static/**`, `svelte.config.js`, `package.json` | `npm`, `npm test`, `vite` |

### Backend presets

| Stack | `owns_paths` | `default_tools` |
|-------|--------------|-----------------|
| `fastapi` | `app/**`, `tests/**`, `alembic/**`, `requirements.txt`, `pyproject.toml`, `Dockerfile` | `pytest`, `mypy`, `ruff`, `uvicorn`, `alembic` |
| `django` | `<project>/**`, `apps/**`, `static/**`, `templates/**`, `manage.py`, `requirements.txt`, `pyproject.toml` | `pytest`, `mypy`, `ruff`, `manage.py` |
| `flask` | `app/**`, `tests/**`, `requirements.txt`, `pyproject.toml` | `pytest`, `mypy`, `ruff`, `flask` |
| `express` | `src/**`, `tests/**`, `package.json`, `tsconfig.json` | `npm test`, `jest`, `eslint` |
| `nestjs` | `src/**`, `test/**`, `package.json`, `nest-cli.json`, `tsconfig.json` | `npm test`, `nest`, `eslint` |
| `go-gin` | `cmd/**`, `internal/**`, `pkg/**`, `go.mod`, `go.sum` | `go test`, `go vet`, `golangci-lint` |
| `spring-boot` | `src/main/java/**`, `src/test/java/**`, `build.gradle*`, `pom.xml` | `gradle`, `mvn`, `junit` |

### AI presets

| Stack | `owns_paths` | `default_tools` |
|-------|--------------|-----------------|
| `minimax-only` | `prompts/**`, `eval/**`, `lib/llm/**`, `tests/test_prompts.py`, `tests/test_eval.py` | `pytest`, `ruff`, `minimax-sdk` |
| `anthropic-only` | `prompts/**`, `eval/**`, `lib/llm/**`, `tests/test_prompts.py`, `tests/test_eval.py` | `pytest`, `ruff`, `anthropic-sdk` |
| `multi-provider` | `prompts/**`, `eval/**`, `providers/**`, `lib/llm/**`, `tests/test_prompts.py`, `tests/test_eval.py`, `tests/test_providers.py` | `pytest`, `ruff`, `minimax-sdk`, `anthropic-sdk`, `openai-sdk` |

### Design presets

| Stack | `owns_paths` | `default_tools` |
|-------|--------------|-----------------|
| `figma-mcp` | `design/**`, `tokens/**`, `figma-export/**`, `screenshots/**` | `mcp__figma__*` tools, JSON validators |
| `penpot-export` | `design/**`, `tokens/**`, `penpot-export/**`, `screenshots/**` | `penpot-cli`, JSON validators |
| `sketch-export` | `design/**`, `tokens/**`, `sketch-export/**`, `screenshots/**` | `sketchtool`, JSON validators |

User can add their own preset at `templates/tech-stacks/<custom-name>.json` and reference it by name.

## Repo layouts

| Layout | When to use |
|--------|-------------|
| `monorepo` (default) | Single repo, role-owned subtrees. PR review sees cross-role changes. Speed > isolation. Requires explicit boundary rules (see above) when same repo. |
| `multi-repo` | One repo per role + shared `contracts/` repo for interfaces. Cross-role change requires multiple PRs + a contracts bump. Mandatory for: different deployment cadences, different security boundaries, or already-existing per-role repos. |

The skill **prompts the user at first invocation** which layout they want. If `multi-repo`, the role skill only writes the *config fragment* for the current repo — the user is responsible for mirroring the same role spec across the other role repos.

## Workflow

### Step 1 — Resolve current role config

Read `.dev-kit/role-config.json` if it exists; otherwise fall back to parsing `templates/roles-matrix.md`. Print the active config so the user sees the source of truth, including `repo_layout` and every role's `tech_stack` (or warn if `tech_stack` is unset).

### Step 2 — Tech-stack + responsibility-area check (the new combined check)

For every role:
- If `tech_stack` is unset and `owns_paths` is empty → **NEEDS_SETUP**, block plan generation
- If `tech_stack` is set but `owns_paths` is empty → **STACK_PICKED_NO_PATHS**, ask user to either apply a preset or write custom paths
- If `owns_paths` is non-empty → **CONFIGURED**, proceed

Then for every top-level directory in the repo:
- Exactly one role's `owns_paths` matches → **clear** ✓
- Zero roles claim it → **default to planner**, flag for review
- 2+ roles claim it via `owns_paths` → **AMBIGUOUS** — must resolve (pick one owner, split, or move to `shared_write_paths`)
- A role's `owns_paths` overlaps another via `shared_read_paths` → **OK**, print the read relationship

Print the responsibility-area map:

```
apps/web/              → frontend (write), backend (read), design (read)
api/                   → backend (write), frontend (read for types)
prompts/               → ai (write), backend (read)
PRD.md                 → planner (write), all (read)
```

### Step 3 — Validate proposed change

For `add` or `modify`:
- `role_key` must match `^[a-z][a-z0-9-]{0,31}$` (kebab-case, ≤ 32 chars)
- `display_name` non-empty
- `headcount_default` is `1+`, `2+`, or a number
- `tech_stack` is a free-form string OR null (null = tech-agnostic role)
- `owns_paths` is an array of glob paths (may be empty during transition); reject if any `owns_paths` glob overlaps another role's `owns_paths` glob (responsibility-area conflict)
- `shared_read_paths` is fine to overlap (reads are non-exclusive)
- `shared_write_paths` requires an explicit `boundary_notes` justification — print a loud warning
- `branch_prefix` is `feat/<scope>-<owner>-<slug>` form OR empty (for `planner`)
- `default_tools` is an array of tool names
- For `modify`: changing `owns_paths` is a hard warning if plan data references the role (steps may now fall outside the lane)

For `planner`: cannot be deleted (mandatory). Cannot have `tech_stack` (always `"none"`).

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
      "tech_stack": "none",
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
      "tech_stack": "nextjs-app-router",
      "owns_paths": ["app/**", "components/**", "lib/client/**", "public/**", "next.config.js", "package.json", "tsconfig.json"],
      "shared_read_paths": ["api/**", "tokens/**", "tools/**"],
      "shared_write_paths": [],
      "branch_prefix": "feat/web-<owner>-<slug>",
      "default_tools": ["npm", "npm test", "npm run build", "npm run lint"],
      "boundary_notes": "Owns the UI surface. Reads API contracts (typed) and design tokens.",
      "rules_file": "rules/role-frontend.md"
    },
    "backend": {
      "display_name": "Backend",
      "mandatory": false,
      "headcount_default": 2,
      "tech_stack": "fastapi",
      "owns_paths": ["app/**", "tests/**", "alembic/**", "requirements.txt", "pyproject.toml"],
      "shared_read_paths": ["prompts/**", "tools/**"],
      "shared_write_paths": [],
      "branch_prefix": "feat/api-<owner>-<slug>",
      "default_tools": ["pytest", "mypy", "ruff", "uvicorn", "alembic"],
      "boundary_notes": "Owns the API + persistence. Reads prompt catalog from ai role.",
      "rules_file": "rules/role-backend.md"
    },
    "ai": {
      "display_name": "AI Engineer",
      "mandatory": false,
      "headcount_default": 1,
      "tech_stack": "minimax-only",
      "owns_paths": ["prompts/**", "eval/**", "lib/llm/**", "tests/test_prompts.py", "tests/test_eval.py"],
      "shared_read_paths": ["tools/**"],
      "shared_write_paths": [],
      "branch_prefix": "feat/ai-<owner>-<slug>",
      "default_tools": ["pytest", "ruff", "minimax-sdk"],
      "boundary_notes": "Owns prompt catalog and eval harness. Other roles consume prompts as imports.",
      "rules_file": "rules/role-ai.md"
    },
    "design": {
      "display_name": "Design (Figma MCP)",
      "mandatory": false,
      "headcount_default": 1,
      "tech_stack": "figma-mcp",
      "owns_paths": ["design/**", "tokens/**", "figma-export/**", "screenshots/**"],
      "shared_read_paths": ["components/**"],
      "shared_write_paths": [],
      "branch_prefix": "feat/design-<owner>-<slug>",
      "default_tools": ["mcp__figma__*", "JSON validators"],
      "boundary_notes": "Owns design tokens and exports. Frontend reads tokens.",
      "rules_file": "rules/role-figma-mcp.md"
    }
  }
}
```

**`templates/roles-matrix.md`** (human-readable, regenerated from JSON — shows `tech_stack` column prominently so the team can see at a glance what each role owns).

**`templates/repo-layout.md`** (NEW, human-readable directory map showing which role owns each top-level dir, with tech_stack label and read/write indicators).

### Step 5 — Generate per-role rules file

For any role that doesn't have a matching `rules/role-<key>.md`, write one using the JSON config (display_name, tech_stack, owns_paths, shared_read_paths, branch_prefix, default_tools, boundary_notes). The per-role rules file MUST mention the tech_stack at the top so the agent in that worktree knows what tooling to expect.

### Step 6 — Cross-reference with plan data (read-only check)

If `phases/<name>/owners.json` exists:
- For each step's owner, verify their role still exists in the new config
- If a role was removed and owners reference it, warn loudly
- If `owns_paths` was modified, list steps whose `Ows:` paths fall outside the new lane
- If two steps at the same dependency layer now share a `shared_write_paths` dir, that's a **co-edit conflict** — flag it

### Step 7 — Emit tech-stack-aware plan design hints

Print a "Suggested plan partition" block the `plan` skill consumes. Each step lives in **one role's `owns_paths`** directory. Cross-role coordination happens via the handoff chain or `shared_read_paths`, never via shared `owns_paths`:

```markdown
## Suggested plan partition (from tech_stack × responsibility-area map)

| Layer | Step | Role | Owner id | Tech stack | Lane (dir) | Cross-role read | Depends on |
|-------|------|------|----------|------------|------------|-----------------|-----------|
| 0 | design-tokens | design | design-1 | figma-mcp | design/, tokens/ | — | — |
| 0 | api-models | backend | be-1 | fastapi | app/, alembic/ | — | — |
| 0 | prompts-baseline | ai | ai-1 | minimax-only | prompts/ | — | — |
| 1 | api-checkout | backend | be-1 | fastapi | app/ | — | api-models |
| 1 | frontend-types | frontend | fe-1 | nextjs-app-router | app/, lib/client/ | api/ (read types) | api-checkout |
| 2 | frontend-checkout | frontend | fe-1 | nextjs-app-router | app/, components/ | tokens/, prompts/ (read) | frontend-types, design-tokens |
| 3 | ai-prompt-iteration | ai | ai-1 | minimax-only | prompts/, eval/ | app/ (read for context) | frontend-checkout |
```

Each row's `Lane` is the role's `owns_paths` slice (driven by `tech_stack`). `Cross-role read` shows what the step pulls from other roles' lanes (read-only).

### Step 8 — Render change report

```markdown
# Role config update

## Tech-stack choices

| Role | Tech stack | Status |
|------|-----------|--------|
| planner | none | CONFIGURED (no paths needed) |
| frontend | nextjs-app-router | CONFIGURED |
| backend | fastapi | CONFIGURED |
| ai | minimax-only | CONFIGURED |
| design | figma-mcp | CONFIGURED |

## Responsibility-area check

- Top-level dirs: 18
- Clear ownership: 16
- Default-to-planner: 2 (README.md, .gitignore)
- AMBIGUOUS (must resolve): 0
- Read-only relationships: 12

## Responsibility map

```
app/                   → frontend (write) + backend (write) — AMBIGUOUS — must resolve
api/                   → backend (write), frontend (read)
prompts/               → ai (write), backend (read)
PRD.md                 → planner (write), all (read)
```

## Changes

- **frontend**: MODIFIED
  - tech_stack: react-vite → nextjs-app-router
  - owns_paths: updated to Next.js App Router layout
- **ai**: ADDED
  - tech_stack: minimax-only
  - owns_paths: prompts/**, eval/**, lib/llm/**, tests/test_prompts.py, tests/test_eval.py

## Files written

- .dev-kit/role-config.json (5 roles, repo_layout=monorepo)
- templates/roles-matrix.md (regenerated, shows tech_stack column)
- templates/repo-layout.md (new)
- rules/role-frontend.md, rules/role-ai.md (regenerated to mention tech_stack)

## Cross-references with plan data

- phases/<name>/owners.json: 4 entries match new config
- 0 owners reference removed roles
- 0 steps have Ows paths outside new lanes
```

## Validation gates

- `.dev-kit/role-config.json` parses as JSON, has `version: 1`, `repo_layout` set
- All 5 built-in roles present (planner mandatory)
- Every role has either: `tech_stack` set + `owns_paths` non-empty, OR `tech_stack: "none"` (planner only)
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
- ❌ **Defaulting `owns_paths` to a tech-stack-specific path** (e.g., `apps/web/**` without user picking the stack) — the defaults must be empty until the team chooses
- ❌ Editing `templates/roles-matrix.md` by hand and forgetting to regenerate the JSON (drift)
- ❌ Adding a role without a corresponding `rules/role-<key>.md`
- ❌ Removing `planner` (mandatory role)
- ❌ Writing to another role's `owns_paths` even "just to fix one line" — open a handoff instead, or escalate to `shared_write_paths` with PM sign-off
- ❌ Using `shared_write_paths` for more than root-level cross-cutting config — anything deeper belongs in one role's lane
- ❌ Marking a role `mandatory: false` retroactively if owners reference it — would orphan steps
- ❌ Picking a tech stack in `multi-repo` mode and forgetting to mirror the role spec across the other role repos — every repo needs the same `role-config.json` fragment

## Next step

- New role added → run `/dev-kit-lite:team-roster` to add members to it
- Role `owns_paths` changed → run `/dev-kit-lite:plan-update` to align existing step `Ows:` paths
- Role removed → run `/dev-kit-lite:reassign` to move affected steps to other roles
- Tech stack changed (e.g., frontend switches from React to Vue) → re-run `role`, then `plan-update` to migrate `owns_paths`, then `team-roster` if branch prefixes change
- Responsibility-area ambiguity detected → recommend a documented split, then re-run `plan`

## Downstream contracts

This skill is the **upstream** of four:

| Skill | Reads from `role` |
|-------|-------------------|
| `plan` | uses `headcount_default`, `tech_stack`, `owns_paths`, `shared_read_paths`, `branch_prefix`, `repo_layout` when generating steps; consumes the "Suggested plan partition" output |
| `plan-update` | validates that step owner role still exists + step's `Ows:` still falls within the role's `owns_paths` or `shared_write_paths` |
| `team-roster` | uses `headcount_default` to warn when a role has fewer members than recommended |
| `build-tdd` | reads `owns_paths` from the step's role to enforce write boundaries in the worktree; reads `tech_stack` to know which test/lint commands to run |

If `role` is updated, those four skills must be re-invoked to pick up the new defaults.
