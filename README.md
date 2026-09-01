# dev-harness-kit-lite

A 4-hour MVP/POC team-collab plugin — pruned from the full `dev-harness-kit`.

## What it is

7 skills · 7 hooks · 6 stages · ~40 files. Optimized for **greenfield MVP sprints** where a small team (1 PM + 2 FE + 2 BE + 1 Design) ships in one focused 4-hour session.

## What it is NOT

- ❌ Not for retrofitting into existing repos (use the full kit)
- ❌ Not for multi-week, multi-session work (use the full kit)
- ❌ Not a security review tool (excluded by design — speed > gating)
- ❌ Not an auto-merge / babysit loop (team merges manually)

## Quick start

```bash
# 1. Install into a fresh repo (refuses if package.json/requirements.txt exists)
cd /path/to/new-project
git init
bash /path/to/dev-harness-kit-lite/bin/install.sh .

# 2. Cut a worktree for the PM's planning session
git worktree add -b plan/mvp-v0 .worktrees/pm-mvp origin/main
cd .worktrees/pm-mvp

# 3. Run the 6-stage loop
/dev-kit-lite:plan "<your 1-line MVP goal>"
/dev-kit-lite:ci-setup                           # opt-in: installs ONE advisory review.yml
/dev-kit-lite:build-tdd                          # per-step, in each role-owner's worktree
/dev-kit-lite:review                             # per-step correctness check
/dev-kit-lite:build-verify                       # L3 evidence gate before "done"
```

## The 6-stage loop

```
   ┌──────────┐    ┌──────┐    ┌──────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐
   │ bootstrap├───►│ plan ├───►│ ci-setup ├───►│ build-tdd├───►│ review ├───►│build-verify│
   └──────────┘    └──────┘    └──────────┘    └──────────┘    └────────┘    └──────────┘
                                       │                              ▲
                                       ▼                              │
                                   review.yml                     verdict
                                  (advisory only,                  Approve |
                                   never blocks                     Changes |
                                   merge)                           Blocked
```

## Role model (L5-R non-overlap)

Each phase step has exactly **one Owner** and a list of **Owns:** paths. The `phases/<name>/owners.json` registry is the machine-checkable contract — `build-tdd` refuses to start a step if its Owner or paths conflict with an in-flight step.

| Role | Headcount | Owns | Branch prefix |
|------|-----------|------|---------------|
| PM / Coordinator | 1 | PRD.md, .dev-kit/session-log.md, decision arbitration | — |
| Frontend | n (default 2) | apps/web/, components/, hooks/, styles/ | feat/web/<owner>-<slug> |
| Backend | n (default 2) | api/, services/, models/, tests/ | feat/api/<owner>-<slug> |
| Design (Figma MCP) | n (default 1) | design/, tokens/, figma-export/, screenshots/ | feat/design/<owner>-<slug> |

## When to use vs the full kit

| Use **lite** when | Use **full** when |
|---------------------|---------------------|
| Greenfield MVP / POC | Multi-week / multi-session |
| 4-hour sprint with 4-7 people | Multi-agent autonomous work |
| Manual merges + local gates | GH-Actions gating + remote babysit |
| Speed > rigor | Rigor > speed |

## See also

- `iron-laws/index.md` — L1–L5 + L5-R (non-overlap)
- `rules/git-workflow.md` — branch + worktree protocol
- `rules/role-pm-coordinator.md` — PM's escalation path
- `hooks/index.md` — what runs when

## Future work (v0.2+)

- Existing-project importer (`bin/import-existing.sh`) for retrofitting lite into half-finished repos
- Multi-session feature-list shape (lifted from full kit's `templates/init.sh`)
- Auto-PR-creation in build-verify (currently manual)
