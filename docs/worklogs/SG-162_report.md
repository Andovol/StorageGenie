SG-162 — Merge Batch 2 landed unserved: PR#44 (EvidenceGallery a11y error-fallback + first test +
palette journal, MINUS the smuggled pnpm lockfile) and PR#48 (CandidateCard restyle via shared
catalog constants) applied onto automation by their real bytes; every landed blob byte-identical to
its audited head; the lockfile is absent from the tree; derived 5-file vitest set 37/37 green +
eslint/tsc clean; no conflict, no rebase, no head moved; diff exactly the four named product files.
Code changes sit on disk only — they go live on the SG-165 deploy rider, never here.

Dispatch-ID: SG-162
Role:        Coder (no dispatch verb run; no other unit started or polled)
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git (fetch+push, as on host)
BASE (packet ref `origin/automation` -> resolved commit): d97697c23c74bcdd73576cf210afa5d4bbee7884
             (ref requested and resolved commit stated separately; ref == commit this run)
WORK_HEAD:   5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed
             (G1 product commit, PR#48; the G0 product commit is its parent
             20e18a957e40dd1a04ba1df71a5115a4190fd7e8, PR#44)
Model/effort (`CO-78`/`PB-4`, from process arguments): model `opencode-go/deepseek-v4.1-flash`, effort
             `high` — source `/proc/322469/cmdline` (parent `opencode run --auto --dir
             /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high # SG-162 …`).
             No system-prompt identity used.
Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`
             (equals the packet's expected 0.46.0). Checkout HEAD `925cb575c0ef0e1c5a15b6112041a270c2dbd730`;
             payload `RULES.sha256` = `487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef`
             (equals the `487841B1…` pinned in `AGENTS.md`). `rules_check.sh` run live, exit 0:
             `G-L1 UNCHECKED the cache is not checked out at a contract tag`,
             `G-L5`/`G-L7 UNCHECKED gh-unauthenticated`, two `G-L6 BYTES` lines. Recorded ruleset 0.46.0.
Gates:       DATABASE none · Restart none · Deploy none (unserved by design; lands on SG-165).
Spend:       real $0.000000 USD · zero metered calls · zero live calls · zero container execs
             (local git fetch/apply, local vitest, local eslint/tsc — all unmetered).
Live clock (`CO-79`, UTC): start not separately stamped; first command batch ~2026-10-12T14:58:02Z
             (inference from run order, labelled), vitest Start 2026-10-12T14:58:23Z; static gates end
             2026-10-12T14:58:35Z; as-of-report-writing 2026-10-12T14:59Z. Total ~1–2 min, well inside
             RUN_BUDGET_S.
Autonomy:    L2 (merge execution covered by D-1012-1; verdicts from SG-160). Class: CHANGED.

## (a) Issues / deviations / surprises

- **Heads unmoved (`PB-1`).** `refs/pull/44/head` = `03304b130cefa17bc285db6a092755669b43cc05` (packet
  expected `03304b13`) and `refs/pull/48/head` = `33f079f3b691f3321763503100fc656124c44584` (packet expected
  `33f079f3`) — both equal the packet's expectation. No STOP; nothing rebased. Both merge-base to the same
  commit `4c1eb7da6b282109f84a9130b500746453d33aa3`; `git merge-tree` was clean for both against current
  automation (exit 0 each) — re-proved live, not inherited from SG-160.
- **Method chosen for #44 (decided and reported per G1).** **Selected-paths apply**, not cherry-pick-then-
  excise: `git checkout origin/pr/44 -- <3 paths>`. Rationale — the three kept paths' index blobs then equal
  the head's blobs by construction, and the lockfile is never staged even transiently, so there is no window
  in which the smuggled file could be committed. #48 landed the same way over its single path.
- **F-SG162-1 — derived test set larger than the packet's 2-file list (`PB-7`; finding, not a defect).** The
  packet named `EvidenceGallery.test.tsx` + `CandidateCard.test.tsx`. The derived set is **5**: the packet's
  two, plus `routes/ReviewPage.test.tsx` (clicks the touched "Accept"/"Save edits"/"Hold / Unknown"/"Reject"
  buttons and the Split control through `CandidateCard`), `routes/AssetDetailPage.test.tsx` (renders
  `AssetDetailPage`, which mounts `EvidenceGallery`), and `types/product.test.ts` (a grep hit — a test named
  "builds originalUrl on the EvidenceGallery route"; it does **not** drive the component, but it names the
  symbol, so it is run as the floor, stated rather than silently omitted). All 5 green; no red.
- **F-SG162-2 — `.rules-cache/` absent on the host (carry-over, SG-145 F5 / SG-149 F5 / SG-153 F-SG153-2 /
  SG-161 F-SG161-2).** The live contract path is `/home/andrei/storagegenie-contract`; the packet's
  `bash .rules-cache/rules_check.sh` fails `No such file or directory`. Ran against the live path instead.
  Offered for reconciliation.
- **F-SG162-3 — `CO-25` FAIL-then-PASS does not apply to this slice (stated, not silently skipped).** #44
  **adds** the first test for `EvidenceGallery` (so it is a genuine new guard, not a fetched red→green); #48
  adds no test and its changed file already had a green test at base. There is no pre-existing failing test
  for either change to flip, so no manufactured FAIL run was staged (`CO-25`).
- **F-SG162-4 — `npx` is absent on this host (carry-over, SG-161 F-SG161-4).** `which npx` empty; `node`
  v24.14.1 / `npm` 11.11.0 present. Ran `./node_modules/.bin/vitest` and `./node_modules/.bin/tsc` directly,
  and `npm run lint` (which resolves its script through npm). No privileged denial occurred; nothing routed
  around (`PB-2`).
- No command was killed by its bound (`PB-5`). No production write. Nothing outside the scope ceiling changed.

## (b) Actions

- **Changed paths (product):** `.jules/palette.md` (new), `frontend/src/components/EvidenceGallery.tsx`,
  `frontend/src/components/EvidenceGallery.test.tsx` (new, from #44) and
  `frontend/src/components/CandidateCard.tsx` (from #48) — only these four; 167 insertions / 22 deletions.
  **`frontend/pnpm-lock.yaml` was deliberately dropped and does not appear.**
- **Commits:** G0 `20e18a957e40dd1a04ba1df71a5115a4190fd7e8` (land PR#44 minus lockfile); G1
  `5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed` (land PR#48) = WORK_HEAD; then the docs commit carrying
  `docs/worklogs/SG-162.log`, `SG-162_verify.log`, `SG-162_report.md`.
- **Push:** work pushed to `automation`; clean local `HEAD == origin/automation` after push.
- **External / production effects:** none. No deploy, no restart, no container exec, no migration. The four
  files are changed **on disk only** and are not served until the SG-165 rider rebuilds.
- **Durations:** orientation/premise + apply < 30 s; G2 vitest 2.38 s; eslint + tsc ~12 s; close/receipt
  < 30 s. Retry count 0; test-command count 1 (targeted derived suite) + 2 static gates; provider-call count 0.
- **Health delta (`CO-92`): `HEALTH: not run`** — this slice serves no server and the packet sets DATABASE
  none / Restart none / Deploy none; the running container is untouched, so a start/end probe would add
  nothing. Recorded as deliberately-not-run rather than claimed unchanged.
- **Highest-impact action:** landing PR#44's EvidenceGallery fix (the pile's one real defect) while proving
  the smuggled lockfile never entered the tree, plus proving PR#48 byte-identical.

## (c) Verification

### A1 — #44 minus lockfile (per-blob equivalence + lockfile absence) and #48 blob-identical

```
$ git checkout origin/pr/44 -- .jules/palette.md frontend/src/components/EvidenceGallery.tsx \
      frontend/src/components/EvidenceGallery.test.tsx            # exit=0
44 .jules/palette.md                                 landed=49178626778a0fa56e0a4d02f2c539f44518c9b3 head=49178626778a0fa56e0a4d02f2c539f44518c9b3  IDENTICAL
44 frontend/src/components/EvidenceGallery.tsx       landed=564156dd8cf28dc883ffdc3ca460e974b0730692 head=564156dd8cf28dc883ffdc3ca460e974b0730692  IDENTICAL
44 frontend/src/components/EvidenceGallery.test.tsx  landed=b782dc4f7606ab8c16925ce964555b893a72146d head=b782dc4f7606ab8c16925ce964555b893a72146d  IDENTICAL
$ git checkout origin/pr/48 -- frontend/src/components/CandidateCard.tsx   # exit=0
48 frontend/src/components/CandidateCard.tsx landed=a3784b29bba669f63a8d4b79a232b63b5db4c252 head=a3784b29bba669f63a8d4b79a232b63b5db4c252  IDENTICAL
```

Head SHAs applied: #44 `03304b130cefa17bc285db6a092755669b43cc05`, #48 `33f079f3b691f3321763503100fc656124c44584`.
Equivalence evidence = landed `git rev-parse :<path>` equals the head's blob OID, so the residual diff of
landed-vs-head is empty by construction (blob identity, `PB-3`-safe: non-empty concrete OIDs, both sides).

Lockfile absence (both in the index and across the whole tree):
```
$ git ls-files --error-unmatch frontend/pnpm-lock.yaml
error: pathspec 'frontend/pnpm-lock.yaml' did not match any file(s) known to git   # exit=1 (absent)
$ git diff --cached --name-only | grep -i pnpm      # exit=1 (nothing staged)
$ git ls-files | grep -i pnpm                       # exit=1 (no pnpm lockfile anywhere in HEAD)
$ git ls-files | grep -iE lock                      # backend/requirements.lock · frontend/package-lock.json
```
The head added a 3171-line `frontend/pnpm-lock.yaml` (blob `f72d46aa5686a06ac2ce95e479584e7a8355d6b6`);
that exact blob is **not** in the landed tree. `frontend/package-lock.json` remains the repo's only frontend
lockfile (`Makefile:12` `cd frontend && npm test`, `:16` `npm run lint`).

### A2 — derived affected suites green + static gates clean

```
$ ./node_modules/.bin/vitest run \
    src/components/EvidenceGallery.test.tsx src/components/CandidateCard.test.tsx \
    src/routes/ReviewPage.test.tsx src/routes/AssetDetailPage.test.tsx src/types/product.test.ts
 ✓ src/types/product.test.ts                (12 tests)   8ms
 ✓ src/components/EvidenceGallery.test.tsx  ( 3 tests) 172ms
 ✓ src/components/CandidateCard.test.tsx    ( 5 tests) 336ms
 ✓ src/routes/ReviewPage.test.tsx           ( 4 tests) 415ms
 ✓ src/routes/AssetDetailPage.test.tsx      (13 tests) 938ms
 Test Files  5 passed (5)      Tests  37 passed (37)      VITEST_EXIT=0

$ npm run lint                       # eslint src      -> LINT_EXIT=0
$ ./node_modules/.bin/tsc --noEmit                    -> TSC_EXIT=0
```
No full end-to-end sweep (packet: none). No red anywhere; no drive-by fixes needed. Full log:
`docs/worklogs/SG-162_verify.log`. Non-hits considered and excluded: `theme.test.tsx` and
`HouseholdSelector.test.tsx` reference `focus-ring`, but on `ThemeToggle` / a `selectClassName` prop — they do
not drive either changed component.

### A3 — diff file list == the named files (+ worklogs); no pnpm-lock anywhere

```
$ git diff --name-status origin/automation..HEAD
A	.jules/palette.md
M	frontend/src/components/CandidateCard.tsx
A	frontend/src/components/EvidenceGallery.test.tsx
M	frontend/src/components/EvidenceGallery.tsx
```
Exactly the four named product files (`EvidenceGallery.tsx` + its test + `.jules/palette.md` + `CandidateCard.tsx`);
the only other writes are `docs/worklogs/SG-162_*`. **No `pnpm-lock.yaml` in the diff** (would have been a STOP).
A secret scan over added lines (`CO-100`) matched nothing (`secret_scan_match_exit=1`, 171 added lines scanned).

### A4 — report + receipt read back on remote; no production write

- Report committed at `docs/worklogs/SG-162_report.md` (tracked; `CO-57`), with `SG-162_verify.log` and
  `SG-162.log`.
- Receipt note published on `refs/notes/storagegenie-coder-reports` anchoring **WORK_HEAD**
  `5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed`, first line carrying BOTH `Dispatch-ID:` and `Report:` (`CO-97`);
  read back via a mapped fetch — verbatim block pasted in the receipt section below (this report does not
  carry its own commit hash, `CO-55b`).
- Production writes: none. Proven by the diff file list above (four frontend/journal files) plus tip movement
  limited to this slice's commits (G0, G1, docs) on `automation`; no datastore, no migration, no deploy,
  no container exec.

## Receipt

Work pushed to `automation`; worktree clean (`CO-55`). No `storagegenie-evidence` push, no `{{RECEIPT_CMD}}`
product-script run (legacy finalize refused on this lane, retired per `AGENTS.md`); the Coder publishes the
notes-ref receipt. Note published on `refs/notes/storagegenie-coder-reports` anchored on **WORK_HEAD**
`5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed` and, dual-annotation (`SG-092` precedent), on the docs tip; read
back via a **mapped** fetch. Executed output, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed
error: no note found for object 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed.
existing_note_exit=1

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-162 | Report: docs/worklogs/SG-162_report.md | Work-HEAD: 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed" 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed
add_wh_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-162 | Report: docs/worklogs/SG-162_report.md | Work-HEAD: 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed" <docs-tip>
add_tip_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg162-fetched
$ git notes --ref=refs/notes/sg162-fetched show 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed
Dispatch-ID: SG-162 | Report: docs/worklogs/SG-162_report.md | Work-HEAD: 5592d6a05da9a457fb0b51a30c1a5ae9aa3acbed
show_wh_exit=0
```

`<docs-tip>` is the report's own commit, which cannot be named in the report (`CO-55b`). `work commit:
5592d6a0…` is the product commit; the committed verify log cites it as `WORK_HEAD`, not the tip (`CO-55c`).

## INTENT

`INTENT: code does apply the two audited PR head trees verbatim onto automation, dropping exactly the
smuggled lockfile from #44 and nothing else; the checks expect each landed blob OID to equal its head blob OID,
the lockfile to be absent, and the derived affected suites to stay green; the approved packet (G1/G2) says
exactly that.` X, Y, Z agree — no item stopped.

## TWINS

Not applicable — this is a mechanical merge of external bytes, not a defect fix; no wrong construct to search
for (`CO-17`). No out-of-scope sites exist for the construct "landed blob != head blob": all four are equal.

## Vacuity check (`PB-3`)

No criterion can pass vacuously: A1 compares concrete non-empty OIDs per path (all equal) and the
lockfile-absence check fails closed (`exit=1` on a file known to git — a present lockfile would return exit 0);
A2 ran a non-empty derived set (5 files, 37 tests) with a nonzero exit on any failure plus two static gates that
exit nonzero on failure; A3's ceiling is a 4-file product diff (not empty) and the pnpm grep would match a
smuggled file; A4's note was read back from a mapped fetch of the remote ref. The failing possibility was real
in every gate.

## UNCLEAR

- **FIRST READ:** the packet lands #44-minus-lockfile and #48 (unserved) — a merge slice covered by D-1012-1,
  verdicts from SG-160. It names 2 test files as `PB-7`-style expectation; `PB-7` itself is **not** named in
  the packet, but G2 instructs "grep and add every hit — a hit is a file", so I derived the set (5 files) and
  treated the packet's list as the floor. I echoed contract 0.46.0 verbatim from the host path.
- **DURING EXECUTION:** both head SHAs matched the expectation exactly (no STOP); both merge-trees clean.
  Chose **selected-paths apply** for #44 so the lockfile never touches the index. `npx` is absent
  (F-SG162-4); used local binaries. `CO-25` has no target here (F-SG162-3). Health probe deliberately not run
  (no server surface touched). The derived set exceeded the packet's 2 by 3 files (F-SG162-1).
- **REMAINING:** nothing owed by this slice. The bundle is on disk only; the served change rides SG-165.
  SG-163 (#47 rewrite over #48 + #46 minus lockfile) and SG-164 (#49) are untouched here per the packet.
  `.rules-cache/` absence (F-SG162-2) is a carry-over environment finding for reconciliation.
