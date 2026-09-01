---
name: build-verify
category: verify
description: L3 evidence gate before "done". Verifies the step's quoted exit code + test count, snapshots the role-contract from owners.json, releases the step's path locks, and clears active_step. Blocks on missing evidence.
when_to_use:
  - After /dev-kit-lite:review returns Approve
  - Before merging a step's PR
  - As the final step in any role-owner's 6-stage loop
allowed-tools: Read Write Bash
model: sonnet
---

# /dev-kit-lite:build-verify

## Workflow

### Step 1 — Pull the evidence

Read the latest commit on the role-owner's feature branch:

```bash
git log -1 --format='%H%n%B' origin/main..HEAD
```

Parse the commit body for the L3 evidence gate markers:
- `Exit code:` line — the quoted exit code from the build-tdd GREEN step
- `Tests:` line — the test count (passed / total)
- A non-empty body is required; "fix typo" commits with no evidence are rejected

If any marker is missing, print a hard error and refuse to proceed.

### Step 2 — Verify the AC one more time

Re-read `phases/<name>/step<N>.md` `## Acceptance Criteria`. The commit body must reference each AC by id. If the role-owner claimed GREEN but the AC isn't satisfied, this is the gate that catches it.

### Step 3 — Snapshot the role-contract

Read `phases/<name>/owners.json` and verify:
- The step's Owner is in `owners` and matches the role from `## Role`
- The step's `Ows:` paths are listed in the owner's `owns_paths`
- The owner has at most one `active_step` (L5-R: one person = one in-flight step)

Write a snapshot to `.dev-kit/verify/<step-id>-<commit-sha>.json` for audit trail:

```json
{
  "step": "<name>",
  "commit": "<sha>",
  "owner": "<identifier>",
  "role": "<role>",
  "owns_paths": ["..."],
  "active_step_before": null,
  "ac_evidence": ["AC-1: satisfied (file:line)", "AC-2: satisfied (file:line)"],
  "test_evidence": "exit=0 passed=N/M",
  "snapshot_at": "<iso8601>"
}
```

### Step 4 — Release the path locks

Edit `phases/<name>/owners.json` to:
- Set the owner's `active_step` to `null`
- Remove the step's path entries from `path_locks` (those paths are now merge-candidate, not locked)

This unlocks the same paths for the next step's owner (L5-R non-overlap maintained).

### Step 5 — Write the verify report

Append to `.dev-kit/verify/<step-id>-<commit-sha>.md`:

```markdown
# build-verify — <step-id>

**Commit:** <sha>
**Owner:** <identifier> (<role>)
**Active step before:** null
**Active step after:** null (released)

## AC traceability

- AC-1: satisfied — <file:line>
- AC-2: satisfied — <file:line>

## Test evidence

- Command: <test_command>
- Exit code: 0
- Tests passed: N / M

## L4 check (no TODO / FIXME)

PASS — no TODO / FIXME / "later" in committed code

## Verdict

**PASS** — step cleared for merge.
```

### Step 6 — Return

Return "PASS" or "FAIL" with the verify report path. Do NOT merge (that's the role-owner's job, manual).

## Validation gates

- Commit body has `Exit code:` and `Tests:` lines
- Every AC in the step file is referenced by the commit body
- L4 check ran
- `.dev-kit/verify/<step-id>-<commit-sha>.json` was written
- `phases/<name>/owners.json` was updated (active_step = null, paths removed)

## Iron Laws

- **L1** (no prod code without a failing test) — block if commit body has no test evidence
- **L2** (verification before completion) — every quoted exit code + test count re-verified
- **L3** (evidence before claim) — no "done" without a verify report
- **L4** (no TODO in committed code) — surface in the L4 check
- **L5-R** (non-overlap) — releasing the path lock is what makes the next step available

## Anti-patterns

- ❌ Accepting "fix typo" commits with no L3 evidence as "verified"
- ❌ Skipping the role-contract snapshot — leaves no audit trail
- ❌ Releasing path locks BEFORE the role-contract snapshot (race with concurrent verify)
- ❌ Marking a step verified when its owner is still `active_step` on another step (L5-R violation)
- ❌ Auto-merging — verify gates, doesn't merge

## Next step

- Verdict = PASS → role-owner opens PR; reviewer runs `/dev-kit-lite:review`; merge is manual
- Verdict = FAIL → role-owner pushes a fix with proper L3 evidence; re-invoke `/dev-kit-lite:build-verify`
- All steps in a phase verified → PM closes the phase in `phases/<name>/index.json`
