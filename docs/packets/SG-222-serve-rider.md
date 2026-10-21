# SG-222 — serve rider: put the SG-221 drawer surfacing live (one rebuild + one recreate + verify)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Echo requested ref and actual resolved commit separately.
**DATABASE: read-only probes** (`GET /v1/health`, served-asset GETs, DB sha/migration-head reads; zero writes). **Restart: exactly ONE rebuild + ONE recreate of the app service** (precedent SG-214/SG-210/SG-206; lane-socket `docker` scoping per packet).
**Autonomy: L2** (one retry, root-cause only). Authority: standing 2026-09-28 close-deploy directive + D-22 standing close-release rule + owner message "I want to see the test results in the app" (this serve exists so the owner can open the pilot renders live).

Authoring date (metadata, never a gate): 2026-10-21.

## Why this exists

SG-221 linked the 3 pilot scene renders and taught the drawer Scene tab to show them — proven on the unserved candidate (suite 298/298). The served container still runs the pre-SG-221 image, so the owner cannot see any of it. This rider rebuilds, recreates once, and verifies the served bytes carry the SG-221 change — then the owner opens Miso / Costiță and sees the renders in the Scene tab.

## Handed-over facts (expected — re-verify at execution, `PB-1`)

- Candidate: `0779966..4c7ac42` delta = SG-221 only (5 product/test paths: `assets.py` +1 key, `types.ts` kind, drawer scene branch, 2 test files) + `docs/worklogs/SG-221_*`. Product delta since the SERVED image (`98f8af1f`, SG-214): SG-221 only — verify live (`git log` served-image commit vs HEAD), report difference either way.
- Lane: `RUN_BUDGET_S=2100` (`/etc/dispatch/storagegenie.conf`, read-only). Health probe: `GET http://127.0.0.1:8003/v1/health` must read `{"status":"ok","db":"ok","storage":"ok"}` before AND after (delta none). Precedent shape: SG-214 (16 s build + 1 s recreate, served==in-image `cmp` 0 ×3, DB sha identical ×3, focused suite, smoke skipped with stated reasons — same allowances apply here).
- Marker: the served bundle must read the SG-221 change (serializer key present in the served code / served JS bundle hash moved off the SG-214 value `8bab60ce…` — re-derive live, never inherit).

## G1 — rebuild + one recreate + verify

- ONE lane-scoped build + ONE recreate of the app service (named units only — read the lane conf, never guess names). Zero other restarts; a second attempt of either is a STOP (`PB-2` denial path: disclose verbatim, do not route around).
- Verify: health ok/ok/ok pre+post with zero delta; served bundle hash differs from the SG-214 value AND `cmp` byte-identical against a fresh in-image build (3 reads); DB sha + migration head identical pre/post (read-only); drawer Scene-tab rule present in the SERVED bytes (grep the served bundle for the `scene-image` test id / `scene_render` predicate — the served-filesystem read the packet allows).
- Report container/image/bundle shas, DB reads, elapsed vs ≈400 s (Architect record, `G-A9` uncalibrated; SG-214 took 457 s). Browser smoke: same packet-allowed skip as SG-214 ONLY with the same 4 stated reasons re-verified live, else drive it.

## Constraints

- **Money:** $0 — zero billed calls (reads + build + recreate + local probes only). Stated.
- **Scope ceiling:** serve ONLY — evidence ONLY `docs/worklogs/SG-222_*`. Zero product/config/test/DB bytes; no secret in any artifact; reads: lane socket + `localhost` GETs + one container-filesystem read under the byte-proof allowance (+ `git`); exactly the two named issuances, no second attempt.
- `PB-2`: any denied privileged operation STOPS the whole slice — report-and-leave, never route around. `PG-PR-03/04/06/10`: the two issuances are the ONLY privileged acts; the report states how the code became live (this rebuild), runtime-vs-budget with units, and actual-vs-expected; restart discipline explicit.
- Hang bounds: reads 120 s; build 600 s; recreate 120 s; probes 120 s; idle kill never approached.
- Simplicity: one rebuild + one recreate + proof; no new machinery. Excluded (stated): any product change; backfill; second attempt; browser-driven sweep (packet-allowed skip only with re-verified reasons).

## Acceptance criteria

- **A1:** ONE build + ONE recreate, both named with shas; served bundle moved off the SG-214 value AND `cmp`-clean vs in-image build (3 reads); health ok/ok/ok pre+post, delta none; DB sha + migration head identical.
- **A2:** SG-221 rule read point present in SERVED bytes (`scene-image`/`scene_render` in the served bundle); live asset route for a pilot asset returns its render with `source_kind` (curl the served port, ids quoted).
- **A3:** report `docs/worklogs/SG-222_report.md`; elapsed vs ≈400 s; constraints answered on explicit lines; FIRST/DURING/REMAINING; FIRST token `SG-222`.
- **A4:** notes-ref receipt: FIRST line exactly `Dispatch-ID: SG-222 | Report: docs/worklogs/SG-222_report.md` + `Work-HEAD` recorded, pushed + read back. Never the retired finalizer. Exact commands (run after the report commit, on the work HEAD):
  - `git log --format=%H -n 1 HEAD`
  - `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-222 | Report: docs/worklogs/SG-222_report.md" <work-head>`
  - `git push origin refs/notes/storagegenie-coder-reports`
  - `git push origin automation`
  - Read back on the remote (mapped fetch of the notes ref) and commit the verbatim transcript as `docs/worklogs/SG-222_receipt.log`.

Guards invoked: PG-EV-02/03/08; PG-IC-01/07; PG-PR-03/04/06/10. Stop follows `PB-6`.
