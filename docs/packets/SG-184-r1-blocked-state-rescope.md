# SG-184 — R1: verify merged SG-175 repair without product change, request waiver (RE-SCOPED D11)

`PB-1`–`PB-6` bind (`CODER.md` §14).
**BASE REF: automation.** Report actual resolved commit.
**STATUS: RE-SCOPED 2026-10-13 per D11 Option A from tree re-review at `3f3ae8f`; supersedes the re-derive draft. Zero product/test file change by design — this slice proves the merged repair, it does not re-implement it.**
**DATABASE: separately isolated disposable test database/storage; production GET observations read-only.**
**Restart: none. Autonomy: L3** (owner-set 2026-10-13; supersedes the L2 draft line). No STOP-breach waiver granted by this slice — the waiver is REQUESTED here, GRANTED only by a later audit/owner verdict. Serving the merged code is a later rider, never this slice.

## Why this exists

Re-review (`PG-IC-09`) found the re-derive premise stale: commit `0b42e7d` (SG-175 G1/G2) is an ancestor of `HEAD` (verify: `git merge-base --is-ancestor 0b42e7d HEAD`), so `get_candidate` already serves live `open_review_task_ids` (`backend/app/api/v1/candidates.py:164`, helper `backend/app/services/candidates.py:946`, predicate subject_ref + household_id + status=open, same rule as the `decide_candidate` gate at `backend/app/api/v1/candidates.py:52`) and `CandidateCard.tsx` already carries the single blocked sentence. Re-implementing would produce an empty diff and vacuous proof. The open question is not function but trust: SG-175 rated 90 `FLAG:SAFETY` (continued after a privileged-denial on an optional Docker listing) and its code is merged-but-`UNSERVED`. This slice re-proves the merged bytes cleanly, from scratch, without touching them.

## G1 — Discriminating fail-pre in a transient reverted worktree, pass-post on HEAD

Create a disposable worktree under `/tmp` (never in the repo): check out the resolved base there, restore the pre-`0b42e7d` bytes of ONLY `backend/app/api/v1/candidates.py` + `backend/app/services/candidates.py` via `git show 0b42e7d^:<path>` (reachability: `0b42e7d` must be an ancestor of repo `HEAD`, never `HEAD ==` a hash), copy in the three HEAD candidate test files unchanged. Run `tests/test_candidate_read.py + tests/test_candidates.py` there: EXPECT the SG-175 failpre signature (stale IDs served, live IDs missed — at least the four known failures) with the already-passing controls still passing. Then run the same node set on the repo `HEAD`: EXPECT full pass. Commit BOTH logs to `docs/worklogs/SG-184_failpre.log` + `SG-184_passpost.log`. Transient-plant exception to the no-product-change ceiling: reverted bytes live only in `/tmp`; end-of-slice clean-tree proof (`git status --porcelain` empty, no product diff) is a report gate, not prose.

## G2 — UI single-reason and pending-guard assertions on HEAD output

Run `src/components/CandidateCard.test.tsx + src/routes/ReviewPage.test.tsx` on `HEAD` (EXPECT pass, 18 per SG-175 architect verify). Assert on rendered output: the blocked sentence counted exactly once, dedup alert advisory-only, shortcut A/R inert while `decision.isPending`. One deliberate-wrong-input check (e.g. expect the sentence twice) must FAIL in the same run, proving the gate can fail. No frontend file changes.

## G3 — Measured probe re-run plus served-baseline GETs

Re-run committed `docs/worklogs/SG-175_probe.py` unchanged on disposable state from `backend/` with in-process fake provider + nulled keys (never copy `.env`); EXPECT `PROBE_OK` with missing-assertion and wrong-date controls rejecting on the same real reader. Separately capture read-only production GETs (status AND body) for one open-task and one resolved-task candidate: EXPECT the served bundle (SG-174 `d5da5684`, pre-repair) to show the OLD shape — that is the documented baseline, never a failure of this slice. The running service is NOT touched, rebuilt, restarted or redeployed by this slice (`PG-PR-04`).

## Constraints and acceptance

- Write ceiling `docs/worklogs/SG-184*` ONLY; zero product/test/config change in the repo. No migration/schema/dependency/lockfile change; no production row/evidence write; no paid call; no auth/credential/infra change; no rebuild/restart/recreate.
- Known-denied optional Docker listing is EXCLUDED up front (SG-175 lever); container identity stays UNVERIFIED this slice. ANY privileged denial, optional or not, STOPS the whole slice (`PB-2`); disclosure never substitutes for stopping (`PG-EV-03`).
- Disposable `DATABASE_URL`/`STORAGE_ROOT` asserted before any app import; scripted/fake providers only; no `.env` copy/dump (`PG-EV-13`).
- Ordinary commands 120s; focused disposable tests/probes 600s (uncalibrated); no full suite — waived explicitly, substitute is the named node sets above (`PG-DP-02`); no watcher.
- Start/end health GET; contract 0.47.0 echo with actual source; requested/resolved base, Work-HEAD, settings identity, lane budget/deadline/elapsed.
- A1: fail-pre shows the discriminating failures on reverted bytes, pass-post green on HEAD, both logs committed (`PG-EV-01/02/09`, `PG-SC-12`: BEFORE derived at the pre-repair bytes, recorded loader named).
- A2: single-reason + pending-guard asserted on real rendered output with a shown-failing wrong-input control; no divergent wordings.
- A3: probe `PROBE_OK` re-measured with negative controls on the real reader; no placebo.
- A4: served-baseline GETs captured showing pre-repair shape, explicitly dispositioned as baseline.
- A5: clean-tree proof, first token SG-184; `docs/worklogs/SG-184_report.md`; FIRST READ (packet premises checked/corrected) / DURING EXECUTION / REMAINING with dispositions; explicit waiver REQUEST for the SG-175 `FLAG:SAFETY` hold (grant stays with audit/owner). Partial honest proof, never invented completeness.

Guards: PG-EV-01/02/03/05/09/13; PG-SC-09/10/12; PG-IC-01/07/09; PG-DP-02/03; PG-PR-03/04/10.

Receipt: commits carry `Dispatch-ID: SG-184`; notes `refs/notes/storagegenie-coder-reports` first line `Dispatch-ID: SG-184 | Report: docs/worklogs/SG-184_report.md`, Work-HEAD; push automation/notes with exact remote readback. No retired finalizer. Architect audits/rates before any serving rider. No close or deploy inside this slice.
