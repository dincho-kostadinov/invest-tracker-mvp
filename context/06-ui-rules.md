# UI Rules

How to apply the tokens in `05-ui-tokens.md`. Design assets in `context/designs/`
are the visual source of truth (dashboard, login, holdings, transactions,
settings). shadcn/ui components, light theme. References tokens by name — never
restates raw values.

## Layout

- Top nav only (no sidebar): white, `--border` bottom, height 60. Logo (indigo
  tile) + wordmark left; nav links; right = currency chip + avatar.
- Active nav item: `--foreground` text on `#f4f4f5`; inactive: `--muted-foreground`.
- Content max-width ~1280px, centered; page padding 24px; section gap 16px.
- Page header: title (22/700) + one muted subline; primary action right-aligned.

## Cards

Everything sits in a card: `--card` bg, `1px --border`, `--radius`, `--shadow-sm`,
padding 18px. Never colored card backgrounds — color lives in badges, text, marks.

## Buttons (shadcn)

- **Primary:** `--primary` bg, `--primary-foreground` text (near-black).
- **Outline:** white, `--border`, `--foreground`.
- **Ghost:** transparent, `--muted-foreground`.
- Height ~38px, `--radius-sm` (8px), 13.5px/500, optional leading icon 15px.

## Inputs

White, `1px --border`, `--radius-sm`, height 38px, 13.5px; placeholder `--faint`;
focus `ring --ring`. Selects show a chevron. Labels 12.5px/500 above the field.

## Badges & status

Pill (`--radius-full`), 11.5px/600, `2px 9px`. Map by meaning:

- Asset type: Fund → `--accent` on `--accent-soft`; Gold → `--gold` on `--gold-bg`.
- Transaction: Buy → `--gain`/`--gain-bg`; Sell → `--loss`/`--loss-bg`; Dividend → `--accent`/`--accent-soft`.
- Connection status: Connected = `--gain` dot + label; Manual = `--faint` dot + label.

Gain/loss numbers use `--gain` / `--loss` text; deltas may sit in a soft
`-bg` chip. Never encode state by color alone — always a sign, label, or icon too.

## Tables

- No zebra striping — white rows separated by `1px --border-subtle`.
- Header: uppercase, 11.5px/600, `--faint`. Cells 13.5px, `--foreground`.
- Right-align all numeric columns; `tabular-nums` everywhere numbers appear.
- Asset cell = square icon tile (initials) + name + sub-line (ISIN / detail).

## Charts

Follow `05-ui-tokens.md` chart tokens. Charts live in `components/`, fed
already-computed data from the API — no return math on the frontend.

- **Portfolio value:** area chart, single series, `--accent` line + soft gradient
  fill, faint grid, labeled endpoint dot, €-value y-labels + month x-labels.
- **Allocation:** donut, Funds `--accent` + Gold `--gold`, 2px surface gap, center
  total, legend with % and € value.
- Give every SVG label room inside the viewBox; chart text uses ink tokens, not the series color.

## Empty & loading states

Every section that can be empty has an empty state (muted text + a CTA, e.g.
"No holdings yet — Add your first holding"). Every async area has a loading
skeleton. Prices that failed to refresh show the last value with a subtle
"stale" hint, never a crash (per architecture invariants).

## Do / Don't

- **Do** reference tokens by name; match the patterns in `context/designs/` and `07-ui-registry.md` before inventing a component.
- **Don't** use raw hex, colored card backgrounds, zebra tables, or state-by-color-alone.
- **Don't** introduce a new pattern when an approved one exists.
