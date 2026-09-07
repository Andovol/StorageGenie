SG-011 — queued findings report

Status: complete

Ref and provenance
- BASE_REF_REQUESTED: `automation`
- BASE_RESOLVED_COMMIT: `c67026f1778c72e2497e046f8343cc61f4cdebea`
- WORK_HEAD (implementation commit): `384ba99257de3a4e585edda196ec1d61ef229922`
- Origin: `git@github.com:Andovol/StorageGenie.git`
- Work dir: `/home/andrei/StorageGenie`
- Process provenance: `codex exec --sandbox danger-full-access -c model_reasoning_effort=high`; coder `codex`; reasoning effort `high`; model ID `unknown` because it was not present in process arguments or provider metadata.

Acceptance evidence

1. Mypy instance and count: The pre-change targeted run reported exactly `app/services/evidence_service.py:95: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]`, followed by `Found 1 error in 1 file (checked 1 source file)`. The post-change targeted run reported `Success: no issues found in 1 source file`. Repo-wide `mypy app` changed from `Found 44 errors in 11 files` to `Found 43 errors in 10 files`; it did not grow. The remaining 43 are listed by file/line in `docs/worklogs/SG-011.log` and are outside the scope ceiling.

2. Evidence behavior: Before the change, `timeout 300s ../venv/bin/pytest -q tests/test_evidence_upload.py tests/test_export.py` exited 0 with `13 passed, 1 warning in 1.04s`. After the change, the same two named modules exited 0 with `13 passed, 1 warning in 0.96s`. Both were real non-empty collections; no skipped test or vacuous gate was reported.

3. Alembic head construction: `backend/alembic/versions/` was enumerated and contained exactly `0201cf10c56c_001_core_foundation.py`, with revision `0201cf10c56c`. `backend/app/api/v1/exports.py` now computes `ALEMBIC_HEAD` with Alembic `ScriptDirectory.get_current_head()` rooted at `backend/alembic`; the existing body route still emits `"db_revision": ALEMBIC_HEAD`. The export test compares the HTTP response to both the computed module value and an independently constructed script-directory head.

4. Scratch divergence control: In a temporary, never-committed copy, the migration revision was perturbed to `0201cf10c56d`. The mechanism emitted `scratch db_revision=0201cf10c56d` and `scratch alembic_head=0201cf10c56d`, while `original literal=0201cf10c56c`; the check printed `CAUGHT: runtime export revision diverged from the old literal after scratch migration perturbation`. The scratch copy was removed. This is an observed divergence response, not a gate that could pass vacuously.

5. Full gates: `timeout 300s ../venv/bin/pytest -q` exited 0 with `23 passed, 1 warning in 1.45s`; `timeout 120s ../venv/bin/ruff check app tests` exited 0 with `All checks passed!`; and `timeout 120s git diff --check` exited 0. The only test warning was the existing Starlette deprecation about httpx/TestClient.

6. Scope and findings: Committed implementation paths are `backend/app/services/evidence_service.py`, `backend/app/api/v1/exports.py`, and `backend/tests/test_export.py`; committed evidence paths are `docs/worklogs/SG-011.log` and `docs/worklogs/SG-011_report.md`. No migration was added, no runtime dependency was added, and no database, service, restart, environment, secret, infrastructure, host, or privileged operation was touched. The packet’s expected baseline count of 43 differed from the measured pre-change count of 44; this was recorded as a finding. Direct `python`/`pytest` commands were unavailable, so explicit project-local venv binaries were used.

7. Timing: Ordinary commands had a 120s bound; suite legs had a 300s bound; overall budget was 2100s. The two required targeted suite legs took 1.04s before and 0.96s after; the full suite took 1.45s; timed suite legs totaled 3.45s. No command timed out or was killed, and the slice completed within the 2100s budget.

8. Commit/receipt handoff: Implementation commit is `384ba99257de3a4e585edda196ec1d61ef229922`. The final evidence commit containing this report is the receipt target; after it is pushed, the notes ref will carry the exact `Dispatch-ID: SG-011 | Report: docs/worklogs/SG-011_report.md | Work-HEAD: <final-evidence-commit>` note, verified locally and remotely. No commit will follow the note.

UNCLEAR: FIRST READ — The queued line-95 error and single migration file matched; the packet’s claimed 43-error baseline was one lower than the measured 44.
UNCLEAR: DURING EXECUTION — The local venv was required because direct `python` and `pytest` commands were absent; all required gates still ran with explicit binaries, and the scratch perturbation caught the old-literal divergence.
UNCLEAR: REMAINING — The 43 advisory mypy findings outside scope and one Starlette deprecation warning remain; no production/database/restart verification was required or performed.
