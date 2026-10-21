# SG-222 audit — serve rider: SG-221 drawer surfacing live (one rebuild + one recreate, byte-proven), rated 98

Immutable audit: base `d221db0` → work `45a8f69` (serve evidence) → report `a5ea650` → receipt `6a656ee` (transcript + mapped read-back; Work-HEAD a5ea650). Local `--ff-only` to the exact tip (`6a656ee` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-222 exit=0`. Receipt note `Dispatch-ID: SG-222 | Report: docs/worklogs/SG-222_report.md` IS on the remote — own read-back finds `a5ea650` via `git log --notes`. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — seventh clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **ONE build + ONE recreate, both exit 0, zero denials:** build log shows manifest `d6c6a106…` (27 s); recreate log shows container `f419758d…` StartedAt 19:55:22Z RestartCount 0 (2 s). No second attempt, no other restart.
- **Served bytes == candidate bytes:** `cmp` rc 0 ×3 (index.html `345bbe8c…`, JS `43c05c51…` 321283 B, CSS `c3b58cda…`); JS moved off the SG-214 value `8bab60ce…`; CSS byte-identical (expected — SG-221 touched no CSS). Container Image == build manifest `d6c6a106…`.
- **SG-221 read points live in served bytes:** `scene-image` 0→1, `scene_render` 0→1 on live GETs, with the exact compiled branch quoted (`data-testid:"scene-image"`, `source_kind==="scene_render"`); honest fallback retained. Live asset routes on the served port: Miso returns its render, Costiță returns both renders, all `kind=scene_render`; all three render files GET 200 `image/jpeg` with shas matching the committed pilot artifacts (`41d619db…`, `ce4794a2…`, `f3d56bfb…`).
- **Health + API controls:** ok/ok/ok pre+post, delta none; SPA routes + households control unchanged.
- **DB (F-SG222-1, the honest miss):** main-file sha moved by the SQLite WAL checkpoint on clean container stop (WAL 210152 B → 0 B) — NOT a slice write (every probe read-only, WAL already drained before any post query). Logical identity proven: 28 tables, identical per-table counts (asset_evidence 17, evidence 21, provider_call 33, audit_event 94), same alembic head, the 3 link rows present. A1's literal sha sub-clause is NOT met and is NOT claimed met — disclosed with the proof that replaces it. No deduction: the miss is physics under the packet's own read-only rule, and the packet's intent (no slice-caused row change) is proven.
- **Tests:** focused drawer 18/18 + serializer 1/1 green on the served tree; full suite not re-run per D443 (SG-221 ran 298/298 on this exact tree 7 minutes earlier, zero product bytes changed here) — stated, not silent.
- **Scope:** 12 files, all `docs/worklogs/SG-222_*`; $0; secrets gates EMPTY (literal + broadened key-value rc 1).

## Rating

**Holistic: 98/100, no flag.** One build, one recreate, byte-identity proven three ways, read points live on the served port with matching shas, and the one unachievable sub-clause disclosed with the inventory that proves the intent instead of a smoothed-over claim. `deduction_attribution`: empty. `slowest_waste`: `none` — every CO-79 phase output was used. Guards: PG-EV-02/03/08; PG-IC-01/07; PG-PR-03/04/06/10.

## Dispositions

| Item | Destination |
|---|---|
| SG-221 drawer surfacing live (image `d6c6a106`, container `f419758d`) | Owner opens Miso / Costiță → Scene tab — the deliverable this whole arc was for |
| WAL-checkpoint sha movement | Recorded (F-SG222-1) — future serve packets write the expectation as inventory-identity, not file-sha, when a WAL is pending at admission |
| Render scripts in the image (non-runtime) | Recorded — runtime delta stays SG-221-only; no action |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
