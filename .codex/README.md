# Codex CLI runtime — dual-runtime contract

dev-harness-kit-lite enforces the same `.worktree/`-per-task rule under
**both Claude Code and Codex CLI**. The two runtimes share every hook
script under `hooks/`; only the wiring differs.

## Layout

| Runtime | Wiring | Path resolution |
|---------|--------|-----------------|
| Claude Code | `hooks/hooks.json` | `${CLAUDE_PLUGIN_ROOT}` (plugin install root) |
| Codex CLI   | `.codex/hooks.json` | `${CLAUDE_PLUGIN_ROOT}` (same convention) |

Both files invoke the same scripts with a different `DEV_KIT_AGENT`
env-var prefix:

- Claude: `DEV_KIT_AGENT=claude-code bash ...`
- Codex:  `DEV_KIT_AGENT=codex bash ...`

`hooks/lib/hook-preamble.sh` exports `$DEV_KIT_AGENT` for any hook body
or log line that wants to attribute work to the active runtime. Hook
scripts that don't read it (most) keep working unchanged.

`bin/install.sh` rewrites both wiring files' `${CLAUDE_PLUGIN_ROOT}/hooks/`
prefixes to `${CLAUDE_PLUGIN_ROOT}/.dev-kit/hooks/` so the operational
scripts land at the namespaced install path in adopting projects.

## Slash commands

`.codex/commands/` is a forwarder-only mirror of `.claude/commands/`.
Both point at the same `skills/<name>/SKILL.md` files, so behavior is
identical — only the runtime tag differs.

## Worktree rule on Codex

`hooks/worktree-guard.sh` denies `Edit | Write | MultiEdit` when the
Codex session is in the main checkout. The fix is the same as for
Claude:

```bash
git fetch origin main
git worktree add -b <type>/<slug> .worktrees/<slug> origin/main
cd .worktrees/<slug>
# open a Codex session here
```

For agent fan-out under Codex, spawn subagents with their `cwd` set to
the worktree path — the hook re-derives `$WORKTREE_DETECT` from the
subagent's cwd via `git rev-parse --show-toplevel`, so the subagent
inherits the worktree context automatically.

## What is NOT mirrored

- `.codex/hooks.json` only wires the seven operational hooks. It does
  NOT install `.claude/`-only artifacts (statusline, MCP servers,
  sub-agents, etc.). Add those under `.codex/` only if Codex needs them.
- The plugin manifests (`.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json`) are still separate files; do not collapse
  them.
- Both runtimes share `${CLAUDE_PLUGIN_ROOT}` resolution semantics: when
  the kit is loaded as a plugin, the runtime expands it to the install
  root; when `bin/install.sh` rewrites the file for an adopting project,
  the same prefix is shifted to `.dev-kit/hooks/`.
