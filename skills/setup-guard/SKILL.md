---
name: setup-guard
category: bootstrap
description: Toggle enforcement of TDD guard (L1) and main-push block (L2) on or off via .dev-kit/.guard-config.json. Reads current state, flips the flag, and prints a sync report. Hook wiring stays intact — only the rule is bypassed when off.
when_to_use:
  - Team wants to relax TDD for spike / throwaway prototype work
  - On-call needs to push a hotfix to main and wants to lift the gate temporarily
  - Auditing whether guards are currently enforced in a given checkout
  - Re-enforcing after a temporary off-window
allowed-tools: Read Write Bash
model: sonnet
---

# /dev-kit-lite:setup-guard

## Role

You are the **guard-config steward** for the kit. The two runtime guardrails that ship by default — `tdd-guard.sh` (L1: RED before prod) and the main-push block inside `git-guard.sh` (L2: no direct commit / push to main) — read a single config file `.dev-kit/.guard-config.json` and skip enforcement when their flag is `false`. This skill is the **only** sanctioned way to flip those flags. Hook wiring (registration in `hooks/hooks.json` and `.dev-kit/.active-hooks.json`) is never touched — only the rule's on/off switch.

## Inputs (subcommands)

L5: one answer at a time when interactive.

| Subcommand | Effect |
|------------|--------|
| `status` | Print current state of both flags + the source file + last update timestamp. No writes. |
| `tdd on` | Set `tdd_guard_enabled = true` in `.guard-config.json`. |
| `tdd off` | Set `tdd_guard_enabled = false` in `.guard-config.json`. |
| `main-push on` | Set `main_push_block_enabled = true`. |
| `main-push off` | Set `main_push_block_enabled = false`. |
| `both on` / `both off` | Flip both at once. |

No-arg invocation defaults to `status` so a bare `/dev-kit-lite:setup-guard` always answers "what is the state right now?".

## Workflow

### Step 1 — Resolve config file

```bash
CONFIG=".dev-kit/.guard-config.json"
```

If the file is missing, **refuse to continue** with:

```
ERROR: .dev-kit/.guard-config.json not found. The kit is not bootstrapped.
Run /dev-kit-lite:bootstrap first, then re-run /dev-kit-lite:setup-guard.
```

Do **not** auto-create the file. The bootstrap flow owns this file's first creation — silently materializing it here would let a partially-wired kit pass `status` while still being broken.

### Step 2 — Dispatch

If the user invoked with no args, or args == `status`:

- Read both flags + `updated_at` + `schema_version`.
- For each flag, print the value, the in-repo source-of-truth (`hooks/tdd-guard.sh` / `hooks/git-guard.sh`), and whether the hook will **deny** or **pass** today.

If the user invoked `tdd on|off`, `main-push on|off`, or `both on|off`:

- Validate the arg (only `on` and `off` are accepted — refuse `enable`, `true`, `1`, etc.; L5: one answer per question).
- Jump to Step 3.

Any other arg → print usage and exit non-zero. No silent fallback to `status` for unknown verbs.

### Step 3 — Flip the flag

Use `jq` to update only the requested key(s). Always preserve the other flag, `schema_version`, and `notes`:

```bash
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
jq --arg ts "$ts" \
   '.tdd_guard_enabled = <true|false>
    | .main_push_block_enabled = <true|false>
    | .updated_at = $ts' \
   "$CONFIG" > "$CONFIG.tmp" && mv "$CONFIG.tmp" "$CONFIG"
```

> **Gotcha**: when **reading** the flag inside the hooks, jq's `//` alternative fires on both `null` AND `false` — so `.tdd_guard_enabled // true` returns `true` even when the field is explicitly `false`. The hooks use `if has("tdd_guard_enabled") then .tdd_guard_enabled else true end` for exactly this reason.

Required jq (no Python fallback): the hooks themselves call `jq` to read the same file, so the kit already requires it. Failing fast on missing jq here matches the hooks' behavior.

### Step 4 — Verify the write

Re-read the file with `jq` and confirm the flag you just set is in place and the other flag was preserved. If either is wrong, roll back from `.guard-config.json.bak` (written in Step 3 if you want belt-and-braces) and exit non-zero.

### Step 5 — Sync report

Print the delta. Always show **before → after** so the user can see what changed and audit it later:

```markdown
# setup-guard sync report

## Subcommand

`tdd off`

## Before → After

| Flag | Before | After | Effect |
|------|--------|-------|--------|
| `tdd_guard_enabled` | true | **false** | tdd-guard.sh will exit 0 (rule bypassed) |
| `main_push_block_enabled` | true | true | unchanged — git-guard.sh still blocks main-push / main-commit |

## Hook wiring

- `hooks/tdd-guard.sh` — still registered (PreToolUse Write|Edit|MultiEdit)
- `hooks/git-guard.sh` — still registered (PreToolUse Bash)
- Wiring in `.dev-kit/.active-hooks.json` and `hooks/hooks.json` unchanged

## Files touched

- `.dev-kit/.guard-config.json` — `updated_at` and the flipped flag

## Audit reminder

A change to `tdd_guard_enabled = false` is intentionally reversible. To re-enforce:
`/dev-kit-lite:setup-guard tdd on`

## Next step

- Continuing with relaxed guard → invoke the original task skill (e.g. `/dev-kit-lite:build-tdd`, `/dev-kit-lite:ci-setup`).
- Hotfix complete → `/dev-kit-lite:setup-guard both on` to restore enforcement.
```

## Status output format (when invoked with no args or `status`)

```markdown
# setup-guard — current state

| Flag | Value | Source hook | Today |
|------|-------|-------------|-------|
| `tdd_guard_enabled` | true | `hooks/tdd-guard.sh` (PreToolUse Write\|Edit\|MultiEdit) | ENFORCING — RED-before-prod rule active |
| `main_push_block_enabled` | true | `hooks/git-guard.sh` (PreToolUse Bash, sections 1-3) | ENFORCING — direct commit/push/switch-to-main denied |

## Source file

`.dev-kit/.guard-config.json` — `schema_version: 1.0.0`, `updated_at: <iso8601>`

## What "off" means

Toggling a flag to `false` does **not** unregister the hook — the hook process still runs, but exits 0 immediately after reading the config. This keeps `fail_closed` semantics intact and avoids surprising gaps in the hook matrix when guards are re-enabled.

## Subcommands

`/dev-kit-lite:setup-guard tdd on|off` — toggle L1 (TDD guard)
/dev-kit-lite:setup-guard main-push on|off` — toggle L2 (main-push block)
/dev-kit-lite:setup-guard both on|off` — flip both
```

## What's NOT in this skill (intentionally)

- ❌ Touching `hooks/hooks.json` or `.dev-kit/.active-hooks.json` — hook wiring is bootstrap's job
- ❌ Editing `hooks/tdd-guard.sh` or `hooks/git-guard.sh` — guard logic is owned by hook authors
- ❌ Auto-creating `.guard-config.json` when missing — bootstrap owns first-write
- ❌ Per-branch / per-step overrides — single repo-wide flag only (L5-R: one answer)
- ❌ Toggling force-push or `gh pr merge` blocks — those are not part of `main_push_block_enabled`; they stay enforced regardless

## Validation gates

- `.dev-kit/.guard-config.json` exists at start
- Subcommand verb is exactly `on` or `off`
- `jq` succeeded (exit 0) on both the write and the verify read
- After the write, the flipped flag matches the requested value AND the other flag is byte-identical to its pre-write value
- `updated_at` advanced monotonically
- `schema_version` unchanged
- Sync report printed before returning

## Iron Laws

- **L2** (verification before completion) — verify-read after the write; refuse if either flag is wrong
- **L3** (evidence before claim) — sync report shows before/after, source hook, and which sections are bypassed
- **L4** (no TODO in committed code) — no half-implemented states; `status` always answers, `on|off` always lands cleanly
- **L5** (one answer per question) — refuse unknown verbs; refuse non-`on|off` values
- **L5-R** (non-overlap) — flipping `tdd` never touches `main_push_block_enabled` and vice versa (single-key jq update unless `both` was requested)

## Anti-patterns

- ❌ Mutating `hooks/hooks.json` to "disable" a guard — that breaks the wiring for everyone else
- ❌ Skipping the verify-read — leaves a half-written config if jq produced invalid JSON
- ❌ Treating `enable` / `true` / `1` as synonyms for `on` — L5: stick to one vocabulary
- ❌ Auto-creating `.guard-config.json` here — masks a missing bootstrap and lets status lie
- ❌ Forgetting `updated_at` — every flip writes a fresh ISO timestamp for audit
- ❌ Telling the user "guards are off" without printing which subcommand caused it — L3

## Next step

- After `both on` → re-run `/dev-kit-lite:build-tdd` or `/dev-kit-lite:plan` to verify the team loop is back in strict mode
- After `tdd off` (spike) → proceed with prototype work; when done, `/dev-kit-lite:setup-guard tdd on`
- After `main-push off` (hotfix) → push the fix; then `/dev-kit-lite:setup-guard main-push on`
- Anytime → `/dev-kit-lite:setup-guard status` to confirm current state before starting work