# SG-302 contrast — every Pantry text pair, DOM-read, light and dark

Computed colours read from the DevTools session on the scratch app (`output/SG-302-scratch/shoot_full.mjs` → `docs/worklogs/SG-302_shots/proof_full.json`, empty link via `read_empty_link.mjs`). Background is the effective background walked up from the text node until opaque (page `--paper` `rgb(32,27,23)` dark / `rgb(244,240,232)` light; buttons/notice on `--card` `rgb(28,26,24)` dark / `rgb(255,255,255)` light). Ratios computed from the quoted `rgb()` values (WCAG relative luminance). Size class: normal < 18px (or < 14px bold); large ≥ 18px or ≥ 14px bold. Bar: 4.5:1 normal, 3:1 large. `--link` dark `rgb(213,156,154)` (`2 41% 72%`); light `rgb(110,48,46)` (`2 41% 30.6%`, identical to `--primary` light).

| element | light fg / bg (DOM) | light ratio | dark fg / bg (DOM) | dark ratio | size | pass |
|---|---|---|---|---|---|---|
| heading `h1.page-header` | `rgb(28,25,23)` on `rgb(244,240,232)` | 15.39 | `rgb(245,245,244)` on `rgb(32,27,23)` | 15.64 | large (24px bold) | pass (≥3:1) |
| subtitle (What you have…) | `rgb(102,98,93)` on `rgb(244,240,232)` | 5.32 | `rgb(184,176,166)` on `rgb(32,27,23)` | 7.96 | normal 13px | pass (≥4.5:1) |
| count `12 ITEMS` | `rgb(25,25,25)` on `rgb(244,240,232)` | ~15.0* | `rgb(244,240,232)` on `rgb(32,27,23)` | 15.01 | normal 13px bold | pass |
| Not sorted yet line | `rgb(25,25,25)` on `rgb(244,240,232)` | ~15.0* | `rgb(244,240,232)` on `rgb(32,27,23)` | 15.01 | normal 13px | pass |
| Not sorted link (Sort them…) | `rgb(25,25,25)` on `rgb(244,240,232)` | ~15.0* | `rgb(244,240,232)` on `rgb(32,27,23)` | 15.01 | normal 13px | pass |
| section heading USE SOON / EVERYTHING | `rgb(28,25,23)` on `rgb(244,240,232)` | ~15.4* | `rgb(245,245,244)` on `rgb(32,27,23)` | ~15.6* | normal 13px bold | pass |
| tile name | `rgb(25,25,25)` on `rgb(244,240,232)` | ~15.0* | `rgb(244,240,232)` on `rgb(32,27,23)` | 15.01 | normal 14px 600 | pass |
| time-left muted (No date / later) | `rgb(102,98,93)` on `rgb(244,240,232)` | 5.32 | `rgb(184,176,166)` on `rgb(32,27,23)` | 7.96 | normal 13px | pass |
| time-left accent (expired / ≤2d) | `rgb(110,48,46)` on `rgb(244,240,232)` | 8.69 | `rgb(213,156,154)` on `rgb(32,27,23)` | 7.36 | normal 13px | pass |
| EXPIRED label | `rgb(110,48,46)` on `rgb(244,240,232)` | 8.69 | `rgb(213,156,154)` on `rgb(32,27,23)` | 7.36 | normal 11px bold | pass |
| quantity (N left) | `rgb(25,25,25)` on `rgb(244,240,232)` | ~15.0* | `rgb(244,240,232)` on `rgb(32,27,23)` | 15.01 | normal 13px | pass |
| No photo yet | `rgb(102,98,93)` on `rgb(244,240,232)` | 5.32† | `rgb(184,176,166)` on `rgb(32,27,23)` | 7.96† | normal 13px | pass |
| action buttons (−1/Edit/Use it up/Put back) | `rgb(25,25,25)` on `rgb(255,255,255)` | 17.58 | `rgb(244,240,232)` on `rgb(28,26,24)` | 15.27 | normal 13px | pass |
| notice text (Juice used up ·) | — (dark-only shot) | — | `rgb(244,240,232)` on `rgb(28,26,24)` | 15.27 | normal 13px | pass |
| empty state text | `rgb(25,25,25)` on `rgb(244,240,232)` | ~15.0* | `rgb(244,240,232)` on `rgb(32,27,23)` | ~15.0* | normal 13px | pass |
| empty Capture link | `rgb(110,48,46)` on `rgb(244,240,232)` | 8.69 | `rgb(213,156,154)` on `rgb(32,27,23)` | 7.36 | normal 13px underline | pass |
| tile error text (`--badge-failed-fg`, only on error) | not rendered in normal DOM; token `343.4 79.7% 34.7%` light / `353 95.7% 81.8%` dark on paper | UNCLEAR (no error state rendered) | — | — | normal 13px | REMAINING (no error triggered in scratch) |

\* Light `rgb(25,25,25)` / `rgb(28,25,23)` are `--ink` (`0 0% 9.8%`) resolved in the two contexts; ratio computed from quoted values is ≥15:1 in every case (representative rows computed explicitly).
† No-photo pair uses the same tokens as time-muted (`--ink-muted` on `--paper`); the tile low-photo tile was not isolated by selector in the run, so the ratio is carried from the identical token pair measured above.

**Surface established:** the EXPIRED label's effective background in dark is `rgb(32,27,23)` (dark `--paper`, `26.7 16.4% 10.8%`), not the body `rgb(15,14,13)` (`--background`). Page div sets `--paper` (`PantryPage.tsx:327`); the tile article has no background, so it inherits paper. Audit's 1.95:1 was `--primary` on body; on the real surface `--primary` is 1.73:1 (computed), `--link` is 7.36:1 — both ≥4.5:1 only with `--link`. Light `--link` equals `--primary` (`2 41% 30.6%`, `rgb(110,48,46)`), so light is unchanged.

**Result:** every rendered pair passes its bar. No shared-component failure to report. The error-text pair was not rendered (no error triggered); it is listed as REMAINING, not claimed.
