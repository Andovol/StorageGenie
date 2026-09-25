# SG-118 — Group B UI batch: six leftover threads, one sweep, served

- **Dispatch-ID:** SG-118
- **Coder:** `opencode`
- **Effort:** `high` — read from the process arguments (`opencode run --auto --dir /home/andrei/StorageGenie --variant high`)
- **Model:** `unknown` — no `--model` flag is present on argv and no provider metadata is readable; the CLI default is the model (per policy). Not guessed.
- **Contract (verbatim echo + source path):** `recorded 0.36.0 == published (a9324d5)` — source `/home/andrei/storagegenie-contract/VERSION` = `0.36.0`; `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `a9324d5e1782384c036c1411ec8adac6bb2acaa1`; `sha256sum RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.
- **BASE_REF:** `origin/automation` → **BASE_RESOLVED:** `5b501b055391b8f9f90975e4689eb1d614404977` (== start HEAD; two fields, never one).
- **WORK_HEAD:** `__WORK_HEAD__` (set by the docs-only receipt commit below).
- **DATABASE:** none touched (behavioural proofs on temp DBs / read-only live reads) · **Restart:** exactly ONE recreate (D12-authorized) · **Deploy:** rebuild + recreate + verify, this slice.
- **Spend (real $):** **$0.000000** — zero provider calls; no metered path.

## Premises re-verified against the tree (a difference is a finding, not an obstacle)

| Packet premise | Reality on the tree | Action |
|---|---|---|
| F-SG105-3 skeleton "still 3/4" | `ProductCardSkeleton.tsx:17` had `aspectRatio: "3 / 4"` while `ProductCard` is content-sized (SG-105 G4) — a real gap (loaded card shorter than its skeleton) | Fixed; fail-then-pass |
| `.text-primary` at `tokens.css:119` low contrast | Same dark maroon in both themes: light ≈9.87:1, dark ≈1.76:1 on `--card` | Dedicated `--link` token + `.text-link` |
| `InboxPage.tsx:45` carries an inline width | **FALSE** — `InboxPage.tsx:45` is a `display:grid; gap:8` div; InboxPage rides `PageContainer` since SG-105 | Reported; not "fixed" |
| `ReviewPage.tsx:55` carries inline width | Confirmed (`padding:24, maxWidth:1100`) | Converted to `PageContainer` |
| `CatalogPage.tsx:75` / `CatalogToolbar.tsx:18` pill edge | Confirmed: counts merged per display, filter key kept the first-seen raw key | Per-raw-key pills; fail-then-pass |
| `ExpiryPage.tsx:188-197` raw `asset_id` link text; engine carries no display names | Confirmed; `ExpiryUnresolvedRow` = `{ asset_id, reason }` only | Frontend-only label; no backend widening |
| `local_store.py:12` keeps SOURCE suffix for JPEG bytes | Confirmed; `_thumbnail_bytes` emits JPEG for jpeg/heic/heif, reader serves `image/jpeg` | `thumbnail_path` always `.jpg`; fail-then-pass |

## G0 — F-SG105-3 (gap remained: wrong ratio)

The skeleton was complete and pinned but carried a fixed `aspectRatio: "3 / 4"`; `ProductCard` has none (content-sized), so loading→loaded jumped height. Removed the pin in `ProductCardSkeleton.tsx` and rewrote the pin at `catalog.test.tsx` to assert `skeleton.style.aspectRatio === ""` (+ aria-hidden + 3 pulses). Fail-pre: `ProductCardSkeleton > …` FAIL. Pass-post: pass. **No manufactured change** — a wrong ratio was genuinely present.

## G1 — link contrast F-SG105-4 (decision forced by measurement)

Measured `.text-primary` (`tokens.css:119`, `2 41% 30.6%`) against the surfaces its instances sit on:

| surface | contrast |
|---|---|
| light card | 9.87:1 |
| light background | 9.44:1 |
| dark card | **1.76:1** |
| dark background | 1.76:1 (primary) |

Light is fine; dark is far below WCAG AA. **Decision: a dedicated token, not a scoped per-link override** — `--link` (`:root` = `2 41% 30.6%`; `.dark` = `2 41% 72%`, ≈7.49:1 on card / ≈8.33:1 on background) plus `.text-link { color: hsl(var(--link)); }`. A scoped treatment would have duplicated the value in every file; twiddling `--primary` itself would have broken the active-pill pair (`bg-primary` + `text-primary-foreground` are used together across CatalogToolbar/ProductGrid/drawer). Converted every link instance: `InboxPage`, `ReviewPage` (back link + split children), `ExpiryPage` (row + unresolved), `ChatPage`, `CatalogToolbar` (Delete + Clear all), `AssetDetailPage`. Pinned fail-then-pass in `theme.test.tsx` (per-surface ratio ≥ 4.5 and dark primary < 4.5) plus class assertions in the Inbox/Expiry/Chat/shell tests. (Note: `CatalogToolbar.tsx:224` Delete carried inline `color:"inherit"` that already neutralized the class; converted for consistency.)

## G2 — widths sweep F-SG105-5 (enumerated on the target)

**My enumeration (differs from the packet):** the hand-rolled **page** wrappers were 6 route files — `ReviewPage.tsx:55` (1100), `AnalyticsPage.tsx:61` (900), `ChatPage.tsx:74` (900), `PlanningPage.tsx:64` (900), `AssetDetailPage.tsx:328` (900), `SettingsPage.tsx:14` (padding only; its card-level `maxWidth:520` at `:29` is a component dimension). Already shared before this slice: Inbox/Capture (SG-105), Expiry (SG-108), Catalog (`AppShell`). **Before: 6 → After: 0** hand-rolled route wrappers; `PageContainer` importers now 9 route files. Non-page component dimensions left alone (`ProductGrid` cell `maxWidth:200`, `ItemInspectorDrawer` panel/viewer constants, `SettingsPage` card `:29`) and reported, not swept. Pinned by a new sweep test in `theme-adoption.test.tsx` that mounts all six and asserts `.page-container` max-width 1100 centred (fail-pre: it FAILs).

## G3 — pill edge F-SG105-6 (multi-key fixture decides)

The old code merged counts by display label and kept the **first-seen** raw key, so a display fed by two raw keys showed a count it could not filter. Fixture `{ unknown: 2, Uncategorized: 2 }` exposes it: both normalize to `Uncategorized` and, with equal counts, produced identical labels from different keys. **Decision: one pill per RAW `asset_type` key, sorted deterministically; never merge across keys.** The server filter is single-valued (`assets.py:215`, `Asset.asset_type == asset_type`), so a merged pill would misstate its own filter — per-key pills are the only honest aggregation. Labels stay the display vocabulary; when two raw keys would render the same label, the later (sorted) one is disambiguated with its raw key (`Uncategorized · unknown (2)`). The existing `Uncategorized (1)` vocabulary test still passes; the collision fixture pins both pills and each one's exact `asset_type` call, fail-then-pass.

## G4 — unresolved rows F-SG108-1 (frontend-only label, engine untouched)

`ExpiryUnresolvedRow` carries only `{ asset_id, reason }` (`api/types.ts:343`), so no engine display name exists and none was invented. The row link now renders the human reason label plus a short-id affordance (`No date · #abcdef`); the full `asset_id` stays in the `href` (and a `title`), never as visible text. Pinned fail-then-pass in `ExpiryPage.test.tsx` (long-id fixture: text has reason + `#last6`, text excludes the full id, href carries it). Backend untouched.

## G5 — thumbnail suffix F-SG110-1 (writer + reader move as one, `PG-SC-02`)

`_thumbnail_bytes` (`evidence_service.py:139-156`) emits JPEG for `image/jpeg`/`image/heic`/`image/heif`; the reader already serves `media_type="image/jpeg"` (`evidence.py:120`). `local_store.thumbnail_path` now always appends `.jpg`. Post-change call sites (shared function): writer `evidence_service.py:202 tp = thumbnail_path(rel, size)`; reader `evidence.py:117 tp = thumbnail_path(ev.storage_key, size)`. Proven through the **real writer** with a HEIC-suffixed source fixture: focused test asserts `thumbnail.suffix == ".jpg"` and JPEG magic `\xff\xd8\xff` (fail-pre: 2 failed / 28 passed; pass-post: 30 passed). **Orphan policy: leave.** Old `_thumb<size>.<srcext>` artifacts are inert once nothing reads them; migrating means renaming files inside `/data/storage` — a declared sensitive surface (`G-K3`) and a production write the packet forbids, with nothing gained. Bound: cleanup belongs to a future storage-maintenance/GC slice. Follow-up (reported, not widened): PNG/WEBP sources still yield PNG/WEBP bytes under a `.jpg` name served as `image/jpeg` — a pre-existing wire inconsistency (the reader already claimed JPEG); making `_thumbnail_bytes` flatten them too, or making `thumbnail_path` media-type aware, would close it, but `evidence_service.py` is read-only under this ceiling.

## G6 — rebuild + exactly ONE recreate + served proof

One rebuild (`BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`, exit 0, 10:17:10Z→10:17:28Z) then exactly one recreate (`docker compose up -d backend`: Recreate→Recreated→Started). **Container id changed** `1acbe40836d0…` → `16a07ae1af25…` (the authorized proof; `RestartCount+1` never asserted — M42). Image `3905a75aed70…` → `b92210feb120…`. Served bundle `index-XGj8xV3t.js` (317188 B, `65736eec…`) → `index-CYlI1-ao.js` (317045 B, `f15d01cc…`); loopback bytes == in-image bytes; route/code markers `text-link` 0→9 and CSS `--link` 0→3. Alembic `20260924_sg114_relation` unchanged; 28-table counts byte-identical (`a6ab0e07…`, delta 0); health 6× exact `{"status":"ok","db":"ok","storage":"ok"}`; gate 301/401; `/expiry` 200 and `/v1/assets?household_id=…` 200 through the fresh server (GET only). Post-restart sweep waived per `PG-DP-02` (restart-gated); substitute authority = in-process vitest/pytest pre-restart + these targeted live probes.

**Containment (`PG-PR-06`, per leg, units):** G0–G5 ~240 s (budget 1200 s); G6 ~90 s (budget 1200 s); overall ~460 s wall clock (budget 1200 s). No command killed; none hung.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| F-SG105-3 closed or fixed fail-then-pass; no manufactured change | **MET** | wrong ratio present; removed; 9-FAIL-pre → pass-post |
| Contrast decided by measurement + pinned; widths before/after quoted; pill edge on multi-key fixture | **MET** | 1.76:1 forcing measure; 6→0 widths; `{unknown,Uncategorized}` fixture |
| Unresolved rows human-labelled, asset_id in href only (no silent widening) | **MET** | `No date · #abcdef`; href carries full id |
| Thumbs carry JPEG suffix through real writer; reader sites quoted; orphan policy decided | **MET** | HEIC fixture `.jpg` + JPEG magic; two call sites; leave + reason |
| Exactly ONE recreate; bundle/health/gate/alembic/counts/`/expiry`+catalog 200s | **MET** | container-id change; all AFTER values above |
| $0; no production writes; no writes outside ceiling; no vacuous pass | **MET** | temp DBs only; diff within ceiling; 9 seen-to-fail gates |

**Vacuous-pass check (`PG-EV-01`, loudly):** every new/changed gate was seen to fail on the unchanged source at its own assertion (9 frontend failures; 2 backend failures), so none can pass vacuously. **Where this slice is weaker than it looks:** (a) the dark `--link` value is a chosen tint, asserted by computed WCAG ratio from the token values, not a pixel-rendered accessibility audit; (b) G2 converts 900px pages to the shared 1100px width — a real layout change for Analytics/Chat/Planning/AssetDetail, reported as a design call; (c) the G5 orphan policy intentionally leaves inert old-suffix files on disk.

## Design calls (mine, reported)

- **G1:** dedicated `--link` token over scoped per-link styles or `--primary` surgery (protects the active-pill pair).
- **G3:** per-raw-key pills over merged-by-display (a merged pill cannot express its own single-valued filter).
- **G2:** kept the `SettingsPage` card's `maxWidth:520` (component dimension) while moving the page wrapper to `PageContainer`.
- **G5:** leave old-suffix thumbnails (no sensitive-surface write); don't widen into the read-only writer module.

## Findings / disagreements

- **F-SG118-1:** packet's `InboxPage:45` inline-width premise is false — InboxPage rides `PageContainer` since SG-105; `:45` is a grid gap div. Real set is the 6 route files enumerated in G2.
- **F-SG118-2:** `_thumbnail_bytes` does not emit JPEG for PNG/WEBP sources, so "always JPEG suffix" makes the name match the served type but not the bytes for those two source types; pre-existing (reader hardcoded `image/jpeg`). Follow-up outline: extend the JPEG flatten branch to png/webp or pass media type into `thumbnail_path`. Not widened (read-only module).
- **F-SG118-3 (out of scope, reported):** `CatalogToolbar.tsx:224` Delete's inline `color:"inherit"` had already neutralized its `text-primary`; class converted for consistency only.

## Receipt note on the notes ref (M20-corrected block)

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on the work HEAD; notes ref pushed; verified against the explicitly fetched, MAPPED ref. Existing-note refusal is a STOP; precheck showed no existing note. Executed output is pasted by the docs-only receipt commit (section to be filled verbatim).

## Three UNCLEAR lines

- **FIRST READ:** whether "correct aggregation" for the pill edge meant merging counts per display with a deterministic key, or not merging at all. I chose per-raw-key pills because the server filter is single-valued, so any merged pill would advertise a count it cannot filter; the collision fixture pins it.
- **DURING EXECUTION:** whether forcing `.jpg` on every `thumbnail_path` was meant to cover PNG/WEBP sources too (whose writer bytes stay PNG/WEBP). I applied it to all (the reader already serves `image/jpeg`) and reported the residual bytes/suffix mismatch rather than widening into the read-only writer.
- **REMAINING:** the dark `--link` = `2 41% 72%` is a design tint validated by computed WCAG ratios; whether the owner prefers a different hue is a visual sign-off question. Orphaned old-suffix thumbnails remain on disk by decision.

note=yes
