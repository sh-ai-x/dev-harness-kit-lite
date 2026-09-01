# Skills — dev-harness-kit-lite

9 skills for 4-hour MVP/POC team sprints.

| Skill | Stage | Purpose |
|-------|-------|---------|
| `/dev-kit-lite:idea-eval` | 0 | Score an idea on 8 axes (100 pts) — pre-sprint gate before `plan` |
| `/dev-kit-lite:bootstrap` | 1 | Scaffold CLAUDE.md + AGENTS.md + .active-hooks.json + first commit |
| `/dev-kit-lite:team-roster` | 1.5 | Define team roster (role + identifier + name) and split steps by dependency graph. Coverage check so no one is left out. |
| `/dev-kit-lite:plan` | 2 | Write PRD.md + phases/<name>/ + owners.json (initial assignment) |
| `/dev-kit-lite:plan-update` | 2b | PM-only mid-sprint PRD/phases mutation |
| `/dev-kit-lite:ci-setup` | 3 | Install ONE file: .github/workflows/review.yml (advisory-only) |
| `/dev-kit-lite:build-tdd` | 4 | Red-Green-Refactor cycle + L5-R non-overlap pre-flight |
| `/dev-kit-lite:build-verify` | 6 | L3 evidence gate + role-contract snapshot + releases ownership locks |
| `/dev-kit-lite:review` | 5 | 1-dim correctness review (no security fan-out) |
| `/dev-kit-lite:reassign` | (cross) | PM-only mid-sprint ownership transfer |

Each skill is one `SKILL.md` file under `skills/<name>/`.
