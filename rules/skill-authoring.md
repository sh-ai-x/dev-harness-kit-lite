---
name: skill-authoring
description: SKILL.md frontmatter schema for dev-kit-lite
---

# Skill authoring rules (lite)

Every skill lives at `skills/<skill-name>/SKILL.md`. Directory name MUST match `name:` in the frontmatter. Same as full kit.

## Required frontmatter

```yaml
---
name: <skill-name>             # kebab-case; must match dir name
category: <one of allowed list>
description: <one-line English summary>
when_to_use: |
  - <bullet 1>
  - <bullet 2>
allowed-tools: <space-separated list>
disallowed-tools: <space-separated list, optional>
model: opus | sonnet | haiku   # optional; default = sonnet
user-invocable: true | false   # optional; default = true
# alpha: state | enforcement | analysis   # OPTIONAL in lite (L6 dropped)
---
```

## Required body sections

1. `## Workflow` — what the skill does, in 1-3 sentences
2. `## Step 1` / `## Step 2` / ... — the actual procedure
3. `## Validation gates` — deterministic checks (exit codes, file paths, JSON keys)
4. `## Iron Laws` — which iron laws this skill enforces (cite L1–L5, L5-R)
5. `## Next step` — hand-off chain (which skill to invoke next)

## Style

- One answer per question (L5)
- No "could also do X, or Y, or Z" lists
- Working code; no TODO/FIXME (L4)
- Verified artifacts only (L3): quoted exit codes, test counts, file paths
