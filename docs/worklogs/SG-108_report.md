# SG-108 report — Expiry dashboard: /expiry route + nav reading the SG-107 engine, owns its refresh

**Dispatch-ID:** SG-108
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**Branch:** `automation`
**BASE_REF:** `origin/automation` → **BASE_RESOLVED:** `faf828e949ca3c6d655aecfdab4b75f395619411` (== start HEAD)
**WORK_HEAD:** `__WORK_HEAD__`
**Model / effort (CO-78, from process arguments):** argv = `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet>` → **model = CLI default** (no `--model` flag on argv; omitted per policy), **effort = `high`** (from `--variant high`).
**Spend (real $):** **$0.000000** — no metered call exists on any path (zero provider calls).
**Contract echo (verbatim):** `recorded 0.33.0 == published (b232b84; D129 adoption, G-L1 clean 2026-09-24)` — source path `/home/andrei/storagegenie-contract/VERSION` = `0.33.0`, `git -C /home/andrei/storagegenie-contract rev-parse HEAD` = `b232b845d74e89cb346c60fa4b9a40ec401c42dd` ("Contract payload 0.33.0"), `sha256sum RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload `RULES.sha256`.

## What shipped

- **New** `frontend/src/routes/ExpiryPage.tsx` — the blueprint §11.2 screen-7 urgency view: `PageContainer` + `useHouseholds` + `localStorage household_id` + `useQuery` gated on the effective household; urgency sections Expired → This week → This month → Safe, then Unresolved, then an Uncategorized line from the served analytics summary.
- **New** `frontend/src/routes/ExpiryPage.test.tsx` — 8 tests, fail-then-pass (both raw runs committed).
- **`frontend/src/api/client.ts`** — `fetchExpiryStatus(householdId, category?)` → `apiGet` on `/v1/plugins/expiry-tracker/status` (unset category is dropped by `buildUrl`).
- **`frontend/src/api/types.ts`** — `ExpiryStatusResponse` + row/tier/bucket/reason types mirroring the SG-107 route keys exactly.
- **`frontend/src/App.tsx`** — `NavLink to="/expiry"` (after Analytics) + `<Route path="/expiry" ... />`.
- **`frontend/src/components/shell/shell.test.tsx`** — the legacy-nav test updated (diff quoted below).
- **Refresh** — one frontend-inclusive rebuild + exactly ONE recreate + verify (D145 owned refresh).

Nothing else: `backend/` shows an **empty diff** (0 tracked lines; no untracked backend files) — quoted in the verify log. `CatalogPage`/`ProductCard`/token/other-route surfaces untouched.

## G1 BEFORE → G4 AFTER (raw values)

| Observable | BEFORE | AFTER |
|---|---|---|
| image id (`storagegenie-backend:latest`) | `sha256:8dce9eb2cec50309d858b9eb13259a77cb597ede1b9ec35762141f86d11f0781` | `sha256:6a555108f9a47a828db328162950e451f9c67aaae4d700ceb47e973a47e858ed` |
| container | `171e3d7ec196…` | `234b04b0f1e2c553439ce00b7fbcff30cecea1ab9e612a92702e22534f397d97` (healthy t=12s) |
| served bundle (loopback bytes) | `index-DlD86cZ6.js` 307014 B `6e0a3af7…` | `index-DAsiAK51.js` 312408 B `77c60463…` — **DIFFERED** (`cmp` ≠; CSS byte-identical) |
| in-image file sha (consumer-decode) | `6e0a3af7…` | `77c60463…` (loopback == in-image) |
| route-path literal `/v1/plugins/expiry-tracker/status` | `0` | `1` (the real new-route marker) |
| `No tier` literal | `0` | `1` |
| `Expiry` literal | `5` | `7` |
| alembic current | `20260923_sg100_enrich_snapshot` | `20260923_sg100_enrich_snapshot` (unchanged) |
| table count | 25 | 25 |
| counts | all 25 tables | **delta exactly 0** on every table |
| health | `{"status":"ok","db":"ok","storage":"ok"}` | same, ×6 |
| gate | http 301 / https 401 | http 301 / https 401 |
| app page `/expiry` | n/a | `200` (SPA index carries `id="root"`) |
| engine `GET /status` | 200 empty-zeroed (live 200/404/422 re-proven SG-107) | 200 empty-zeroed, unchanged |

## Findings / corrections (verified, not bent to match)

1. **PREMISE CORRECTION — the `"Expiry"` literal was never 0.** G1 measured **5** occurrences in the pre-existing served bundle (from `ExpiryEntryForm` labels, the Analytics "Expiry urgency" section, and the `expiry_date` field label). AFTER = **7**. The packet's "0→1 marker" is therefore false as stated; the honest consumer-decode marker is the route path literal `/v1/plugins/expiry-tracker/status` **0→1** (and `No tier` **0→1**), both quoted raw. The refresh leg still proves the served code changed while data stood still (image id + bundle name/size/sha all differ; counts delta 0).
2. **ENVIRONMENT — root filesystem is read-only.** `/` is mounted `ro,errors=remount-ro` (`/dev/vda1 on / type ext4 (ro,nosuid,relatime,discard,errors=remount-ro,commit=30)`). The first `docker compose build backend` failed (exit 1) with `failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/.tmp-default…: read-only file system`. The worktree (`/home/andrei/StorageGenie`) and `/tmp` remain separate **rw** mounts (verified with `mount`). This is **not** a denied privilege routed around: the image build is authorized by the packet, and no privileged operation was refused — the buildx **client-state** directory (`~/.docker/buildx`, on the ro `/`) was relocated to a writable path with `BUILDX_CONFIG=/tmp/opencode/buildx`; the build then succeeded (exit 0). Disclosed for the Architect.
3. **DNS — public hostname failed to resolve at G1 then recovered.** At G1 (`09:16:36Z`) `getent hosts storagegenie.dynv6.net` exit 2 and both public curls returned `code=000`; by G4 (`09:20`) the public http gate returned `301` again. The gate is therefore proven two ways: public DNS at G4 (301) and deterministically via `--resolve storagegenie.dynv6.net:80:127.0.0.1` → `301` + `https :443` → `401` (local nginx, ports 80/443 listening).
4. **F-SG107-1 ANSWERED (Architect-decided, implemented).** Unclassified assets stay outside the engine stream; the dashboard renders an `Uncategorized` line from the served `GET /v1/analytics/summary` (`categories.uncategorized`). Live shape on target verified: `categories.uncategorized = 6`, keys match the existing `AnalyticsSummary` type — no guessed number, never merged into the engine rows/summary.
5. **Design call — stronger `PG-SC-02` read assert.** The packet suggested mocking `../api/client` (AnalyticsPage precedent). I mocked `../hooks/useAssets` as suggested but deliberately did **not** mock `../api/client`; the test stubs `global.fetch` so the real `apiGet`/`buildUrl` run and the test asserts the actual request URL `/v1/plugins/expiry-tracker/status` with `household_id=` (and `category=` when the filter is set). Asserting a mocked fetcher call would not have proven the path; this does.
6. **Live household is honestly empty of expiry rows.** `GET /status` for the live household returns `rows: []` (no accepted-expiry classified asset); the empty-zeroed render is exercised in-process by the vitest fixture and the live page is served (200) — no fixture data was written live.

## G3 tests + gates

- New test file: **fail-then-pass, both raw runs committed.** FAIL (implementation absent, final test file) = `Failed to resolve import "./ExpiryPage"` (exit 1, 0 tests). PASS = **8 passed** (exit 0).
- Full frontend suite: **24 files / 199 tests passed**; `tsc` = No errors; `vite build` = built in 1.70 s (`index-DiBJBQbJ.js` 312.25 kB); `eslint src` = clean (exit 0).
- Backend suite untouched: **empty backend diff** (`git diff origin/automation -- backend/` = 0 lines; `git ls-files --others backend/` = empty) — not re-run.
- Secret gate: grep over the 6 changed/new files (`api[_-]?key|secret|passwd|password|bearer|private key|BEGIN …PRIVATE KEY|sk-…|ghp_|AKIA…|jina_…`) → **exit 1, 0 real matches** (quoted in the verify log).
- `PG-EV-01` seen-to-fail in-run: the committed FAIL run is the final test file against an absent implementation.
- Post-restart sweep **waived** per `PG-DP-02` (restart-gated): substitute = in-process vitest pre-restart + the post-restart live probes as authority. No browser-driven tests exist on this path — the derived set differed nowise.

## Acceptance-criteria question (`PG-SC-09`)

- Sections — does the page show engine truth in blueprint bucket order? Yes: buckets read from `row.bucket` (engine `bucket_for`), rendered Expired → This week → This month → Safe; labelled unresolved reasons map the engine's four `reason` values.
- Filter — does narrowing reach the server? Yes: the test asserts `category=<slug>` appears in the real request URL, not merely a client-side filter.
- Refresh — did the served bundle actually change while data stood still? Yes: image id + bundle id/size/sha changed, route-path marker 0→1, all 25 counts delta 0.

## Receipt note (M20-corrected block)

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Work pushed to `automation`; worktree clean.
Commands executed (verbatim), on `WORK_HEAD=__WORK_HEAD__`:

```
__RECEIPT_BLOCK__
```

First line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Existing-note refusal would have been a STOP; the precheck showed no existing note. Final line **note=yes**.

## Three UNCLEAR lines

- **FIRST READ:** whether the `"Expiry"` bundle-literal premise (hypothesis 0) would hold — it did not (measured 5); reported as a correction and replaced with the route-path literal as the marker.
- **DURING EXECUTION:** whether relocating buildx client state (`BUILDX_CONFIG=/tmp/opencode/buildx`) to complete the authorized build counted as routing around a denied privilege — decided no (no privilege was refused; the build is authorized; only a client cache path on a read-only FS was moved), disclosed for audit.
- **REMAINING:** whether the `Uncategorized` line belongs in a separate section after `Unresolved` or beside the engine summary counts — chose a distinct `Uncategorized` section so it is never merged into the engine stream.

note=yes
