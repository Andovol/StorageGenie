# SG-009 — Frontend verify/repair + lint unmasking (Codex High)

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
> to hide.

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: automation.** A packet naming a tree hash is wrong by the time it runs — the packet commit becomes the tip. **The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.**

**DATABASE: none. Restart: none.** No backend, no datastore, no service touch. Frontend `vitest` (jsdom) + `tsc` + eslint only. A dependency install (`npm ci`) is permitted once within its own bound (300s); if the registry is unreachable, that leg is reported as unanswered and the slice continues with the checked-in tree — never vendored by hand, never fetched by other means.

## Why this exists

`frontend/src` carries the Task 12–14 surface — `api/client.ts` (fetch wrapper with household injection + RFC9457 error parsing), `CatalogPage`, `AssetDetailPage`, `CapturePage`, `AssetForm`, `EvidenceGallery`, `ProvenanceBadge`, `useAssets` hook — with three test modules (`client.test.ts`, `AssetCard.test.tsx`, `ProvenanceBadge.test.tsx`) recorded at 3 files / 7 passing, but that figure is inherited, not re-verified (`PG-IC-09`: re-prove it here). The standing defect is `frontend/package.json:10`: `"lint": "eslint src --ext ts,tsx || true"` — a gate that cannot fail — and `eslint` is absent from `devDependencies`, so the mask may be load-bearing rather than historical (`TS-5`). Backend is proved through SG-008 (suite 23) and is out of scope: no backend file may change in this slice.

Answers to prior open items, so they are not rediscovered: run frontend gates with `./node_modules/.bin` (or `npx --no-install`) inside `frontend/`; the ARCHITECT/PACKET/DISPATCH/CLOSE/LEDGER/PRODUCTION contract files are absent on the host, so all needed context is embedded here; a non-fast-forward prefill resolves content-neutrally per G5, never force-push.

## G1 — Vitest suite, re-proved and repaired where broken

- Run the full frontend suite (`vitest run`) with output quoted: file count, test count, failures named. A zero-test collection or a fully-skipped run is a FAIL, not a pass. Vacuous-green (no tests found, all skipped) is declared loudly.
- Repair inside `frontend/src` only, and only what failing tests prove broken. Added tests (if any) fail first against the unmodified tree with both runs committed in the log (`PG-EV-09`).

## G2 — Typecheck clean

- `tsc --noEmit` (or the `tsc` leg of `npm run build`, without emitting) exits 0 with output quoted. Every error fixed is quoted before/after; `skipLibCheck` stays as-is, no new `// @ts-ignore` or `any` casts to silence the gate — a suppression is a finding, not a fix.

## G3 — Lint unmasking (`TS-5`)

- Add `eslint` (plus exactly the plugins/config the tree needs — choose flat `eslint.config.js` for eslint 9, record the choice) as pinned `devDependencies` via the lockfile (`package-lock.json` updated by the installer, never hand-edited). Drop the `|| true` mask so `npm run lint` fails when violations exist.
- Prove the unmasked gate is real (`PG-EV-01` control): introduce a temporary unused variable in a scratch copy — never committed — show eslint flagging it, then remove it. Quote both.
- `npm run lint` exits 0 on the final tree with output quoted. Auto-fixable violations may be fixed with `eslint --fix`; manual fixes are limited to unused imports/variables and formatting. Any structural violation ( 平 rule requiring redesign) is reported file+line as a finding for the next slice rather than redesigned here — but the mask stays dropped regardless: a failing lint that reports honestly beats a passing lint that cannot fail.
- If the registry is unreachable and eslint cannot be installed, STOP the G3 leg only: report it as unanswered with the exact error, leave `package.json` untouched, and name the next slice as its destination. G1/G2 still ship.

## G4 — Worklog and report (unconditional per `CO-57`)

- `{{WORKLOG_DIR}}/SG-009.log` and `{{WORKLOG_DIR}}/SG-009_report.md`, first token `SG-009`, every output path named in the report committed, three UNCLEAR lines at the end.

## G5 — Prefill the evidence ref, then auto-publish

- After WORK_HEAD is pushed to `automation`: `git push origin <WORK_HEAD>:refs/heads/storagegenie-evidence` (120s bound), then `git fetch origin refs/heads/storagegenie-evidence` and verify `git rev-parse origin/storagegenie-evidence` equals WORK_HEAD — quote both hashes. The publisher gates on this equality (`candidate_not_remote`); the prefill is what establishes it. If the push is non-fast-forward, merge content-neutrally and push the merge — never force-push (`CO-54`, as SG-005…SG-008 demonstrated).
- Only then invoke `{{RECEIPT_CMD}}` with (`SG-009`, header `contract_sync=refresh version=0.17.2`, report path, WORK_HEAD), unmodified. A repair need is a finding, never a local patch to the wrapper.
- A `candidate_not_remote` from the unmodified publisher AFTER the verified prefill is a STOP — commit `BLOCKED`, push, report. Never hand-move the ref by other means and never force-push outside the publisher (`CO-54`).
- Verify the artifact, not the command: the evidence ref carries a commit with the `Dispatch-ID: SG-009` trailer — quote its hash. A zero-exit publish with no such commit is a FAIL.

## Constraints

- Scope ceiling: `frontend/` (source, tests, config, lockfile via installer) + `docs/worklogs` files + the G5 prefill/publish mechanism. No backend, no migrations, no `.env`/restart/secrets/infra, no new runtime dependency (devDeps for lint only). Anything else is a STOP, not a stretch goal ("STOP and report" is not satisfiable by disclosure).
- Cross-product (`PG-IC-01`): every acceptance criterion below is satisfiable inside the ceiling — none requires the backend, a migration, or a production write.
- Secrets: never commit `.env`, tokens, or `auth.json` contents — redact per `CO-44`.
- Privileged-denial: a denied `sudo` or `docker` operation is reported as unanswered per the block above, not routed around.
- Stash: worktree ends clean per `CO-55`.
- Test scope: full frontend suite runs; every gate names the files it checked and its counts; a gate emitting no output is a FAIL, not a pass.
- Budget: 120s per ordinary command, 300s for the install + suite legs, 2100s overall — report actual-versus-budget with units.
- Simplicity: verify before repairing; write no new checklist (`G-A7`).
- No Coder-side SSH checks: the dispatch key is absent inside the confined run — host paths and the prefill/publish return codes are the verification. Do not require what the confinement forbids.

## Acceptance criteria

- `vitest run` green and non-vacuous (file + test counts quoted, zero silent skips); any repair fail-then-pass quoted.
- `tsc` typecheck exit 0 quoted, no new suppressions.
- `npm run lint` runs unmasked and exits 0 quoted, with the fire-control demonstrated; `package-lock.json` records the pinned eslint tree.
- `docs/worklogs/SG-009.log` and `docs/worklogs/SG-009_report.md` committed; every output path in the report committed.
- `storagegenie-evidence` carries the `Dispatch-ID: SG-009` receipt commit; hash quoted; prefill equality quoted before publish.
- No criterion passed vacuously.

## Report

- Work dir `/home/andrei/StorageGenie`, remote `git@github.com:Andovol/StorageGenie.git`, `BASE` = packet start HEAD, `WORK_HEAD` = work commit hash.
- State model/effort provenance per `CO-78` — never from a system-prompt identity line.

## Budget

120s ordinary, 300s install + suite legs, 2100s overall (`TIMEOUT_S=2100` in wrapper).
