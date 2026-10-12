SG-163 — Merge Batch 3 (Q1/D-1012-1): PR#47 re-expressed over the landed #48 (blocked-Accept tooltip,
shared catalog constants) and PR#46 applied minus its smuggled pnpm lockfile (Chat form + Enter-submit
test), both onto automation. Every #46 landed blob is byte-identical to its audited head; the lockfile is
absent from index and tree; #47 was re-derived fresh (its head bytes were NOT applied) preserving each
hunk's visual intent with the shared constants plus its unique tooltip. Derived 4-file vitest set 28/28
green + eslint/tsc clean; no conflict, no rebase, both heads unmoved; diff exactly the three named product
files. Code changes sit on disk only — they go live on the SG-165 deploy rider, never here.

Dispatch-ID: SG-163
Role:        Coder (no dispatch verb run; no other unit started or polled)
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git (fetch+push, as on host)
BASE (packet ref `automation` -> resolved commit): cea0ecf0c0989fe2277ba554beedf9b6411e8c7f
             (ref requested and resolved commit stated separately; ref == commit this run)
WORK_HEAD:   954b43b5598db9560531a8c0cdfb8ca01614c4bf
             (single G1 product commit: #47 rewrite + #46-minus-lockfile in one commit)
Model/effort (`CO-78`/`PB-4`, from process arguments): model `opencode-go/deepseek-v4.1-flash`, effort
             `high` — source `/proc/330807/cmdline` (`opencode run --auto --dir /home/andrei/StorageGenie
             --model opencode-go/deepseek-v4.1-flash --variant high # SG-163 …`). No system-prompt
             identity used.
Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`
             (equals the packet's expected 0.46.0). `rules_check.sh` run live, exit 3:
             `G-L1 UNCHECKED the cache is not checked out at a contract tag`,
             `G-L5`/`G-L7 UNCHECKED gh-unauthenticated`, two `G-L6 BYTES` lines. Payload
             `RULES.sha256` = `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef`
             (equals the `487841B1…` pinned in `AGENTS.md`). Recorded ruleset 0.46.0.
Gates:       DATABASE none · Restart none · Deploy none (unserved by design; lands on SG-165).
Spend:       real $0.000000 USD · zero metered calls · zero live calls · zero container execs
             (local git fetch/checkout, local vitest, local eslint/tsc — all unmetered).
Live clock (`CO-79`, UTC): first command batch ~2026-10-12T15:03Z (labelled, run-order inference);
             vitest Start 2026-10-12T15:04:26Z; static gates end ~2026-10-12T15:04:5xZ. Well inside
             RUN_BUDGET_S; no command near its bound.
Autonomy:    L2 (merge execution covered by D-1012-1; verdicts from SG-160). Class: CHANGED.

## (a) Issues / deviations / surprises

- **Heads unmoved (`PB-1`).** `refs/pull/46/head` = `78cf8e4260d8e66c63ab7bba905faaf5784b0779` (packet
  expected `78cf8e42`) and `refs/pull/47/head` = `742e18751f7691a02bdd44fa3cda8ba34b68318b` (packet expected
  `742e1875`) — both equal the packet's expectation. `refs/pull/48/head` = `33f079f3b691f3321763503100fc656124c44584`
  (the #48 SG-162 landed). No moved head; nothing rebased. Both #46/#47 merge-base to `4c1eb7da…`.
- **F-SG163-1 — the packet's literal-grep list is over-broad for the landed #48 (PB-1; finding, not a defect).**
  G1 asks to prove "no hardcoded `bg-primary`/`bg-card`/`text-primary-foreground`/`border-border` literals
  remain in the button block". The landed #48 (HEAD at slice start, blob `a3784b29`) **already** carries
  `className="bg-primary text-primary-foreground focus-ring"` on the **primary Accept** button — it was
  landed byte-identically by SG-162 and rated 99. That token pair is the repo's **primary-button convention**,
  used as a literal in **10** `src/**/*.tsx` files — including `CatalogToolbar.tsx:146,177`, the very file
  that exports the shared constants. Removing it would (i) require editing `CatalogToolbar.tsx` (outside the
  scope ceiling), or (ii) demote Accept from primary to themed, breaking #47's **per-hunk intent**. I did
  **not** bend the tree to match: the rewrite keeps #48's primary Accept. The literals #47 actually
  *introduced* are gone: the repeated secondary `bg-card text-foreground border-border focus-ring` literal
  (now `THEMED_CONTROL_CLASS`) and the Accept conditional's `bg-muted`/`text-muted-foreground` (dropped).
  Grep quoted under A1. Offered for the Architect's reconciliation.
- **F-SG163-2 — `.rules-cache/` absent on the host (carry-over, SG-145 F5 / SG-149 / SG-153 / SG-161 /
  SG-162).** The live contract path is `/home/andrei/storagegenie-contract`; ran `rules_check.sh` there.
- **F-SG163-3 — `npx` absent (carry-over, SG-161/SG-162).** `node` v24.14.1 / `npm` 11.11.0 present.
  Ran `./node_modules/.bin/vitest` and `./node_modules/.bin/tsc` directly, `npm run lint` via npm.
- **F-SG163-4 — derived test set is 4 files, not the packet's 2 (`PB-7`; finding, not a defect).** The packet
  named `CandidateCard.test.tsx` + `ChatPage.test.tsx`. Grepping the test tree for importers/renderers of the
  changed components adds `routes/ReviewPage.test.tsx` (renders `ReviewPage`, which mounts `CandidateCard`,
  and clicks all four decision buttons — lines 23-26) and `routes/theme-adoption.test.tsx` (renders both
  `<ChatPage />` (line 190) and `<ReviewPage />` (lines 207/240)). All 4 green. See A2.
- **F-SG163-5 — #47 textually overlaps #48 by design; it is a rewrite, never a merge.** #47 and #48 restyle
  the same button block from the same base, so their merge-tree is not a target here: the packet forbids
  applying #47's head bytes. `git merge-tree` was re-proved clean for the **applied** PR only (#46).
- **F-SG163-6 — `CO-25` FAIL-then-PASS does not apply to this slice (stated, not silently skipped).**
  #47 adds no test (only a component restyle); #46 **adds** a genuine new test (Enter-to-submit) so it is a
  new guard, not a fetched red→green. There is no pre-existing failing test to flip, so no manufactured FAIL
  run was staged.
- No command was killed by its bound (`PB-5`). No production write. Nothing outside the scope ceiling changed.

## (b) Actions

- **Changed paths (product):** `frontend/src/components/CandidateCard.tsx` (#47 rewrite over #48),
  `frontend/src/routes/ChatPage.tsx` and `frontend/src/routes/ChatPage.test.tsx` (#46) — only these three;
  54 insertions / 17 deletions. **`frontend/pnpm-lock.yaml` was deliberately dropped and does not appear.**
- **Commit:** G1 `954b43b5598db9560531a8c0cdfb8ca01614c4bf` = WORK_HEAD; then the docs commit carrying
  `docs/worklogs/SG-163.log`, `SG-163_verify.log`, `SG-163_report.md`.
- **Push:** work pushed to `automation`; clean local `HEAD == origin/automation` after push.
- **External / production effects:** none. No deploy, no restart, no container exec, no migration. The three
  files are changed **on disk only** and are not served until the SG-165 rider rebuilds.
- **Durations:** orientation/premise + apply < 40 s; G2 vitest 2.22 s; eslint + tsc ~8 s; close/receipt < 30 s.
  Retry count 0; test-command count 1 (targeted derived suite) + 2 static gates; provider-call count 0.
- **Health delta (`CO-92`): `HEALTH: not run`** — this slice serves no server and the packet sets DATABASE
  none / Restart none / Deploy none; the running container is untouched, so a start/end probe would add
  nothing. Recorded as deliberately-not-run rather than claimed unchanged.
- **Highest-impact action:** re-expressing #47 as a fresh edit over the already-landed #48 (never applying
  #47's head bytes, so #48's DRY/shared-constant treatment survives intact) while keeping #47's one unique
  value — the blocked-Accept tooltip — and landing #46's Enter-to-submit Chat form without its smuggled
  second lockfile.

## (c) Verification

### A1 — #47 re-expressed over #48 (tooltip + shared constants, per-hunk intent) and #46-minus-lockfile blob-identical

#47 was **not** applied from `742e1875`; the landed `CandidateCard.tsx` (blob `a3784b29`, == #48 head blob)
was edited once, wrapping the primary Accept button in #47's tooltip span and changing nothing else:

```
$ git diff 954b43b^ 954b43b -- frontend/src/components/CandidateCard.tsx
-        <button
-          type="button"
-          onClick={() => onDecision("accept", values)}
-          disabled={busy || blocked}
-          className="bg-primary text-primary-foreground focus-ring"
-          style={{ ...CONTROL_STYLE, border: "none", opacity: busy || blocked ? 0.5 : 1, cursor: busy || blocked ? "not-allowed" : "pointer" }}
-        >
-          Accept
-        </button>
+        <span title={blocked ? "Acceptance is blocked until open review tasks are resolved" : undefined}>
+          <button
+            type="button"
+            onClick={() => onDecision("accept", values)}
+            disabled={busy || blocked}
+            className="bg-primary text-primary-foreground focus-ring"
+            style={{ ...CONTROL_STYLE, border: "none", opacity: busy || blocked ? 0.5 : 1, cursor: busy || blocked ? "not-allowed" : "pointer" }}
+          >
+            Accept
+          </button>
+        </span>
```

Tooltip present (grep):
```
$ grep -n "Acceptance is blocked until open review tasks are resolved" frontend/src/components/CandidateCard.tsx
89:        <span title={blocked ? "Acceptance is blocked until open review tasks are resolved" : undefined}>
```

Literal grep over the **button block** (lines 88-136) — the only token literal is the primary pair on Accept:
```
$ git show 954b43b:frontend/src/components/CandidateCard.tsx | sed -n '88,136p' \
    | grep -n "bg-card\|border-border\|bg-muted\|text-muted-foreground\|bg-primary\|text-primary-foreground"
94:            className="bg-primary text-primary-foreground focus-ring"
```
All five buttons use the shared `CONTROL_STYLE`; the four secondary/split buttons use the shared
`THEMED_CONTROL_CLASS`. `bg-card`, `border-border`, `bg-muted`, `text-muted-foreground` appear **nowhere**
in the block (the remaining `bg-card`/`border-border`/`text-muted-foreground` hits in the file are the
pre-existing `article`/field/evidence markup, untouched). See F-SG163-1 for why the primary pair remains.

Per-hunk intent (base `4c1eb7d` had unstyled `<button>`s) — #47's five hunks, each preserved:
```
  hunk 1  Accept           : primary emphasis (bg-primary/text-primary-foreground; opacity .5 when
                             busy||blocked) + blocked tooltip span   -> kept (span added; #48 styling)
  hunk 2  Save edits       : themed secondary (bg-card/text-foreground/border-border) -> THEMED_CONTROL_CLASS
  hunk 3  Hold / Unknown   : themed secondary                          -> THEMED_CONTROL_CLASS
  hunk 4  Reject           : themed secondary                          -> THEMED_CONTROL_CLASS
  hunk 5  Split into N     : themed secondary (conditional render)      -> THEMED_CONTROL_CLASS
```
#46 selected-paths apply (lockfile never staged), landed blobs == head blobs:
```
$ git checkout 78cf8e4260d8e66c63ab7bba905faaf5784b0779 -- frontend/src/routes/ChatPage.tsx frontend/src/routes/ChatPage.test.tsx
46 frontend/src/routes/ChatPage.tsx      landed=4ec5fb76de07792c4917f3decaba4cbcdbf73911 head=4ec5fb76de07792c4917f3decaba4cbcdbf73911  IDENTICAL
46 frontend/src/routes/ChatPage.test.tsx landed=5fb1ad4cba04b616009cbffd0593d57de137aa9a head=5fb1ad4cba04b616009cbffd0593d57de137aa9a  IDENTICAL
```
Equivalence evidence = landed `git rev-parse :<path>` equals the head's blob OID, so the residual
landed-vs-head diff is empty by construction (blob identity, `PB-3`-safe: non-empty concrete OIDs, both
sides). Clean merge-tree re-proved live for the applied PR: `git merge-tree <mb> HEAD 78cf8e42` exit 0,
ChatPage blobs merging to the head blobs (`4ec5fb76`/`5fb1ad4c`); no conflict.

Lockfile absence (index and whole tree):
```
$ git ls-files --error-unmatch frontend/pnpm-lock.yaml
error: pathspec 'frontend/pnpm-lock.yaml' did not match any file(s) known to git   # exit=1 (absent)
$ git diff --cached --name-only | grep -i pnpm      # exit=1 (nothing staged)
$ git ls-files | grep -i pnpm                        # exit=1 (no pnpm lockfile anywhere in HEAD)
```
The #46 head added a 3171-line `frontend/pnpm-lock.yaml`; that blob is **not** in the landed tree
(`frontend/package-lock.json` remains the repo's only frontend lockfile).

### A2 — derived affected suites green + static gates clean

```
$ ./node_modules/.bin/vitest run \
    src/components/CandidateCard.test.tsx src/routes/ReviewPage.test.tsx \
    src/routes/ChatPage.test.tsx src/routes/theme-adoption.test.tsx
 ✓ src/components/CandidateCard.test.tsx  ( 5 tests) 274ms
 ✓ src/routes/ChatPage.test.tsx           ( 7 tests) 461ms
 ✓ src/routes/ReviewPage.test.tsx         ( 4 tests) 516ms
 ✓ src/routes/theme-adoption.test.tsx     (12 tests) 408ms
  Test Files  4 passed (4)      Tests  28 passed (28)      VITEST_EXIT=0

$ npm run lint                       # eslint src      -> LINT_EXIT=0
$ ./node_modules/.bin/tsc --noEmit                    -> TSC_EXIT=0
```
No full end-to-end sweep (packet: none). No red anywhere; no drive-by fixes needed. Full log:
`docs/worklogs/SG-163_verify.log`. Non-hits considered and excluded: `SettingsPage.test.tsx`,
`AssetDetailPage.test.tsx`, `AnalyticsPage.test.tsx` matched the broad word grep (`Reject`/`Accept`) but do
**not** import or render `CandidateCard` (only `ReviewPage.tsx` does); `theme-adoption.test.tsx` *does*
render both changed components, so it was added.

### A3 — diff file list == the named files (+ worklogs); no pnpm-lock anywhere

```
$ git diff --name-status cea0ecf0c0989fe2277ba554beedf9b6411e8c7f 954b43b5598db9560531a8c0cdfb8ca01614c4bf
M	frontend/src/components/CandidateCard.tsx
M	frontend/src/routes/ChatPage.test.tsx
M	frontend/src/routes/ChatPage.tsx
```
Exactly the three named product files; the only other writes are `docs/worklogs/SG-163_*`. **No
`pnpm-lock.yaml` in the diff** (would have been a STOP). A secret scan over added lines (`CO-100`) matched
nothing (`secret_scan_exit=1`, 57 added lines scanned).

### A4 — report + receipt read back on remote; no production write

- Report committed at `docs/worklogs/SG-163_report.md` (tracked; `CO-57`), with `SG-163_verify.log` and
  `SG-163.log`.
- Receipt note published on `refs/notes/storagegenie-coder-reports` anchoring **WORK_HEAD**
  `954b43b5598db9560531a8c0cdfb8ca01614c4bf`, first line carrying BOTH `Dispatch-ID:` and `Report:` (`CO-97`);
  read back via a mapped fetch — verbatim block pasted in the receipt section below (this report does not
  carry its own commit hash, `CO-55b`).
- Production writes: none. Proven by the diff file list above (three frontend files) plus tip movement
  limited to this slice's commits (G1 + docs) on `automation`; no datastore, no migration, no deploy, no
  container exec.

## Receipt

Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no `{{RECEIPT_CMD}}`
product-script run (legacy finalize refused on this lane, retired per `AGENTS.md`); the Coder publishes the
notes-ref receipt. Note published on `refs/notes/storagegenie-coder-reports` anchored on **WORK_HEAD**
`954b43b5598db9560531a8c0cdfb8ca01614c4bf` and, dual-annotation (`SG-092` precedent), on the docs tip; read
back via a **mapped** fetch. Executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show 954b43b5598db9560531a8c0cdfb8ca01614c4bf
error: no note found for object 954b43b5598db9560531a8c0cdfb8ca01614c4bf.
existing_note_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-163 | Report: docs/worklogs/SG-163_report.md | Work-HEAD: 954b43b5598db9560531a8c0cdfb8ca01614c4bf" 954b43b5598db9560531a8c0cdfb8ca01614c4bf
add_wh_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-163 | Report: docs/worklogs/SG-163_report.md | Work-HEAD: 954b43b5598db9560531a8c0cdfb8ca01614c4bf" <docs-tip>
add_tip_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg163-fetched
$ git notes --ref=refs/notes/sg163-fetched show 954b43b5598db9560531a8c0cdfb8ca01614c4bf
Dispatch-ID: SG-163 | Report: docs/worklogs/SG-163_report.md | Work-HEAD: 954b43b5598db9560531a8c0cdfb8ca01614c4bf
show_wh_exit=0
```

`<docs-tip>` is the report's own commit, which cannot be named in the report (`CO-55b`). `work commit:
954b43b5…` is the product commit; the committed verify log cites it as `WORK_HEAD`, not the tip (`CO-55c`).

## INTENT

`INTENT: code does re-express #47's five-button restyle fresh over the already-landed #48 (shared catalog
constants; #47's head bytes never applied) keeping only #47's unique blocked-Accept tooltip, and applies
#46's audited head tree for exactly ChatPage.tsx + ChatPage.test.tsx, dropping the smuggled lockfile and
nothing else; the checks expect the tooltip present, the #47-introduced literals gone, each #46 landed blob
OID equal to its head blob OID, the lockfile absent, and the derived affected suites to stay green; the
approved packet (G1/G2) says exactly that.` X, Y, Z agree — no item stopped.

## TWINS

Not applicable — this is a mechanical merge/rewrite of external bytes, not a defect fix; no wrong construct
to search for (`CO-17`). No out-of-scope sites exist for the construct "landed #46 blob != head blob": both
are equal.

## Vacuity check (`PB-3`)

No criterion can pass vacuously: A1 compares concrete non-empty OIDs per path (both equal) and the
lockfile-absence check fails closed (`exit=1` on a file known to git — a present lockfile would return 0);
the literal grep was scoped to the actual button block and returned a real non-empty match line (the primary
pair) rather than an empty result; the tooltip grep returned the concrete added line; A2 ran a non-empty
derived set (4 files, 28 tests) with a nonzero exit on any failure plus two static gates that exit nonzero
on failure; A3's ceiling is a 3-file product diff (not empty) and the pnpm grep would match a smuggled file;
A4's note was read back from a mapped fetch of the remote ref. The failing possibility was real in every
gate.

## UNCLEAR

- **FIRST READ:** the packet lands #47 (re-expressed over #48, unserved) and #46-minus-lockfile — a merge
  slice covered by D-1012-1, verdicts from SG-160. It names 2 test files as an expectation; `PB-7` is not
  named in the packet, but G2 instructs "grep and add every hit — a hit is a file", so I derived the set
  (4 files) and treated the packet's list as the floor. I echoed contract 0.46.0 verbatim from the host path.
- **DURING EXECUTION:** both head SHAs matched the expectation exactly (no STOP); #46's merge-tree is clean
  and was re-proved live. I chose to **edit** the landed #48 for #47 (never applying #47's head bytes), so
  the shared-constant treatment is byte-preserved; the only #47 value carried over is the tooltip. The
  packet's literal-grep token list includes the primary pair that the landed #48 (and repo convention, 10
  files incl `CatalogToolbar.tsx`) already uses on Accept — I did not bend the tree to match; reported as
  F-SG163-1. `npx` absent (F-SG163-3); `CO-25` has no target here (F-SG163-6). Health probe deliberately not
  run (no server surface touched). The derived set exceeded the packet's 2 by 2 files (F-SG163-4).
- **REMAINING:** nothing owed by this slice. The bundle is on disk only; the served change rides SG-165.
  SG-164 (#49 rewrite over #46) is untouched here per the packet. `.rules-cache/` absence (F-SG163-2) and
  F-SG163-1 are offered for the Architect's reconciliation.
