# Changelog

## v0.1.7 (2026-09-05)

Ports the worktree-prune workflow from dev-harness-kit so operators can
manage the `.worktrees/` queue without leaving the kit:

- **`bin/worktree-prune.sh`** — interactive oldest-first removal with
  `--yes`, `--dry-run`, `--keep N`. Drives `lib/worktree_prune.py` for
  porcelain parsing + age sort, then dispatches each path to
  `bin/worktree-remove-safe.sh`. Pruned: drops the janitor-agent
  cross-link and the per-worktree log archive (lite has no telemetry
  retention requirement).
- **`bin/worktree-remove-safe.sh`** — refuses to remove the main
  checkout, verifies the path is a registered worktree, prompts for
  confirmation unless `--yes` is passed, then forwards to
  `git worktree remove`.
- **`lib/worktree_prune.py`** — `collect(repo) -> list[Row]` (oldest
  first) + `render_table(rows, now, head)` + CLI (`--table`,
  `--count`, `--head`). 130 LOC; upstream was 197.
- **Slash commands** — `.claude/commands/worktree-prune.md` (Claude
  Code) + `.codex/commands/worktree-prune.md` (Codex). Both forward
  to `bin/worktree-prune.sh` with `$ARGUMENTS`.
- **`tests/test_worktree_prune.py`** — 18 hermetic tests covering
  `Row.age_days`, `_porcelain_blocks`, `render_table`, `collect` (main
  exclusion + detached exclusion + oldest-first), and the CLI modes
  (`--table`, `--count`, `--head`).

Pair with `rules/git-workflow.md` (already on origin/main) which
declares `.worktrees/` the canonical root and forbids new work there
from the main checkout.

## v0.1.6 (2026-09-02)

**Breaking (install path):** the kit's operational hook scripts now install to
`.dev-kit/hooks/` in adopting projects instead of project-root `hooks/`, which
collides with the React/Next.js/Vue convention for custom hooks
(`hooks/useAuth.ts`) — and with the kit's own `role-frontend` rule that assigns
`hooks/` to the frontend role. Project-root `hooks/` is now never written to by
the kit. Updated: `bin/install.sh`, `skills/bootstrap` Step 1 verify,
`skills/migrate` Step 6 coexistence table + Phase 3–5 install paths,
`rules/git-workflow.md`, `rules/role-frontend.md`, `rules/role-backend.md`.
The installer also rewrites `${CLAUDE_PLUGIN_ROOT}/hooks/` → `${CLAUDE_PLUGIN_ROOT}/.dev-kit/hooks/`
in the copied `.claude/settings.json`, `.codex/settings.json`, and `hooks.json`.

The kit repo's own `hooks/hooks.json` + `hooks/*.sh` layout is unchanged (plugin
auto-load convention).

**Migration** for projects already bootstrapped/migrated:

```bash
mkdir -p .dev-kit/hooks && git mv hooks/* .dev-kit/hooks/ && rmdir hooks
sed -i '' 's#/hooks/#/.dev-kit/hooks/#g' .claude/settings.json .codex/settings.json .dev-kit/hooks/hooks.json
```

`.dev-kit/.active-hooks.json` needs no change — it lists bare script names.

## v0.1.5 (2026-09-01)

Adds two role-scoped skills for daily-driver work:

**`role-plan` (Stage 1.6)** — slices the project plan into one focused doc per role. Reads `.dev-kit/role-config.json`, `.dev-kit/team-roster.json`, `PRD.md`, `phases/<name>/index.json`, and `phases/<name>/owners.json`; emits `phases/<name>/role-plans/<role-key>.md` for each role. Each file lists ONLY that role's assigned steps (filtered by owner identifier), their dependency edges, the cross-role read paths they're allowed to consume, and the per-step branch/worktree/TDD entry points. The `planner.md` file is special — it's the PM's overview with the cross-role handoff chain. Idempotent: re-runnable after `plan-update` or `team-roster` changes.

**`role-tdd` (Stage 4a)** — TDD workflow scoped to one role-owner identifier. The role-owner runs this in their own worktree; the skill filters `phases/<name>/index.json` to only their steps and drives Red-Green-Refactor in dependency order. Same Iron Laws as `build-tdd` (L1/L2/L3/L4/L5/L5-R), but the pre-flight explicitly refuses to start a step whose cross-role dependency isn't merged yet (no silent reaching across roles). Writes status updates to both `phases/<name>/index.json` and the role-plan.

Together these give each role-owner a one-file daily-driver view of their work, plus a scoped TDD command they can run without PM involvement. Replaces the "PM writes one plan, role-owners grep for their step" pattern.

## v0.1.4 (2026-09-01)

Adds `migrate` skill (Stage 1.4) — adopts dev-kit-lite into an **existing** project with minimal disruption. **Layout-agnostic by design**: the same skill works whether the project lives in one repo, a workspace (pnpm/nx/turbo/lerna), or several repos with a shared contracts/ location. The skill detects the setup automatically (records it as `migrated_from.setup_kind` — purely informational) and never asks the user to declare monorepo-vs-multi-repo.

Detection covers: repo structure, existing tooling (Nx/Turborepo/Lerna/pnpm workspaces), tech-stack inference per directory via file signatures (next.config.* → Next.js, pyproject.toml → Python, etc.), and existing ownership via CODEOWNERS + git-history contributor counts.

Generates a portable `role-config.json` adapted to whatever the team already has, a coexistence report (which kit files would overlap existing ones), and a 5-phase migration plan (inventory → team review → L5-R hooks opt-in → L1/L3 hooks → full adoption). Three aggressiveness modes (`conservative` / `balanced` / `aggressive`) let the team pick how much to install on day one.

Phase-gated so the team never gets overwritten on day one. For multi-repo, writes per-repo configs and prints a mirror-this-anywhere reminder.

## v0.1.3 (2026-09-01)

Adds `role` skill (Stage 1.3) — manages the role taxonomy with **responsibility-area separation** (SRP here means "clear lane boundaries", not "every file has exactly one owner") and is fully **tech-stack agnostic** (no baked-in Next.js / FastAPI defaults). Roles: planner, frontend, backend, ai, design.

## v0.1.2 (2026-09-01)

Adds `team-roster` skill (Stage 1.5) — defines the team roster with `{role, identifier, name}` per member. Accepts a dependency graph and splits steps along dependency layers (DAG; cycle = hard error). Coverage check blocks success while any member is unassigned.

## v0.1.1 (2026-09-01)

Adds `idea-eval` skill (Stage 0) — scores an MVP/hackathon idea on 8 axes (100 pts). CI: switches to MiniMax via `api.minimax.io/anthropic`. Hooks: drops `session-start-check.sh`. Adds `id-token: write` to `review.yml`.

## v0.1.0 (2026-09-01)

Initial release. 7 skills (bootstrap, plan, ci-setup, build-tdd, build-verify, review, reassign), 7 hooks, 6 stages.
