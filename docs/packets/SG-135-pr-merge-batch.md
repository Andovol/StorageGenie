# SG-135 — Land the 11 audited winners: ordered merges, journal union, tests, no serve

**Settings travel on the trigger** (`SG-135 coder=opencode effort=high`, D6) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D6-authorized merge batch (owner quote "D6 - ok", `G-L7` audit-and-merge): SG-133 (98) + SG-134 (98) audited all 24 open PRs; the 7 verdict-closes are already closed from the workstation (`#5,#19,#21,#22,#23,#25,#30`); THIS slice lands the 11 MERGE verdicts as code. Land EXACTLY these 11 heads (re-verify each `refs/pull/N/head` on the target; a moved head is a STOP for that PR — land the rest, report it): `#15` 84dc691 · `#17` 3269107 · `#20` aea591d · `#26` 3dc8349 · `#2` 217ee06 · `#28` 0cd1c35 · `#29` 431d323 · `#31` 3872595 · `#27` 9b86ce3 · `#24` 0211c8a · `#18` 6e624c2. Method: `git merge --no-ff` of each head in the order below (bot authorship preserved; GitHub marks each PR merged on landing — never `gh pr merge`, never close by hand). The ONLY expected conflicts are `.jules/bolt.md` journal appends (8 appenders — resolve by UNION of lines, every line kept, duplicates dropped once) — **a third conflict region anywhere else is a STOP: commit landed merges, report, receipt (`PG-IC-08`: expected 11 merges, journal-only conflicts; anything else differs either way).** The rewrites (`#16`, `#11–#14` fold, `#4`-minus-artifact) ride SG-136/137/138 — never folded in here. **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-134's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** MERGE-ONLY slice. Writes: the 11 merge commits + resolutions, affected-test additions NONE (no new tests — the PRs carry their own), `docs/worklogs` (3 files). NOTHING else: no rebuild, no recreate, no migration (prove empty diff over `models/`+`alembic/` at end — a needed migration is a STOP), no serving (`PG-PR-04`: landed code is UNSERVED until its own rider word; the running image is untouched and no served-leg proof is owed here), no closes, no rebases of unlanded branches. `gh` is unauthenticated on this host — never touch it; all reads/writes are git-native. Never copy secrets (`CO-100`).
**Money posture:** REAL metered $0.000000 USD bound (no USD-metered call exists on any path). `PG-PR-06` stated upfront; actual-versus-budget per leg with units in the report.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-07` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-08` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` · `PG-PR-06`.

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

**DATABASE: none (no migration — empty `models/`+`alembic/` diff quoted). Restart: none. Deploy: none.**

## G0 — verify heads + land in order (stated, not solved)

- Re-verify the 11 head SHAs above against `refs/pull/N/head` on the target (`PG-IC-09`); a moved head stops THAT PR only.
- Land in this order, cheapest-and-most-isolated first (each: fetch head to `refs/audit/pr/N`, `git merge --no-ff`, resolve ONLY journal-union conflicts, commit): `#15` (evidence query) → `#17` (asset filters) → `#20` (dedup) → `#26` (ProductCard) → `#2` (chat init) → `#28` → `#29` (new test files) → `#31` (health logger) → `#27` (taxonomy winner) → `#24` (analytics winner) → `#18` (chat+planning).
- Landed-content proof per PR (`PG-SC-12`): the merged tree contains the head's hunks — quote the post-merge grep of each PR's signature lines (e.g. `#15`'s `ev_map`, `#27`'s `_score_candidates`, `#31`'s `logger.warning`), derived from the head diff, never from memory.
- At 1500s elapsed: stop starting new merges, commit landed ones, run G1 on what landed, write the report, publish the receipt — **a partial slice WITH a receipt is a success**; report elapsed at each merge transition. Order above already puts the most droppable last (`#18` largest).

## G1 — prove it (targeted per landing + one full suite)

- Per merge: run the test FILE(S) the PR's area owns (derive by grep — `CO-101`: every test file asserting on a symbol this merge touches is RUN, each named with its result; my expectation: `#31`→`test_health.py`, `#27`→taxonomy tests, `#24`→analytics tests, `#20`→dedup tests, `#15/#17`→asset/evidence tests, `#18`→chat+planning tests, `#2`→`python -c` import of the package, `#26/#28/#29`→their vitest files IF runnable via `npx vitest run <file>` — if the host cannot run node tests, report that file UNANSWERED, never a pass, and the merge still stands on the audit read).
- End state: ONE full backend suite green-except-base-proved-reds (600s bound; reds stash-reproved on bare BASE); ruff clean; mypy quoted (delta vs BASE stated, never assumed zero). Empty `models/`+`alembic/` diff quoted.
- `$0.000000 USD; no vacuous pass (an unrun suite, a skipped unanswered file read as green, or a merge without its signature grep evidences nothing).

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-135.log`, `SG-135_report.md`, `SG-135_verify.log` (per-PR head + merge commit + signature grep + targeted results, suite/mypy/ruff, empty-migration proof, unlanded remainder if partial). First token `SG-135`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the merge commits (+ journal-union resolutions only) + the 3 worklog files. **Any other write — rewrites of `#16/#11–#14/#4`, closes, rebuild/recreate, migration files, new tests — is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs fetches + merges + union resolutions (modify-versus-call: merges MODIFY precisely the 11 audited heads; touching any other branch is a STOP); G1 needs targeted + full suite (600s class bound for suites); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 600s suite / 2400s overall), never one blanket timeout. Reads INCLUDE test runs + `git` network reads; pulling any container image or launching any runtime beyond the suite's own is NOT included and is a STOP. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): merge the audited winners in order, union the journal, prove with tests. No re-implementation, no benchmark harness, no serving.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): landed — does the tree contain all 11 heads' hunks (signature greps)? correct — do targeted + full suite hold with reds proved base-side? clean — is the migration surface empty and the only conflicts the journal union?
- 11-row table quoted from the commit (PR, head, merge commit, signature grep, targeted result) + full-suite/mypy/ruff quotes + empty `models/`+`alembic/` diff + $0.000000 USD; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-135 | Report: docs/worklogs/SG-135_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite · 2400s overall; expected ~1800s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
