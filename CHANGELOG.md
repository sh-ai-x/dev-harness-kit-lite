# Changelog

## v0.1.3 (2026-09-01)

Adds `role` skill (Stage 1.3) — manages the role taxonomy (`planner`, `frontend`, `backend`, `ai`, `design`) with **responsibility-area separation** (SRP here means "clear lane boundaries", not "every file has exactly one owner"). The check is: for every top-level directory, does the configuration unambiguously say which role owns it? Two roles claiming the same `owns_paths` is ambiguous — must be resolved (pick one owner, split the directory, or move to `shared_write_paths` with PM sign-off). Cross-role reads via `shared_read_paths` are allowed and expected.

**Tech-stack agnostic**: every role declares its own `tech_stack` + `owns_paths`; the skill ships no baked-in defaults like `apps/web/**` or `next.config.js`. Users pick from built-in presets (`nextjs-app-router`, `react-vite`, `react-native-cli`, `expo`, `vue-nuxt`, `sveltekit`, `fastapi`, `django`, `flask`, `express`, `nestjs`, `go-gin`, `spring-boot`, `minimax-only`, `anthropic-only`, `multi-provider`, `figma-mcp`, `penpot-export`, `sketch-export`) or write custom ones at `templates/tech-stacks/<name>.json`. Empty `owns_paths` blocks plan generation until the team picks a stack.

**Repo-layout gating**: the skill asks upfront whether this is `monorepo` (default, single repo with role-owned subtrees) or `multi-repo` (one repo per role + shared `contracts/` repo). For `multi-repo`, the user is responsible for mirroring the role spec across every role repo.

Writes both `.dev-kit/role-config.json` (machine-readable, consumed by plan/plan-update/team-roster/build-tdd) and `templates/roles-matrix.md` + `templates/repo-layout.md` (human-readable, both include the `tech_stack` column). Generates per-role rules files at `rules/role-<key>.md` that open with the tech_stack label.

Upstream of `plan`, `plan-update`, `team-roster`, and `build-tdd` — those four must be re-invoked after any `role` change.

## v0.1.2 (2026-09-01)

Adds `team-roster` skill (Stage 1.5) — pre-plan gate that defines the team roster (`{role, identifier, name}` per member, multiple per role allowed) and acceptance-checks coverage. Accepts a dependency graph and splits steps along dependency layers (DAG; cycle = hard error), then assigns owners per layer with critical-path priority. Syncs `phases/<name>/owners.json` with `identifier` field and updates each `step<N>.md` `## Role` section with `Depends on:` and `Layer:`. Refuses to return success while any roster member has zero step assignments.

Roles supported: `planner` (PM), `frontend`, `backend`, `ai`, `design`. AI is a first-class role in this skill.

## v0.1.1 (2026-09-01)

Adds `idea-eval` skill (Stage 0) — pre-sprint gate that scores an MVP/hackathon idea on 8 axes (100 pts) and returns S/A/B/C/D grade with the single biggest risk + 1-minute demo tip. Cold-realism judge role, evidence-before-claim scoring reasons, artifact written to `.dev-kit/idea-eval/<slug>.md`.

Also switches CI review provider from Anthropic to MiniMax (`MINIMAX_API_KEY` via `api.minimax.io/anthropic`), drops the SessionStart `session-start-check.sh` hook (worktree-guard is the hard-block layer; the gentle reminder added noise without value). Adds `id-token: write` to `review.yml` permissions.

## v0.1.0 (2026-09-01)

Initial release. 7 skills (bootstrap, plan, ci-setup, build-tdd, build-verify, review, reassign), 7 hooks, 6 stages. Designed for 4-hour greenfield MVP/POC team sprints.

### Iron Laws (5 + 1)
- L1: No prod code without a failing test
- L2: No Edit/Write on main checkout
- L3: No "done" without quoted exit code + test count
- L4: No TODO / FIXME in committed code
- L5: One answer per question
- L5-R (NEW): One person = at most ONE in-flight step; one directory = at most ONE active owner

### Highlights
- Per-step `## Role` section mandatory in `phases/<name>/step<N>.md`
- `phases/<name>/owners.json` registry — machine-checkable non-overlap contract
- PM/coordinator role (NEW, mandatory)
- Advisory-only `review.yml` (no required CI checks, merge works on red)
- 6-person team template (1 PM + 2 FE + 2 BE + 1 Design)
