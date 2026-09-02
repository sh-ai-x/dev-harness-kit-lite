# role-frontend

## Headcount
- **n people** (default 2)

## Owns
- `apps/web/` (Next.js app router)
- `components/` (shared React components)
- `hooks/` (custom React hooks)
- `styles/` (CSS modules / Tailwind config)
- `public/` (static assets)
- `package.json`, `tsconfig.json`, `next.config.js` (frontend-side)

## Branch format
- `feat/web-<owner>-<slug>` — e.g. `feat/web-alice-checkout`
- `fix/web-<owner>-<slug>` — e.g. `fix/web-bob-form-validation`

## Worktree root
- `.worktrees/web-<owner>` — e.g. `.worktrees/web-alice`

## Non-overlap iron rule (L5-R)
- One frontend person = at most ONE in-flight step
- One frontend path (e.g. `apps/web/checkout/`) = at most ONE active owner
- Cross-frontend paths must go through PM reassignment (cannot be claimed by two frontend devs simultaneously)

## Before commit (checklist)
- [ ] Test passes: `npm test` → exit 0, ≥1 test for new code
- [ ] Build passes: `npm run build` → exit 0
- [ ] Lint passes: `npm run lint` → exit 0
- [ ] No TODO/FIXME (L4)
- [ ] Quoted exit code in commit body (L3)
- [ ] Owner uniqueness verified against `phases/<name>/owners.json` (L5-R)
- [ ] PM sign-off in `.dev-kit/session-log.md` for cross-role merges

## Hand-off contract
- **Send to role-backend**: API contract spec (request/response schema)
- **Receive from role-backend**: confirmed schema + URL
- **Send to role-figma-mcp**: token usage feedback (which tokens are missing/broken)
- **Receive from role-figma-mcp**: design tokens dump (`design/tokens.json`)

## Coordination
- Sub-tasks between multiple frontend devs: `<scope>-<owner>-<slug>` (e.g. `feat/web-alice-form`, `feat/web-bob-list`)
- Merge conflicts → PM arbitrates
- Daily standup: every 30 min, append status to `.dev-kit/session-log.md`

## Forbidden
- Editing `api/`, `services/`, `models/` (backend territory)
- Editing `design/`, `tokens/` directly (use role-figma-mcp's tokens dump)
- Pushing to main (L2)
- Skipping TDD RED phase (L1)
