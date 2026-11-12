# SG-301 contrast — header, Inbox, Expiry, asset page (DOM-read values)

Computed from `frontend/src/theme/tokens.css` HSL tokens (light and `.dark`),
converted to sRGB and checked with the WCAG relative-luminance ratio.
All text on these screens uses `--ink`, `--ink-muted` or `--link` on `--paper`
(or `--paper` on `--ink` for the selected nav item and primary buttons).
Font sizes read from the rendered DOM inline styles; the floor is 13 px.

RGB (rounded): light paper (244,240,232), light ink (25,25,25),
light muted (102,98,93), light link (110,48,46);
dark paper (32,27,23), dark ink (244,240,232),
dark muted (184,176,166), dark link (213,156,154).

| Element | fg / bg | Light ratio | Dark ratio | Font size | Size class | Pass |
|---|---|---|---|---|---|---|
| Header brand (StorageGenie) | ink / paper | 15.47 | 15.01 | 20px | normal | 4.5:1 pass |
| Nav links, selected (paper on ink, underline) | paper / ink | 15.47 | 15.01 | 13px | normal | 4.5:1 pass |
| Nav links, unselected | ink / paper | 15.47 | 15.01 | 13px | normal | 4.5:1 pass |
| Catalog header badge (Showing: N items) | ink / paper, line border | 15.47 | 15.01 | 13px | normal | 4.5:1 pass |
| Page headings (Inbox, Expiry, item name) | ink / paper | 15.47 | 15.01 | 24px (page-header) | large | 3:1 pass |
| Section headings (Import jobs, Review queue, Shelf life) | ink / paper | 15.47 | 15.01 | 15px / h2 default | normal | 4.5:1 pass |
| Body text, buttons (Import job, Start, Retry, Resolve) | ink / paper | 15.47 | 15.01 | 13px | normal | 4.5:1 pass |
| Secondary text (subject kind, Checked date, No photo yet) | ink-muted / paper | 5.32 | 7.96 | 13px | normal | 4.5:1 pass |
| Links (Review, Open item, Back to catalog) | link / paper | 8.69 | 7.36 | 13px | normal | 4.5:1 pass |
| Tier pill, status labels (Done, Waiting for you) | ink / paper, line border | 15.47 | 15.01 | 13px | normal | 4.5:1 pass |
| EXPIRED label (Pantry) | link / paper | 8.69 | 7.36 | 13px | normal | 4.5:1 pass |

No text under 13 px remains on the header, Inbox, Expiry page, asset page,
or the EXPIRED label (verified by the sg301-screens header test and the
`fontSize: 11/12` grep returning empty on those files).
Every pair passes its bar (normal text 4.5:1, large `page-header` 3:1).
