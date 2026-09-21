# SG-070 — deploy rider: taxonomy endpoint + inspector swap live on the public entry

**Dispatch:** SG-070 · coder: opencode · effort: medium (read from process argv `--variant medium`)
**Model:** unknown — no `--model` on argv (CLI default; omitted per policy); not read from any system-prompt identity line.
**Contract:** recorded `0.28.2` == published (`0.28.2`); source path `/home/andrei/storagegenie-contract/VERSION`; contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2` (`contract-v0.28.2`).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**BASE ref:** `origin/automation` · **resolved:** `cd51ba7e13943da930feb9d1060fb598a170899b`
**WORK_HEAD:** `0cd854fdf91390f9134556be4b4839cc57f40d92` (docs-only work commit).
**Spend:** real **$0.000000** (zero metered calls).

---

## Outcome (one line)

Rebuilt `storagegenie-backend:latest` from BASE and recreated the single backend container **once** (the authorized D88 production mutation); the served bundle changed `index-CVg0y-4w.js` → `index-CZqbqy4J.js`, and `GET /v1/taxonomy` went **404 → 200** with the registered `expiry-tracker` descriptor; DB head and row counts unchanged; health green, loopback preserved, RestartCount 0→0.

---

## Legs — actual vs budget (units per leg)

| Leg | Actual | Bound | Margin |
|---|---|---|---|
| Reconf (git/docker/pre curls/sqlite) | ~22 s | 120 s | under |
| G1 `docker compose build` | **16.340 s** | 900 s | under |
| G1 `docker compose up -d` (one recreate) | **1.332 s** | 900 s | under |
| G1/G2 health + discriminators + G2b | ~15 s | 120 s | under |
| **Overall (proc 09:11:28Z → work commit)** | **~9 min** | 1800 s | under |

No command was killed; no interactive command was run.

---

## G1 — rebuild + bring up (authorized restart)

- **BUILDX_CONFIG relocation applied.** `~/.docker` is read-only under the coder confinement, so `BUILDX_CONFIG=/tmp/opencode/buildx` (accepted SG-067 `F-SG067-2` precedent, reused SG-069). No privilege probing.
- `docker compose build` rc=0, **16.340 s**. New frontend stage emitted `dist/assets/index-CZqbqy4J.js` (296.89 kB). New image `1b2de06ad96a` (manifest list `sha256:1b2de06ad96a6c84014120a82fbe1ee5e62147d6b3c1aa61471642e44d9d5431`); previous image `cc880df58b9e` (2026-09-17 19:44:17Z).
- `docker compose up -d` rc=0, **1.332 s**: `Recreate → Recreated → Starting → Started` — **exactly one recreate**; new container `56ffb19533d30c84831e5cc13e19a87022ee6957186ef6b40efd1d5d31a73b97`.
- Health: attempt 1 already `200 {"status":"ok","db":"ok","storage":"ok"}` (no settle window observed), then two consecutive 200 reads; final health `healthy`.
- **RestartCount 0 → 0** (no restart loop). `ss`: `LISTEN 127.0.0.1:8003` preserved.

## G2 — the new behavior is LIVE (before-leg captured first)

| Check | BEFORE | AFTER |
|---|---|---|
| Served bundle | `index-CVg0y-4w.js` · 296747 B · `fcafabbfef694bdc8488156484ca1ac0e8dba16d51f1338cc1f0d02de07ab179` | `index-CZqbqy4J.js` · 296980 B · `5bf83861197eb73b1b54c94bc12e7215fa734a77329329a6d480a53051cf1598` |
| `GET /v1/taxonomy` | **404** `{"type":"about:blank","title":"Not Found","status":404,"detail":"Not Found: /v1/taxonomy"}` | **200** (descriptor body below) |
| `GET /v1/saved-searches?household_id=<seed>` | 200 `{"items":[]}` | 200 `{"items":[]}` |
| `GET /v1/assets/facets?household_id=<seed>` | 200 | 200 (identical body) |
| gate `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` | 401 | 401 |
| `ss` loopback | `127.0.0.1:8003` | `127.0.0.1:8003` |

Packet premise confirmed exactly: the pre bundle name, sha256 and byte size match the SG-069 measured record. Post is different in name **and** size **and** hash; the served `index.html` references `/assets/index-CZqbqy4J.js`.

**Taxonomy AFTER body (200, 1120 B, quoted):**

```json
{"plugins":[{"plugin_id":"expiry-tracker","version":"1.0.0","categories":[
 {"id":"food_beverages","name":"Food & beverages","active":true,"notification":"tiered-30-7-1","opened_date_tracking":false,"chat":"category"},
 {"id":"medicine_pharma","name":"Medicine/pharma","active":true,"notification":"tiered-short","opened_date_tracking":false,"chat":"category"},
 {"id":"cosmetics_personal_care","name":"Cosmetics/personal care","active":true,"notification":"tiered-90-30-7","opened_date_tracking":true,"chat":"none"},
 {"id":"household_chemicals","name":"Household chemicals","active":false,"notification":"basic-expiry","opened_date_tracking":false,"chat":"fallback"},
 {"id":"documents_other","name":"Documents/other","active":false,"notification":"long-lead-60-30","opened_date_tracking":false,"chat":"fallback"},
 {"id":"non_perishable","name":"Non-perishable","active":true,"notification":"none","opened_date_tracking":false,"chat":"none"}],
 "date_types":["expiry_date","best_before","use_by","manufacture_date","period_after_opening","batch_lot_code"],
 "units":["piece","unit","ml","l","g","kg","dose","tablet","application"]}]}
```

Every category carries both `opened_date_tracking` and `chat`; `cosmetics_personal_care` is the `opened_date_tracking:true` case. The new bundle also contains the string `v1/taxonomy` (grep count 1), i.e. the inspector actually calls the endpoint — not a dead route.

`PG-SC-09` wrong-green world named: a stale image whose health endpoint returns `{"status":"ok",…}` passes a health-only gate. The load-bearing discriminators here are the **bundle hash/name/size change** and the **404→200 taxonomy pair** (plus the in-bundle `v1/taxonomy` grep). A health-only green cannot fake any of them. New container id `56ffb19533d3`, new image id `1b2de06ad96a` quoted above.

`PG-EV-06` authority line: **NONE** — every request was a read-only GET; no writes, no credential file fetched, no provider call.

## G2b — what must NOT change

- **DB head unchanged.** In-container `alembic current` read the head *both* sides: PRE `20260917_sg068_saved_search (head)`, POST `20260917_sg068_saved_search (head)`; `alembic heads` same. (The F-SG069-1 substitution was not needed — this image resolves the head; the DB `alembic_version` table nonetheless read `20260917_sg068_saved_search` directly before and after via `mode=ro`.) **No `alembic upgrade` was run.**
- **No rows created.** Read-only row counts identical before and after (24 tables): `asset=1`, `assertion=3`, `evidence=2`, `audit_event=10`, `job=2`, `job_step=16`, `observation=4`, `provider_call=6`, `idempotency_key=4`, `candidate=1`, `saved_search=0`, `review_task=0`, `source_attribution=0`, `guardrail_event=0`, `planning_suggestion=0`, `household=1`, `user=2`, plus FTS shadow tables. DB file mtime unchanged (`2026-09-17 19:44:28`).
- **No-write construction (`PG-EV-06`):** every HTTP request issued this slice was GET (health, taxonomy, saved-searches, facets, `/` index.html, gate); zero POST/PUT/PATCH/DELETE. DB access was a read-only SQLite open (`file:…?mode=ro`). No credential file was fetched.
- Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.
- `frontend` service (profile `dev`) untouched (its container is not running; the public bundle is baked into the backend image per `F-SG069-2`).

## Findings / disagreements

- **F-SG070-1 (packet premise nuance).** The packet's G2 states saved-searches and facets are "still 200 after the rebuild". Bare `GET /v1/saved-searches` and `GET /v1/assets/facets` return **422** (`household_id` is a required query param). With the seed household `01a0a029-1477-7ca0-b200-bce78a96c679` they are 200, both before and after. The endpoint is live as claimed; the criterion is correct only with the required param. Not a defect, but a precision gap in the packet text.
- **F-SG070-2 (explained, not a defect).** The served taxonomy shows `household_chemicals` `active:false`. This matches the committed descriptor verbatim (`backend/app/plugins/descriptor.py:157`, the F-SG065-2 "inactive Phase-3 placeholder" pilot profile). The slice title's "Household chemicals pilot" refers to the profile being *present* in the descriptor, not enabled. No divergence between code and live body.
- **F-SG070-3 (evidence limitation, disclosed).** After the rebuild retagged `storagegenie-backend:latest`, the previous image `cc880df58b9e` is no longer present locally (`docker images -a` lists only the new backend and the frontend), so the `v1/taxonomy` grep could not be run against the old bundle. Before-evidence stands on the container file hash `fcafabbf…` (captured while the old container was live) plus the live 404. Not a gate failure; reported for honesty.
- **F-SG070-4 (environment note).** `AGENTS.md` references a repo `.rules-cache/` contract checkout; no `.rules-cache/` exists in this worktree. Contract authority was read from the host path `/home/andrei/storagegenie-contract/VERSION` as the packet instructs.

## Vacuous-pass check

The pass is **not vacuous**: the before/after bundles differ in name, size and hash; `404` before and `200` after are distinct served responses; the new bundle contains `v1/taxonomy`; the DB counts and `alembic current` were read on both sides from the mounted DB. No gate was skipped; no test was stubbed.

## Receipt — notes ref (M20-corrected block)

Work pushed to `automation` (`cd51ba7..0cd854f`), worktree clean. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-070 | Report: docs/worklogs/SG-070_report.md | Work-HEAD: 0cd854fdf91390f9134556be4b4839cc57f40d92" 0cd854fdf91390f9134556be4b4839cc57f40d92
notes add rc=0
$ git push origin refs/notes/storagegenie-coder-reports
   4df2932..a646c2f  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes push rc=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg070-verify
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg070-verify
fetch rc=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg070-verify
a646c2f3b5274c487c8efae767840baddfd52add
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg070-verify show 0cd854fdf91390f9134556be4b4839cc57f40d92
Dispatch-ID: SG-070 | Report: docs/worklogs/SG-070_report.md | Work-HEAD: 0cd854fdf91390f9134556be4b4839cc57f40d92
show rc=0
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg070-verify show 0cd854fdf91390f9134556be4b4839cc57f40d92 | grep -c SG-070
1
grep rc=0
note=yes
```

Instrument finding: `git notes --ref=… list` prints only `<note-blob-sha> <object-sha>` pairs, not bodies, so a `list | grep SG-070` cannot match the body; content grep requires `show` per object (or `git log --notes`). `show` was run against the fetched mapped ref and is pasted above.

## UNCLEAR

- **FIRST READ:** whether the packet's "before" taxonomy criterion (a 404) could be confounded by route fall-through to another handler; it could not — the framework returned an explicit `Not Found: /v1/taxonomy` body, so the route was genuinely absent in the old image.
- **DURING EXECUTION:** the packet's saved-searches/facets "still 200" line omits the required `household_id` param (bare GET is 422) — resolved by using the named seed household read-only (F-SG070-1).
- **REMAINING:** the previous image `cc880df58b9e` is no longer on disk, so no post-hoc grep of the old bundle is possible (F-SG070-3); any future before-leg of this shape should grep the old bundle while the old container is still live.
