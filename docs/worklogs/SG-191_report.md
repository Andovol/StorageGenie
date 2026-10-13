SG-191 — Serving rider (R1 repair live): STOPPED before any build — denied capability read on the default Docker endpoint

RESULT: BLOCKED (CO-48 class 3) — zero rebuilds, zero recreates, zero production effect. The merged R1 repair stays UNSERVED; the pre-repair bundle 1b4680a0… is still served. STOP invoked per CODER §3 / PB-2 / PG-PR-03 as bound by the SG-175 audit ("Optional read denial is not an exception to PB-2") and SG-179 ("whole-slice STOP on ANY new privileged denial, including an optional read"). No route-around: no lane-socket Docker call after the denial, no sudo, no alternate identity or mount, no host config change. Publication did NOT fail: branch and notes-ref pushes succeeded (CO-50).

model opencode-go/deepseek-v4.1-flash · effort max — read from /proc/1845148/cmdline (`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant max`), never from a system-prompt identity line. Served-model response metadata not available; no substitute value claimed. `max` is catalogue-valid but uncalibrated vs D120/D15-high (G-A9, stated).
Work dir /home/andrei/StorageGenie · branch `automation` · remote git@github.com:Andovol/StorageGenie.git. BASE ref requested `automation` → resolved commit 49947c2cba671ad3f72b90307a658dfb5a562afa (== local HEAD == origin/automation at start; worktree clean at start). WORK_HEAD: 24a9f93df1481a31a4a776745120518ae2962209 (the BLOCKED evidence commit: four frozen logs + the worklog). This report lands in the receipt-paste commit, so it does not carry its own hash (CO-55b).
Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version: 0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than assumed its contents."
Source readback: /home/andrei/storagegenie-contract/VERSION=0.47.0; RULES.md sha256 49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed == RULES.sha256 (installed payload). rules_check.sh run from the host contract path exits 3 (G-L1 cache-not-at-checkout-tag; L5/L7 gh-unauthenticated) — the SG-184/SG-174/SG-173-documented host shape; no host tag/auth/config touched or repaired; no version delta vs the packet's expected 0.47.0.

(a) issues / deviations / surprises

- F-SG191-1 (blocking; self-inflicted trigger + packet defect — stated loudly). The packet orders "Read grant/capability without attempting privileged writes as a probe", but does not name the lane endpoint and omits the SG-179 exclusion of the known-denied default socket read. My capability read ran against the default endpoint first — `docker ps`, `docker images`, `docker inspect storagegenie-backend-1` — each returning `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` (exit 1; /var/run/docker.sock mode=0 root:root on this host). A denied privileged operation is a whole-slice STOP with no optional-read exception (PB-2; SG-175 audit, owed to the ISS-SG175-A1 flag; SG-179 bound reading). I stopped: no lane-socket Docker call was issued after the denial, no sudo/alternate identity/mount, no second probe. The denial is the reason no build was issued — the granted lane below was never used. Recommended packet fix (small, mechanical): name `DOCKER_HOST=unix:///run/dispatch-storagegenie-<ID>/docker.sock` explicitly (SG-172's documented lane, F-SG172-5) and re-include SG-179's exclusion sentence.
- F-SG191-2 (premise confirmed — PB-1; no impact). The granted lane IS present, read without a privileged call: /run/dispatch-storagegenie-SG-191/docker.sock mode=1660 uid=1000(andrei) gid=100987, with RUNTIME_DIRECTORY=/run/dispatch-storagegenie-SG-191 and RUNTIME_SOCKETS=docker.sock in the process environment; SG-174-I5 (rated 97, no flag) exercised the same mechanism (`docker version` via this socket answered Server 29.6.2). Its operability was NOT re-tested after the stop (SG-175 lesson: no fresh privileged probing post-denial); container/image identity is therefore UNVERIFIED this slice, as in SG-175.
- F-SG191-3 (premise confirmed — PB-1). The merged-vs-served product diff is EXACTLY the waived R1 set plus its tests: 7 files, +242/-6 — backend/app/api/v1/candidates.py, backend/app/services/candidates.py, backend/tests/test_candidate_read.py, frontend/src/components/CandidateCard.tsx, frontend/src/components/CandidateCard.test.tsx, frontend/src/routes/ReviewPage.tsx, frontend/src/routes/ReviewPage.test.tsx. No product change outside the set; backend/app/models and backend/alembic diffs empty (no migration); the served-close commit 3454e1c adds no product delta vs the deployed product base 3ae5541. The A2 product-diff guard would have passed; the deployment was stopped by the denial, not by the diff. 0b42e7d (R1) is an ancestor of HEAD and NOT an ancestor of the served close 3454e1c.
- F-SG191-4 (baseline re-confirmed, read-only). Served bundle still pre-repair: index.html sha256 2f035bec…, assets/index-CYyuxefG.js sha256 1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d (322255 B) == the SG-175/SG-184 recorded pre-repair served bundle, assets/index-DO0gjGV6.css sha256 37b25dbd… (3911 B). Health {"status":"ok","db":"ok","storage":"ok"} [200]. alembic_version 20260924_sg114_relation (head), unchanged. 28/28 tables enumerated on target with counts aligning to the SG-174/SG-184 records (review_task 8 all resolved, candidate 10, asset 7, evidence 18, job 11, provider_call 29, audit_event 91, job_step 72, assertion 37, observation 20). prod DB sha256 e6bef157… (mode=ro; end re-read identical).
- SG-191-I1 (context): a different project's dispatch (LNR-153, launcher-desk) was in flight on the host during this slice — permitted (concurrency across projects); no interaction, no shared branch.

INTENT: not applicable — no behaviour change was performed; the slice stopped before any product action.
TWINS: not applicable — no defect fixed, no predicate replaced.

(b) actions

- Read-only only: git inspection; health and served-bundle GETs; one mode=ro SQLite read (28 tables enumerated + counts + db hash); socket/environment metadata reads. ZERO builds, ZERO recreates, ZERO production writes/migrations, zero INSERT/UPDATE/DELETE, no manual resolving, no imports, no evidence-store mutation, zero provider calls, no browser interaction, no paid call, no host change, no sudo.
- Commits/push: WORK_HEAD 24a9f93df1481a31a4a776745120518ae2962209 (`BLOCKED: …` first line; five files); pushed `49947c2..24a9f93  automation -> automation` (exit 0, origin/automation == 24a9f93). Receipt-paste commit (this report) pushed immediately after this file is committed. Notes ref pushed `62b9f51..66a5e08`.
- External / production effects: branch push + notes-ref push only; NOTHING on the running service; production DB read-only.
- Durations (UTC box clock, CO-79; lane start epoch 1791913989 = 17:53:09Z, source ps lstart PID 1845148 + /proc/stat btime 1785224168 + starttime 668982187 ticks @ CLK_TCK=100): orientation + contract/receipt-method reconstruction ≈ 350 s (17:53:09→17:58:59); stop decision + pre-state capture + evidence freeze + receipt publishing ≈ 190 s (17:58:59→18:02:09). End and total as of report writing: epoch 1791914529 = 18:02:09Z → 540 s total of RUN_BUDGET_S=2100 (25.7%; source: process environ; packet PG-PR-06). Lane stop window: ends_by ≈ 1791916089 = 18:28:09Z. No command hit its bound (longest leg is reading, not a bounded command); no visible timeout finding; nothing killed, no hang; IDLE_KILL_S=900 default never approached.
- Retry count: 0 (one STOP, no second attempt on anything). Test-command count: 0 (full suite waived per PG-DP-02; the packet's substitute verification is VOID because the recreate never happened — stated unmet, not passed). Provider-call count: 0. Health delta: none.
- Highest-impact action: the STOP itself — declining to route around the denied default endpoint (in particular, declining to "just use the lane socket" after the denial). Highest-impact non-action: no rebuild/recreate issued.

(c) verification

Pre-state (read-only, before any deployment attempt; SG-191_prestate.log / SG-191_health_served.log / SG-191_db_readonly.log / SG-191_diff.log):

    git: HEAD 49947c2cba671ad3f72b90307a658dfb5a562afa == origin/automation; worktree clean at start
    0b42e7d ancestor of HEAD: yes; ancestor of served close 3454e1c: no
    health [200]: {"status":"ok","db":"ok","storage":"ok"}
    served: index.html 2f035becd05b63e226af82e2e8fe60c8f3b5effb9f37e49dd95a2265c4da0d55
            assets/index-CYyuxefG.js 1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d (322255 B)
            assets/index-DO0gjGV6.css 37b25dbdd4b0ecfdedb8255bc7f8af286726334e95a1a3a9e85b9ba381b3d57c (3911 B)
    db (mode=ro): 28 tables enumerated on target; alembic_version 20260924_sg114_relation; counts incl. review_task 8,
            candidate 10, asset 7, evidence 18, job 11, provider_call 29, audit_event 91, job_step 72; db sha256
            e6bef157440fb8b4a3262577362b071dcae07507ea9a7e04a614e11be28ee5bd (end re-read identical)

Capability-read denial (default endpoint; session transcript, quoted verbatim as captured):

    $ docker ps --format 'table ...'
    permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
    EXIT=1
    $ docker images --format 'table ...'
    permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
    $ docker inspect storagegenie-backend-1
    []
    permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
    (the single [] line is quoted as captured; no container data was obtained — every call failed to reach the API)

Grant presence (read, no privileged call): /var/run/docker.sock mode=0 uid=0 gid=0 (unusable by design; not the lane) · /run/dispatch-storagegenie-SG-191/docker.sock mode=1660 uid=1000(andrei) gid=100987 · RUNTIME_SOCKETS=docker.sock (SG-172/174 lane mechanism). Operability untested after the STOP.

Product-diff guard (SG-191_diff.log):

    $ git diff --stat 3ae5541..HEAD -- backend frontend
     backend/app/api/v1/candidates.py               |   4 +-
     backend/app/services/candidates.py             |  20 ++++
     backend/tests/test_candidate_read.py           | 152 +++++++++++++++++++++++++
     frontend/src/components/CandidateCard.test.tsx |  17 +++
     frontend/src/components/CandidateCard.tsx      |   2 +-
     frontend/src/routes/ReviewPage.test.tsx        |  49 ++++++++
     frontend/src/routes/ReviewPage.tsx             |   4 +-
     7 files changed, 242 insertions(+), 6 deletions(-)
    $ git diff --name-only 3ae5541..HEAD -- backend frontend   → exactly the 7 files above
    $ git diff --name-only 3ae5541..HEAD -- backend/app/models backend/alembic   → (empty)
    $ git diff --name-only 3ae5541..3454e1c -- backend frontend                  → (empty)

Work-diff scope (this slice; five harness logs + worklog + this report, all docs/worklogs/SG-191*):

    $ git diff --name-only 49947c2..24a9f93
    docs/worklogs/SG-191_db_readonly.log
    docs/worklogs/SG-191_diff.log
    docs/worklogs/SG-191_health_served.log
    docs/worklogs/SG-191_prestate.log
    docs/worklogs/SG-191_worklog.log
    (+ the receipt-paste commit adds only docs/worklogs/SG-191_report.md)

Committed blob sha256 (bytes as pushed on WORK_HEAD 24a9f93):
    f51a004f7d2eff6a25d0a9257013fa23e6b43268f029a7541702b9185cff38fd  SG-191_prestate.log
    0f495eb5cda9b386aa57176e33d9567c94ad053a49a3f2ca6636c7e108c9c3cf  SG-191_health_served.log
    66db353998b75a7ab4255ec1d7ffd5b2f715d8eb5a4e62ee63dfa019c3a6f60d  SG-191_db_readonly.log
    6c132bcdf4ce046c817a641cc336ea2fce4d2336ba6f83030bad8163e1fbc5ae  SG-191_diff.log
    54de6580a08d9266cd31299df0457200f7125cfde617a4b315ca858f70f81f8d  SG-191_worklog.log

Health (CO-92): start and end identical {"status":"ok","db":"ok","storage":"ok"} [200] — HEALTH: unchanged, OK.

Receipt (CO-60/CO-97; bound lane notes-ref; mapped refspec — a default fetch never carries notes; transcript executed):

    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports
    local tip before add: 62b9f51bbeb17a54e7ff142bc9aaba0178d9b0c0
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-191 | Report: docs/worklogs/SG-191_report.md | Work-HEAD: 24a9f93df1481a31a4a776745120518ae2962209" 24a9f93df1481a31a4a776745120518ae2962209
    add_exit=0
    $ git push origin refs/notes/storagegenie-coder-reports
       62b9f51..66a5e08  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
    notes_push_exit=0
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg191-fetched
       62b9f51..66a5e08  refs/notes/storagegenie-coder-reports -> refs/notes/sg191-fetched
    $ git notes --ref=refs/notes/sg191-fetched show 24a9f93df1481a31a4a776745120518ae2962209
    Dispatch-ID: SG-191 | Report: docs/worklogs/SG-191_report.md | Work-HEAD: 24a9f93df1481a31a4a776745120518ae2962209
    show_exit=0

The same note (Work-HEAD bound to the published head) is re-published on the receipt-paste commit after this file is committed — SG-140a/SG-092 dual annotation; a post-report step by construction (CO-55b/CO-79), its own show output cannot appear inside this file. The retired finalizer was not used; no other publisher was sought.

acceptance
- A1 NOT MET (stated, not passed): no rebuild and no recreate were issued (STOP before deployment); no new running instance exists to prove; served bundle remains 1b4680a0… (unchanged — consistent with no build, and contrary to the packet's changed-bundle expectation for a successful ride); health green; application/schema/count deltas zero because the deployment never happened. The six-health-GET and pages/preflight legs were not reached.
- A2 PARTIALLY MET: base ref requested/resolved echoed; product diff merged-vs-served checked = only the waived R1 set + its tests (actual diff reported); work diff only docs/worklogs/SG-191*; the still-unrepaired stories (bare-Resolve, active-unclassified visibility, SG-176/177/178 scope) were NOT touched and are unchanged by construction — nothing was deployed.
- A3 MET: command logs (four files, hashes above) + this report; elapsed per leg and total vs lane bound with seconds and sources; all constraints answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned.
- A4 MET: notes-ref receipt on refs/notes/storagegenie-coder-reports published and mapped-fetch/read-back verified (transcript above for WORK_HEAD; paste-commit note per the dual-annotation convention, post-report); first line `Dispatch-ID: SG-191 | Report: docs/worklogs/SG-191_report.md`; Work-HEAD recorded; branch and report pushes complete; bound lane receipt used, never the retired finalizer.

constraints — every stated constraint answered
Scope docs/worklogs/SG-191* only — answered (work diff names). No product/config/schema/migration/test edits — answered (zero product diff; the only non-SG-191 path touched is none). No production INSERT/UPDATE/DELETE, manual resolving, imports, evidence-store mutation — answered (one mode=ro read; health/GETs only). One rebuild + one recreate only; second issuance STOP — answered (ZERO issued; the first was never issued because the STOP preceded it; a second cannot occur). Ordinary reads bounded 120 s / build 600 s; visible timeout finding; never approach idle kill 900 s — answered (no bounded command exceeded its bound; no timeout finding; not approached). No interactive prompt or polling loop — answered. Full suite waived per PG-DP-02; substitute named — answered (the substitute verification is VOID without the recreate; SG-184's executed re-proof — failpre 4F/6P, passpost 10P, UI 18P, probe PROBE_OK — remains the standing verification of the merged bytes, cited, not re-run). No new code is required to pass a new behaviour test — answered (no code shipped). Application provider spend prohibited; platform spend not exposed — answered ($0.000000, 0 calls). Runtime-vs-lane budget with seconds and source — answered above. PG-PR-03 denial is STOP, never sudo/another identity/another mount — answered (stopped; none used). No host config changes — answered. PG-PR-04 (how the code becomes live) — answered (the packet's build+recreate lane; not executed due to the STOP). PG-PR-06 — answered (RUN_BUDGET_S=2100, seconds from process environ/stamps). PG-PR-10 — answered (no state created; production SQLite read-only; D13/D14 cited as the authorisation basis; no write). PG-EV-02/03, PG-IC-01/07, PG-DP-01/02 — answered (deployment/verification legs not reached, stated as unmet not passed; UTC clock used throughout; no secret in any committed artifact — health bodies carry status strings only; no app write; no client-set cursor claims; full-suite waiver handled).

UNCLEAR
- FIRST READ: the packet's lane sentence names only `BUILDX_CONFIG=/tmp/opencode/buildx docker compose build backend` and refers to "the granted lane" without the endpoint. Read SG-172's report (F-SG172-5) + SG-174-I5 to identify the per-unit runtime socket as the grant and the default socket as root-only. My capability read nonetheless ran against the default endpoint first; that denial is the trigger of this STOP (F-SG191-1), disclosed as self-inflicted and avoidable, with the packet's omission also named.
- DURING EXECUTION: after the denial, no interpretation permitted continuing (PB-2 absolute; SG-175 audit binding; SG-179 whole-slice STOP). The one judgement call was whether the separately-present lane grant removes the stop; I took the bound reading and stopped rather than route around. Container/image identity stays UNVERIFIED (SG-175 precedent) and the lane's operability is untested this slice.
- REMAINING: (1) architect fix + re-dispatch — name DOCKER_HOST (lane socket) explicitly in the packet and repeat SG-179's exclusion; the mission itself is unchanged and mechanical; (2) R1 repair stays UNSERVED and CLOSE_BLOCKED remains until a verified live serve; (3) SG-176/177/178 and the probe-declared STILL-UNREPAIRED items remain open and untouched; (4) the report-commit receipt note is post-report by construction (CO-55b).

State of the world: product tree UNCHANGED at HEAD 49947c2 + two docs-only SG-191 commits (24a9f93 and the receipt-paste commit); running service unchanged — pre-repair bundle 1b4680a0… still served, health green, zero recreates; production writes NONE; SG-175 repair still UNSERVED; D13 waiver acknowledged, unused.
