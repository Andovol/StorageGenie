SG-141 — Fix the 3 TS2739 literals blocking the production build (test-only, then green tsc)

**Result: PASS.** The three `WebAlternate[]` literals in `frontend/src/components/WebAlternates.test.tsx` were completed with the required `source_type`/`source_url`/`retrieved_at` keys (explicit `null`), `tsc --noEmit` is exit 0, the file + full frontend suite are green, `types.ts` is byte-identical, and the diff ceiling holds.

Settings (CO-78, from process arguments / provider metadata — never the identity line): coder `opencode`; **model `opencode-go/deepseek-v4.1-flash`** and **effort `high`** read from argv `/proc/162575/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high`. **Spend: real $0.000000 USD** (zero metered calls; no USD-metered call exists on any path — `PG-PR-06`).
Work dir `/home/andrei/StorageGenie`; origin `git@github.com:Andovol/StorageGenie.git`.
**BASE** (`origin/automation` requested; resolved): `b4fec8bebcde3ef33fa6c2c1f765047091df6646` · **WORK_HEAD:** `bb30209802ab6f53e862b59b2b1f1285f9363130` (product fix + verify log; receipt-note target). This report lives in the following worklog commit, so it does not carry its own hash (CO-55b).
Gates: **DATABASE** none (no read/write) · **Restart** none · **Deploy** none (the re-ride owns serving; `PG-PR-04` stated). Role guard held (Coder only; no dispatch verb, no unit started/polled).
Contract echo `0.40.0` verbatim; source path `/home/andrei/storagegenie-contract/VERSION`. Recorded `0.40.0` == published (`f26dbd3`, D4 adoption).

## G0 — reproduce the red on BASE (fail-pre, committed): PASS

- Base clean: HEAD == `origin/automation` == `b4fec8b…`; `git status --porcelain` empty.
- `cd frontend && ./node_modules/.bin/tsc --noEmit` on the unmodified tree → **EXIT=2**, quoted verbatim:
  - `WebAlternates.test.tsx(59,7): error TS2739: … missing … source_type, source_url, retrieved_at`
  - `WebAlternates.test.tsx(74,7): error TS2739: … missing … source_url, retrieved_at`
  - `WebAlternates.test.tsx(79,7): error TS2739: … missing … source_url, retrieved_at`
- **Packet expectation `:59,74,79` == observed exactly** (the packet's prose *"`:58-63` model literal, `:73-83` brand + category"* describes the literal spans; the compiler-reported error lines are 59/74/79).
- **PG-IC-08 blast radius:** the error set is **exactly** those 3, all in the one file; no error anywhere else. Blast radius clean.
- Capture committed at `0b57b12` **before any edit**.

## G1 — complete the literals + prove green: PASS

- **Shape decision (decide + report):** read `WebAlternates.tsx` first — `source_type ?? "unknown source"` (:31) and `source_url ? … : null` (:32) / `retrieved_at ? … : null` (:46) treat explicit `null` identically to an omitted key (both falsy). So the decided shape is **explicit `null`**, which is observationally identical here. No reason to touch `types.ts`; the required triple stands.
- **Edit:** only the 3 literals; **7 inserted keys** (3 + 2 + 2), all `null`. Diff quoted in `SG-141_verify.log`.
- **Fail-post, same repo toolchain (`PG-SC-12`):**
  - `tsc --noEmit` → **EXIT=0** (full output = zero diagnostics; quoted as exit, not a grep-for-absence).
  - file vitest → `Test Files 1 passed (1)` / `Tests 4 passed (4)` / EXIT=0 — vitest **calls the real `WebAlternates`** through the repo config.
  - full frontend suite (`npm test` = `vitest run`) → `Test Files 27 passed (27)` / `Tests 243 passed (243)` / EXIT=0. **No reds**; base-proved-reds not applicable because vitest never typechecks — the defect was invisible to the suite at BASE too.
  - `eslint src/components/WebAlternates.test.tsx` → EXIT=0.
- Both runs committed (`0b57b12` pre, `bb30209` post).

## G2 — worklog and report

`docs/worklogs/SG-141.log`, `SG-141_report.md`, `SG-141_verify.log` (fail-pre + fail-post captures, suite/eslint, diff ceiling proof). First token `SG-141`. No secret in any committed artifact (`CO-100` — asserted; the only new values are the `null` literal).

### Actual-versus-budget per goal (units)
| Goal | Budget | Actual | Note |
|---|---|---|---|
| G0 tsc red read | ≤600s suite class (typecheck) | ~15s | exit 2, 3 errors captured |
| G1 tsc fail-post | ≤600s suite class (typecheck) | ~10s | exit 0 |
| G1 file vitest + eslint | ≤120s ordinary | ~2s | 4/4 green, eslint 0 |
| G1 full suite | ≤600s suite | ~5.1s | 27 files / 243 tests |
| G2 worklogs + notes | ≤120s / 300s push | ~90s | 3 files + note |
| Overall | ≤2400s | well under | no command killed, no hang |
| Spend | $0.000000 USD | **$0.000000 USD** | zero metered calls |

### Diff ceiling proof
`git diff --stat -- frontend/` → `1 file changed, 7 insertions(+)` in `WebAlternates.test.tsx`; no other product file. `git diff --exit-code -- frontend/src/api/types.ts` → exit 0 (byte-identical). Non-product writes are the three `docs/worklogs/SG-141_*` files only.

### Official guards (reviewer copies to the rating row)
`PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-09` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

### Receipt note (M20-corrected block; executed output pasted verbatim)
```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   b4fec8b..bb30209  automation -> automation
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-141 | Report: docs/worklogs/SG-141_report.md | Work-HEAD: bb30209802ab6f53e862b59b2b1f1285f9363130" \
    bb30209802ab6f53e862b59b2b1f1285f9363130
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   700df76..dc37ad9  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg141-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg141-fetched
$ git notes --ref=refs/notes/sg141-fetched show bb30209802ab6f53e862b59b2b1f1285f9363130
Dispatch-ID: SG-141 | Report: docs/worklogs/SG-141_report.md | Work-HEAD: bb30209802ab6f53e862b59b2b1f1285f9363130
```
The final-tip dual-annotation (SG-092 precedent) and its fetched `show` output are pasted in `SG-141.log`. Final line `note=yes`.

### No vacuous pass — stated loudly
- The fail-pre red is a **reproduced non-zero `tsc` exit with 3 quoted TS2739 compiler errors**, not an assertion.
- The fail-post green is **quoted full exit-0**; the suite green is quoted by file/test counts, not silence.
- The "no other file touched" claim is backed by `git diff --name-only` + a byte-identical `types.ts` check.
- **Watch-out flagged:** an exit-0 read from a `tsc` run with no `include` coverage would be vacuous. Here `tsconfig.json` `include: ["src"]` typechecks `*.test.tsx` (proven by the pre-edit red pointing at the test file), so the post-edit exit-0 is meaningful.

### Issues / disagreements (including outside this slice's scope)
- **F-SG141-1 (resolved here):** SG-135's merged `WebAlternates.test.tsx` broke the production `tsc && vite build`; this slice repairs it.
- **F-SG141-2 (premise delta, no impact):** the packet cites Architect-verified literal spans `:58-63` / `:73-83`; the compiler emits the errors at `:59,74,79`, which I quote. Both are consistent (span start vs object-literal start line).
- **F-SG141-3 (environment, no impact):** `npx` is not on PATH on this host; I invoked the repo-local binaries under `frontend/node_modules/.bin/` (`tsc`, `vitest`, `eslint`) and `npm test`, i.e. the same tools the build uses. No substitute toolchain introduced.

### UNCLEAR
- **FIRST READ:** whether the packet's expected error lines `:59,74,79` were meant to be the *literal span* lines or the compiler-reported lines; they coincide with the compiler output here, so the ambiguity was harmless.
- **DURING EXECUTION:** none material — the null-vs-omitted question was settled by reading `WebAlternates.tsx`; `npx` absence was worked around with the repo-local binaries without changing the toolchain.
- **REMAINING:** whether the re-ride close-out deploy (SG-140's blocked rebuild) will now be re-dispatched to ship the queue, since this slice expressly performed no rebuild/recreate.
