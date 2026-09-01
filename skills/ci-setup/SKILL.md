---
name: ci-setup
category: bootstrap
description: Install ONE file — .github/workflows/review.yml — advisory-only, never blocks merge.
when_to_use:
  - After plan, before build-tdd (optional — speed > gating)
  - When the team wants a PR-comment-only review verdict
allowed-tools: Read Write Bash
model: sonnet
---

# /dev-kit-lite:ci-setup

## Workflow

Installs **exactly one file**: `.github/workflows/review.yml`. Nothing else.

The workflow:
- Triggers on `pull_request` (any branch → main)
- Runs `/dev-kit-lite:review` and posts the verdict as a PR comment
- Sets `continue-on-error: true` on every job → **never blocks merge**
- Branch protection should mark the check as "advisory" (not required)

## Step 1 — Check idempotency

If `.github/workflows/review.yml` already exists, ask the user: "Overwrite? [y/N]". Default = no.

## Step 2 — Write `review.yml`

```yaml
name: dev-kit-lite review (advisory)
on:
  pull_request:
    branches: [main]

jobs:
  review:
    runs-on: ubuntu-latest
    continue-on-error: true   # ADVISORY: never blocks merge
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Run /dev-kit-lite:review
        uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Run /dev-kit-lite:review on this PR.
            Post the verdict as a PR comment.
            Do NOT set a commit status; the verdict is advisory only.
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Step 3 — Optional branch protection advice

Print (do not auto-apply):

```
To mark the check as advisory:
  GitHub repo → Settings → Branches → main → Require status checks
  → Add "review" but UNCHECK "Require branches to be up to date before merging"

This way the green/red is informational; merge works on red.
```

## Validation gates

- `.github/workflows/review.yml` exists
- `continue-on-error: true` is set on the `review` job
- No other CI files were created (this skill does NOT install `ci.yml`, `lint.yml`, `test.yml`, `auto-fix.yml`)

## Iron Laws

- L5 (one answer per question) — overwrite prompt
- L2 (no edit on main) — operator must be in a worktree (ci-setup writes `.github/workflows/`)

## What's NOT installed (intentionally)

- ❌ `ci.yml` — no lint/test/build CI (use local `build-verify` instead)
- ❌ `lint.yml` — lint is local
- ❌ `test.yml` — tests are local
- ❌ `auto-fix.yml` — no babysit loop (team fixes forward manually)
- ❌ `security.yml` — security excluded by design

## Next step

```
/dev-kit-lite:build-tdd
```
