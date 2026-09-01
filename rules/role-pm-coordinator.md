# role-pm-coordinator

## Headcount
- **1 person** (mandatory; full kit doesn't have this role)

## Owns
- `PRD.md`
- `.dev-kit/session-log.md`
- `.dev-kit/decision-log.md`
- `phases/<name>/owners.json` (PM is the only one who writes here mid-sprint)
- Arbitration rights: scope, owner reassignment, AC change

## Branch format
- PM does not own feature branches; PM owns `plan/<phase>-v<n>` for the planning worktree
- Merges to main: PM creates the merge commit, not the role-owner

## Worktree root
- `.worktrees/pm-<phase>` — e.g. `.worktrees/pm-mvp-v0`

## Non-overlap iron rule (L5-R)
- PM is exempt from the "one step at a time" rule (PM owns the meta-loop)
- PM is NOT exempt from the "one directory at a time" rule for code paths — PM does not edit code

## Before any decision
- [ ] Read PRD.md §5 Phase plan
- [ ] Read `.dev-kit/session-log.md` last 5 entries
- [ ] Confirm conflict exists in `phases/<name>/owners.json` (or new scope change)
- [ ] Pick one of:
  1. `/dev-kit-lite:reassign <stepN> <new-owner>` — change ownership
  2. `/dev-kit-lite:plan-update "<reason>"` — change scope/AC/steps
  3. `/dev-kit-lite:build-verify <stepN>` — sign off a step

## Hand-off contract
- Receives: all step ACs from role-owners (via `.dev-kit/session-log.md` + `docs/review/<step>.md`)
- Sends: build-verify verdict, reassignment notices, scope updates

## Coordination
- PM runs `/dev-kit-lite:build-verify` per step — this is the AC sign-off gate
- PM arbitrates merge conflicts (read-only: examines git diff, picks a side, instructs owner)
- PM is the only role allowed to run `/dev-kit-lite:reassign` or `/dev-kit-lite:plan-update`

## Forbidden
- Editing code in role-owned directories
- Merging to main without build-verify = Approve on all touched steps
- Skipping session-log entry for >30 min (clock drift)
