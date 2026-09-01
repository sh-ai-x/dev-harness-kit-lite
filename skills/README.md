# Skills — dev-kit-lite

13 skills for 4-hour MVP/POC team sprints.

| Skill | Stage | Purpose |
|-------|-------|---------|
| `/dev-kit-lite:idea-eval` | 0 | Score an idea on 8 axes (100 pts) — pre-sprint gate before `plan` |
| `/dev-kit-lite:bootstrap` | 1 | Scaffold CLAUDE.md + AGENTS.md + .active-hooks.json + first commit (greenfield) |
| `/dev-kit-lite:role` | 1.3 | Manage role taxonomy (planner/frontend/backend/ai/design) with responsibility-area separation + tech-stack-agnostic presets |
| `/dev-kit-lite:migrate` | 1.4 | Adopt dev-kit-lite into an EXISTING project. Layout-agnostic — same skill for one repo, workspace, or multi-repo. |
| `/dev-kit-lite:team-roster` | 1.5 | Define team roster (role + identifier + name) and split steps by dependency graph |
| `/dev-kit-lite:role-plan` | 1.6 | Generate per-role plan docs from the project plan. Each role gets a focused doc with only their assigned steps. |
| `/dev-kit-lite:plan` | 2 | Write PRD.md + phases/<name>/ + owners.json (initial assignment) |
| `/dev-kit-lite:plan-update` | 2b | PM-only mid-sprint PRD/phases mutation |
| `/dev-kit-lite:ci-setup` | 3 | Install ONE file: .github/workflows/review.yml (advisory-only) |
| `/dev-kit-lite:role-tdd` | 4a | Role-scoped TDD — Red-Green-Refactor on ONLY the calling role-owner's assigned steps |
| `/dev-kit-lite:build-tdd` | 4b | Full Red-Green-Refactor cycle + L5-R non-overlap pre-flight (PM/orchestrator variant) |
| `/dev-kit-lite:review` | 5 | 1-dim correctness review (no security fan-out) |
| `/dev-kit-lite:build-verify` | 6 | L3 evidence gate + role-contract snapshot + releases ownership locks |
| `/dev-kit-lite:reassign` | (cross) | PM-only mid-sprint ownership transfer |

Each skill is one `SKILL.md` file under `skills/<name>/`.

`role-tdd` is the role-owner variant of `build-tdd` — same discipline, but auto-scoped to one identifier. Use `role-tdd` if you're a frontend/backend/ai/design owner running your own slice. Use `build-tdd` if you're the PM/orchestrator coordinating across roles.
