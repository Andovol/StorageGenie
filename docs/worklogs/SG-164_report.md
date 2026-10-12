SG-164 — Merge Batch 4 (Q1/D-1012-1): PR#49 theming re-derived over the landed #46 (Chat select + both
inputs + Send + Log-correction classes and cursor states), unserved. #49's head bytes were NOT applied; the
theming was written fresh on the current `ChatPage.tsx` and the `<form onSubmit>` wrapping + `type="submit"`
wiring landed by #46 (SG-163) is byte-intact. The re-derived file's blob is byte-identical to #49's head
ChatPage.tsx (`b55742c6…`) and its base blob is #46's landed blob (`4ec5fb76…`). The smuggled
`frontend/pnpm-lock.yaml` is absent from index and tree. Derived 2-file vitest set 19/19 green + the
Enter-submit test run explicitly green + eslint/tsc clean; #49 head unmoved; diff exactly
`frontend/src/routes/ChatPage.tsx` + worklogs. Code sits on disk only — it goes live on the SG-165 deploy
rider, never here.

Dispatch-ID: SG-164
Role:        Coder (no dispatch verb run; no other unit started or polled)
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git (fetch+push, as on host)
BASE (packet ref `automation` -> resolved commit): 1d96e84798742cd70cfd0fd99199dbc7486b1249
             (ref requested and resolved commit stated separately; ref == commit this run)
WORK_HEAD:   9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8
             (single G1 product commit: #49 theming over landed #46)
Model/effort (`CO-78`/`PB-4`, from process arguments): model `opencode-go/deepseek-v4.1-flash`, effort
             `high` — source `/proc/342353/cmdline` (`opencode run --auto --dir /home/andrei/StorageGenie
             --model opencode-go/deepseek-v4.1-flash --variant high # SG-164 …`). No system-prompt
             identity used.
Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`
             (equals the packet's expected 0.46.0). `rules_check.sh` run live, exit 3:
             `G-L1 UNCHECKED the cache is not checked out at a contract tag`,
             `G-L5`/`G-L7 UNCHECKED gh-unauthenticated`, two `G-L6 BYTES` lines. Payload
             `RULES.sha256` = `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef`
             (equals the `487841B1…` pinned in `AGENTS.md`). Recorded ruleset 0.46.0.
Gates:       DATABASE none · Restart none · Deploy none (unserved by design; lands on SG-165).
Spend:       real $0.000000 USD · zero metered calls · zero live calls · zero container execs
             (local git fetch/hash-object, local vitest, local eslint/tsc — all unmetered).
Live clock (`CO-79`, UTC): orientation + head re-verify ~2026-10-12T15:07Z; re-derive + three-way proof
             ~2026-10-12T15:08Z; Enter test 15:09:20Z; derived suite 15:09:24Z; commit/push ~15:09:5xZ.
             Well inside RUN_BUDGET_S; no command near its bound.
Autonomy:    L2 (merge execution covered by D-1012-1; verdicts from SG-160). Class: CHANGED.

## (a) Issues / deviations / surprises

- **Head unmoved (`PB-1`).** `refs/pull/49/head` = `33252132a6b4b027a94e966f8cbc221a113a1c23` (packet expected
  `33252132`) — equal to the packet's expectation. No STOP; nothing rebased. Merge-base to `4c1eb7da…` and
  #49's diff-to-base is exactly `pnpm-lock.yaml` + `ChatPage.tsx`, confirming the packet's premise.
- **F-SG164-1 — the re-derived theming is byte-identical to #49's head `ChatPage.tsx` (`PB-1`; finding, not a
  defect).** Because #46 and #49 branched from the same base `4c1eb7da` and #46 landed *exactly* the form
  wrapping #49 also carries, "landed #46 + #49's theming delta" is mathematically equal to #49's head file. I
  built on the landed file (base blob `4ec5fb76`, == #46's landed/head blob) and added the five theming
  deltas; the resulting blob `b55742c6` equals `33252132:frontend/src/routes/ChatPage.tsx`. This is a
  *consequence* of re-deriving, not an application of the head bytes: the method was file-edit over the
  current tree, and #46's form/submit structure is proven untouched (A1). Offered for the Architect.
- **F-SG164-2 — `.rules-cache/` absent on the host (carry-over, SG-145 F5 / SG-149 / SG-153 / SG-161 /
  SG-162 / SG-163).** The live contract path is `/home/andrei/storagegenie-contract`; ran `rules_check.sh`
  there.
- **F-SG164-3 — `npx` absent (carry-over, SG-161/SG-162/SG-163).** `node` v24.14.1 / `npm` 11.11.0 present.
  Ran `./node_modules/.bin/vitest` and `./node_modules/.bin/tsc` directly, `npm run lint` via npm.
- **F-SG164-4 — packet's `PB-7` not named; derived set stays 2 files (finding, consistent with SG-163).** The
  packet names `ChatPage.test.tsx` and says "grep and add every hit". Grep over the test tree for importers/
  renderers of the changed component adds `routes/theme-adoption.test.tsx` (renders `<ChatPage />` at lines
  190 and 233). Files matching only the generic word "Category" (`catalog.test.tsx`, `drawer.test.tsx`,
  `shell.test.tsx`, `ExpiryPage.test.tsx`) do **not** import or render `ChatPage` (they assert on unrelated
  asset/catalogue selects) and were excluded — same classification as SG-163. Set = 2 files, 19 tests.
- **F-SG164-5 — #49 adds no test; no `CO-25` FAIL-then-PASS target (stated, not silently skipped).** #46
  already landed the Enter-submit test; this slice only restyles controls, so no pre-existing red test exists
  to flip. The Enter-submit test was instead run explicitly against the themed tree as G2 requires.
- No command was killed by its bound (`PB-5`). No production write. Nothing outside the scope ceiling changed.

## (b) Actions

- **Changed paths (product):** `frontend/src/routes/ChatPage.tsx` only (22 insertions / 2 deletions — the 2
  deletions are the two pre-existing `style={{ flex: 1, padding: 8 }}` lines replaced). **No test file
  written** (#49 ships none). **`frontend/pnpm-lock.yaml` never staged and absent from the tree.**
- **Commit:** G1 `9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8` = WORK_HEAD; then the docs commit carrying
  `docs/worklogs/SG-164.log`, `SG-164_verify.log`, `SG-164_report.md`.
- **Push:** work pushed to `automation`; clean local `HEAD == origin/automation` after push.
- **External / production effects:** none. No deploy, no restart, no container exec, no migration. The file is
  changed **on disk only** and is not served until the SG-165 rider rebuilds.
- **Durations:** orientation/premise + re-derive + proof < 60 s; Enter test 1.45 s; derived suite 2.03 s;
  eslint + tsc ~6 s; close/receipt < 60 s. Retry count 0; test-command count 2 (explicit Enter test + derived
  suite) + 2 static gates; provider-call count 0.
- **Health delta (`CO-92`): `HEALTH: not run`** — this slice serves no server and the packet sets DATABASE
  none / Restart none / Deploy none; the running container is untouched, so a start/end probe would add
  nothing. Recorded as deliberately-not-run rather than claimed unchanged.
- **Highest-impact action:** writing #49's five theming deltas fresh onto the already-landed #46 tree (never
  applying #49's head bytes) so #46's `<form onSubmit>` structure and Enter-submit behaviour survive intact,
  while the smuggled lockfile never enters the tree.

## (c) Verification

### A1 — #49 theming present per hunk; #46 form wrapping byte-intact; lockfile absent

Base blob = the landed #46 file: `4ec5fb76de07792c4917f3decaba4cbcdbf73911` (== #46 head blob, landed
SG-163). Five theming deltas added (no structural change):

```
$ git show 9b46aea -- frontend/src/routes/ChatPage.tsx    (hunk content)
  hunk 1  category <select>      : + className="bg-background text-foreground border-border focus-ring"
                                   + style={{ padding: "4px 8px", borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
  hunk 2  Question <input>       : + className="bg-background text-foreground border-border focus-ring"
                                   style  { flex: 1, padding: 8 } -> { flex: 1, padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }
  hunk 3  Send <button>          : + className="bg-primary text-primary-foreground focus-ring"
                                   + style={{ padding: "8px 16px", borderRadius: 6, border: "none", fontWeight: 600, cursor: … }}
  hunk 4  Correction <input>     : + className="bg-background text-foreground border-border focus-ring"
                                   style  { flex: 1, padding: 8 } -> { flex: 1, padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }
  hunk 5  Log correction <button>: + className="bg-card text-foreground border-border focus-ring"
                                   + style={{ padding: "8px 16px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: … }}
```

Presence grep on the resulting file:
```
$ grep -n 'className="bg-background text-foreground border-border focus-ring"' frontend/src/routes/ChatPage.tsx
100:            className="bg-background text-foreground border-border focus-ring"   (select)
140:          className="bg-background text-foreground border-border focus-ring"     (Question input)
173:          className="bg-background text-foreground border-border focus-ring"     (Correction input)
$ grep -n 'className="bg-primary text-primary-foreground focus-ring"' frontend/src/routes/ChatPage.tsx
146:          className="bg-primary text-primary-foreground focus-ring"               (Send)
$ grep -n 'className="bg-card text-foreground border-border focus-ring"' frontend/src/routes/ChatPage.tsx
179:          className="bg-card text-foreground border-border focus-ring"            (Log correction)
$ grep -c 'cursor: !effectiveHousehold' frontend/src/routes/ChatPage.tsx   -> 2
```

Form wiring byte-intact (content-only; line numbers stripped so indentation shifts do not pollute):
```
$ git show HEAD:frontend/src/routes/ChatPage.tsx \
    | grep -E '<form|onSubmit=\{\(event\)|event\.preventDefault|\.mutate\(\);|type="submit"|</form>' \
    | sed -E 's/^[0-9]+://' > pre
$ grep -E '<form|onSubmit=\{\(event\)|event\.preventDefault|\.mutate\(\);|type="submit"|</form>' \
    frontend/src/routes/ChatPage.tsx | sed -E 's/^[0-9]+://' > post
$ diff pre post
FORM+SUBMIT WIRING BYTE-INTACT (content diff empty)
```

Re-derive method proof — built on the landed #46 blob, result equals #49's head blob:
```
$ git rev-parse HEAD:frontend/src/routes/ChatPage.tsx          # 4ec5fb76de07792c4917f3decaba4cbcdbf73911 (base = #46 landed)
$ git hash-object frontend/src/routes/ChatPage.tsx            # b55742c6668409b2b6c8f81fabb583e13b4dc7f0 (result)
$ git rev-parse 33252132:frontend/src/routes/ChatPage.tsx     # b55742c6668409b2b6c8f81fabb583e13b4dc7f0 (== result; diff empty)
RE-DERIVED == #49 HEAD (byte-identical)
```

Lockfile absence (index and whole tree):
```
$ git ls-files --error-unmatch frontend/pnpm-lock.yaml
error: pathspec 'frontend/pnpm-lock.yaml' did not match any file(s) known to git   # exit=1 (absent)
$ git diff --cached --name-only | grep -i pnpm      # exit=1 (nothing staged)
$ git ls-files | grep -i pnpm                        # exit=1 (no pnpm lockfile anywhere in HEAD)
```
#49's head added a 3171-line `frontend/pnpm-lock.yaml`; that blob is **not** in the landed tree
(`frontend/package-lock.json` remains the repo's only frontend lockfile).

### A2 — Enter-submit + derived suites green; static gates clean

```
$ ./node_modules/.bin/vitest run src/routes/ChatPage.test.tsx \
    -t "submitting the form by pressing Enter sends the question"
 ✓ src/routes/ChatPage.test.tsx  (7 tests | 6 skipped) 105ms
 Test Files  1 passed (1)
      Tests  1 passed | 6 skipped (7)          ENTER_EXIT=0

$ ./node_modules/.bin/vitest run \
    src/routes/ChatPage.test.tsx src/routes/theme-adoption.test.tsx
 ✓ src/routes/ChatPage.test.tsx           ( 7 tests) 370ms
 ✓ src/routes/theme-adoption.test.tsx     (12 tests) 379ms
 Test Files  2 passed (2)      Tests  19 passed (19)   VITEST_EXIT=0

$ npm run lint                       # eslint src      -> LINT_EXIT=0
$ ./node_modules/.bin/tsc --noEmit                    -> TSC_EXIT=0
```
No full end-to-end sweep (packet: none). No red anywhere; no drive-by fixes needed. Full log:
`docs/worklogs/SG-164_verify.log`. Non-hits considered and excluded (F-SG164-4): `catalog.test.tsx`,
`drawer.test.tsx`, `shell.test.tsx`, `ExpiryPage.test.tsx` matched the broad word grep (`Category`) but do not
import or render `ChatPage`.

### A3 — diff file list == the named file (+ worklogs); no pnpm-lock anywhere

```
$ git diff --name-status 1d96e84798742cd70cfd0fd99199dbc7486b1249 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8
M	frontend/src/routes/ChatPage.tsx
```
Exactly the one named product file (plus `docs/worklogs/SG-164_*` in the docs commit); the only other writes
are those worklogs. **No test file and no `pnpm-lock.yaml` in the diff** (either would have been a STOP). A
secret scan over added lines (`CO-100`) matched nothing (`secret_scan_exit=1`, 22 added lines scanned).

### A4 — report + receipt read back on remote; no production write

- Report committed at `docs/worklogs/SG-164_report.md` (tracked; `CO-57`), with `SG-164_verify.log` and
  `SG-164.log`.
- Receipt note published on `refs/notes/storagegenie-coder-reports` anchoring **WORK_HEAD**
  `9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8`, first line carrying BOTH `Dispatch-ID:` and `Report:` (`CO-97`);
  read back via a mapped fetch — verbatim block pasted in the receipt section below (this report does not
  carry its own commit hash, `CO-55b`).
- Production writes: none. Proven by the diff file list above (one frontend file) plus tip movement limited
  to this slice's commits (G1 + docs) on `automation`; no datastore, no migration, no deploy, no container
  exec.

## Receipt

Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no `{{RECEIPT_CMD}}`
product-script run (legacy finalize refused on this lane, retired per `AGENTS.md`); the Coder publishes the
notes-ref receipt. Note published on `refs/notes/storagegenie-coder-reports` anchored on **WORK_HEAD**
`9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8` and, dual-annotation (`SG-092` precedent), on the docs tip; read
back via a **mapped** fetch. Executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8
error: no note found for object 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8.
existing_note_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-164 | Report: docs/worklogs/SG-164_report.md | Work-HEAD: 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8" 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8
add_wh_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-164 | Report: docs/worklogs/SG-164_report.md | Work-HEAD: 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8" <docs-tip>
add_tip_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg164-fetched
$ git notes --ref=refs/notes/sg164-fetched show 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8
Dispatch-ID: SG-164 | Report: docs/worklogs/SG-164_report.md | Work-HEAD: 9b46aeae00ba894afd3f1ec6fe9bedcb7ae136c8
show_wh_exit=0
```

`<docs-tip>` is the report's own commit, which cannot be named in the report (`CO-55b`). `work commit:
9b46aea…` is the product commit; the committed verify log cites it as `WORK_HEAD`, not the tip (`CO-55c`).

## INTENT

`INTENT: code writes #49's theming deltas fresh over the already-landed #46 ChatPage.tsx (never applying
#49's head bytes) so the category select, both inputs and both buttons gain #49's classes/cursor states while
#46's <form onSubmit> wrapping stays byte-intact, drops the smuggled lockfile, and ships no test; the checks
expect each theming hunk present, the form/submit wiring content-identical, the lockfile absent, and the
Enter-submit + derived suites green; the approved packet (G1/G2) says exactly that.` X, Y, Z agree — no item
stopped.

## TWINS

Not applicable — this is a mechanical rewrite of external bytes, not a defect fix; no wrong construct to
search for (`CO-17`). No out-of-scope site exists for the construct "landed #46 form wrapping != #49 form
wrapping": they are the same wrapping.

## Vacuity check (`PB-3`)

No criterion can pass vacuously: A1 compares concrete non-empty blob OIDs on both sides (base `4ec5fb76` / 
result+head `b55742c6`) and the lockfile-absence check fails closed (`exit=1` on a file known to git — a
present lockfile would return 0); the per-hunk grep returned real non-empty match lines with line numbers;
the form-wiring diff was a genuine content compare that could have been non-empty; A2 ran a non-empty derived
set (2 files, 19 tests) plus the Enter test explicitly, and two static gates that exit nonzero on failure;
A3's ceiling is a 1-file product diff (not empty) and the pnpm grep would match a smuggled file; A4's note was
read back from a mapped fetch of the remote ref. The failing possibility was real in every gate.

## UNCLEAR

- **FIRST READ:** the packet lands #49's theming re-derived over the landed #46 (unserved) — a merge slice
  covered by D-1012-1, verdicts from SG-160. It names `ChatPage.test.tsx` and instructs "grep and add every
  hit", so I derived the set (2 files) and treated the named file as the floor. I echoed contract 0.46.0
  verbatim from the host path.
- **DURING EXECUTION:** #49's head matched the expected `33252132` exactly (no STOP). Re-deriving over the
  landed #46 produced a blob byte-identical to #49's head ChatPage.tsx (F-SG164-1) — a consequence of the
  shared base + identical form wrapping, arrived at by file-edit, not by applying head bytes; #46's
  form/submit structure was proven content-identical. `npx` absent (F-SG164-3); no `CO-25` target exists
  (F-SG164-5). Health probe deliberately not run (no server surface touched). The derived set stayed 2 files
  (F-SG164-4).
- **REMAINING:** nothing owed by this slice. The bundle is on disk only; the served change rides SG-165
  (close-out deploy). `.rules-cache/` absence (F-SG164-2) and F-SG164-1 are offered for the Architect's
  reconciliation.
