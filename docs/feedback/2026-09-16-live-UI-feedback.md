# Live-UI feedback triage 2026-09-16 (owner screenshots ×4)

Source: owner live pass at https://storagegenie.dynv6.net, image `86f7436d5a61` (SG-053).
Grounded in tree at `automation` head `69b4ef9`.

## Owner reports (verbatim-ish)

- FB-1 "My toothpaste product has no icon."
- FB-2 "Top bar is white, rest is dark, is that intentional?"
- FB-3 "Other pages were not updated to the new design system, just the first one."
- FB-4 "Check for other UI glitches or issues, or any other type of issues." (screenshots ×4)

## Grounding

- Double header: `frontend/src/App.tsx:22` legacy `Nav` (`background: "#f9fafb"`, hard-coded) wraps
  every route, PLUS `frontend/src/components/shell/AppShell.tsx:46` sticky
  `AppHeader` (`bg-card border-border`, tokens) on the catalog route. Two "StorageGenie"
  wordmarks stack — screenshots 1–2 show it. **Not intentional.** Wardrobe scope was
  catalog-only (SG-043→047/050/051); the legacy Nav was never removed.
- Shell: `frontend/src/App.tsx:51` root is hard-coded `background: "white"`, so non-catalog
  routes (Capture, Chat) render light while the catalog shell renders dark tokens
  (`tokens.css:25-44` `.dark`). `ThemeProvider` (`theme/ThemeProvider.tsx:40-53`) toggles
  `.dark` on `<html>`, but hard-coded inline styles ignore it.
- Empty icon: `ProductCard.tsx:60-65` `cardMedia` returns `null` with no evidence/cutout/scene;
  `ProductCard.tsx:136-144` renders nothing in that case (no fallback icon); same in
  `ProductGrid.tsx:87-94` `TableThumb`. Toothpaste is `status: "raw"` (`product.ts:86`,
  DQ10 initial state) with no photo → empty dark well/square. Real gap, no fallback specified.
- Catalog mapping: `product.ts:67-74` `toProductCategory` maps `unknown`/empty → `Uncategorized`;
  `assetToProductItem` sets `status: "raw"`, `metadata: {}` (`product.ts:76-90`). So Toothpaste
  shows "Uncategorized" + "Source Only" + blank specs by construction until S3 AI derivation.
- Old-design routes (grep 2026-09-16, 28 hard-coded-style hits): `CapturePage.tsx:22`,
  `ChatPage.tsx:69`, `SettingsPage.tsx:14`, `InboxPage.tsx:22`, `PlanningPage.tsx:64`,
  `ReviewPage.tsx:55`, `AssetDetailPage.tsx:53-129`, `AssetForm.tsx:161,200`,
  `CandidateCard.tsx:52`, `ChatTranscript.tsx:23`, `AssetCard.tsx:26`, `JobCard.tsx:11`.
  All use hard-coded light inline styles, no token classes. **Expected — staged scope, not a regression.**
- Table overflow (screenshot 2): `ProductGrid.tsx:41-49` `COLUMNS` fixed widths sum ~804px + padding,
  `<table>` has no scroll container (`ProductGrid.tsx:113`); pills row (`CatalogToolbar`) has no
  wrap/scroll affordance → right edge cuts ("Dim", "Standard" pill). Real.
- Capture dup inputs (screenshot 3): `AssetForm.tsx` dropzone + "Choose Files" + separate
  "Take a photo / Choose File" — redundant pre-S2 UI. S2/SG-048 photo-first replaces it.
- Chat dead-end (screenshot 4): `ChatPage.tsx:35-44` renders raw `consent_disabled` + disabled Send;
  AI OFF by default (SG_PROVIDER_ID=fake, SG_CONSENT=false); no pointer to Settings → consent.
  Needs D62 (consent + provider key) for S3; guidance copy is the gap.
- Nits: `AppHeader.tsx:62` "Total: 1 items" grammar; title attr clarifies page-count not household
  total. Pills include full 6-category set in table density vs top-5+All per DQ1 — minor.

## Filing (destination slices)

| ID | Issue | Destination |
|---|---|---|
| FB-1 | Toothpaste/any sourceless asset shows empty well + empty table thumb, no fallback icon | New UI-polish slice SG-054 (fallback icon, e.g. Lucide `Package`, both densities) |
| FB-2 | White legacy top nav stacked over dark token header (double wordmark) | New UI-polish slice SG-054 (remove/merge legacy `Nav` into token shell; `App.tsx:11-47` → tokens or delete) |
| FB-3 | Capture/Chat/Settings/Inbox/Planning/Review/AssetDetail still light hard-coded styles | New UI-polish stage SG-055+ (route-by-route token migration; catalog shell is the reference) |
| FB-4a | Table + pill-row horizontal cutoff on narrow screens | SG-054 (scroll container + responsive pills) |
| FB-4b | Capture duplicate file inputs | S2/SG-048 (photo-first capture replaces it; do NOT polish the old UI separately) |
| FB-4c | Chat `consent_disabled` dead-end with no guidance | S3/SG-049 (needs D62) + one-line Settings pointer in the same slice |
| FB-4d | "Total: 1 items" grammar | SG-054 one-liner |
| FB-4e | Toothpaste "Uncategorized/Source Only/blank specs" | By construction until S3 AI derivation (SG-049); no separate slice |

## Order

SG-054 (shell + fallback icon + overflow + grammar) → S2/SG-048 (fire word owed) →
S3/SG-049 (needs D62) → SG-055+ (remaining routes to tokens).
SG-054 touches no DB/host/secret — safe before S2. S2 touches the live SQLite migration (G-K3).
