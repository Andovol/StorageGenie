SG-189 — R7 operator _guard direction fix: both containment directions rejected, messages name the true geometry

Model / effort: coder opencode, model opencode-go/deepseek-v4.1-flash, effort max — read from own process args
(/proc/$PPID/cmdline: "opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash
--variant max"). Served-model response metadata not available; no substitute value claimed. `max` is
catalogue-valid but uncalibrated vs D120/D15-high (G-A9, stated).
Working dir: /home/andrei/StorageGenie (branch automation). Remote: git@github.com:Andovol/StorageGenie.git.
BASE (packet requested automation, resolved at dispatch, clean): b4a995312aabe927ec108d871cd5531fc8b2abe4
(== origin/automation at start). WORK_HEAD (work commit): 02f1214e012d102a20310885e471d212bf59bbf9.
Evidence commit 908430bff6a94d200d5ef9f5ca54a0919079df38 (docs-only). This report lands in the receipt-paste
commit and carries no hash of its own (CO-55b).

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim): "**Contract version:
0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you read this file rather than
assumed its contents."
Source readback: VERSION=0.47.0; sha256(RULES.md)=49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed
== RULES.sha256 payload; contract HEAD bdbbaa7; no tag at HEAD (tag-object peel still not done — limitation
retained). rules_check.sh verbatim: `G-L1 UNCHECKED the cache is not checked out at a contract tag:
/home/andrei/storagegenie-contract` / `G-L5 UNCHECKED gh-unauthenticated` / `G-L7 UNCHECKED gh-unauthenticated` /
`G-L6 BYTES /home/andrei/.codex/AGENTS.md 2275` / `G-L6 BYTES /home/andrei/.config/opencode/AGENTS.md 1933` /
`G-L6 BYTES total[codex]=2275 unseen=architect-layer,state-file,other-ritual-files` / `G-L6 BYTES
total[opencode]=1933 unseen=architect-layer,state-file,other-ritual-files`; exit 3.

Health (CO-92): START epoch 1791922608 {"status":"ok","db":"ok","storage":"ok"} -> END epoch 1791922778
identical; delta none.

Lane budget/deadline/elapsed (own-dispatch metadata only): unit cgroup dispatch-storagegenie@SG-189.service;
runner pid 2187134 starttime ticks 669835731, btime 1785224168, CLK_TCK 100 -> start epoch 1791922525;
RUN_BUDGET_S=2100 from world-readable /etc/dispatch/storagegenie.conf -> deadline 1791924625; report written at
epoch 1791922817, elapsed 292 s of 2100 s. Phase split (box clock): recon/reads 2525->2608 (83 s);
fix + captures + work commit 2608->2778 (170 s); evidence commit/push/draft 2778->2817 (39 s). No single command
over 60 s; no command hit its bound; no hang; no watcher. No privileged operation attempted (all optional
environment/Docker probes excluded) -> no denial -> no PB-2 stop.

(a) Issues / deviations / surprises
1. PB-1 premises verified exactly: `_guard` at backup_restore_drill.py:115-125; equal + prod-inside-work rejected
   under one message naming the opposite geometry ("work-dir ... is inside production storage ..." for the case
   where the production storage sits INSIDE the work dir); work-inside-prod allowed (the recursive-copy shape the
   message claims to stop). Helper + test untouched since SG-086: `git log --follow` over both files shows only
   6eb805b then this slice — confirmed, matching the packet.
2. Message split beyond the literal ask (finding): the old shared message also misnamed equality ("inside" for
   identity). A1 requires every rejection to name its true geometry, so the branch was split three ways
   (equal / prod-inside-work / work-inside-prod). Accepted-set diff (CO-18): old {disjoint, work-inside-prod} ->
   new {disjoint}; the single member that left is work-inside-prod (intended, packet G1). No other arm narrowed;
   missing + readability checks unchanged.
3. CO-101 consumer: docs/worklogs/SG-182_probe_g1.py (committed SG-182 artifact) uses `_guard`; re-run against the
   fixed helper -> checks=22 fails=1, the one fail being its dated pre-fix expectation
   `guard[work-inside-source] expected=allowed actual=rejected` — the inversion itself, corrected message quoted.
   Not a product defect; log committed as SG-189 evidence.
4. Twin search (CO-17): the `in .*parents` comparator class in backend/scripts+app is the fixed helper only
   (class count 1, reconfirmed by grep). jobs.py:116 cursor twin is a different construct on a product route —
   out of this slice by packet design (follow-up micro-slice after SG-190); reported, not touched.
5. README runbook invocation (README.md:127-131, read; not reworded): no `--work-dir` -> main() tempfile.mkdtemp
   default -> work dir under /tmp while prod sits at repo `data/db` + the volume mountpoint -> disjoint; unchanged
   by this fix and pinned green by test_runbook_commands.py.
6. No other deviations: write ceiling respected, no production open (not even mode=ro), no Docker/environment
   probe, $0, no provider call, no privileged operation, tree clean at start and each commit staged explicitly.

(b) Actions
- Changed: backend/scripts/backup_restore_drill.py (4 insertions / 1 deletion inside `_guard`);
  backend/tests/test_backup_drill.py (+5 guard geometry tests through the ACTUAL `_guard`, docstring +2 lines;
  51 insertions / 2 deletions); docs/worklogs/SG-189* (probe script, 8 logs, worklog, this report). No other
  operator script, no product route, no production run, no installs, no infra change.
- Commits: 02f1214e012d102a20310885e471d212bf59bbf9 work; 908430bff6a94d200d5ef9f5ca54a0919079df38 evidence
  (docs-only); this report's commit and the notes receipt publish after this file is written.
- Push (observed at readback): `b4a9953..908430b automation -> automation` (exit 0); ls-remote
  refs/heads/automation = 908430bff6a94d200d5ef9f5ca54a0919079df38 (work commit 02f1214 contained). The
  report/receipt commits land after this file by design; their readback is the receipt sequence, not this report
  (CO-55b).
- External/production effects: NONE written. The production DB and storage were never opened (not even mode=ro);
  the only production interaction is the two health GETs. Scratch only: /tmp/opencode/sg189-* probe dirs (removed
  with containment checks) and /tmp/opencode/sg189-base-tree (base archive used for the FAIL leg).
- Durations (UTC, box clock): start 1791922525; report write 1791922817; elapsed 292 s. Test-command count: 3
  pytest invocations (implementation ladder, base FAIL leg, authoritative) + 3 script executions (probe base,
  probe candidate, SG-182 probe re-run). Retry count: 0 slice retries; 0 verification_attempts (the FAIL->PASS
  pair is one demonstration). Provider-call count: 0. Health delta: none. Highest-impact action: the guard
  direction fix plus the five-geometry test extension through the actual helper.

(c) Verification — verbatim blocks (full logs committed; labels per invocation)

FAIL leg — CANDIDATE test file vs BASE helper (docs/worklogs/SG-189_focused_base.log; base = git archive of
b4a9953 at /tmp/opencode/sg189-base-tree, candidate test file sha256
2cac034c8bf078ab03fc0179be15a766e4b073c81062961464c7aac7f3635bf2 equal in both trees; command:
`/home/andrei/StorageGenie/backend/venv/bin/python -m pytest backend/tests/test_backup_drill.py -v` cwd=base tree):
  E       AssertionError: Regex pattern did not match.
  E         Expected regex: 'equals production storage'
  E         Actual message: 'STOP: work-dir /tmp/pytest-of-andrei/pytest-0/test_guard_rejects_work_dir_eq0/prod/storage is inside production storage /tmp/pytest-of-andrei/pytest-0/test_guard_rejects_work_dir_eq0/prod/storage'
  E       AssertionError: Regex pattern did not match.
  E         Expected regex: 'production storage .* is inside work-dir'
  E         Actual message: 'STOP: work-dir /tmp/pytest-of-andrei/pytest-0/test_guard_rejects_work_dir_en0/work is inside production storage /tmp/pytest-of-andrei/pytest-0/test_guard_rejects_work_dir_en0/work/storage'
  E       Failed: DID NOT RAISE SystemExit
FAILED backend/tests/test_backup_drill.py::test_guard_rejects_work_dir_equal_to_production_storage
FAILED backend/tests/test_backup_drill.py::test_guard_rejects_work_dir_enclosing_production_storage
FAILED backend/tests/test_backup_drill.py::test_guard_rejects_work_dir_inside_production_storage
========================= 3 failed, 5 passed in 0.13s ==========================

Probe BASE (docs/worklogs/SG-189_probe_base.log; five geometries through the ACTUAL base `_guard`):
[FAIL] guard[equal] message names the true geometry fragment='equals production storage' msg='STOP: work-dir /tmp/opencode/sg189-nfz7fazu/equal/stor is inside production storage /tmp/opencode/sg189-nfz7fazu/equal/stor'
[FAIL] guard[prod-inside-work] message names the true geometry fragment='is inside work-dir' msg='STOP: work-dir /tmp/opencode/sg189-nfz7fazu/prod-inside-work/enclose is inside production storage /tmp/opencode/sg189-nfz7fazu/prod-inside-work/enclose/stor'
[FAIL] guard[work-inside-prod] expected=rejected actual=allowed work=/tmp/opencode/sg189-nfz7fazu/work-inside-prod/stor/work storage=/tmp/opencode/sg189-nfz7fazu/work-inside-prod/stor msg=''
[FAIL] guard[work-inside-prod] message names the true geometry fragment='is inside production storage' msg=''
[summary] checks=9 fails=4

Probe CANDIDATE (docs/worklogs/SG-189_probe_candidate.log; same five geometries through the fixed `_guard`):
[PASS] guard[equal] ... msg='STOP: work-dir ... equals production storage ...'
[PASS] guard[prod-inside-work] ... msg='STOP: production storage ... is inside work-dir ...'
[PASS] guard[work-inside-prod] ... msg='STOP: work-dir ... is inside production storage ...'
[PASS] guard[disjoint] expected=allowed actual=allowed msg=''
[PASS] guard[missing] ... msg='STOP: production DB not found: .../missing/db/absent.db'
[summary] checks=9 fails=0 (rc=0)

Authoritative focused run — CANDIDATE, post-commit (docs/worklogs/SG-189_focused_candidate.log; echoed
CANDIDATE HEAD 02f1214e012d102a20310885e471d212bf59bbf9 == published work commit; echoed BASE
b4a995312aabe927ec108d871cd5531fc8b2abe4 == packet start HEAD; command:
`backend/venv/bin/python -m pytest backend/tests/test_backup_drill.py backend/tests/test_runbook_commands.py -v`):
============================== 11 passed in 0.10s ==============================
(test_backup_drill.py 8 nodes incl. the 5 new guard geometries + test_runbook_commands.py 3 nodes; rc=0)

CO-101 cross-check — SG-182 probe re-run on the fixed helper (docs/worklogs/SG-189_sg182_probe_rerun.log):
[FAIL] guard[work-inside-source] expected=allowed actual=rejected work=/tmp/opencode/sg182-g1-gyn2ls4l/guard/stor3/work db=/tmp/opencode/sg182-g1-gyn2ls4l/guard/db3/prod.db storage=/tmp/opencode/sg182-g1-gyn2ls4l/guard/stor3 msg='STOP: work-dir /tmp/opencode/sg182-g1-gyn2ls4l/guard/stor3/work is inside production storage /tmp/opencode/sg182-g1-gyn2ls4l/guard/stor3'
[summary] checks=22 fails=1
(the single fail is that artifact's dated pre-fix expectation; every other check green, drill on synthetic state
green, process exit 1 by its own fail counter — the inversion itself.)

Health (docs/worklogs/SG-189_health_end.log): `{"status":"ok","db":"ok","storage":"ok"}` (http_code=200),
identical to START.

Runbook disjoint by reading (README.md:127-131, quoted verbatim):
backend/venv/bin/python backend/scripts/backup_restore_drill.py \
  --prod-db data/db/storagegenie.db \
  --prod-storage "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')"
No --work-dir -> mkdtemp default is under /tmp, production paths are data/db and the volume mountpoint -> the
documented invocation stays disjoint; no reword needed.

INTENT: code rejects both containment directions (and equality) with messages naming the true geometry; the check
expects each of the five geometries through the ACTUAL `_guard` (no reimplementation); the approved packet says
reject work-inside-prod alongside the existing cases and correct the inverted message. X=Y=Z.
TWINS: `in .*parents` comparator class in backend/scripts+app = 1 (the fixed helper). No out-of-scope
operator-script comparator sites. jobs.py:116 cursor construct is a different class on a product route — out of
scope by packet design, rides the follow-up micro-slice after SG-190.

UNCLEAR
FIRST READ: packet premises all held (line range 115-125; defect direction; helper/test untouched since SG-086);
README invocation read and disjoint; write ceiling respected; probe cases re-derived on target, not copied
(SG-182's script re-run separately under CO-101).
DURING EXECUTION: equality branch message split was needed for A1 precision (reported in (a)2); the candidate test
bytes were sha256-verified equal in the FAIL and PASS trees; the SG-182 probe re-run's single fail is its dated
expectation; /tmp/opencode/sg189-base-tree archive left in scratch; no repo dirt (status clean at commits).
REMAINING: Architect audit/rating of SG-189 before SG-190; jobs.py:116 cursor micro-slice after SG-190;
F-SG182-1 disposition candidate RESOLVED (guard + messages + tests) at audit; no close or deploy in this slice
(SG-175 CLOSE_BLOCKED status untouched).
