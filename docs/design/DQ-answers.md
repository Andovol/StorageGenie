# Design-track answers DQ1–DQ10 (owner-relayed from the design AI, 2026-09-16)

Source: chat relay, recorded verbatim-ish here so packets embed from this file instead of
citing out-of-band text (M19). Packets quote the sections they rely on.

## DQ1: Category Taxonomy & Extensibility

The taxonomy is **user-extensible with a fixed fallback baseline**. Categories are dynamic
strings on the data model (`category: string`); the UI seeds a canonical set:

1. `Hardware & Tools`
2. `Electronics & Gadgets`
3. `Apparel & Textiles`
4. `Home & Decor`
5. `Packaging & Materials`
6. `Uncategorized`

Behavior: the filter bar renders the top 5 most populated categories plus `All` and
`Uncategorized`. Custom categories from asset metadata populate the filter list dynamically
or collapse into a "More Categories..." popover.

## DQ2: Styling Engine vs. Token Naming Convention

**Tailwind is an optional implementation detail; the CSS Custom Property design tokens are
the strict requirement.** With plain CSS: do NOT install Tailwind; implement the exact
semantic token names via CSS Custom Properties (`--background`, `--foreground`, `--card`,
`--card-muted`, `--border`, `--muted-foreground`); map utility classes to plain CSS classes
(e.g. `.bg-card { background-color: hsl(var(--card)); }`).

## DQ3: Dark-Mode Elevation, Surfaces & Contrast

Depth layers, not drop shadows:

| Surface Layer | Hex | Variable | Used for |
|---|---|---|---|
| 0: Canvas | `#0F0E0D` | `--background` | Page body, table background, empty canvas |
| 1: Elevated | `#1C1A18` | `--card` | Product cards, sticky header, modals, inspector drawer |
| 2: Inset wells | `#262320` | `--card-muted` | Cutout wells, raw JSON blocks, input fills |
| Borders | `#2C2926` | `--border` | Hairline 1px between all layers |

Status badges (desaturated backgrounds, WCAG AA):

- Complete / Scene Rendered (green): light `bg-emerald-50 text-emerald-800
  border-emerald-200`; dark `bg-emerald-950/40 text-emerald-400 border-emerald-800/50`
- Cutout Extracted (blue): light `bg-sky-50 text-sky-800 border-sky-200`; dark
  `bg-sky-950/40 text-sky-400 border-sky-800/50`
- Source Only / Pending (gray): light `bg-stone-100 text-stone-700 border-stone-200`;
  dark `bg-stone-800/50 text-stone-400 border-stone-700/50`
- Failed / Error (rose): light `bg-rose-50 text-rose-800 border-rose-200`; dark
  `bg-rose-950/40 text-rose-400 border-rose-800/50`

## DQ4: Media Pipeline, Coordinates & Response Persistence

Producers: (1) Vision Detector (photo → items, bbox, classification, suggested name);
(2) Asset Isolation Engine (segmentation → transparent PNG cutout); (3) Scene Generator
(diffusion → contextual preview).

Bounding box: normalized relative coordinates `[0.0, 1.0]`, independent of display scale:
`{ x, y, width, height }` as fractions.

Storage: `modelInfo` inline (`{ provider, model, executedAt, latencyMs }`).
`rawResponse`: do NOT persist large raw provider payloads in the primary store — keep
extracted parameters, confidence scores, prompt tokens only; full debug logs go to a
separate ephemeral log or are ignored in production.

## DQ5: Compact Table View

Row click opens the same Inspector Drawer. Columns: 1. Asset `56px` center (40x40
thumbnail on `bg-card-muted`) · 2. Name `min-w-[200px]` left, truncated ·
3. Category `140px` left, monospace micro-badge (`text-[11px] font-mono`) ·
4. Status `130px` left, color badge with dot · 5. Dimensions/Specs `120px` left ·
6. Added `110px` right, tabular relative date (`font-mono text-muted-foreground`) ·
7. Actions `48px` center, ghost `...` button (inspector or deletion).

## DQ6: ⌘K Behavior

Lightweight Command Palette Modal: `⌘K`/`Ctrl+K`; item search with keyboard selection;
quick actions `> Import New Asset`, `> Switch Theme`, `> Filter by [Category]`.
MVP fallback allowed: `⌘K` focuses the top-bar search field and selects the query text.

## DQ7: AI Action Buttons & State Transitions

Idle (icon + label) → Processing (disabled, `Generating...`, `Loader2` spinner; well shows
pulse overlay + progress) → Failure (idle + `Retry Generation` label, dismissible toast
with reason, error banner with "View Error Details" expander). Cost/model micro-text below
the button group (e.g. `Model: gpt-image-2 · Est. Cost: ~1 credit ($0.04)` — model/cost
strings always read from settings/ledger, never hardcoded).

## DQ8: Typography

System sans baseline (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
"Helvetica Neue", Arial, sans-serif`); monospace tokens (`ui-monospace, SFMono-Regular,
Menlo, Monaco, Consolas, "Liberation Mono", monospace`). Optional upgrade: Inter or Geist
Sans variable 400/500/600. Avoid Instrument Sans unless self-hosted.

## DQ9: Asset Import Flow

Import buttons open an `AssetImportModal.tsx` dialog (not a route): dropzone
(drag-drop / file selector / clipboard paste `Ctrl+V`/`⌘V`; PNG, JPG, WebP up to 25MB),
"Automatically detect items and isolate cutouts" checkbox, pending review queue with
Remove, Cancel / `Process N Items`. Auto-detect wiring is S3-era; the shell ships first.

## DQ10: Badge-to-Status Mapping & Error Presentation

State machine: `[Source Only] —(Run Isolation)→ [Cutout Extracted] —(Run Scene Render)→
[Scene Rendered]`; failures → `[Isolation Failed]` / `[Render Failed]` → failed state
(red badge + error banner + retry CTA). Card failure visuals: red pill top-right, hairline
red well border (`border-rose-500/30`) with `AlertTriangle`, error icon by the title;
click opens the drawer on the failed step with a **Retry Pipeline** button.
