# SG-091 — SG-088 failure probe: read-only diagnosis of the 221s exit-1 with zero commits and dirty tree (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** SG-088 (derived registry, D107 slice 4) dispatched under the D107 L3 grant; the unit failed with `result=no_receipt exit=1`, and the host's own negative receipt (fetched from the notes ref, verified by the Architect) states: `utc=2026-09-21T17:46:49Z coder=opencode exit=1 head=dd2bb9c note=no moved=no rewrite=no dirty=yes elapsed=221s budget=2100s`, i.e. the Coder ran ~221s, committed NOTHING, and left the tree DIRTY. No positive receipt exists. The dirt gate will treat SG-088's debris as attributable (last run, no receipt) and quarantine it — confirm that classification, do not pre-empt it. `SG-088 --force` is CONDITIONAL on this probe's GO. THIS slice changes nothing: it reads the failure's traces and returns GO (transient-shaped, re-fire) or NO-GO (persistent root named + fix home named). **Authoring date (metadata, never a gate):** 2026-09-21. Transport: the standard job_spawn lane. Contract: recorded `0.28.2` == published (`b495b59`); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** READ-ONLY diagnosis (enumerated ceiling below). No file writes outside `docs/worklogs`; no provider calls; no `--force`, no re-trigger of any unit, no quarantine invocation, no restart, no deploy (`PG-PR-04` — nothing becomes live).
**Money posture:** $0.00 by construction — no metered call exists on any path. No bound to multiply out (`PG-IC-04` stated as not firing).
**Guards invoked (0.28.2 — Architect copies these to the rating row):** `PG-EV-02` · `PG-EV-05` · `PG-SC-05` · `PG-SC-09` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-04` (NOTHING live stated).

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. Deploy: none.**

## G0 — packet + base resolution on the host (proves the slice COULD run)

- Confirm `docs/packets/SG-088-*.md` resolves to exactly one file on the host checkout; quote its dispatch-params head. Confirm `dd2bb9c` reachability in the host history (reachability form — ancestor check, never `HEAD ==`, `PG-IC-07`).

## G1 — unit journal (what killed it?)

- Bounded read: `journalctl --no-pager -u dispatch-storagegenie@SG-088.service` tail (state the bound; 120s). Quote the tail raw, or quote the exact denial if refused (reported as `unanswered`, never routed around). State whether any `run_coder=fail reason=` line exists for the SG-088 invocation, with the raw count.

## G2 — CLI smoke + debris inventory (what runs, what was left)

- `opencode --version` (bounded 120s); quote raw output + exit.
- READ-ONLY debris inventory: `git status --porcelain` on the host checkout (quote raw) + `ls` of any untracked paths named. Touch nothing, move nothing, delete nothing — the dispatch dirt gate owns attributable debris, not this probe. Classify each entry (scratch log, partial work, unknown) without opening file contents beyond what `ls`/`file` shows (contents are the failed slice's, not this probe's, to interpret).

## G3 — launcher artifact (what exactly ran?)

- `output/dispatch/SG-088.launcher.sh` (path hypothesis — verify on target): quote the exact `opencode` argv. Quote the lane log's provider/model banner + its LAST line. Both readable or the exact refusal quoted.

## G4 — verdict GO vs NO-GO (the slice's only product)

- GO iff: packet resolved, CLI starts, journal shows a transient-shaped death (upstream/provider-side error or equivalent) with no runner-side fault, and the debris is scratch-class. Quote the discriminating lines. NO-GO otherwise: name the persistent root + which future slice owns the fix.
- Commit `docs/worklogs/SG-091_report.md` (+ `SG-091.log`) so the receipt can publish positively; if forbidden, the negative-receipt path is stated, not silent.

## Constraints

- **Scope ceiling:** host packet file (read) · unit journal (read) · `opencode` smoke (run, bounded) · host status/ls inventory (read-only) · run dir launcher/log (read) · `docs/worklogs` (report + log ONLY). **Anything else is a STOP** — no quarantine moves, no debris deletion, no unit restarts, no re-triggers, no pipeline runs, no production contact.
- Cross-product (`PG-IC-01`): no criterion writes outside worklogs, calls no provider, restarts nothing, moves no debris; reads include the journal + launcher + status only — no container image pull/run; G4's verdict is covered by the same read-only rule.
- A count or absence premise carries the RAW command output, never a paraphrase.
- No fixed dates except this header's authoring-date metadata; time reads the live clock (`PG-IC-07`). No commit named, no `HEAD ==` precondition.
- Simplicity (`G-A7`): four reads + inventory + verdict + worklog; no fix attempts (a fix is its own slice).

## Acceptance criteria

- Packet resolution quoted (exactly-one) + reachability verdict (quoted).
- Journal tail quoted raw (or exact denial with `unanswered`); `run_coder=fail` presence/absence with raw count.
- CLI smoke raw output quoted; launcher argv + banner + last line quoted (or exact refusals quoted).
- Debris inventory quoted raw with scratch/unknown classification; NOTHING moved or deleted (prove by re-listing status at the end, identical).
- GO/NO-GO verdict carried by quoted evidence; fix home named on NO-GO. Question each criterion answers (`PG-SC-09`): G0 — could the slice run at all? G1 — what killed it? G2 — does the Coder start, and what was left behind? G3 — what exactly ran? G4 — re-fire or fix-first?
- Worklog committed (or negative path stated); $0.000000; no vacuous pass.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **$0.000000 actual** (zero provider calls — containment per `PG-PR-04` stated: nothing live exists to contain).
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-091 | Report: docs/worklogs/SG-091_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. (A zero-commit probe takes the negative-receipt path — stated in G4, never silent.)
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s overall; **$0.00** — no metered call exists on any path in this slice.
