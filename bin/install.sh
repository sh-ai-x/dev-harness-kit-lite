#!/usr/bin/env bash
# install.sh — fresh-repo installer for dev-harness-kit-lite.
#
# Refuses to run if the target directory already has package.json,
# requirements.txt, or pyproject.toml (lite v0.1.0 is greenfield-only).
#
# Usage:
#   bash /path/to/dev-harness-kit-lite/bin/install.sh /path/to/new-project

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "usage: $0 <target-dir>" >&2
  echo "  target-dir must be empty or a fresh 'git init'-ed directory" >&2
  exit 2
fi

TARGET="$1"
TARGET="$(cd "$TARGET" && pwd)"  # canonicalize

# Pre-flight: refuse if existing project markers exist
if [ -f "$TARGET/package.json" ] || [ -f "$TARGET/requirements.txt" ] || [ -f "$TARGET/pyproject.toml" ]; then
  echo "ERROR: existing project files detected in $TARGET" >&2
  echo "  dev-kit-lite v0.1.0 is fresh-repo only." >&2
  echo "  Remove package.json / requirements.txt / pyproject.toml and retry," >&2
  echo "  or wait for v0.2 which will support an --import flag." >&2
  exit 1
fi

# Pre-flight: refuse if non-empty git history exists (not just git init)
if [ -d "$TARGET/.git" ]; then
  COMMIT_COUNT="$(git -C "$TARGET" rev-list --count --all 2>/dev/null || echo 0)"
  if [ "$COMMIT_COUNT" -gt 0 ]; then
    echo "ERROR: $TARGET/.git already has $COMMIT_COUNT commit(s)" >&2
    echo "  dev-kit-lite v0.1.0 is fresh-repo only." >&2
    exit 1
  fi
fi

KIT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Scaffold: copy the kit contents into the target
echo "Installing dev-harness-kit-lite into $TARGET ..."
mkdir -p "$TARGET"

# Copy files (preserve structure)
for entry in CLAUDE.md AGENTS.md README.md CHANGELOG.md .gitignore \
             iron-laws rules skills templates lib tests \
             .claude-plugin .codex-plugin .claude .codex; do
  if [ -e "$KIT_ROOT/$entry" ]; then
    cp -R "$KIT_ROOT/$entry" "$TARGET/$entry"
  fi
done

# The kit's operational hook scripts install under .dev-kit/hooks/ in the
# adopting project. Project-root hooks/ is reserved for the app's own custom
# hooks (React/Vue composables) and is never written to by the kit.
mkdir -p "$TARGET/.dev-kit"
rm -rf "$TARGET/.dev-kit/hooks"
cp -R "$KIT_ROOT/hooks" "$TARGET/.dev-kit/hooks"

# Re-point plugin-root-relative hook paths at the namespaced location.
# Includes .codex/hooks.json (Codex CLI mirror, v0.1.8) so the DEV_KIT_AGENT=codex
# wiring gets rewritten alongside the Claude Code side.
for cfg in "$TARGET/.claude/settings.json" "$TARGET/.codex/settings.json" \
           "$TARGET/.dev-kit/hooks/hooks.json" "$TARGET/.codex/hooks.json"; do
  [ -f "$cfg" ] || continue
  sed -i.bak 's#${CLAUDE_PLUGIN_ROOT}/hooks/#${CLAUDE_PLUGIN_ROOT}/.dev-kit/hooks/#g' "$cfg"
  rm -f "$cfg.bak"
done

# Re-create AGENTS.md as a symlink (cp -R preserves the source as a file)
ln -sf CLAUDE.md "$TARGET/AGENTS.md"

# Write .dev-kit/.active-hooks.json
mkdir -p "$TARGET/.dev-kit"
cat > "$TARGET/.dev-kit/.active-hooks.json" <<JSON
{
  "schema_version": "1.0.0",
  "phase": "bootstrap",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hooks": {
    "PreToolUse:Write|Edit|MultiEdit": ["worktree-guard.sh", "tdd-guard.sh", "destructive-confirm.sh"],
    "PreToolUse:Bash": ["git-guard.sh", "destructive-confirm.sh"],
    "PostToolUse:Write|Edit|MultiEdit": ["secret-scan.sh"],
    "SessionStart": ["session-start-check.sh"],
    "Stop": ["stop-verify.sh"]
  }
}
JSON

# git init + first commit if not already a repo
if [ ! -d "$TARGET/.git" ]; then
  (cd "$TARGET" && git init -q && git add -A && git -c user.email=lite@dev-kit-lite -c user.name=dev-kit-lite commit -q -m "chore(bootstrap): scaffold dev-harness-kit-lite v0.1.0")
  echo "Initialized fresh git repo with bootstrap commit."
else
  (cd "$TARGET" && git add -A && git -c user.email=lite@dev-kit-lite -c user.name=dev-kit-lite commit -q -m "chore(bootstrap): scaffold dev-harness-kit-lite v0.1.0" --allow-empty)
  echo "Bootstrap commit added to existing repo."
fi

cat <<MSG

✅ dev-harness-kit-lite installed at: $TARGET

Next steps:
  cd $TARGET
  git worktree add -b plan/mvp-v0 .worktrees/mvp-v0 origin/main
  cd .worktrees/mvp-v0
  /dev-kit-lite:plan "<your 1-line MVP goal>"

See README.md for the full 6-stage loop.
MSG
