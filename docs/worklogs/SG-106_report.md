# SG-106 — presentation rider: rebuild + one recreate + verify, serves the SG-105 UI (report)

**Dispatch-ID:** SG-106
**Coder / effort:** `opencode` / `high` — effort read from the process arguments (`opencode run --auto --dir /home/andrei/StorageGenie --variant high …`); **model: `unknown`** (no model id is sent per policy, and no process argument or provider metadata exposed one — reported `unknown`, never guessed from a system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `59f731f83e47e63549c79d736c64995ae20e65e5` (== start HEAD)
**WORK_HEAD:** `<filled below>` · **Report:** `docs/worklogs/SG-106_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:3` and `AGENTS.md:4`; **source path** `/home/andrei/storagegenie-contract/VERSION` → `0.33.0`, `FETCH_HEAD` `b232b845d74e89cb346c60fa4b9a40ec401c42dd` "branch 'contract' of github.com:Andovol/Launcher". `.rules-cache/` is **ABSENT** on this host (no in-repo cache); the contract checkout named by `/etc/dispatch/storagegenie.conf` (`CONTRACT_DIR=/home/andrei/storagegenie-contract`) is the source path. Recorded == published == `0.33.0`.
**DATABASE: none live** (read-only counts/health probes only; no write of any kind). **Restart: ONE backend recreate (D146). Deploy: THIS slice.**
**Spend (real $):** **$0.000000** — build/recreate are $0; every probe was loopback-only; no external service, no synthesis call, no Jina request, no metered byte.

---

## Result in one line

The backend image was **rebuilt** from the committed tree (`dc6a4382…`, differing from the served `a76f1455…`) with the **SG-105 frontend bytes in-image** (served bundle `index-D4-L2yOb`→`index-DlD86cZ6`, `+1733 B`, new sha `6e0a3af7…`), the backend **recreated exactly once** (`f2ca0be9…`, loopback-only, healthy), and the **new UI verified live**: the served bundle carries the new `page-container`/`page-container--form`/`form-container` literals (0→1 each), health/gate/alembic/25 table counts are exactly as before, and a read-only catalog-list probe answers through the fresh container. No code changed. Two packet premises proved wrong (the marker set and "DB bytes unmoved") — both **explained, not bent**.

---

## G1 — capture BEFORE: **MET**

| Observable | BEFORE (raw) |
|---|---|
| image id | `sha256:a76f145592656da45d5fa3bab7efffd1d89cf42565f1236d65f2d1898b4c12e6` (SG-104 build) |
| container / RestartCount | `40bcc32160be6f0c4cf43a09fd7992c9ae58eccd0f91a5dbb1f82de588aedce8` · **0** · Started `2026-09-23T18:12:48Z` |
| served JS bundle | `index-Cj3z97gk.js` **305281 B** sha256 `d68479443243f59d272265f8b3f8ba4002ec4c027a18b8f3c7ad2f9c79b56fd0` (loopback == in-image) |
| served CSS | `index-CoNI-1Zn.css` **3839 B** sha256 `b18dbb336eef5c580bf0a2e6726d647c4f6c63edbc48373580d31e4508659ad3` |
| SG-105 markers in served JS | `page-container` **0** · `THEMED_CONTROL_CLASS` **0** · `Uncategorized (` **0** |
| `alembic current` | `20260923_sg100_enrich_snapshot` (single head, verified) |
| tables / DB bytes | **25** tables · `storagegenie.db` **528384 B** (`-wal` 90672, `-shm` 32768) |
| gate | HTTP :80 → **301** → `https://storagegenie.dynv6.net/` · HTTPS :443 → **401** (no login) |
| health exact | `{"status":"ok","db":"ok","storage":"ok"}` |

- **No-migration proof (raw, empty diff):** `git diff 59d4bf1..HEAD -- backend/app/models backend/alembic backend/app/db` → **0 lines**; `git show --stat 3b18e93 -- backend/app/models backend/alembic backend/app/db` → empty. The migration vehicle stays parked.
- **Question (G1): what did production serve before?** The SG-104 image (`a76f1455…`) with the pre-SG-105 bundle `index-Cj3z97gk.js`, all three SG-105 markers absent, `sg100` head, 25 tables.

## G2 — rebuild + ONE recreate: **MET (with a disclosed log-capture re-invocation — F-SG106-3)**

- **Context proof:** `PageContainer.tsx` + the seven SG-105-edited screens (`InboxPage`, `CapturePage`, `CatalogPage`, `AppShell`, `AssetForm`, `JobCard`, `ProductCard`) present in the tree at build (timestamps 19:16–19:18), `grep -c page-container PageContainer.tsx` = 3.
- **Build:** attempt 1 (default `BUILDX_CONFIG`) **denied** — `failed to update builder last activity time: open /home/andrei/.docker/buildx/activity/.tmp-default…: read-only file system` (exit 1). Relocated `BUILDX_CONFIG=/tmp/sg106/buildx` (explicitly allowed, SG-067 precedent) → **exit 0, 11 s**; the `frontend-build` stage ran `npm run build` (**DONE 7.1 s, not cached**) and `#21 COPY --from=frontend-build /ui/dist ./static`. New image **`sha256:dc6a4382c99d247ef51dc7f3742c52cf195d3d563adccb5fbc690a8c158086cb`** (config digest `40059cac…`).
- **Recreate (exactly ONE):** `docker compose up -d --no-deps backend` → `Recreate / Recreated / Starting / Started`, **exit 0, 1 s**; new container **`f2ca0be90eb0f982af332d3199b2cd7d0f333f248ca685a21f98425003f5a070`** from `dc6a4382…`, loopback-only `127.0.0.1:8003->8000/tcp`, healthy at **t=12 s**, `RestartCount=0`.
- **Question (G2): was exactly the authorised sequence performed with the UI bytes in the image?** Yes — one rebuild (SG-105 frontend source entered the build context and the bundle was regenerated), then exactly one recreate, then verify. No `run --rm`, no migration, no second recreate.

## G3 — verify AFTER (the UI is served): **MET (marker set NOT MET literally — F-SG106-1)**

| Observable | BEFORE | AFTER |
|---|---|---|
| image id | `a76f1455…` | **`dc6a4382…` — DIFFERS** |
| container | `40bcc321…` | **`f2ca0be9…` — DIFFERS** |
| ports | loopback-only | **loopback-only preserved** |
| health | ok | **ok** |
| gate | 301 / 401 | **301 / 401** |
| served JS | `index-Cj3z97gk.js` 305281 B | **`index-DlD86cZ6.js` 307014 B — DIFFERS**, sha `6e0a3af7…` (loopback == in-image) |
| served CSS | `index-CoNI-1Zn.css` 3839 B | **IDENTICAL** |
| `alembic current` | `20260923_sg100_enrich_snapshot` | **`20260923_sg100_enrich_snapshot`** (unchanged) |
| tables / counts | 25 · candidate 7, job 8, enrich_snapshot 2, provider_call 17, audit_event 68, … | **IDENTICAL, every table** |
| DB bytes | db 528384, wal 90672, shm 32768 | **db 552960, wal 0, shm 32768 — MOVED (F-SG106-2)** |

- **Served proof (`PG-SC-12` — decode what the consumer runs):** the served asset was fetched over loopback (`/assets/index-DlD86cZ6.js`), and its sha256 (`6e0a3af7…`) equals the in-image file's sha256. New SG-105-specific literals in the served JS: `page-container` **0→1**, `page-container--form` **0→1**, `form-container` **0→1**. (The two remaining packet-named markers cannot match post-build — F-SG106-1.)
- **Fresh server answers:** `GET /v1/health` → `{"status":"ok","db":"ok","storage":"ok"}` through the fresh container; read-only catalog-list probe `GET /v1/assets?household_id=01a0a029-1477-7ca0-b200-bce78a96c679&limit=2` → **200**, top keys `{items,next_cursor}`, 2 items, item shape `{id,household_id,display_name,asset_type,status,quantity,unit,condition,version,created_at,evidence_ids}`.
- **`PG-DP-01` — the delivery path (image) was changed BY the delivery path (rebuild):** the going-live behaviour deltas are **exactly the disclosed SG-105 set** — centered pages (one shared `.page-container`), themed controls (shared `THEMED_CONTROL_CLASS`), one brand row (duplicate AppHeader brand dropped), content-sized cards (ProductCard no longer 3:4), and `Uncategorized` pills (catalog pill vocabulary). **No surprise behaviour, stated in as many words.**
- **Full-suite sweep WAIVED (`PG-DP-02` — restart-gated):** externally-driven tests would exercise the previous build. **Substitute:** the build itself (SG-105 bytes regenerated into `/app/static`) plus the container-side probes above (served-asset identity + health + catalog-list shape). **The post-restart in-container run is named the authority.**
- **Question (G3): is the new UI actually served?** Yes — new image/container live, the served bundle differs and carries the new container literals, health/gate/alembic/counts intact, and a real read-only route answers through the fresh server.

---

## Findings (disclosed, not hidden)

- **F-SG106-1 — the packet's three markers are not all valid post-build greps (1 of 3 matches).** Only `page-container` survives (`0→1`). `THEMED_CONTROL_CLASS` is a **JS identifier erased by esbuild minification** — proven by the same bundle containing none of `toProductCategory`/`CatalogToolbar`/`ProductCard` (all 0). `Uncategorized (` is a **template-literal pattern** that esbuild compiles to `display+" ("+count+")"`; the contiguous string never appears (0 in both old and new; `unknown (` is likewise 0 in the old bundle, confirming the old template also never survived). A grep for either "could not have matched" by construction — reported loudly rather than written as a pass. **Substitutes that are genuinely SG-105-specific and literal:** `page-container--form` (0→1), `form-container` (0→1), plus the bundle-name/sha delta. `focus-ring` and `bg-background text-foreground border-border focus-ring` exist in the **old** bundle too (1 each) and are therefore **not** SG-105-specific.
- **F-SG106-2 — "DB bytes unmoved" is not achievable across a recreate; the bytes that moved are a WAL checkpoint, not a write.** BEFORE db 528384 + wal 90672 + shm 32768; AFTER db 552960 + wal 0 + shm 32768. The main-file mtime is exactly the recreate moment (`2026-09-23 19:37:30`), the `-wal` was truncated to 0 at `19:37:40`, and **every table count is byte-for-byte identical** (incl. `provider_call` 17→17, `audit_event` 68→68). The backend has **no startup/lifespan/create_all/seed path** (grep empty), and a `journal_mode=wal` DB is checkpointed when the old container's last connection closes at recreate. Total on-disk bytes actually *decreased* (619056 → 552960). This is the SQLite lifecycle, not an application write; the packet's "any movement is a finding" is honoured by reporting it. Same family as SG-104's F-SG104-2 (a recreate moves observables the packet assumed stable).
- **F-SG106-3 — build was invoked three times (one denied, one real, one cache-hit log capture).** Attempt 1 denied (read-only buildx activity path), attempt 2 the real rebuild (`npm run build` 7.1 s, image manifest `18906a7c…`), attempt 3 a `--progress=plain` re-invocation purely to capture the complete build log. Attempt 3 was an **all-CACHED hit** producing the **same image config digest** `40059cac…`; only the provenance-attestation timestamp changed the manifest-list id (`18906a7c…` → `dc6a4382…`). One logical rebuild; no source changed between invocations; no dangling images remain. Disclosed rather than hidden.
- **F-SG106-4 — "24-table counts" is a stale premise.** The live DB has **25** tables because SG-104 added `enrich_snapshot` (2 rows from its press). The acceptance criterion is "counts = BEFORE exactly", which is met; the number `24` in G1 is corrected to **25**.
- **F-SG106-5 — `.rules-cache/` remains absent on this host** (unchanged from SG-104/SG-105); the contract was echoed from the checkout path `/home/andrei/storagegenie-contract`. No in-repo cache exists to check.
- **F-SG106-6 (cosmetic) — my image-inspect probe used `.Config.Image`, which does not exist on `docker image inspect`** (template error). No impact: the container inspect already returned the image digest. Noted so the raw log's error line is not mistaken for a deploy problem.

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

G1–G3 needed only: image/container/bundle reads, `docker` build/up, and gate/health/catalog probes. **No** second recreate, **no** `run --rm`, **no** migration, **no** live press, **no** synthesis call, **no** config dump (`docker compose config` never invoked), **no** secrets printed. The only identifiers touched are household/asset ids and names already present in prior worklogs; no photo bytes, GPS or key value left the box. Time reads the live clock (`PG-IC-07`); no fixed dates in code. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.

## Guards invoked (0.33.0) — satisfaction

Guard texts live in the external contract (not in-repo), so each is stated against the packet's own description.

| Guard | How satisfied |
|---|---|
| `PG-EV-01` | Vacuous-pass section below; every "pass" has a non-empty artifact. |
| `PG-EV-02` | Raw before/after evidence quoted; `SG-106_verify.log`. |
| `PG-EV-05` | Every command bounded and quoted; nothing killed. |
| `PG-EV-08` | Production-change claim backed by the G1 before-capture. |
| `PG-SC-09` | Each criterion's question answered below. |
| `PG-SC-12` | Served asset fetched over loopback and hashed == in-image. |
| `PG-DP-01` | Delivery path changed by rebuild; disclosed SG-105 delta set, no surprise. |
| `PG-DP-02` | Full sweep waived (restart-gated); substitute named (build + container probes). |
| `PG-IC-01` | Cross-product enumerated above; nothing else touched. |
| `PG-IC-07` | All timestamps from the live clock (`date -u`). |
| `PG-IC-09` | No invented fact; unknowns written as `unknown`. |
| `PG-PR-01` | Enumerated with non-mutating forms only (reads/build/up/probes). |
| `PG-PR-03` | Scope ceiling honoured: writes only under `docs/worklogs` (3 files). |
| `PG-PR-04` | **THIS DEPLOY stated** in the header and result line. |
| `PG-PR-06` | Actual-vs-budget per leg below, with units. |

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| G1 before-captures quoted for every observable, markers absent before | **MET** | G1 table; all three markers 0 |
| One rebuild with SG-105 bytes in-image | **MET** | build exit 0; `npm run build` 7.1 s; bundle regenerated |
| Exactly ONE recreate | **MET** | one `up -d --no-deps backend`; `f2ca0be9…` |
| image differs · health/gate/counts as stated | **MET** | `a76f1455…`→`dc6a4382…`; ok; 301/401; all counts identical |
| DB bytes unmoved | **NOT MET (explained)** | db 528384→552960, wal 90672→0; WAL checkpoint, not a write — F-SG106-2 |
| `alembic current` still `sg100` | **MET** | `20260923_sg100_enrich_snapshot` before and after |
| Served bundle DIFFERS | **MET** | `index-Cj3z97gk`→`index-DlD86cZ6`, `+1733 B`, sha differs |
| All three SG-105 markers present | **NOT MET (1 of 3; explained)** | `page-container` 0→1; other two impossible to grep post-build — F-SG106-1 |
| Fresh server answers health + one read-only list probe | **MET** | health exact; `GET /v1/assets` 200, shape intact |
| $0 as stated; full sweep waived with substitute named; no vacuous pass | **MET** | $0.000000; substitute named; vacuity note below |

**Question each criterion answers (`PG-SC-09`):** **G1** — what did production serve before? The SG-104 image and the pre-SG-105 bundle, markers absent. **G2** — was exactly the authorised sequence performed with the UI bytes in the image? Yes: one rebuild (SG-105 source → regenerated bundle) then exactly one recreate. **G3** — is the new UI actually served? Yes: new image/container, served bundle differs and carries the new container literals, health/gate/counts intact, catalog route answers.

## Vacuous-pass check (`PG-EV-01`, loudly)

Every passing claim carries a non-empty artifact: the build log shows a **non-cached** `npm run build`; the served bundle is fetched over the wire and hashed; the three new literals are present **and were proven absent before** (0→1); the counts are compared table-by-table; the catalog probe returns real rows (`Costiță de porc`, `asset_type=meat`). **Where this slice is weaker than it looks:** (a) two of the three packet-named markers are **unmatchable post-build** (F-SG106-1), so the literal "all three present" criterion fails while the underlying goal is proven by the surviving new literals; (b) the full-suite sweep is waived (restart-gated) and replaced by build + container probes only; (c) DB bytes moved and the cause is inferred from mtime + identical counts + absence of startup writes, not from a write-audit hook (F-SG106-2). None of these is papered over.

## Actual-versus-budget per leg (`PG-PR-06`)

| Leg | Actual | Bound | Units |
|---|---|---|---|
| Recon + G1 before | ≈ 1 min | 120 s/command, 1800 s overall | wall |
| Build (attempt 2, real) | **11 s** (attempt 1 denied 1 s; attempt 3 cache-hit ~0 s) | **600 s** | wall |
| Recreate (cmd) | **1 s** | 600 s (recreate+verify) | wall |
| Health wait | **12 s** | 600 s | wall |
| G3 verify probes | ≈ 26 s | 600 s | wall |
| Overall (recon→G3) | **≈ 4 min** | **1800 s** | wall |

Commands producing no progress were never killed; no interactive command was run.

## Report note on the notes ref (receipt)

<filled after execution>

---

## UNCLEAR

- **FIRST READ:** two packet premises are hypotheses that failed on target, both in the same "observables a recreate moves" family as SG-104's F-SG104-2: the three named markers are **not** all valid post-build greps (F-SG106-1 — identifiers are minified, template literals are compiled), and "DB bytes unmoved" is unachievable across a recreate because SQLite checkpoints the WAL when the old container closes (F-SG106-2). I continued rather than `BLOCKED` because both differences are fully explained, the packet's own governing rule is "a difference is a finding, not an obstacle", and the underlying goal — the SG-105 UI is served — is proven.
- **DURING EXECUTION:** the build was invoked three times (denied / real / cache-hit log capture); I disclosed the third invocation rather than hide it, and proved the image content identical via the shared config digest `40059cac…` (F-SG106-3). The G1 "24-table" premise is stale — the live DB has 25 tables since SG-104 (F-SG106-4).
- **REMAINING:** `.rules-cache/` is still absent on this host (contract echoed from the checkout path). The packet's marker list should be corrected to post-build literals (`page-container`, `page-container--form`, `form-container`) in any future rider, and "DB bytes unmoved" should be restated as "row counts unmoved; WAL may checkpoint on recreate". No production gap introduced by this slice.
