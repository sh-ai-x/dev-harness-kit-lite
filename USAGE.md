# USAGE.md — dev-harness-kit-lite for each team role

This is a **4-hour MVP/POC team sprint guide**, written for the 6 personas you'll find on a typical team. Read the section that matches your role.

> **Quick map** (everyone reads this):
> - PM/Coordinator → §1
> - Frontend → §2
> - Backend → §3
> - Design (Figma MCP) → §4
> - Reviewer (peer) → §5
> - New joiner mid-sprint → §6

---

## §0 — Before the sprint (everyone, 5 minutes)

```bash
# 1. Install the plugin from the marketplace
claude plugin marketplace add sh-ai-x/dev-harness-kit-lite
claude plugin install dev-kit-lite

# 2. In a FRESH (empty) target repo, run the installer
mkdir ~/my-mvp && cd ~/my-mvp && git init
bash /path/to/dev-harness-kit-lite/bin/install.sh .

# 3. Confirm 8 skills are wired
ls .claude/commands/   # → 8 forwarders (bootstrap/plan/plan-update/ci-setup/build-tdd/build-verify/review/reassign)
```

**Time-box the install to 10 min.** If it takes longer, something is wrong (probably an existing file the installer should have refused).

---

## §1 — PM / Coordinator (1 person, mandatory)

You own the loop. You are the only one allowed to:
- Run `/dev-kit-lite:plan` at sprint start
- Run `/dev-kit-lite:plan-update` mid-sprint
- Run `/dev-kit-lite:reassign` mid-sprint
- Run `/dev-kit-lite:build-verify` (this is your **sign-off** gate)
- Merge to the protected branch

### Your worktree

```bash
git worktree add -b plan/<phase>-v<n> .worktrees/pm-<phase> origin/main
cd .worktrees/pm-<phase>
```

PM's worktree is the **planning hub**. Code edits do not happen here.

### Hour 0 (0:00–0:30) — Plan

```bash
/dev-kit-lite:plan "One-page checkout with Next.js + FastAPI + Stripe"
```

You will be asked 5 questions (L5: one answer each):
1. **Goal** (1 sentence)
2. **Target user** (1 sentence)
3. **Situation** (1 sentence)
4. **Role assignment** — names of your team
5. **Step breakdown** — 3-8 steps, each with owner + AC

Outputs: `PRD.md`, `phases/<name>/index.json`, `phases/<name>/step<N>.md` (one per step), `phases/<name>/owners.json`.

### Hour 0–3 (every 30 min) — Check-in

Append to `.dev-kit/session-log.md`:

```markdown
[HH:MM] PM check-in: step<N> by <owner> — <status>
```

### Hour 0–3 (as needed) — Resolve conflicts

If a role-owner reports they're blocked or scope changed:

```bash
# Pure ownership change (e.g. Alice sick → reassign her step to Bob)
/dev-kit-lite:reassign <stepN> <new-owner>

# Scope / AC / step-count change
/dev-kit-lite:plan-update "<one-line reason>"
# Then answer the multiSelect: which kind of change
```

Both skills write to `phases/<name>/owners.json` and `decision-log.md`. You are the **only one** allowed to call these.

### Hour 2.5–3 — Verify (per step)

When a role-owner reports "step N is done", you sign off:

```bash
cd .worktrees/<scope>-<owner>     # cd into the owner's worktree, not yours
/dev-kit-lite:build-verify <N>
```

This runs tests, captures exit codes, writes `.dev-kit/verify/<N>.json`, releases the ownership lock in `owners.json`, and appends your sign-off to `session-log.md`. **Never skip this** — it's L3 (the "done" gate).

### Hour 3–4 — Review + merge

```bash
# Each role-owner's branch is reviewed
/dev-kit-lite:review <stepN>

# After Approve, merge via squash
cd /path/to/my-mvp
git merge --squash feat/web-alice-checkout
```

**CI is advisory-only.** You can merge on red CI if local build-verify passed. Speed > gating.

### Your forbidden list

- ❌ Editing code in role-owned directories (`apps/web/`, `api/`, etc.)
- ❌ Calling `build-tdd` (that's the owner's job)
- ❌ Skipping `build-verify` before claiming "done"
- ❌ Merging without an Approve review verdict in `docs/review/<N>.md`

---

## §2 — Frontend (n people, default 2)

You own `apps/web/`, `components/`, `hooks/`, `styles/`, `public/`, and frontend-side `package.json` / `tsconfig.json` / `next.config.js`.

### Your worktree (cut once per step)

```bash
git worktree add -b feat/web-<your-name>-<step-slug> .worktrees/web-<your-name> origin/main
cd .worktrees/web-<your-name>
```

Example: `feat/web-alice-checkout` → `.worktrees/web-alice`

### Your loop per step

1. **Read** `phases/<name>/step<N>.md` `## Role` section. Confirm **you** are the Owner.
2. **Verify** L5-R: run `cat phases/<name>/owners.json | jq '.owners.<your-name>.active_step'` — must be `null` before you start.
3. **RED**: write a failing test, run it, log via `python3 -m lib.tdd_cycle red -- "<test command>"`.
4. **GREEN**: write minimum code to pass. `tdd-guard.sh` now allows prod edits.
5. **REFACTOR**: clean up; tests must still pass.
6. **Stage + commit + push** with quoted exit codes in the commit body (L3).
7. **Hand off to PM**: "step 1 done, ready for build-verify". PM runs `/dev-kit-lite:build-verify 1`.

### Your forbidden list

- ❌ Editing `api/`, `services/`, `models/` (backend territory)
- ❌ Editing `design/`, `tokens/` directly (ask role-figma-mcp for a token dump)
- ❌ Starting a second step while your first is still `active_step: <N>` in `owners.json`
- ❌ Editing in the main checkout (worktree-guard blocks with a clear error)
- ❌ Skipping RED phase (tdd-guard blocks prod-code edits)

### When you get blocked

1. Append to `.dev-kit/session-log.md`: `[HH:MM] alice blocked on step 1: <reason>`
2. Ping PM in chat
3. PM runs `/dev-kit-lite:reassign 1 <someone-else>` if needed, or `/dev-kit-lite:plan-update` if scope must change
4. **Don't** edit `owners.json` yourself — only PM can.

---

## §3 — Backend (n people, default 2)

You own `api/`, `services/`, `models/`, `tests/`, `requirements.txt`, `pyproject.toml`, `alembic/`.

### Your worktree

```bash
git worktree add -b feat/api-<your-name>-<step-slug> .worktrees/api-<your-name> origin/main
cd .worktrees/api-<your-name>
```

Example: `feat/api-carol-checkout` → `.worktrees/api-carol`

### Your loop per step

1. **Read** `phases/<name>/step<N>.md`. Confirm you're the Owner.
2. **Verify L5-R**: same as frontend.
3. **RED**: write a failing pytest, log via `python3 -m lib.tdd_cycle red -- "pytest tests/test_checkout.py -v"`.
4. **GREEN**: write the route handler. `tdd-guard.sh` allows prod edits.
5. **REFACTOR**: clean up; tests must still pass.
6. **Stage + commit + push** with quoted exit codes in the commit body (L3).
7. **Hand off**: notify PM.

### Your forbidden list

- ❌ Editing `apps/web/`, `components/` (frontend territory)
- ❌ Hitting external services (Stripe, AWS, etc.) in tests — mock them
- ❌ Skipping type check (`mypy api/ services/ models/`)
- ❌ Skipping `ruff check` (lint is part of `build-verify`)

### Hand-off to frontend

After your step is verified, write the API contract so frontend knows what to call. Save it to `docs/api/<endpoint>.md` and notify frontend in chat.

---

## §4 — Design / Figma MCP (n people, default 1)

You own `design/`, `tokens/`, `figma-export/`, `screenshots/`.

### Your worktree

```bash
git worktree add -b feat/design-<your-name>-<step-slug> .worktrees/design-<your-name> origin/main
cd .worktrees/design-<your-name>
```

Example: `feat/design-eve-tokens` → `.worktrees/design-eve`

### Setup (one-time, before sprint)

Figma MCP server is configured **globally** per the user's `~/.claude/CLAUDE.md`. No local setup needed. If it's not working, raise the issue to PM **before** starting the sprint.

### Your loop per step

1. **Read** `phases/<name>/step<N>.md`. Confirm you're the Owner.
2. **Export tokens from Figma** via the Figma MCP tool.
3. **Validate tokens** (if validator exists): `node scripts/validate-tokens.js` → exit 0.
4. **Re-export screenshots** (any time source changes).
5. **Stage + commit + push** with quoted export counts in body (L3).

### Hand-off to frontend

After your step is verified, the tokens are ready for frontend to consume:
- `design/tokens/colors.json`
- `design/tokens/typography.json`
- `design/tokens/spacing.json`
- `screenshots/*.png` (visual references)

Frontend will mirror these into `apps/web/styles/tokens.css`.

### Your forbidden list

- ❌ Editing `apps/web/`, `api/` (other roles' territory)
- ❌ Pushing tokens without role-frontend sign-off (L5-R: frontend must accept the names)
- ❌ Skipping screenshot re-export after Figma source change

---

## §5 — Reviewer (any role-owner, peer review)

You run `/dev-kit-lite:review` on a PR opened by another role-owner.

### When to run

- After a role-owner pushes their branch and opens a PR
- Before the PM merges
- Optional but recommended: every PR gets a second pair of eyes

### How to run

```bash
cd /path/to/my-mvp
git fetch origin feat/web-alice-checkout
git checkout feat/web-alice-checkout

/dev-kit-lite:review 1
```

### What you produce

`docs/review/<step>.md`:
```markdown
# Review: step 1
**Verdict:** Approve | Changes Requested | Blocked
**Reviewer:** <your-name>
**Date:** <iso>

## AC matrix
| AC | Status | Evidence |
|----|--------|----------|
| AC-1 | PASS | test_x.py:42 |
| AC-2 | FAIL | missing error handler at api/checkout.py:18 |

## Findings
- api/checkout.py:18 — no error handler for 4xx responses
```

### Verdict semantics

| Verdict | Meaning | Next action |
|---------|---------|-------------|
| Approve | All ACs satisfied | Owner merges (or PM merges if PM-mediated) |
| Changes Requested | Some ACs fail or nitpicks | Owner fixes → re-runs build-tdd → re-runs review |
| Blocked | Fundamental issue (wrong scope, breaks other steps) | Owner + PM discuss → use `/dev-kit-lite:plan-update` |

### What you DON'T review

- ❌ Security (excluded by design — manual review at PR is OK, but no security fan-out)
- ❌ Architecture (deferred to team lead — no 3-dim review)
- ❌ Performance (out of scope for 4-hour MVP)

---

## §6 — New joiner mid-sprint (rare, but happens)

You joined after the PM already ran `/dev-kit-lite:plan`. Here's how to catch up.

### 1. Read the sprint context (10 min)

```bash
cat PRD.md
cat phases/<name>/owners.json | jq
for f in phases/<name>/step*.md; do
  status=$(grep -E '^## Status' "$f" -A 1 | tail -1)
  echo "$f: $status"
done
```

### 2. Find your role

Open `rules/role-<your-discipline>.md`. Read the Owns / Branch / Worktree sections.

### 3. Pick an unclaimed step

```bash
cat phases/<name>/index.json | jq '.steps[] | select(.status == "pending")'
```

### 4. Ask PM for an assignment

In chat: "I'm <name>, I want to own step<N> as <FE | BE | Design>."

PM runs:
```bash
/dev-kit-lite:reassign <N> <your-name>
```

PM updates `owners.json` and the step's `## Role` section. **Then** you can cut your worktree.

### 5. Cut your worktree (after PM has reassigned)

```bash
git fetch origin main
git worktree add -B feat/<scope>-<your-name>-<slug> .worktrees/<scope>-<your-name> origin/main
cd .worktrees/<scope>-<your-name>
```

### 6. Continue with /dev-kit-lite:build-tdd

See §2 / §3 / §4 for the per-discipline loop.

---

## §7 — Common workflows (everyone)

### "I want to push to main"

You don't. PM merges. PM is the only one with merge authority in lite.

### "CI is red"

CI is **advisory-only** (`continue-on-error: true` in `review.yml`). Red CI does not block merge. Fix forward in your next step.

### "I need to add a step mid-sprint"

PM runs `/dev-kit-lite:plan-update "<reason>"` and selects "Add new step". PM updates `PRD.md §5`, `index.json`, and writes a new `step<N+1>.md` with a `## Role` section.

### "My teammate is sick and I need to take over their step"

PM runs `/dev-kit-lite:reassign <N> <your-name>`. PM updates `owners.json` and the step's `## Role`. **Do not** edit `owners.json` yourself.

### "The AC for my step changed"

PM runs `/dev-kit-lite:plan-update` and selects "Change AC of existing step". PM updates `PRD.md §3` AND the step's `## Acceptance Criteria` section.

### "I want to test the loop without a real sprint"

```bash
mkdir /tmp/lite-dryrun && cd /tmp/lite-dryrun
bash /path/to/dev-harness-kit-lite/bin/install.sh /tmp/lite-dryrun
cd /tmp/lite-dryrun
git worktree add -b plan/test-v0 .worktrees/test-v0 origin/main
cd .worktrees/test-v0
/dev-kit-lite:plan "Dry-run: hello world Next.js + FastAPI"
```

---

## §8 — Reference card (print and stick to monitor)

```
+------------------------------------------------------------------+
|                   dev-kit-lite 4-hour loop                       |
+------------------------------------------------------------------+
|  PM only:        /dev-kit-lite:plan                              |
|                  /dev-kit-lite:plan-update                       |
|                  /dev-kit-lite:reassign <step> <owner>           |
|                  /dev-kit-lite:build-verify <step>  <- sign-off  |
|  Anyone:         /dev-kit-lite:bootstrap                        |
|                  /dev-kit-lite:ci-setup                         |
|                  /dev-kit-lite:build-tdd                         |
|                  /dev-kit-lite:review <step>                     |
+------------------------------------------------------------------+
|  Iron Laws:     L1 RED->GREEN  L2 worktree  L3 verify  L4 no-TODO|
|                 L5 one-answer  L5-R non-overlap                  |
+------------------------------------------------------------------+
|  Worktree:      .worktrees/<scope>-<your-name>                   |
|  Branch:        feat/<scope>-<your-name>-<slug>                  |
|  Owner lock:    phases/<name>/owners.json                        |
|  Verify:        .dev-kit/verify/<step>.json                      |
|  Session log:   .dev-kit/session-log.md                          |
+------------------------------------------------------------------+
```

---

## §9 — Installation matrix (for team leads)

| What | Command | Notes |
|------|---------|-------|
| Add marketplace | `claude plugin marketplace add sh-ai-x/dev-harness-kit-lite` | One-time per developer |
| Install plugin | `claude plugin install dev-kit-lite` | After marketplace add |
| Update plugin | `claude plugin update dev-kit-lite` | When team upgrades the version |
| Scaffold new project | `bash bin/install.sh <path>` | Refuses if package.json/requirements.txt exists |
| Re-bootstrap | `/dev-kit-lite:bootstrap` | Idempotent; safe to re-run |
| Tear down | `rm -rf .dev-kit/ .worktrees/ phases/` | Discards runtime state |

### Compatibility

| Works with | Notes |
|------------|-------|
| Claude Code (latest) | Primary target |
| Codex CLI | Mirror at `.codex-plugin/`; same skills, same hooks |
| Both at once | Both CLIs read the same `phases/<name>/owners.json` registry; non-overlap enforced cross-CLI |
| Full `dev-harness-kit` | Complementary — use lite for 4-hour MVP, full for multi-week |

### See also

- `README.md` — quick-start (5 commands)
- `iron-laws/index.md` — L1–L5 + L5-R
- `rules/team-collab.md` — 4-hour cadence
- `rules/role-<discipline>.md` — your role's owning spec
- `templates/step.md` — the step template with mandatory `## Role` section
- `templates/owners.example.json` — the L5-R non-overlap registry shape
