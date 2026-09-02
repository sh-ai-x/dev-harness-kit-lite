# Iron Laws — dev-harness-kit-lite (L1–L5 + L5-R)

These 6 iron rules are non-negotiable. The hooks (`hooks/`) enforce the machine-checkable ones automatically; the rest are team discipline.

## L1 — No prod code without a failing test

The TDD cycle is **Red → Green → Refactor**. You cannot know the test fails without running it.

- RED: write a failing test, run it, capture `exit_code != 0`
- GREEN: minimum code to pass, capture `exit_code == 0`
- REFACTOR: cleanup, tests still pass

Enforcement: `hooks/tdd-guard.sh` blocks Edit/Write when `.dev-kit/.tdd-cycle.json` does not show `phase == "red"` with a logged failure.

## L2 — No Edit/Write on `main` checkout

All edits happen in a worktree under `.worktrees/<scope>-<owner>/`. Main is sacred.

Enforcement: `hooks/worktree-guard.sh` denies Edit/Write/MultiEdit when session cwd is the main checkout (fails closed when `jq` is missing).

## L3 — No "done" claim without quoted exit code + test count

`/dev-kit-lite:build-verify` writes `.dev-kit/verify/<step>.json` with `exit_code`, `test_count`, `passed_count`, `failed_count`, last 20 lines of build log. Until that JSON exists for the current step, `stop-verify.sh` refuses the "done" claim.

## L4 — No TODO / FIXME / "we'll extend later" in committed code

Enforcement: `hooks/slop-detector.sh` (post-tool scan) + `hooks/l4-todo-scan.sh` (post-tool marker scan).

## L5 — One answer per question

No unrequested options list. Pick the recommended one and proceed. If the user wants alternatives, they'll ask.

## L5-R — Role non-overlap (team MVP rule)

**One person = at most ONE in-flight step at a time. One directory = at most ONE active owner at a time.**

Enforcement: `phases/<name>/owners.json` registry, checked by:
- `/dev-kit-lite:build-tdd` (pre-flight, refuses to start a step)
- `/dev-kit-lite:build-verify` (refuses to verify if owners.json shows a conflict)
- `/dev-kit-lite:reassign <stepN> <new-owner>` (PM-only mid-sprint ownership transfer)
- `/dev-kit-lite:plan-update` (PM-only mid-sprint PRD/phases mutation, may trigger reassign)

See `rules/role-pm-coordinator.md` for the PM's escalation path.
