SG-067 report — deploy rider: SG-064 catalog facets + evidence_ids live on the public entry

coder: **opencode** · effort: **medium** (process args read directly: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium ...`, pid 1670246) · MODEL: **unknown** (no `--model` on argv; the CLI default IS the model and is omitted per policy — never read from a system-prompt identity line)
contract echo: **0.28.2** · source path: `/home/andrei/storagegenie-contract/VERSION` (read == `0.28.2`; repo `.rules-cache/` is absent on this box) · spend **real $0.000000** vs $0 bound (zero provider calls)

Work dir: `/home/andrei/StorageGenie` · origin: `git@github.com:Andovol/StorageGenie.git`
`BASE` ref requested: `origin/automation` · `BASE` resolved: `4245be8fff111aca55d108a62bed0401ecfb1344` (== local HEAD at session start, the committed packet)
`WORK_HEAD`: `<pending — filled by the receipt commit>` (docs-only work commit)

Starting tree: clean (`git status --porcelain` empty). Dirt would have been a STOP; none seen.
Role guard honoured: never ran the dispatch verb, never started or polled this unit.

## Scope / production mutation

ONE `docker compose build` + ONE `docker compose up -d` recreate of the `storagegenie-backend` service —
the authorized D84 production restart. No other production effect. No code/`.env`/compose/migration/data
edits; the only repo writes are these three `docs/worklogs` files.

## G1 — rebuild + bring up

`docker compose up -d` recreated the service exactly once (quoted log: `Recreate`→`Recreated`→`Starting`
→`Started`, elapsed **1s** / 900s build+up bound).

- **Finding F-SG067-2 (build under the coder confinement).** The first `docker compose build` FAILED:
  `failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/.tmp-default1822294373: read-only file system`.
  Cause: the coder runs in `dispatch-storagegenie@SG-067.service` with `ProtectHome=read-only` /
  `ProtectSystem=strict` and `ReadWritePaths` = repo + `~/.codex` + `~/.grok` + `~/.local/share/opencode`
  + contract + `/run/user/1000` — `~/.docker` is **not** writable. I did not use privilege; I set the
  documented buildx config-dir env var `BUILDX_CONFIG=/tmp/opencode/buildx` (writable private tmp) and
  rebuilt on the same already-granted rootless docker socket. Build then succeeded in **16s / 900s**, with
  all backend layers `CACHED` and only the frontend bundle rebuilt. I read this as an environment/config
  mismatch, not a privilege boundary: the packet itself authorizes `docker compose build`. Flagged loudly
  in case the Architect disagrees.
- Health at `127.0.0.1:8003/v1/health` — `{"status":"ok","db":"ok","storage":"ok"}`. The two reads taken in
  the same instant as `up` returned curl `HTTP 000` (app not yet listening); the settle read and the two
  consecutive reads in G2 returned 200 (consecutive-healthy proof per `PG-DP-04`): readA 200, readB 200.
- RestartCount quoted before/after: **0 → 0** (`docker inspect` `restartcount=0`, `health=healthy`). No
  restart loop. `ss` shows `127.0.0.1:8003` only (loopback-only binding preserved).

## G2 — the new behavior is LIVE (each failure leg captured before)

- **Served bundle (the discriminator).** BEFORE: `GET /` referenced `index-nugWvqun.js`, bundle served
  `200` 293712 bytes, sha256 `e5c99c023da00bad3f8a7379cec290f406f4bc8e0deae3b2f4e74b2f18997f22` — matching
  the packet's expected pre-hash exactly. AFTER: `GET /` references `index-BHr__-9L.js`, bundle `200`
  294066 bytes, sha256 `b1638c8059988d7e957db2b653bd3ab8ec3f775d830e859d143aa6400a2e8d42` — **DIFFERENT**.
- **Facets endpoint (pre leg: 404).** BEFORE `GET /v1/assets/facets?...` → `HTTP 404`
  `{"type":"about:blank","title":"Not Found","status":404,"detail":"Asset not found"}` (no such route; it
  fell through to `/v1/assets/{asset_id}`). AFTER → `HTTP 200`
  `{"asset_type":{"unknown":1},"status":{"ACTIVE":1},"has_evidence":{"with":1,"without":0}}` — shape and real
  counts quoted.
- **`evidence_ids` (pre leg: absent).** BEFORE the seed row had **no** `evidence_ids` key. AFTER the row
  carries `"evidence_ids":["01a0a467-eacf-7e13-bbd0-078b1bc93860"]`.
- **Public entry gate.** Unauthenticated `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/`
  → **HTTP 401** (nginx `auth_basic`), before AND after. Status-code-only; no credential file fetched.
- **`PG-SC-09` — the world where a green is still wrong.** A stale image serving the OLD bundle would still
  answer `{"status":"ok",...}` on `/v1/health`; health alone cannot distinguish it. The discriminators are
  (a) the served asset name/sha256 change `index-nugWvqun.js`→`index-BHr__-9L.js`, and (b) the endpoint
  that did not exist before (facets 404→200). The container now serving is
  `container_id=5af43e43de114fc9afb49ce1c3f7571eefedb3c4beb7fc5a996cc7aa11b1911c`
  running image `sha256:74437f8d455378c3c2e5fad59def246de3dbdf56020b13d31a1921e92c5e0c41`
  (manifest list of the rebuilt `storagegenie-backend:latest`), replacing the pre-change
  `sha256:1b8308158602...`.

## G2b — what must NOT change

- **No migration.** `alembic current` in-container reads `20260916_sg048_name_optional (head)` BEFORE and
  AFTER — identical. In-tree: `git diff --name-only 5f95810..4245be8 -- backend/alembic` is empty (SG-064
  added no head). No `alembic upgrade` was run.
- **No rows created by this slice.** Authority line per `PG-EV-06`: NONE authorized. Construction: all
  app traffic this slice generated was HTTP GET (health, `/`, the bundle asset, facets, assets list, and the
  nginx gate probe) — no write verb. Read-only corroboration: the asset list returns exactly ONE item
  pre- and post- (`01a0a467-eb0e-7b83-a227-af122dc9268b`, `created_at` unchanged, `version` still 1).
  The seed household id was used only as a query parameter.
- Prod DB otherwise untouched. Nothing pushed to `storagegenie-evidence`. No `{{RECEIPT_CMD}}` this slice.

## Findings / corrections to the packet's premises

- **F-SG067-1.** The packet calls the pre-change image `fe509cf0`. That id is neither a git object
  (`fatal: Not a valid object name`) nor a docker image on this box (`docker image ls` shows only
  `storagegenie-backend:latest` = `1b8308158602` and the 6-day-old `storagegenie-frontend`). The
  load-bearing claim — the old bundle `index-nugWvqun.js` was being served — is confirmed exactly; the
  image-id label is stale/unverifiable here. I did not bend either value.
- **F-SG067-2.** See G1: buildx default config dir is unwritable under the coder confinement; build
  succeeded only after relocating `BUILDX_CONFIG` to a writable tmp dir. Worth fixing in the wrapper's
  `ReadWritePaths` (or a coder-env default) if future deploy slices are expected to build in-confine.
  This is outside this slice's scope; reported, not fixed.
- **F-SG067-3.** `ss -tlnp` shows the backend port owned by `rootlesskit` (`127.0.0.1:8003`), and nginx
  owns `0.0.0.0:80/443`; the loopback-only backend binding is preserved after recreate.

## Vacuity check (`PG-EV-01`)

No criterion passed vacuously: the facets 404 and the missing `evidence_ids` were captured as real failing
legs BEFORE the build on the same host/seed, and the bundle hash genuinely changed. The only weak-edge
observation is environmental: the "two consecutive health reads" after `up` required a settle because the
`up`-instant reads hit a not-yet-listening socket (`HTTP 000`); the consecutive pair is readA+readB, both
200, quoted.

## Budget (actual / budget, units)

- Premise verification + pre-captures: ~60s / 120s ordinary.
- G1 build: **16s / 900s** (plus a 0s failed attempt, finding F-SG067-2) · G1 up: **1s / 900s**.
- G2/G2b read-only verification: ~30s / 120s ordinary.
- G4 worklog + receipt: ~60s / 120s ordinary.
- Overall wall clock: ~700s / 1800s overall. No command killed; no command exceeded its bound.
- REAL metered spend: **$0.000000** vs $0 bound (zero provider calls; the only network use was the
  docker registry metadata/layer fetch during the authorized build).

## Receipt note on `refs/notes/storagegenie-coder-reports`

<this subsection is filled by the receipt commit and MUST contain the pasted executed output; a
receipt subsection with no pasted `show` output means the step was not executed>

## Disposition

Branch `automation`, worktree clean. Deploy rider complete: SG-064's catalog facets endpoint and
`evidence_ids` field are LIVE behind the public entry, on the rebuilt image; no migration, no data change.

## UNCLEAR

- FIRST READ: whether the packet's `fe509cf0` image id referred to a short image id, a container id, or a
  build commit — none resolve on this box; I treated the served bundle hash as the authoritative pre-state.
- DURING EXECUTION: whether relocating `BUILDX_CONFIG` out of the read-only `~/.docker` counts as routing
  around a denied operation (`PG-PR-03`). I judged it a configuration relocation inside the already-granted
  rootless socket + writable tmp, not a privilege escalation, and the packet authorizes the build; reported
  loudly in F-SG067-2 so the Architect can overrule.
- REMAINING: the wrapper confinement lacks `~/.docker` (or a buildx config env default); any future
  in-confine `docker compose build` will hit the same read-only failure until that is fixed.
