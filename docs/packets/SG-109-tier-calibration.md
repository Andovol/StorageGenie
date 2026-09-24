# SG-109 — Tier calibration on live dates: measure, verdict per category, change only with evidence ($0, opencode, high)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: high

**Context and standing lines.** D143 L3 Arc B slice 3 of 3 (engine GREEN 98 → dashboard GREEN 98 → calibration; D150 run-to-completion — no per-slice words). D143 calibration scope: tier windows are DECLARED UNCALIBRATED (`G-A9`; food/medicine/cosmetics shipped profiles vs household/documents declared values, `expiry_tracker.py:111-122` lineage) — THIS slice measures the live household distributions and changes ONLY what evidence supports. Live hypothesis from SG-108 (re-verify, never inherit): 6 assets, 0 accepted-expiry rows, `uncategorized = 6` — i.e. the expected outcome is NO window change with the calibration method + recompute query recorded. A predicted no-change does NOT make this vacuous: the live captures are real measurements, every per-category verdict cites a number, and any change carries fail-then-pass proof. NO sender/scheduler/dashboard/backend-refactor work (all out of scope); NO fixture authorship for tuning (calibrating on invented dates is forbidden — real rows only); NO production writes of any kind. $0 — read-only GETs + offline tests; a metered call is a STOP-and-report. **Authoring date (metadata, never a gate):** 2026-09-24. Transport: the standard job_spawn lane. Contract: recorded `0.33.0` == published (`b232b84`; D129 adoption, G-L1 clean 2026-09-24); echo verbatim + source path.
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit**. If you believe a dispatch is needed, STOP and report it.
**Standing lines:** calibration ONLY. `docs/worklogs` + (ONLY on the change path) `backend/app/plugins/expiry_tracker.py` window values + `backend/tests/test_sg107_expiry_engine.py` boundary updates — NOTHING else (no route/engine-shape/dashboard hunks; no migration — window values are data, never schema; `docker compose config` FORBIDDEN). Refresh rides the change path ONLY (no served-code change → no rebuild, no recreate — D145 triggers on served-code change, and a docs-only outcome changes none; state which path executed).
**Money posture:** $0.000000 actual vs $0 bound — no metered call exists on any path.
**Guards invoked (0.33.0 — Architect copies these to the rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-08` · `PG-EV-09` · `PG-SC-05` · `PG-SC-07` · `PG-SC-08` · `PG-SC-09` · `PG-IC-01` · `PG-IC-03` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` · `PG-PR-06`.

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

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint, 600s build+recreate+verify (change path only), 1500s early-close, 2100s overall. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING. "STOP and report" is satisfied ONLY by the
> `BLOCKED:` commit path, never by disclosure alone (`PG-EV-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none live** (read-only GETs only — a write of any kind is a STOP). **Restart: none on the no-change path; exactly ONE backend recreate on the change path** (D145 — served-code change only). **Deploy: change path only** (`PG-PR-04` — code becomes live by rebuild+recreate; no-change path touches no served code).

## G1 — live measurement (real rows only; `PG-EV-08`, `PG-SC-08`)

- Read-only captures, quoted raw: every household id; per household `GET /v1/plugins/expiry-tracker/status` (full body) + `GET /v1/analytics/summary` (`categories` + `expiry` blocks). The comparison baseline in the same slice (`PG-SC-08`): the CURRENT windows read live from `CATEGORIES` (assert equals food 1/7/30 · medicine 1/3/14 · cosmetics 7/30/90 · household 30 · documents 30+60 — the SG-107 pin test already proves this; quote its pass, do not re-prove).
- Per-category verdict, each citing a MEASURED number (resolved live rows in that category, their `days_remaining` spread, and what the current windows do to them): KEEP (evidence supports current) or CHANGE (evidence contradicts current — allowed ONLY on measured rows, never on invented ones). Zero resolved rows in a category is itself the verdict input: windows stay provisional for lack of evidence, stated as such — never tuned to fit nothing (`PG-SC-09` inverse stated upfront: a change with no measured rows behind it is the defect).
- `PG-SC-07`: the smallest population that reaches "no evidence" is named (today: the whole live catalog) and it IS reachable today (measured above) — the no-change path returns KEEP-provisional with the revisit rule, never an error and never a fallback number.

## G2 — change path (executes ONLY if a G1 verdict is CHANGE; precedence: G1 measurement wins over any urge to tune, `PG-IC-03`)

- Edit ONLY the contradicting category's `tier_defaults` values in `backend/app/plugins/expiry_tracker.py` (data, minimal, root-cause-cited per verdict); update the SG-107 boundary table expectations for that category + the declared-data pin test; fail-then-pass BOTH runs committed raw (`PG-EV-09`, seen-to-fail in-run `PG-EV-01`); full backend suite green modulo the 2 known decoder env reds (stash-proved on the slice — quote the proof), ruff clean, mypy delta 0, secret gate 0 real over changed files (quote the grep).
- Rebuild + exactly ONE recreate + verify (image id differs; health x6; gate 301/401; counts delta 0; engine route 200; NO press, NO writes). Actual-versus-budget per leg with units (`PG-PR-06`).
- If NO verdict is CHANGE, G2 is skipped ENTIRELY — state the skip with the G1 numbers that forced it (a skipped gate with its reason is not a vacuous pass).

## G3 — calibration record + worklog/report (unconditional per `CO-57`)

- The record (committed in `docs/worklogs/SG-109_calibration.md`, quoted in the report): per-category verdict + numbers; the RECOMPUTE QUERY that derives the next calibration (`GET /status` per household + the resolved-rows-per-category count — name it, `G-A3`: a volatile count never lives in prose, the query does); the REVISIT RULE (re-calibrate when any category holds ≥5 resolved live rows — uncalibrated threshold, stated as such); which path executed (change/no-change) and why.
- `{{WORKLOG_DIR}}/SG-109.log`, `SG-109_report.md`, `SG-109_verify.log` (raw outputs + every gate + live captures + EITHER both fail-then-pass runs OR the numbered skip). First token `SG-109`; elapsed-versus-budget per leg with units; MODEL + effort from process arguments; spend (**real $** $0.000000); contract echo + source path; three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `docs/worklogs` + (change path only) plugin window values + SG-107 boundary test updates — NOTHING else (no engine-shape/route/dashboard/migration hunks; `docker compose config` FORBIDDEN). Ordered paths committable (re-verify `.gitignore` before commit, `PG-SC-10`).
- Cross-product (`PG-IC-01`): no criterion demands engine-shape changes, new routes, dashboard hunks, migration, press, sender, or any metered call — no cell collides; stated so the check exists on paper. Reads include pytest/TestClient + host read-only GETs + (change path only) the authorized image build and ONE recreate; pulling/running any OTHER image or launching unnamed runtimes counts as execution — not authorised.
- Privacy: identifiers TEXT only; host `.env` never printed, never read into any artifact (`PG-SC-05` by rule, literal grep-gate quoted).
- No fixed dates except this header's authoring-date metadata; live `as_of` reads the clock at execution (`PG-IC-07`).
- STATE/AGENTS/packet dirs: untouched (state pushes buffer until the wake).

## Acceptance criteria

- Live captures raw per household with the current-window baseline beside them; per-category KEEP/CHANGE verdicts each citing measured numbers; change path (if taken) proven fail-then-pass with suite/gates green and served refresh verified; no-change path states the numbered skip + commits the calibration record with recompute query + revisit rule; $0; production untouched; no vacuous pass.
- Question each criterion answers (`PG-SC-09`): measurement — what do the live rows actually look like against current windows? change — did any measured row contradict its window? record — can the next calibration run without re-deriving the method?

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Spend **real $** $0.000000. Actual-versus-budget per leg with units.
- **Receipt note on the notes ref (M20-corrected block):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Add the note on the work HEAD (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-109 | Report: docs/worklogs/SG-109_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Then PUSH the notes ref (300s bound): `git push origin refs/notes/storagegenie-coder-reports`. Then verify against the FETCHED ref: fetch the refspec explicitly into a MAPPED local name (a default fetch never carries notes; a bare refspec fetch rewrites only FETCH_HEAD — map it), `git notes --ref=… show <WORK_HEAD>`, and PASTE the executed output verbatim — **a receipt subsection with no pasted `show` output means the step was not executed: say so loudly instead of writing it as done.** Existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL. Dual-annotate the final tip too (note-anchor inoculation, SG-092 precedent).
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint · 600s build+recreate+verify (change path only) · 1500s early-close · 2100s overall; REAL metered $0.000000 (zero calls); actual-versus-budget per leg with units.
