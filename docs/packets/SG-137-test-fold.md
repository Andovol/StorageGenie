# SG-137 — Fold #11–#14 into one client.test.ts coverage slice, dedupe updateAiModel

**Settings travel on the trigger** (`SG-137 coder=opencode effort=high`, D8) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D8-authorized rewrite (owner quote "D8 - approved"; SG-134 verdict REWRITE-AS-SLICE on PRs #11–#14): all four edit ONLY `frontend/src/api/client.test.ts` (same import line 2, same insert region ~112) and cannot each land as-is; #12/#13 both add `describe("updateAiModel")`. The union to ship, one file (Architect-measured 2026-09-28 from the four head diffs — re-verify each block on the target; a missing block is a finding): `describe("apiPatch")` (#11: success/detail/JSON-fallback) + `describe("apiPut")` (#12) + `describe("updateAiModel")` ONE copy (#12 vs #13 — compare both, keep the stronger, report which + why) + `describe` for the `fetchAiSettings` failure test (#13) + `describe("apiPost")` + `describe("apiPost helpers")` (`candidateDecision`/`sendChat`/`runPlanning`/`resolveReviewTask`, #14), with the import line extended to the union of used symbols. Sources (read on target, never merged): `refs/pull/11,12,13,14/head` (`#11 c593382` · `#12 03487ee` · `#13 08baa1d` · `#14 7356f9d`, all base `c849088` — a moved head is a STOP for that PR's blocks). The four PRs themselves are NEVER merged/rebased here — they stay open until this slice lands, then close from the workstation. **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-136's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** FOLD slice. Writes: `frontend/src/api/client.test.ts` (the union ONLY — no product file, no other test file), `docs/worklogs` (3 files) — and NOTHING else. No product-code write of any kind (prove by diff `--stat`: exactly 1 test file + 3 worklogs); no merge, no close, no rebase of the four PRs. Frontend tests run via `node_modules/.bin/vitest` (`npx` absent on host — SG-135 F4). No secret in test fixtures (`CO-100` — assert it).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-10` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G0 — read the four diffs, name the union (reads only — stated, not solved)

- Diff each head against the tree (`git diff <merge-base>...<head>`); enumerate every `describe`/`it` each PR adds (criterion: all test blocks across the four heads; expectation: the six describes above + ONE `updateAiModel` — differenced either way, a handed list is a fact too — DISPATCH.md §2a).
- Decide the `updateAiModel` keeper (#12 vs #13) by reading both blocks: keep the one with stronger failure coverage, report the choice + the dropped block's delta (any assertion the loser covers and the winner does not is folded in, not lost — dropping coverage silently is a STOP condition to check, not a finding to report later).

## G1 — write the union + prove it (fail-then-pass where the tree allows)

- Single edit to `client.test.ts`: union import line + the six describes (five unique + one `updateAiModel`). No product file touched; no other test file touched.
- Proof: the file's vitest run green (600s bound), quoted; then the FULL frontend suite green-except-base-proved-reds if it completes in-bound (reds stash-reproved on bare BASE) — if the full run cannot complete in-bound, report it UNRUN (never a pass) with the file-level green as the shipped proof and the full run as follow-up. `PG-EV-07`: the tests ship IN the file they cover (`client.test.ts` tests `client.ts` — state the covered module explicitly).
- Placebo read (`AUDIT.md` lens, applied to the union): each ported `describe` drives the REAL exported function (import present, call present, assertion on the result — not on a mock's echo). A ported block that cannot name its function is left OUT and reported, never pasted to make the count.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-137.log`, `SG-137_report.md`, `SG-137_verify.log` (per-PR blocks table + keeper choice, file + full-suite captures, diff `--stat` ceiling proof). First token `SG-137`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — `client.test.ts` (union only) + the 3 worklog files. **Any other write — product code, other test files, merges, closes, rebases — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs diff reads (reads INCLUDE `git` network reads; `gh` is known-absent — touching it is a STOP); G1 needs the union edit + vitest runs (modify-versus-call: tests CALL the real `client.ts` exports through vitest, never a hand-rolled harness); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): fold the four, keep one `updateAiModel`, prove the file. No new test authorship beyond the fold, no product refactor, no coverage-threshold machinery — however small.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): union — does the file contain all six describes with no duplicate `updateAiModel` and no lost assertion? green — does the file pass under vitest, and the full suite hold-or-explain? clean — is the diff exactly 1 test file + worklogs?
- Per-PR blocks table quoted + keeper choice quoted + file-level green quoted + full-suite quoted-or-UNRUN + diff `--stat` ceiling proof + $0.000000 USD; no vacuous pass (an unreread head, a pasted-but-unrun block, or a full-suite silence read as green evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-137 | Report: docs/worklogs/SG-137_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~900s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S=2100`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
