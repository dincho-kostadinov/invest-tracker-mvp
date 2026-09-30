# UI Registry  ·  OPTIONAL — UI / frontend projects only

Living document. Updated after every UI component is built (via `/imprint`).
Read it before building any new component — match existing patterns exactly
before inventing new ones.

> Skip for non-UI projects.

---

## How to Use

Before building any component:
1. Check whether a similar component already exists here.
2. If yes — match its exact classes/values.
3. If no — build it following `06-ui-rules.md` and `05-ui-tokens.md`, then add it here.

After building any component — run `/imprint` to append it to this registry.

---

## Components

### Button

File: `frontend/components/ui/button.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Height | `h-[38px]` |
| Padding | `px-4` |
| Border radius | `rounded-sm` (→ 8px via `--radius-sm`) |
| Text | `text-[13.5px] font-medium` |
| Primary | `bg-primary text-primary-foreground hover:bg-primary/90` |
| Outline | `bg-card text-foreground border border-border hover:bg-muted` |
| Ghost | `text-muted-foreground hover:bg-muted` |
| Focus | `focus-visible:ring-2 focus-visible:ring-ring` |
| Disabled | `disabled:pointer-events-none disabled:opacity-50` |

**Pattern notes:** Only 3 variants exist — `06-ui-rules.md` defines exactly Primary/
Outline/Ghost, not shadcn's stock 6 (no secondary/destructive/link variant yet; add one
only if `06-ui-rules.md` grows a matching pattern). Ghost's hover is `--muted`
(`#f4f4f5`), not shadcn's stock `--accent` — this project's `--accent` already means
brand indigo, so reusing it for a neutral hover would tint every ghost button on hover.
`asChild` (via `@radix-ui/react-slot`) is supported for rendering as a different
element (e.g. a `Link`).

### Input

File: `frontend/components/ui/input.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Height | `h-[38px]` |
| Background | `bg-card` |
| Border | `border border-border` |
| Border radius | `rounded-sm` |
| Text | `text-[13.5px] text-foreground` |
| Placeholder | `placeholder:text-faint` |
| Focus | `focus-visible:ring-2 focus-visible:ring-ring` |
| Disabled | `disabled:cursor-not-allowed disabled:opacity-50` |

**Pattern notes:** Matches Button's height/radius/text-size exactly so form rows align.

### Label

File: `frontend/components/ui/label.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Text | `text-[12.5px] font-medium text-foreground` |
| Other | `select-none` |

**Pattern notes:** Sits directly above its input with `gap-1.5` in the parent flex
column (see `auth-form.tsx`).

### Card

File: `frontend/components/ui/card.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Background | `bg-card` |
| Border | `border border-border` |
| Border radius | `rounded-lg` (→ 10px via `--radius`) |
| Padding | `p-[18px]` |
| Shadow | `shadow-sm` (custom value, not Tailwind's stock shadow-sm — see `05-ui-tokens.md`) |
| Title | `text-[14.5px] font-semibold text-foreground` (`CardTitle`) |
| Description | `text-[12.5px] font-medium text-muted-foreground` (`CardDescription`) |

**Pattern notes:** Composed as `Card` / `CardHeader` / `CardTitle` / `CardDescription` /
`CardContent` / `CardFooter`. Never a colored card background — color lives in badges,
text, and marks per `06-ui-rules.md`.

### Separator

File: `frontend/components/ui/separator.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Color | `bg-border` |
| Thickness | `h-px` (horizontal) / `w-px` (vertical) |

**Pattern notes:** Thin wrapper over `@radix-ui/react-separator`; used with flanking
text (e.g. the login page's "OR" divider) by wrapping in a `flex items-center gap-3`
row.

### Avatar

File: `frontend/components/ui/avatar.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Size | `size-9` |
| Shape | `rounded-full` |
| Fallback background | `bg-accent-soft` |
| Fallback text | `text-[12.5px] font-semibold text-accent` |

**Pattern notes:** Fallback shows initials — from the user's `name` if set, else the
first letter of `email` (see `app/(app)/layout.tsx`). No image upload yet, so
`AvatarImage` is unused so far but kept for when one exists.

### App shell nav

File: `frontend/app/(app)/layout.tsx`, `frontend/components/nav/nav-link.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Header height | `h-[60px]` |
| Header background | `bg-card`, `border-b border-border` |
| Content max-width | `max-w-[1280px]`, `mx-auto`, `p-6` |
| Nav link (inactive) | `text-muted-foreground hover:bg-muted hover:text-foreground` |
| Nav link (active) | `bg-muted text-foreground` |
| Nav link shape | `rounded-sm px-3 py-1.5 text-[13.5px] font-medium` |
| Currency chip | `rounded-full border border-border px-2.5 py-0.5 text-[11.5px] font-semibold text-muted-foreground` |

**Pattern notes:** `NavLink` is a client component (`usePathname()`) since the App
Router layout itself has no reliable per-request pathname without it. Logo mark is the
shared `components/brand/logo-mark.tsx` SVG inside a `size-7 rounded-md bg-accent` tile
(a larger `size-11 rounded-lg` version is used on the auth cards).

### Placeholder / empty state

File: `frontend/components/nav/placeholder-page.tsx`
Last updated: 2026-09-24

| Property | Class |
| --- | --- |
| Title | `text-[22px] font-bold text-foreground` |
| Body box | `rounded-lg border border-border bg-card p-[18px] shadow-sm`, `min-h-[240px]`, centered |
| Body text | `text-[13.5px] font-medium text-muted-foreground` |

**Pattern notes:** Used for the 4 `(app)` pages that don't have a real feature yet
(Dashboard/Holdings/Transactions/Settings). Matches `06-ui-rules.md`'s "Empty & loading
states" rule (muted text, no crash) — swap for real content page-by-page as each
feature is built, not by deleting this component.
