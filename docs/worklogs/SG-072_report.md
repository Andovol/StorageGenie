# SG-072 — deploy rider: analytics routes + screen live on the public entry

**Dispatch:** SG-072 · coder: opencode · effort: **medium** (read from process argv `/proc/4115690/cmdline` → `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Model:** `deepseek-v4.1-flash` — **provider metadata**, source `~/.local/share/opencode/log/opencode.log`, run=`b32e46b4`, line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`. No `--model` on argv (CLI default, omitted per policy); not read from any system-prompt identity line.
**Contract:** recorded `0.28.2` == published (`0.28.2`); source path `/home/andrei/storagegenie-contract/VERSION`; contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2` (`contract-v0.28.2`).
**Work dir:** `/home/andrei/StorageGenie` · **origin:** `git@github.com:Andovol/StorageGenie.git`
**BASE ref:** `origin/automation` · **resolved:** `408e8cd0fb86f53562d3985e9ddaaba118005bb0`
**WORK_HEAD:** `0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe` (docs-only work commit; note target).
**Spend:** real **$0.000000** (zero metered calls; the insights POST was never issued).

---

## Outcome (one line)

Rebuilt `storagegenie-backend:latest` from BASE and recreated the single backend container **once** (the authorized D93 production mutation); the served bundle changed `index-CZqbqy4J.js` → `index-BKFq1uFR.js`, and `GET /v1/analytics/summary?household_id=<seed>` went **404 → 200** with the full stats shape; `POST /v1/analytics/insights` was **never called** (proved structurally from the served bundle + the built tree); DB head and row counts unchanged; health green, loopback preserved, RestartCount 0→0.

---

## Legs — actual vs budget (units per leg)

| Leg | Actual | Bound | Margin |
|---|---|---|---|
| Reconf (git/docker/pre curls/sqlite) | ~37 s | 120 s | under |
| G1 `docker compose build` | **16.590 s** | 900 s | under |
| G1 `docker compose up -d` (one recreate) | **1.098 s** | 900 s | under |
| G1/G2/G2b after captures (health → row counts) | ~8 s | 120 s | under |
| **Overall (proc 10:18:46Z → final commit)** | **< 300 s** | 1800 s | under |

No command was killed; no interactive command was run.

---

## G1 — rebuild + bring up (authorized restart)

- **BUILDX_CONFIG relocation applied.** `~/.docker` is read-only under the coder confinement (`test -w` → not writable), so `BUILDX_CONFIG=/tmp/opencode/buildx` (accepted SG-067 `F-SG067-2` precedent, reused SG-069/070). No privilege probing.
- `docker compose build` rc=0, **16.590 s**. New frontend stage emitted `dist/assets/index-BKFq1uFR.js` (300.98 kB / gzip 89.20 kB). New image manifest list `sha256:56277bc0c5f75f3c72fabd3f759db4c63c4f3034a5936b7dc89a897dd755651c` (2026-09-21 10:19:38Z); previous image `1b2de06ad96a` (2026-09-21 09:12:07Z).
- `docker compose up -d` rc=0, **1.098 s**: `Recreate → Recreated → Starting → Started` — **exactly one recreate**; new container `9abefa97b534b2b2d1ba8cde4e84d866c6366e54ed7bcf8e106da5ce97e8f1a6`, image `sha256:56277bc0c5f7…`.
- Health: attempt 1 already `200 {"status":"ok","db":"ok","storage":"ok"}` (no settle window observed), then two consecutive 200 reads; final state `healthy`.
- **RestartCount 0 → 0** (no restart loop). `ss`: `LISTEN 127.0.0.1:8003` preserved (no `0.0.0.0` bind).

## G2 — the new behavior is LIVE (before-leg captured first — `PG-EV-08`/`PG-SC-12`)

| Check | BEFORE (image `1b2de06ad96a` / container `56ffb19533d3`) | AFTER (image `56277bc0c5f7` / container `9abefa97b534`) |
|---|---|---|
| Served bundle | `index-CZqbqy4J.js` · 296980 B · `5bf83861197eb73b1b54c94bc12e7215fa734a77329329a6d480a53051cf1598` | `index-BKFq1uFR.js` · **301077 B** · `36456c0194061600f9b483773e13493fd51a4e8886dd3f34fcebd50c2aafe2ae` |
| `GET /v1/analytics/summary?household_id=<seed>` | **404** `{"type":"about:blank","title":"Not Found","status":404,"detail":"Not Found: /v1/analytics/summary"}` | **200** (5022 B; stats body quoted in `SG-072_verify.log`) |
| `GET /v1/taxonomy` | 200 (1120 B) | 200 (1120 B) |
| `GET /v1/saved-searches?household_id=<seed>` | 200 `{"items":[]}` | 200 `{"items":[]}` |
| `GET /v1/assets/facets?household_id=<seed>` | 200 `{"asset_type":{"unknown":1},…}` | 200 (identical body) |
| gate `curl -sk -H "Host: storagegenie.dynv6.net" https://127.0.0.1/` | 401 | 401 |
| `ss` loopback | `127.0.0.1:8003` | `127.0.0.1:8003` |

Packet premise confirmed exactly: the pre bundle name, sha256 and byte size match the SG-070 measured record verbatim. Post is different in name **and** size **and** hash; the served `index.html` references `/assets/index-BKFq1uFR.js`.

**Analytics AFTER body (200, 5022 B, quoted shape):** totals `assets.total=1`, `assets.active=1`, `by_status={"ACTIVE":1}`; category counts for all six served taxonomy ids (each `0`) plus `uncategorized=1`; the five expiry buckets (`expired=0`, `within_7_days=0`, `within_30_days=0`, `safe=0`, `unknown=1`); adherence signals `suggestions{pending,confirmed,dismissed}` and `review_tasks{open,resolved}`; and a 21-row `stats[]` list where every row carries a non-empty `source` naming table + query (`PG-SC-02`). The full body is pasted in `SG-072_verify.log`.

**Insights POST — structural proof only (never called, `$0` held):**
- The served bundle contains the client call: `docker exec … grep -o "analytics/insights" /app/static/assets/index-BKFq1uFR.js | wc -l` → **1** (and `analytics/summary` → 1); the screen is genuinely wired, not a dead route (SG-070 `v1/taxonomy` precedent).
- The built tree contains both route decorators: `grep -rn` in the image's `/app/app/api/v1/analytics.py` → `@router.get("/analytics/summary")` (line 29) and `@router.post("/analytics/insights")` (line 38).
- **`POST /v1/analytics/insights` was never issued.** A metered call would have been a STOP-and-report; none was made.

`PG-SC-09` wrong-green world named: a stale image (old bundle) returning `{"status":"ok",…}` on health passes a health-only gate. The load-bearing discriminators here are the **bundle hash/name/size change**, the **404→200 analytics GET pair**, and the **two structural greps** (bundle `analytics/insights` count=1; built-tree route decorators). A health-only green cannot fake any of them.

`PG-EV-06` authority line: **NONE** — every request was a read-only GET; no writes, no credential file fetched, no provider call.

## G2b — what must NOT change

- **DB head unchanged.** In-container `alembic current` read the head *both* sides: PRE `20260917_sg068_saved_search (head)`, POST `20260917_sg068_saved_search (head)`; `alembic heads` same. The DB `alembic_version` table read `20260917_sg068_saved_search` directly via `mode=ro`. (F-SG069-1 substitution was **not** needed — the image resolves the head.) **No `alembic upgrade` was run.**
- **No rows created.** Read-only counts: `provider_call` **7 → 7**, `guardrail_event` **1 → 1**, `saved_search` 0→0, `asset` 1→1, `assertion` 3→3; full 24-table dump identical. 24 tables + the `asset_fts_content` **view** (SG-017 FTS migration, `DROP VIEW`), so no new table.
- **No migration ships:** `backend/alembic/versions/` top revision remains `20260917_sg068_saved_search.py`; SG-066 shipped no revision. Verified in-slice.
- **No-write construction (`PG-EV-06`):** every HTTP request this slice was GET (health, `/`, analytics summary, taxonomy, saved-searches, facets, gate); zero POST/PUT/PATCH/DELETE against any live route. DB access was a read-only SQLite open. The only mutating command was the authorized build + single recreate.
- Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. `frontend` service (profile `dev`) untouched (baked-UI shape, `F-SG069-2`).

## Findings / disagreements

- **F-SG072-1 (disclosed; not a data write).** The prod DB file mtime moved to the container-start instant (`2026-09-21 10:19:45.510824996 +0000`) and its size grew one 4 KiB page (335872 → 339968), while the WAL went `36.2K → 0B`. This is a **WAL checkpoint** folded into the main DB as the previous container's SQLite connection closed on the authorized `up -d` recreate — not a row write. Logical state is provably unchanged: `provider_call`/`guardrail_event`/`asset`/`assertion` counts and the `alembic_version` head are identical, and the 24-table set is unchanged. No write command was issued. Reported rather than hidden.
- **F-SG072-2 (premise confirmed, no correction needed).** Every quoted packet number matched measurement exactly: pre bundle name/size/sha256; `404` analytics GET; `alembic` head; seed household. No number had to be bent.
- **F-SG072-3 (cosmetic).** Vite reports the new bundle as `300.98 kB`, the on-disk file is `301077 B` — the same artifact, just kB vs bytes. Both quoted.
- No finding this slice contradicts SG-070's `F-SG070-1` (required `household_id`): each regression curl carries the seed param, so no bare-GET 422 was produced.

## Vacuous-pass check

The pass is **not vacuous**: the before/after bundles differ in name, size and hash; `404` before and `200` after are distinct served responses from the exact same URL; the new bundle contains `analytics/insights` (count 1); the built tree contains both route decorators; the DB counts and `alembic current` were read on both sides from the mounted DB. No gate was skipped; no test was stubbed; the insights POST is proven live **structurally** precisely because calling it is forbidden at $0.

## Receipt — notes ref (M20-corrected block; executed output pasted verbatim)

Work pushed to `automation` (`408e8cd..0be2063`), worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on WORK_HEAD `0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe`, notes ref pushed, then fetched into a **mapped** local name and verified with `show`:

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   408e8cd..0be2063  automation -> automation
push rc=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-072 | Report: docs/worklogs/SG-072_report.md | Work-HEAD: 0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe" 0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe
note add rc=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   862168b..3543ef1  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes push rc=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg072-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg072-verify
fetch rc=0

$ git rev-parse refs/notes/storagegenie-coder-reports-sg072-verify
3543ef1d387a5e34a74d9fb6bea87fe8a1178ce2

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg072-verify show 0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe
Dispatch-ID: SG-072 | Report: docs/worklogs/SG-072_report.md | Work-HEAD: 0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe
show rc=0

$ git notes --ref=refs/notes/storagegenie-coder-reports-sg072-verify show 0be2063d7f5a55524f8d287eb7b3b97f9d5f46fe | grep -c "Dispatch-ID: SG-072"
1
grep rc=0
```

First line carries both `Dispatch-ID:` and `Report:` (`CO-97`). Final line `note=yes`.

## UNCLEAR

- **FIRST READ:** whether the "before" analytics `404` could be confounded by route fall-through; it could not — the framework returned an explicit `Not Found: /v1/analytics/summary` body, so the route was genuinely absent in the old image.
- **DURING EXECUTION:** that the prod DB file mtime/size would move despite GET-only traffic — traced to the SQLite WAL checkpoint on the authorized container stop/start, not a write (F-SG072-1); row-count and head equality settle it.
- **REMAINING:** whether the live UI actually reaches the analytics screen over the public entry (auth gate `401` blocks an unauthenticated browser fetch; the screen's behavior is proven by SG-066's on-HTTP tests and this slice's served-bundle grep, not by an authenticated browser run in-slice).
