# SG-221 — Show the pilot scene renders in the app: link 3 pilot renders to source assets + drawer Scene tab reads them (read-only surfacing, no new renders)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: sqlite live** (`/data/db/storagegenie.db` + storage volume — exactly 3 new `asset_evidence` link rows, grants D-27 + this owner message ("I want to see the test results in the app"), `PG-PR-10`). No UPDATE/DELETE of existing rows, ever; the 3 links reported with identifiers and left in place (`PG-EV-06`). No migration: `asset_evidence` + `Evidence.source_kind` already exist.
**Restart: none.** No serve in this slice — the serve rider that makes this visible live is the NAMED next slice (it owns the rebuild + recreate + verify; this slice proves unserved code, stated).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

The D-27 pilot stored 3 scene renders as `Evidence` rows (`source_kind="scene_render"`, SG-217 Miso + SG-218/SG-220 Costiță) that are NOT linked to any asset — the inspector drawer reads only `asset_evidence`-linked rows, so the app shows honest-empty Scene tabs. The owner wants to see the test results in the app. This slice links the 3 pilot renders to their source assets and teaches the Scene tab to show a linked render, honest-empty otherwise. No new renders, no new sends, no pipeline changes.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Drawer: `frontend/src/components/shell/ItemInspectorDrawer.tsx` — `ViewerTab` scene branch (`:271-275` honest-empty), `sourceUrl` pattern (`:143-146`, file route + `household_id`), `evidence` from `GET /v1/assets/:id` (`:78-88`). Tests: `frontend/src/components/shell/drawer.test.tsx` (`:127-133` scene honest-state, `:187-190` AI button sends nothing — that behavior MUST NOT change).
- Serializer: `backend/app/api/v1/assets.py` `_asset_to_dict` (`:107-125`) sends evidence WITHOUT `source_kind` — the drawer cannot tell a render from a photo until this slice adds the field (additive only: add one key, change nothing else — `PG-DP-01` permissive-only). TS type: `frontend/src/api/types.ts` `Evidence` (`:3-10`, no kind field — extend it).
- Evidence model: `backend/app/models/evidence.py` (`asset_evidence` join; `source_kind`, `scene_render` rows carry content sha256). File route: `GET /v1/evidence/:id/file` serves any same-household row with serve-time sha verification (`evidence.py:134-165`) — renders serve through the existing route, no new route.
- Pilot rows (criterion, not an inventory — derive live): the 3 `source_kind="scene_render"` Evidence rows created on/after the D-27 record date, each linked to the asset owning its source photo (ledger `input_hashes.photo_sha256` → source Evidence → `asset_evidence` → asset). Expectation (verify, report difference either way): SG-217 Miso render → Miso asset; SG-218 + SG-220 Costiță renders → Costiță asset. Exactly 3 links expected — more or fewer STOPS before writing (`PG-IC-08` either direction).

## G1 — link + serializer field (+ backend test)

- Derive the 3 links live per the criterion above; write exactly the 3 `asset_evidence` rows (ids quoted); re-read and confirm each render resolves through `_asset_to_dict` for its asset. Any 4th `scene_render` row from the pilot window, or any mismatch of photo→asset, STOPS (report, no write).
- Add `source_kind` to the evidence dicts in `_asset_to_dict` (one additive key; no other serializer change). Backend test: scene-linked asset serializes the kind, photo rows unchanged — fail-pre on base (field absent) → pass-post, both runs committed (`PG-EV-09`).

## G2 — Scene tab shows a linked render, honest otherwise (+ frontend tests)

- Scene tab: if the asset's evidence holds a `source_kind === "scene_render"` row, show it (`img` through the existing file-route pattern, `alt` names the asset + "context scene", `data-testid="scene-image"`); else keep the exact honest-empty copy (`scene-honest-state`). Cutout tab and both AI buttons UNTOUCHED — the buttons still send nothing (existing test keeps passing unmodified).
- Frontend tests: honest-empty when no render linked (existing test, still green) + render shown when a scene row is present (new test with a scene-kind fixture row through the mocked asset GET) + no-fetch assertion on the AI buttons retained. New test fail-pre on base (tab shows honest-empty despite the fixture — field absent) → pass-post; both runs committed.
- Full frontend suite once on the candidate; on the base only the new rows' FAIL half (`D443`). Backend suite: the serializer test file likewise; targeted, not whole-tree.

## Constraints

- **Money:** $0 — zero billed calls in this slice (no renders, no probes; reads are lane + repo + local test runners only). Stated, not silent.
- **Scope ceiling:** `backend/app/api/v1/assets.py` (one additive key) + its test; `frontend/src/api/types.ts` (Evidence kind) + `ItemInspectorDrawer.tsx` (scene branch only) + `drawer.test.tsx`; evidence ONLY `docs/worklogs/SG-221_*`. No migration; no restart; no new route; no secret in any artifact; no renders, no sends (asserted, not assumed).
- **Production writes:** EXACTLY the 3 derived `asset_evidence` link rows — counted both directions pre/post (linked-scene count 0→3 for the pilot assets, total link delta +3); any other write is a STOP. Rows left in place, ids in the report.
- Hang bounds: reads 120 s; suites 600 s each; idle kill never approached. Expected duration ≈600 s (Architect record, `G-A9` uncalibrated; SG-046/SG-167 same-shape drawer slices).
- Simplicity: link + one field + one tab branch + tests; no new machinery. Excluded (stated): CEAFĂ re-render; cutout pipeline; resolution pin; Generate-button wiring (still notice-only); provider routing; the serve rider (named next slice owns live proof).

## Acceptance criteria

- **A1:** 3 link rows derived live (photo→asset criterion quoted per link), re-read through the asset route showing `source_kind: "scene_render"`; pre/post link counts quoted; no other DB delta.
- **A2:** drawer Scene tab shows the render image for a linked asset and the exact honest copy for an unlinked one; cutout tab + AI-button behavior byte-identical (existing tests green unmodified).
- **A3:** backend + frontend tests fail-pre→pass-post, both runs committed (logs, not prose); full frontend suite green once on the candidate; backend serializer tests green; suite deltas quoted against base reds if any.
- **A4:** report `docs/worklogs/SG-221_report.md`; elapsed vs ≈600 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-221`.
- **A5:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-221 | Report: docs/worklogs/SG-221_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-221 | Report: docs/worklogs/SG-221_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-221_receipt.log`.

Guards invoked: PG-EV-02/03/05/06/09; PG-SC-05/09/12; PG-IC-01/07/08/09; PG-PR-01/03/10; PG-DP-01. Stop follows `PB-6`.
