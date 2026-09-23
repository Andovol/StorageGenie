# SG-104 — Arc A deploy rider: rebuild + migrate + one recreate + verify, one live press (report)

**Dispatch-ID:** SG-104
**Coder / effort:** `opencode` / `high` — effort read from the process arguments (`opencode run --auto --dir /home/andrei/StorageGenie --variant high …`); **model: `unknown`** (no model id is sent per policy, and no process argument or provider metadata exposed one — reported `unknown`, never guessed from a system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `59d4bf17daf12faaa3ff9cb04f9169beccc167d8` (== start HEAD)
**WORK_HEAD:** `WORK_HEAD_PLACEHOLDER` · **Report:** `docs/worklogs/SG-104_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:4` and `AGENTS.md:4`; **source path** `/home/andrei/storagegenie-contract/VERSION` → `0.33.0`, `FETCH_HEAD` `b232b845d74e89cb346c60fa4b9a40ec401c42dd` "branch 'contract' of github.com:Andovol/Launcher". `.rules-cache/` is **ABSENT** on this host (no in-repo cache); the contract checkout named by `/etc/dispatch/storagegenie.conf` (`CONTRACT_DIR=/home/andrei/storagegenie-contract`) is the source path. Recorded == published == `0.33.0`.
**DATABASE: the live SQLite** (`sqlite:////data/db/storagegenie.db`, compose bind `./data/db`) for (a–c) under **D142**; read-only otherwise. **Restart: ONE backend recreate (D142). Deploy: THIS slice.**
**Spend (real $):** **$0.000000** — build/recreate are $0; the ONE Jina fallback attempt failed at DNS resolution **before any request left the host** (`ConnectError: Name or service not known` for `eu.s.jina.ai`), so **no metered Jina byte was sent**. Under the `$0.05` per-press cap (`ENRICH_PER_PRESS_CAP_USD`, `enrich.py:46`); the request's own `X-Token-Budget: 6000` was the only configured bound.

---

## Result in one line

The backend image was **rebuilt** from the committed tree (`a76f1455…`, differing from the served `24224bc5…`), the **SG-100 migration applied** by a one-off container (`sg068 → sg100`, new table present with 0 rows), the backend **recreated exactly once**, and the new build **verified live**: one loopback Enrich press on a real Popescu-Household asset returned **HTTP 200** with a gated candidate and **`snapshots_recorded: true`**, writing **1 Job + 1 Candidate + 2 snapshot rows** (ids below, left in place). No code changed. Two packet premises proved wrong (bundle identity; `RestartCount +1`) — both **explained, not bent**, and both have direct SG-096 precedent.

---

## G0 — backup BEFORE any write: **MET (with a confinement finding)**

- Timestamped file-level copy at **`/home/andrei/.local/share/opencode/storagegenie-backups/SG-104-20260923T181120Z/`** — outside the live DB dir (`/home/andrei/StorageGenie/data/db`) and outside version control. Copied `storagegenie.db` **512000 B** + `-shm` **32768 B** + `-wal` **0 B**; copy sha256 `8342093029abf7456a7a59257c57a9a48cec20e1c1c444b2762e2b710dccbc30`.
- `sqlite3 <COPY> "PRAGMA integrity_check"` → **`ok`**; copy `alembic_version` = `20260917_sg068_saved_search`. Checked the **copy**, never the live file.
- **F-SG104-4 (confinement):** the natural backup location is denied. The dispatch unit is `ProtectSystem=strict` + `ProtectHome=read-only` with `ReadWritePaths=/home/andrei/StorageGenie /home/andrei/.codex /home/andrei/.grok /home/andrei/.local/share/opencode /home/andrei/storagegenie-contract /run/user/1000`; `~/storagegenie-backups` and `/var/backups` return `Read-only file system`. The backup was placed in a writable, non-VCS, non-live-DB path (`~/.local/share/opencode/…`). Not routed around, not privileged — reported.
- **Question (G0): can we roll back?** Yes: the pre-migration DB is a byte copy with an `ok` integrity check.

## G1 — capture BEFORE: **MET**

| Observable | BEFORE (raw) |
|---|---|
| image id | `sha256:24224bc5dcc098f59b4211981ebd7f67fcedfc2b0621024266c00c67b89bcbc8` (SG-096) |
| container / RestartCount | `324f1cc4fbac68d7db89b49dc3cd58a00eb054df6a19422707d457ea15a11239` · **0** · Started `2026-09-23T13:51:33Z` |
| served JS bundle | `index-D4-L2yOb.js` **305133 B** sha256 `f9a28f5ff507e5a48ecce324a43e134b927a7387d37ac7ce2b1e2106a5da542c` |
| served CSS | `index-CoNI-1Zn.css` **3839 B** sha256 `b18dbb336eef5c580bf0a2e6726d647c4f6c63edbc48373580d31e4508659ad3` |
| `alembic current` | `20260917_sg068_saved_search` (single head, verified) |
| tables / DB bytes | **24** tables · `storagegenie.db` **512000 B** (`-wal` 0, `-shm` 32768) |
| gate | HTTP :80 → **301** → `https://storagegenie.dynv6.net/` · HTTPS :443 → **401** (no login) |
| health exact | `{"status":"ok","db":"ok","storage":"ok"}` |
| Enrich-route shape probe (in-process, no press) | `enrich_routes= []`; `POST /v1/enrich/does-not-exist…` → **405** — the SG-096 image predates the endpoint |

- **Question (G1): what did production look like before?** Captured raw for every observable the proof moves; notably the served image has **no Enrich route at all**.

## G2 — rebuild + one-off migrate + ONE recreate: **MET**

- **Context grep (raw, `SG-104_verify.log`):** `synthesize.py`, `snapshots.py`, `enrich_snapshot.py`, `alembic/versions/20260923_sg100_enrich_snapshot.py`, `providers/prompts/enrich-synthesis-v1.md` all **PRESENT**; `opencode_go.py:42 TEXT_MAX_TOKENS = 8000` (SG-101); `enrich.py` SG-102/103 hunks (`record_off_snapshot`, `record_jina_snapshot`, `label_existing_fields`, `web_alternates`); `candidates.py:145-158` alternates round-trip.
- **Build:** `docker compose build backend`. First attempt **denied** — `failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/.tmp-default…: read-only file system`. Relocated `BUILDX_CONFIG=/tmp/sg104/buildx` (explicitly allowed, SG-067 precedent) → **exit 0, 16.32 s**. New image **`sha256:a76f145592656da45d5fa3bab7efffd1d89cf42565f1236d65f2d1898b4c12e6`** (differs). In-image `sha256sum` of the five Arc A files **equals the committed blobs** exactly (`synthesize f3af958d…`, `snapshots 7b455cf7…`, `enrich_snapshot 3549e1ed…`, migration `a1ff8aeb…`, prompt `cb6b6890…`).
- **Migrate (one-off NEW image, `run --rm`, NOT a recreate):** `alembic current` before = `20260917_sg068_saved_search`; history = single head `20260923_sg100_enrich_snapshot` (revises `sg068`, linear); `alembic upgrade head` → `20260917_sg068_saved_search -> 20260923_sg100_enrich_snapshot`; after = `20260923_sg100_enrich_snapshot (head)`; `enrich_snapshot` present with **0 rows**; table count **24 → 25**.
- **Recreate (exactly ONE):** `docker compose up -d --no-deps backend` → `Recreate / Recreated / Starting / Started`. New container **`40bcc32160be6f0c4cf43a09fd7992c9ae58eccd0f91a5dbb1f82de588aedce8`** from `a76f1455…`, loopback-only `127.0.0.1:8003->8000/tcp`, healthy.
- **Question (G2): was exactly the authorised sequence performed with the Arc bytes in the image?** Yes — build → migrate → recreate, in that order; Arc bytes proven in-image by sha256.

## G3 — verify AFTER + the ONE live press: **MET (bundle identity NOT MET — F-SG104-1)**

| Observable | BEFORE | AFTER |
|---|---|---|
| image id | `24224bc5…` | **`a76f1455…` — DIFFERS** |
| container | `324f1cc4…` | **`40bcc321…` — DIFFERS** |
| `RestartCount` | 0 | **0** (see F-SG104-2) |
| ports | loopback-only | **loopback-only preserved** |
| health | ok | **ok** |
| gate | 301 / 401 | **301 / 401** |
| served JS | `index-D4-L2yOb.js` 305133 B | **`index-Cj3z97gk.js` 305281 B — DIFFERS (F-SG104-1)** |
| served CSS | `index-CoNI-1Zn.css` 3839 B | **IDENTICAL** |
| `alembic current` | `sg068` | **`sg100`** |
| tables / DB bytes | 24 · 512000 B | 25 · 528384 B (`-wal` 90672) |
| counts | job 7, candidate 6, snapshot 0, provider_call 17 | **job 8, candidate 7, snapshot 2, provider_call 17** |

- **Count delta is EXACTLY the press rows** (`+1 job`, `+1 candidate`, `+2 enrich_snapshot`); every other count identical; `provider_call` unchanged ⇒ **no synthesis call rode the press**. DB bytes moved only by (a) backup [none], (b) migration [`+16384` B for the new table], (c) press [WAL growth].
- **In-image proof (`PG-SC-12`, real runtime loaders inside the fresh container):** `load_synthesis_prompt()` → `enrich-synthesis-v1`, prompt **2368 B**; `snapshots.SNAPSHOT_SCHEMA_VERSION = enrich-snapshot-v1`; `EnrichSnapshot.__tablename__ = enrich_snapshot`; `client`/`jina`/`synthesize` all import from `/app/app/services/enrich/`. `GET /v1/candidates/01a0cf79-a42a-7612-8f74-8e413dd8ee69?household_id=…` → **200**, shape `{id,state,job_id,fields,dedup_matches,review_task_ids,evidence_ids,asset_id,web_alternates}`.
- **THE press (18:14:10Z, loopback, one call):** `POST /v1/enrich/01a0a467-eb0e-7b83-a227-af122dc9268b?household_id=01a0a029-1477-7ca0-b200-bce78a96c679&last_spend_usd=0.0` → **HTTP 200**, `candidate_id 01a0cf79-a42a-7612-8f74-8e413dd8ee69`, `snapshots_recorded: true`, `off_accepted:false` (`below_threshold`), `fallback_fired:true`.
  - Rows **LEFT in place** (`PG-EV-06`): Job **`01a0cf79-a429-7220-b466-534d6dca94ab`** (enrich/COMPLETED); Candidate **`01a0cf79-a42a-7612-8f74-8e413dd8ee69`** (proposed); snapshots **off `01a0cf79-a425-77c3-8769-e20d2cca1b08`** (status 200) and **jina `01a0cf79-a427-7893-8c25-abdfee99b2bd`** (degraded, F-SG104-3). No second press.
- **Asset criterion (enumerated on target):** Popescu Household assets with non-empty `display_name` (the endpoint's `name` identifier; no `brand`/`identifier` assertions exist). All **6** qualify: Toothpaste, CEAFĂ DE PORC, UHT Lapte 3,5% grăsime, Milbona Parmigiano…, Miso Soup, Costiță de porc. **Picked:** `01a0a467…` "Toothpaste".
- **Waived sweep substitute:** 8 targeted enrich legs in-process **inside the fresh container** → **106 passed, 2 failed**; the 2 are container-environment artifacts (image ships no `docs/`; compose `env_file` injects `JINA_API_KEY`). Same 8 legs on the host tree → **108 passed**. **The post-restart in-container run is named the authority**, with the host run as corroboration (F-SG104-5).
- **Question (G3): is the new build live, migrated, and serving real Enrich proposals?** Yes — image/container changed, `sg100` live, health/gate intact, and a real press landed a gated candidate + snapshots.

---

## Findings (disclosed, not hidden)

- **F-SG104-1 — served bundle DIFFERS (explained; same family as F-SG096-1).** BEFORE `index-D4-L2yOb.js` 305133 B → AFTER `index-Cj3z97gk.js` 305281 B; CSS identical. Root cause: the running image was built at **SG-096** (`a4e25ee`), and **SG-098** (`c159d4d`) later changed `frontend/src/routes/AssetDetailPage.tsx` (`git diff a4e25ee HEAD -- frontend/` = `AssetDetailPage.tsx +9/-1`, `AssetDetailPage.test.tsx +12`) — the **Enrich button `onRun` wiring**, i.e. exactly the feature this deploy serves. The packet's premise ("SG-099→103 touched no frontend") is true but incomplete: the delta from the served image also includes SG-098. The rebuild correctly picks up committed source. **Bundle-identical acceptance criterion is therefore NOT MET**, and this is reported, not bent (SG-096 recorded the identical situation as F-SG096-1 and continued).
- **F-SG104-2 — `RestartCount +1` premise is wrong for a recreate.** A `compose up -d` recreate produces a **new container**, so the restart-policy counter **resets to 0** (BEFORE 0, AFTER 0); the moved observables are the **container id** (`324f1cc4…`→`40bcc321…`), the **image id**, and `StartedAt`. This is the same finding SG-096 recorded as F-SG096-3.
- **F-SG104-3 — the Jina fallback cannot reach its EU host in production.** `eu.s.jina.ai` is **NXDOMAIN** from both the host (`getent hosts` → empty) and the container (`socket.gethostbyname` → `[Errno -2] Name or service not known`), while `s.jina.ai` resolves (`104.26.11.242`) and OFF resolves. So `JINA_EU_BASE_URL = "https://eu.s.jina.ai/"` (`jina.py:42`) never connects, and every fallback records a loud degraded snapshot (`transport: ConnectError`). The snapshot writer correctly persisted the degradation (which is why the press still proves the wiring). **Outside this slice's scope (no code changes); reported for a later slice.**
- **F-SG104-4 — backup path confinement** (G0): see above.
- **F-SG104-5 — 2 container test failures are environmental.** `test_missing_key_degrades_loudly_with_zero_sends` (the container has `JINA_API_KEY` injected by compose `env_file`, so `settings.jina_api_key` is populated at import) and `test_worked_example_artifact_matches_the_real_driver` (the image excludes `docs/` via `.dockerignore`). Both pass on the host tree; neither is a code regression.

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

G0–G3 needed only DB-file/backup reads+writes, `docker` build/run/exec, gate/health/count probes, and the one press. No second press, no synthesis call (`provider_call` 17→17), no frontend change, no second migration, no second recreate. Identifiers were **TEXT only** (`display_name`); no photo bytes, GPS or key value left the box; the key is added at send time and never logged. No fixed dates in code; the live clock was read (`PG-IC-07`). No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| G0 backup quoted + integrity OK before any write | **MET** | copy sha256 `83420930…`, `integrity_check=ok` (on copy) |
| G1 before-captures quoted for every observable | **MET** | image/container/RestartCount/bundle/alembic/counts/bytes/gate/health/probe (G1 table) |
| One rebuild with Arc bytes in-image | **MET** | build exit 0 (16.32 s); in-image sha256 == committed blobs |
| One-off migrate `sg068→sg100`, table present 0 rows | **MET** | `run --rm` log; `enrich_snapshot` present, 0 rows; 24→25 tables |
| Exactly ONE recreate | **MET** | one `up -d --no-deps backend`; `Recreate/Recreated/Starting/Started` |
| image differs · health/gate/counts as stated | **MET** | `24224bc5…`→`a76f1455…`; ok; 301/401; +1/+1/+2 exactly |
| `RestartCount +1` | **NOT MET (premise wrong)** | 0→0; F-SG104-2 (SG-096 F-SG096-3 precedent) |
| bundle IDENTICAL to BEFORE | **NOT MET (explained)** | differs; F-SG104-1 (SG-096 F-SG096-1 precedent) |
| ONE press: 200 + gated candidate + `snapshots_recorded: True` + rows reported/left | **MET** | ids above; 2 snapshots; no second press |
| Jina actuals under cap | **MET** | **$0.000000** (DNS failure pre-send) < $0.05 cap |
| $ as stated; sweep waived with substitute named; no vacuous pass | **MET** | build/recreate $0; 8 enrich legs in-container (authority) + host; see vacuity note |

**Question each criterion answers (`PG-SC-09`):** **G0** — can we roll back? **Yes** (verified pre-migration copy). **G1** — what did production look like before? **Captured raw** (SG-096 image, no Enrich route, `sg068`, 24 tables). **G2** — was exactly the authorised sequence performed with the Arc bytes in the image? **Yes** (build→migrate→one recreate; in-image sha256). **G3** — is the new build live, migrated, and serving real Enrich proposals? **Yes** (new image live, `sg100`, one real press landed a gated candidate + 2 snapshots).

**Vacuous-pass check (`PG-EV-01`, loudly):** the press is a **real** HTTP call to the live service, not a test double — the OFF snapshot carries `count:46927` of live OFF data, and the rows are readable from the live SQLite after the fact. The count delta is **exactly** the press rows, so an empty or phantom press could not pass. **Where this slice is weaker than it looks:** (a) the Jina half of the fallback is **non-functional** (F-SG104-3) — the press proves the writer persists a *degraded* Jina snapshot, not a successful Jina fetch; (b) the full-suite sweep is waived (restart-gated) and replaced by 8 enrich legs only; (c) the `RestartCount` and bundle criteria are reported **NOT MET** with root causes, not papered over.

## Interim honesty (`PG-PR-05`)

The deploy itself is the point of this slice, so the new build **is** live and was exercised. The unresolved production gap is F-SG104-3 (Jina EU host unresolvable): the fallback path degrades loudly rather than failing silently, but it does not currently enrich. Reported for an owner-gated follow-up; no code was changed here.

## Report note on the notes ref (receipt)

RECEIPT_PLACEHOLDER

---

## UNCLEAR

- **FIRST READ:** two packet premises were hypotheses that failed on target and both have direct SG-096 precedent: the bundle is **not** byte-identical (F-SG104-1 — the served image predates SG-098's frontend button) and `RestartCount` does **not** go `+1` on a recreate (F-SG104-2 — a new container resets the counter). I continued (rather than `BLOCKED`) because the differences are fully explained by committed, intended source and the packet's own governing rule that "a difference is a finding, not an obstacle"; SG-096 recorded the identical two as F-SG096-1/F-SG096-3 and continued. The backup location was also forced off its natural path by the unit's `ProtectHome=read-only` confinement (F-SG104-4).
- **DURING EXECUTION:** the Jina fallback could not resolve `eu.s.jina.ai` (NXDOMAIN) while `s.jina.ai` resolves — a real production gap in the SG-082 client, discovered by the verification press (F-SG104-3). The waived-sweep substitute run inside the production image produced 2 environmental failures (no `docs/`, injected `JINA_API_KEY`), not code failures (F-SG104-5); the host run of the same legs was 108/108.
- **REMAINING:** F-SG104-3 (Jina EU base unresolvable) is the one live behaviour gap and needs its own owner-gated slice; the frontend button now served still does not render `web_alternates` (SG-103 backlog); `.rules-cache/` remains absent on this host (contract echoed from the checkout path).
