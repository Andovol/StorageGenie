SG-161 — Merge Batch 1 landed unserved: PR#43 (ExpiryEntryForm) and PR#45 (AssetImportModal) applied
onto automation by their real hunks, both landed blobs byte-identical to the audited heads; derived
5-file vitest set 85/85 green + eslint/tsc clean; no conflict, no rebase, no head moved; diff exactly the
two component files. Served code changes on disk only — goes live on the SG-165 deploy rider.

Dispatch-ID: SG-161
Role:        Coder (no dispatch verb run; no other unit started or polled)
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git (fetch+push, as on host)
BASE (packet ref `origin/automation` -> resolved commit): 7fa810c3d5f8f7a2fc9fbac820484de897ec346c
             (ref requested and resolved commit stated separately; ref == commit this run)
WORK_HEAD:   ba3827ebe29151c7a97376280e4002ceb2fb46c0
             (G1 product commit, PR#45; the G0 product commit is its parent 373d7018ed53c02ce70c8ef5456016cda5cdfa44)
Model/effort (`CO-78`/`PB-4`, from process arguments): model `opencode-go/deepseek-v4.1-flash`, effort
             `high` — source `/proc/317222/cmdline` (parent `opencode run --auto --dir /home/andrei/StorageGenie
             --model opencode-go/deepseek-v4.1-flash --variant high # SG-161 …`). No system-prompt identity used.
Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`
             (equals the packet's expected 0.46.0). Checkout HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730`;
             payload `RULES.sha256` = `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef`
             (equals the `487841B1…` pinned in `AGENTS.md`). `rules_check.sh` run live, exit 3:
             `G-L1 UNCHECKED the cache is not checked out at a contract tag`,
             `G-L5`/`G-L7 UNCHECKED gh-unauthenticated`, two `G-L6 BYTES` lines. Recorded ruleset 0.46.0.
Gates:       DATABASE none · Restart none · Deploy none (unserved by design; lands on SG-165).
Spend:       real $0.000000 USD · zero metered calls · zero live calls · zero container execs
             (local git fetch/apply, local vitest, local eslint/tsc — all unmetered).
Live clock (`CO-79`, UTC): start not separately stamped; first command batch ~2026-10-12T14:52:30Z
             (inference from run order, labelled), vitest Start 2026-10-12T14:53:42Z; end 2026-10-12T14:54:18Z;
             as-of-report-writing 2026-10-12T14:54:18Z. Total ~110 s (inferred start), well inside RUN_BUDGET_S.
Autonomy:    L2 (merge execution covered by D-1012-1; verdicts from SG-160). Class: CHANGED.

## (a) Issues / deviations / surprises

- **F-SG161-1 — derived test set larger than the packet's list (`PB-7`; finding, not a defect).** The packet
  named 2 files. The derived set is **5**: the packet's `ExpiryEntryForm.test.tsx` +
  `shell/import-modal.test.tsx`, plus `routes/AssetDetailPage.test.tsx` (asserts the touched "Save expiry"
  button and its empty-date-disabled state), `components/shell/shell.test.tsx` (opens the import dialog,
  which mounts `AssetImportModal`), and `components/catalog/catalog.test.tsx` (opens the import dialog via
  `ProductGrid`). `ReviewPage.tsx` renders `ExpiryEntryForm` but `ReviewPage.test.tsx` never references the
  component or its markup -> **not** a hit. All 5 are green; no red.
- **F-SG161-2 — `.rules-cache/` absent on the host (carry-over, SG-145 F5 / SG-149 F5 / SG-153 F-SG153-2).**
  The live contract path is `/home/andrei/storagegenie-contract`; the packet's `bash .rules-cache/rules_check.sh`
  fails `No such file or directory`. Run against the live path instead. Offered for reconciliation.
- **F-SG161-3 — `CO-25` FAIL-then-PASS does not apply to this slice (stated, not silently skipped).** Both PRs
  add **no test**, and both changed files already had tests at base that are green before and after; a
  pass-on-both test proves nothing and none was authored (`CO-25`). The actual equivalence proof here is
  **blob identity** (A1): the landed file bytes equal the audited head bytes exactly. The suite is the
  regression guard, not the change proof.
- **F-SG161-4 — `npx` is absent on this host.** `which npx` empty; `node`/`npm` present (`/usr/local/bin`,
  node v24.14.1). Ran `./node_modules/.bin/vitest` and `./node_modules/.bin/tsc` directly. No workaround of a
  privileged denial (none occurred).
- **Heads unmoved (`PB-1`).** `refs/pull/43/head` = `6d34e6e9f943fc586a05f928b686f3129d0c2823` and
  `refs/pull/45/head` = `3676e69f1716f98e42e205ee057bce2be99e2438` — both equal the packet's expected SHAs.
  No STOP condition; nothing rebased.
- No denied privileged operation occurred; nothing was routed around (`PB-2`). No command was killed by its
  bound (`PB-5`). No production write.

## (b) Actions

- **Changed paths (product):** `frontend/src/components/ExpiryEntryForm.tsx`, and
  `frontend/src/components/shell/AssetImportModal.tsx` — only these two; 64 insertions / 6 deletions total.
- **Commits:** G0 `373d7018ed53c02ce70c8ef5456016cda5cdfa44` (land PR#43); G1
  `ba3827ebe29151c7a97376280e4002ceb2fb46c0` (land PR#45) = WORK_HEAD; then the docs commit carrying
  `docs/worklogs/SG-161.log`, `SG-161_verify.log`, `SG-161_report.md`.
- **Push:** work pushed to `automation`; clean local `HEAD == origin/automation` after push.
- **External / production effects:** none. No deploy, no restart, no container exec, no migration. The two
  component bundles are changed **on disk only** and are not served until the SG-165 rider rebuilds.
- **Durations:** orientation/premise + apply ~60 s; G2 vitest 3.64 s; eslint+tsc ~25 s; close/receipt < 30 s.
  No phase over a minute individually beyond the aggregate. Retry count 0; test-command count 1 (targeted
  suite) + 2 static gates; provider-call count 0.
- **Health delta (`CO-92`): `HEALTH: unchanged, OK`** — start `{"status":"ok","db":"ok","storage":"ok"}`,
  end identical (the running container serves the prior bundle; this slice touches no server).
- **Highest-impact action:** landing PR#43 with the landed blob proven byte-identical to its audited head.

## (c) Verification

### A1 — both heads applied blob-identical (real hunks; equivalence per PR)

```
$ git cherry-pick -n 6d34e6e9f943fc586a05f928b686f3129d0c2823   # PR#43  exit=0
43 landed=b9267e2d0126e6a55a7d1cf82e01027342941138 head=b9267e2d0126e6a55a7d1cf82e01027342941138  IDENTICAL
$ git cherry-pick -n 3676e69f1716f98e42e205ee057bce2be99e2438   # PR#45  exit=0
45 landed=0727642fde9bdffe5ed2a0005ae1f69f21de3142 head=0727642fde9bdffe5ed2a0005ae1f69f21de3142  IDENTICAL
```
Method: cherry-pick (real hunks via git 3-way), oldest first. Equivalence evidence = landed `git hash-object`
equals the head's blob OID, so the residual diff of landed-vs-head is empty by construction. Merge-tree clean
for both against current automation; the touched files were unchanged on automation since the common
merge-base `4c1eb7da6b282109f84a9130b500746453d33aa3` (`git rev-list --count` = 0 each). No conflict, no rebase.

### A2 — derived affected suites green + static gates clean

```
$ ./node_modules/.bin/vitest run src/components/ExpiryEntryForm.test.tsx \
    src/components/shell/import-modal.test.tsx src/routes/AssetDetailPage.test.tsx \
    src/components/shell/shell.test.tsx src/components/catalog/catalog.test.tsx
 ✓ src/components/ExpiryEntryForm.test.tsx  (2 tests)
 ✓ src/components/shell/import-modal.test.tsx  (14 tests)
 ✓ src/routes/AssetDetailPage.test.tsx  (13 tests)
 ✓ src/components/catalog/catalog.test.tsx  (33 tests)
 ✓ src/components/shell/shell.test.tsx  (23 tests)
 Test Files  5 passed (5)      Tests  85 passed (85)      VITEST_EXIT=0

$ npm run lint     # eslint src      -> LINT_EXIT=0
$ ./node_modules/.bin/tsc --noEmit   -> TSC_EXIT=0
```
No full end-to-end sweep (packet: none). No red anywhere; no drive-by fixes needed. Full suite run: none
by instruction.

### A3 — diff file list == the two component files (+ worklogs)

```
$ git diff --stat origin/automation..HEAD
 frontend/src/components/ExpiryEntryForm.tsx        | 55 ++++++++++++++++++++--
 frontend/src/components/shell/AssetImportModal.tsx | 15 +++++-
 2 files changed, 64 insertions(+), 6 deletions(-)
```
Product diff is exactly the two component files; the only other writes are `docs/worklogs/SG-161_*`. A secret
scan over added lines (`CO-100`) matched nothing (`secret_scan_exit=1`).

### A4 — report + receipt read back on remote; no production write

- Report committed at `docs/worklogs/SG-161_report.md` (tracked; `CO-57`), with `SG-161_verify.log` and
  `SG-161.log`.
- Receipt note published on `refs/notes/storagegenie-coder-reports` anchoring **WORK_HEAD**
  `ba3827ebe29151c7a97376280e4002ceb2fb46c0`, first line carries BOTH `Dispatch-ID:` and `Report:` (`CO-97`);
  read back via a mapped fetch — verbatim block pasted in the receipt section below (this report does not
  carry its own commit hash, `CO-55b`).
- Production writes: none. Proven by the diff file list above (two frontend files) plus tip movement limited
  to this slice's commits (G0, G1, docs) on `automation`; no datastore, no migration, no deploy.

## Receipt

Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no
`{{RECEIPT_CMD}}` product-script run (legacy finalize refused on this lane, retired per `AGENTS.md`); the
Coder publishes the notes-ref receipt. Note published on `refs/notes/storagegenie-coder-reports` anchored on
**WORK_HEAD** `ba3827ebe29151c7a97376280e4002ceb2fb46c0` and, dual-annotation (`SG-092` precedent), on the
docs tip; read back via a **mapped** fetch. Executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show ba3827ebe29151c7a97376280e4002ceb2fb46c0
error: no note found for object ba3827ebe29151c7a97376280e4002ceb2fb46c0.
existing_note_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-161 | Report: docs/worklogs/SG-161_report.md | Work-HEAD: ba3827ebe29151c7a97376280e4002ceb2fb46c0" ba3827ebe29151c7a97376280e4002ceb2fb46c0
add_wh_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-161 | Report: docs/worklogs/SG-161_report.md | Work-HEAD: ba3827ebe29151c7a97376280e4002ceb2fb46c0" <docs-tip>
add_tip_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   7068ebb..621a42e  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg161-fetched
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/sg161-fetched
fetch_exit=0
$ git notes --ref=refs/notes/sg161-fetched show ba3827ebe29151c7a97376280e4002ceb2fb46c0
Dispatch-ID: SG-161 | Report: docs/worklogs/SG-161_report.md | Work-HEAD: ba3827ebe29151c7a97376280e4002ceb2fb46c0
show_wh_exit=0
```

`<docs-tip>` is the report's own commit, which cannot be named in the report (`CO-55b`). `work commit:
ba3827eb…` is the product commit; the committed verify log cites it as `WORK_HEAD`, not the tip (`CO-55c`).

## INTENT

`INTENT: code does apply the two audited PR head trees verbatim onto automation; the check expects the landed
blob OID to equal the head blob OID and the affected suites to stay green; the approved packet (G1/G2) says
exactly that.` X, Y, Z agree — no item stopped.

## TWINS

Not applicable — this is a mechanical merge of external bytes, not a defect fix; no wrong construct to search
for (`CO-17`). No out-of-scope sites exist for the construct "landed blob != head blob": both are equal.

## Vacuity check (`PB-3`)

No criterion can pass vacuously: A1 compares two concrete OIDs per PR (both non-empty, equal); A2 ran a
non-empty derived set (5 files, 85 tests) with a nonzero exit on any failure plus two static gates that
exit nonzero on failure; A3's ceiling is a 2-file product diff (not an empty diff); A4's note was read back
from a mapped fetch of the remote ref. The failing possibility was real in every gate (e.g. a blob mismatch
would print DIFFER, a lint/tsc error would set a nonzero exit).

## UNCLEAR

- **FIRST READ:** the packet names 2 test files; `PB-7` requires deriving the set from what changes. I read
  the touched-markup grep as authoritative and ran 5 files, treating the packet's list as the floor, not the
  set. `ReviewPage.tsx` renders `ExpiryEntryForm` but its test never drives it, so I did not add it — stated
  rather than silently omitted.
- **DURING EXECUTION:** `npx` is absent (F-SG161-4); used the local binaries. `CO-25` FAIL-then-PASS has no
  target here because neither PR adds a test and the changed files' tests are green both sides — I disclosed
  this (F-SG161-3) instead of manufacturing a test outside the scope ceiling.
- **REMAINING:** nothing owed by this slice. The bundle is on disk only; the served change rides SG-165.
  Later slices (#44, #46, #47, #48, #49) are untouched here per the packet. `.rules-cache/` absence
  (F-SG161-2) is a carry-over environment finding for reconciliation.
