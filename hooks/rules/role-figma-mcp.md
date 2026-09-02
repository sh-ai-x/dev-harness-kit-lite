# role-figma-mcp

## Headcount
- **n people** (default 1)

## Owns
- `design/` (Figma export bundles — SVG / PNG / JSON)
- `tokens/` (design tokens — colors, type, spacing, components)
- `figma-export/` (Figma MCP output cache)
- `screenshots/` (visual regression baselines)

## Branch format
- `feat/design-<owner>-<slug>` — e.g. `feat/design-eve-tokens`
- `fix/design-<owner>-<slug>` — e.g. `fix/design-eve-color-contrast`

## Worktree root
- `.worktrees/design-<owner>` — e.g. `.worktrees/design-eve`

## Non-overlap iron rule (L5-R)
- One design person = at most ONE in-flight step
- One design path (e.g. `tokens/colors.json`) = at most ONE active owner
- Design tokens are the contract between design and frontend — once `tokens/colors.json` is checked in, frontend adopts it

## Setup
- Figma MCP server is configured **globally** per the user's `~/.claude/CLAUDE.md` convention
- No local setup checklist in this role spec; if Figma MCP is not available, raise the issue to PM before starting

## Before commit (checklist)
- [ ] Tokens validate: `node scripts/validate-tokens.js` → exit 0 (if validator exists)
- [ ] Screenshots up to date: re-export via `mcp__figma__export` before commit
- [ ] No TODO/FIXME in design comments (L4)
- [ ] Quoted export count + file paths in commit body (L3)
- [ ] Owner uniqueness verified against `phases/<name>/owners.json` (L5-R)

## Hand-off contract
- **Send to role-frontend**: design tokens (`tokens/*.json`), component screenshots (`screenshots/*.png`), Figma URLs
- **Receive from role-frontend**: feedback on token usage (broken references, missing sizes)
- **Send to role-pm-coordinator**: design system summary (colors, type scale, spacing scale) at plan time

## Coordination
- Sub-tasks between multiple design devs: split by component family (e.g. `feat/design-eve-forms`, `feat/design-frank-nav`)
- Merge conflicts → PM arbitrates (rare; design files usually additive)
- Daily standup: every 30 min, append status to `.dev-kit/session-log.md`

## Forbidden
- Editing `apps/web/`, `components/`, `api/`, `services/` (other roles' territory)
- Pushing tokens to main without role-frontend sign-off (L5-R — frontend must accept the token names)
- Skipping screenshot re-export after Figma source change (causes visual regression drift)
