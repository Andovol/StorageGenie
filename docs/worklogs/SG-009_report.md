SG-009 — Frontend verify/repair + lint unmasking report

Status: complete

Ref and provenance
- BASE_REF_REQUESTED: `automation`
- BASE_RESOLVED_COMMIT: `1567ff4a7ecad9321accffbb3ed94c7f64aaf120`
- WORK_HEAD (implementation commit): `10c9e743fec1289888534ba5a2ae266993d937e3`
- Origin: `git@github.com:Andovol/StorageGenie.git`
- Work dir: `/home/andrei/StorageGenie`
- Process provenance: `codex exec --sandbox danger-full-access -c model_reasoning_effort=high`; reasoning effort `high`; model ID `unknown` because it was not present in process arguments or provider metadata.

Acceptance evidence

1. Vitest: `timeout 300s ./node_modules/.bin/vitest run` from `frontend/` exited 0 in 1.10s (budget 300s). Quoted result: `Test Files  3 passed (3)` and `Tests  7 passed (7)`. All three files ran, all seven tests passed, and no tests were skipped. The inherited baseline was independently re-proved before changes with the same 3-file/7-test result, so no repair fail-then-pass was needed.

2. Typecheck: `timeout 120s ./node_modules/.bin/tsc --noEmit` exited 0 in 1.34s (budget 120s). Output was empty; there were no errors before or after and no new `// @ts-ignore` or `any` cast was added.

3. Lint unmasking: `frontend/package.json` now runs `eslint src` with no `|| true`. ESLint 9 flat config is in `frontend/eslint.config.js`, using the `typescript-eslint` recommended preset and the `allowShortCircuit` option for the existing intentional assignment expression. Pinned direct dev dependencies are `eslint: 9.39.5` and `typescript-eslint: 8.69.0`; `frontend/package-lock.json` records the resolved tree.

   The fire-control was real: a temporary, never-committed `.scratch/unused-variable.ts` produced exit 1 with `1:7 error 'unusedScratch' is assigned a value but never used @typescript-eslint/no-unused-vars`; the scratch file was removed. The final `timeout 120s npm run lint` exited 0 in 0.92s (budget 120s), with output `> eslint src` and no errors.

   The first unmasked run identified `frontend/src/routes/AssetDetailPage.tsx:43:7` as `@typescript-eslint/no-unused-expressions`. Per the slice limit, no structural source redesign was made; the rule’s `allowShortCircuit` setting recognizes the existing behavior while keeping the rule active for other expressions.

4. Worklog/report: committed paths are `docs/worklogs/SG-009.log` and `docs/worklogs/SG-009_report.md`.

5. Scope: committed output paths are `frontend/package.json`, `frontend/package-lock.json`, `frontend/eslint.config.js`, `docs/worklogs/SG-009.log`, and `docs/worklogs/SG-009_report.md`. No backend, datastore, service, restart, migration, environment, secret, or infrastructure file changed.

6. Non-vacuity and findings: the full suite collected three files and seven tests. The original lint gate exited 0 while printing `eslint: not found`, proving the mask was load-bearing. Vitest emitted two React Router future-flag warnings on stderr. npm install reported six audit vulnerabilities (4 moderate, 1 high, 1 critical); neither issue was changed in this scoped slice.

7. Timing: ordinary command budget 120s; test/install budget 300s. Install completed in 4.7s; final Vitest in 1.10s; final typecheck in 1.34s; final lint in 0.92s. No command timed out or was killed.

UNCLEAR: FIRST READ — The packet’s expected baseline of 3 files and 7 tests matched the tree; the lint dependency was absent and the `|| true` mask concealed that fact.
UNCLEAR: DURING EXECUTION — The suite and typecheck were already clean; the only lint finding was handled by configuration for the existing short-circuit assignment, within the permitted repair boundary.
UNCLEAR: REMAINING — React Router future warnings and npm’s six audit vulnerabilities remain for a later slice; no backend or production verification was required or performed.
