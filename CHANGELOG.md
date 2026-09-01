# Changelog

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
