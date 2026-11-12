# SG-318 report — plain words sweep W1–W10

First line: slice SG-318; model and effort read from process arguments: not visible, so I do not infer them; working directory /home/andrei/StorageGenie; remote git@github.com:Andovol/StorageGenie.git; BASE ref origin/automation; resolved BASE commit 0e04e0a96179bc26796ad4827da4f1c79a4b9f28; WORK_HEAD see publish hashes below (report commit).

Elapsed: start 1794511993, G0 1794511996–1794511997 (1s), W1–W5 commit 1794512326 (333s elapsed), W6–W10 commit 1794512430 (437s), G2 tests commit 1794513028 (1035s); total ~1040s to tests commit. Health 200 at start (1794511997) and 200 at end (1794512943) via `curl -s http://127.0.0.1:8003/v1/health`.

W1 — premise confirmed: ProductCard.tsx:227 `{item.category}` and ProductGrid.tsx:193 chip raw. Old `food_beverages` → new `Food & beverages` via `labelAssetType`. File: ProductCard.tsx, ProductGrid.tsx.
W2 — premise confirmed: AssetDetailPage.tsx:836 `String(a.value)` showed `[object Object]`, raw `food_beverages/ACTIVE`, rows `Detail`. Old `[object Object]/food_beverages/ACTIVE/Detail` → new `7 Nov 2026/Food & beverages/Live/Kind of item/Status/Unit` via `plainDetailValue` + shared `formatPlainDate`. File: AssetDetailPage.tsx.
W3 — premise confirmed: AssetDetailPage.tsx:858 ISO `2026-11-12T19:06:54.601245`, `Asset Create/Asset Accepted`. Old ISO/`Asset Create` → new `Today, 19:06`/`Added`, `Accepted`, `Date entered by you` via shared `formatJobDate`. File: AssetDetailPage.tsx.
W4 — premise falsified in AssetDetailPage; true source EvidenceGallery.tsx:51 `Thumbnail unavailable` at 11px. Old `Thumbnail unavailable`/11px → new `No photo yet`/13px. File: EvidenceGallery.tsx (out-of-scope, named; packet said same file).
W5 — premise confirmed: ItemInspectorDrawer.tsx source/scene `<img>` no onError, broken icon + alt. Old broken `<img>` → new `No photo yet.` fallback on load error too. File: ItemInspectorDrawer.tsx.
W6 — premise confirmed: `Untitled asset` (types/product.ts:30), `Untitled item` (ExpiryPage/CatalogPage/PantryPage/etc), `noname` stem from backend `_deterministic_display_name`/`_display_name`. Old `Untitled asset/Untitled item/noname` → new `Unnamed item` (value of `UNNAMED_ITEM`/`UNTITLED_ASSET_NAME`). Frontend fixed in scope files + types/product.ts (named extra); backend `noname` stem reported and left (no backend file); out-of-scope `Untitled item` literals in CatalogPage/PantryPage/OpenedCountdownSection/AssetCard left as REMAINING. Files: types/product.ts, AssetDetailPage.tsx, ItemInspectorDrawer.tsx, ExpiryPage.tsx, InboxPage.tsx.
W7 — premise confirmed: ExpiryPage.tsx:252 `{row.expiry_date}` ISO. Old `2026-11-07 · Expiry date` → new `7 Nov 2026 · Expiry date` via shared `formatPlainDate`. Shared formatter: `formatPlainDate` in labels.ts for W2+W7 date-only (`7 Nov 2026`); `formatJobDate` in labels.ts for W3 datetime (`Today, 19:06`). File: ExpiryPage.tsx.
W8 — premise confirmed: ExpiryPage.tsx:32 `TIER_LABELS` + pill for every tier; Long lead under Safe heading. Old pill for Upcoming/Long lead/Safe → new pill only for `Use first`/`Use soon` (critical/urgent); no pill otherwise. File: ExpiryPage.tsx.
W9 — premise confirmed: labels.ts:17 `PENDING`→`In progress`. Old `In progress` for PENDING → new `Not started`; `In progress` only for RUNNING/PROCESSING/IN_PROGRESS/RETRYING. File: labels.ts.
W10 — premise confirmed: labels.ts:142 lacks VALIDATING_INPUT/ANALYZING_WITH_AI/BUILDING_CANDIDATES. Old `Validating input/Analyzing with ai/Building candidates` → new `Checking your upload/Reading the photo/Making items`. Why: upload (what you sent), photo (what AI reads, no AI word), items (owner word, not candidates). File: labels.ts.

Test changes: new frontend/src/routes/sg318-plain-words.sg318.test.tsx (10 tests, one per row). Older updated old→new, none loosened: ExpiryPage.test `Upcoming, Long lead, Safe → no pill` + length 2→3 (reminder pill); JobCard.test `In progress → Not started` for QUEUED; EvidenceGallery.test `Thumbnail unavailable → No photo yet`; AssetCard.test `Untitled asset → Unnamed item`; drawer.test `Untitled asset → Unnamed item`; product.test `Untitled asset → Unnamed item`; AssetDetailPage.test `Asset Update → Updated`.

Gate counts: eslint only `App.household-nav.test.tsx` fireEvent unused (1 error, known) — proves via `eslint src` output in SG-318_eslint.log; tsc rc0 no output — SG-318_tsc.log; build 1973 modules, built in ~3s into scratch — SG-318_build.log; backend host 805 passed, 2 deselected — SG-318_backend.log; image proof 2 passed, 6 deselected — SG-318_image.log; frontend full 55 files, 477 passed, 0 failed — SG-318_frontend.log; SG-318 new 10/10 pass — SG-318_pass.log; base 10/10 fail — SG-318_fail.log; 8-file set twice 84/84 both runs — SG-318_twice_run1/2.log.

Changed files: frontend/src/lib/labels.ts, frontend/src/components/catalog/ProductCard.tsx, frontend/src/components/catalog/ProductGrid.tsx, frontend/src/routes/AssetDetailPage.tsx, frontend/src/components/shell/ItemInspectorDrawer.tsx, frontend/src/components/EvidenceGallery.tsx, frontend/src/routes/ExpiryPage.tsx, frontend/src/routes/InboxPage.tsx, frontend/src/types/product.ts; tests: 6 older + 1 new; logs: 10 SG-318 logs.

Contract: I received no contract version line.

UNCLEAR: none new. REMAINING: W4 touched EvidenceGallery.tsx (packet said AssetDetailPage; out-of-scope named); W6 backend `noname` stem needs backend byte (reported, left); W6 out-of-scope `Untitled item` literals in CatalogPage.tsx:313, PantryPage.tsx:190, OpenedCountdownSection.tsx:37, AssetCard.tsx:54 `no image` left for follow-up (touching would be PG-EV-03 STOP).

A1 — W1–W10 met except W6-backend-stem and out-of-scope literals reported with files; shared formatter named (formatPlainDate for W2/W7, formatJobDate for W3).
A2 — FAIL on base 10/10, PASS on candidate 10/10; older named old→new above.
A3 — gate green: eslint only known error, tsc rc0, build into scratch, host 805 + image 2 green, frontend 477 0 failed, 8 files twice 84/84; exact counts in logs.
A4 — zero backend/migration/Dockerfile/compose/lockfile/dependency/.env/live-DB/stored-files/host/provider/container/deploy bytes; frontend/dist untouched (build went to scratch); no /tmp (scratch only output/SG-318-scratch, npm cache there); tree clean except output/ (output/ holds only prior SG-301-scratch + dispatch, untouched); scratch output/SG-318-scratch removed before report.
A5 — preflight Server section + rc0, health 200 start/end; phase seconds above.
A6 — PB-3 vacuity: checked old strings absent (food_beverages/[object Object]/ISO/Thumbnail/broken img/noname/Untitled/Long lead pill/In progress for PENDING/Analyzing with ai), no test passes on base (10/10 fail), no loosened assertion (all old→new quoted, lengths tightened only where reminders demand 3), suite red would be 2 fails fixed.
A7 — see last line.

Verification: PASS
