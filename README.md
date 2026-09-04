# dev-harness-kit-lite

A Claude Code plugin for **4-hour MVP/POC team sprints**. One PM runs the planning. Each role-owner builds in their own worktree. Hooks block the dangerous stuff automatically. Local gates decide "done". No babysit loop, no auto-merge.

If you have ever wanted a small team to ship something demoable in one focused session without arguing about who-owns-what, this is the kit.

---

## Is this for me?

Use this kit when:

- You have 4-7 people, 4 hours, and one concrete MVP goal.
- You want a planner (PM), a couple of frontend devs, a couple of backend devs, maybe one designer, maybe one AI engineer.
- You want each person to own specific directories, no overlap.
- You want TDD enforced locally before anyone claims "done".
- You do not want a multi-week, multi-session orchestration tool.

Do not use this kit when:

- Your sprint is multi-week or multi-session. Use the full `dev-harness-kit` instead.
- You need GH-Actions gating or remote babysit loops. Lite is local-first; CI is advisory only.
- You want security/architecture fan-out reviews. Lite's `review` skill is one-dimensional (correctness only) by design.
- Your team is one person. The role separation assumes at least a PM + one builder.

When in doubt, the table at the bottom ("When to use vs the full kit") settles it.

---

## Vocabulary you will see

Three terms show up constantly. Here is what each one means.

| Term | Meaning |
|------|---------|
| **Skill** | A slash command you invoke as `/dev-kit-lite:<name>`. For example, `/dev-kit-lite:plan` writes the PRD. Skills live in `skills/<name>/SKILL.md` and (for the older ones) also in `.claude/commands/<name>.md` as forwarders. |
| **Hook** | A script that runs automatically when Claude Code does something (writes a file, runs bash, finishes a turn). Hooks block bad behaviour before it happens. See `hooks/index.md` for the full matrix. |
| **Stage** | A numbered phase in the 8-stage loop. Stage 0 is idea evaluation; Stage 6 is "done". Each stage has one or two skills wired to it. |

Iron Laws (L1 through L5 + L5-R) are the non-negotiable rules the kit enforces. They live in `iron-laws/index.md`. You don't need to memorise them; the hooks enforce the machine-checkable ones automatically.

---

## Install

You need Claude Code CLI on your machine. The kit runs through Claude Code's plugin system.

### Step 1: Add the marketplace (one time per developer)

```bash
claude plugin marketplace add sh-ai-x/dev-harness-kit-lite
claude plugin install dev-kit-lite
```

The marketplace URL is `sh-ai-x/dev-harness-kit-lite`. If your team upgrades the kit version later, run `claude plugin update dev-kit-lite`.

### Step 2a: Greenfield path (fresh repo)

For a brand-new project that has no `package.json` or `pyproject.toml` yet:

```bash
mkdir ~/my-mvp && cd ~/my-mvp
git init
bash /path/to/dev-harness-kit-lite/bin/install.sh .
```

The installer refuses if it sees `package.json`, `requirements.txt`, or `pyproject.toml` in the target directory. That is by design — lite's greenfield installer assumes you are starting from zero.

### Step 2b: Existing-project path

For a project that already has code:

```bash
cd /path/to/existing-project
claude  # open Claude Code
# then inside Claude Code:
/dev-kit-lite:migrate
```

`/dev-kit-lite:migrate` auto-detects whether your project is one repo, a workspace (pnpm / Nx / Turborepo / Lerna), or several repos with a shared `contracts/` location. It picks an aggressiveness mode (`conservative` / `balanced` / `aggressive`) and writes a 5-phase migration plan you can review before anything is installed.

### Step 3: Confirm the install

```bash
ls .claude/commands/   # 11 forwarder files
ls skills/             # 10 skill bundles + README.md
```

If `ls skills/` shows fewer than 10 directories, your plugin cache is stale. See the troubleshooting section below.

---

## First-time setup (10 minutes)

Once the kit is installed:

```bash
cd ~/my-mvp
git worktree add -b plan/mvp-v0 .worktrees/pm-mvp origin/main
cd .worktrees/pm-mvp
```

You are now in the PM's planning worktree. From here, run:

```bash
/dev-kit-lite:plan "One-page todo app with Next.js + FastAPI + SQLite"
```

The PM answers 5 short questions (Iron Law L5: one answer each), and the kit writes `PRD.md`, `phases/<name>/step<N>.md`, `phases/<name>/owners.json`. The PM is the only person who runs `plan`, `plan-update`, `reassign`, and `build-verify`.

Time-box this setup to 10 minutes. If it takes longer, something is wrong.

---

## The workflow

### Fast path: 4 skills if you already have a plan

If your team already knows the goal, the user, the roles, and the steps, skip Stage 0 and go straight to building.

```bash
/dev-kit-lite:plan "<your 1-line MVP goal>"
/dev-kit-lite:ci-setup                 # optional: installs ONE advisory review.yml
/dev-kit-lite:build-tdd                # each role-owner runs this in their own worktree
/dev-kit-lite:build-verify             # PM-only sign-off gate
```

That is the four-skill minimum. The PM runs `plan` and `build-verify`. Each role-owner runs `build-tdd` for their own steps. `ci-setup` is optional.

### Full loop: 8 stages + 2 cross-cutting

When you want the full kit — including idea scoring, role taxonomy, team roster, and review — the 8 stages look like this:

```
Stage 0       Stage 1                       Stage 2     Stage 3    Stage 4       Stage 5     Stage 6
idea-eval  -> bootstrap  ->  role  ->  plan    -> ci-setup -> build-tdd -> review -> build-verify
                     \-> migrate (existing projects instead of bootstrap)
                     \-> setup-guard (Stage 1.1, optional — toggle TDD/main-push guards)
                     \-> team-roster (Stage 1.5, after role)
                     \-> role-plan (Stage 1.6, after team-roster)
                     \-> role-tdd (Stage 4a, role-owner variant of build-tdd)
                     \-> proposal (Stage 2c, optional before/after design doc, after plan)

Cross-cutting (anytime):
  - reassign       (PM-only ownership transfer)
  - plan-update    (PM-only PRD mutation)
```

The 15 skills by stage:

| Stage | Skill | Who runs it | What it writes |
|-------|-------|-------------|----------------|
| 0 | `/dev-kit-lite:idea-eval` | PM (optional) | `.dev-kit/idea-eval/<slug>.md` with an S/A/B/C/D grade |
| 1 | `/dev-kit-lite:bootstrap` | PM | `CLAUDE.md`, `AGENTS.md`, `.dev-kit/.active-hooks.json`, first commit |
| 1.1 | `/dev-kit-lite:setup-guard` | PM (optional) | Toggles `tdd_guard_enabled` / `main_push_block_enabled` in `.dev-kit/.guard-config.json` |
| 1.3 | `/dev-kit-lite:role` | PM | Role taxonomy + tech-stack presets |
| 1.4 | `/dev-kit-lite:migrate` | PM (existing project) | `role-config.json`, coexistence report, 5-phase plan |
| 1.5 | `/dev-kit-lite:team-roster` | PM | `phases/<name>/owners.json` with per-role identifier + name |
| 1.6 | `/dev-kit-lite:role-plan` | PM | Per-role plan docs, each scoped to one role's assigned steps |
| 2 | `/dev-kit-lite:plan` | PM | `PRD.md`, `phases/<name>/step<N>.md`, `owners.json` |
| 2b | `/dev-kit-lite:plan-update` | PM (mid-sprint) | Mutates PRD or steps; may trigger reassign |
| 2c | `/dev-kit-lite:proposal` | PM (optional) | `docs/proposals/<bucket>/<main>/<sub>.html` — self-contained before/after design doc for reviewers |
| 3 | `/dev-kit-lite:ci-setup` | PM (opt-in) | `.github/workflows/review.yml` (advisory only) |
| 4a | `/dev-kit-lite:role-tdd` | Role-owner | Role-scoped Red-Green-Refactor, auto-scoped to one identifier |
| 4b | `/dev-kit-lite:build-tdd` | Role-owner / PM | Failing test, then code, then refactor (PM/orchestrator variant) |
| 5 | `/dev-kit-lite:review` | Reviewer | `docs/review/<step>.md` verdict |
| 6 | `/dev-kit-lite:build-verify` | PM | `.dev-kit/verify/<step>.json`, releases owner lock |
| (cross) | `/dev-kit-lite:reassign` | PM | Updates `owners.json` + step's `## Role` |

The full list (with one-line purposes) lives in `skills/README.md`.

---

## Worked example: a todo app in 4 hours

A 5-person team — Priya (PM), Alice + Bob (frontend), Carol + Dan (backend) — wants to ship a small todo app demoable to stakeholders by EOD. Tech stack: Next.js (App Router) frontend, FastAPI backend, SQLite for storage, no auth.

### Hour 0 — Priya (PM) plans

Priya cuts the planning worktree and runs:

```bash
git worktree add -b plan/todo-v0 .worktrees/pm-todo origin/main
cd .worktrees/pm-todo
/dev-kit-lite:plan "Todo app: add, list, complete, delete. Next.js + FastAPI + SQLite."
```

Priya answers 5 questions and the kit produces a 6-step plan. A realistic step breakdown with dependency edges:

| Step | What | Owner | Depends on | Layer |
|------|------|-------|------------|-------|
| 1 | FastAPI `/todos` CRUD routes + SQLite schema | Carol (BE) | — | 0 (foundation) |
| 2 | Pytest suite for the routes | Dan (BE) | step 1 | 1 |
| 3 | Next.js App Router page shell + types | Alice (FE) | — | 0 (foundation) |
| 4 | TanStack Query hooks + form for create | Bob (FE) | step 3 | 1 |
| 5 | List view + complete/delete handlers | Alice (FE) | step 4 | 2 |
| 6 | End-to-end happy-path test + README | Bob (FE) | steps 2, 5 | 3 |

Critical path: steps 1 -> 2 -> 6 (backend) and 3 -> 4 -> 5 -> 6 (frontend). Layer 0 can run in parallel (Carol and Alice both start at hour 0). Layer 1 starts as soon as Layer 0 lands. Step 6 integrates both.

### Hour 0:30 — Team cuts role-owner worktrees

Alice cuts hers, branches off `origin/main`:

```bash
git fetch origin main
git worktree add -b feat/web-alice-step3 .worktrees/web-alice origin/main
cd .worktrees/web-alice
```

Carol does the same on a backend branch:

```bash
git worktree add -b feat/api-carol-step1 .worktrees/api-carol origin/main
cd .worktrees/api-carol
```

### Hours 0:30 to 2:30 — Each role-owner runs build-tdd

In `.worktrees/api-carol` Carol runs:

```bash
/dev-kit-lite:build-tdd
```

The skill reads `phases/<name>/step1.md`, confirms Carol is the Owner, checks `owners.json` for conflicts, and walks her through the Red-Green-Refactor cycle. She writes a failing pytest first, logs the failure, then writes the route handler. Hooks block production-code edits until the RED phase is logged (L1).

Alice does the same in `.worktrees/web-alice` for step 3.

### Hour 2:30 — Priya verifies per step

When Carol says "step 1 is done", Priya runs:

```bash
cd .worktrees/api-carol
/dev-kit-lite:build-verify 1
```

This captures test counts and exit codes, writes `.dev-kit/verify/1.json`, and releases the ownership lock in `owners.json` (so Dan can pick up step 2 without conflict). L3 evidence is now on file.

### Hour 3 — Review and merge

Priya (or a peer reviewer) runs:

```bash
/dev-kit-lite:review 1
```

This writes `docs/review/1.md` with verdict `Approve` / `Changes Requested` / `Blocked`. After Approve, Priya merges the branch manually. CI is advisory only — `continue-on-error: true` in `review.yml` — so a red CI does not block merge.

### Hour 4 — Demo

The team has a working todo app. Step 6 was an end-to-end test that proves the wiring. Time to demo.

---

## Roles, in plain language

The kit has 5 structural roles. Each role is a slot, not a person — you can have two frontend devs and one backend dev; that is fine.

### PM / Coordinator (1 person, mandatory)

You own the loop. You are the only one who runs `plan`, `plan-update`, `reassign`, and `build-verify`. You are the only one who merges to the protected branch. You do not write code in role-owned directories. Your worktree is the planning hub.

### Frontend (n people, default 2)

You own `apps/web/`, `components/`, `hooks/`, `styles/`, `public/`, and frontend-side `package.json` / `tsconfig.json` / `next.config.js`. You do not touch `api/`, `services/`, `models/`. Your tech stack is one of `nextjs-app-router`, `react-vite`, `react-native-cli`, `expo`, `vue-nuxt`, `sveltekit` (or write your own at `templates/tech-stacks/<name>.json`).

### Backend (n people, default 2)

You own `api/`, `services/`, `models/`, `tests/`, `requirements.txt`, `pyproject.toml`, `alembic/`. You do not touch `apps/web/`, `components/`. Your stack is one of `fastapi`, `django`, `flask`, `express`, `nestjs`, `go-gin`, `spring-boot`.

### AI Engineer (n people, default 0–1)

You own AI-related files (model client wrappers, prompt files, eval scripts). Stack: `minimax-only`, `anthropic-only`, or `multi-provider`.

### Design (Figma MCP) (n people, default 0–1)

You own `design/`, `tokens/`, `figma-export/`, `screenshots/`. Stack: `figma-mcp`, `penpot-export`, or `sketch-export`.

### Two key concepts

| Concept | Meaning |
|---------|---------|
| `tech_stack` | The label that says what your role uses (Next.js, FastAPI, etc.). Run `/dev-kit-lite:role` to set it. The kit will not write a plan until every role has a non-empty `tech_stack`. |
| `owns_paths` | The directory globs your role is allowed to edit. Two roles cannot claim the same `owns_paths`. If both FE and BE want `types/`, the team picks one owner or splits the directory. |

The rule "one directory = one active owner at a time" is **L5-R non-overlap**. The `phases/<name>/owners.json` file is the machine-checkable contract — `build-tdd` refuses to start a step if its Owner or paths conflict with an in-flight step.

Read your role spec in `rules/role-<your-discipline>.md` before you cut a worktree. It tells you exactly which paths you own and which are off-limits.

---

## Common-task recipes

These are the situations you will hit. Each one has a copy-pasteable fix.

### Add a member mid-sprint

A new person joined. PM reassigns one or more steps to them.

```bash
/dev-kit-lite:reassign <stepN> <new-owner-identifier>
```

This updates `owners.json` and the step's `## Role` section. Only PM can run it. The new owner then cuts their worktree:

```bash
git fetch origin main
git worktree add -B feat/<scope>-<new-owner>-<slug> .worktrees/<scope>-<new-owner> origin/main
cd .worktrees/<scope>-<new-owner>
```

### Switch tech stack mid-sprint

PM runs:

```bash
/dev-kit-lite:role
```

and re-picks the tech-stack preset for the affected role(s). After this, `/dev-kit-lite:plan` (or `/dev-kit-lite:plan-update` if steps already exist) must be re-run so `owners.json` and the step `## Role` sections reflect the new paths.

### Reassign a step to a different role (e.g. FE -> BE)

If a step is misrouted, PM uses both skills:

```bash
/dev-kit-lite:plan-update "<one-line reason>"
# multiSelect: pick "Reassign owner" + "Update owns_paths"
/dev-kit-lite:reassign <stepN> <new-owner-identifier>
```

Only PM touches `owners.json`. Do not edit it by hand.

### Force-refresh a stale plugin cache

If you updated the kit version but Claude Code is still showing old skills, the marketplace cache is stale (issue #6, fixed by PR #7).

```bash
claude plugin marketplace update dev-kit-lite
claude plugin update dev-kit-lite
# If that doesn't work, remove and re-add:
claude plugin uninstall dev-kit-lite
claude plugin marketplace update sh-ai-x/dev-harness-kit-lite
claude plugin install dev-kit-lite
```

### Test the loop without a real sprint

```bash
mkdir /tmp/lite-dryrun && cd /tmp/lite-dryrun
git init
bash /path/to/dev-harness-kit-lite/bin/install.sh /tmp/lite-dryrun
cd /tmp/lite-dryrun
git worktree add -b plan/test-v0 .worktrees/test-v0 origin/main
cd .worktrees/test-v0
/dev-kit-lite:plan "Dry-run: hello world Next.js + FastAPI"
```

This is a real install; clean up with `rm -rf /tmp/lite-dryrun` when done.

### Tear down the kit runtime state (keep code)

```bash
rm -rf .dev-kit/ .worktrees/ phases/
```

This discards verify logs, owners registry, and per-step plans. Your code stays.

---

## Troubleshooting

Concrete errors you might see and what each means.

### `ERROR: existing project files detected in /path/to/target`

The greenfield installer refuses if it sees `package.json`, `requirements.txt`, or `pyproject.toml` in the target. For an existing project, use `/dev-kit-lite:migrate` instead — it detects the layout and writes a 5-phase migration plan.

### `ERROR: /path/to/.git already has N commit(s)`

Same refusal: the installer assumes a fresh `git init`. Move existing commits to a backup branch, or use `migrate`.

### `worktree-guard: cannot Edit/Write on main checkout`

You tried to edit code while sitting in the main checkout. Iron Law L2: every edit happens in a worktree. Cut one:

```bash
git worktree add -B feat/<scope>-<your-name>-<slug> .worktrees/<scope>-<your-name> origin/main
cd .worktrees/<scope>-<your-name>
```

### `tdd-guard: cannot Edit/Write without a logged RED phase`

Iron Law L1: write a failing test, run it, log the failure first, then write production code. The hook reads `.dev-kit/.tdd-cycle.json` and refuses prod edits if `phase != "red"` with a logged exit code. The fix: write the test, run it, observe the non-zero exit, *then* write the production code.

### `owners.json conflict: <path> already owned by <other-role>`

L5-R non-overlap. Two roles are claiming the same path. PM resolves this — either pick one owner, split the directory, or move the contested path to `shared_write_paths` with PM sign-off. Do not edit `owners.json` yourself.

### `stop-verify: cannot claim "done" without .dev-kit/verify/<step>.json`

Iron Law L3. You cannot say "done" without quoted exit codes and test counts. PM runs `/dev-kit-lite:build-verify <step>` to capture them.

### Skill shows up as slash command but not as a bundle

`ls skills/` shows fewer than 10 directories. This is issue #8 — `review` and `build-verify` ship as slash-command forwarders (`.claude/commands/review.md`) but not as full `SKILL.md` bundles. They still work via `/dev-kit-lite:review` and `/dev-kit-lite:build-verify`; PR #9 adds the missing bundles. Until that PR merges, treat those two skills as command-only.

### Plugin cache shows old version after a `git pull` or new release

Issue #6 — the marketplace cache can go stale when new files land without a version bump. Fix: see "Force-refresh a stale plugin cache" above. PR #7 added a CI guard that fails the PR if `skills/` or `commands/` grow without a version bump, so this should not recur.

### CI is red

CI is **advisory only**. `continue-on-error: true` in `.github/workflows/review.yml` means red CI does not block merge. Fix forward in the next step.

### `claude plugin marketplace add` says "marketplace already exists"

You added it before. Skip to `claude plugin install dev-kit-lite` (or `claude plugin update dev-kit-lite` to upgrade).

---

## When to use vs the full kit

One table, no fence-sitting.

| If your situation looks like this | Use |
|-----------------------------------|-----|
| 4-hour sprint, 4-7 people, one demo | **lite** |
| Multi-week / multi-session project | full `dev-harness-kit` |
| Manual merges + local gates are fine | **lite** |
| You need GH-Actions gating + remote babysit | full kit |
| Greenfield OR existing project (via `migrate`) | **lite** |
| Multi-agent autonomous work | full kit |
| Speed > rigor | **lite** |
| Rigor > speed | full kit |
| TDD enforced locally, advisory CI | **lite** |
| CI-as-gate with required status checks | full kit |

If your row says "lite", stay here. If your row says "full", see `dev-harness-kit`.

---

## Resources

Read these in order. Each one is short.

1. `skills/README.md` — the 11-skill table with one-line purposes per stage.
2. `iron-laws/index.md` — L1, L2, L3, L4, L5, L5-R. Hooks enforce the machine-checkable ones automatically.
3. `hooks/index.md` — the 6-hook matrix: which event fires which script, and which ones block on failure.
4. `rules/role-<your-discipline>.md` — your role's owning spec. Read this before cutting a worktree.
5. `rules/team-collab.md` — the 4-hour cadence and role hand-off protocol.
6. `rules/git-workflow.md` — branch + worktree protocol. The three bedrock rules: main is sacred, every task gets its own worktree, branches fork from `origin/main`.
7. `USAGE.md` — per-role walkthrough (PM, FE, BE, Design, Reviewer, new joiner). Longer than this README; read when you have a specific role question.
8. `CHANGELOG.md` — version history. Each entry explains what changed and why.

If you find a bug in this README, open an issue against `sh-ai-x/dev-harness-kit-lite`.
