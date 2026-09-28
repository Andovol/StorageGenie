# SG-134 — Outside-PR audit, tests + cleanup: 10 diffs read as Coder reports, verdicts, no merges

**Settings travel on the trigger** (`SG-134 coder=opencode effort=high`, D5) — this packet carries no `coder:` / `model:` / `effort:` line; such a line in the first 40 lines is refused `packet_settings_retired` (D302, contract 0.40.0).

**Context and standing lines.** D5-authorized slice (owner quote "D5 - yes, do them all", `G-L7`): audit the tests + cleanup outside PRs — NEVER merge as they stand; each gets a verdict (merge / rewrite-as-slice / close) + one-line reason, and merges return for the owner's yes afterwards. SG-133 (rated 98) audited the 14 perf PRs; THIS slice takes the remaining 10 (Architect-measured 2026-09-28 via `gh pr view`, all `base=automation` — RE-VERIFY each number/branch/stat on the target; a difference is a finding): tests `#11` +75/-1 f1 · `#12` +95/-1 f1 · `#13` +55/-1 f1 · `#14` +210/-1 f1 · `#28` +93/-1 f1 · `#29` +90/-1 f1 — all six additive single-file frontend unit tests; cleanup `#2` +7/-7 f1 (chat-init re-exports) · `#4` +167/-66 f8 (HouseholdSelector extraction, the largest) · `#30` +0/-0 f0 (**empty diff** — verify empty on the target; an empty diff is a CLOSE recommendation with the proof quoted, never a pass) · `#31` +8/-3 f2 (health-check logger — touches `GET /v1/health`, the `G-T9` proof route: audit for status/body-shape preservation + no secret in the log line). Overlap expectation (Coder confirms or differs — a handed set is a fact too, DISPATCH.md §2a): test PRs are independent single files (no overlap expected) · `#4` may collide with catalog/shell files other PRs touch (name any hit) · `#30` overlaps nothing. **Authoring date (metadata, never a gate):** 2026-09-28. Transport: the standard job_spawn lane. Contract: recorded `0.40.0` == published (`f26dbd3`, D4 adoption); host link from SG-133's echo (`0.40.0` from `/home/andrei/storagegenie-contract/VERSION`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** READ-ONLY audit. Writes: `docs/worklogs` (3 files: `SG-134.log`, `SG-134_report.md`, `SG-134_verify.log`) — and NOTHING else. No product-file write (prove by `git status` showing only the 3 worklog paths + empty diff over everything else), no merge, no close, no push to `automation` except the worklog commit + notes receipt, no suite run, no container exec, no live call. `gh` is UNAUTHENTICATED on this host (SG-133 F1 — do not retry auth, do not work around it): use the git-native path (`git ls-remote origin 'refs/pull/*'` → local `refs/audit/pr/N`, then `git diff <merge-base>...<head>`). Never copy `.env`, keys or credential stores anywhere (`CO-100`); no credential in any committed artifact.
**Guards invoked (0.40.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-10` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-SC-09`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 2400s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G0 — fetch + enumerate (reads only — stated, not solved)

- Per PR: resolve the head branch on the target, quote branch + merge-base + diffstat. My 10-number table above is the EXPECTATION — quote the measured difference either way, including any PR closed/retargeted since (`PG-IC-09`).
- Fetch the full diff per PR (`git diff <merge-base>...<head>`, bytes not rendering). For `#30`: quote the empty diffstat + empty diff as the CLOSE proof.

## G1 — audit each diff as a Coder report (`G-L7`, `AUDIT.md` lens)

- Test PRs (#11,#12,#13,#14,#28,#29): does the added test drive the REAL function (placebo read — a test asserting something real about the wrong path is a finding, not a pass), and does it touch only its own file (any product-file hunk in a "test-only" PR is scope creep — name it)?
- Cleanup PRs: `#2` re-export behaviour-preservation · `#4` extraction equivalence across its 8 files (callers updated, no behaviour drift) · `#31` health-shape preservation + log-line secret scan (assert the logged exception carries no credential/row bytes).
- Per-PR verdict MERGE (as-is) / REWRITE-AS-SLICE (idea sound, diff not — say what the slice must change) / CLOSE (one-line reason). A PR fixing a defect is also a lesson (`D336`): name the defect + why this project's own packets, tests and audit let it through.
- Overlap check across the 10 + against SG-133's merge order (same-file pairs that would serialize landings).
- Order of work, cheapest first, most droppable last: `#30,#2,#31,#13,#11,#29,#28,#12,#14,#4`. At 1500s elapsed: stop starting new PRs, commit finished audits, write the report, publish the receipt — **a partial slice WITH a receipt is a success**; report elapsed at each PR transition.

## G2 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-134.log`, `SG-134_report.md`, `SG-134_verify.log` (per-PR branch + merge-base + diffstat + verdict + reason + lesson-or-N/A, overlap note, `git status` proof of read-only). First token `SG-134`; elapsed-versus-budget per goal with units; MODEL + effort from process arguments; spend **real $** $0.000000 USD + zero metered calls; contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** WRITES — the 3 worklog files. **Any product-file write, merge, close, suite run, container exec, live call, or push beyond the worklog commit + notes receipt is a STOP.**
- Cross-product (`PG-IC-01`): G0 needs fetches + diffs (reads INCLUDE `git` network reads; `gh` auth is known-absent — retrying it or working around it is NOT included and is a STOP; launching any runtime or pulling any image is NOT included and is a STOP); G1 needs read-only audit (modify-versus-call: NOTHING is modified — the receipt push in G2 is the packet's own delivery path, stated here so the exclusion carries its exception); G2 needs the worklog commit + notes receipt. Per-command-class bounds (120s ordinary / 2400s overall), never one blanket timeout. No criterion demands what the ceiling forbids — stated so the check exists on paper.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`).
- Simplicity (`G-A7`): read each diff, judge it, tabulate. No re-implementation, no test runs, no refactor proposals beyond the verdict line each PR already requires.

## Acceptance criteria

- Question each criterion answers (`PG-SC-09`): per-PR — is this diff safe to merge as-is, and if not, what must the rewrite slice change? `#30` — is the diff provably empty? `#31` — does the health route keep its shape with nothing secret logged? overlap — does anything here serialize against SG-133's merge order?
- 10-row table quoted from the commit (PR, measured diffstat, verdict, reason, lesson-or-N/A) + overlap note + `git status` read-only proof + $0.000000 USD spend; no vacuous pass (an unfetched PR, an unread diff, a placebo test read as green, or a verdict without a quoted diff hunk evidences nothing).

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000 USD + zero metered calls. Actual-versus-budget per goal with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean except the 3 worklog files (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-134 | Report: docs/worklogs/SG-134_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 2400s overall; expected ~1200s (Architect's record, uncalibrated per `G-A9`; the lane enforces `RUN_BUDGET_S`); REAL metered $0.000000 USD + zero metered calls; actual-versus-budget per goal with units.
