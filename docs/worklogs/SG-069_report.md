# SG-069 — deploy rider: saved-searches UI live on the public entry

**Dispatch:** SG-069 · coder: opencode · effort: medium (read from process argv `--variant medium`)
**Model:** unknown — no `--model` on argv (CLI default; omitted per policy), not read from any system-prompt identity line.
**Contract:** recorded `0.28.2` == published (`0.28.2`); source path `/home/andrei/storagegenie-contract/VERSION`; `RULES.md` sha256 `a66aa4313d62cebff8b44f10299928288e05dc4d7c45f4f4e83e0bbd954c131d` == payload `RULES.sha256`.
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**BASE ref:** `origin/automation` · **resolved:** `37aaf881d0b3d0f27ce060121f61a061c653cd28`
**WORK_HEAD:** see receipt follow-up (docs-only work commit hash).
**Spend:** real **$0.000000** (zero metered calls).

---

## Outcome (one line)

Rebuilt `storagegenie-backend:latest` from BASE and recreated the single backend container **once** (the authorized D87 production mutation); the served bundle changed `index-BHr__-9L.js` → `index-CVg0y-4w.js`, and `GET /v1/saved-searches` went **404 → 200 `{"items":[]}`**; DB head and row counts unchanged; health green, loopback preserved, RestartCount 0→0.

---

## Legs — actual vs budget (units per leg)

| Leg | Actual | Bound | Margin |
|---|---|---|---|
| Reconf (git/docker/pre curls/sqlite) | ~25 s | 120 s | under |
| G1 `docker compose build` | **17 s** | 900 s | under |
| G1 `docker compose up -d` (one recreate) | **1 s** | 900 s | under |
| G1/G2 health + discriminators + settle | ~30 s | 120 s | under |
| **Overall** | **~90 s** | 1800 s | under |

No command was killed; no interactive command was run.

---

## G1 — rebuild + bring up (authorized restart)

- **BUILDX_CONFIG relocation applied.** Default `~/.docker` is read-only under the coder confinement (`touch …/.wtest` → "Read-only file system"), so `BUILDX_CONFIG=/tmp/opencode/buildx-sg069` (accepted SG-067 `F-SG067-2` precedent). No privilege probing; rootless docker socket as granted.
- `docker compose build` rc=0, 17 s. New frontend stage emitted `dist/assets/index-CVg0y-4w.js` (296.66 kB). Image manifest list `sha256:cc880df58b9e253b51c68adac207b8eda9ec45ed176eb2fd6ef31b0e261f28e6`.
- `docker compose up -d` rc=0: `Recreate → Recreated → Starting → Started` — **exactly one recreate**, new container `17b12061d3d919ebdd65e49fcde274878161af09e7b412f08bee214eb3fc250f`.
- Health: attempt 1 = HTTP 000 during settle (disclosed, SG-067 precedent), then two consecutive `200 {"status":"ok","db":"ok","storage":"ok"}`; later settled reads also 200; compose reports `(healthy)`.
- **RestartCount 0 → 0** (no restart loop). `ss`: `LISTEN 127.0.0.1:8003` preserved.

## G2 — the new behavior is LIVE (before-leg captured first)

| Check | BEFORE | AFTER |
|---|---|---|
| Served bundle | `index-BHr__-9L.js` · 294066 B · `b1638c8059988d7e957db2b653bd3ab8ec3f775d830e859d143aa6400a2e8d42` | `index-CVg0y-4w.js` · 296747 B · `fcafabbfef694bdc8488156484ca1ac0e8dba16d51f1338cc1f0d02de07ab179` |
| `GET /v1/saved-searches?household_id=<seed>` | **404** `{"detail":"Not Found: /v1/saved-searches"}` | **200** `{"items":[]}` |
| `GET /v1/assets/facets?household_id=<seed>` | 200 | 200 |
| gate `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` | 401 | 401 |
| `ss` loopback | `127.0.0.1:8003` | `127.0.0.1:8003` |

Packet premise confirmed exactly: the pre bundle name, sha256 and byte size match the SG-067 measured record. Post hash is different on name **and** size **and** hash.

`PG-SC-09` wrong-green world named: a stale image whose health endpoint returns `{"status":"ok",…}` would pass a health-only gate. The load-bearing discriminators here are the **bundle hash change** and the **404→200 saved-searches pair** — a health-only green cannot fake either. New container id and image id quoted above.

## G2b — what must NOT change

- **DB head unchanged.** The packet expected in-container `alembic current` to read the head *before*; it **cannot** (see F-SG069-1). Authoritative read is the DB directly (read-only, `mode=ro`):
  - PRE: `alembic_version = ('20260917_sg068_saved_search',)` · `saved_search rows = 0` · `assets rows = 1`
  - POST: `alembic_version = ('20260917_sg068_saved_search',)` · `saved_search rows = 0` · `assets rows = 1`
  - After rebuild, `alembic current` → `20260917_sg068_saved_search (head)` (the new image carries the revision script).
- **No migration run** (`alembic upgrade` never invoked), **no rows created**. Construction: every request issued to the app was a GET (`/v1/health`, `/`, `/assets/<bundle>`, `/v1/saved-searches?`, `/v1/assets/facets?`, gate probe); no POST/PUT/PATCH/DELETE. `saved_search` rows 0 both sides; `asset` rows 1 both sides.
- Nothing pushed to `storagegenie-evidence`; no `finalize_dispatch_report.sh` / `{{RECEIPT_CMD}}`. No credential file fetched.

## Findings

- **F-SG069-1 (packet premise corrected).** `alembic current` inside the **old** container fails: `ERROR [alembic.util.messaging] Can't locate revision identified by '20260917_sg068_saved_search'` / `FAILED: Can't locate revision identified by '20260917_sg068_saved_search'`. The old image predates SG-068's revision file, so it cannot resolve the version the DB already stores — expected for a stale image and precisely what this deploy fixes. The DB's `alembic_version` table (read directly, read-only) is the authoritative before-read and equals the head; `alembic current` resolves the head after the rebuild. I did **not** treat this as a STOP because the invariant the gate protects (DB head unchanged, no upgrade) is proven both sides; proceeding is the packet's clear intent. Flagging loudly per the stale-image `PG-SC-09` note.
- **F-SG069-2 (surface clarification).** `docker compose ps` shows only `storagegenie-backend-1`; the `frontend` service is under profile `dev` (its container exited 6 days ago). The public bundle is baked into the backend image by `backend/Dockerfile`'s multi-stage `frontend-build` stage → `backend/static`, so the backend rebuild+recreate is the entire deploy. No frontend service action was taken.

## Acceptance criteria

- [x] Pre-bundle quoted (`index-BHr__-9L.js`, `b1638c80…`, 294066 B); build+up once; two consecutive healthy reads; RestartCount 0→0; loopback preserved.
- [x] Post-bundle hash different (`index-CVg0y-4w.js`, `fcafabbf…`, 296747 B); saved-searches 404-before → 200-after (`{"items":[]}`); facets still 200; gate 401 both sides.
- [x] DB head identical before/after (`20260917_sg068_saved_search`, direct read-only) — with F-SG069-1 disclosed; no rows created (GET-only construction stated); prod DB otherwise untouched; nothing pushed to `storagegenie-evidence`; no vacuous pass (bundle/name/size/hash and endpoint status pair are non-vacuous discriminators).

## Receipt — notes ref (M20-corrected block)

WORK_HEAD: `<filled by receipt follow-up>`. To be completed with pasted `git notes … show` output after `WORK_HEAD` exists. `note=yes` required; zero-exit with `note=no` is a FAIL.

## UNCLEAR

- **FIRST READ:** whether the packet's `alembic current`-must-read-head BEFORE was achievable at all with the pre-deploy image; it is not, because the image predates the revision file. Resolved as F-SG069-1 rather than a STOP.
- **DURING EXECUTION:** whether the disposable `frontend-build` stage cache miss (frontend source changed) vs the existing dev-profile frontend image implies any surface beyond the backend service. Resolved as F-SG069-2: no, the bundle is baked into the backend image.
- **REMAINING:** the served-bundle hash is still a build-output identity, not a content assertion of the saved-searches UI; the endpoint 404→200 pair carries the functional claim. No UI-rendering screenshot was taken (out of scope; no headless browser authorized).
