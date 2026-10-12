SG-172 — Close-out deploy rider: serve SG-171 gating (rebuild + one recreate + verify)

**Dispatch:** SG-172 · **Coder:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `high`
(from process arguments — `/proc/$PPID/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high`; wrapper `bash /usr/local/lib/dispatch/run-coder SG-172`).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `automation` → **resolved commit:** `3ae5541b7b36b240b62e2860bea7a51272229641`
(== local HEAD at start == `origin/automation`; worktree clean at start). **WORK_HEAD:** `b200b05570164066903ec62e02828e26998e91eb`
(deploy-evidence commit carrying the before/build/recreate/after/verify logs).
**Authoring date (metadata):** 2026-10-12. Live UTC clock reads below.
**Type:** DEPLOY RIDER. Production restart + production writes authorized **solely** by the standing
close-out directive (`AGENTS.md` Close-out row; "Always do a live deploy before session close", owner
2026-09-28, `G-O4`) at this session close (`D-1012-14` approval: "first work next session; close-out
deploy of SG-171 rides this close"). **Zero product hunks expected — and zero produced.**

**Contract echo (verbatim):** `0.46.0` — source path `/home/andrei/storagegenie-contract/VERSION`.
Contract HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730` == `refs/tags/contract-v0.46.0^{}` (verified
live by `git -C /home/andrei/storagegenie-contract ls-remote --tags origin 'refs/tags/contract-v0.46.0*'`;
annotated tag object `4c23869c09683a749468a34ab193606d365cb111`); `RULES.md` sha256
`487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` == `RULES.sha256` == the installed
`487841B1…` payload recorded in `AGENTS.md` for 0.46.0. **Recorded == published == host.**
`bash /home/andrei/storagegenie-contract/rules_check.sh` exits **3**, re-measured:

    G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract
    G-L5 UNCHECKED gh-unauthenticated
    G-L7 UNCHECKED gh-unauthenticated
    G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275
    G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933

**Money posture (REAL $):** **$0.000000 USD actual**, **zero metered calls** — no USD-metered
provider/model path exists anywhere in this slice (image rebuild + container recreate + local reads).
Spend constraint ($0) honored.

---

## What this slice did

Served the SG-171 review-gating fix. SG-171 landed `frontend/src/components/CandidateCard.tsx` (always-visible
blocked-Accept reason + Inbox `Link`; evidence-thumb fallback) on disk that the running service (image
`5f4f4ccb…`, the SG-170 generation) did not serve. This slice is **rebuild + exactly one recreate + verify
only**. No product, test or config byte was edited: the diff ceiling is the `docs/worklogs/SG-172*` files.

How the code became live (`PG-PR-04`): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`
(one rebuild) + `docker compose up -d --no-deps backend` (exactly one recreate) + verify. All docker
commands ran with `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-172/docker.sock` (the lane's per-unit
runtime socket; the default `/var/run/docker.sock` is root-only — `F-SG172-5`).

---

## G1 — rebuild (one) + exactly one recreate

**BEFORE (read-only, capture 2026-10-12T20:03:08Z, `SG-172_before.log`):**

| field | value |
|---|---|
| container | `420c4051c21564f309b3cd8922b405bcddf638bd63394b21f7f7e8497fe1cf09` |
| image | `sha256:5f4f4ccbff4707cffbcc11fcbdf02745909207e2a9bceed8b001f42045fadab2` (expectation `5f4f4ccb` — **confirmed**) |
| RestartCount / Created | `0` / `2026-10-12T19:10:05.677332479Z` (StartedAt `2026-10-12T19:10:06.797351762Z`, SG-170 generation) |
| health | 6× 200 `{"status":"ok","db":"ok","storage":"ok"}` |
| gate | http:80 **301** / https:443 **401** |
| alembic | `20260924_sg114_relation (head)` |
| bundle | `index-DtD-fVNX.js` `3ff965fc69dd13d244f3240b95482cbc1a0adbd4900b73920516a3e0becdad91` (321685 B) + `index-DO0gjGV6.css` `37b25dbdd4b0ecfdedb8255bc7f8af286726334e95a1a3a9e85b9ba381b3d57c` (3911 B) |
| index.html | `e36ddb9489430d9a2b2e911513f0cc624c14f0829995aa78cfc928fd2d9513ca` (references `/assets/index-DtD-fVNX.js`) |
| counts | 28 tables read (delta source); `provider_call` 29, `audit_event` 91, `asset` 7, `candidate` 10, `review_task` 8 |
| CORS preflight | `If-Match` PATCH → **200**; `TRACE` → **400**; `X-Evil-Header` → **400**; `allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS` (no HEAD) |
| shipped-copy markers (occurrences, read live from the prior container) | `open review task(s) are resolved` **1** · `View them in the Inbox` **0** · `Thumbnail unavailable` **1** |

**BUILD (exactly one):** `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` → `BUILD_EXIT=0`,
**15 s** (`20:03:33Z → 20:03:48Z`, `SG-172_build.log`). Image **`sha256:5f4f4ccb…` →
`sha256:9064d2ced325220a4e7a2a16670cf678651e142c032c840e6e1e2d059c0cd4bf`** (new). The `BUILDX_CONFIG`
relocation is the documented EROFS-sandbox workaround (SG-154/SG-165/SG-168/SG-170 precedent). The
frontend stage re-ran `tsc && vite build`: `dist/assets/index-CYyuxefG.js 322.14 kB` (was `index-DtD-fVNX.js`);
CSS `index-DO0gjGV6.css` 3.91 kB unchanged (same name/hash — expected, `F-SG165-2`/`F-SG170-1`).

**RECREATE (exactly one):** `docker compose up -d --no-deps backend` → `REC_EXIT=0`, **2 s**
(`20:03:56Z → 20:03:58Z`, `SG-172_recreate.log`), one `Recreate / Recreated / Starting / Started`.

| field | BEFORE | AFTER |
|---|---|---|
| container id | `420c4051c215…` | **`91a073730e495dae222f179710879199237398040926adbbf8c57602fe97ef3f`** |
| image | `sha256:5f4f4ccb…` | **`sha256:9064d2ce…`** |
| RestartCount | 0 | 0 |

The recreate is proven by the **container-id change**, never by `RestartCount` (a recreate replaces the
container; the counter reads 0→0). Exactly one recreate was issued (a second is a STOP) — none was.

---

## G2 — verify live (state change by post-state)

AFTER capture `2026-10-12T20:04:15Z` (all quoted in `SG-172_after.log` / `SG-172_verify.log`):

- **Health ×6 exact** through `{{HEALTH_CMD}}` (`curl -s http://127.0.0.1:8003/v1/health`): all six
  bodies `{"status":"ok","db":"ok","storage":"ok"}` at HTTP 200 — **delta 0 vs BEFORE**.
- **Gate:** http:80 **301** / https:443 **401** — both unmoved.
- **Alembic:** `20260924_sg114_relation (head)` == BEFORE (unmoved; no migration run).
- **Counts — delta 0 on every table:** **28/28 BEFORE == AFTER**, none moved (`provider_call` 29 == 29;
  `audit_event` 91 == 91; `job_step` 72 == 72; `asset` 7, `candidate` 10, `review_task` 8, `job` 11).
- **Served bundle MOVED (rebuild proof):** `index-DtD-fVNX.js` `3ff965fc…` (321685 B) →
  **`index-CYyuxefG.js` `1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d` (322255 B)**;
  `index.html` moved `e36ddb94…` → **`2f035becd05b63e226af82e2e8fe60c8f3b5effb9f37e49dd95a2265c4da0d55`**
  (references the new `/assets/index-CYyuxefG.js`). The CSS bundle is **byte-identical**
  `index-DO0gjGV6.css` `37b25dbd…` (3911 B) — expected per `F-SG165-2`: the SG-171 change re-uses
  existing Tailwind classes/copy, so no new CSS bytes; **the JS move carries the proof.**
- **Served markers in the fresh JS** (occurrence counts of the served bundle; each quoted ×1):
  `open review task(s) are resolved` **1 → 2** · `View them in the Inbox` **0 → 1** ·
  `Thumbnail unavailable` **1 → 2**. All three moved upward; see `F-SG172-2` for why the raw presence of
  two of them was **already 1** before the rebuild and does not, by itself, discriminate.
- **CORS live proof, ZERO writes** (OPTIONS preflight only; no PATCH/POST/PUT/DELETE sent):
  `OPTIONS /v1/assets` with `If-Match` → **200** (`access-control-allow-headers …If-Match…`);
  `Access-Control-Request-Method: TRACE` → **400**; `X-Evil-Header` → **400**;
  `allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS` (no HEAD). Identical to BEFORE.
- **Pages through the fresh server:** `/review/01a0afaa-3ff4-7da0-987a-87f29c73ee5b` (a live candidate id,
  enumerated on target — the route is `/review/:candidateId`, `App.tsx:86`), `/inbox`, `/catalog` → **200**
  each.
- **Full end-to-end sweep WAIVED** per `PG-DP-02` (restart-gated: externally-driven tests would exercise
  the previous build). Substitute coverage is the health/counts/preflight/bundle-marker proof above plus
  SG-171's already-green targeted suites; **no browser-driven hits were run.**

---

## Findings (premise corrections; reported, not bent)

- **F-SG172-1 — the packet's "served markers … for the shipped copy" are only partially new (premise
  delta; loud per `PB-3`).** The packet quotes `open review task(s) are resolved`, `View them in the
  Inbox`, `Thumbnail unavailable` as markers of the shipped copy. Read live from the **pre-slice** served
  bundle (`index-DtD-fVNX.js`, image `5f4f4ccb`), two of the three were **already present with one
  occurrence each**: `open review task(s) are resolved` = **1** and `Thumbnail unavailable` = **1** (only
  `View them in the Inbox` = **0**). Their source is pre-existing: `CandidateCard.tsx:65` (the dedup
  alert's sentence, byte-identical before SG-171) and `EvidenceGallery.tsx:51` (the gallery's own
  fallback). SG-171 added a **second** occurrence of each (the new always-visible block, the new per-thumb
  `onError` fallback) plus the genuinely new Inbox link. Consequence: **a naive presence grep for two of
  the three markers would read `1` on both sides and pass vacuously.** The discriminating evidence is
  (a) the **JS asset name/hash move** (`index-DtD-fVNX.js` `3ff965fc…` → `index-CYyuxefG.js` `1b4680a0…`)
  plus the moved `index.html` reference, and (b) the **occurrence-count deltas** (1→2, 0→1, 1→2). Unlike
  SG-170 (whose old image was already pruned before any before-grep), this rider could read the old bundle
  live because the previous container was still running at BEFORE capture — so the delta is real and
  measured, not inferred. Stated so no criterion reads as passing vacuously.
- **F-SG172-2 — the CSS bundle is byte-identical again; only the JS moved (confirms F-SG165-2 /
  F-SG168-1 / F-SG170-1).** BEFORE and AFTER both ship `index-DO0gjGV6.css` sha256 `37b25dbd…` (3911 B).
  The SG-171 change re-used existing Tailwind classes/copy; all changed bytes landed in the JS chunk. The
  packet anticipated exactly this ("a byte-identical CSS bundle is expected … the JS move carries the
  proof"); direction stated explicitly.
- **F-SG172-3 — `.rules-cache/` is absent from the workspace.** AGENTS.md's Loading line instructs
  `bash .rules-cache/rules_check.sh`; the directory does not exist in the repo (`F-SG145-1`,
  `F-SG167-3`, `F-SG170-5`, `F-SG171-1`, re-measured). Ran the check from the host contract path
  `/home/andrei/storagegenie-contract/rules_check.sh` (exit **3**). `G-L1 UNCHECKED` is the local
  tag-ref shape — the checkout is *at* the tag's peeled commit `925cb575…` but carries no local tag
  object; the tag lives on the Launcher contract remote, not the StorageGenie repo (`F-SG168-4`/
  `F-SG170-5`), **not** payload drift.
- **F-SG172-4 — the `ls -la` header line `total 328` is not a table count (method note, not a defect).**
  A naive `^name count$` scan of the bundle listing also matches `total 328`; excluding it, the live
  datastore carries exactly **28** application tables, 28 == 28 both sides.
- **F-SG172-5 — the default docker socket (`/var/run/docker.sock`) is root-only on this host**
  (mode `s---------`) and `sudo` is unavailable (`no new privileges` flag). The lane provides a per-unit
  runtime socket at `/run/dispatch-storagegenie-SG-172/docker.sock`; all docker commands ran with
  `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-172/docker.sock` exported. Same lane mechanism
  SG-168/SG-170 used (`F-SG170-4`). Not a privilege denial routed around — the socket is the lane's grant.

**No vacuous pass:** the rebuild is evidenced by a changed image ID (one build), the recreate by a changed
container ID, health by six quoted bodies on both sides, counts by a full 28-table read on both sides,
the served surfaces by **occurrence-count deltas** of all three markers **backed by** the asset-name/hash
move, and CORS by live OPTIONS preflights with zero writes. No gate skipped, no mutating live request
sent. The one honest caveat is F-SG172-1 (raw marker presence alone is not discriminating for two of the
three; the asset move + occurrence deltas are).

---

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| **A1** rebuilt + one recreate + live | image ID new (one build)? container ID new (one recreate)? health ×6 delta 0, counts delta 0, preflight green? | YES — `5f4f4ccb…`→`9064d2ce…`, `420c4051…`→`91a07373…`, health ×6 = 200 delta 0, 28/28 counts delta 0, preflight 200/400/400 green |
| **A2** no migration | `alembic current` == head both sides? `models/`+`alembic/` diff empty? | YES — `20260924_sg114_relation (head)` both sides; `git diff 3ae5541b -- backend/app/models backend/alembic` **EMPTY** (0 lines) |
| **A3** product diff empty | is the diff exactly worklogs? | YES — only `docs/worklogs/SG-172*` added; `git diff 3ae5541b -- . ':(exclude)docs/worklogs'` EMPTY (0 lines) |
| **A4** report + receipt remote | report + notes-ref note (Dispatch-ID + Work-HEAD) read back on remote? writes = rebuild + one recreate only? | YES — see Receipt; production writes = one rebuild + one recreate; image IDs quoted; publish-before-bound honored (elapsed ≈ 180 s ≪ 1050 s) |
| **A5** guards invoked | PG-DP-01, PG-DP-02, PG-IC-01, PG-IC-07, PG-PR-04, PG-PR-10 | YES — see Guards below |

---

## Guards (A5)

- **`PG-DP-01`** — the fixed code is *running*, not re-read: the served-bundle markers for the SG-171 copy
  are read from the serving container, and the served JS asset name/hash moved.
- **`PG-DP-02`** — full end-to-end sweep **waived** (restart-gated); substitute coverage = health ×6 /
  28-table counts / CORS preflight / bundle proof + SG-171's green targeted suites; no browser hits.
- **`PG-IC-01`** — cross-product run; no blanket bans. The only in-slice collision (CSS byte-identical vs
  "bundle moved") was resolved by stating the JS move as the proof (F-SG172-2).
- **`PG-IC-07`** — live UTC clock (`date -u`); no fixed time gate; base named as resolved commit
  `3ae5541b…`, stated as the `automation` tip at start (== `origin/automation`).
- **`PG-PR-04`** — rebuild + one recreate + verify through the documented lane commands
  (`BUILDX_CONFIG=… docker compose build backend`; `docker compose up -d --no-deps backend`).
- **`PG-PR-10`** — no migration; `alembic current` == head both sides; `models/`+`alembic/` diff empty;
  exactly one recreate (a second would be a STOP); live DB read-only (28 counts both sides, delta 0).

---

## Budget — actual vs bound, per leg (units stated)

| leg | bound | actual |
|---|---|---|
| recon + orientation | 120 s | ~90 s |
| BEFORE capture | 120 s | ~20 s |
| rebuild (build class) | 600 s | **15 s** |
| recreate | 120 s | **2 s** |
| AFTER verify | 120 s | ~15 s |
| report + receipt | remainder | see below |
| **overall** | **2400 s** (lane `RUN_BUDGET_S=2100`) | within; lane start `20:01:42Z`, publish before `1050 s` half-bound |

No command hit its bound; nothing was killed; no command needed a retry. **Spend: REAL $0.000000 USD +
zero metered calls.**

---

## Receipt

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The receipt is the note on
`refs/notes/storagegenie-coder-reports`; the refspec is fetched into a **mapped** local name
(`refs/notes/sg172-fetched`) and each `show` is pasted verbatim below (a default fetch never carries
notes). **WORK_HEAD = `b200b05570164066903ec62e02828e26998e91eb`** (deploy-evidence commit).

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m "Dispatch-ID: SG-172 | Report: docs/worklogs/SG-172_report.md | Work-HEAD: b200b05570164066903ec62e02828e26998e91eb" b200b05570164066903ec62e02828e26998e91eb
add_wh_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
notes_push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg172-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg172-fetched show b200b05570164066903ec62e02828e26998e91eb
Dispatch-ID: SG-172 | Report: docs/worklogs/SG-172_report.md | Work-HEAD: b200b05570164066903ec62e02828e26998e91eb
show_wh_exit=0
```

Report-commit note (added after this file is committed — `CO-79`: the report cannot contain the moment
its own receipt is published), same mapped-refspec read-back:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m "Dispatch-ID: SG-172 | Report: docs/worklogs/SG-172_report.md | Work-HEAD: b200b05570164066903ec62e02828e26998e91eb" <report-commit>
add_rc_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
notes_push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg172-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg172-fetched show <report-commit>
Dispatch-ID: SG-172 | Report: docs/worklogs/SG-172_report.md | Work-HEAD: b200b05570164066903ec62e02828e26998e91eb
show_rc_exit=0
```

**note=yes** (required note present on WORK_HEAD and on the report commit, both read back through the
mapped refspec). **Report commit = the commit carrying this report** (its hash is recorded in the receipt
note on `refs/notes/storagegenie-coder-reports`); the very tip's final note is published by the runner
after this file is committed.

---

## UNCLEAR

- **FIRST READ:** whether the three packet "markers … for the shipped copy" were all new to the served
  bundle. Measured: only `View them in the Inbox` was new (0→1); the other two were already present once
  each (pre-existing dedup-alert line + `EvidenceGallery` fallback) and SG-171 added a second occurrence
  (F-SG172-1). Also: the default docker socket is root-only; the lane's per-unit runtime socket is the
  grant (F-SG172-5).
- **DURING EXECUTION:** whether raw marker *presence* could stand as the "is the fixed code running"
  proof. Resolved: no — two of three read `1` on both sides. The discriminating proof is the JS
  asset-name/hash move (`index-DtD-fVNX.js` → `index-CYyuxefG.js`) plus the occurrence-count deltas; the
  prior bundle was read live before the rebuild (the old container was still running), so the delta is
  measured, not inferred.
- **REMAINING:** the owner's visual verdict on the now-served review gating; the taxonomy-mapping slice
  (`D-1012-8`) and the end-to-end review-to-catalog story repair (`D-1012-14`) remain outside this
  rider's scope. SG-171's `REMAINING` items (double-sentence dedupe for blocked+dedup candidates; hover
  `title` redundancy) are likewise unaddressed here — this rider only makes the existing fix live.
