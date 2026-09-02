# design-lite.md — Design tokens reference (lite)

> Apple design system reference is at `/Users/sanghee/dev/meta_harness/shared/design.md` (global CLAUDE.md mandate).
> If that file does not exist on disk, use this stub + the operator's project-specific design tokens.

## Lite version: tokens your MVP needs

For a 4-hour MVP, you need ~15 tokens, not the full Apple design system:

### Colors (5 max)
- `--color-bg` (background)
- `--color-fg` (foreground)
- `--color-accent` (primary action)
- `--color-border`
- `--color-danger`

### Typography (3 max)
- `--font-body` (Inter / system-ui)
- `--font-mono` (JetBrains Mono / ui-monospace)
- `--type-scale-ratio` (default 1.250 = major third)

### Spacing (8px grid)
- `--space-1` = 8px
- `--space-2` = 16px
- `--space-3` = 24px
- `--space-4` = 32px
- `--space-6` = 48px

### Components (3 max)
- Button (primary / secondary / ghost)
- Input (single line + label)
- Card (white bg + border + 16px padding)

## Where these tokens live

- `design/tokens/colors.json` (Figma MCP exports here)
- `design/tokens/typography.json`
- `design/tokens/spacing.json`
- `apps/web/styles/tokens.css` (frontend mirrors JSON to CSS custom properties)
- `apps/web/tailwind.config.ts` (if using Tailwind, extends theme from tokens.css)

## Hand-off contract

| From | To | Artifact |
|------|----|----------|
| role-figma-mcp | role-frontend | `design/tokens/*.json` |
| role-figma-mcp | role-frontend | `screenshots/*.png` (component visuals) |
| role-frontend | role-pm-coordinator | `apps/web/styles/tokens.css` (mirror) |

## See also

- `rules/role-figma-mcp.md` (the role that owns these tokens)
- `rules/role-frontend.md` (the role that consumes them)
