# Changelog

## v0.1.4 (2026-09-01)

Adds `migrate` skill (Stage 1.4) — adopts dev-kit-lite into an **existing** project with minimal disruption. **Layout-agnostic by design**: the same skill works whether the project lives in one repo, a workspace (pnpm/nx/turbo/lerna), or several repos with a shared contracts/ location. The skill detects the setup automatically (records it as `migrated_from.setup_kind` — purely informational) and never asks the user to declare monorepo-vs-multi-repo.

Detection covers: repo structure, existing tooling (Nx/Turborepo/Lerna/pnpm workspaces), tech-stack inference per directory via file signatures (next.config.* → Next.js, pyproject.toml → Python, etc.), and existing ownership via CODEOWNERS + git-history contributor counts.

Generates a portable `role-config.json` adapted to whatever the team already has, a coexistence report (which kit files would overlap existing ones), and a 5-phase migration plan (inventory → team review → L5-R hooks opt-in → L1/L3 hooks → full adoption). Three aggressiveness modes (`conservative` / `balanced` / `aggressive`) let the team pick how much to install on day one.

Phase-gated so the team never gets overwritten on day one. For multi-repo, writes per-repo configs and prints a mirror-this-anywhere reminder.

## v0.1.3 (2026-09-01)

Adds `role` skill (Stage 1.3) — manages the role taxonomy (`planner`, `frontend`, `backend`, `ai`, `design`) with **responsibility-area separation** (SRP here means "clear lane boundaries", not "every file has exactly one owner"). The check is: for every top-level directory, does the configuration unambiguously say which role owns it? Two roles claiming the same `owns_paths` is ambiguous — must be resolved (pick one owner, split the directory, or move to `shared_write_paths` with PM sign-off). Cross-role reads via `shared_read_paths` are allowed and expected.

**Tech-stack agnostic**: every role declares its own `tech_stack` + `owns_paths`; the skill ships no baked-in defaults like `apps/web/**` or `next.config.js`. Users pick from built-in presets (`nextjs-app-router`, `react-vite`, `react-native-cli`, `expo`, `vue-nuxt`, `sveltekit`, `fastapi`, `django`, `flask`, `express`, `nestjs`, `go-gin`, `spring-boot`, `minimax-only`, `anthropic-only`, `multi-provider`, `figma-mcp`, `penpot-export`, `sketch-export`) or write custom ones at `templates/tech-stacks/<name>.json`. Empty `owns_paths` blocks plan generation until the team picks a stack.

Upstream of `plan`, `plan-update`, `team-roster`, `build-tdd`, and `migrate` — those five must be re-invoked after any `role` change.

## v0.1.2 (2026-09-01)

Adds `team-roster` skill (Stage 1.5) — pre-plan gate that defines the team roster (`{role, identifier, name}` per member, multiple per role allowed) and acceptance-checks coverage. Accepts a dependency graph and splits steps along dependency layers (DAG; cycle = hard error), then assigns owners per layer with critical-path priority. Syncs `phases/<name>/owners.json` with `identifier` field and updates each `step<N>.md` `## Role` section with `Depends on:` and `Layer:`. Refuses to return success while any roster member has zero step assignments.

Roles supported: `planner` (PM), `frontend`, `backend`, `ai`, `design`. AI is a first-class role in this skill.

## v0.1.1 (2026-09-01)

Adds `idea-eval` skill (Stage 0) — pre-sprint gate that scores an MVP/hackathon idea on 8 axes (100 pts) and returns S/A/B/C/D grade with the single biggest risk + 1-minute demo tip. Cold-realism judge role, evidence-before-claim scoring reasons, artifact written to `.dev-kit/idea-eval/<slug>.md`.

Also switches CI review provider from Anthropic to MiniMax (`MINIMAX_API_KEY` via `api.minimax.io/anthropic`), drops the SessionStart `session-start-check.sh` hook (worktree-guard is the hard-block layer; the gentle reminder added noise without value). Adds `id-token: write` to `review.yml` permissions.

## v0.1.0 (2026-09-01)

Initial release. 7 skills (bootstrap, plan, ci-setup, build-tdd, build-verify, review, reassign), 7 hooks, 6 stages. Designed for 4-hour greenfield MVP/POC team sprints.
