# SG-165 — close-out deploy rider: serve the Palette pile (rebuild + one recreate + verify)

**Dispatch:** SG-165 · **Coder:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `high`
(from process arguments — `/proc` cmdline: `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high`; wrapper `bash /usr/local/lib/dispatch/run-coder SG-165`).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `automation` → **resolved commit:** `4ea62aa68d333a1b9fa08128084539f9f4d7039a`
(== local HEAD at start, worktree clean). **WORK_HEAD:** `de02103848b544ac84e64a710809aedcfc8aa509`
(build+verify evidence commit).
**Authoring date (metadata):** 2026-10-12. Live clock reads below.
**Type:** DEPLOY RIDER. Production restart + production writes authorized **solely** by the standing close-out
directive (`AGENTS.md` Close-out row; "Always do a live deploy before session close", owner 2026-09-28, `G-O4`).
**Zero product hunks expected — and zero produced.**

**Contract echo (verbatim):** `0.46.0` — source path `/home/andrei/storagegenie-contract/VERSION`.
Contract HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730` == `refs/tags/contract-v0.46.0^{}` (ls-remote);
`RULES.md` sha256 `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` == the installed payload
hash recorded in `AGENTS.md` for 0.46.0. **Recorded == published.** `.rules-cache/` is absent on the host
(`F-SG145-1`); the live contract checkout is the source path. `G-L1 UNCHECKED` here is a local-tag-fetch shape,
not payload drift (`F-SG165-1`).

**Money posture (REAL $):** **$0.000000 USD actual**, **zero metered calls** — no USD-metered provider/model
path exists anywhere in this slice (image rebuild + container recreate + local reads). Per-leg budget below.

---

## What this slice did

Served the Palette pile: SG-161..164 landed 7 PRs' worth of frontend changes on disk (ExpiryEntryForm
double-submit guard; AssetImportModal busy state; EvidenceGallery a11y + first test; CandidateCard restyle +
tooltip; ChatPage form + theming) that the running service (image `c6fc45ab…`, the SG-154 generation) did not
serve. This slice is **rebuild + exactly one recreate + verify only**. No product, test or config byte was
edited: the diff ceiling is `docs/worklogs/SG-165*`.

How the code became live (`PG-PR-04`): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`
(one rebuild) + `docker compose up -d --no-deps backend` (exactly one recreate) + verify.

---

## G1 — rebuild (one) + exactly one recreate

**BEFORE (read-only, 2026-10-12T16:35:18Z):**

| field | value |
|---|---|
| container | `596e7d7a35d2c0ec6483cb2a418419394c0ba383ea84a73d427f823f7c1a5f40` |
| image | `sha256:c6fc45abbd1e7725ccf6ef33027ce63fa0bd6192e6f39ea3094b83ff4acdee4f` |
| RestartCount / Created | `0` / `2026-09-29T15:14:18.703231663Z` (SG-154 generation, unchanged since) |
| health | 6× 200 `{"status":"ok","db":"ok","storage":"ok"}` |
| gate | http:80 **301** / https:443 **401** |
| alembic | `20260924_sg114_relation (head)` |
| bundle | `index-CTQCofuO.js` `d9dbdef3…` (318152 B) + `index-DO0gjGV6.css` `37b25dbd…` (3911 B) |

**BUILD (exactly one):** `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` → `BUILD_EXIT=0`,
**26 s** (`16:35:26Z → 16:35:52Z`). Image **`sha256:c6fc45ab…` → `sha256:0bed0cc46f27f8d9d39fd3f0f41bce14cb4d9894a55d93356872d276284b2956`** (new).
The `BUILDX_CONFIG` relocation is the documented EROFS-sandbox workaround (SG-132/SG-142/SG-143/SG-154 precedent).
The frontend stage re-ran `tsc && vite build` (not cached — the pile's `frontend/` bytes are what changed).

**RECREATE (exactly one):** `docker compose up -d --no-deps backend` → `REC_EXIT=0`, **2 s**
(`16:36:03Z → 16:36:05Z`), one `Recreate/Recreated/Starting/Started`.

| field | BEFORE | AFTER |
|---|---|---|
| container id | `596e7d7a35d2…` | **`41ac9fd1ed963908d3c6e31628daa7c911bfe96e076f7ecd5c65411041d9b187`** |
| image | `sha256:c6fc45ab…` | **`sha256:0bed0cc4…`** |
| RestartCount | 0 | 0 |

The recreate is proven by the **container-id change**, never by `RestartCount` (a recreate replaces the
container; the counter resets 0→0). Exactly one recreate was issued (a second is a STOP) — none was.

---

## G2 — verify live (state change by post-state)

- **Health ×6 exact** through `{{HEALTH_CMD}}` (`curl -s http://127.0.0.1:8003/v1/health`) at
  `2026-10-12T16:36:29Z`: all six bodies `{"status":"ok","db":"ok","storage":"ok"}` at HTTP 200
  (quoted in the verify log) — **delta 0 vs BEFORE**.
- **Gate:** http:80 **301** (`https://storagegenie.dynv6.net/`) / https:443 **401** — both unmoved.
- **Alembic:** `20260924_sg114_relation (head)` == BEFORE (unmoved; no migration run).
- **Counts — delta 0 on every table:** 28/28 BEFORE == AFTER. None moved (`provider_call` 25 == 25).
- **Served bundle (changed, as required):** `index-C7iDBZmw.js` `a6c89a579770f2139944c215512f5cf76d9e13c5563f5f8801b195c30214f9da`
  (321242 B) — the new build. `index.html` moved `ec17cccc…` → `e394fd6b…` (references the new asset name).
- **Merged surfaces present in what is served** (grep of the served JS, each ×1; `aria-busy` ×4):
  `No evidence attached` (EvidenceGallery) · `Thumbnail unavailable` (EvidenceGallery error fallback) ·
  `Select a date to save` + `Save expiry` (ExpiryEntryForm) · `Acceptance is blocked until open review tasks
  are resolved` (CandidateCard blocked-Accept tooltip) · `aria-busy` (AssetImportModal busy state).
  This is the `PG-DP-01` "is the fixed code even running" proof — the fixed code is served, not re-read.
- **CORS live proof, ZERO writes** (OPTIONS preflight only; no PATCH/POST/PUT/DELETE sent): `OPTIONS /v1/assets`
  with `If-Match` → **200** (`allow-headers …If-Match…`); `Access-Control-Request-Method: TRACE` → **400**;
  `X-Evil-Header` → **400**; `allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS` (no HEAD). Identical to BEFORE.
- **Pages:** `/capture` `/inbox` `/catalog` → **200** each through the fresh server.
- **Full end-to-end sweep WAIVED** per `PG-DP-02` (restart-gated: externally-driven tests would exercise the
  previous build). Substitute coverage is the health/counts/preflight/bundle-marker proof above plus the
  already-green targeted suites; **no browser-driven hits were run.**

---

## Findings (premise corrections; reported, not bent)

- **F-SG165-1 — `G-L1 UNCHECKED` is local-tag-fetch shape, not contract drift.** `rules_check.sh` exits 3 with
  "the cache is not checked out at a contract tag". That is because the local contract repo has no tag beyond
  `contract-v0.33.0` fetched; `git describe` therefore cannot name the tag for HEAD. The content is pinned:
  HEAD `925cb57…` == `refs/tags/contract-v0.46.0^{}` (verified live by `git ls-remote --tags`), and the payload
  hash matches `AGENTS.md`. Recorded == published. (Same shape as SG-164's exit-3 line.)
- **F-SG165-2 — the CSS bundle is byte-identical; only the JS moved.** BEFORE and AFTER both ship
  `index-DO0gjGV6.css` sha256 `37b25dbd…` (3911 B). The pile's restyle/theming reused Tailwind utility classes
  already present in the pre-pile stylesheet, so `vite build` emitted no new CSS bytes; all changed behaviour
  landed in the JS chunk (`index-C7iDBZmw.js`, 318152 → 321242 B). Direction stated explicitly — the deploy is
  still proven by the changed JS + the served markers, not by a stylesheet move.
- **F-SG165-3 — inline post-recreate wait-poll emitted no captured lines (logging artifact, not a health fault).**
  The recreate block's `for`-poll produced no lines in the `{ … } | tee` pipeline. The construct was re-tested
  green in isolation and a clean 3-read recapture was appended to the verify log; the authoritative
  post-recreate health is the AFTER ×6 block, all 200. No impact on any criterion.

**No vacuous pass:** the rebuild is evidenced by a changed image ID (one build), the recreate by a changed
container ID, health by six quoted bodies on both sides, counts by a full 28-table read on both sides, the
served surfaces by a marker grep of the served JS, and CORS by live OPTIONS preflights with zero writes. No gate
skipped, no mutating live request sent.

---

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| **A1** rebuilt + one recreate + live | image ID new (one build)? container ID new (one recreate)? health ×6 delta 0, counts delta 0, preflight green? | YES — `c6fc45ab…`→`0bed0cc4…`, `596e7d7a…`→`41ac9fd1…`, health ×6 = 200 delta 0, 28/28 counts delta 0, preflight green |
| **A2** no migration | `alembic current` == head? `models/`+`alembic/` diff empty? | YES — `20260924_sg114_relation (head)` both sides; `git diff b16d0670..HEAD -- backend/app/models backend/alembic` **EMPTY** |
| **A3** product diff empty | is the diff exactly worklogs? | YES — `docs/worklogs/SG-165.{log,report.md,verify.log}` only |
| **A4** report + receipt remote | report + notes-ref note (Dispatch-ID + Work-HEAD) read back on remote? writes = rebuild + one recreate only? | YES — see Receipt; production writes = one rebuild + one recreate; image IDs quoted |

---

## Budget — actual vs bound, per leg (units stated)

| leg | bound | actual |
|---|---|---|
| recon + BEFORE capture | 120 s | ~110 s |
| rebuild (rebuild class) | 600 s | **26 s** |
| recreate | 300 s | **2 s** |
| AFTER verify | 120 s | ~30 s |
| report + receipt | remainder | see below |
| **overall** | **2400 s** (lane `RUN_BUDGET_S=2100`) | within |

No command hit its bound; nothing was killed; no command needed a retry. **Spend: REAL $0.000000 USD + zero
metered calls.**

---

## Receipt

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The receipt is the note on
`refs/notes/storagegenie-coder-reports`; the refspec is fetched into a **mapped** local name
(`refs/notes/sg165-fetched`) and each `show` is pasted verbatim below (a default fetch never carries notes).

**WORK_HEAD = `de02103848b544ac84e64a710809aedcfc8aa509`** (build+verify evidence commit).

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   4ea62aa..689c57c  automation -> automation
push_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-165 | Report: docs/worklogs/SG-165_report.md | Work-HEAD: de02103848b544ac84e64a710809aedcfc8aa509" de02103848b544ac84e64a710809aedcfc8aa509
add_wh_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-165 | Report: docs/worklogs/SG-165_report.md | Work-HEAD: de02103848b544ac84e64a710809aedcfc8aa509" 689c57cd88eedd2097f7d1f13f0aade7ebccffcf
add_rc_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   48385ec..36edc3f  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes_push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg165-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg165-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg165-fetched show de02103848b544ac84e64a710809aedcfc8aa509
Dispatch-ID: SG-165 | Report: docs/worklogs/SG-165_report.md | Work-HEAD: de02103848b544ac84e64a710809aedcfc8aa509
show_wh_exit=0

$ git notes --ref=refs/notes/sg165-fetched show 689c57cd88eedd2097f7d1f13f0aade7ebccffcf
Dispatch-ID: SG-165 | Report: docs/worklogs/SG-165_report.md | Work-HEAD: de02103848b544ac84e64a710809aedcfc8aa509
show_rc_exit=0
```

**note=yes** (both required notes present on WORK_HEAD and the report commit; read back through the mapped
refspec — a default fetch never carries notes). The report commit `689c57c` is the tip at report write; its own
final-tip note is published by the runner after this file is committed (`CO-79`: the report cannot contain the
moment its own receipt is published).

---

## UNCLEAR

- **FIRST READ:** whether the "Palette pile" bundle was expected to include a stylesheet change. Resolved by
  measuring: the served CSS is byte-identical because the pile re-used existing Tailwind classes; all changed
  behaviour is in the JS chunk. Disclosed as F-SG165-2.
- **DURING EXECUTION:** whether an empty inline health-poll was a post-recreate health failure. Resolved by
  re-testing the construct in isolation and re-capturing health (F-SG165-3); health is green ×6 after.
- **REMAINING:** the owner's visual verdict on the now-served UI (Inbox / Capture / Catalog) and the still-open
  desk items remain outside this rider's scope.
