---
name: review
category: review
description: 1-dim correctness review of one step's diff. Reads PRD.md or the relevant step file, walks the diff, verifies each AC, posts an advisory verdict as a PR comment. No security fan-out — that's the full kit's job.
when_to_use:
  - After /dev-kit-lite:build-tdd completes for a step
  - When a PR is opened targeting main
  - When the role-owner wants a second pair of eyes before claiming "done"
allowed-tools: Read Bash
model: sonnet
---

# /dev-kit-lite:review

## Workflow

### Step 1 — Read the AC source

1. Open `PRD.md` and locate the AC mapped to this PR's step.
2. If the PR is per-step, also read `phases/<name>/step<N>.md` `## Acceptance Criteria` block.
3. If neither exists, walk the diff and infer what the PR is trying to achieve — but only after printing a warning that AC traceability is unverifiable.

### Step 2 — Walk the diff

```bash
git diff origin/main..HEAD --stat
git diff origin/main..HEAD
```

For every file changed, read the actual hunk and check:
- Does it actually advance the AC? (not just touch code)
- Are the new tests covered? (does `tests/` get exercised?)
- Any obvious bug — wrong type, off-by-one, missing null check, leaked secret pattern?
- Any new TODO / FIXME / "later" comment? (L4 forbids these in committed code)

Do NOT review for security (no secrets scan, no injection patterns, no auth bypass) — that's the full kit. Do NOT review for performance / style — those are out of scope for the lite kit's correctness gate.

### Step 3 — Post the verdict

Post a single PR comment in this format (do NOT set a commit status — that's a separate GitHub Action):

```markdown
## /dev-kit-lite:review

**Verdict:** Approve | Changes Requested | Blocked

**AC traceability:**
- AC-1: satisfied — <file:line evidence>
- AC-2: NOT satisfied — <reason>
- AC-3: satisfied — <file:line evidence>

**Findings (correctness only):**
- `apps/web/checkout.ts:42` — `parseInt(x)` without radix → off-by-one on hex strings
- `tests/test_x.py:18` — assertion missing; the test passes trivially

**L4 check (no TODO / FIXME in committed code):**
- PASS | FAIL — <reason>
```

The verdict is **advisory only**. `continue-on-error: true` on the `dev-kit-lite review (advisory)` GitHub Action means merge proceeds even on red. Speed > gating.

### Step 4 — Return

Return the verdict to the calling session. Do not block; do not loop; do not re-review unless explicitly asked.

## Validation gates

- Verdict posted as a PR comment (not a commit status)
- Each AC has a file:line citation OR an explicit "not satisfied" reason
- L4 check ran (no TODO / FIXME / "later")
- Findings (if any) reference file:line

## Iron Laws

- **L2** (verification before completion) — every AC citation points to a file:line you actually read
- **L3** (evidence before claim) — never post "Approve" without an AC traceability table
- **L4** (no TODO in committed code) — surface TODO / FIXME / "later" findings explicitly
- **L5** (one answer per question) — single verdict, not a back-and-forth

## Anti-patterns

- ❌ Posting a generic "looks good" without AC traceability
- ❌ Setting a commit status (that's the GitHub Action's job)
- ❌ Reviewing for security / performance / style — out of scope
- ❌ Looping back to re-review after the user replies — single pass per invocation
- ❌ Blocking the merge — review is advisory

## Next step

- Verdict = Approve → run `/dev-kit-lite:build-verify` to close out the step
- Verdict = Changes Requested → role-owner addresses findings, push a fix, re-invoke `/dev-kit-lite:review`
- Verdict = Blocked → escalate to PM via `reassign` or `plan-update`
