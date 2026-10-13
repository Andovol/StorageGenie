SG-175 — Live blocked-task projection and consistent Review acceptance (UNSERVED)

model opencode-go/deepseek-v4.1-flash · effort max — read from /proc/1154838/cmdline
(`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash
--variant max`; wrapper `bash /usr/local/lib/dispatch/run-coder SG-175`), never from a
system-prompt identity line. Work dir /home/andrei/StorageGenie · remote
git@github.com:Andovol/StorageGenie.git · BASE requested ref `automation` → resolved commit
`803cf522723158c65f9c4a6ba1ac3679da57f53a` (local HEAD == origin/automation at start; worktree
clean) · WORK_HEAD `0b42e7d62dd4e5bc379950c0175d4284176d3a1e`.

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim):
"**Contract version: 0.46.0** — **echo this line verbatim in your receipt.** It is the only
proof that you read this file rather than assumed its contents." Source readback:
/home/andrei/storagegenie-contract/VERSION=0.46.0; RULES.md sha256
487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef == RULES.sha256 (installed
payload). `rules_check.sh` run from the host contract path exits 3 (G-L1 cache-not-at-tag +
gh-unauthenticated) — inherited SG-172/173/174 shape; the repo `.rules-cache/` is absent, so the
host path is the current source; no host rule or cache was changed.

RESULT: CHANGED. G1/G2/G3 implemented; W1 `0b42e7d` (product+tests+probe), W2 `2b8c962`
(evidence logs), this report commit follows and carries `SG-175_query_delta.log`. Code is
UNSERVED: no rebuild/restart/deploy. Production writes: NONE; production DB sha256
`e6bef157440fb8b4a3262577362b071dcae07507ea9a7e04a614e11be28ee5bd` before == after. Live surface
unchanged (served bundle `1b4680a0…` == SG-173 deployed record).

(a) Issues / deviations / surprises

- Live image re-observation DENIED in this lane: /var/run/docker.sock is mode `s---------`
  root:root (user andrei is in group docker 988 but the socket itself is unreadable); `docker ps`
  returned `permission denied`. No sudo, alternate socket/identity/mount, or any route-around was
  used (PB-2 / PG-PR-03). Judgement: the denial hit an OPTIONAL listing, not a packet-required
  operation — the packet's mandated reproduction is "GETs only" and explicitly says image
  d5da5684 is prior SG-174 evidence, not a freshness gate — so the whole slice was not stopped on
  it. If PB-2 is meant as whole-slice STOP for any denied socket read, this is the line to
  re-judge. Capability readback: container/image identity is NOT re-observable by the Coder in
  this lane; expected image inherited: d5da5684 (SG-174 evidence). No mutation was used as a
  probe.
- Probe first run FAILED for setup, not criteria: run from the repo root, pydantic
  `env_file: ".env"` (CWD-relative) loaded the repo-root `.env` and selected a provider that
  needs the original evidence file → ANALYZING_WITH_AI FAILED, job FAILED, no candidate built.
  Corrected run from `backend/` (never reads the repo-root .env; SG-173's actual working shape)
  plus in-process `sg_provider_id="fake"` and provider keys nulled; clean PROBE_OK. The failed
  attempt is disclosed here and committed nowhere.
- Interpreter verified on execution: the probe asserts `sys.executable` resolves to
  /home/andrei/StorageGenie/backend/venv/bin/python AND `sys.prefix` == backend/venv before any
  write (A4). SG-173's root-venv docstring path was not used.
- Probe controls intentionally print a `CHECK_FAILED` line when they reject; each is immediately
  paired with `[CTL] expected rejection observed: …` and the T3 summary. 52 checks passed;
  PROBE_OK is printed only after the whole body, and a failed check raises before the footer
  (exit 1).
- failpre used an isolated worktree `/tmp/sg175-base` at the base commit (CO-20c): base product
  code, only the three candidate test files copied in; no in-place base checkout; no `.env`
  copied (CO-100).
- `.rules-cache` absent in the workspace (AGENTS Loading resolves to the host path); host
  cache/tag/gh-auth limitations are inherited SG-174 observations, not authority to change host
  rules.
- Baseline benchmark reproduces the exact divergence: pre-change GET returned
  `review_task_ids=[]` while one live open task existed (open_only=false); candidate returns the
  open id (open_only=true). Runtime delta +1.504 ms/GET (4.144 → 5.648 ms over 300 real-route
  GETs, 4-row fixture) = one added indexed SELECT per GET (`SG-175_query_delta.log`).

(b) Actions

- Changed paths (scope ceiling only): `backend/app/api/v1/candidates.py` (get_candidate now
  serves `candidates.open_review_task_ids(db, candidate)`); `backend/app/services/candidates.py`
  (+`open_review_task_ids` helper; predicate subject_ref + household_id + status=open, ordered
  created_at,id — same rule as the decision gate); `frontend/src/components/CandidateCard.tsx`
  (dedup alert keeps only its advisory; the SG-171 standalone reason is the single blocked
  sentence); `frontend/src/routes/ReviewPage.tsx` (shortcut A and R skip while
  `decision.isPending`); `backend/tests/test_candidate_read.py` (+6 tests);
  `frontend/src/components/CandidateCard.test.tsx` (+2), `frontend/src/routes/ReviewPage.test.tsx`
  (+3); `docs/worklogs/SG-175_probe.py` (new).
- Commits/push: `0b42e7d` (product+tests+probe) → `2b8c962` (evidence logs) → this report commit
  (+ query-delta log); automation pushed `803cf52..2b8c962` before this file, report commit
  pushed after; `Dispatch-ID: SG-175` trailer on all.
- External effects: none. Provider calls: 0 (probe forced fake + keys nulled; tests offline).
  Production effects: none (GETs + read-only sqlite + hash). Health delta: none.
- Consumers re-read and dispositioned: frontend `CandidateCard.tsx:48` and `ReviewPage.tsx:48`
  are the only review_task_ids readers and now consume the live response; no other component
  imports CandidateCard. Backend snapshot readers left unchanged (outside ceiling):
  `api/v1/jobs.py:158` `_candidate_list_item` (job-candidate list; no frontend caller),
  `enrich.py:276` (literal `[]`), `services/candidates.py:792` (job-step historical output).
  Proposal writers (`dedup.py:199/216/232/241`, `services/candidates.py:722/771/1154`) untouched;
  historical snapshots not rewritten.
- Durations (UTC clock, measured at commit time): session start 12:39:10Z; W1 committed
  12:49:06Z; W2 12:49:42Z; report commit 12:52:41Z; elapsed at report commit 811 s of lane
  `RUN_BUDGET_S=2100` (stop window 13:14:10Z) — inside bound. No command hit
  its bound and none hung (reads <1 s; tests 4.3 s and 2.1 s; probe ≈20 s; build ≈7 s including
  tsc). Test-command count: backend 3 runs (implementation, failpre base, passpost), frontend 3
  (implementation, failpre base, passpost), probe 2 (one setup-failed, one clean). No prove
  criterion was retried.
- Outcomes: G1 done (live projection; API shape, household authorization, proposal storage and
  historical snapshots preserved; no new persistence/schema/route). G2 done (single reason
  sentence; same live source for button and shortcut; pending guard; input/textarea protection
  and non-Accept actions preserved; no task-list-derived blocker added). G3 done (measured probe,
  corrected command, controls, isolation). A1/A2/A3/A4/A5 evidence below; A6 is this report.
  Constraints: scope-ceiling only; no production write/import/row repair; no rebuild/restart;
  read-only GET reproduction; no classification/Resolve/ordering/Scene/PR/schema/migration work;
  no privileged route-around; edits exact-match with backups and addressed-line prints
  (`/tmp/sg175-backup/`); no stash, no force-add; per-command bounds respected.

(c) Verification (candidate == W1 `0b42e7d`; base == `803cf52`; bytes unchanged since the runs —
W2/W3 touch only docs/worklogs/SG-175*)

    PASS POST backend — cd backend && ../backend/venv/bin/python -m pytest -q \
      tests/test_candidate_read.py tests/test_candidates.py \
      tests/test_plugin_expiry.py::test_dateless_import_requires_manual_entry_and_reads_back
    11 passed, 5 warnings in 4.27s          (7 candidate-read incl. 6 new; 3 candidates; 1 unchanged plugin control)

    FAIL PRE backend — /tmp/sg175-base/backend (base product tree + the three candidate test files)
    4 failed, 3 passed, 2 warnings in 3.46s
    FAILED test_candidate_get_drops_resolved_task_ids_and_accept_succeeds   (assert stale ids == [])
    FAILED test_candidate_get_ignores_stale_embedded_task_ids               (assert ['stale-task-id'] == [])
    FAILED test_candidate_get_includes_live_task_absent_from_proposal      (assert [] == [omitted live task])
    FAILED test_candidate_get_excludes_foreign_household_and_other_subject_tasks (stale/foreign ids served)
    (the 3 passes are the open-task control, snapshot byte-independence, and household-denial tests that the gate already satisfied)

    PASS POST frontend — node node_modules/vitest/vitest.mjs run \
      src/components/CandidateCard.test.tsx src/routes/ReviewPage.test.tsx
    Test Files  2 passed (2) · Tests  18 passed (18)      (CandidateCard 11, ReviewPage 7)

    FAIL PRE frontend — same command on /tmp/sg175-base/frontend
    Tests  2 failed | 16 passed (18)
    FAIL CandidateCard > blocked candidate with dedup matches renders the blocked reason exactly once — AssertionError: expected 3 to be 2
    FAIL ReviewPage > pending decision prevents repeated accept mutations from the keyboard — expected "spy" to be called 1 times, but got 3 times

    BUILD — cd frontend && npm run build (deployed command: package.json scripts.build = "tsc && vite build")
    exit 0; 1965 modules transformed; dist/assets/index-DRTd3YaC.js 322.00 kB

    PROBE — cd backend && /home/andrei/StorageGenie/backend/venv/bin/python ../docs/worklogs/SG-175_probe.py
    [T1] GET candidate -> 200 live_ids=3 includes_omitted=True state=proposed
    [T1] accept with live open tasks -> 409 detail='Candidate has unresolved review tasks' (control)
    [T1] GET candidate after resolution -> review_task_ids=[] live_open_tasks=0
    [T1] accept after resolution -> 200 state=accepted asset_exists=True (repaired blocked state)
    [T2] completion POST -> 200 resolved_contains_own_task=True; GET readback
         value={'expiry_date': '2026-10-14', 'date_type': 'expiry_date'} source_type='user'
         source_evidence_ids=['…'] task_row=resolved
    [CTL] expected rejection observed: accepted EXPIRY_FIELD count=0 expected exactly 1
    [CTL] expected rejection observed: value mismatch expected {'expiry_date': '2026-10-22', …} observed {'expiry_date': '2026-10-14', …}
    [T4] STILL-UNREPAIRED (SG-177): bare resolve of expiry.manual_entry returns 200 with zero expiry data
    [T4] STILL-UNREPAIRED (SG-178): ACTIVE unclassified asset absent from rows and unresolved_rows
    [ISO] prod_db_untouched=True; prod evidence stores untouched=True; evidence writes confined to override
    [CHECK] checks_passed=52 (every exercised criterion asserted before success)
    [RESULT] PROBE_OK        exit=0

    HEALTH (CO-92) — start and end: HTTP 200 {"status":"ok","db":"ok","storage":"ok"} — delta none.
    PROD DB — sha256 before == after == e6bef157440fb8b4a3262577362b071dcae07507ea9a7e04a614e11be28ee5bd.
    LIVE REPRO (GETs only, sanitized) — GET /v1/candidates/01a131a1-… → 200, state=edited,
    review_task_ids=['01a131a1-11c4-…'] (the embedded id points at a RESOLVED task); GET
    /v1/review-tasks → total=8 statuses=['resolved'] open=0; served bundle sha256
    1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d (== SG-173 record).

    Full captures: docs/worklogs/SG-175_failpre.log, SG-175_passpost.log, SG-175_probe_out.log,
    SG-175_verify.log, SG-175_query_delta.log (all committed).

INTENT — G1: code projects live open task ids into the same response field; the checks expect GET
== live gate with stale/foreign/other-subject excluded and omitted live tasks included; the
packet says project current open IDs for this candidate AND household with the same blocker
semantics. X=Y=Z. G2: code removes the duplicated blocked sentence from the dedup alert and adds
a keyboard pending guard; the checks expect exactly one reason sentence and no repeated mutation
while pending; the packet says render once, preserve pending protection, no repeated mutation.
X=Y=Z. G3: code replaces the literal probe label with measured assertions and controls; the probe
checks observed values and rejects deliberate wrong/missing expectations before PROBE_OK; the
packet says measure values before success. X=Y=Z.

TWINS (PG-SC-04) — after the fix, remaining `proposal.get("review_task_ids")` READ sites: 2
(`backend/app/api/v1/jobs.py:158`, `backend/app/services/candidates.py:792`), both outside the
scope ceiling and historical/API-only (no frontend caller); the candidate GET read site is now 0.
Remaining `review_task_ids` matches overall: 11 lines in 6 files (writers in `dedup.py` and
`services/candidates.py`, the new helper, the decision/split/merge routes, plugins
`resolved_review_task_ids`). Historical producers were not forced to zero.

UNCLEAR

- FIRST READ: "report actual image" vs the denied docker socket. Interpretation: health
  re-observed; image identity inherited as prior SG-174 evidence (packet: not a freshness gate);
  no route-around; judgement recorded in (a) for re-judging if PB-2 reads stricter.
- DURING EXECUTION: keyboard pending semantics. The keyboard previously had no pending guard; I
  added `!decision.isPending` to A and R only, preserving navigation shortcuts, input/textarea
  protection and non-Accept actions. Failpre shows the old repeated accept fired 3 times.
- DURING EXECUTION: probe `.env`/CWD/provider selection — corrected command and docstring; fake
  provider forced before any job step.
- REMAINING: deployed-URL story proof owes the post-repair deploy (this code is UNSERVED);
  SG-176 classification UI, SG-177 task-type-aware Resolve, SG-178 missing/unresolved visibility
  stay pending in STATE; F-SG171-5 duplicate sentence is cleaned up here; jobs/enrich snapshot
  readers remain by design (historical); docker socket remains denied in this lane (capability
  readback only).

Receipt (CO-60, notes ref): note added on WORK_HEAD `0b42e7d…` (exit 0) before this file was
committed; notes ref pushed `46b7d45..c59b282` (exit 0). After this report is committed the same
note is added to the report commit, the branch and notes ref are pushed, and the note is read
back on the remote with its annotated commit — runner-recorded. Legacy
finalize_dispatch_report.sh not used.

State of the world: product tree CHANGED and pushed; running service unchanged; production writes
NONE; tree UNSERVED; no close initiated.
