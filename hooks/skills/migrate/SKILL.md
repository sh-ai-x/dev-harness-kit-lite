---
name: migrate
category: bootstrap
description: Adopt dev-kit-lite into an EXISTING project with minimal disruption. Detects layout, tech stack, and existing ownership automatically. Generates a portable role-config.json and a phased migration plan. No layout pre-commitment required.
when_to_use:
  - Bringing dev-kit-lite into a project that already has a repo layout
  - Projects with prior tooling (Nx, Turborepo, Lerna, pnpm workspaces, mixed languages)
  - When the team is mid-flight and can't do a clean greenfield bootstrap
allowed-tools: Read Write Bash AskUserQuestion
model: opus
---

# /dev-kit-lite:migrate

## Role

You are the migration steward. Existing projects are not greenfield — they have prior commits, prior conventions, prior tooling, and people who don't want to be disrupted. Your job is to detect what's there, map it onto dev-kit-lite's role/team model, and produce a **portable role-config.json** that matches reality rather than overriding it. Cold realism: if the existing layout cannot be cleanly partitioned into the 5 roles, surface the conflict. Recommend either (a) merge roles, (b) split a role, or (c) accept that this project doesn't fit the kit and abort.

The skill works the same way whether your project lives in one repo, several repos, a workspace, a monorepo, or some hybrid the team assembled over time. You do NOT need to declare a layout. The skill figures it out and adapts.

## Inputs

| Input | Required? | How to provide |
|-------|-----------|----------------|
| Target repo path | yes (default: cwd) | path arg or detected |
| Migration aggressiveness (`conservative` / `balanced` / `aggressive`) | yes (default: `balanced`) | AskUserQuestion |

That's it. Everything else is detected.

## Aggressiveness modes

| Mode | What it does | When to use |
|------|--------------|-------------|
| `conservative` | Only writes `.dev-kit/role-config.json` and `.dev-kit/migration-report.md`. No hooks, no rules files, no AGENTS.md changes. Team adopts gradually. | Projects with strong existing conventions and an existing PM. |
| `balanced` (default) | Writes role-config.json, migration report + plan, and the hooks (worktree-guard, tdd-guard, git-guard) into each repo the team uses. Skips AGENTS.md changes if one already exists. | Most projects. |
| `aggressive` | Writes everything including AGENTS.md (with a backup of the existing one), the per-role rules files, and the L5-R enforcement hooks. Assumes the team is bought in. | Projects explicitly adopting dev-kit-lite as the new convention. |

## Workflow

### Step 1 — Detect the repo setup (no user input needed)

Run these checks; the skill uses whatever it finds without asking the user to declare:

1. **Are there multiple repos?** Look for `.gitmodules`, a parent manifest (`repos.json`, `manifest.json`), sibling repos in known locations, references in `CODEOWNERS` parent. If yes, the skill treats each as a separate repo and proposes per-repo role configs. A "shared contracts" location is auto-detected or the user is asked once.
2. **Is there a workspace config in the current repo?** `pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json`, `rush.json`, `package.json` with `"workspaces"`. If yes, treat the workspace packages as candidate role dirs.
3. **Otherwise, single repo.** The skill operates on `cwd`.

The detected setup is recorded in `role-config.json` as `migrated_from.setup_kind` (one of: `multi-repo`, `workspace-monorepo`, `single-repo`) — purely informational, not a hardcoded contract. The skill works the same regardless.

### Step 2 — Inventory existing tooling

Scan for and report:

| Category | Files to check | Why we care |
|----------|----------------|-------------|
| Node workspace | `package.json` (workspaces), `pnpm-workspace.yaml`, `yarn.lock | yes |
| JS/TS frameworks | `next.config.*`, `vite.config.*`, `nuxt.config.*`, `svelte.config.*`, `expo.*`, `metro.config.*` | detect frontend tech_stack |
| Python | `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `manage.py`, `app.py` | detect backend tech_stack |
| Go | `go.mod`, `go.sum` | detect backend tech_stack (Go) |
| Rust | `Cargo.toml` | detect backend tech_stack (Rust) |
| Java/Kotlin | `pom.xml`, `build.gradle*` | detect backend tech_stack (JVM) |
| AI/LLM | `prompts/`, `eval/`, `lib/llm/`, presence of `anthropic-sdk`/`minimax-sdk`/`openai-sdk` in deps | detect ai role |
| Design | `design/`, `tokens/`, `figma-export/`, `.figma` URLs in README | detect design role |
| Existing dev-kit | `.dev-kit/`, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/` | detect prior adoption |

Print an inventory table so the user can see what the skill is reasoning about.

### Step 3 — Detect existing role assignments

For each role candidate directory, find the most frequent recent contributors:

```bash
git log --since="6 months ago" --pretty=format:"%an" -- <dir> | sort | uniq -c | sort -rn | head -5
```

Other signals:
- `CODEOWNERS` file (if present) — explicit ownership
- `package.json` maintainers field
- Branch naming convention (`feat/web-*`, `feat/api-*` → role prefixes already exist)

Print an inferred roster:
```
Top contributors (last 6 months):
  apps/web/    → alice (47 commits), bob (32 commits)
  api/         → carol (89 commits), dan (12 commits)
  prompts/     → eve (18 commits)
  design/      → no recent contributors (orphaned)
```

### Step 4 — Infer tech_stack per role

For each role candidate dir, match against the tech_stack presets in `templates/tech-stacks/<stack>.json`. The match is by file signature (presence of `next.config.js`, `pyproject.toml`, `Cargo.toml`, etc.), not by path name.

If no preset matches, mark `tech_stack: "custom"` and ask the user for the stack name + paths.

### Step 5 — Generate proposed role-config.json

Construct `.dev-kit/role-config.json` from the inferences:

```json
{
  "version": 1,
  "updated_at": "<iso8601>",
  "migrated_from": {
    "detected_at": "<iso8601>",
    "setup_kind": "single-repo | workspace-monorepo | multi-repo",
    "prior_tooling": ["nx", "jest"],
    "coexistence_notes": "..."
  },
  "roles": {
    "planner": { ... },
    "frontend": {
      "tech_stack": "<inferred>",
      "owns_paths": ["<detected dirs>"],
      ...
    },
    ...
  }
}
```

If existing role mappings conflict with the 5-role taxonomy (e.g., the project has separate "DevOps" and "SRE" teams but no "AI"), the skill **proposes a merge or split**:
- "DevOps + planner" → planner grows a `path_locks: [".github/", "Dockerfile", "docker-compose.yml"]` field, with `boundary_notes: "Owns the registry + infra/CI; does not own product code"`
- "SRE" → propose splitting into a new role (`sre`) or merging into `backend` with a `boundary_notes: "Also owns infra observability"`

The user confirms or rejects each proposal.

### Step 6 — Coexistence report

Print which dev-kit-lite files would overlap with existing ones:

| Kit file | Existing file | Action |
|----------|---------------|--------|
| `CLAUDE.md` | exists | backup to `CLAUDE.md.bak-<ts>`, append role rules |
| `AGENTS.md` | exists | same |
| `.claude/settings.json` | exists | merge allow-list, do not overwrite |
| `hooks/worktree-guard.sh` | absent | install |
| `.dev-kit/` | exists (partial) | preserve, add what's missing |

For each repo the team uses (detected in Step 1), do this.

### Step 7 — Migration plan

Phased adoption — never overwrite on day one:

#### Phase 1 (day 1): Inventory + role-config (no code change)

- Write `.dev-kit/role-config.json` (proposed, marked `"status": "draft"`)
- Write `.dev-kit/migration-report.md`
- Write `.dev-kit/migration-plan.md`
- Add the kit's `.gitignore` patterns to `.gitignore` (merged, not replaced)

#### Phase 2 (day 1-2): Team review

- Team reviews the proposed role-config
- Adjusts owns_paths, tech_stack, headcount, boundary_notes
- Marks `"status": "agreed"` when consensus reached
- No code or hook changes yet

#### Phase 3 (day 2-3): L5-R hooks opt-in

- Install `hooks/worktree-guard.sh` (L2 enforcement)
- Install `hooks/git-guard.sh` (L2 enforcement)
- Do NOT install tdd-guard or destructive-confirm yet (those need team training)
- For each repo the team uses (detected): install per-repo, with shared config in the contracts/ location

#### Phase 4 (day 3-5): Rules + L1/L3 hooks

- Generate `rules/role-<key>.md` per role
- Install `hooks/tdd-guard.sh` (L1)
- Install `hooks/stop-verify.sh` (L3)
- Update AGENTS.md / CLAUDE.md (append, do not overwrite)

#### Phase 5 (week 2): Full adoption

- `hooks/secret-scan.sh`
- `hooks/destructive-confirm.sh`
- Switch review workflow provider (optional, e.g., to MiniMax via this kit's CI template)

The skill prints this plan and the user picks where to stop.

### Step 8 — Render migration report

```markdown
# Migration report — dev-kit-lite adoption

## Detected setup

**`single-repo`** (one repo, no workspace config detected). The skill would have worked identically for `workspace-monorepo` or `multi-repo`.

## Top-level directory inventory

| Dir | Inferred role | Tech stack | Recent contributors | Confidence |
|-----|---------------|------------|---------------------|-----------|
| apps/web/ | frontend | nextjs-app-router | alice (47), bob (32) | HIGH |
| api/ | backend | fastapi | carol (89) | HIGH |
| prompts/ | ai | minimax-only | eve (18) | MEDIUM |
| design/ | design | figma-mcp | — (orphaned) | LOW |
| lib/ | (unassigned) | — | dan (12) | — |

## Coexistence

| Kit file | Existing file | Action |
|----------|---------------|--------|
| CLAUDE.md | exists | backup + append |
| AGENTS.md | exists | backup + append |
| .dev-kit/ | absent | create |

## Proposed role-config.json

(printed inline)

## Migration plan (5 phases)

(printed inline)

## Risks / open questions

- `design/` has no recent contributors — assign a fallback owner or remove the role?
- `lib/` is unassigned — backend (dan has 12 commits) or shared (frontend reads)?
- Existing CODEOWNERS says alice owns both apps/web/ and api/ — current proposal splits this. Confirm?
```

## Validation gates

- `.dev-kit/role-config.json` parses as JSON, `version: 1`, all 5 built-in roles present (planner mandatory)
- `migrated_from.setup_kind` is one of the three values (informational, not enforced)
- Coexistence report generated (every kit file listed, even if no-op)
- Migration plan has all 5 phases printed (user can stop early)
- `migrated_from.detected_at` populated

## Iron Laws

- **L2** (verification before completion) — verify proposed role-config.json against detected inventory before writing
- **L3** (evidence before claim) — every inferred ownership cites the file:line or git command that produced it
- **L5** (one answer per question) — one migration decision at a time when in interactive mode
- **L5-R** (non-overlap) — proposed `owns_paths` must be disjoint; surface any inferred overlap

## Anti-patterns

- ❌ Overwriting existing `CLAUDE.md` / `AGENTS.md` / `.claude/settings.json` without backup
- ❌ Asking the user "is this monorepo or multi-repo?" — just detect and proceed
- ❌ Treating multi-repo setups as "monorepo with extra steps" — they have different sync semantics (the user must mirror `role-config.json` across repos), but the SKILL itself is the same
- ❌ Forcing the 5-role taxonomy on a project that has fundamentally different roles — escalate to a merge/split proposal, don't silently fit
- ❌ Skipping Phase 1 inventory and going straight to hook installation — team has no time to review
- ❌ Writing `owns_paths` from path-name guesses alone (e.g., assuming `app/` is always frontend) — confirm with file signature + git history
- ❌ Making the skill's behavior differ based on the detected setup_kind — the only difference is which files get written WHERE; the user-facing workflow is identical

## Next step

- Phase 1 done → circulate `migration-report.md` to the team for review
- After Phase 2 agreement → start Phase 3 hook opt-in
- After all 5 phases → run `/dev-kit-lite:bootstrap` for any remaining kit files (or skip, if migrate covered them)

## Downstream contracts

This skill is the **upstream** of two:

| Skill | Reads from `migrate` |
|-------|----------------------|
| `role` | consumes the proposed `role-config.json`; user can run `role` after `migrate` to refine |
| `bootstrap` | if migrate was skipped and the team wants a clean bootstrap later, `bootstrap` is the greenfield path |

If the team restructures (new repos added, new tech stack adopted), run `migrate` again with the same aggressiveness mode.
