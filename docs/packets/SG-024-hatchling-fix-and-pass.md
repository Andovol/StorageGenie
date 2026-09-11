# SG-024 — Hatchling fix, rebuild, ISS-1 re-proof, remap, up, UI, restart (opencode, medium)

**Dispatch params for the new runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Stage:** D12 manual compose pass continued (L2 single slice, one retry) under D32 — fixes SG-023's deterministic G2 STOP, then completes the pass. This slice's approval IS D32. SG-023 history (not re-litigated): G1 green, builder route holds, apt layer proved, Dockerfile:7 `pip install --no-cache-dir --no-build-isolation --no-deps -e .` fails with `BackendUnavailable: Cannot import 'hatchling.build'` (exit 2, identical over 2 attempts); `pyproject.toml:51-52` declares hatchling, `requirements.lock` (uv pip compile) has no hatchling entry. Fix route ordered below is LOCK-FIRST, Dockerfile pre-install second — `PG-IC-03`: lock wins wherever compilable; the fallback runs only on quoted compile-impossible evidence, never as a shortcut. Bounds carried: D12 + D20 (`8003`) + `BUILDX_CONFIG` project-local route. Prior art: SG-022 lane proof, SG-023 partial (G-structure reused, README `:8000` count corrected to 12 lines `:40,104,106,109,110,117,125,126,127,129,138,140`).
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; decoder legs are proved HERE (this pass owns ISS-1 — no further carry).

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.** (Owner standing requirement: the report quotes model provenance after EVERY slice.)

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, and each leg below names
> the bound its own work needs. **A command producing no observable progress within its bound is killed and reported.**
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: live mounts, zero catalog writes. Restart: own backend container only (allowlisted `restart: unless-stopped`).** Bounds: `docker compose build/run/up/exec/restart` against THIS project's compose file only; no `docker volume/server` inspection beyond the probe (report a denial, don't route around); no catalog writes (temp DBs only); the hatchling fix below + D20 remap are the ONLY authorized product changes; no `.env` content changes (presence only, `CO-44`). Test rows live and die in temp databases (`PG-EV-06`, `PG-PR-10`). Transport kill real (`RUN_BUDGET_S=2100`): at 1800 s elapsed STOP starting new work, close out, publish receipt — partial WITH receipt is a success. Report elapsed per leg. Resolve actual binaries first (`venv/bin/`, `docker`), never assume host PATH.

## Why this exists

SG-023 left exactly one defect between the tree and a green pass: the room builds our package without hatchling in it. Everything else is proved (rootless docker, free `8003`/`5173`, builder route, apt layer, clean tree). Fix the one line-item, rebuild, prove decoders in-image, apply the carried remap, bring the stack up and prove it serves and recovers. Starting premises (verify — `PG-IC-09`): tree clean (SG-023 left it clean); `.cache/buildx` exists with the `.gitignore` entry (adopt, don't duplicate); compose still `8000:8000`, `VITE_API_BASE=http://localhost:8000`, README 12 `:8000` lines (all as-handed per SG-023 — carry each now with live proof behind it).

## G1 — re-verify the gates (report only; moved facts get rechecked, nothing assumed)

- `git status --porcelain` quoted (clean expected — any dirt is a STOP before all other goals, quoted).
- `docker info` alive under rootless + `docker buildx ls` selection quoted (route held per SG-023 — re-prove, never inherit).
- Listener recheck on `8000`/`8001`/`8003`/`5173` (candidate, not reservation — `PG-SC-07`): `8003`/`5173` foreign-occupied is a STOP, no rebind. `8000`/`8001` foreign is expected, never touched.
- `docker compose config` valid as-handed.

## G2 — hatchling fix, LOCK-FIRST (only if G1 passes)

- FIRST: add hatchling to the locked set (`uv pip compile` or the repo's own lock command — resolve, don't assume; bound 300 s). Constraint on the diff: the lock change must be HATCHLING-SCOPED (added pins only) — quote the diff; a reshuffled lock (version churn beyond hatchling) is a STOP with the diff quoted, never a quiet accept. If no compile tooling exists in reach or compilation is impossible without violating the ceiling, quote that evidence and take the fallback ONCE — the fallback never runs as a shortcut (`PG-IC-03`).
- FALLBACK (only on the quoted evidence above): one Dockerfile line before step 7 pre-installing hatchling (`--no-cache-dir`, pinned to the `pyproject.toml` requirement), quoted. No other Dockerfile redesign.
- Rebuild: `docker compose build backend` (bound 1500 s). Step 7 green is the criterion — quote it. Any OTHER failing layer is a STOP with the layer quoted (new defect, new destination).

## G3 — ISS-1 re-proof in the image (only if G2 built green; no ports, no live writes)

- `docker compose run --rm --no-deps backend venv/bin/python -m pytest -q tests/test_signals.py` (resolve in-image path, don't assume): the two decoder nodes go GREEN —
  `test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier` and
  `test_ocr_has_text_boxes_and_mean_confidence`. Quote both. Then the full backend suite in-image: green except NOTHING (no sandbox excuse — any non-decoder red is a defect finding with a destination).
- mypy not run (state the reason if no code changed beyond lock/Dockerfile/remap — say so, don't silently omit).

## G4 — remap, up, health, suites, UI, restart (only if G1 shows 8003 + 5173 free; 8000 + 8001 foreign expected)

- D20 remap (authorized product change): backend publish `8000:8000`→`8003:8000`, `VITE_API_BASE`→`http://localhost:8003` (compose env + the 12 README runbook `:8000` lines), then `docker compose config` proves validity. Pre-bind listener recheck immediately before `up`.
- `docker compose up -d --build` (or up since G2 built — your call): `GET http://localhost:8003/v1/health` via curl returns the expected JSON (anything but our backend answering IS the collision signal — STOP with evidence quoted). Backend suite via `compose exec`; frontend `npm run build`-clean OR dev-server HTML shell with the app root via curl (prove served bytes, never a log line); `docker compose restart backend` → healthy within healthcheck retries (quote recovery).
- No catalog writes in any leg; any write need is a STOP.

## G5 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-024.log` and `{{WORKLOG_DIR}}/SG-024_report.md`, first token `SG-024`, every output path named, three UNCLEAR lines, elapsed-versus-budget PER LEG with units. Model + effort provenance from process arguments — the MODEL line is an owner standing requirement, quoted every slice. Live-state ledger: what runs now, what proved per goal, every stop with evidence, exact remaining delta if any.

## G6 — Receipt note on the notes ref (proven shape, unchanged obligation)

- Push the work to `automation`, worktree clean (`CO-55`; runner proves P1/P2/P6 itself). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`.
- Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-024 | Report: docs/worklogs/SG-024_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`). Verify locally with `show <WORK_HEAD>` and QUOTE the note (two straight slices shipped placeholders — this time the executed output, not the command shape).
- Existing-note refusal is a STOP (replay case — never force-replace, `CO-97`). Final result line must read `note=yes`; zero-exit with `note=no` is a FAIL.

## Constraints

- Scope ceiling: the hatchling fix (lock-scoped, or the one fallback line) + D20 remap (compose publish, `VITE_API_BASE`, 12 README lines) + `docs/worklogs` + G6 note. `README.md` corrections beyond the remap only where live behavior contradicts a line (quote each). Builder-state contents never committed/force-added (`PG-SC-10`). Anything else is a STOP with evidence. STOP beats retry itch (`PG-IC-03`) — one L2 retry covers transients only.
- Cross-product (`PG-IC-01`): G2 needs only lock tooling/Dockerfile; G3 only the built image; G4 only free ports + `.env` presence. Recorded once.
- Secrets: `.env` presence only, `CO-44`. Privileged-denial (`PG-PR-03`): report exact text, never route around; no `sudo`/socket/chmod.
- Test scope: gates name what they checked with counts+elapsed; silent gates FAIL.
- Budget (`PG-PR-06`): 120s probes, 300s lock leg, 1500s build, 600s suite legs, 1800 s early-close, 2100s overall — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): verify before asserting; no new checklists. No Coder-side SSH (key absent in confinement).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first).
- G2: lock diff quoted and hatchling-scoped (or fallback evidence + one line quoted); step-7 green quoted; any other red layer = STOP.
- G3: both decoder nodes green IN-IMAGE quoted; full suite green-except-nothing or defect findings named.
- G4 (only if 8003/5173 free): remap diff + `config` valid, pre-bind recheck, `:8003` health JSON, exec suites, UI bytes, restart recovery — all quoted. Occupied = STOP, no rebind.
- MODEL + effort provenance quoted (owner rule). Live-state ledger complete. No vacuous pass.
- Worklog + report committed; notes ref carries `Dispatch-ID: SG-024` + `Report:`, quoted executed output, result `note=yes`.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments.

## Budget

120s probes, 300s lock, 1500s build, 600s suites, 1800 s early-close, 2100s overall.
