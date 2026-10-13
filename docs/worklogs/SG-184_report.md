SG-184 — R1 verification: merged SG-175 repair re-proved without product change; waiver REQUESTED (UNSERVED)

model opencode-go/deepseek-v4.1-flash · effort max — read from /proc/1772133/cmdline
(`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash
--variant max`), never from a system-prompt identity line. Served-model response metadata was not
available; no substitute value claimed. `max` is catalogue-valid but uncalibrated vs D120/D15-high
(G-A9, stated).
Work dir /home/andrei/StorageGenie · branch `automation` · remote
git@github.com:Andovol/StorageGenie.git · BASE requested ref `automation` → resolved commit
`df1b5c825226676c0d9231b8f3938c61140e5811` (local HEAD == origin/automation at start; worktree
clean) · WORK_HEAD (product bytes) `df1b5c8` — ZERO product/test/config change by design; evidence
commit W1 `04e80b52e29f4b08d7d4e98989af770b11ff8f6c` (six logs); this report lands in the next commit
per CO-55b and the receipt note carries the published head.

Contract echo (host copy /home/andrei/storagegenie-contract/CODER.md line 3, verbatim):
"**Contract version: 0.47.0** — **echo this line verbatim in your receipt.** It is the only proof that you
read this file rather than assumed its contents."
Source readback: /home/andrei/storagegenie-contract/VERSION=0.47.0; RULES.md sha256
49338e39a5749821e7e26724d28715d4d27b0a34e01b359ec91bc3d85239e3ed == RULES.sha256 (installed
payload). `rules_check.sh` run from the host contract path exits 3 (G-L1 cache-not-at-tag +
gh-unauthenticated L5/L7) — inherited SG-172..182 shape; the repo `.rules-cache/` is absent (host
path is the current source); no host rule or cache was changed.

RESULT: NO PRODUCT CHANGE. G1/G2/G3 re-proof executed from scratch on the merged bytes; all three
acceptance gates green; six evidence logs committed; SG-175 `FLAG:SAFETY` hold waiver REQUESTED
(grant stays with audit/owner). The running service was NOT touched, rebuilt, restarted or
redeployed (`PG-PR-04`). Production writes: NONE. Provider calls: 0. No privileged operation was
attempted (the known-denied optional Docker listing is excluded up front) → no denial → no `PB-2`
stop.

Health (CO-92): START `{"status":"ok","db":"ok","storage":"ok"}` (HTTP 200) → END identical;
delta none.
Lane budget/deadline/elapsed (own-dispatch metadata only): unit cgroup
dispatch-storagegenie@SG-184.service; coder pid 1772133 start epoch 1791912468 (17:27:48Z);
RUN_BUDGET_S=2100 from /proc environ (stop window 1791914568 = 18:02:48Z); report written at
epoch ≈1791912830, elapsed ≈360 s of 2100 s. No command hit its bound and none hung (failpre
3.84 s, passpost 3.40 s, ui 1.95 s, control 1.69 s, probe well inside its 600 s bound; ordinary
commands under 120 s). No watcher.

(a) FIRST READ — packet premises checked / corrected (PB-1)

1. VERIFIED: `0b42e7d` (SG-175 G1/G2) is an ancestor of HEAD — `git merge-base --is-ancestor
   0b42e7d HEAD` exit 0, HEAD `df1b5c8` != `0b42e7d`; parent `0b42e7d^` = `803cf52` (the SG-175
   base). `get_candidate` serves live `open_review_task_ids` at
   `backend/app/api/v1/candidates.py:164`; helper at `backend/app/services/candidates.py:946` with
   predicate subject_ref + household_id + status=open, ordered created_at,id. Frontend
   `CandidateCard.tsx` carries the single blocked sentence; `ReviewPage.tsx` carries the pending
   guard. Re-implementation would indeed be an empty diff — the re-scope premise holds.
2. CORRECTED (trivial): the packet cites the decision gate at
   `backend/app/api/v1/candidates.py:52`; the gate is the `if` at :50 with its `raise` at :51. Same
   rule as the helper, as the packet says.
3. CORRECTED (material, stated loudly per `PB-3`): G3 asks for "one open-task and one
   resolved-task candidate" production GETs. At capture time production has 8/8 review tasks
   `status=resolved` (open = 0; read-only sqlite + served listing in
   `SG-184_served_baseline.log`). NO open-task candidate exists, so that branch of the pair is
   VACUOUS in production and cannot be captured. I did not fabricate or substitute one; the
   discriminating open-task proof is carried by the G1 disposable failpre (below), and the
   resolved-task branch is captured as specified.
4. INTERPRETATION: "the three HEAD candidate test files" = `backend/tests/test_candidate_read.py`,
   `frontend/src/components/CandidateCard.test.tsx`, `frontend/src/routes/ReviewPage.test.tsx`
   (exactly the candidate-test files `0b42e7d` touched); copied into the worktree unchanged.

(b) DURING EXECUTION — what was run, and what it showed

G1 (failpre/passpost; `PG-SC-12` BEFORE derived at the pre-repair bytes, loader named):
- Disposable worktree `/tmp/sg184-g1` (detached at resolved base `df1b5c8`; never in the repo).
  ONLY the two product files restored to pre-repair bytes via `git show 0b42e7d^:<path>`:
  worktree diff vs base = 2 files, +3/-21 lines (exact inverse of `0b42e7d`'s product hunks);
  `grep -c open_review_task_ids` = 0 in both. The three HEAD test files copied in unchanged.
- FAILPRE (worktree): `pytest -q tests/test_candidate_read.py tests/test_candidates.py` →
  **4 failed, 6 passed** — the identical four SG-175 failures: drops-resolved (stale resolved id
  served), ignores-stale-embedded (`['stale-task-id']` served), includes-live-absent-from-proposal
  (`[] == [live task]`), excludes-foreign/other-subject (stale/foreign ids served). The three
  already-passing controls in `test_candidate_read.py` and all three `test_candidates.py` tests
  passed. Full raw output: `docs/worklogs/SG-184_failpre.log`.
- PASSPOST (repo HEAD): same node set → **10 passed** in 3.40 s. Raw:
  `docs/worklogs/SG-184_passpost.log`. Discriminating and green — A1 met.

G2 (UI rendered output on HEAD; `docs/worklogs/SG-184_ui.log`):
- `vitest run src/components/CandidateCard.test.tsx src/routes/ReviewPage.test.tsx` on HEAD →
  **18 passed (11 + 7)** == SG-175 architect verify. The rendered-output assertions cover: blocked
  sentence counted exactly once with dedup matches; dedup alert keeps only its advisory (no second
  blocked sentence); shortcut A/R inert while `decision.isPending` (keyboard accept fired exactly
  once across repeat A/R); blocked Accept disabled with no shortcut decision.
- Wrong-input control (same run shape, transient edit ONLY in the `/tmp/sg184-g1` worktree, never
  in the repo): one added test expecting the blocked sentence TWICE (split length 3) against
  rendered truth once (split length 2) → run = **1 failed | 18 passed (19)**, failure
  `expected 2 to be 3` — the gate can fail. Raw: `docs/worklogs/SG-184_ui_control.log`. A2 met.

G3 (probe + served baseline):
- `docs/worklogs/SG-175_probe.py` re-run UNCHANGED from `backend/` with disposable
  `DATABASE_URL`/`STORAGE_ROOT` set before any app import, in-process fake provider, keys nulled
  (never copied `.env`) → **PROBE_OK**, `checks_passed=52`, with the missing-assertion and
  wrong-date controls rejecting on the same real reader and the true value accepted; prod DB
  sha256 `e6bef157…` before == after; prod evidence stores untouched (diff vs SG-175 raw log:
  only tmp paths + random ids). Raw: `docs/worklogs/SG-184_probe.log`. A3 met — re-measured, no
  placebo.
- Served baseline (read-only GETs; `docs/worklogs/SG-184_served_baseline.log`): served bundle
  sha256 `1b4680a0eddadff3c95a64b6bc00d744764d127a72cd5690ebea948b7664a29d` == SG-175 recorded
  served bundle (SG-173/174 deployed record) — bytes identical to the pre-repair baseline. GET
  resolved-task candidate `01a131a1-11c3…` → 200 with `review_task_ids=
  ["01a131a1-11c4-…"]` (a RESOLVED task) and second candidate `01a0c4a2-2a46…` → 200 with its two
  resolved ids — the OLD shape, dispositioned as the documented pre-repair BASELINE, not a failure
  of this slice. GET /v1/review-tasks → 200, total=8, all `resolved`. A4 met (open-task branch
  vacuous, see (a)3).

(c) Verification summary — exact command returns

    FAILPRE  /tmp/sg184-g1/backend (pre-repair bytes + HEAD tests)   4 failed, 6 passed  (3.84 s)
    PASSPOST /home/andrei/StorageGenie/backend (HEAD)               10 passed            (3.40 s)
    UI       frontend vitest (HEAD)                                 18 passed (2 files)  (1.95 s)
    UI CTL   /tmp/sg184-g1/frontend (+wrong-input test)             1 failed | 18 passed (1.69 s)
    PROBE    SG-175_probe.py unchanged                              PROBE_OK, 52 checks
    SERVED   GET /v1/review-tasks + two candidate GETs              200; OLD shape (baseline)

External effects: none. Production DB/evidence untouched (hash proof in probe log; GETs only).
No migration/schema/dependency/lockfile change; no rebuild/restart/recreate; no paid call; no
auth/credential/infra change; write ceiling `docs/worklogs/SG-184*` respected (six logs + this
report). End-of-slice clean-tree proof is `git status --porcelain` empty after the report commit
and `git diff HEAD-1:product` = 0 lines (product bytes == `df1b5c8`; see receipt readback).

WAIVER REQUEST (explicit; grant stays with audit/owner): I request the audit/owner waive the
SG-175 `FLAG:SAFETY` hold for the purpose of a later serving rider. Basis: the merged bytes were
re-proved cleanly from scratch (discriminating failpre → green passpost; UI single-reason,
advisory-only dedup and pending guard on real rendered output with a shown-failing wrong-input
control; measured probe re-run with negative controls; no privileged operation attempted anywhere
in this slice). This slice grants NO waiver itself and takes no serving action; if the audit's
reading of `PB-2` for SG-175's optional Docker listing is stricter than SG-175's own disclosure,
that judgement belongs to the grant step, not here.

UNCLEAR

- FIRST READ: the G3 pair premise — no open-task candidate exists in production (8/8 tasks
  resolved), so the open-task branch is vacuous and documented rather than substituted; the packet
  gate line `candidates.py:52` is actually :50-51.
- DURING EXECUTION: nothing blocked; no privileged denial (Docker listing excluded up front;
  container/image identity stays UNVERIFIED this slice as stated). Probe output differs from
  SG-175's only in tmp paths and random ids.
- REMAINING: the SG-175 code remains `UNSERVED` (no deploy/close in this slice); serving it is a
  later rider gated on the audit/owner verdict this slice requests; SG-176/177/178 items and the
  probe-declared STILL-UNREPAIRED findings (SG-177 bare-resolve, SG-178 active-unclassified
  visibility) remain open and were not touched.

Receipt (CO-60, notes ref): note `Dispatch-ID: SG-184 | Report: docs/worklogs/SG-184_report.md`
+ Work-HEAD added on the report commit, branch and notes ref pushed, note read back on the remote
with its annotated commit — runner-recorded; legacy finalizer not used. Architect audits/rates
before any serving rider. No close or deploy inside this slice.

State of the world: product tree UNCHANGED (HEAD `df1b5c8` + docs-only evidence commits); running
service unchanged (pre-repair bundle `1b4680a0…` still served); production writes NONE; SG-175 code
still UNSERVED; waiver REQUESTED, not granted.
