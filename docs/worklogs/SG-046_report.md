BLOCKED: G2's card/table-click wiring requires editing `frontend/src/components/catalog/ProductCard.tsx`
and/or `frontend/src/components/catalog/ProductGrid.tsx`, neither of which is in the packet's scope
ceiling — so the drawer ships unmounted and the slice stops per the packet's own STOP rule.

SG-046 — inspector drawer (opencode, medium)

Dispatch-ID: SG-046 · Coder: opencode · Effort: medium (`--variant medium`, from process args) ·
Model: `unknown` (no `--model` on argv; per policy the CLI default is the model and is omitted —
provider banner in `output/dispatch/SG-046.log` prints `deepseek-v4.1-flash`, recorded as provider
metadata, not an argv fact) · Contract: 0.27.0
BASE REF: `origin/automation` — BASE COMMIT (resolved): `ec22539d00360a3fdbad7f1af7d8fd21800eb995`
(start HEAD; worktree clean at start).
WORK_HEAD: the commit carrying this report + worklog + verify log (resolved hash published in the
receipt note; labelled work commit, not a tip, per CO-55c).
Work dir: `/home/andrei/StorageGenie` · Remote: `git@github.com:Andovol/StorageGenie.git` (as on host).
Spend: `$0` metered · Network: none (AI OFF, no npm, no fetch beyond the receipt git refspecs) ·
DB: none · Restart: none.

## (a) Issues / deviations / surprises

- **STOP — ceiling collision (`PG-IC-01`, packet-caused).** G2 says "card/table clicks open the
  drawer (replacing detail-route nav on those clicks)". Verified reads: the grid click destination
  is `ProductCard.tsx:73-74` (`<Link to="/assets/:id?...">`) and the table row click destination is
  `ProductGrid.tsx:99-100` (`navigate(`/assets/${item.id}?...`)`). **Neither file is in the packet's
  scope ceiling**, which names only `CatalogPage.tsx` (drawer-state hunk only). `CatalogPage.tsx`
  renders `<ProductGrid>` and owns no click event for a card or row. The requirement therefore names
  a behaviour no ceiling file can enable — exactly the case the packet's own line covers: *"Every
  requirement above names a file the ceiling enables it; if you find one that does not, STOP and say
  which."* **Destination files: `frontend/src/components/catalog/ProductCard.tsx` and
  `frontend/src/components/catalog/ProductGrid.tsx`** (an optional `onSelect?` prop, additive,
  no behaviour change when absent). I reverted my out-of-ceiling edits to those two files and to
  `CatalogPage.tsx` and shipped the in-ceiling remainder; the drawer component ships complete and
  fully tested but is not mounted from the catalog (G2 unshipped).
- **Premise correction (F-1).** The packet's G2 premise that `CatalogPage` owns card/table
  navigation is false. The packet's `Why-this-exists` paragraph is correct that cards/rows navigate
  to the old detail route; it is the ceiling that does not reach the code holding that navigation.
- **`ProductGrid`/`ProductCard` revert proof.** `git diff --name-only` shows neither after revert.
- **F-3 cleanup shipped.** `CatalogToolbar.tsx` stale note removed; `shell.test.tsx` updated to
  assert the real table (`role="table"`, name "Product results") and the note's absence.
- **Ceiling respected elsewhere.** No file under `backend/` touched; no migration; no new
  dependency; no `tokens.css` / `product.ts` edit; `AssetDetailPage.tsx` read-only.
- **Not a "pre-existing failure" claim anywhere.** No failure was reported as pre-existing.

## (b) Actions

Changed paths (all inside the ceiling):
- `frontend/src/components/shell/ItemInspectorDrawer.tsx` (new) — slide-over drawer, three viewer
  tabs with truthful empty states, source-photo file-route image, read-only observed rows, honest
  AI block (no request sent), collapsible raw JSON.
- `frontend/src/components/shell/drawer.test.tsx` (new) — 11 tests (open/close/Esc, focus in+out,
  tabs + honest states, PATCH payload + If-Match, passthrough category, read-only rows, AI no-request,
  raw panel, empty-evidence state).
- `frontend/src/components/shell/CatalogToolbar.tsx` — F-3 stale note removed.
- `frontend/src/components/shell/shell.test.tsx` — F-3 test updated to assert the real table.
- `docs/worklogs/SG-046.log`, `docs/worklogs/SG-046_report.md`, `docs/worklogs/SG-046_verify.log`.

Reverted (out of ceiling, disclosed): `frontend/src/components/catalog/ProductCard.tsx`,
`frontend/src/components/catalog/ProductGrid.tsx`, `frontend/src/routes/CatalogPage.tsx`.
Commits: fail leg (hollow context) then implementation then this worklog commit — hashes in the
receipt note. Push: `automation`. External/production effects: none.
Durations (UTC): start 15:08:46, end 15:18:07 → total 561 s (budget 2100 s overall; 27%).
  - premise reads + design: ~150 s (aggregate, ordinary 120 s per-command bound, none exceeded).
  - implementation writes: ~120 s.
  - suite+lint+build: ~90 s (well under the 600 s bound).
  - mutation run (3 caught, each reverted): ~85 s.
  - hollow run: ~30 s.
  - gates + commit/report: ~86 s.
Retry count: 0 (no re-dispatch of the slice). Test-command count: 7 (1 hollow, 1 green suite,
3 mutation single-files, 1 post-revert single-file, plus the drawer-only green pre-suite).
Provider-call count: 0. Health delta: none (no HEALTH_CMD run — no live service touched, no DB,
no restart; `PRODUCTION.md` trigger not fired by a frontend-only, read/write-through-existing-endpoint
slice; stated rather than omitted, CO-72). HIGHEST-IMPACT action: the STOP/revert of the
out-of-ceiling wire-up (it is what keeps the slice honest).

## (c) Verification

Artifacts (rendered DOM / committed outputs, never exits — `PG-EV-02`):
- Drawer test alone: `11 passed` (raw §3).
- Full suite: `20 files / 107 tests passed` (raw §3).
- `eslint src` exit 0; `tsc` exit 0; `vite build` exit 0 (raw §3).
- Hollow pre-change run: unresolved-import, 0 tests — LABELLED HOLLOW, not evidence (raw §2).
- Mutation run, each wrong value caught singly, each reverted to byte-identical original (raw §4):
  M1 tab label → 1 failed/10 passed · M2 PATCH payload key → 1 failed/10 passed ·
  M3 Esc handler → 1 failed/10 passed.
- Properties asserted (`PG-EV-05`): "Esc closes the drawer and focus returns to the invoking
  element"; "Save PATCHes display_name/asset_type with `If-Match`"; "AI click sends no request";
  "cutout tab states cutouts are not available" (raw §3).
- Gates (raw §5): backend diff empty · migration diff empty · dep diff empty · secret scan 0 ·
  no ignored file · nothing pushed to `storagegenie-evidence` · live spend `$0` · no live writes.
- `PG-EV-09`: both the hollow run and the mutation values are committed in
  `docs/worklogs/SG-046_verify.log`; the green run is in the same file.
- Vacuous-pass statement: G2's acceptance criterion ("card/table clicks open the drawer") is
  **NOT satisfied** — it is reported BLOCKED, never as a pass. The drawer tests exercise the
  component directly, so they are real, but they do not and cannot prove the unmounted wiring.
- INTENT (behaviour-changing item): code does render a drawer with honest empty states and a
  no-request AI block; the check expects those properties in the rendered DOM; the approved packet
  says G1's drawer + G2's click wiring — X and Y agree, **Z's wiring half is unreachable in-ceiling**
  and is stopped, not bent.
- TWINS: `AssetDetailPage.tsx` remains the deep-link editor; the drawer duplicates its PATCH shape
  deliberately (packet says "same pattern"), and the two now coexist rather than one replacing the
  other — stated so the duplication is not mistaken for drift.

## Receipt (note on the coder-reports notes ref)
Work committed and pushed to `automation`, worktree clean (CO-55). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (per this packet's M20-corrected block). The note was
added on WORK_HEAD, the notes ref pushed, the refspec fetched explicitly (`<ref>:<ref>`, M21), and
the `git notes --ref=… show <WORK_HEAD>` output is pasted verbatim in the delivery message (it cannot
live inside this file, which is itself the commit the note is attached to). If that `show` output is
absent, this step was not executed and should be called out loudly. Final line: `note=yes`.

## (d) UNCLEAR
- **FIRST READ:** whether the cards/rows already carried a selection hook the ceiling's `CatalogPage`
  hunk could invoke. Verified they do not — they own their own `Link`/`navigate` — which made G2
  unreachable in-ceiling and triggered the STOP.
- **DURING EXECUTION:** whether to ship the wire-up anyway as an additive optional prop and report the
  ceiling breach, or to revert and STOP. Chose revert + STOP per the packet's explicit
  "Anything else is a STOP" and its "if you find one that does not [name a ceiling-enabled file],
  STOP and say which"; shipping the breach silently was the failure mode the rule exists to prevent.
- **REMAINING:** (1) G2 wiring — needs `ProductCard.tsx` + `ProductGrid.tsx` added to a ceiling
  (`onSelect?: (id) => void`); (2) `CatalogPage` drawer-state hunk + query invalidation — prepared but
  reverted with the same collision, since an unmounted drawer's invalidation cannot fire; (3) SG-047
  import modal closes the wardrobe track; (4) delete control — still no slice assigned (DELETE route
  exists at `assets.py:229`, no UI ships).
