# SG-259 audit — close-deploy rider for SG-258

**Score 96/100; no flag.** The rider served the SG-258 household-and-document half live. The diff is `docs/worklogs/SG-259*` only; no product byte. Every material claim in the report matches its log: the runtime diff exactly the three SG-258 backend files (`SG-259_g2.log`), the JS bundle changed (`g2`), the served code/bundle/taxonomy (`g3`), the census identical (`g4`), the health/routes (`g5`), the build/recreate (`deploy`), the pre-state (`prestate`), the socket (`g0`), the receipt (`receipt`). The receipt is on the notes ref; the contract echo is 0.56.0; the report's last line is `Verification: PASS`.

## Findings

I1. The session denied `/tmp` scratch; the Coder used the workspace-untracked `output/sg259-*` for `DOCKER_CONFIG` and scratch. No sudo, no alternate socket, no daemon restart. **ACCEPTED** — no product effect; the `output/` is untracked.

I2. The build was cache-satisfied; the image `d620e39d` was created 13:16:40Z during SG-258's gate. The Python tree equals the worktree 100/100 (`deploy` log, `python_diff_rc=0`). The `g1` full-tree diff is rc=1 for the worktree `__pycache__` only; the report's I2 says 100/100 Python files, diff rc=0, which is the Python-only comparison. **ACCEPTED** — the `__pycache__` is not product; the report's I2 should name the exclusion (report clarity, no code fix).

I3. The worktree's `frontend/dist` is stale (`index-Bc0MxNy8.js`), not the image's static (`index-C3mGPvdC.js`); the served HTTP bundle equals the image's `/app/static` byte-for-byte. **ACCEPTED** — observation; the serve is correct.

I4. The evidence scripts mis-measured the JS `cmp` (a `$?` overwritten by two `$(basename)` expansions in one `echo`) and the census extraction (a range header not in the log; the post file empty). Both were re-measured; the corrections are appended to `g2`/`g4`; the report's A3/A5 use the corrected values. **ACCEPTED** — disclosed; no product effect; the evidence scripts' `$?` capture and census parse are the lever.

I5. `AGENTS.md` binds no language overlay (`CO-83`). **ACCEPTED** — binding, not a gap.

I6. `has_expiry=True` is positional in the served constructor; the served module's introspection prints `documents_other.has_expiry=True`. **ACCEPTED** — the phrase and the artifact agree.

I7. The startup log's only error-pattern hit is the daily pass's own `errors=0`. **ACCEPTED** — the same false positive as SG-251/SG-257; no traceback.

I8. The three SG-258 findings are not this rider's work. **ACCEPTED** — the next stage; the engine `UNCLEAR` is answered by the served `dateless` code and the runtime diff; the coupled test is not served.

## Verification

A1–A8 PASS. The default endpoint was tried first and recorded; the socket proof; the pre-state; one build; one recreate; no migration; the runtime diff exactly three files; the JS bundle changed; the served code/bundle/taxonomy; the census identical; the health/routes; the receipt; the contract echo 0.56.0. The honest limit: the live classification/date/clear writes were not exercised (owner data). The release is the Architect's next act.

UNCLEAR FIRST READ — the positional `has_expiry` — resolved (I6). DURING EXECUTION — the `/tmp` denial and the evidence-script bugs — resolved (I1/I4). REMAINING — the root-owned `~/.docker` — accepted (engine arc).
