---
name: proposal
category: design
description: 0-arg HTML renderer for design proposals / plans. Renders any docs/proposals/<bucket>/<main>/<sub>.yaml (status auto-routed from YAML `status:`) to a self-contained HTML doc for pre-implementation review, with structured before/after + pros/cons/limitations analysis.
when_to_use:
  - User types /dev-kit-lite:proposal
  - PM wants to share a draft proposal/plan with reviewers before `/dev-kit-lite:build-tdd` starts
  - User wants to view an existing proposal as a single self-contained HTML doc
allowed-tools: Read Write Bash
model: sonnet
---

# /dev-kit-lite:proposal — design proposal HTML viewer

Renders any proposal YAML to a single self-contained HTML document. Ported
from the full `dev-kit`'s `proposal` skill — the renderer is generic and has
no dependency on dev-kit-lite's heavier machinery (owners.json, worktrees,
TDD cycle), so it works unchanged as a standalone doc-review tool.

**Requires**: PyYAML (`python3 -c "import yaml"` — install with
`pip install pyyaml` if missing). This is the only skill in the kit with a
dependency beyond the Python standard library.

**Status-routed layout** (default for new renders): every proposal lives at
`docs/proposals/<bucket>/<main>/<sub>.{yaml,html}` where `<bucket>` is one of
`review`, `accepted`, `rejected`. The bucket is auto-routed from the YAML's
`status:` field:

      draft               -> review
      design-discussion   -> review
      ready-for-review    -> review
      accepted            -> accepted
      rejected            -> rejected
      superseded          -> rejected

Unknown statuses fall back to `review` so a typo in the YAML still produces
a routable path. Pass `<bucket>/<main>/<sub>` explicitly to override.

- `<main>` is the umbrella (e.g. `todo-app` — one umbrella groups related
  sub-proposals for one MVP sprint).
- `<sub>` is the sub-topic slug (e.g. `auth-flow`, `00-index`). The file is
  named after the sub-topic — not `index.{yaml,html}` — so the leaf is
  recognisable on a flat directory listing.

## What it does

1. List available proposal topics: `python3 -m lib.render_proposal_html --list`
2. Render one: `python3 -m lib.render_proposal_html <main>/<sub>` (status
   auto-routes) or `python3 -m lib.render_proposal_html <bucket>/<main>/<sub>`
   (explicit bucket override). Writes `docs/proposals/<bucket>/<main>/<sub>.html`.
3. Print the file path so the user can open it in a browser
   (`open docs/proposals/<bucket>/<main>/<sub>.html` on macOS, or any browser
   via `file://`).
4. Stop. The skill does not edit the YAML — the PM/owner authors the
   proposal; this skill only renders.

The render logic lives in `lib/render_proposal_html.py` (pure function) plus
a `__main__` CLI entry (`python3 -m lib.render_proposal_html`).

## Workflow (BEFORE / AFTER)

The skill **prescribes** a before-then-after authoring discipline. A
proposal is a contract between the existing code and the change being
proposed; reviewers benefit when both sides are present and citable.

The renderer does NOT enforce this discipline — the parser accepts a YAML
that omits `before:`/`after:` entirely. The discipline below is the
recommended shape; reviewers are the enforcement mechanism, same as every
other advisory gate in this kit (L5-R non-overlap is the only
machine-enforced ownership rule; this is not one).

### Before — analyze the existing code

```yaml
before:
  summary: |
    No proposal-doc skill exists in dev-kit-lite today.
  evidence:
    - 'skills/ has 14 SKILL.md files, none named proposal'
```

### After — describe the proposed state

```yaml
after:
  summary: |
    A ported proposal skill renders docs/proposals/**/*.yaml to HTML.
  files:
    - path: skills/proposal/SKILL.md
      change: 'new skill, ported from dev-kit'
    - path: lib/render_proposal_html.py
      change: 'new lib, ported from dev-kit unchanged except command prefix'
```

The `files` list is a **reviewer commitment**. Anything not listed should
not change in the implementation PR.

### Pros, cons, limitations

```yaml
pros:
  - 'Deterministic, self-contained HTML — safe to email or open from file://'
cons:
  - 'Authoring burden: before/after/pros/cons/limitations is more ceremony than a free-form doc'
limitations:
  - 'No syntactic diff between before: and after: — the reviewer reads both halves'
```

- **Pros** = strengths the change brings, with citation.
- **Cons** = known weaknesses knowingly accepted, not scope-cut items.
- **Limitations** = what the design cannot do by design, not "didn't get to it".

### When the structured fields are not used

Proposals with only `sections:` (no `before:`/`after:`/`pros:`/`cons:`/
`limitations:`) still render correctly — the HTML is identical to the plain
shape, just without the before/after cards.

## Output (in chat)

```
## /dev-kit-lite:proposal — <main>/<sub>

**Source**: docs/proposals/<bucket>/<main>/<sub>.yaml
**Output**: docs/proposals/<bucket>/<main>/<sub>.html (one self-contained HTML doc, inline CSS only, no JS, dark-mode aware)
**Status**: <status from YAML frontmatter>
**Sections**: <count>

**Open in browser**: `open docs/proposals/<bucket>/<main>/<sub>.html` (macOS)
```

## Authoring a proposal

Create `docs/proposals/<main>/<sub>.yaml` (or `<bucket>/<main>/<sub>.yaml` to
force a bucket) with this shape:

```yaml
title: <one-line title>
status: draft | design-discussion | ready-for-review | accepted | rejected | superseded
issue: <issue number, optional>
date: YYYY-MM-DD
tags: [<tag1>, <tag2>]

# Structured before/after + pros/cons/limitations — all optional.
before:
  summary: |
    Markdown-lite description of the code's CURRENT state.
  evidence:
    - 'file:line, log excerpt, or commit hash supporting the claim'
after:
  summary: |
    Markdown-lite description of the code's PROPOSED state.
  files:
    - path: <repo-relative file path>
      change: |
        Markdown-lite description of what this file becomes.
pros:
  - 'Strength 1 with citation'
cons:
  - 'Weakness the proposal knowingly accepts + mitigation'
limitations:
  - 'What the design CANNOT do (out-of-scope-by-design)'

sections:
  - title: <section 1>
    body: |
      Markdown-lite body. Supports:

      - # ## ### headings
      - paragraphs
      - **bold**, *italic*, `code`
      - [link text](https://...)
      - [cross-doc link](<sub>.html) — bare relative paths and
        `../<sibling>.html` are both allowed
      - unordered (- ) and ordered (1. ) lists
      - | GFM tables |
      - ``` fenced code blocks ```
      - > blockquotes
      - --- horizontal rules
```

Then run `/dev-kit-lite:proposal <main>/<sub>` to render. The topic slug
must match `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}/[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`.
The filenames `proposal.yaml` and `index.yaml` are reserved and skipped by
the renderer.

### Cross-references between proposals

Inside a body, link to another proposal in the same umbrella as
`[label](<other-sub>.html)` — resolves as a sibling under `<main>/`.
Cross-umbrella links use `../<other-main>/<sub>.html`.

## Contract

**Defensive HTML escaping on every interpolated value.** The renderer
escapes titles, anchors, free-text fields, and link URLs — a title with
`<script>` in it renders as `&lt;script&gt;`, never executes. **No
`<script>` tag, no external assets, inline CSS only** — the output is safe
to email, archive, or open from `file://`.

## Editing the proposal

The YAML is hand-edited, not generated. Re-run `/dev-kit-lite:proposal
<main>/<sub>` (or `python3 -m lib.render_proposal_html <main>/<sub>`) to
refresh the HTML after an edit.

## Related

- `lib/render_proposal_html.py` — pure function: `parse_proposal_yaml` +
  `render` + `__main__` CLI entry
- `lib/atomic.py` — `atomic_write_text`, the POSIX-atomic write helper the
  renderer uses so a crash mid-write never leaves a half-written HTML file

## Pros of this skill

- **Structured before/after analysis forces honest proposals**, without
  blocking a bare `sections:`-only draft for early-stage ideas.
- **Pros/Cons/Limitations are visually distinct** in the rendered HTML
  (check / ballot-x / warn-glyph cues), so a reviewer scans the trade-off
  shape in one glance.
- **Deterministic renderer** — two reviewers opening the same proposal see
  byte-identical output. `atomic_write_text` makes partial writes
  impossible.
- **Inline-CSS-only, escaped output** — safe to email, archive, or open
  from `file://`.

## Cons of this skill

- **Markdown-lite grammar is intentionally narrow** — H1-H3 only, no
  nested lists, no footnotes, no images, no raw HTML.
- **Authoring burden is higher than a free-form document** for a team that
  just wants to jot "should we add X?" during a 4-hour sprint. Workaround:
  leave `before:`/`after:`/`pros:`/`cons:`/`limitations:` out entirely for
  `status: draft` and add them once the idea matures.
- **No diff between `before:` and `after:`** — the renderer shows them
  side-by-side, not as a syntactic diff.

## Limitations of this skill

- **Cannot detect shallow evidence.** The parser enforces that
  `before.evidence` is a list of strings, not that each string is a real
  citation. The reviewer must catch hand-waved evidence.
- **Cannot enforce that `after.files` matches the implementation PR.** The
  hand-off contract is the implementation PR body citing the proposal.
- **Not wired into any other skill's gate.** Unlike the full kit (where
  `/dev-kit:plan`'s final gate auto-renders a proposal), this port is a
  standalone skill — the PM decides when to write and render one. Lite's
  own `/dev-kit-lite:plan` has no proposal-emitting gate.

## Hand-off

Next: open `docs/proposals/<main>/<sub>.html` in a browser, share the file
with reviewers, then update the YAML's `status:` field as the proposal
moves through review. Once `status: accepted`, proceed to
`/dev-kit-lite:plan` → `/dev-kit-lite:build-tdd` for implementation.
