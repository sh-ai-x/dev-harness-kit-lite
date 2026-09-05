#!/usr/bin/env bash
# Cleanup-safe `git worktree remove` wrapper for dev-kit-lite.
#
# Lite version — drops the per-worktree logs/ archival step from
# dev-harness-kit's wrapper (lite has no AGENT_LOG_ROOT retention
# requirement). Adds a safety check: refuses to remove the main
# checkout, and prompts unless --yes is passed.
#
# Usage:
#   bin/worktree-remove-safe.sh <worktree_path> [-- git-worktree-remove-args...]
#   bin/worktree-remove-safe.sh --yes <worktree_path>
#
# Examples:
#   bin/worktree-remove-safe.sh /path/to/repo/.worktrees/feat-x
#   bin/worktree-remove-safe.sh /path/to/repo/.worktrees/feat-x -- --force
#   bin/worktree-remove-safe.sh --yes /path/to/repo/.worktrees/feat-x

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel 2>/dev/null)" || {
  echo "error: worktree-remove-safe.sh must live inside a git repo" >&2
  exit 1
}

YES=0
if [[ "${1:-}" == "--yes" ]]; then
  YES=1
  shift
fi

if [[ $# -lt 1 ]]; then
  cat <<EOF >&2
usage: $(basename "$0") [--yes] <worktree_path> [-- git-worktree-remove-args...]

Safely removes a registered worktree. Refuses to remove the main
checkout. Pass --yes to skip the confirmation prompt.
EOF
  exit 64
fi

WORKTREE_PATH="$1"
shift

# Anything after `--` is forwarded to git worktree remove verbatim.
GW_ARGS=()
if [[ "${1:-}" == "--" ]]; then
  shift
  GW_ARGS=("$@")
fi

# Resolve to absolute path so the safety check is unambiguous.
case "$WORKTREE_PATH" in
  /*) WT_ABS="$WORKTREE_PATH" ;;
  *)  WT_ABS="$PWD/$WORKTREE_PATH" ;;
esac

MAIN_ABS="$(git -C "$REPO_ROOT" rev-parse --show-toplevel)"
if [[ "$WT_ABS" == "$MAIN_ABS" ]]; then
  echo "error: refusing to remove the main checkout ($WT_ABS)" >&2
  exit 2
fi

# Verify the path is a registered worktree before asking git.
if ! git -C "$REPO_ROOT" worktree list --porcelain | grep -qF "worktree $WT_ABS"; then
  echo "error: $WT_ABS is not a registered worktree" >&2
  exit 2
fi

if [[ "$YES" -eq 0 && -t 0 ]]; then
  printf "Remove worktree %s? [y/N] " "$WT_ABS"
  read -r confirm
  case "${confirm,,}" in
    y|yes) ;;
    *)     echo "Aborted."; exit 2 ;;
  esac
fi

# Defensive `--` so a path starting with `--` is not interpreted as
# a git flag.
git -C "$REPO_ROOT" worktree remove -- "$WT_ABS" "${GW_ARGS[@]}"
