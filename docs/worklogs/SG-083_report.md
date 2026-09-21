# SG-083 — deploy rider: v3 pipeline live on the public entry

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `164234585cce0b7c32996902bc4fbe20003b5470` (`D105+D106: rider approval + L3 recorded; SG-083 v3 deploy rider packet`)
**WORK_HEAD:** `e6f35a5b3eb534abde130ef4ac8d47139316bfe0` (work commit; the post-note receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published `0.28.2`; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`, read from provider metadata `/home/andrei/.local/share/opencode/log/opencode.log` line `llm.provider=opencode-go llm.model=deepseek-v4.1-flash`, **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/499275/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L3` (D106; 1 retry available; not used).

The D105-approved deploy rider for the D101 photo-ingest track. SG-079 (schema v3) + SG-080 (reader flipped
to v3 + transcript evidence + gated category) are committed (`20fbbde`, audited 98), but the running container
still served the SG-078-era image (`e9ad06fb9f7e`, built 13:07). This slice rebuilt the baked-UI backend image,
recreated the one service **exactly once** (the only authorized production mutation, D105), and proved the new
image is live with the standard before/after discriminators. **No extraction POST was made** — the v3 wiring is
proven structurally (`PG-SC-12`, in-image prompt files + live `load_prompt` version), not by spending.

## Premise verification (a difference would have been a finding)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| SG-079/080 backend-only, **no frontend diff since SG-078** | `git diff --stat 29fd8f9..HEAD -- frontend/` = **empty** | **confirmed** |
| Running container serves the SG-078-era bundle | served `index-fOM9Er4k.js`, **304117 B**, sha256 `91b53c1c7eb377353d7d9e8863d91f1e913fc6c517f327099b6f46dce49b6c1c` | **confirmed exactly** (matches SG-078 quoted AFTER) |
| Production DB at head `20260917_sg068_saved_search`; no migration since | in-container `alembic current` + `heads` → `20260917_sg068_saved_search (head)`; versions dir ends at `20260917_sg068_saved_search` | **confirmed** |
| v3 files + `PROMPT_FILES` v3 in the committed tree | 3 `*-v3.md` tracked; `reader.py` maps food/medicine/cosmetics → v3 | **confirmed** |
| Baked-UI shape: backend rebuild+recreate IS the deploy | `backend/Dockerfile` `COPY --from=frontend-build /ui/dist ./static`; `frontend` service under profile `dev` untouched | **confirmed** |
| One service, loopback `127.0.0.1:8003` | `docker ps` one running service; `ss -ltn` → `LISTEN 127.0.0.1:8003` only | **confirmed** |

## G1 — capture BEFORE (the production baseline)

- **Container / image / restarts:** container `f1e44f3b6bce991e6346333c6518596f9cee9185d2359d74c2519ee769c068a3`,
  image `sha256:e9ad06fb9f7ed17ee2a9c58d3b28a992c8d2f9ca92599f48d58d9b010c0c3856` (`storagegenie-backend:latest`,
  created `2026-09-21 13:07:26 UTC`), `RestartCount=0`.
- **Served frontend (loopback):** `GET /` → 944 B; assets `index-fOM9Er4k.js` **304117 B** sha256
  `91b53c1c…` and `index-CoNI-1Zn.css` **3839 B** sha256 `b18dbb33…`.
- **`alembic current` / `heads`:** both `20260917_sg068_saved_search (head)` — **no unapplied head** (STOP-guard not fired).
- **DB:** `/home/andrei/StorageGenie/data/db/storagegenie.db` `size=339968 mtime=2026-09-21 10:19:45.510824996 +0000`;
  `journal_mode=wal`, `-wal` 444992 B, `-shm` 32768 B. **24-table row counts** (raw in `SG-083_verify.log`):
  `alembic_version=1 assertion=6 asset=2 asset_evidence=2 asset_fts=2 asset_fts_config=1 asset_fts_data=4
  asset_fts_docsize=2 asset_fts_idx=2 audit_event=20 candidate=2 evidence=3 guardrail_event=1 household=1
  idempotency_key=5 job=3 job_step=24 observation=6 planning_suggestion=0 provider_call=8 review_task=1
  saved_search=0 source_attribution=0 user=2`.
- **Gate (unauthenticated):** `http://127.0.0.1/` Host `storagegenie.dynv6.net` → **301**; `https://127.0.0.1/` → **401**.
- **Regressions:** taxonomy 200/1118 B · saved-searches 200/12 B · facets 200/97 B · analytics-summary 200/5022 B.
- **Pre-existing owner activity disclosed (not a slice write):** `asset` row `…2b51fa518191` type `meat`, created
  `2026-09-21 14:02:14` — the owner used the live (pre-v3) public entry at 14:02, before this slice began; the
  `-wal` mtime `14:02:14` matches. The DB main file had not been checkpointed since 10:19:45. This is why the
  BEFORE row counts (asset=2, provider_call=8) are higher than SG-078's quoted record (asset=1, provider_call=7).

## G2 — rebuild + one recreate (the authorized restart)

- **`docker compose build backend`** — rc=0 in **11 s** (bound 600 s), with `BUILDX_CONFIG=/tmp/opencode/buildx`
  (`$HOME/.docker` exists but is **not writable** — F-SG067-2 / F-SG076-2 relocation precedent, reused and
  reported; nothing else probed). Image became `sha256:65eb3d6433b70bd09f85faf9d902064a0e9ca8c6afcc38d5980ad88c6b60c016`.
  The build log's `COPY --from=frontend-build /ui/dist ./static` step ran (raw tail in `SG-083_verify.log`);
  buildkit does not enumerate context files, so the **v3-enters-image proof is the in-image hash** below.
- **`docker compose up -d backend`** — rc=0 in **2 s** (bound 600 s); exactly **one** recreate
  (`Recreate / Recreated / Starting / Started`). Container `f1e44f3b6bce` → `f6539f65094e069d448921686099bb27e79a5bfbf487fd31eddae8ba527a017d`;
  image `e9ad06fb9f7e` → `65eb3d6433b7`.
- **No `alembic upgrade` was run** — `alembic heads` showed only the already-applied `20260917_sg068_saved_search`.

## G3 — verify AFTER (delta from the captured baseline)

### Discriminators

| | BEFORE (SG-078-era) | AFTER (rebuilt v3) |
|---|---|---|
| image | `e9ad06fb9f7e` | `65eb3d6433b7` (**DIFFERS**) |
| container | `f1e44f3b6bce` | `f6539f65094e` (**DIFFERS**) |
| RestartCount | `0` | `0` (**new container — see F-SG083-1**) |
| health | 200 `ok/ok/ok` | 200 `ok/ok/ok` ×6 consecutive |
| served JS | `index-fOM9Er4k.js` 304117 B `91b53c1c…` | **IDENTICAL** (expected) |
| served CSS | `index-CoNI-1Zn.css` 3839 B `b18dbb33…` | **IDENTICAL** |
| `index.html` | — | **`cmp` IDENTICAL** |
| `alembic current` | `20260917_sg068_saved_search (head)` | **IDENTICAL** |
| 24-table row counts | (above) | **IDENTICAL** |
| gate | 301 / 401 | **301 / 401** |
| loopback | `127.0.0.1:8003` | **preserved** |

The frontend bundle is **byte-identical** before and after, exactly as the packet predicted (backend-only change):
the deploy proof is the **image/container id change** plus the **in-image v3 files**, not a bundle change.
This is the `PG-SC-09` inverse stated upfront: a changed bundle here would have been the finding.

### New-image proof (`PG-SC-12` — decode what the consumer runs)

The fresh container `f6539f65094e` was created from `65eb3d6433b7` (quoted `docker ps` image column + `docker
images` ID above). Inside that running container:

```
$ docker exec storagegenie-backend-1 sha256sum /app/app/services/providers/prompts/extract-food-v3.md
3767253f9aae238a3f6b79cd2db4c65de95afa72a1c2ed2c8637161f650567b8  .../extract-food-v3.md
$ docker exec storagegenie-backend-1 python -c "... PROMPT_FILES ... load_prompt ..."
PROMPT_FILES= {'food': 'extract-food-v3.md', 'medicine': 'extract-medicine-v3.md', 'cosmetics': 'extract-cosmetics-v3.md'}
food extract-food-v3
medicine extract-medicine-v3
cosmetics extract-cosmetics-v3
```

The in-image `extract-food-v3.md` sha256 `3767253f…` is **byte-identical to the committed blob** (same for
medicine `d68dc7e9…`, cosmetics `e9a940d3…`), and the running process's `load_prompt` returns the v3
`template_version` for all three categories. **No extraction POST was made** (`$0`, structural proof).

### Regression checks

taxonomy / saved-searches / facets returned **byte-identical** bodies both sides (same sha256). analytics-summary
returned 5022 B both sides with a body diff whose **only** change is `generated_at`
(`14:48:15.669005+00:00` → `14:50:25.074326+00:00`) — the SG-078 F-SG078-1 precedent, a per-request timestamp.

### What must NOT change

- **`alembic current` identical** both sides; no `upgrade` run; the image ships no revision.
- **24-table row counts identical**; reads were `sqlite3 'file:…?mode=ro'` (read-only open, never a writer) and
  GET-only HTTP; `provider_call` 8→8 confirms no provider call was made.
- **DB main file grew 339968 → 372736 B, WAL 444992 → 0** (F-SG083-2): a **physical WAL checkpoint** on the old
  container's connection close at recreate, not a data write. Logical content is unchanged (row counts identical;
  the checkpoint only moves committed WAL pages into the main file). Same family as F-SG072-1, disclosed.
- **Nothing pushed to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`; no credential file fetched; no extra restart.**

## G4 — worklog and report

- `docs/worklogs/SG-083.log`, `SG-083_report.md`, `SG-083_verify.log` written (first token `SG-083`).
- Elapsed vs budget (units, per leg): recon+BEFORE **~90 s** / 120 s · build **11 s** / 600 s · recreate **2 s** /
  600 s · AFTER capture **~40 s** / 120 s · overall **~350 s** / 1800 s (`PG-PR-06`). No command hit its bound;
  nothing was killed.
- Model `deepseek-v4.1-flash` / effort `medium` (sources above). Spend: **real $0.000000** (zero metered calls).
  Contract echo + source path above.

### Receipt note verification (pasted `show` output)

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-083 | Report: docs/worklogs/SG-083_report.md | Work-HEAD: e6f35a5b3eb534abde130ef4ac8d47139316bfe0" e6f35a5b3eb534abde130ef4ac8d47139316bfe0
(add_rc=0)
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   3e20615..b18973d  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
(fetch_rc=0)
$ git rev-parse refs/notes/storagegenie-coder-reports
b18973deb178c77bea32489fa0c1ab146ced9b48
$ git ls-remote origin refs/notes/storagegenie-coder-reports
b18973deb178c77bea32489fa0c1ab146ced9b48	refs/notes/storagegenie-coder-reports
$ git notes --ref=refs/notes/storagegenie-coder-reports show e6f35a5b3eb534abde130ef4ac8d47139316bfe0
Dispatch-ID: SG-083 | Report: docs/worklogs/SG-083_report.md | Work-HEAD: e6f35a5b3eb534abde130ef4ac8d47139316bfe0
```

## Findings

- **F-SG083-1 (packet's `RestartCount +1` premise does not apply to a recreate).** The packet's G3 acceptance
  says "`RestartCount` +1", but the authorized operation is an `up -d` **recreate**, which replaces the container
  and resets `RestartCount` to 0. Measured: BEFORE container `f1e44f3b6bce` `RestartCount=0` → AFTER container
  `f6539f65094e` `RestartCount=0`. The genuine restart discriminator is the **container-id change** (plus the
  image-id change), which is present. Reported as measured, not bent; SG-078 hit the identical 0→0. If the
  Architect wants a numeric restart increment, the operation would have to be `docker restart` (in-place), not
  `up -d` — the packet's G2 explicitly says recreate.
- **F-SG083-2 (physical WAL checkpoint on recreate — logical content unchanged).** The DB main file changed size
  and mtime (339968→372736 B, 10:19:45→14:49:50) and the WAL drained (444992→0) because the old container's
  SQLite connections closed at recreate, checkpointing the WAL. All 24 logical row counts are identical and no
  write path was invoked. Precedent F-SG072-1; disclosed rather than hidden behind the "bytes unchanged" criterion.
- **F-SG083-3 (pre-existing owner import in the BEFORE baseline).** BEFORE row counts (asset=2, provider_call=8,
  assertion=6) are higher than SG-078's record (asset=1, provider_call=7) because the owner used the live
  pre-v3 public entry at `2026-09-21 14:02:14` (asset type `meat`), before this slice began. Not a slice write;
  the slice's own before/after are identical. Flagged so the count delta is not mistaken for slice movement.
- **F-SG083-4 (buildkit does not list COPY context files).** The packet asked the build log to "show the v3
  prompt files entering the image". BuildKit's log does not enumerate context files (only `COPY … ./static`).
  The stronger proof was used instead: the **in-image** sha256 of each v3 file equals its committed blob hash
  (`PG-SC-12`, decode what the consumer runs).

## Vacuity check (loud)

No acceptance criterion passed vacuously. The before-leg is the real prior artifact (`index-fOM9Er4k.js` 304117 B
`91b53c1c…` matches SG-078's quoted AFTER exactly, not re-typed). The image/container ids genuinely changed and
the fresh container's in-image v3 hashes match committed blobs byte-for-byte. Health was read six times on the
real service; the gate was read on both sides; regressions ran real GETs with the seed `household_id`; the
alembic and row-count reads came from the real mounted DB and the real container. The one criterion that could
look like a skipped check — the "DB bytes unchanged" — is **not** unchanged (F-SG083-2) and is explained, not
hidden. The "no extraction POST" claim is structural (provider_call 8→8), stated explicitly rather than assumed.

## UNCLEAR

- **FIRST READ:** the packet's G3 acceptance requires `RestartCount +1`, but G2 authorizes a `up -d` **recreate**,
  which cannot increment a replaced container's counter. I reported `0 → 0` with the container-id change as the
  real discriminator (F-SG083-1); if the Architect intended an in-place `docker restart`, that contradicts the
  packet's own "ONE `up -d` recreate" line and is the item to correct.
- **DURING EXECUTION:** the recreate triggered a physical WAL checkpoint (F-SG083-2), so the DB main file's
  size/mtime moved despite zero logical data change. This is the first rider in this arc where the before-state
  carried an un-checkpointed WAL (owner import at 14:02); SG-078's DB was already checkpointed and stayed
  byte-identical. Disclosed rather than claiming the stricter criterion.
- **REMAINING:** the v3 pipeline's *runtime behaviour* on a real photo (v3 prompt actually sent, transcribed
  fields returned, category gated) is proven structurally here, not by an extraction call — no metered POST was
  made ($0). The owner's next real capture on `https://storagegenie.dynv6.net` is the end-to-end authority.

Final line: `note=yes`
