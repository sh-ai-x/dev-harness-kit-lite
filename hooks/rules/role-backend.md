# role-backend

## Headcount
- **n people** (default 2)

## Owns
- `api/` (FastAPI / Flask / Django routes)
- `services/` (business logic)
- `models/` (SQLAlchemy / Pydantic schemas)
- `tests/` (pytest)
- `requirements.txt`, `pyproject.toml`, `alembic/` (backend-side)

## Branch format
- `feat/api-<owner>-<slug>` — e.g. `feat/api-carol-checkout`
- `fix/api-<owner>-<slug>` — e.g. `fix/api-dave-payment-bug`

## Worktree root
- `.worktrees/api-<owner>` — e.g. `.worktrees/api-carol`

## Non-overlap iron rule (L5-R)
- One backend person = at most ONE in-flight step
- One backend path (e.g. `api/checkout/`) = at most ONE active owner
- Cross-backend paths must go through PM reassignment

## Before commit (checklist)
- [ ] Test passes: `pytest tests/ -v` → exit 0, ≥1 test for new code
- [ ] Type check: `mypy api/ services/ models/` → exit 0
- [ ] Lint: `ruff check api/ services/ models/` → exit 0
- [ ] No TODO/FIXME (L4)
- [ ] Quoted exit code in commit body (L3)
- [ ] Owner uniqueness verified against `phases/<name>/owners.json` (L5-R)

## Hand-off contract
- **Send to role-frontend**: API contract spec (request/response schema, status codes, error format)
- **Receive from role-frontend**: API consumption requirements (what UI calls, what data it needs)
- **Send to role-pm-coordinator**: dependency list (`requirements.txt` diff)
- **Receive from role-pm-coordinator**: build-verify verdict per step

## Coordination
- Sub-tasks between multiple backend devs: `<scope>-<owner>-<slug>` (e.g. `feat/api-carol-checkout`, `feat/api-dave-list`)
- Merge conflicts → PM arbitrates
- Daily standup: every 30 min, append status to `.dev-kit/session-log.md`

## Forbidden
- Editing `apps/web/`, `components/`, `hooks/` (frontend territory)
- Editing `design/`, `tokens/` (use frontend hand-off)
- Pushing to main (L2)
- Skipping TDD RED phase (L1)
- Hitting external services in tests without mocking
