# Changelog

## v0.1.0 (2026-09-01)

Initial release. 7 skills (bootstrap, plan, ci-setup, build-tdd, build-verify, review, reassign), 7 hooks, 6 stages. Designed for 4-hour greenfield MVP/POC team sprints.

### Iron Laws (5 + 1)
- L1: No prod code without a failing test
- L2: No Edit/Write on main checkout
- L3: No "done" without quoted exit code + test count
- L4: No TODO / FIXME in committed code
- L5: One answer per question
- L5-R (NEW): One person = at most ONE in-flight step; one directory = at most ONE active owner

### Highlights
- Per-step `## Role` section mandatory in `phases/<name>/step<N>.md`
- `phases/<name>/owners.json` registry — machine-checkable non-overlap contract
- PM/coordinator role (NEW, mandatory)
- Advisory-only `review.yml` (no required CI checks, merge works on red)
- 6-person team template (1 PM + 2 FE + 2 BE + 1 Design)
