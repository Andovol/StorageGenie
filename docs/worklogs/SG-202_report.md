SG-202 — Close-out deploy rider: SG-196 + SG-198 served live — one lane-socket rebuild + one recreate — both rated frontend slices SERVED and verified (CHANGED)

RESULT: CHANGED (CO-48 class 1; the repo work commit is evidence-only, the live service changed). Exactly ONE backend rebuild (exit 0, 15 s) and ONE recreate (exit 0, 1 s), both through this unit's own lane socket; zero denials anywhere. New container d868f373b661 (Created 2026-10-17T12:03:52.700720908Z, image sha256:15a1fe632ef87f459e9747afd21fd1fba29a5aff01566144c7ebec97ebe0f20d) replaced a77e3f2ff0dd (Created 2026-10-16T19:41:19.974177688Z, image sha256:e3b7c0aa…); RestartCount=0 both, recreate proven by ID/Created. Health green: start and end 200 ok/ok/ok; six post-recreate GETs all 200. Served JS bundle dd4f1bd0876de5dfba0b0bc351342a4e5ca3df35f8b5f4752e0ab31845579f53 (325039 B) != SG-197's 8ba02c64… (325053 B); index.html e3eb6736… != 5ce95f29…; CSS e1e5ff63… unchanged (no CSS change among the two slices' files — reported, expected). Production SQLite byte-identical end-to-end (no migration, no slice row change, all 28 table counts identical). The two slices are live: SG-196 markers present in the served bundle bytes (inbox-open-count ×1, "Could not load households" ×3, "Could not load catalog facets" ×1, "Could not load saved searches" ×1, "Select household" ×3); SG-198 is proven by the bundle rebuilt from the merged tree (new content-hashed filename index-DgiNiCw9.js == the served asset filename) plus the 12-file/162-test in-process run over the union of both reports' focused sets. SG-194's live cursor repair and the SG-188 control are unchanged (identical malformed-cursor 422 bodies).
model opencode-go/deepseek-v4.1-flash · effort max — read from /proc/808647/cmdline (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), PB-4; never from a system-prompt identity line. Served-model response metadata not available; no substitute value claimed. `max` catalogue-valid, uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch `automation` · remote git@github.com:Andovol/StorageGenie.git.
BASE ref requested `automation` → resolved commit 23c59b16c78f87ed4abb55aa226745cdfe0d8974 (== local HEAD == origin/automation at start after fetch; worktree clean; f757ebd/faea4d6/144190c all ancestors of HEAD — reachability form, PG-IC-07). WORK_HEAD 3857b6a37b7cb4c27186d3a71e0b2f34907c5eb1 (seven frozen evidence logs, +414 insertions). This report lands in the receipt-paste commit, so it does not carry its own hash (CO-55b); no field here is "final HEAD".
Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md lines 3-4, verbatim): "**Contract version: 0.50.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: /home/andrei/storagegenie-contract/VERSION=0.50.0; RULES.md sha256 49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed == RULES.sha256 (installed payload, clean). Recorded/published/host all 0.50.0 — NO difference to report. rules_check.sh output verbatim: `G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract` / `G-L5 UNCHECKED gh-unauthenticated` / `G-L7 UNCHECKED gh-unauthenticated` / `G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275` / `G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933` / `G-L6 BYTES total[codex]=2275 unseen=architect-layer,state-file,other-ritual-files` / `G-L6 BYTES total[opencode]=1933 unseen=architect-layer,state-file,other-ritual-files`; exit 3 (known host shape, independently explained in the SG-190/194/195/196/199 reports, reported as read, no host tag/auth/config touched).

(a) issues / deviations / surprises

- SG-202-I1 (probe precondition, disclosed and corrected). The first API-shape probe set omitted the required `household_id` on `/v1/jobs` and `/v1/review-tasks`, so both returned the 422 missing-param envelope (recorded as the current shape); a supplementary capture with `household_id=01a0a029-…` followed (same prestate log, appended). Both captures are committed; no measurement bent, no criterion affected.
- SG-202-I2 (vite display offset, reconciled not hidden; SG-197-I5 shape). The build log's human-readable line prints the JS as 324.92 kB while the served file is 325039 B; SG-193/SG-197 recorded the same shape (324.94 kB reported ↔ 325053 B served). The serve-identity chain does not rest on the rounded display: the content-hash filename `index-DgiNiCw9.js` in the build log equals the served asset filename, the pre/post served hashes differ (8ba02c64… → dd4f1bd0…), and the served bytes are re-hashed from the live GET. No contradiction; recorded for the audit.
- Docker endpoint rule (the SG-191 correction) obeyed: every docker call ran with DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-202/docker.sock (this unit's RUNTIME_DIRECTORY/RUNTIME_SOCKETS, read from the process environment); the default socket was never read, listed or probed; no prior unit's path used; zero denials on the lane; no sudo, no alternate identity/mount, no host config change.
- PB-3 vacuity (stated loudly): the discriminating evidence is (i) the served bundle/index bytes changed to the merged-tree build (content-hash filename match + marker strings present) and (ii) the new container identity across the recreate; the API-shape GETs are controls (they discriminate schema/row drift and regression of the already-served SG-194/SG-188 repairs, not this frontend delta). Live browser rendering of SG-196's five alert branches and the nav selector is NOT measured (jsdom-only, no screenshots/driver — the same scope limit SG-196 declared); nothing here claims it. The CSS hash being unchanged is a real expected result, not vacuity: neither slice's diff touches CSS.
- Known-host condition unchanged: the backend suite's two environmental rows stay red on this host (pyzbar/libzbar, tesseract absent); host provisioning is Launcher's; no project action (STATE known-host condition). Full suite waived per PG-DP-02; substitute executed (see (c)).

(b) actions

- Read-only pre-state (SG-202_prestate.log): git refs/clean tree, lane identity, docker version/ps/inspect via lane (including mounts), health GET, served bundle hashes, PRE-SERVE API shape capture (PG-EV-08 before), one mode=ro SQLite enumeration (tables, alembic head, all counts), product-diff guard.
- Deployment (SG-202_build.log, SG-202_recreate.log), through the lane socket only:
  `BUILDX_CONFIG=/tmp/opencode/buildx DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-202/docker.sock timeout 600 docker compose build backend` — one issuance, exit 0, 15 s (build log: `tsc && vite build` ran; dist/assets/index-DgiNiCw9.js 324.92 kB; index-DHv-3aM4.css 4.54 kB; manifest list sha256:15a1fe63…; image storagegenie-backend:latest).
  `DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-202/docker.sock timeout 120 docker compose up -d --no-deps backend` — one issuance, exit 0, 1 s; `Container storagegenie-backend-1 Recreated/Starting/Started`.
- Post verification (SG-202_poststate.log, SG-202_health_end.log): identity + mounts re-inspect, six post-recreate health GETs all 200, bundle hashes, DB re-read, SPA routes, CORS preflight, live API-shape probes (PG-EV-08 after), end health.
- Focused tests (SG-202_tests_frontend.log): one vitest invocation, 12 files (the union of the two reports' sets), 162 passed / 0 failed, exit 0, vitest 6.39 s. Production DB sha unchanged after the run (checked, not assumed).
- Commits/push: WORK_HEAD 3857b6a37b7cb4c27186d3a71e0b2f34907c5eb1 (`SG-202 G1+G2: one lane-socket rebuild+recreate serving SG-196+SG-198; evidence logs`, seven files, +414 insertions); pushed `23c59b1..3857b6a automation -> automation` (exit 0). Receipt-paste commit (this report + SG-202_receipt.log) pushed immediately after. Notes-ref receipt pushed `67fbd02..ffcb51f`; remote tip ffcb51f2ed52e861b040c896bf3c949f564f700c read back by ls-remote.
- External / production effects (CO-85): docker image storagegenie-backend rebuilt (new ID sha256:15a1fe632ef87f459e9747afd21fd1fba29a5aff01566144c7ebec97ebe0f20d) and the backend container recreated ONCE on the host — the authorized live serve (owner D-5 approval 2026-10-17, `docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`, executing the standing close-out directive; audits SG-196 98 + SG-198 98, no flag); effect complete and observable as container d868f373b661 / bundle dd4f1bd0…. Branch push + notes-ref push. Production DB read-only: sha256 e6bef157… before and after, identical.
- Durations (UTC box clock; lane start epoch 1792238439 = 12:00:39Z, source systemd ExecMainStartTimestamp for dispatch-storagegenie@SG-202.service; RUN_BUDGET_S=2100 → deadline 1792240539 = 12:35:39Z): orientation + FIRST READ + contract/report/precedent reading 143 s (12:00:39→12:03:02; no command over its bound); prestate capture ~2 s (→12:03:04); supplementary shape capture + one build issuance 12:03:2x→12:03:39 (build 15 s of its 600 s bound); gap ~13 s; one recreate issuance 12:03:52→12:03:53 (1 s of 120 s); post legs 12:04:45→12:04:58 (~13 s; health set inside); focused tests 12:05:08→12:05:15 (7 s wall, vitest 6.39 s); end health 12:05:15; evidence freeze/commit/push + receipt publish/read-back + report drafting ~135 s (→~12:07:30). Elapsed at report writing: epoch 1792238818 = 12:06:58Z → 379 s of 2100 (18.0%) against the packet's ~300 s uncalibrated expectation (STATE: derived from lane precedent SG-193 31 s+2 s / SG-197 27 s+2 s) — 79 s over, stated per G-A9; the overage sits in orientation/reading and evidence/receipt legs, not in the deploy legs (15 s + 1 s). No command hit its bound; no visible timeout finding; build bound 600 s used 15 s; idle kill 900 s never approached.
- Retry count 0. Test-command count 1 (one vitest invocation). Provider-call count 0 (application spend $0.000000; platform spend not exposed — stated, not substituted). Verification reruns 0.
- Highest-impact action: the single lane-socket recreate at 12:03:52Z, which served the two rated frontend slices live for the first time.

(c) verification

Pre-state (read-only; SG-202_prestate.log):

    git: HEAD 23c59b16c78f87ed4abb55aa226745cdfe0d8974 == origin/automation; worktree clean
    f757ebd ancestor of HEAD: yes; faea4d6 ancestor of HEAD: yes; 144190c ancestor of HEAD: yes (reachability form; PG-IC-07)
    lane socket: /run/dispatch-storagegenie-SG-202/docker.sock mode=srw-rw---T uid=andrei gid=100987; RUNTIME_SOCKETS=docker.sock
    docker version via lane: Client 29.6.2 / Server 29.6.2 (API 1.55) exit 0 — capability granted, zero denial; Docker Compose v5.3.1
    container pre: Id=a77e3f2ff0dd… Created=2026-10-16T19:41:19.974177688Z RestartCount=0 Image=sha256:e3b7c0aa… State=running (healthy) StartedAt=2026-10-16T19:41:21.658871595Z
    mounts: volume .../storagegenie_storage_data/_data=>/data/storage, bind /home/andrei/StorageGenie/data/db=>/data/db
    health pre [200]: {"status":"ok","db":"ok","storage":"ok"}
    served pre: index.html 5ce95f29… (944 B); assets/index-_9IDZb0V.js 8ba02c64… (325053 B); assets/index-DHv-3aM4.css e1e5ff63… (4541 B) — the EXPECTED SG-197 serve
    pre-serve API shape (PG-EV-08 before): GET /v1/households 200 sha256 69215837…; GET /v1/jobs?household_id=… page 1 200 sha256 045a80a7…;
                GET /v1/jobs|/v1/review-tasks?household_id=…&cursor=not-a-cursor → 422 {"detail":"malformed cursor"} body sha256 d117e66a…; bare (no household_id) → 422 missing-param (shape, I1)
    db (mode=ro): 28 tables enumerated on target; alembic_version ['20260924_sg114_relation']; db sha256 e6bef157…
                 counts: review_task 8, candidate 10, asset 7, evidence 18, job 11, provider_call 29, audit_event 91, job_step 72, assertion 37, observation 20,
                 household 1, user 2, asset_evidence 14, idempotency_key 11, enrich_snapshot 4, guardrail_event 2, … — all identical to SG-197 post (no owner activity)

Product-diff guard (merged-vs-served; pre-deployment):

    $ git log --oneline f757ebd..HEAD -- backend frontend
      144190c SG-198 G1: AppHeader onto household context, ReviewPage onto shared useReviewTasks
      faea4d6 SG-196 G1+G2+G3: shared household context (one fetch), nav selector+household alert, Inbox open-task badge, catalog facets/saved-search alerts
      → exactly the two EXPECTED commits, no third
    $ git diff --stat f757ebd..HEAD -- backend frontend   → 24 files changed, 622 insertions(+), 170 deletions(-) (frontend only)
    $ git diff --name-only f757ebd..HEAD -- backend frontend → 12 product files (App.tsx, AppHeader.tsx, HouseholdContext.tsx, useAssets.ts,
      routes/{Analytics,Capture,Catalog,Chat,Expiry,Inbox,Planning,Review}Page.tsx) + 12 test files (App.household-nav.test.tsx + 11 edited modules)
      → no product change outside the two sets
    $ git diff --name-only f757ebd..HEAD -- backend/app/models backend/alembic → (empty; no migration)
    $ changed top-level paths since f757ebd: docs 96, frontend 24, AGENTS.md 1, STATE.md 1 (product = frontend only; no backend hunks at all)

Deployment (lane socket only; one issuance each):

    $ BUILDX_CONFIG=/tmp/opencode/buildx DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-202/docker.sock timeout 600 docker compose build backend
      #13 [frontend-build 6/6] RUN npm run build → tsc && vite build; dist/assets/index-DgiNiCw9.js 324.92 kB, index-DHv-3aM4.css 4.54 kB
      #22 exporting manifest list sha256:15a1fe63…; naming to storagegenie-backend:latest
      build_exit=0  elapsed_s=15
    $ DOCKER_HOST=unix:///run/dispatch-storagegenie-SG-202/docker.sock timeout 120 docker compose up -d --no-deps backend
      Container storagegenie-backend-1 Recreated / Starting / Started
      up_exit=0  elapsed_s=1
    container post: Id=d868f373b661e51247db757ca755bd9dad5906606233a76807860141a0ef780d Created=2026-10-17T12:03:52.700720908Z
                    RestartCount=0 Image=sha256:15a1fe63… State=running StartedAt=2026-10-17T12:03:53.419536516Z Health=healthy

Health (CO-92): start 12:03:02Z and end 12:05:15Z identical {"status":"ok","db":"ok","storage":"ok"} [200] — HEALTH: unchanged, OK. Six post-recreate GETs 12:04:45→12:04:56Z all 200 (standing precedent, not a reliability rate).

Post-recreate served bytes / schema / counts (SG-202_poststate.log):

    served post: index.html e3eb67360d145260465ca379bb325bf5868bf4923692f274902caf11c2d44280 (944 B) != 5ce95f29… : CHANGED
                 assets/index-DgiNiCw9.js dd4f1bd0876de5dfba0b0bc351342a4e5ca3df35f8b5f4752e0ab31845579f53 (325039 B) != 8ba02c64… : CHANGED as required
                 assets/index-DHv-3aM4.css e1e5ff63… (4541 B) == pre : UNCHANGED (expected; no CSS in either slice's diff)
    serve identity chain: build log dist/assets/index-DgiNiCw9.js == the served asset filename (content-hash named); served bytes re-hashed from the live GET (325039; vite prints 324.92 kB — I2, known display offset)
    db post (mode=ro): sha256 e6bef157… — IDENTICAL to pre (no migration, no slice row change; all 28 table counts identical); also identical after the test run
    SG-196 content in the served bundle bytes: inbox-open-count ×1; "Could not load households" ×3; "Could not load catalog facets" ×1; "Could not load saved searches" ×1; "Select household" ×3

Live route/serve verification (SG-202_poststate.log):

    SPA routes through the new server: /inbox /catalog /analytics /planning /capture /review each HTTP 200 text/html bytes=944,
      sha256 == new index e3eb6736… (SPA fallback live; previous serve was 5ce95f29…)
    CORS preflight: OPTIONS /v1/review-tasks Origin http://localhost:5173, Access-Control-Request-Method GET → HTTP 200,
      access-control-allow-origin: http://localhost:5173, allow-methods GET,POST,PUT,PATCH,DELETE,OPTIONS, allow-credentials true
    API-shape controls post (PG-EV-08 after; unchanged from pre): /v1/households sha 69215837…; jobs page-1 sha 045a80a7…;
      malformed-cursor 422 body sha d117e66a… both on /v1/jobs and /v1/review-tasks (SG-194 live repair + SG-188 control intact)

Focused test set (enumerated from the two reports on target; actual set == expectation; PB-7 not bound — no widening):

    frontend (union of the two reports' sets; 12 files, 162 passed / 0 failed, exit 0, vitest 6.39 s):
      SG-196's 11-file derived set (SG-196_focused_candidate.log header): App.household-nav.test.tsx,
        routes/{Inbox,Chat,Planning,Analytics,Expiry}Page.test.tsx, routes/query-error-alerts.test.tsx, routes/theme-adoption.test.tsx,
        components/shell/shell.test.tsx, components/shell/import-modal.test.tsx, components/catalog/catalog.test.tsx
      ∪ SG-198's authoritative focused 6-file set; only non-subset member ReviewPage.test.tsx (8 tests) — the SG-198 addition the packet expected
    substitute executed (PG-DP-02 waiver; full suite waived): this targeted run + post-recreate read-only identity/health/schema/counts/pages/preflight above.
    backend: no backend file changed since the last served commit (f757ebd..HEAD backend = empty), so no backend focused set is owed by this rider;
    SG-194's live cursor repair was re-proven by the live 422 control instead (above).

Committed evidence blob sha256 (work commit 3857b6a, bytes as pushed):

    70b42052cbd1aba49a588182a772099b61cc8f8eec8b4ad15c76c864cd066541  SG-202_prestate.log
    56d46f4df89fee4b8dbfa65233da0e50b3c142120280efb9a0cd93df0ec7c0dc  SG-202_build.log
    b2b292a68685b0026fdf31a7819d0808348a32d364e6c406e81a7e92ac4052a8  SG-202_recreate.log
    92f2e72c6f826941625d83f3998886e54fffbf80b3fd7708a37430fff2efc460  SG-202_poststate.log
    00e703cc5dd0fa06a3b3f2dd8c8d06f8db99767b464376332ad535c2bd5bfe83  SG-202_tests_frontend.log
    3defbe86cfff82a168bac91c30f9f74cdcb3ec87cb3059f62b97defc0fefcd30  SG-202_health_end.log
    ac128d238d8a9d15ee2dbbc213f266a918321e0ddd991d19f8101ac81bfabb6c  SG-202_worklog.log
    (paste commit adds this report and SG-202_receipt.log e3f0b405….)

acceptance

- A1 MET: exactly one rebuild + one recreate THROUGH THE LANE SOCKET (commands + exits above; zero denials; default socket never touched); direct new running-instance proof (container d868f373b661, Created 2026-10-17T12:03:52.700720908Z, image 15a1fe63…, RestartCount 0, healthy); health green start/end + six GETs; explicit deltas — application: index+bundle changed (dd4f1bd0…, == build-log asset); schema: none (alembic head unchanged); counts: none (all 28 identical); DB sha e6bef157… identical; served bundle recorded and DIFFERENT from 8ba02c64… (no byte-identical claim needed).
- A2 MET: actual base/hash frozen (requested `automation` → 23c59b16… == origin/automation; faea4d6/144190c ancestors); merged-vs-served product diff = exactly the two expected sets (24 files, +622/−170, frontend-only, no migration, no third commit, nothing outside); still-open items expressly unchanged — SG-199 REMAINING (density numbers, auth-live, live-container rendering, zoom/touch/dark) stands untouched and is D-6's next slice, ISS-4 (runner report_unreadable misfire, 4 instances) carried as the known runner-observation shape with receipt-based failure condition held; work diff only SG-202 namespace (seven logs at work commit; report + receipt log at paste).
- A3 MET: first token SG-202; command logs are the eight committed SG-202_* artifacts; elapsed per leg with source and total vs the observed lane bound (379 s of 2100 = 18.0%; deadline from RUN_BUDGET_S, start from systemd ExecMainStartTimestamp; overage vs the ~300 s uncalibrated expectation stated per G-A9); all constraints answered below; FIRST READ / DURING EXECUTION / REMAINING dispositioned at the end.
- A4 MET: notes-ref receipt on refs/notes/storagegenie-coder-reports published (`67fbd02..ffcb51f`, exit 0) and mapped-fetch/read-back verified (transcript SG-202_receipt.log; remote tip ffcb51f2ed52e861b040c896bf3c949f564f700c read back by ls-remote); first line `Dispatch-ID: SG-202 | Report: docs/worklogs/SG-202_report.md | Work-HEAD: 3857b6a37b7cb4c27186d3a71e0b2f34907c5eb1`; Work-HEAD recorded; branch/report push complete. Bound lane receipt used, never the retired finalizer.

constraints answered

- Scope respected: work commit = docs/worklogs/SG-202_* only (7 logs, +414); paste commit adds report + receipt log; zero product/config/schema/migration/test edits (the deployed product tree is the pre-existing merged SG-196+SG-198 tree).
- Production DB: read-only (mode=ro enumerations + sha reads); no INSERT/UPDATE/DELETE, no manual resolving, no imports, no evidence-store mutation; DB sha identical pre/post deployment and post tests; no migration, no slice-caused row change; no owner-activity delta appeared (I report none; nothing hidden).
- Restart discipline: exactly one build issuance and one recreate issuance; second issuance would have been STOP; none attempted. No host config change, no sudo, no alternate identity/mount.
- No browser interaction causing writes; no paid calls; provider spend $0.000000 (application); no secret or credential in any log or committed artifact; no interactive prompt, no polling loop; every command under its stated bound (reads/verification 120 s, build 600 s); no timeout finding; idle kill 900 s never approached.
- Full suite waived per PG-DP-02 with the substitute executed (targeted 12-file run + post-recreate read-only identity/health/schema/counts/pages/preflight); waste cut none owed (SG-199 `slowest_waste = none`; the removed `5s precommit-focused` gate was not re-introduced); runtime-vs-lane budget reported in seconds with sources (PG-PR-06), never guessed.
- PB-2 denial path: no privileged operation attempted; no denial occurred anywhere (lane granted version/inspect/compose build/recreate); stop path never reached. PB-6: no design call needed escalation; nothing decided by asking.
- Guards invoked all satisfied: PG-EV-02/03 (no stop condition arose; no disclosure-substitution), PG-EV-08 (pre+post bundle/API capture committed), PG-IC-01 (only build+recreate+tests+read-only GETs/enumeration ran), PG-IC-07 (reachability, never HEAD equality), PG-DP-01/02 (waiver + substitute), PG-PR-03/04/06/10 (single recreate through lane; PR-06 seconds).

UNCLEAR
FIRST READ:
- AGENTS.md's `.rules-cache/` path is absent in this workdir (gitignored by design, D138 "git, never disk"); used /home/andrei/storagegenie-contract/ (complete 0.50.0 copy, RULES.md hash verified against RULES.sha256). rules_check.sh G-L1/G-L5/G-L7 UNCHECKED lines are environment (cache not tag-checked-out / gh auth), not slice scope. Disposition: recorded, block-free; same as SG-190/194/195/196/199. No host tag/auth/config touched — the known exit-3 shape is not a repair license.
- Packet premises all verified against the tree (PB-1): pre-state container/image/bundle exactly as EXPECTED; product diff exactly the two named commits; no divergence to explain this time.
DURING EXECUTION:
- The only correction: the first API-shape probes omitted the required household_id (the 422s recorded are the current shape itself); the supplementary capture supplies it (I1). No other judgment calls; the deploy legs executed to plan first try.
REMAINING (named, not silently done):
- SG-199 REMAINING unchanged and carried: density numbers (now D-6's proposal slice), auth-live coverage, live-container rendering, zoom/touch/dark measurement.
- ISS-4 runner `report_unreadable` misfire (4th instance at SG-199): known runner-observation shape with receipt-based failure condition held; filed Launcher #84; not a slice fault; no re-trigger.
- Live browser rendering of SG-196's selector/badge/alert branches is jsdom-only proof (structural evidence in served bytes); screenshots/driver stay out of scope for this rider.
- SG-196's report-vs-audit delta line (+556 vs +565, 9 lines) remains a docs-only records discrepancy, out of this rider's scope.
- Backend full suite still carries the two known environmental rows on this host (pyzbar/libzbar/tesseract absent; Launcher provisioning), unchanged.
