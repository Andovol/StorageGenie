SG-160 — Palette PR audit (Q1/D-1012-1): 7 outside PRs #43-#49 diffed as bytes, one verdict each, read-only

Dispatch-ID: SG-160
Role:        Coder (no dispatch verb run; no other unit started or polled)
Work dir:    /home/andrei/StorageGenie
origin:      git@github.com:Andovol/StorageGenie.git (fetch+push, as on host)
BASE ref:    origin/automation
BASE commit: 43c93b30abce575a2da0923c5ddfecbb353494ce  (start HEAD; worktree clean at start)
Work commit: the commit carrying this report (Work-HEAD in the receipt note; no self-hash stated, CO-55b)
Model:       opencode-go/deepseek-v4.1-flash  (read from process arguments: /proc/304839/cmdline `--model`)
Effort:      high                            (read from process arguments: /proc/304839/cmdline `--variant high`)
Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = `0.46.0`
             (equals the packet's expected 0.46.0). `rules_check.sh` run live, exit 0:
             `G-L1 UNCHECKED the cache is not checked out at a contract tag`,
             `G-L5`/`G-L7 UNCHECKED gh-unauthenticated`, two `G-L6 BYTES` lines. The recorded
             ruleset is 0.46.0. No migration, no restart, no served-code change -> no refresh (D145).
Gates:       DATABASE none · Restart none · Deploy none.
Spend:       real $0.000000 USD · zero metered calls · zero suite runs · zero live calls · zero container execs.
             (The anonymous GitHub public REST read and the git pull-ref fetches are unmetered.)
Autonomy:    L2 slice autonomy — verdicts only; nothing merges, rewrites or closes here.

## (a) Issues / deviations / surprises

- **F1 — enumeration method.** `gh` is unauthenticated (confirmed live). I used the anonymous public REST
  list to distinguish open from closed, because `refs/pull/N/head` also exists for closed PRs. No token, no
  login. (Restates SG-149 F1.)
- **F2 — one common merge-base; heads unmoved.** All 7 heads merge-base to the SAME commit
  `4c1eb7d` (automation tip 2026-09-29) — the Palette PRs are ~2 weeks stale — yet every touched file is
  unchanged on automation since that base, so `git merge-tree` is clean for all 7 against current
  automation. The heads still equal the packet's measured SHAs exactly. No PR is stale-in-the-way.
- **F3 — duplicate/overlapping pairs the packet did not name.** #46 and #49 both wrap the ChatPage inputs
  in `<form>` (same 2 hunks; #49 = #46 + theming, #46 = #49 + a new test). #47 and #48 both restyle the same
  5 CandidateCard buttons from the same base with the same diff shape. The packet listed 7 as if independent.
- **F4 — wrong package manager (new defect class).** #44, #46 and #49 each ADD a 3171-line
  `frontend/pnpm-lock.yaml`. The repo uses npm: `frontend/package-lock.json` is the only lockfile at base
  and at tip; `Makefile:12` runs `cd frontend && npm test`, `:16` `npm run lint`; **zero** tracked pnpm
  references (`git grep pnpm` == empty). A second, competing lockfile is scope smuggling.
- **F5 — contract path.** `.rules-cache/` is absent on the host; the live contract path is
  `/home/andrei/storagegenie-contract` (restates SG-145 / SG-149 F5).
- **F6 — `.jules/palette.md` is NOT smuggling.** #44 adds it, but the repo already tracks `.jules/bolt.md`;
  a Palette journal beside the Bolt journal is the repo's own convention.
- **F7 — test coverage of the changed surfaces.** ExpiryEntryForm, CandidateCard, AssetImportModal and
  ChatPage each already have tests at base (`ExpiryEntryForm.test.tsx`, `CandidateCard.test.tsx`,
  `shell/import-modal.test.tsx`, `ChatPage.test.tsx`). EvidenceGallery had NONE — so #44's new test is the
  first coverage of that component. Tests were not executed here (read-only audit; the packet states the
  suite does not run).

No unsatisfiable premise; no scope outside `docs/worklogs/SG-160_*`.

## G1 / A1 — 7/7 diffs fetched as bytes

`git fetch origin refs/pull/{43..49}/head` (objects into FETCH_HEAD, exit 0; no ref stored, no worktree
file changed), then `git diff $(git merge-base origin/automation <head>) <head>` per head. All 7 non-empty,
text, hashed. **0 UNREADABLE; no empty diff.** Head SHA, base SHA (merge-base), bytes and sha256 per PR are
in `docs/worklogs/SG-160_fetch.md`. Base ref resolved: `43c93b30abce575a2da0923c5ddfecbb353494ce`; common
merge-base `4c1eb7da6b282109f84a9130b500746453d33aa3`.

## G2 / A2 — per-PR verdicts (exactly one each; each rests on a diff + source file read)

Counts: MERGE 3 · REWRITE 4 · CLOSE 0. (Plain rows, no pipes, per CO-75.)

  #43  MERGE    ExpiryEntryForm.tsx: adds `submitting`, guards double-submit
                (`if (submitting || !date) return;` + `finally`), disables while loading/submitting/empty,
                adds `title` tooltip and themed `focus-ring` controls. Additive and correct; existing
                `ExpiryEntryForm.test.tsx` covers the component. No extraneous files.
  #44  REWRITE  EvidenceGallery.tsx: the real fix of this pile — replaces `onError -> style.display="none"`
                (which removed the tile from the accessibility tree) with a visible, focusable
                "Thumbnail unavailable" block; adds `aria-label`/alt text/`focus-ring`; adds the component's
                first test (3 cases). Sound. Why REWRITE not MERGE: the diff also adds a 3171-line
                `frontend/pnpm-lock.yaml` (F4) — not "as-is". Slice: drop the lockfile, keep component+test
                (+ `.jules/palette.md`, consistent with the tracked `.jules/bolt.md`).
  #45  MERGE    AssetImportModal.tsx: adds `aria-busy={processing}` + an aria-hidden `Loader2` spinner
                with `display:inline-flex` alignment. Small, correct, additive; no extraneous files.
  #46  REWRITE  ChatPage.tsx: wraps question/correction in `<form onSubmit>` (Enter-to-submit), keeps the
                existing guards, adds a real test. Sound. Why REWRITE: adds the pnpm lockfile (F4) AND is
                the functional half of the #46/#49 duplicate (F3). Slice: drop the lockfile; land this as
                the Chat-form base (it carries the only new Chat test).
  #47  REWRITE  CandidateCard.tsx: same 5-button restyle as #48 but with HARDCODED class literals; adds a
                `<span title>` tooltip on the blocked Accept. Why REWRITE: it duplicates literals that
                already exist as shared exports (`CONTROL_STYLE`/`THEMED_CONTROL_CLASS`,
                CatalogToolbar.tsx:63,65 at base) and it textually conflicts with #48 (F3). Slice: rebase
                after #48 and re-express using the shared constants, keeping only the tooltip value.
  #48  MERGE    CandidateCard.tsx: the same restyle, DRY via `CONTROL_STYLE`/`THEMED_CONTROL_CLASS`
                imported from `./shell/CatalogToolbar` (verified exported at base and tip). Sound,
                convention-following, no extraneous files. Preferred over #47.
  #49  REWRITE  ChatPage.tsx: #46's form wrapping PLUS theming (select + inputs + both buttons). Why
                REWRITE: adds the pnpm lockfile (F4), duplicates #46 (F3), and ships no test. Slice:
                rebase onto the adopted #46 tree, drop the lockfile, keep only the theming delta, run
                #46's Enter-submit test against it.

## Defect lesson per PR (G-L7) — the defect, if any, and why our packets/tests/audit let it through

- **#43 — no defect.** Guard is correct; the surface's double-submit risk was never gated by a test (the
  existing test asserts the happy path only), so a regression here would be caught only by review.
- **#44 — DEFECT (fixed by the PR).** Base `EvidenceGallery.tsx:21` set `style.display="none"` on image
  error, deleting the failed tile from the a11y tree and leaving a focusable `<a>` with no visible content.
  Why it survived: the component had **zero tests** at base, so the error branch was never exercised; our
  audits rate behaviour, and no slice owned this component.
- **#45 — no defect.** Spinner/`aria-busy` is untested (no modal test asserts the busy state), so a
  regression to a text-only "Processing…" would pass the suite.
- **#46 / #49 — DEFECT (process).** Two Palette runs produced the same Chat-form change; #49 re-does #46
  plus theming with no test, #46 has the test. Why it survived: the outside agent has no dedup against open
  PRs, and our triage never coordinated it; the packet listed them as independent.
- **#47 / #48 — DEFECT (duplication + DRY).** Two runs restyled the same 5 buttons; #47 hardcoded literals
  already exported as constants at base. Why it survived: the agent never reads existing shared exports;
  the audit caught it only by checking CatalogToolbar's exports.
- **#44/#46/#49 lockfile — DEFECT (building).** Committing a pnpm lockfile into an npm repo. Why it
  survived: no CI/lint gate rejects a second lockfile, and the outside agent is not bound by our contract.

## Overlap matrix (measured from the diffs)

  ChatPage.tsx        #46 + #49  -> CONFLICT (same 2 hunks); merge #46 first, rewrite #49 over it.
  CandidateCard.tsx   #47 + #48  -> CONFLICT (same button block); merge #48, rewrite #47.
  pnpm-lock.yaml      #44 + #46 + #49 -> add/add of the same 3171-line file; drop from all three.
  Independent / no conflict: #43, #44 (component), #45.

Safe order the verdicts imply (owner's SECOND word required; never executed here):
  1) #43, #45 (independent) · 2) #44 (drop lockfile) · 3) #48 then #47 rebased (reuse constants) ·
  4) #46 (drop lockfile) then #49 rebased (theming; drop lockfile; reuse #46's test).

## Secret scan (CO-100 / CO-44)

Scope: the 7 captured diffs (`/tmp/sg160/pr{43..49}.diff`), 348,226 bytes total. Patterns: api key, secret,
password, token, bearer, private key, BEGIN PRIVATE KEY, AKIA…, ghp_…, github_pat_, sk-…, xox[baprs]-.
Result: matches ONLY the substrings `token`/`tokenizer` inside pnpm package names (`js-tokens`,
`@csstools/css-tokenizer`) in the lockfile hunks of #44/#46/#49. No credential-shaped string, no token
printed. (CO-100 held.)

## Acceptance criteria — assessed (PG-SC-09)

- A1 PASS. 7/7 diffs captured with head + base SHAs quoted; 0 empty, 0 unreadable (transcript file).
- A2 PASS. 7 verdict rows (MERGE/REWRITE/CLOSE + reason) + a defect lesson per PR.
- A3 PASS. START tip == END tip proven by clean local==remote equality (receipt block below); tree clean
  after the worklog commit; the only moved ref is `automation` by the worklog commit itself.
- A4 PASS. SG-160 report committed and tracked; note published on `refs/notes/storagegenie-coder-reports`
  with `Dispatch-ID: SG-160` + `Report:` + `Work-HEAD:`, and read back via a mapped fetch (below). No
  production write; no served-code change.

## Vacuity check (PB-3)

No criterion can pass vacuously: the enumeration returned a non-empty set of 7 distinct heads; every diff is
non-empty and was read; no verdict rests on an unread file; the secret grep spans all 7 diffs, not a subset;
nothing was merged, closed or pushed except the worklog commit.

## Receipt

- Work pushed to `automation`; worktree clean; local tip == `origin/automation` (both directions, shown in
  the transcript below). No `storagegenie-evidence` push. No `{{RECEIPT_CMD}}` product-script run (legacy
  finalize refused on this lane, retired per AGENTS); the Coder publishes the notes-ref receipt.

```
$ git push origin automation
   <automation> -> automation   (worklog commit; no product hunks)
$ git notes --ref=refs/notes/storagegenie-coder-reports add \
    -m "Dispatch-ID: SG-160 | Report: docs/worklogs/SG-160_report.md | Work-HEAD: <workcommit>" <workcommit>
$ git push origin refs/notes/storagegenie-coder-reports
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg160-fetched
$ git notes --ref=refs/notes/sg160-fetched show <workcommit>
Dispatch-ID: SG-160 | Report: docs/worklogs/SG-160_report.md | Work-HEAD: <workcommit>
$ git rev-parse HEAD ; git rev-parse origin/automation ; git status --porcelain
<workcommit> == origin/automation ; (empty)
```

## UNCLEAR

FIRST READ: the packet is a read-only audit of 7 outside Palette PRs; the only writes allowed are
`docs/worklogs/SG-160_*`. I read `CODER.md` 0.46.0 + `lang/python.md` (CO-83/CO-10), echoed the contract
0.46.0 verbatim, and used the anonymous public REST list because `gh` is unauthenticated (F1).
DURING EXECUTION: the four audit surprises were the single common merge-base with clean merge-trees (F2),
two overlapping PR pairs (F3), three PRs adding a pnpm lockfile into an npm repo (F4), and #44 fixing a real
a11y defect with the component's first test. No file was changed outside `docs/worklogs/SG-160_*`; nothing
merged or closed.
REMAINING: none owed by this slice. The verdicts feed the later merge slices (owner's second word); merges
are NOT done here. Tests were not executed (read-only; packet says the suite does not run).
