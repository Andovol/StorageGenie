SG-174 — Standing close-out rebuild, one recreate and live verification

**Dispatch identity (`PB-4`, read from `/proc/697104/cmdline`, never a system-prompt line):**
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`
(wrapper `bash /usr/local/lib/dispatch/run-coder SG-174`) → **model `opencode-go/deepseek-v4.1-flash`, effort
`max`** (D-1012-15). Work dir `/home/andrei/StorageGenie` · origin `git@github.com:Andovol/StorageGenie.git`.

**BASE ref requested:** `automation` → **resolved commit `f53fcd554544421641fe41a8d9751f8becc4f5b1`**
(== local HEAD at start == `origin/automation`; worktree clean at start — `git status --porcelain` empty before
the first in-slice log). **WORK_HEAD: `ab55c0163d2025470bb81c2ea1253521c9cfdc33`** (deploy-evidence commit: the
six leg logs). **Report commit:** the commit carrying this file (noted on the notes ref after publication;
its hash cannot appear inside itself, `CO-79`). **Authoring-date metadata 2026-10-12; live UTC clock throughout.**

**RESULT: deploy rider complete — one rebuild + exactly one recreate, new live instance verified, no repair
claimed.** Container `91a07373…` → **`23d31ff5…`** (Created `2026-10-12T20:03:57Z` → `2026-10-12T21:05:12Z`);
health ×6 green; schema head unmoved; 28/28 table counts delta 0; served bundle byte-identical (expected:
product bytes unchanged); zero product hunks; production DB read-only throughout. The SG-173 story defects
(stale blocked-Accept, classification has no UI, bare Resolve) are **still present and unchanged** — SG-175..178
repairs are not shipped by this rider.

**Contract echo (verbatim + source):** `/home/andrei/storagegenie-contract/VERSION` = **`0.46.0`**; `RULES.md`
sha256 `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` == `RULES.sha256` == the installed
`487841B1…` payload recorded in `AGENTS.md` for 0.46.0. **Recorded == published == host; zero version delta**
vs the packet's expected 0.46.0. `bash /home/andrei/storagegenie-contract/rules_check.sh` exits **3**,
re-measured:

    G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract
    G-L5 UNCHECKED gh-unauthenticated
    G-L7 UNCHECKED gh-unauthenticated
    G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275
    G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933
    G-L6 BYTES total[codex]=2275 unseen=architect-layer,state-file,other-ritual-files
    G-L6 BYTES total[opencode]=1933 unseen=architect-layer,state-file,other-ritual-files

Known host shape, independently explained in SG-173 (F-SG173-6): `G-L1` is the local tag-ref shape (checkout at
the tag's peeled commit `925cb575…`, no local tag object — F-SG168-4 lineage); L5/L7 are the unauthenticated
`gh` on this host; the two `G-L6 BYTES total[…]` lines are the richer current output shape — **same payload,
same exit 3, no version delta. No host tag/auth/config was touched or repaired** (not licensed; `PG-PR-03`).

---

## (a) Issues / deviations / surprises

- **SG-174-I1 (measured premise delta, `PB-1`) — the image ID moved although every build step was CACHED.**
  BEFORE tag `storagegenie-backend:latest` = `sha256:9064d2ce…` (the packet's expected live image, re-observed);
  after the one build the tag = `sha256:d5da5684…` (manifest list; config `78fcc311…`, attestation manifest
  `8732c6f9…`, `SG-174_build.log`). All 23 build steps report CACHED and the served `/app/static` bytes are
  byte-identical on both sides, so the moved ID is buildkit attestation/manifest re-export, **not a product
  change**. The packet warned that a reproducible build *may retain* its image ID and that neither retention nor
  identity is proof of recreation; here it is the inverse shape (ID moved, bytes identical) and it is likewise
  neither failure nor proof. **Recreation is proven by container identity and start time, as stated.**
- **SG-174-I2 — the http/https gate reading is Host/SNI-dependent.** Bare `http://127.0.0.1/` reads `404` and
  `https://127.0.0.1:443/` reads `303`; pinned to the vhost (`--resolve storagegenie.dynv6.net:80/443:127.0.0.1`)
  it reads the SG-172-precedent `301`/`401` on both sides (`SG-174_before.log`, `SG-174_after.log`). Both
  asymmetries measured once and reported, not smoothed.
- **SG-174-I3 — the first BEFORE capture was defective and was corrected once.** Two defects in my capture
  script: `SELECT candidate_id` against a column that does not exist (real column is `id`; sqlite traceback) and
  a `sha256sum` glob expanded on the host instead of in the container. Cause: I wrote a query from recall
  instead of reading the schema (`CO-12` slip); corrected by `PRAGMA table_info(candidate)` and `sh -c` in the
  container. The superseded run's traceback is in this session; the committed `SG-174_before.log` (21:04:35Z) is
  the corrected, complete capture. No product or production effect; no verification rerun.
- **SG-174-I4 — `.rules-cache/` is still absent from the workspace** (AGENTS.md Loading line). Ran the check
  from the host contract path; same shape as F-SG172-3/F-SG173-1, re-measured. Not a contract drift.
- **SG-174-I5 (method note) — docker capability was read, not probed by a privileged write.** The lane socket
  `/run/dispatch-storagegenie-SG-174/docker.sock` (mode `srw-rw---T`, `RUNTIME_SOCKETS=docker.sock`) answers
  `docker version` (Server 29.6.2, exit 0); the default `/var/run/docker.sock` is root-only (`s---------`) and
  was not used; `sudo` exists but **was not invoked** (no route-around, `PG-PR-03`). Same lane grant as
  SG-172/173 (F-SG172-5).

**INTENT:** the deploy path does one cache-exact rebuild + one recreate of `storagegenie-backend`; the check
expects a new container identity with health green and no migration/row change; the packet says exactly that
("neither image-ID retention nor identical hashes is failure here"). X / Y / Z agree — no disagreement to stop.

**TWINS:** not applicable — no defect fixed, no predicate replaced (documentation-only diff ceiling).

---

## (b) Actions

- **Changed paths (all tracked, all in scope):** `docs/worklogs/SG-174_before.log`, `SG-174_diff.log`,
  `SG-174_build.log`, `SG-174_recreate.log`, `SG-174_after.log`, `SG-174_verify.log` (WORK_HEAD `ab55c01`);
  report commit adds `SG-174_report.md` + `SG-174_receipt.log`. No other path was created or modified.
- **Commits/push:** WORK_HEAD `ab55c0163d2025470bb81c2ea1253521c9cfdc33` pushed
  (`f53fcd5..ab55c01  automation -> automation`, push exit 0, `origin/automation` == `ab55c01`); report commit
  pushed immediately after this file is committed.
- **Production / external effects:** (1) one image rebuild — local tag re-export only, no registry push;
  (2) **exactly one backend container recreate** (production restart; `Recreate/Recreated/Starting/Started`,
  `SG-174_recreate.log`); (3) notes-ref push to GitHub (receipt). **No host config change, no sudo, no second
  recreate. Production SQLite read-only:** counts read through `file:…?mode=ro`, `alembic current` read-only;
  zero INSERT/UPDATE/DELETE; no manual resolving, imports, or evidence-store mutation; only GETs and OPTIONS
  preflights against the app; no browser interactions; zero paid/provider API calls.
- **Durations (UTC, `CO-79`; from leg logs' embedded stamps):** lane start `21:01:08Z` (source:
  `ps -o lstart` PID 697063 / RUNTIME_DIRECTORY mtime). **Orientation + recon + contract echo ≈ 203 s**
  (`21:01:08→21:04:31`, includes the corrected capture attempt). Fast remainder as one aggregate ≈ 66 s:
  BEFORE capture 14 s (`21:04:35→21:04:49`), build 3 s (`21:04:49→21:04:52`), recreate 1 s
  (`21:05:12→21:05:13`), AFTER capture 14 s (`21:05:26→21:05:40`), verify 5 s, commit+push ~5 s, receipt
  publish+read-back 10 s (`21:06:51→~21:07:01`). Report writing + commit ≈ `21:08→21:09`. **End and total as
  of report writing: `21:07:57Z`, ≈ 409 s** (the final figure is the runner's record, not this file's).
- **Retry count:** 0 dispatch retries; 1 in-slice capture correction (SG-174-I3, not a prove-attempt).
  **Test-command count: 0** (full suite waived per `PG-DP-02`; SG-173's already-executed targeted controls are
  the packet-declared substitute). **Provider-call count: 0.**
- **Health delta:** none (start and end batches identical, below).
- **Highest-impact action:** the single backend recreate — production traffic now served by container
  `23d31ff5…` of the re-exported tag.

---

## G1 — read-only pre-state (`SG-174_before.log`, 21:04:35Z)

    git:      f53fcd554544421641fe41a8d9751f8becc4f5b1 == origin/automation; porcelain = only in-slice logs
    container 91a073730e495dae222f179710879199237398040926adbbf8c57602fe97ef3f
    image     sha256:9064d2ced325220a4e7a2a16670cf678651e142c032c840e6e1e2d059c0cd4bf  (expected 9064d2ce — confirmed)
    RestartCount=0 · Created=2026-10-12T20:03:57.235297734Z · StartedAt=2026-10-12T20:03:58.043100489Z · healthy
    health ×6: {"status":"ok","db":"ok","storage":"ok"} [200] every time
    gate: http:80 = 301 · https:443 = 401 (vhost-pinned)
    alembic current: 20260924_sg114_relation (head)
    bundle: index.html 2f035becd05b63e226af82e2e8fe60c8f3b5effb9f37e49dd95a2265c4da0d55
            assets/index-CYyuxefG.js 1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d (322255 B)
            assets/index-DO0gjGV6.css 37b25dbdd4b0ecfdedb8255bc7f8af286726334e95a1a3a9e85b9ba381b3d57c (3911 B)
    tables: 28 enumerated on target (not assumed); counts incl. provider_call 29, audit_event 91, job_step 72,
            asset 7, candidate 10, review_task 8, evidence 18, job 11, assertion 37, observation 20
    prod DB: data/db/storagegenie.db sha256 e6bef157440fb8b4a3262577362b071dcae07507ea9a7e04a614e11be28ee5bd
    CORS: If-Match PATCH => 200 · TRACE => 400 · X-Evil-Header => 400 · allow-methods GET,POST,PUT,PATCH,DELETE,OPTIONS
    candidates enumerated (5); chosen /review 01a0afaa-3ff4-7da0-987a-87f29c73ee5b; /review,/inbox,/catalog => 200,200,200
    served-JS markers: review_task_ids=2 · blocked sentence=2 · View them in the Inbox=1 · Thumbnail unavailable=2

**Product-diff guard (`SG-174_diff.log`, 21:04:31Z):** `git diff 3ae5541 f53fcd5 -- backend frontend` **EMPTY**;
`git diff --stat 3ae5541 -- backend/app/models backend/alembic` **EMPTY**; worktree product dirt **none**.
Non-product changes since the deployed base `3ae5541` are docs only: `AGENTS.md`, `STATE.md`,
`docs/decisions/2026-10-12-codex-dispatch-transport.md`, `docs/history/archive-2026-10-12-pre-SG173-resume.md`,
`docs/packets/SG-173*`, `docs/packets/SG-174*`, `docs/ratings.md`. **Expectation confirmed — deployed product
tree unchanged; guard passed before any deployment command.**

**BUILD (exactly one, `SG-174_build.log`):** `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend`
(plus `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-174/docker.sock`) → **exit 0, 3 s**; all stages CACHED;
tag re-exported as manifest list `d5da5684…` (SG-174-I1).

**RECREATE (exactly one, `SG-174_recreate.log`):** `docker compose up -d --no-deps backend` → **exit 0, 1 s**;
one `Container storagegenie-backend-1 Recreate / Recreated / Starting / Started`; no second issuance.

## G2 — post-recreate verification (`SG-174_after.log`, 21:05:26Z; `SG-174_verify.log`, 21:06:32Z)

    container 23d31ff5f3caa07d6b019f57ce686a595687e4dff64f8f8be708307bf5f124b9   (CHANGED — recreate proof)
    image     sha256:d5da5684a95e20e2ea9d85f8eddcbd007b2542cc6493ebb2f0da090bb2419927 (re-exported tag)
    RestartCount=0 · Created=2026-10-12T21:05:12.713648479Z · StartedAt=2026-10-12T21:05:13.674463854Z · healthy
    health ×6: {"status":"ok","db":"ok","storage":"ok"} [200] every time          — delta 0
    gate: 301/401 unchanged · alembic 20260924_sg114_relation (head) unchanged    — no migration
    served sha256: identical on all three (index.html 2f035bec, JS 1b4680a0, CSS 37b25dbd)  — product bytes unchanged
    tables: 28/28 identical values; counts delta 0 (all-delta diff empty in SG-174_verify.log)
    prod DB sha256: e6bef157… unchanged (re-read at 21:06:32Z)                    — no slice-caused row change
    CORS + allow-methods: identical · pages /review/01a0afaa-…, /inbox, /catalog => 200,200,200
    served-JS markers: 2 / 2 / 1 / 2 — identical; SG-171/172 gating code is what is being served

The recreate is proven by container ID + Created/StartedAt, **not** RestartCount (a recreate replaces the
container; 0 → 0). Identical bundle hashes are expected because product bytes did not move; they are **not**
offered as recreation proof, and no changed-bundle requirement is invented (`PB-3`: no vacuous pass — the
identity move is the evidence, and the counts/pages/preflights are nonempty observations).

**Known defects expressly unchanged (`A2`):** the served JS still carries the SG-172 generation markers; the
SG-173 diagnosis' defects — stale embedded `review_task_ids` blocking Accept, no classification UI, bare
Resolve erasing the manual-entry reminder — are code that this rider did not touch and did not serve repaired.
Zero product hunks in the slice diff (below).

---

## (c) Verification — final summary blocks

Work-diff scope (`SG-174_receipt.log`): `git diff --name-only f53fcd5 ab55c01` =

    docs/worklogs/SG-174_after.log
    docs/worklogs/SG-174_before.log
    docs/worklogs/SG-174_build.log
    docs/worklogs/SG-174_diff.log
    docs/worklogs/SG-174_recreate.log
    docs/worklogs/SG-174_verify.log

Committed blob sha256 (bytes as pushed on WORK_HEAD):

    c96d2c6c4658cb682d3f7021540df2e0373cf923ef6e5eb3b7bb4035f178f711  SG-174_before.log
    9f456b2105872f77a107ff73c19f70fc7aa897c30ec1f12e2073183bef151c5a  SG-174_diff.log
    100503acf836716f9c02855eb22780f65e6f2bc5a057672cec70e71ac69444a8  SG-174_build.log
    5265819f069e0d9278cd9a16d1cd38cef06b1c803615bf6d4d43821048ff12db  SG-174_recreate.log
    88aaee3101c9081b1e663c00b269dd1156a8c99c985518d9bb043bd1c0a2a8d3  SG-174_after.log
    dcb178c7195daeeb726ee135b7700e9e074a3720f1f8a520259f25b858cf8d4e  SG-174_verify.log

BEFORE-vs-AFTER mechanical diffs (`SG-174_verify.log`; every `*_diff_exit=0`): health lines, table counts,
served sha256, alembic head, CORS section, marker counts, story pages, prod-DB hash — all empty; the only
moved fields are the container identity trio (Id/Created/StartedAt) and the image tag digest.

Health (`CO-92`): start 6× `{"status":"ok","db":"ok","storage":"ok"}` [200]; end 6× same — **HEALTH: unchanged, OK**.

Receipt (`CO-60`/`CO-97`; transcript in `SG-174_receipt.log`; mapped refspec — a default fetch never carries notes):

    $ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m "Dispatch-ID: SG-174 | Report: docs/worklogs/SG-174_report.md | Work-HEAD: ab55c0163d2025470bb81c2ea1253521c9cfdc33" ab55c0163d2025470bb81c2ea1253521c9cfdc33
    add_wh_exit=0
    $ git push origin refs/notes/storagegenie-coder-reports
       c6f8610..a9c61fa  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    notes_push_exit=0
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg174-fetched
    fetch_exit=0
    $ git notes --ref=refs/notes/sg174-fetched show ab55c0163d2025470bb81c2ea1253521c9cfdc33
    Dispatch-ID: SG-174 | Report: docs/worklogs/SG-174_report.md | Work-HEAD: ab55c0163d2025470bb81c2ea1253521c9cfdc33
    show_wh_exit=0

**note=yes** (WORK_HEAD note published and read back through the mapped refspec). The report commit receives
the same note **after** this file is committed (its hash cannot appear inside itself); that post-report step's
output is recorded by the runner. The legacy `finalize_dispatch_report.sh` was **not** used.

---

## Acceptance criteria — question answered

- **A1** — one rebuild (exit 0, all-cached, 3 s) + exactly one recreate (exit 0, one
  Recreate/Recreated/Starting/Started) → new running instance `23d31ff5…` Created `21:05:12Z`; health ×6 green;
  explicit deltas: container id CHANGED, image tag CHANGED (re-export), Created/Started CHANGED; schema head
  unchanged; counts 28/28 delta 0; bundle hashes unchanged (expected). **YES.**
- **A2** — base requested `automation` → resolved `f53fcd55…`; product diff vs deployed base `3ae5541` EMPTY
  (backend/frontend/models/migrations); work diff = only `docs/worklogs/SG-174*` (six names above); old
  code/known SG-173 defects expressly identified as unchanged and still served. **YES.**
- **A3** — command logs (`SG-174_before/diff/build/recreate/after/verify.log`) + this report; per-leg elapsed and
  total vs lane bound below; every constraint answered; UNCLEAR dispositioned. **YES.**
- **A4** — notes-ref receipt published + mapped-fetch read-back verified (transcript above); first line
  `Dispatch-ID: SG-174 | Report: docs/worklogs/SG-174_report.md` (+ Work-HEAD); branch push complete
  (`f53fcd5..ab55c01`, origin == `ab55c01`); report push complete immediately after this file commits. **YES.**

**Guards invoked:**
`PG-DP-01` — the deploy rider IS the delivery path; the running instance is re-observed post-recreate by
container identity and served bytes, not inferred. `PG-DP-02` — full end-to-end sweep **waived** (production
restart; externally-driven hits would exercise the previous build); substitute = post-recreate read-only
identity/health/schema/counts/pages/preflight verification + SG-173's already-executed targeted regression
controls (30 backend + 23 frontend passed); no browser-driven hits run. `PG-IC-07` — live UTC clock at every
step; base named as the resolved commit; no fixed-time gate. `PG-PR-03` — no privileged denial occurred; the
lane docker socket is the grant; `sudo` never used; no route-around. `PG-PR-04` — how the code becomes live is
stated and was executed: the documented build+recreate lane commands. `PG-PR-06` — runtime vs bound below.
`PG-PR-10` — no state created; production SQLite read-only; no migration; exactly one restart.

## Budget — actual vs bound (units seconds; source per item)

    lane bound:  RUN_BUDGET_S=2100        (source: process environment; /etc/dispatch/storagegenie.conf;
                                           systemd unit TimeoutStartSec=${RUN_BUDGET_S})
    idle kill:   IDLE_KILL_S=900 default  (source: run-coder LNR-051 G2, declared uncalibrated) — never approached
    per-command: 120 s ordinary / 600 s build (packet) — longest named command = build, 3 s; nothing killed, no
                 command hit its bound, no visible timeout finding
    half-bound:  ≈1050 s convention (SG-172 precedent) — report+receipt complete by ≈21:07Z, ≈360 s
    actual:      lane start 21:01:08Z → end as of report writing 21:07:57Z = 409 s total; identified legs in (b).
    Coder-platform spend: not exposed to the slice (no meter readable); application provider spend = $0.000000, 0 calls.

## Constraints — every stated constraint answered

Scope `docs/worklogs/SG-174*` only — **answered** (work-diff names). No product/config/schema/migration/test
edits — **answered** (product diff empty; diff is six logs + report + receipt log). No production
INSERT/UPDATE/DELETE, manual resolving, imports, evidence-store mutation — **answered** (read-only `mode=ro`
reads; GET/OPTIONS only). One rebuild + one recreate only; second issuance STOP — **answered** (exactly one
each; none second). Bounds 120/600 s, no visible timeout, never approach 900 s idle kill — **answered**.
No interactive prompt or polling loop — **answered**. Full suite waived per `PG-DP-02` with substitute named —
**answered**. No new behavior test required — **answered** (no code shipped). Application provider spend
prohibited — **answered** ($0, 0 calls). Runtime-vs-lane budget reported with seconds and source, not guessed —
**answered** above. PG-PR-03 privilege denial is STOP, never sudo/another identity/another mount — **answered**
(no denial; grant lane socket; no sudo). No host config changes — **answered**.

## UNCLEAR — every item dispositioned

- **FIRST READ:** whether "expected live image is 9064d2ce" means the *deployed bytes* identity or the
  *tag digest*. Measured post-build: tag digest moved to `d5da5684…` (attestation manifest re-export) while
  every layer stayed CACHED and served bytes are identical (SG-174-I1). Disposition: reported as measured; the
  packet's rule ("neither is failure … neither is proof of recreation") applied; recreation proven by
  container identity.
- **FIRST READ:** the bare-IP gate read (`404`/`303`) disagreed with the SG-172-quoted `301`/`401`.
  Disposition: Host/SNI vhost selection; pinned `--resolve` reproduces `301`/`401` — both captured (SG-174-I2).
- **DURING EXECUTION:** my first BEFORE capture failed on a guessed column name and a host-side glob —
  corrected once on the same hypothesis-free path (schema read via PRAGMA; in-container `sh -c`); committed log
  is the corrected complete capture (SG-174-I3). Impact: none on target; one in-slice re-capture.
- **REMAINING:** owner visual verdict on the live review gating; the SG-175..178 repair chain (D-1012-14 scope)
  remains unshipped, including D-1012-13 folded into SG-177 and F-SG171-5 into SG-175; F-SG173-1/6 host
  cache/tag/auth shape stays inherited-open with no host change authorized; F-SG144-1 venv follow-up and the
  parked Scene arc (D-1012-6) remain backlog. The report-commit receipt note is published post-report by
  construction (CO-55(b)).
