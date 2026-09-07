# SG-011 — Queued findings: mypy instance + alembic-head literal (Codex High)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: codex
effort: high

> Facts below are what I believe from the tree that carries this packet. **They are EXPECTED conditions,
> not established truth. Verify each before building on it; a difference is a finding, not an obstacle.**
> For any number, path or quoted line I hand you: if your figures differ from mine, investigate and
> explain — **do not bend your answer to match mine. Correcting me is worth more than agreeing with me.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** No migration, no service touch. Backend tests use `TestClient` + temp SQLite only, never the host database. The 35-minute transport kill is real (`RUN_BUDGET_S=2100`): the whole slice must finish inside 2100s — report elapsed against it.

## Why this exists

Two audit findings queued with this slice named as their destination. Both are small, ordinary product work — this slice is also the first self-run through the repointed transport, so the blast radius stays tiny by construction.

1. SG-007 report: `backend/app/services/evidence_service.py:95` carries a mypy assignment-type error. I believe the line reads `image = ImageOps.exif_transpose(image)` inside `_decode_image`, where the name bound by `Image.open(...)` (a file-backed image) is rebound to the transposed `Image.Image` — verify the exact error text with mypy before fixing, and quote it.
2. SG-008 audit: `backend/app/api/v1/exports.py:17` pins `ALEMBIC_HEAD = "0201cf10c56c"` as a literal that the manifest echoes as `db_revision`. I believe `backend/alembic/versions/` carries exactly one revision file — enumerate that directory, verify, and report every file found. A literal that the next migration must remember to update is how a manifest starts lying.

## G1 — mypy instance gone, count not grown (`PG-EV-01`)

- Reproduce first: run mypy over the file (or repo) with output quoted, showing the `:95` instance. Both runs (before/after) go in the committed log (`PG-EV-09`).
- Fix inside `backend/app/services/evidence_service.py` only — annotation, new variable, or narrow cast, your call. No runtime-behaviour change: prove it by running the evidence test module(s) green before and after with file + test counts quoted.
- The repo-wide mypy count must not grow: quote the before/after totals. mypy stays advisory — a pre-existing error elsewhere is reported file+line as a finding, never fixed by drive-by.

## G2 — manifest revision tracks the migration head by construction or by test (`PG-SC-02`)

- Trace the read-back route: `ALEMBIC_HEAD` → `db_revision` in the export body (`exports.py:42`). Your change must cover that route.
- Your design call: derive the head at runtime (alembic is already a dependency — no new runtime dependency permitted) or pin the literal with a test that fails when the two diverge. Either way the slice ends with the divergence class closed, not merely documented.
- Prove it (`PG-EV-01` control): perturb the value in a scratch copy — never committed — and show the new mechanism catching it (failing test or divergent output quoted); then remove the scratch. A gate never seen to fail is not a gate.
- No migration is added in this slice. If you find the tree needs one, STOP that leg and report it as the destination for the next slice.

## G3 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-011.log` and `{{WORKLOG_DIR}}/SG-011_report.md`, first token `SG-011`, every output path named in the report committed, three UNCLEAR lines at the end.

## G4 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation` and leave the worktree clean (`CO-55`): the runner proves HEAD movement without rewrite (P1/P2) and a clean tree (P6) itself. No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}` — the legacy publisher is dead.
- Attach the receipt note to the work HEAD LAST, with no commit after it (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-011 | Report: docs/worklogs/SG-011_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — the first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`; the dispatch gate greps the ID, the runner parses the path, P3/P5). Then verify locally with `git notes --ref=refs/notes/storagegenie-coder-reports show <WORK_HEAD>` and quote the note. The RUNNER pushes the notes ref and reads it back from the remote — a note existing only locally is not a receipt.
- If `git notes add` refuses because a note already exists for that commit, STOP — a receipted commit running again is the replay case; never force-replace the note (`CO-97`).
- Verify the artifact, not the command: after the run the dispatch result line must report `note=yes` for this ID. A zero-exit run with `note=no` is a FAIL.

## Constraints

- Scope ceiling: `backend/app/services/evidence_service.py` + `backend/app/api/v1/exports.py` + `backend/tests` files (add/adjust) + `docs/worklogs` files + the G4 note mechanism. No migrations, no `.env`/restart/secrets/infra, no new runtime dependency. Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires a migration, a new dependency, or a production write. Recorded here once, not per criterion.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: the evidence + export test modules at minimum; the full backend suite if it fits its bound. Every gate names the files it checked and its counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 300s for suite legs, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the note return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- mypy `:95` instance gone with before/after quoted; repo-wide mypy count not grown; evidence tests green before and after with counts quoted.
- `db_revision` tracks the migration head by mechanism or by failing test, with the catch demonstrated on a scratch perturbation and quoted.
- `docs/worklogs/SG-011.log` and `docs/worklogs/SG-011_report.md` committed; every output path in the report committed.
- the notes ref carries the `Dispatch-ID: SG-011` + `Report:` note on the work HEAD; note quoted; dispatch result line `note=yes`.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as configured on the host, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 300s suite legs, 2100s overall (`RUN_BUDGET_S=2100` in the dispatch conf — the kill is real, finish inside it).
