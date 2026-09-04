#!/usr/bin/env bash
# tdd-guard.sh — lite version (no scope-judge dep).
#
# PreToolUse hook for Write|Edit|MultiEdit. Enforces L1 (no prod code
# without a failing test) by reading `.dev-kit/.tdd-cycle.json`.
#
# States:
#   phase == "red"      → expecting failing test → allow test-file Edit, deny prod-code Edit
#   phase == "green"    → expecting prod-code Edit to make test pass → allow, but require prior red logged
#   phase == "refactor" → allow all (refactor must keep tests green; we trust the dev)
#   phase == "" or no JSON → refuse all prod-code Edit until first /dev-kit-lite:build-tdd invocation
#
# Fails CLOSED when jq is missing.

set -uo pipefail
INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"TDD GUARD: jq is required. Install jq (apt/brew/apk). The TDD rule cannot be enforced without it."}}\n' >&2
  exit 2
fi

# m6: respect .dev-kit/.guard-config.json — tdd_guard_enabled=false → bypass.
# fail_closed wiring stays intact; only the L1 rule is skipped. toggle via
# /dev-kit-lite:setup-guard.
# NOTE: jq's `//` alternative fires on null OR false (unlike most langs), so
# `// true` would return true even when the field is explicitly false. Use
# has() to default only when the key is missing.
GUARD_CONFIG=".dev-kit/.guard-config.json"
if [ -f "$GUARD_CONFIG" ]; then
  TDD_ENABLED="$(jq -r 'if has("tdd_guard_enabled") then .tdd_guard_enabled else true end' "$GUARD_CONFIG" 2>/dev/null)"
  if [ "$TDD_ENABLED" = "false" ]; then
    exit 0
  fi
fi

FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)"
[ -z "$FILE_PATH" ] && exit 0

# Test files always allowed (any phase)
case "$FILE_PATH" in
  *_test.*|*test_*.py|*tests/*|*test/*|*.test.*|*.spec.*)
    exit 0
    ;;
esac

# Harness/guard config files always allowed (any phase). These are plain
# data files with no associated test suite — gating them behind RED/GREEN
# evidence creates a chicken-and-egg problem (the guard-config bypass file
# itself becomes unreachable without first satisfying the guard it exists
# to bypass) and forces contributors to script around this hook via raw
# Bash file writes instead of the Write/Edit tools. See issue #15.
case "$FILE_PATH" in
  */.dev-kit/.guard-config.json|.dev-kit/.guard-config.json|*/.claude/settings.json|.claude/settings.json|*/.claude/settings.local.json|.claude/settings.local.json)
    exit 0
    ;;
esac

# Read TDD cycle state
TDD_JSON=".dev-kit/.tdd-cycle.json"
PHASE=""
EXIT_CODE=""
if [ -f "$TDD_JSON" ]; then
  PHASE="$(jq -r '.phase // ""' "$TDD_JSON" 2>/dev/null)"
  EXIT_CODE="$(jq -r '.last_exit_code // ""' "$TDD_JSON" 2>/dev/null)"
fi

case "$PHASE" in
  red)
    # In RED phase, only test files allowed (handled above). Prod code = deny.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"TDD GUARD: in RED phase. Write the failing test first, run it (must fail), then transition to GREEN. Run: python3 -m lib.tdd_cycle green -- <prod-code-edit>"}}\n' >&2
    exit 2
    ;;
  green|"")
    # GREEN phase requires a prior RED logged with failing exit code
    if [ -z "$EXIT_CODE" ] || [ "$EXIT_CODE" = "0" ]; then
      printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"TDD GUARD: RED evidence required before prod-code edit. Run the failing test first: python3 -m lib.tdd_cycle red -- <test command>"}}\n' >&2
      exit 2
    fi
    exit 0
    ;;
  refactor)
    # Refactor allows edits; build-verify will confirm tests still pass
    exit 0
    ;;
  *)
    # Unknown phase — fail closed
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"TDD GUARD: .dev-kit/.tdd-cycle.json has invalid phase=%s. Reset via python3 -m lib.tdd_cycle reset"}}\n' "$PHASE" >&2
    exit 2
    ;;
esac
