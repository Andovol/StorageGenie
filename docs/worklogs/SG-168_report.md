# SG-168 — Close-out deploy rider: serve SG-167 theming (rebuild + one recreate + verify)

**Dispatch:** SG-168 · **Coder:** opencode · **Model:** `opencode-go/deepseek-v4.1-flash` · **Effort:** `high`
(from process arguments — `/proc/$PPID/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie
--model opencode-go/deepseek-v4.1-flash --variant high`).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**BASE ref requested:** `automation` → **resolved commit:** `4db8da3b88d2fe3cbbef9ca04d2e935da93a40f5`
(== local HEAD at start, worktree clean). **WORK_HEAD:** `e663c13a6bdaa606205aeec1762ee865c01a7898`
(deploy-evidence commit carrying the before/build/recreate/after/verify logs).
**Authoring date (metadata):** 2026-10-12. Live clock reads below.
**Type:** DEPLOY RIDER. Production restart + production writes authorized **solely** by owner quote
"Both approved." (`D-1012-7`) plus the standing close-out directive (`AGENTS.md` Close-out row;
"Always do a live deploy before session close", owner 2026-09-28, `G-O4`).
**Zero product hunks expected — and zero produced.**

**Contract echo (verbatim):** `0.46.0` — source path `/home/andrei/storagegenie-contract/VERSION`.
Contract HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730` == `refs/tags/contract-v0.46.0^{}` (verified
live by `git -C /home/andrei/storagegenie-contract ls-remote --tags origin`); `RULES.md` sha256
`487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` == the installed `487841B1…` payload
recorded in `AGENTS.md` for 0.46.0. **Recorded == published.** `.rules-cache/` is absent on the host
(`F-SG145-1`/`F-SG167-3`); the live contract checkout is the source path. `G-L1 UNCHECKED` here is a
local-tag-fetch shape, not payload drift (`F-SG165-1`, re-measured).

**Money posture (REAL $):** **$0.000000 USD actual**, **zero metered calls** — no USD-metered
provider/model path exists anywhere in this slice (image rebuild + container recreate + local reads).
Spend constraint ($0) honored.

---

## What this slice did

Served the SG-167 theming: SG-167 landed two frontend files on disk (`ChatPage.tsx` household select
theming; `InboxPage.tsx` `Resolve` + `Retry failed job` theming) that the running service (image
`0bed0cc4…`, the SG-165 generation) did not serve. This slice is **rebuild + exactly one recreate +
verify only**. No product, test or config byte was edited: the diff ceiling is `docs/worklogs/SG-168*`.

How the code became live (`PG-PR-04`): `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`
(one rebuild) + `docker compose up -d --no-deps backend` (exactly one recreate) + verify.

---

## G1 — rebuild (one) + exactly one recreate

**BEFORE (read-only, capture 2026-10-12T18:34:25Z):**

| field | value |
|---|---|
| container | `41ac9fd1ed963908d3c6e31628daa7c911bfe96e076f7ecd5c65411041d9b187` |
| image | `sha256:0bed0cc46f27f8d9d39fd3f0f41bce14cb4d9894a55d93356872d276284b2956` (expectation `0bed0cc4` — **confirmed**) |
| RestartCount / Created | `0` / `2026-10-12T16:36:03.320632037Z` (SG-165 generation, unchanged since) |
| health | 6× 200 `{"status":"ok","db":"ok","storage":"ok"}` |
| gate | http:80 **301** / https:443 **401** |
| alembic | `20260924_sg114_relation (head)` |
| bundle | `index-C7iDBZmw.js` `a6c89a57…` (321242 B) + `index-DO0gjGV6.css` `37b25dbd…` (3911 B) |
| index.html | `e394fd6b…` (references `assets/index-C7iDBZmw.js`) |

**BUILD (exactly one):** `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` →
`BUILD_EXIT=0`, **29 s** (`18:34:38Z → 18:35:07Z`). Image **`sha256:0bed0cc4…` →
`sha256:85924507a2442f33427dc09464420c533712b3fcf5689bae5a9eaa634f4481e3`** (new). The `BUILDX_CONFIG`
relocation is the documented EROFS-sandbox workaround (SG-132/SG-142/SG-143/SG-154/SG-165 precedent).
The frontend stage re-ran `tsc && vite build` (not cached — the SG-167 `frontend/` bytes are what
changed): `dist/assets/index-CaM3_fbA.js 321.20 kB` (was `index-C7iDBZmw.js`).

**RECREATE (exactly one):** `docker compose up -d --no-deps backend` → `REC_EXIT=0`, **2 s**
(`18:35:11Z → 18:35:13Z`), exactly one `Recreate / Recreated / Starting / Started`.

| field | BEFORE | AFTER |
|---|---|---|
| container id | `41ac9fd1ed96…` | **`a31f940cdc23d3e9467f6938e175be49527ca4326dc786e908099ab366e0de35`** |
| image | `sha256:0bed0cc4…` | **`sha256:85924507…`** |
| RestartCount | 0 | 0 |

The recreate is proven by the **container-id change**, never by `RestartCount` (a recreate replaces the
container; the counter reads 0→0). Exactly one recreate was issued (a second is a STOP) — none was.

---

## G2 — verify live (state change by post-state)

AFTER capture `2026-10-12T18:35:21Z` (all quoted in `SG-168_after.log` / `SG-168_verify.log`):

- **Health ×6 exact** through `{{HEALTH_CMD}}` (`curl -s http://127.0.0.1:8003/v1/health`): all six
  bodies `{"status":"ok","db":"ok","storage":"ok"}` at HTTP 200 — **delta 0 vs BEFORE**.
- **Gate:** http:80 **301** / https:443 **401** — both unmoved.
- **Alembic:** `20260924_sg114_relation (head)` == BEFORE (unmoved; no migration run).
- **Counts — delta 0 on every table:** 28/28 BEFORE == AFTER. None moved (`provider_call` 27 == 27;
  `audit_event` 78 == 78; `asset 6`, `candidate 9`, `review_task 7`, `job 10`, `job_step 64`, `user 2`).
- **Served bundle MOVED (rebuild proof):** `index-C7iDBZmw.js` `a6c89a57…` (321242 B) →
  **`index-CaM3_fbA.js` `2fe32c978bf59a9fab8465473b88e46d0184c59a051545cd70f8395e42c6c707` (321317 B)**;
  `index.html` moved `e394fd6b…` → **`a18b9684…`** (references the new `assets/index-CaM3_fbA.js`).
  The CSS bundle is **byte-identical** `index-DO0gjGV6.css` `37b25dbd…` (3911 B) — expected per
  `F-SG165-2`: the SG-167 theming re-uses existing Tailwind tokens, so no new CSS bytes; **the JS move
  carries the proof.**
- **Served markers in the fresh JS** (`grep -F` of the served bundle; each quoted ×1): `Retry failed
  job` ×1 · `Resolve` ×2 · `Household` ×10 · themed class token
  `bg-background text-foreground border-border focus-ring` ×24. These markers show the shipped surfaces
  are present in what is served (the `PG-DP-01` "is the fixed code even running" read).
- **CORS live proof, ZERO writes** (OPTIONS preflight only; no PATCH/POST/PUT/DELETE sent):
  `OPTIONS /v1/assets` with `If-Match` → **200** (`access-control-allow-headers …If-Match…`);
  `Access-Control-Request-Method: TRACE` → **400**; `X-Evil-Header` → **400**;
  `allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS` (no HEAD). Identical to BEFORE.
- **Pages through the fresh server:** `/capture` `/inbox` `/catalog` → **200** each.
- **Full end-to-end sweep WAIVED** per `PG-DP-02` (restart-gated: externally-driven tests would exercise
  the previous build). Substitute coverage is the health/counts/preflight/bundle-marker proof above plus
  SG-167's already-green targeted suites; **no browser-driven hits were run.**

---

## Findings (premise corrections; reported, not bent)

- **F-SG168-1 — the CSS bundle is byte-identical again; only the JS moved (confirms F-SG165-2).** BEFORE
  and AFTER both ship `index-DO0gjGV6.css` sha256 `37b25dbd…` (3911 B). The SG-167 theming added
  `className`/`style` pairings and prop passes only; all changed bytes landed in the JS chunk
  (`index-C7iDBZmw.js` → `index-CaM3_fbA.js`). Direction stated explicitly — the deploy is proven by the
  changed JS name/hash + the served markers, not by a stylesheet move.
- **F-SG168-2 — `provider_call` reads 27, not the 25 last quoted in the SG-165 report.** This is a
  pre-slice delta (the SG-166 Muse direct-POST probe is the likely writer; outside this rider's scope and
  uninspected). It is the BEFORE baseline for this slice, and the restart moved **no** table: `27 == 27`.
  No migration and no write of any kind was issued by this slice.
- **F-SG168-3 (vacuity disclosure, loud per PB-3/AC caveat) — the marker grep is a presence read, not by
  itself a change-discriminator.** `Resolve` / `Household` / `Retry failed job` and the Tailwind class
  token are all literals that also existed in the pre-slice bundle; the served-bundle grep could not, on
  its own, distinguish old from new. **The discriminating proof is the JS asset name/hash move
  (`index-C7iDBZmw.js` → `index-CaM3_fbA.js`) plus the one-issuance rebuild and the moved `index.html`
  reference** — the markers are cited as the "shipped surface is live" read (`PG-DP-01`), not as the
  change proof. Stated so no criterion reads as passing vacuously.
- **F-SG168-4 — `contract-v0.46.0` tag lives on the Launcher contract remote, not the StorageGenie
  repo.** `git ls-remote --tags origin` on `/home/andrei/storagegenie-contract` (origin
  `git@github.com:Andovol/Launcher.git`) peels `contract-v0.46.0` to `925cb575…` == contract HEAD;
  StorageGenie's own origin carries no `contract-v*` tag. `rules_check.sh` therefore reads `G-L1
  UNCHECKED` (the local cache has no tag beyond `contract-v0.33.0`) — the SG-165 `F-SG165-1` /
  SG-167 `F-SG167-3` shape, not drift. Recorded == published is established by the peeled tag + payload
  hash.

**No vacuous pass:** the rebuild is evidenced by a changed image ID (one build), the recreate by a changed
container ID, health by six quoted bodies on both sides, counts by a full 28-table read on both sides,
the served surfaces by a marker grep of the served JS **backed by** the asset-name/hash move, and CORS by
live OPTIONS preflights with zero writes. No gate skipped, no mutating live request sent. The one honest
caveat is F-SG168-3 (the marker grep alone is not discriminating; the asset move is).

---

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| **A1** rebuilt + one recreate + live | image ID new (one build)? container ID new (one recreate)? health ×6 delta 0, counts delta 0, preflight green? | YES — `0bed0cc4…`→`85924507…`, `41ac9fd1…`→`a31f940c…`, health ×6 = 200 delta 0, 28/28 counts delta 0, preflight 200/400/400 green |
| **A2** no migration | `alembic current` == head both sides? `models/`+`alembic/` diff empty? | YES — `20260924_sg114_relation (head)` both sides; `git diff 4db8da3 -- backend/app/models backend/alembic` **EMPTY** (0 lines) |
| **A3** product diff empty | is the diff exactly worklogs? | YES — only `docs/worklogs/SG-168*` added; `git diff 4db8da3 -- . ':(exclude)docs/worklogs'` EMPTY |
| **A4** report + receipt remote | report + notes-ref note (Dispatch-ID + Work-HEAD) read back on remote? writes = rebuild + one recreate only? | YES — see Receipt; production writes = one rebuild + one recreate; image IDs quoted; publish-before-bound honored (elapsed ≈ 230 s ≪ 1050 s) |
| **A5** guards invoked | PG-DP-01, PG-DP-02, PG-IC-01, PG-IC-07, PG-PR-04, PG-PR-10 | YES — see Guards below |

---

## Guards (A5)

- **`PG-DP-01`** — the fixed code is *running*, not re-read: served-bundle markers for the shipped
  surfaces are read from the serving container, and the served JS asset name/hash moved.
- **`PG-DP-02`** — full end-to-end sweep **waived** (restart-gated); substitute coverage = health ×6 /
  28-table counts / CORS preflight / bundle proof + SG-167's green targeted suites; no browser hits.
- **`PG-IC-01`** — cross-product run; no blanket bans. The only in-slice collision (theme CSS
  byte-identical vs "bundle moved") was resolved by stating the JS move as the proof (F-SG168-1).
- **`PG-IC-07`** — live UTC clock (`date -u`); no fixed time gate; base named as resolved commit
  `4db8da3b…`, stated as an ancestor of HEAD (not as `HEAD`); tag check via live `ls-remote`.
- **`PG-PR-04`** — rebuild + one recreate + verify through the documented lane commands
  (`BUILDX_CONFIG=… docker compose build backend`; `docker compose up -d --no-deps backend`).
- **`PG-PR-10`** — no migration; `alembic current` == head both sides; `models/`+`alembic/` diff empty;
  exactly one recreate (a second would be a STOP).

---

## Budget — actual vs bound, per leg (units stated)

| leg | bound | actual |
|---|---|---|
| recon + orientation | 120 s | ~55 s |
| BEFORE capture | 120 s | ~60 s |
| rebuild (build class) | 600 s | **29 s** |
| recreate | 300 s | **2 s** |
| AFTER verify | 120 s | ~40 s |
| report + receipt | remainder | see below |
| **overall** | **2400 s** (lane `RUN_BUDGET_S=2100`) | within; lane start `18:33:33Z`, publish ≪ `1050 s` half-bound |

No command hit its bound; nothing was killed; no command needed a retry. **Spend: REAL $0.000000 USD +
zero metered calls.**

---

## Receipt

No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The receipt is the note on
`refs/notes/storagegenie-coder-reports`; the refspec is fetched into a **mapped** local name
(`refs/notes/sg168-fetched`) and each `show` is pasted verbatim below (a default fetch never carries
notes). **WORK_HEAD = `e663c13a6bdaa606205aeec1762ee865c01a7898`** (deploy-evidence commit).

```
$ git push origin automation
   4db8da3..dc42d03  automation -> automation
push_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-168 | Report: docs/worklogs/SG-168_report.md | Work-HEAD: e663c13a6bdaa606205aeec1762ee865c01a7898" e663c13a6bdaa606205aeec1762ee865c01a7898
add_wh_exit=0

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-168 | Report: docs/worklogs/SG-168_report.md | Work-HEAD: e663c13a6bdaa606205aeec1762ee865c01a7898" dc42d036c5a09e4c9ec794d7e8e2bd1f2ae551f2
add_rc_exit=0

$ git push origin refs/notes/storagegenie-coder-reports
   d3befe2..d22dce2  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
notes_push_exit=0

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg168-fetched
 * [new ref]  refs/notes/storagegenie-coder-reports -> refs/notes/sg168-fetched
fetch_exit=0

$ git notes --ref=refs/notes/sg168-fetched show e663c13a6bdaa606205aeec1762ee865c01a7898
Dispatch-ID: SG-168 | Report: docs/worklogs/SG-168_report.md | Work-HEAD: e663c13a6bdaa606205aeec1762ee865c01a7898
show_wh_exit=0

$ git notes --ref=refs/notes/sg168-fetched show dc42d036c5a09e4c9ec794d7e8e2bd1f2ae551f2
Dispatch-ID: SG-168 | Report: docs/worklogs/SG-168_report.md | Work-HEAD: e663c13a6bdaa606205aeec1762ee865c01a7898
show_rc_exit=0
```

**note=yes** (both required notes present on WORK_HEAD and the report commit; read back through the
mapped refspec). `note=yes`, read back on the remote. The report commit `dc42d03` is the tip at receipt
time; this transcript was carried by a follow-up receipt commit (`SG-165` `689c57c`→`f43ced8`
precedent), and the very tip's own final note is published by the runner after this file is committed
(`CO-79`: the report cannot contain the moment its own receipt is published).

---

## UNCLEAR

- **FIRST READ:** whether the SG-167 bundle was expected to carry a stylesheet change. Resolved by
  measuring: the served CSS is byte-identical because the theming re-used existing Tailwind classes; all
  changed bytes are in the JS chunk (F-SG168-1). Also: `provider_call=27` vs the SG-165-quoted 25 —
  a pre-slice write (likely SG-166), zero-delta across this restart (F-SG168-2).
- **DURING EXECUTION:** whether the served-marker grep alone could stand as the "is the fixed code
  running" proof, given the surface strings and class token also existed pre-slice. Resolved by naming
  the JS asset name/hash move (`index-C7iDBZmw.js` → `index-CaM3_fbA.js`) as the discriminating change
  proof and the markers as the presence read; disclosed loudly (F-SG168-3).
- **REMAINING:** the owner's visual verdict on the now-served theming (Chat household select, Inbox
  Resolve/Retry) and the remaining taxonomy-mapping slice (`D-1012-8`) plus the tree-wide native-control
  leaks (`F-SG167-2`) remain outside this rider's scope.
