#!/usr/bin/env bash
# Count worktrees, list them oldest-first, and remove the N oldest on demand.
#
# Companion slash command: /worktree-prune. The slash command is a thin
# wrapper that forwards here; this script owns the actual logic.
#
# What it does, in order:
#   1. `python3 -m lib.worktree_prune --repo <root>` — JSON candidate
#      list (excludes main checkout + detached-HEAD).
#   2. `python3 -m lib.worktree_prune --repo <root> --table` — audit
#      table reusing the same Python call.
#   3. Read N from stdin (interactive) or accept positionally.
#   4. `python3 -m lib.worktree_prune --repo <root> --table --head N`
#      renders the would-be-removed slice in the same format.
#   5. Final y/N gate, then per-row `bin/worktree-remove-safe.sh <path>`.
#
# Pruned from dev-harness-kit's bin/worktree-prune.sh — drops the
# `worktree-janitor` cross-link and the per-worktree log archive
# (lite has no telemetry retention requirement).
#
# Flags:
#   -y, --yes       Skip the final y/N gate (CI / batch mode).
#   -n, --dry-run   Print what would be removed; never mutate.
#   -k, --keep N    Keep exactly N newest worktrees (selects the
#                   TOTAL-N oldest for removal). Mutually exclusive with
#                   positional N.
#   -h, --help      Show usage and exit 0.
#
# Exit codes:
#   0   Removed (or nothing selected, or dry-run completed).
#   1   Invalid CLI / runtime error.
#   2   User aborted at the y/N gate.
#   3   At least one removal failed (partial success).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel)"
SAFE_REMOVE="$SCRIPT_DIR/worktree-remove-safe.sh"

# --- arg parsing ---------------------------------------------------------

YES=0
DRY_RUN=0
KEEP=0
POSITIONAL=()

usage() {
  sed -n '2,/^set -euo pipefail/p' "${BASH_SOURCE[0]}" \
    | sed -e '$d' -e 's/^# \{0,1\}//' \
    | awk 'NF'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes)     YES=1; shift ;;
    -n|--dry-run) DRY_RUN=1; shift ;;
    -k|--keep)    KEEP="${2:-}"; shift 2 || { echo "error: --keep needs an integer" >&2; exit 1; } ;;
    -h|--help)    usage ;;
    --)           shift; POSITIONAL+=("$@"); break ;;
    -*)           echo "error: unknown flag $1 (try --help)" >&2; exit 1 ;;
    *)            POSITIONAL+=("$1"); shift ;;
  esac
done

if [[ "$KEEP" -gt 0 && ${#POSITIONAL[@]} -gt 0 ]]; then
  echo "error: --keep and a positional count are mutually exclusive" >&2
  exit 1
fi

SELECT_COUNT=0
if [[ "$KEEP" -gt 0 ]]; then
  :  # resolved below once total is known
elif [[ ${#POSITIONAL[@]} -gt 0 ]]; then
  SELECT_COUNT="${POSITIONAL[0]}"
  if ! [[ "$SELECT_COUNT" =~ ^[0-9]+$ ]]; then
    echo "error: count must be a non-negative integer, got '$SELECT_COUNT'" >&2
    exit 1
  fi
fi

# --- candidate list ------------------------------------------------------

JSON_OUT="$(python3 -m lib.worktree_prune --repo "$REPO_ROOT")"
TOTAL="$(printf '%s' "$JSON_OUT" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")"

if [[ -z "$TOTAL" || "$TOTAL" -eq 0 ]]; then
  echo "No removable worktrees (only the main checkout is registered)."
  exit 0
fi

TABLE_OUT="$(python3 -m lib.worktree_prune --repo "$REPO_ROOT" --table)"
printf '%s\n' "$TABLE_OUT"
echo

# Resolve --keep into a count.
if [[ "$KEEP" -gt 0 ]]; then
  if [[ "$KEEP" -ge "$TOTAL" ]]; then
    echo "--keep $KEEP >= $TOTAL removable worktrees; nothing to prune."
    exit 0
  fi
  SELECT_COUNT=$((TOTAL - KEEP))
  echo "Selection: --keep $KEEP -> removing the $SELECT_COUNT oldest."
elif [[ ${#POSITIONAL[@]} -eq 0 ]]; then
  if [[ -t 0 && "$YES" -eq 0 && "$DRY_RUN" -eq 0 ]]; then
    read -r -p "How many oldest worktrees to remove? (0-${TOTAL}, q to quit) " answer
    case "${answer,,}" in
      q|quit|"") SELECT_COUNT=0 ;;
      *)        SELECT_COUNT="$answer" ;;
    esac
    if ! [[ "$SELECT_COUNT" =~ ^[0-9]+$ ]]; then
      echo "error: count must be a non-negative integer, got '$SELECT_COUNT'" >&2
      exit 1
    fi
  fi
fi

if [[ "$SELECT_COUNT" -eq 0 ]]; then
  echo "Nothing selected -- exiting."
  exit 0
fi

if [[ "$SELECT_COUNT" -gt "$TOTAL" ]]; then
  echo "error: requested $SELECT_COUNT, only $TOTAL removable worktrees available" >&2
  exit 1
fi

# --- selected list + confirm --------------------------------------------

SELECTED_TABLE="$(python3 -m lib.worktree_prune --repo "$REPO_ROOT" --table --head "$SELECT_COUNT")"

echo
echo "Will remove the following $SELECT_COUNT oldest worktree(s):"
echo
printf '%s\n' "$SELECTED_TABLE" | tail -n +3 | while IFS= read -r line; do
  printf '  %s\n' "$line"
done
echo

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "(dry-run: no changes made)"
  exit 0
fi

if [[ "$YES" -eq 0 && -t 0 ]]; then
  read -r -p "Proceed? [y/N] " confirm
  case "${confirm,,}" in
    y|yes) ;;
    *)     echo "Aborted."; exit 2 ;;
  esac
fi

mapfile -t SELECTED < <(printf '%s' "$JSON_OUT" | python3 -c "
import json, sys
n = int(sys.argv[1])
for r in json.load(sys.stdin)[:n]:
    print(r['path'])
" "$SELECT_COUNT")

fail_count=0
for path in "${SELECTED[@]}"; do
  echo "-> removing: $path"
  if ! "$SAFE_REMOVE" "$path"; then
    echo "  ! removal failed: $path" >&2
    fail_count=$((fail_count + 1))
  fi
done

if [[ "$fail_count" -gt 0 ]]; then
  echo
  echo "$fail_count removal(s) failed. Remaining worktrees:"
  git -C "$REPO_ROOT" worktree list
  exit 3
fi

echo
echo "Done. $SELECT_COUNT worktree(s) removed."
git -C "$REPO_ROOT" worktree list | wc -l | awk '{print "Remaining worktree count: " $1}'
