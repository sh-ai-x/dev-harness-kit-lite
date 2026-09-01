# Changelog

## v0.1.3 (2026-09-01)

Adds `role` skill (Stage 1.3) — manages the role taxonomy (`planner`, `frontend`, `backend`, `ai`, `design`) with SRP-aware directory separation. Each role owns a **disjoint** set of directories; cross-role touching is a design defect, not a normal state. Writes both `.dev-kit/role-config.json` (machine-readable, consumed by plan/plan-update/team-roster/build-tdd) and `templates/roles-matrix.md` + `templates/repo-layout.md` (human-readable). Generates per-role rules files at `rules/role-<key>.md`. Refuses success while any file in the repo is claimed by > 1 role.

Supports `monorepo` (default, single repo with role-owned subtrees) and `multi-repo` (one repo per role + shared `contracts/` repo) layouts. `multi-repo` is recommended only for projects that already have one repo per role.

Upstream of `plan`, `plan-update`, `team-roster`, and `build-tdd` — those four must be re-invoked after any `role` change.

## v0.1.2 (2026-09-01)

Adds `team-roster` skill (Stage 1.5) — pre-plan gate that defines the team roster (`{role, identifier, name}` per member, multiple per role allowed) and acceptance-checks coverage. Accepts a dependency graph and splits steps along dependency layers (DAG; cycle = hard error), then assigns owners per layer with critical-path priority. Syncs `phases/<name>/owners.json` with `identifier` field and updates each `step<N>.md` `## Role` section with `Depends on:` and `Layer:`. Refuses to return success while any roster member has zero step assignments.

Roles supported: `planner` (PM), `frontend`, `backend`, `ai`, `design`. AI is a first-class role in this skill.

## v0.1.1 (2026-09-01)

Adds `idea-eval` skill (Stage 0) — pre-sprint gate that scores an MVP/hackathon idea on 8 axes (100 pts) and returns S/A/B/C/D grade with the single biggest risk + 1-minute demo tip. Cold-realism judge role, evidence-before-claim scoring reasons, artifact written to `.dev-kit/idea-eval/<slug>.md`.


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
