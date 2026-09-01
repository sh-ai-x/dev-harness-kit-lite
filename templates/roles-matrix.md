# Roles matrix — dev-harness-kit-lite

| Role | Headcount | Owns | Branch prefix | Default Tools |
|------|-----------|------|---------------|---------------|
| **PM / Coordinator** | 1 | PRD.md, .dev-kit/session-log.md, .dev-kit/decision-log.md, phases/<name>/owners.json | — (PM does not own feature branches) | AskUserQuestion, Read, session-log append |
| **Frontend** | n (default 2) | apps/web/, components/, hooks/, styles/, public/, package.json (frontend-side), tsconfig.json, next.config.js | feat/web-<owner>-<slug> | npm, npm test, npm run build, npm run lint, Next.js |
| **Backend** | n (default 2) | api/, services/, models/, tests/, requirements.txt, pyproject.toml, alembic/ | feat/api-<owner>-<slug> | pytest, mypy, ruff, FastAPI/Flask/Django |
| **Design (Figma MCP)** | n (default 1) | design/, tokens/, figma-export/, screenshots/ | feat/design-<owner>-<slug> | mcp__figma__* tools, JSON validators |

## Coordination slots

| Cadence | PM action | Team action |
|---------|-----------|-------------|
| Every 30 min | Append check-in to session-log | Update owners.json status |
| Every 1 hour | Run build-verify on completed steps | Address review comments |
| End of session | Final build-verify + retro entry | Clean up worktrees (or keep for next session) |

## Hand-off chain

```
role-figma-mcp ──tokens.json──► role-frontend ──API contract──► role-backend
        ▲                                                                     │
        │                                                                     │
        └────────────screenshots + tokens──────────────────────────────────────┘
```

```
role-pm-coordinator ──plan/PRD──► all roles ──build-tdd──► role-pm-coordinator ──build-verify──► role-pm-coordinator ──merge──► main
```
