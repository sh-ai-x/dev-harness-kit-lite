#!/usr/bin/env bash
# stop-verify.sh — lite version. Enforces L3 (no "done" without quoted exit code + test count).
#
# Stop hook. Reads the session's last assistant transcript; if it contains
# phrases like "done", "finished", "passing", "completed", and the most recent
# step has no `.dev-kit/verify/<step>.json`, refuses to allow Stop.

set -uo pipefail
INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  # Fail open with warning — stop hook failing closed blocks the user
  echo "::warning::jq missing; stop-verify.sh cannot enforce L3"
  exit 0
fi

TRANSCRIPT="$(printf '%s' "$INPUT" | jq -r '.transcript // ""' 2>/dev/null)"

# Only check if transcript looks like a "done" claim
if ! echo "$TRANSCRIPT" | grep -qiE '(\bdone\b|\bfinished\b|\bpassing\b|\bcompleted\b|all green|all tests pass|ship it)'; then
  exit 0
fi

# Determine current step from the most recent verify dir
VERIFY_DIR=".dev-kit/verify"
if [ ! -d "$VERIFY_DIR" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"Stop","permissionDecision":"deny","permissionDecisionReason":"L3 EVIDENCE GATE: no .dev-kit/verify/ directory yet. Run /dev-kit-lite:build-verify before claiming done."}}\n' >&2
  exit 2
fi

LATEST_JSON="$(ls -t "$VERIFY_DIR"/*.json 2>/dev/null | grep -v role.json | head -1)"
if [ -z "$LATEST_JSON" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"Stop","permissionDecision":"deny","permissionDecisionReason":"L3 EVIDENCE GATE: no verify JSON for current step. Run /dev-kit-lite:build-verify <stepN> first."}}\n' >&2
  exit 2
fi

# Check the latest verify has exit_code=0 + test_count>=1
EXIT_CODE="$(jq -r '.exit_code // 1' "$LATEST_JSON" 2>/dev/null)"
TEST_COUNT="$(jq -r '.test_count // 0' "$LATEST_JSON" 2>/dev/null)"

if [ "$EXIT_CODE" != "0" ] || [ "$TEST_COUNT" -lt 1 ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"Stop","permissionDecision":"deny","permissionDecisionReason":"L3 EVIDENCE GATE: latest verify %s shows exit_code=%s test_count=%s. Re-run /dev-kit-lite:build-verify to get a clean result."}}\n' "$LATEST_JSON" "$EXIT_CODE" "$TEST_COUNT" >&2
  exit 2
fi

exit 0
