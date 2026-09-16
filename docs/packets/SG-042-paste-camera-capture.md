# SG-042 — paste-to-add photos + mobile camera capture on the Capture screen (opencode, medium)

**Dispatch params for the runner (read from this committed packet; model is the CLI default and is omitted per policy):**
coder: opencode
effort: medium

**Context and standing lines.** Stage D60 (photo-first capture, L3) slice S1 of 3: S2 makes the name optional + photo-derived (needs a live-DB migration), S3 derives quantity/unit/type via AI (needs consent + key) — **both out of this slice; this slice stages photo bytes only and derives nothing.** Display-name-required stays exactly as-is (`AssetForm.tsx:56-59,101-108`). **Authoring date (metadata, never a gate):** 2026-09-16. Transport: the standard job_spawn lane. Contract 0.27.0 (receipt echoes it).
**Role guard (owner standard line):** you are the Coder, never the Architect — **never run the dispatch verb for any ID, never start or poll your own unit** (SG-027 run-1 lost its entire budget doing exactly that). If you believe a dispatch is needed, STOP and report it.
**Standing lines:** a "pre-existing failure" claim cites the base commit + base-run command and output, or it is a new finding with a destination; **no file under `backend/` is touched by this slice** (frontend-only; a needed backend change is a STOP); **no migration** (an alembic diff is a STOP); **AI stays OFF**: no provider calls, **$0 metered**; no new dependencies, no network (if `node_modules` is absent → STOP, do not `npm install` over the network); no frozen-prompt diff.
**Guards invoked (0.27.0 — Architect copies these to the rating row):** `PG-EV-01` gate-seen-failing · `PG-EV-02` artifact-exists · `PG-EV-05` property-not-command · `PG-EV-09` both-runs-committed · `PG-SC-05` exclude-by-rule · `PG-SC-10` no-ignored-commit · `PG-IC-01` cross-product · `PG-IC-07` no-fixed-dates · `PG-IC-09` premises-live. (`PG-EV-06`/`PG-EV-08`/`PG-DP-02..04` do not fire: no live writes, no delivery change, no entry point, no reported failure — new feature per `PG-DP-03`.)

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine, investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

> A denied privileged operation is never a signal to route around it. **A step you cannot complete without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a test that never invokes the function, a grep scoped so narrowly it could not have matched — say so loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata, never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout — 120s ordinary, 600s suite+lint+build. A command producing no observable progress within its bound is killed and reported. Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean. Report every issue and disagreement, including ones outside this slice's scope. End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.

**DATABASE: none. Restart: none. NETWORK: none.**

## Why this exists

The owner drives the live app and asks: add photos by pasting, and on mobile by taking a picture. Today the Capture screen (`frontend/src/routes/CapturePage.tsx:46-49` renders `AssetForm`) offers drag&drop + file-select only: the drop zone (`AssetForm.tsx:138-174`) handles `onDrop` (`:45-52`) into `addFiles` (`:30-43`), the file input is `type="file" multiple accept="image/*,.pdf"` (`:154-161`) — **no `onPaste` anywhere in the component (stated from grep, re-verify in-slice), no `capture` attribute anywhere in `frontend/src` (stated from grep, re-verify in-slice).** Pasted bytes currently go nowhere; phones get the generic file picker, not the camera.

## G1 — paste stages photos exactly like dropped files (`frontend/src/components/AssetForm.tsx`)

- A paste carrying image file(s) anywhere the capture screen can receive keyboard focus appends them to the staged preview list through the same path as dropped files: preview row shows name + size, SHA preview where computable, working remove button (`AssetForm.tsx:162-173` behaviour).
- **The focus-scope mechanism is delegated — decide and report:** name where the handler attaches (drop-zone element, form, or window with cleanup) and establish that a real paste event reaches it; the report states the choice and the evidence for it. A delegated decision missing its load-bearing fact is a delegated guess.
- Clipboard content with no image files (text-only paste) stages nothing, errors nothing, and changes no existing staged entry.
- Non-image image-mime edge (e.g. a pasted file the browser names `image.png`): staged as-is, never renamed — naming is S2's job. **No user-facing text may promise AI naming or derivation** (`PG-SC-02`: the slice's inventory says derivation does not happen).

## G2 — a take-a-photo control for mobile (same file)

- A visibly labeled photo control (e.g. "Take a photo") beside the existing select: `<input type="file" accept="image/*" capture="environment">`, single shot.
- The existing multi-file input (`AssetForm.tsx:154-161`) stays behaviour-identical — desktop flow unchanged, `.pdf` still accepted there, camera input image-only.
- Label and hint text stay plain; nothing promises analysis.

## G3 — tests: new `frontend/src/components/AssetForm.test.tsx`, FAIL-then-PASS both runs committed

- Render `AssetForm` directly (`householdId` + `onCreated` props — no router needed); mock `../api/client` by the committed pattern (`AssetDetailPage.test.tsx:7-14`, `vi.hoisted` + `vi.mock`).
- Criteria, each a named test: (a) a paste event carrying image file(s) stages them — preview rows show name + size and remove deletes one; (b) a text-only paste stages nothing and disturbs nothing; (c) the camera input renders with `capture="environment"` and an image-only accept; (d) submit with staged files still posts `display_name` + `evidence_ids` (mocked `uploadEvidence`).
- Full frontend suite green (`npm test` = `vitest run`), `npm run lint` clean, `npm run build` (tsc + vite) clean — so the §3 conditional derived-test-set block is NOT pasted. Pre-change run: the new tests fail on the base tree (paste stages nothing; camera input absent) — quoted raw in the verify log; post-change run: green.

## G4 — worklog and report (unconditional per `CO-57`)

`{{WORKLOG_DIR}}/SG-042.log`, `{{WORKLOG_DIR}}/SG-042_report.md`, `{{WORKLOG_DIR}}/SG-042_verify.log` (FAIL-then-PASS both runs raw). First token `SG-042`; elapsed-versus-budget PER LEG with units; MODEL + effort from process arguments; spend line (`$0` — zero provider calls); three UNCLEAR lines.

## Constraints

- **Scope ceiling:** `frontend/src/components/AssetForm.tsx` · `frontend/src/components/AssetForm.test.tsx` (new) · `docs/worklogs` (3 files). **Anything else is a STOP** — including every file under `backend/` (excluded BY RULE per `PG-SC-05`: "no file under `backend/`", grep-gated by `git status --short` showing no `backend/` path) and `CapturePage.tsx` (renders the form as-is; a needed change there is a finding: STOP if it blocks, otherwise report and ship the rest). No new dependencies.
- Every requirement above names a file the ceiling enables it; if you find one that does not, STOP and say which.
- Cross-product (`PG-IC-01`): G1 needs the form file + its drop-zone element only; G2 the same file's input block; G3 the new test file + the `vi.mock` pattern file as read-only context; G4 worklogs. No blanket exclusion is issued, so no exception sentence is owed. No stop-gate shares a condition with a remediation step (`PG-IC-03`) — stops win, stated not assumed.
- Test scope: gates name files checked with counts+elapsed; silent gates FAIL. `PG-EV-01`: feed each new test a deliberately wrong expectation in the same run and show it failing. `PG-EV-02`: the artifact checked is the rendered DOM / committed test output, never a command exit. `PG-EV-05`: properties stated as "a pasted image file appears in the preview list with its name", "the camera input carries `capture=\"environment\"`", checked against the rendered output.
- Budget (uncalibrated per `G-A9`): 120s ordinary · 600s suite+lint+build · **1500s early-close** (stop starting new work, commit what is finished, write the report, publish the receipt) · **2100s overall** — actual-versus-budget per leg with units.
- Simplicity (`G-A7`): two controls, existing staging path reused or the reason stated; nothing else.
- No fixed dates anywhere except this header's authoring-date metadata; every time-dependent check reads the live clock (`PG-IC-07`).

## Acceptance criteria

- Starting tree quoted (clean expected; dirt = STOP first); every premise verified in-slice with quoted reads — in particular the file input (`AssetForm.tsx:154-161`), the drop zone (`:138-174`), `addFiles` (`:30-43`), the untouched name-required lines (`:56-59,101-108`), the `CapturePage` usage (`CapturePage.tsx:46-49`), the `npm test` script (`frontend/package.json:9`), `uploadEvidence` (`client.ts:105-120`), the mock pattern (`AssetDetailPage.test.tsx:7-14`).
- **FAIL-then-PASS, both runs committed (`PG-EV-09`):** pre-change the new tests fail (paste stages nothing; no camera input); post-change all green; both raw outputs in the committed verify log.
- Suite + lint + build green; secret scan 0; no `backend/` diff; no migration; no frozen-prompt diff; no ignored file staged; nothing pushed to `storagegenie-evidence`; no vacuous pass.
- Report states the paste-handler scope decision with its evidence, and confirms desktop select flow unchanged.

## Report

- Work dir `/home/andrei/StorageGenie`, origin remote as on host, `BASE` = start HEAD, `WORK_HEAD` = work hash. Model/effort per `CO-78` from process arguments. Live-state ledger: no DB writes, live spend `$0`, no network.
- **Receipt note on the notes ref (proven shape, unchanged obligation):** push the work to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note on the work HEAD LAST, no commit after (120s bound): `git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-042 | Report: docs/worklogs/SG-042_report.md | Work-HEAD: <hash>" <WORK_HEAD>` — first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`); verify with `show <WORK_HEAD>` and QUOTE executed output; existing-note refusal is a STOP; final line `note=yes`; zero-exit with `note=no` is a FAIL.
- End with the three UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Budget

120s ordinary · 600s suite+lint+build · 1500s early-close · 2100s overall; $0 metered; actual-versus-budget per leg with units.
