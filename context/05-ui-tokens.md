# UI Tokens

Design tokens extracted from the approved design (`context/designs/`). Light,
shadcn/ui-based. These are the single source of visual values — reference them
by name; never hardcode a raw hex in a component. Frontend only.

> Source of truth: the screenshots in `context/designs/`. Dashboard is the hero.

## Foundations

| Token | Value | Use |
| ----- | ----- | --- |
| `--background` | `#f7f7f8` | App background |
| `--card` / `--surface` | `#ffffff` | Cards, panels, nav, dialogs |
| `--border` | `#e4e4e7` | Default borders |
| `--border-subtle` | `#f1f1f3` | Table row separators, faint dividers |
| `--foreground` | `#09090b` | Primary text, headings |
| `--muted-foreground` | `#71717a` | Secondary text, labels |
| `--faint` | `#a1a1aa` | Placeholders, axis labels, table headers |
| `--primary` | `#18181b` | Primary buttons |
| `--primary-foreground` | `#fafafa` | Text on primary |
| `--accent` | `#4f46e5` | Brand: logo, chart line, active nav, links |
| `--accent-soft` | `#eef2ff` | Accent badge/soft backgrounds |
| `--ring` | `#4f46e5` | Focus ring |
| `--radius` | `10px` | Cards/inputs (`--radius-sm` `8px`, `--radius-full` `999px`) |
| `--shadow-sm` | `0 1px 2px rgba(16,17,20,.06), 0 1px 3px rgba(16,17,20,.05)` | Cards |

## Semantic (state) — separate from the accent

| Token | Value | Meaning |
| ----- | ----- | ------- |
| `--gain` / `--gain-bg` | `#16a34a` / `#f0fdf4` | Positive change (up) |
| `--loss` / `--loss-bg` | `#dc2626` / `#fef2f2` | Negative change (down) |
| `--gold` / `--gold-bg` | `#d97706` / `#fef3c7` | Gold asset type |

## Chart tokens

| Token | Value |
| ----- | ----- |
| Portfolio line | `--accent` `#4f46e5`, 2.2px, rounded joins; endpoint dot 4r w/ white ring |
| Portfolio area fill | linear-gradient `rgba(79,70,229,.20)` → `0` |
| Allocation — Funds | `#4f46e5` |
| Allocation — Gold | `#d97706` |
| Grid lines | `#eeeef0`, 1px |
| Axis / tick labels | `--faint` `#a1a1aa`, 11px |

Allocation is a 2-category categorical set (Funds indigo, Gold amber) in fixed
order — do not recolor on filter. Portfolio value is a single series (no legend;
the card title names it).

## Typography

Font: **Inter** (weights 400/500/600/700), `system-ui` fallback. Use
`font-variant-numeric: tabular-nums` on every figure/column of numbers.

| Role | Size / weight / color |
| ---- | --------------------- |
| Page title | 22px / 700 / `--foreground` |
| KPI value | 26px / 700 / `--foreground` |
| Section / card title | 14.5px / 600 / `--foreground` |
| Body / table cell | 13.5px / 500 / `--foreground` |
| Label / secondary | 12.5px / 500 / `--muted-foreground` |
| Table header | 11.5px / 600 / uppercase / `.04em` / `--faint` |

## Spacing & layout

- Nav height `60px`; content padding `24px`; grid gap `16px`; card padding `18px`.
- Content max-width ~`1280px`, centered.

## shadcn mapping

These map to the shadcn CSS-variable convention in `globals.css` (`:root` for
light; add a `.dark` block when a dark theme is introduced). Keep shadcn's
`--background/--foreground/--card/--primary/--muted/--border/--ring/--radius`,
and **add** the app-specific `--accent`, `--gain`, `--loss`, `--gold` (+ `-bg`
variants) above. Every referenced color must have a token — no exceptions, so
the no-raw-hex rule is always followable.

## Invariants

- Reference tokens by name; never a raw hex in a component.
- State color (gain/loss/gold) is semantic and separate from the brand accent.
- `05-ui-tokens.md` owns the *values*; `06-ui-rules.md` owns *how to use them*
  and must not restate the numbers.
