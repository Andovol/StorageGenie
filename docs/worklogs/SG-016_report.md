SG-016 | Inbox + review workspace UI

BASE ref requested: automation
BASE resolved: fbe7fea
Implementation commit before report: 07a904233ffce794ff729ba57b74cf0e2f359661
WORK_DIR: /home/andrei/StorageGenie
Origin: git@github.com:Andovol/StorageGenie.git
Coder: codex
Model: unknown (no model id appeared in readable process arguments; CLI default used)
Reasoning effort: high (verified from live process arguments: `codex exec ... -c model_reasoning_effort=high`)
Autonomy: L3, Phase 1 slice 5 of 7
Elapsed: approximately 6 min (approximately 360 s) / 2100 s (35 min) overall bound; no command was killed

Implemented

- Added the bounded read-only candidate endpoint at `backend/app/api/v1/candidates.py:72-109`. It household-checks candidate ids (404 missing, 403 mismatch) and returns candidate id/state/job id, proposal `fields`, dedup matches, review task ids, evidence ids, and optional asset linkage. `backend/tests/test_candidate_read.py` proves the 200/403/404 legs on a temp database.
- Added `frontend/src/routes/InboxPage.tsx`: household selection with the existing localStorage convention, job list from `GET /v1/jobs`, selected import detail from `GET /v1/imports/{job_id}`, progress/error rendering, retry by loaded job id, review queue, resolve action, candidate links, and asserted empty states.
- Added `frontend/src/components/JobCard.tsx`: loaded job identity/state and optional progress summary.
- Added `frontend/src/routes/ReviewPage.tsx`: candidate read-back, decision mutations, keyboard accept/reject/previous/next handlers, candidate invalidation, and asset handoff for expiry entry.
- Added `frontend/src/components/CandidateCard.tsx`: evidence thumbnails beside editable candidate fields, per-field confidence/source, explicit Unknown handling, duplicate/collision explanation, accept blocking while review tasks are open, and accept/edit/hold/reject actions.
- Added `frontend/src/components/ExpiryEntryForm.tsx`: date-type selector, manual expiry POST through the existing flat expiry contract, source evidence ids, `needs_evidence` display before entry, and query invalidation/read-back after entry.
- Added API types and typed client helpers in `frontend/src/api/types.ts` and `frontend/src/api/client.ts`. Registered `/inbox` and `/review/:candidateId` in `frontend/src/App.tsx`.
- Added focused tests: `frontend/src/components/JobCard.test.tsx`, `CandidateCard.test.tsx`, `ExpiryEntryForm.test.tsx`, `frontend/src/routes/InboxPage.test.tsx`, and `ReviewPage.test.tsx`.

Verification

- Frontend exact gate: `npm test -- --run` — 8 files / 19 tests passed.
- Frontend lint: `npm run lint` — exit 0.
- Frontend types: `tsc --noEmit -p tsconfig.json` — exit 0.
- Frontend discrimination: `vitest run --run -t wrong` — 4 wrong-fixture tests passed as guarded tests; each proves the intended contract assertion throws for wrong ids/state/evidence/read-back, so no test passes unchanged on both mocks. This is not a vacuous skipped gate: the selected tests executed and asserted the failure condition.
- Backend candidate route: `test_candidate_read.py` — 1 passed, with real 200/403/404 legs and loaded response identity.
- Full backend: 48 collected, 46 passed, exactly 2 failed. Only the carried ISS-1 nodes failed: `backend/tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and `backend/tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence`, because decoder libraries are unavailable in this environment. SG-012…SG-015 behavior otherwise stayed green.
- Ruff: `backend/venv/bin/ruff check app tests` — clean.
- Mypy advisory: 40 errors in 9 files / 50 sources, pre-existing untyped/unused-ignore findings; no out-of-ceiling changes attempted.
- Backend route decorator grep: only the existing candidate decision POST and the new candidate GET match in `backend/app/api/v1/candidates.py`; no other route decorator changed. `expiry_tracker.py` and migration paths are absent from the diff.
- `git diff --check` passed. No criterion relied on an empty diff, skipped suite, empty review queue, or uninvoked function; empty Inbox/task states and populated loaded fixtures are both asserted.

Scope decisions and findings

- Optional `candidate_id` job-list linkage was not added. The selected import detail already exposes the DEDUPLICATING output candidate id, so the additive backend surface was unnecessary and no compatibility risk was introduced.
- Batch accept was dropped as explicitly permitted by the packet’s last-goal rule; the single-decision calls are complete and tested.
- No migrations, live database writes, restart, privilege escalation, SSH check, secrets, `.env`, provider/AI code, or runtime dependency were used.
- The packet’s referenced `ARCHITECT.md`, `PACKET.md`, `DISPATCH.md`, and `PRODUCTION.md` files are absent from this checkout. The packet plus project `AGENTS.md` and `STATE.md` were used and the discrepancy is recorded.
- React Router emitted existing future-flag warnings in jsdom. This is a non-blocking test-runtime finding.
- Receipt note delivery is the final step after this report commit. The final work HEAD and the remote notes-ref read-back are quoted in the handoff after that step; no commit will follow the note.

Output paths committed by SG-016:

- `backend/app/api/v1/candidates.py`
- `backend/tests/test_candidate_read.py`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/src/components/CandidateCard.tsx`
- `frontend/src/components/CandidateCard.test.tsx`
- `frontend/src/components/ExpiryEntryForm.tsx`
- `frontend/src/components/ExpiryEntryForm.test.tsx`
- `frontend/src/components/JobCard.tsx`
- `frontend/src/components/JobCard.test.tsx`
- `frontend/src/routes/InboxPage.tsx`
- `frontend/src/routes/InboxPage.test.tsx`
- `frontend/src/routes/ReviewPage.tsx`
- `frontend/src/routes/ReviewPage.test.tsx`
- `docs/worklogs/SG-016.log`
- `docs/worklogs/SG-016_frontend.log`
- `docs/worklogs/SG-016_report.md`

UNCLEAR — FIRST READ: The packet’s method-routing files ARCHITECT.md, PACKET.md, DISPATCH.md, and PRODUCTION.md were absent from the checkout; the committed packet plus AGENTS.md and STATE.md were used.
UNCLEAR — DURING EXECUTION: The two named SG-013 decoder nodes remain red because pyzbar/libzbar and tesseract are unavailable; no privileged workaround was attempted. React Router emitted existing v7 future-flag warnings.
UNCLEAR — REMAINING: Batch accept is intentionally dropped; the two decoder nodes remain for the manual compose proof in SG-018, and expiry EXIF-source hardening remains carried to SG-017 as instructed.
