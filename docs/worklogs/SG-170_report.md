# SG-170 — Close-out deploy rider: serve SG-169 empty-state (rebuild + one recreate + verify)

**Dispatch:** SG-170 · **Coder:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `high`
(from process arguments — `/proc/$PPID/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high`).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `automation` → **resolved commit:** `20350623d7f0f5095d9086ba0b18c6c0ba2e3b87`
(== local HEAD at start, worktree clean). **WORK_HEAD:** `b8017b772f58bd4ee0498654e8b109a4e48d331d`
(deploy-evidence commit carrying the before/build/recreate/after/verify logs).
**Authoring date (metadata):** 2026-10-12. Live clock reads below.
**Type:** DEPLOY RIDER. Production restart + production writes authorized **solely** by owner quote
"Approved." (`D-1012-11`) plus the standing close-out directive (`AGENTS.md` Close-out row;
"Always do a live deploy before session close", owner 2026-09-28, `G-O4`).
**Zero product hunks expected — and zero produced.**

**Contract echo (verbatim):** `0.46.0` — source path `/home/andrei/storagegenie-contract/VERSION`.
Contract HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730` == `refs/tags/contract-v0.46.0^{}` (verified
live by `git -C /home/andrei/storagegenie-contract ls-remote --tags origin`; tag object `4c23869…`);
`RULES.md` sha256 `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` == `RULES.sha256`
== the installed `487841B1…` payload recorded in `AGENTS.md` for 0.46.0. **Recorded == published.**
`.rules-cache/` is absent on the host (`F-SG145-1`/`F-SG167-3`); the live contract checkout is the
source path. `G-L1 UNCHECKED` here is a local-tag-fetch shape, not payload drift (`F-SG165-1`,
`F-SG168-4`, re-measured).

**Money posture (REAL $):** **$0.000000 USD actual**, **zero metered calls** — no USD-metered
provider/model path exists anywhere in this slice (image rebuild + container recreate + local reads).
Spend constraint ($0) honored.

---

## What this slice did

Served the SG-169 honest chat empty-state: SG-169 landed `backend/app/services/chat/service.py`
(`unclassified_count`) and `frontend/src/routes/ChatPage.tsx` (cause sentence + Inbox link) on disk that
the running service (image `85924507…`, the SG-168 generation) did not serve. This slice is
**rebuild + exactly one recreate + verify only**. No product, test or config byte was edited: the diff
ceiling is `docs/worklogs/SG-170*`.

How the code became live (`PG-PR-04`): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`
(one rebuild) + `docker compose up -d --no-deps backend` (exactly one recreate) + verify.

---

## G1 — rebuild (one) + exactly one recreate

**BEFORE (read-only, capture 2026-10-12T19:09:21Z):**

| field | value |
|---|---|
| container | `a31f940cdc23d3e9467f6938e175be49527ca4326dc786e908099ab366e0de35` |
| image | `sha256:85924507a2442f33427dc09464420c533712b3fcf5689bae5a9eaa634f4481e3` (expectation `85924507` — **confirmed**) |
| RestartCount / Created | `0` / `2026-10-12T18:35:11.766685356Z` (SG-168 generation, unchanged since) |
| health | 6× 200 `{"status":"ok","db":"ok","storage":"ok"}` |
| gate | http:80 **301** / https:443 **401** |
| alembic | `20260924_sg114_relation (head)` |
| bundle | `index-CaM3_fbA.js` `2fe32c97…` (321317 B) + `index-DO0gjGV6.css` `37b25dbd…` (3911 B) |
| index.html | `a18b9684…` (references `assets/index-CaM3_fbA.js`) |

**BUILD (exactly one):** `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` →
`BUILD_EXIT=0`, **27 s** (`19:09:30Z → 19:09:57Z`). Image **`sha256:85924507…` →
`sha256:5f4f4ccbff4707cffbcc11fcbdf02745909207e2a9bceed8b001f42045fadab2`** (new). The `BUILDX_CONFIG`
relocation is the documented EROFS-sandbox workaround (SG-154/SG-165/SG-168 precedent). The frontend
stage re-ran `tsc && vite build` (not cached — the SG-169 `frontend/` + `service.py` bytes are what
changed): `dist/assets/index-DtD-fVNX.js 321.57 kB` (was `index-CaM3_fbA.js`); CSS `index-DO0gjGV6.css`
3.91 kB unchanged (same name — expected, `F-SG165-2`).

**RECREATE (exactly one):** `docker compose up -d --no-deps backend` → `REC_EXIT=0`, **2 s**
(`19:10:05Z → 19:10:07Z`), exactly one `Recreate / Recreated / Starting / Started`.

| field | BEFORE | AFTER |
|---|---|---|
| container id | `a31f940cdc23…` | **`420c4051c21564f309b3cd8922b405bcddf638bd63394b21f7f7e8497fe1cf09`** |
| image | `sha256:85924507…` | **`sha256:5f4f4ccbff4707cffbcc11fcbdf02745909207e2a9bceed8b001f42045fadab2`** |
| RestartCount | 0 | 0 |

The recreate is proven by the **container-id change**, never by `RestartCount` (a recreate replaces the
container; the counter reads 0→0). Exactly one recreate was issued (a second is a STOP) — none was.

---

## G2 — verify live (state change by post-state)

AFTER capture `2026-10-12T19:10:14Z` (all quoted in `SG-170_after.log` / `SG-170_verify.log`):

- **Health ×6 exact** through `{{HEALTH_CMD}}` (`curl -s http://127.0.0.1:8003/v1/health`): all six
  bodies `{"status":"ok","db":"ok","storage":"ok"}` at HTTP 200 — **delta 0 vs BEFORE**.
- **Gate:** http:80 **301** / https:443 **401** — both unmoved.
- **Alembic:** `20260924_sg114_relation (head)` == BEFORE (unmoved; no migration run).
- **Counts — delta 0 on every table:** 28/28 BEFORE == AFTER. None moved (`provider_call` 27 == 27;
  `audit_event` 78 == 78; `asset 6`, `candidate 9`, `review_task 7`, `job 10`, `job_step 64`, `user 2`).
- **Served bundle MOVED (rebuild proof):** `index-CaM3_fbA.js` `2fe32c97…` (321317 B) →
  **`index-DtD-fVNX.js` `3ff965fc69dd13d244f3240b95482cbc1a0adbd4900b73920516a3e0becdad91` (321685 B)**;
  `index.html` moved `a18b9684…` → **`e36ddb9489430d9a2b2e911513f0cc624c14f0829995aa78cfc928fd2d9513ca`**
  (references the new `assets/index-DtD-fVNX.js`). The CSS bundle is **byte-identical**
  `index-DO0gjGV6.css` `37b25dbd…` (3911 B) — expected per `F-SG165-2`: the SG-169 change re-uses
  existing Tailwind tokens/copy, so no new CSS bytes; **the JS move carries the proof.**
- **Served markers in the fresh JS** (`grep -oc -F` of the served bundle; each quoted ×1):
  `awaiting classification` ×1 · `Review them in the Inbox` ×1. These markers show the shipped copy is
  present in what is served (the `PG-DP-01` "is the fixed code even running" read).
- **CORS live proof, ZERO writes** (OPTIONS preflight only; no PATCH/POST/PUT/DELETE sent):
  `OPTIONS /v1/assets` with `If-Match` → **200** (`access-control-allow-headers …If-Match…`);
  `Access-Control-Request-Method: TRACE` → **400**; `X-Evil-Header` → **400**;
  `allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS` (no HEAD). Identical to BEFORE.
- **Pages through the fresh server:** `/chat` `/inbox` `/catalog` → **200** each.
- **Full end-to-end sweep WAIVED** per `PG-DP-02` (restart-gated: externally-driven tests would exercise
  the previous build). Substitute coverage is the health/counts/preflight/bundle-marker proof above plus
  SG-169's already-green targeted suites; **no browser-driven hits were run.**

---

## Findings (premise corrections; reported, not bent)

- **F-SG170-1 — the CSS bundle is byte-identical again; only the JS moved (confirms F-SG165-2 /
  F-SG168-1).** BEFORE and AFTER both ship `index-DO0gjGV6.css` sha256 `37b25dbd…` (3911 B). The SG-169
  change added a cause sentence + Inbox link reusing existing Tailwind classes; all changed bytes landed
  in the JS chunk (`index-CaM3_fbA.js` → `index-DtD-fVNX.js`). Direction stated explicitly — the deploy
  is proven by the changed JS name/hash + the served markers, not by a stylesheet move.
- **F-SG170-2 — `provider_call` reads 27 both sides (delta 0).** That is the same value the SG-168 AFTER
  read (`27`) and the SG-168 BEFORE read; SG-169 wrote nothing to the live DB (it is a code-only slice).
  No migration and no write of any kind was issued by this rider.
- **F-SG170-3 (vacuity disclosure, loud per `PB-3`/AC caveat) — the marker grep is a presence read, not
  by itself a change-discriminator.** The two markers are new to the served copy: at **source level** the
  commit that produced the pre-slice bundle (`4db8da3`, base of image `85924507…`) has **0** occurrences
  of `awaiting classification` / `Review them in the Inbox` (and 0 `unclassified_count`), while the
  current source has 2 / 1 — so the served markers were not present in the prior build. A bundle-level
  before-grep was **not possible**: the rebuild pruned/untagged the old image (`85924507…` "No such
  image"), so the pre-slice bundle bytes could not be re-read. The discriminating proof therefore remains
  the **JS asset name/hash move (`index-CaM3_fbA.js` → `index-DtD-fVNX.js`) plus the one-issuance rebuild
  and the moved `index.html` reference.** The markers are cited as the "shipped surface is live" read
  (`PG-DP-01`), not as the change proof. Stated so no criterion reads as passing vacuously.
- **F-SG170-4 — the default docker socket (`/var/run/docker.sock`) is root-only on this host**
  (mode `s---------`), and `sudo` is unavailable (`no new privileges` flag). The lane provides a per-unit
  runtime socket at `$XDG_RUNTIME_DIR/docker.sock` (`/run/dispatch-storagegenie-SG-170/docker.sock`); all
  docker commands ran with `DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock` exported. This is the same
  lane mechanism SG-168 used; recorded for the next rider. Not a privilege denial routed around — the
  socket is the lane's grant.
- **F-SG170-5 — `contract-v0.46.0` tag lives on the Launcher contract remote, not the StorageGenie
  repo** (confirms `F-SG168-4`). StorageGenie's own origin carries no `contract-v*` tag;
  `rules_check.sh` reads `G-L1 UNCHECKED` because the local checkout is not *at* a tag. Recorded ==
  published is established by the peeled tag (`925cb575…` == contract HEAD) + the payload hash.

**No vacuous pass:** the rebuild is evidenced by a changed image ID (one build), the recreate by a
changed container ID, health by six quoted bodies on both sides, counts by a full 28-table read on both
sides, the served surfaces by a marker grep of the served JS **backed by** the asset-name/hash move, and
CORS by live OPTIONS preflights with zero writes. No gate skipped, no mutating live request sent. The one
honest caveat is F-SG170-3 (the marker grep alone is not discriminating; the asset move is).

---

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| **A1** rebuilt + one recreate + live | image ID new (one build)? container ID new (one recreate)? health ×6 delta 0, counts delta 0, preflight green? | YES — `85924507…`→`5f4f4ccb…`, `a31f940c…`→`420c4051…`, health ×6 = 200 delta 0, 28/28 counts delta 0, preflight 200/400/400 green |
| **A2** no migration | `alembic current` == head both sides? `models/`+`alembic/` diff empty? | YES — `20260924_sg114_relation (head)` both sides; `git diff 2035062 -- backend/app/models backend/alembic` **EMPTY** (0 lines) |
| **A3** product diff empty | is the diff exactly worklogs? | YES — only `docs/worklogs/SG-170*` added; `git diff 2035062 -- . ':(exclude)docs/worklogs'` EMPTY (0 lines) |
| **A4** report + receipt remote | report + notes-ref note (Dispatch-ID + Work-HEAD) read back on remote? writes = rebuild + one recreate only? | YES — see Receipt; production writes = one rebuild + one recreate; image IDs quoted; publish-before-bound honored (elapsed ≈ 111 s ≪ 1050 s) |
| **A5** guards invoked | PG-DP-01, PG-DP-02, PG-IC-01, PG-IC-07, PG-PR-04, PG-PR-10 | YES — see Guards below |

---

## Guards (A5)

- **`PG-DP-01`** — the fixed code is *running*, not re-read: the served-bundle markers for the shipped
  empty-state are read from the serving container, and the served JS asset name/hash moved.
- **`PG-DP-02`** — full end-to-end sweep **waived** (restart-gated); substitute coverage = health ×6 /
  28-table counts / CORS preflight / bundle proof + SG-169's green targeted suites; no browser hits.
- **`PG-IC-01`** — cross-product run; no blanket bans. The only in-slice collision (theme/empty-state CSS
  byte-identical vs "bundle moved") was resolved by stating the JS move as the proof (F-SG170-1).
- **`PG-IC-07`** — live UTC clock (`date -u`); no fixed time gate; base named as resolved commit
  `2035062…`, stated as an ancestor of HEAD (not as `HEAD`); tag check via live `ls-remote`.
- **`PG-PR-04`** — rebuild + one recreate + verify through the documented lane commands
  (`BUILDX_CONFIG=… docker compose build backend`; `docker compose up -d --no-deps backend`).
- **`PG-PR-10`** — no migration; `alembic current` == head both sides; `models/`+`alembic/` diff empty;
  exactly one recreate (a second would be a STOP); live DB read-only (28 counts both sides, delta 0).

---

## Budget — actual vs bound, per leg (units stated)

| leg | bound | actual |
|---|---|---|
| recon + orientation | 120 s | ~55 s |
| BEFORE capture | 120 s | ~5 s |
| rebuild (build class) | 600 s | **27 s** |
| recreate | 120 s | **2 s** |
| AFTER verify | 120 s | ~10 s |
| report + receipt | remainder | see below |
| **overall** | **2400 s** (lane `RUN_BUDGET_S=2100`) | within; lane start `19:09:21Z`, notes publish `19:11:12Z` (≈111 s ≪ `1050 s` half-bound) |

No command hit its bound; nothing was killed; no command needed a retry. **Spend: REAL $0.000000 USD +
zero metered calls.**

---

## Receipt

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The receipt is the note on
`refs/notes/storagegenie-coder-reports`; the refspec is fetched into a **mapped** local name
(`refs/notes/sg170-fetched`) and each `show` is pasted verbatim below (a default fetch never carries
notes). **WORK_HEAD = `b8017b772f58bd4ee0498654e8b109a4e48d331d`** (deploy-evidence commit).

```
$ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m "Dispatch-ID: SG-170 | Report: docs/worklogs/SG-170_report.md | Work-HEAD: b8017b772f58bd4ee0498654e8b109a4e48d331d" b8017b772f58bd4ee0498654e8b109a4e48d331d
add_wh_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
notes_push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg170-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg170-fetched show b8017b772f58bd4ee0498654e8b109a4e48d331d
Dispatch-ID: SG-170 | Report: docs/worklogs/SG-170_report.md | Work-HEAD: b8017b772f58bd4ee0498654e8b109a4e48d331d
show_wh_exit=0
```

**note=yes** (required note present on WORK_HEAD, read back through the mapped refspec). The report
commit note is added after this file is committed (`CO-79`: the report cannot contain the moment its own
receipt is published); the very tip's final note is published by the runner after this file is committed.

---

## UNCLEAR

- **FIRST READ:** whether the SG-169 empty-state bundle was expected to carry a stylesheet change.
  Resolved by measuring: the served CSS is byte-identical because the change re-used existing Tailwind
  classes; all changed bytes are in the JS chunk (F-SG170-1). Also: the default docker socket is
  root-only on this host — the lane's per-unit runtime socket is the grant (F-SG170-4).
- **DURING EXECUTION:** whether the served-marker grep alone could stand as the "is the fixed code
  running" proof. Resolved: the two markers are new to the served source (commit `4db8da3` has 0), but the
  old image was pruned so no bundle-level before-grep was possible; the JS asset name/hash move
  (`index-CaM3_fbA.js` → `index-DtD-fVNX.js`) plus the moved `index.html` reference is the discriminating
  change proof; markers are the presence read; disclosed loudly (F-SG170-3).
- **REMAINING:** the owner's visual verdict on the now-served chat empty-state; the taxonomy-mapping slice
  (`D-1012-8`) and per-category-hint copy (SG-169 REMAINING-2) remain outside this rider's scope.
