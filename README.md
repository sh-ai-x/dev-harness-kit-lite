# dev-harness-kit-lite

A 4-hour MVP/POC team-collab plugin — pruned from the full `dev-harness-kit`.

## What it is

11 skills · 6 hooks · 8 stages · ~45 files. Optimized for **4-hour team sprints** where a small team (1 PM + 2 FE + 2 BE + 1 Design + 1 AI) ships in one focused session.

## Skills (11)

| Skill | Stage | Purpose |
|-------|-------|---------|
| `/dev-kit-lite:idea-eval` | 0 | Score an idea on 8 axes (100 pts) — pre-sprint gate before `plan` |
| `/dev-kit-lite:bootstrap` | 1 | Scaffold CLAUDE.md + AGENTS.md + .active-hooks.json + first commit (greenfield) |
| `/dev-kit-lite:role` | 1.3 | Manage role taxonomy (planner/frontend/backend/ai/design) with responsibility-area separation + tech-stack-agnostic presets |
| `/dev-kit-lite:migrate` | 1.4 | Adopt dev-kit-lite into an EXISTING project. Layout-agnostic — same skill for one repo, workspace, or multi-repo. |
| `/dev-kit-lite:team-roster` | 1.5 | Define team roster (role + identifier + name) and split steps by dependency graph |
| `/dev-kit-lite:plan` | 2 | Write PRD.md + phases/<name>/ + owners.json (initial assignment) |
| `/dev-kit-lite:plan-update` | 2b | PM-only mid-sprint PRD/phases mutation |
| `/dev-kit-lite:ci-setup` | 3 | Install ONE file: .github/workflows/review.yml (advisory-only) |
| `/dev-kit-lite:build-tdd` | 4 | Red-Green-Refactor cycle + L5-R non-overlap pre-flight |
| `/dev-kit-lite:review` | 5 | 1-dim correctness review (no security fan-out) |
| `/dev-kit-lite:build-verify` | 6 | L3 evidence gate + role-contract snapshot + releases ownership locks |
| `/dev-kit-lite:reassign` | (cross) | PM-only mid-sprint ownership transfer |

## What it is NOT

- ❌ Not for multi-week, multi-session work (use the full kit)
- ❌ Not a security review tool (excluded by design — speed > gating)
- ❌ Not an auto-merge / babysit loop (team merges manually)

> ✅ **For existing-project retrofitting** use `/dev-kit-lite:migrate` instead of starting from scratch. Layout-agnostic — works for one repo, a workspace (pnpm/nx/turbo/lerna), or several repos with a shared contracts/ location.

## Quick start

### Greenfield (new repo)

```bash
# 1. Install into a fresh repo (refuses if package.json/requirements.txt exists)
cd /path/to/new-project
git init
bash /path/to/dev-harness-kit-lite/bin/install.sh .

# 2. Cut a worktree for the PM's planning session
git worktree add -b plan/mvp-v0 .worktrees/pm-mvp origin/main
cd .worktrees/pm-mvp

# 3. Run the 8-stage loop
/dev-kit-lite:idea-eval "<your 1-line idea>"           # optional: pre-sprint gate
/dev-kit-lite:role                                    # set tech_stack + owns_paths
/dev-kit-lite:team-roster "[members + dependency graph]" # define team + step assignment
/dev-kit-lite:plan "<your 1-line MVP goal>"
/dev-kit-lite:ci-setup                                # opt-in: installs ONE advisory review.yml
/dev-kit-lite:build-tdd                               # per-step, in each role-owner's worktree
/dev-kit-lite:review                                  # per-step correctness check
/dev-kit-lite:build-verify                            # L3 evidence gate before "done"
```

### Existing project

```bash
cd /path/to/existing-project
/dev-kit-lite:migrate                  # auto-detects layout/tooling/ownership
                                       # produces role-config.json + 5-phase plan
                                       # (conservative mode touches nothing else)
```

## The 8-stage loop

```
   ┌─────────┐  ┌──────────┐  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌──────┐  ┌──────────┐  ┌──────────┐
   │idea-eval├──►│bootstrap ├───►│ role ├───►│ team-rost├───►│   plan  ├───►│ci-setup ├───►│build-tdd ├───►│build-verify│
   └─────────┘  └──────────┘  └──────┘  └─────────┘  └──────────┘  └──────┘  └──────────┘  └──────────┘
                                                          │                              ▲
                                                          ▼                              │
                                                       PRD.md                        verdict
                                                       phases/                     Approve |
                                                       owners.json                Changes |
                                                                                   Blocked
```

For existing projects, swap `bootstrap` for `migrate`. For mid-sprint changes, use `plan-update` (PM-only) or `reassign` (PM-only ownership transfer).

## Role model (L5-R non-overlap)

Each phase step has exactly **one Owner** (by identifier, not name) and a list of **Owns:** paths. The `phases/<name>/owners.json` registry is the machine-checkable contract — `build-tdd` refuses to start a step if its Owner or paths conflict with an in-flight step.

The 5 roles are **structural**; `owns_paths` defaults to **empty** until the team picks a tech stack via the `/dev-kit-lite:role` skill (which ships with built-in presets for Next.js / React Native / Expo / Vue Nuxt / SvelteKit / FastAPI / Django / Express / NestJS / Go Gin / Spring Boot / MiniMax / Anthropic / multi-provider / Figma / Penpot / Sketch — or define your own at `templates/tech-stacks/<name>.json`).

| Role | Default headcount | Tech-stack examples |
|------|-------------------|---------------------|
| PM / Coordinator | 1 (mandatory) | none |
| Frontend | 2 | `nextjs-app-router`, `react-vite`, `react-native-cli`, `expo`, `vue-nuxt`, `sveltekit` |
| Backend | 2 | `fastapi`, `django`, `flask`, `express`, `nestjs`, `go-gin`, `spring-boot` |
| AI Engineer | 1 | `minimax-only`, `anthropic-only`, `multi-provider` |
| Design (Figma MCP) | 1 | `figma-mcp`, `penpot-export`, `sketch-export` |

## When to use vs the full kit

| Use **lite** when | Use **full** when |
|---------------------|---------------------|
| 4-hour sprint with 4-7 people | Multi-week / multi-session |
| Manual merges + local gates | GH-Actions gating + remote babysit |
| Greenfield OR existing project (via `migrate`) | Multi-agent autonomous work |
| Speed > rigor | Rigor > speed |

## See also

- `skills/README.md` — full skill list with descriptions
- `iron-laws/index.md` — L1–L5 + L5-R (non-overlap)
- `rules/git-workflow.md` — branch + worktree protocol
- `rules/role-pm-coordinator.md` — PM's escalation path
- `hooks/index.md` — what runs when

## Future work (v0.2+)

- Multi-session feature-list shape (lifted from full kit's `templates/init.sh`)
- Auto-PR-creation in build-verify (currently manual)
