# CLAUDE.md — dev-harness-kit-lite

Minimal pointer. Detailed content lives in linked index files.

## References

- **Iron Laws** → [`iron-laws/index.md`](iron-laws/index.md) (L1–L5 + L5-R non-overlap)
- **Rules** → [`rules/index.md`](rules/index.md) (git-workflow, team-collab, role specs)
- **Hook matrix** → [`hooks/index.md`](hooks/index.md) (state in `.dev-kit/.active-hooks.json`)
- **Skills** → [`skills/README.md`](skills/README.md) (7 skills for 4-hour MVP)
- **Hand-off** → `.dev-kit/hand-off/`
- **Dual-runtime (Claude Code ↔ Codex CLI)** → [`.codex/README.md`](.codex/README.md)

> Regenerate via `/dev-kit-lite:bootstrap`. Manual edits here will be overwritten.

## Worktree rule (Claude Code + Codex)

The `.worktree/`-per-task rule in [`rules/git-workflow.md`](rules/git-workflow.md) is enforced **identically on both runtimes**:

- `hooks/worktree-guard.sh` is wired into `hooks/hooks.json` (Claude) and `.codex/hooks.json` (Codex) with `DEV_KIT_AGENT=<runtime>` so log attribution works.
- Either runtime started in the main checkout will be denied any Edit/Write until you `git worktree add -b <type>/<slug> .worktrees/<slug> origin/main` and re-open the session there.
- Codex entry point: see [`.codex/README.md`](.codex/README.md).
