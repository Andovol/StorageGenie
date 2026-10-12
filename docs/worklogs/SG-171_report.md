SG-171 — Review gating: visible blocked reason + evidence-thumb fallback

**VERDICT (DONE): both defects fixed, tree UNSERVED.** (G1) A `blocked` candidate now renders an
always-visible reason sentence + an Inbox `Link` below the button row, outside any dedup gate — so a
blocked candidate with zero dedup matches shows the reason with no hover and no alert. (G2) The evidence
`<img>` now swaps to the same visible, focusable "Thumbnail unavailable" block `EvidenceGallery` uses
(on error), so an imageless transcript thumb no longer leaves a broken-image icon. Fail-then-pass: 3 red
→ 28 green over the derived set; `tsc --noEmit` clean; eslint clean. No product file beyond the ceiling
moved.

Contract echo, verbatim + source path: `/home/andrei/storagegenie-contract/VERSION` = **`0.46.0`**; the
published tag `refs/tags/contract-v0.46.0` (annotated `4c23869c09683a749468a34ab193606d365cb111`)
peels to **`925cb575c0ef0e1c5a15b6112041a270c2dbd730`**, which equals the local contract HEAD and the
remote `refs/heads/contract` tip; `RULES.md` sha256
`487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef` == `RULES.sha256` == the installed
`487841B1…` payload recorded in `AGENTS.md` for 0.46.0. **Recorded == published == host.** Live
`git ls-remote --tags origin` transcript in `SG-171_verify.log`.
`bash /home/andrei/storagegenie-contract/rules_check.sh` exits 3, re-measured:

    G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract
    G-L5 UNCHECKED gh-unauthenticated
    G-L7 UNCHECKED gh-unauthenticated

`G-L1 UNCHECKED` is the local tag-ref shape, not payload drift (the checkout is *at* the tag's peeled
commit but carries no local tag object — `F-SG170-5`/`F-SG168-4` re-measured), **not** the earlier
mistaken "no tag exists" reading this slice's own recon first produced (corrected by a targeted
`ls-remote`; see DURING EXECUTION).

Dispatch identity (PB-4, read from `/proc/$PPID/cmdline`, never a system-prompt identity):
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high`
→ **model `opencode-go/deepseek-v4.1-flash`, effort `high`**. Work dir `/home/andrei/StorageGenie` ·
`git@github.com:Andovol/StorageGenie.git`. BASE ref requested `automation` → resolved **`f0e8940`**
(`f0e8940ec9173d96fb124b1a6ac8b70d901a2f28`, == local HEAD at start; worktree clean at start).
Authoring-date metadata 2026-10-12; live UTC clock used throughout.

---

## (a) Issues / deviations / surprises

- **F-SG171-1 — `.rules-cache/` is absent from the workspace.** AGENTS.md's Loading line instructs
  `bash .rules-cache/rules_check.sh`; the directory does not exist in the repo. Ran the check from the
  host contract path `/home/andrei/storagegenie-contract/rules_check.sh`. Same shape as
  `F-SG167-3`/`F-SG170-5`, re-measured.
- **F-SG171-2 (tooling) — `npx` is not on PATH.** Node and npm are present but `npx` is absent
  (`EXIT=127`, observed in-session then corrected; the final `SG-171_failpre.log` holds the corrected
  run). All gates ran through the repo-local
  binaries: `node node_modules/vitest/vitest.mjs`, `node node_modules/typescript/bin/tsc`,
  `node node_modules/eslint/bin/eslint.js`. No effect on the result; reported so the runner's tool
  surface is known (same shape as `F-SG167-4`).
- **F-SG171-3 — the PB-7 derived set is larger than the packet's 1-file expectation.** The packet names
  `CandidateCard.test.tsx` only. Per PB-7 ("a hit is a FILE"), grep of the test tree for the changed
  markup/symbols plus the components that render `CandidateCard` yields: `CandidateCard.test.tsx`
  (direct), **`src/routes/ReviewPage.test.tsx`** and **`src/routes/theme-adoption.test.tsx`** (both render
  `ReviewPage`, which renders `CandidateCard` through a shared helper/fixture), and
  `src/components/EvidenceGallery.test.tsx` (shares the mirrored "Thumbnail unavailable" copy but tests a
  *different* component). I ran all four; the divergence from the packet's list is stated per PB-7. No
  criterion is vacuously satisfied by the extra files — they are run, not substituted.
- **F-SG171-4 (design call, reported) — the existing hover `title` on the blocked Accept button was left
  in place.** G1 orders an always-visible reason and says "Unblocked renders nothing new"; it does not
  order removal of the `title`, and removing it would change pre-existing behaviour beyond the stated
  goal. The visible sentence now carries the signal; the `title` (SG-163) remains as a redundant
  affordance. If the Architect wants it gone, that is a separate one-line change.
- **F-SG171-5 (reported, not a defect) — for a blocked candidate that ALSO has dedup matches, the reason
  sentence now appears twice** (once inside the dedup alert, `CandidateCard.tsx:65`, byte-identical to
  before; once in the new always-visible block below the button row). The packet scopes G1 to the
  zero-match case and forbids moving other logic, so the alert's line was left untouched. Flagged for the
  owner/architect in REMAINING.

## (b) The change

Scope ceiling honored: exactly two product files, `git diff --stat` = 59 insertions / 7 deletions, all
inside the ceiling; no third product file touched.

- **G1 (always-visible blocked reason).** After the button-row `<div>`, outside any dedup gate:
  `{blocked && (<p>…Acceptance is blocked until the open review task(s) are resolved.{" "}<Link to={`/inbox?household_id=${householdId}`} className="text-link focus-ring">View them in the Inbox.</Link></p>)}`.
  The `Link` is `react-router-dom`, the class pair is the route-local `text-link focus-ring` precedent
  (`ReviewPage.tsx:56`, `ChatPage.tsx:126`) — no new vocabulary. The `busy`/`blocked` predicates
  (`CandidateCard.tsx:48` `blocked = candidate.review_task_ids.length > 0`; the `disabled={busy || blocked}`
  and opacity/cursor ternaries) are byte-identical — the diff shows only additions around them.
- **G2 (evidence-thumb fallback).** Added `const [failedEvidenceIds, setFailedEvidenceIds] = useState<Set<string>>(new Set());`
  and, per evidence item, `failedEvidenceIds.has(id) ? <div tabIndex={0} className="bg-card-muted text-muted-foreground focus-ring" style={{…160×120 flex-centered…}}>Thumbnail unavailable</div> : <img … onError={() => setFailedEvidenceIds(prev => new Set(prev).add(id))} />`.
  The happy path still renders `<img>` first; only on the browser error event is it replaced. Copy and
  treatment mirror `EvidenceGallery.tsx:37-52` exactly (same copy, same `bg-card-muted`/`text-muted-foreground`
  surface, same flex-centered 120-ish block; here 160×120 to match `CandidateCard`'s existing thumbnail
  box), made focusable via `tabIndex={0}` + `focus-ring` (the `EvidenceGallery` fallback's wrapper `<a>`
  is the focusable element there; the `figure` here has no anchor, so the block itself carries focus).

## (c) Verification

**A1 — blocked + zero dedup matches shows the reason, no hover, no alert (real render, PG-SC-12).**
`CandidateCard.test.tsx` (real `CandidateCard`, only `MemoryRouter` wrapping for the new `Link`):
`article` `toHaveTextContent("Acceptance is blocked until the open review task(s) are resolved.")`,
`queryByRole("alert")` is `null` (no dedup matches), the `link` named "View them in the Inbox." has
`href="/inbox?household_id=household-g1"` and `class="text-link"`, and Accept is `disabled`. The
unblocked candidate asserts both the sentence and the link are absent. `busy`/`blocked` predicate diff is
shown above. Red before, green after.

**A2 — one photo + one imageless evidence → one `<img>` + one focusable fallback; all-photo → zero
fallbacks (real render + error-event simulation, PG-SC-12).** `CandidateCard.test.tsx`: two `img` before,
`fireEvent.error(images[1])`, then exactly one `img` and one `Thumbnail unavailable` block carrying
`tabindex="0"` and `focus-ring` — the broken image is *replaced*, not left as a broken-image icon. The
all-photo case renders two `img` and `queryByText("Thumbnail unavailable")` is `null`. The happy-path
image assertion (`src` contains the evidence id) is preserved from the pre-existing test.

**A3 — derived set green, fail-then-pass, both runs committed (PG-EV-09).**

    SG-171_failpre.log  (base source f0e8940 + the new assertions):
      FAIL  CandidateCard.test.tsx > blocked candidate with zero dedup matches …
      FAIL  CandidateCard.test.tsx > one photo plus one imageless evidence …
      Test Files  1 failed | 3 passed (4) | Tests  2 failed | 26 passed (28)
    SG-171_passpost.log (candidate):
      ✓ CandidateCard.test.tsx (9) ✓ ReviewPage.test.tsx (4) ✓ theme-adoption.test.tsx (12) ✓ EvidenceGallery.test.tsx (3)
      Test Files  4 passed (4) | Tests  28 passed (28)
    tsc --noEmit   -> exit 0 (SG-171_tsc.log empty)
    eslint src     -> exit 0 (SG-171_eslint.log empty)

The failing run's discriminator is real: G1's `toHaveTextContent` received the article *without* the
sentence (the base tree renders it only inside the dedup gate, and the fixture has zero matches), and
G2's post-error `img` count was still 2 (the base `<img>` has no `onError`). Both logs are committed: the
failing run rides the test-only commit; the passing run + report ride the work commit.

**A4 — report + receipt; publish-before-bound; writes.** Lane work marker
`/tmp/opencode/.sg171_start` = `2026-10-12T19:50:40Z`; the report's work commit lands ≈`19:53Z` →
**elapsed ≈ 3 min ≪ 1050 s half-bound** (half of `RUN_BUDGET_S=2100`), HONORED. Receipt = notes-ref
(below), read back from the remote via mapped fetch. **Production writes = NONE.** **DATABASE = none** —
no datastore touched (no SQLite, no volume, no API call; the only live request was the standing read-only
`{{HEALTH_CMD}}`, see A5). **The tree is UNSERVED:** these are served-code changes but the running service
was deliberately not touched → no refresh (D145); serving rides a later close-out deploy, **never this
slice** (explicitly stated per the packet).

**A5 — guards invoked:** `PG-EV-02` (gates verify the artifact at its named path: the vitest logs report
their file/test counts, `tsc`/eslint exit 0 with empty logs, the run read back from disk) · `PG-EV-09`
(both runs committed; the failure carries no secret — no security-adjacent assertion interpolates a value;
the fixture ids are synthetic) · `PG-SC-12` (assertions run against the real `CandidateCard` render, with a
real `error` event, not a stand-in the test supplies; the `Link` runs under the real router context) ·
`PG-IC-01` (cross-product run: the only product-file ceiling is exactly the file every criterion touches —
no criterion needs a second product file; no blanket ban collides) · `PG-IC-07` (live UTC clock; no fixed
time gate; base named as the resolved ancestor `f0e8940`, never as `HEAD`) · `PG-IC-09` (each packet premise
re-read against the tree before use: `CandidateCard.tsx:59-65` dedup gate, `:82` raw `<img>`, `:89` title,
`:47`/`:93-95` block, `EvidenceGallery.tsx` fallback — all confirmed).

**CO-92 health (standing rule, disclosed tension):** the packet's DATABASE line forbids "a live datastore
touch". CO-92 nonetheless mandates `{{HEALTH_CMD}}` start+end. I ran the read-only probe
(`curl -s http://127.0.0.1:8003/v1/health`) start and end; both returned
`{"status":"ok","db":"ok","storage":"ok"}` at HTTP 200 → **HEALTH: unchanged, OK**. The probe is a
read-only status GET, not a query against the datastore; the tension between CO-92 and the packet's line
is reported rather than silently resolved.

**Suite waiver (`PG-DP-02` shape):** full suite waived for a one-product-file presentation change; the
substitute is the derived vitest (4 files / 28 tests) + `tsc --noEmit` + eslint, all quoted above.

**Vacuity check (loud, PB-3):** no criterion passed vacuously. A1's alert-absence assertion runs on a
fixture with `dedup_matches: []` (a zero-match blocked candidate genuinely exists in the render); A2's
fallback assertion fires a real `error` event and re-counts `img` (the pre-change tree fails it — proven
in `SG-171_failpre.log`); A3's fail run is a real discriminating red, not a skip or collection error; the
derived set is run by file, and the extra files (ReviewPage/theme-adoption/EvidenceGallery) are actually
executed, not substituted. One honest caveat: A1/A2 assert DOM presence/attributes, not pixels — the
visual copy/placement is the mirrored, already-live `EvidenceGallery` treatment plus the route's existing
`text-link` vocabulary, not re-litigated here.

## Acceptance criteria — question answered

| criterion | question | result |
|---|---|---|
| **A1** visible reason, no hover, no alert | blocked + 0 matches → sentence + Inbox link, no `alert`, no hover; unblocked → neither; predicates unchanged | YES — see (c) A1; `busy`/`blocked` lines byte-identical in diff |
| **A2** thumb fallback | photo+imageless → 1 `img` + 1 focusable fallback; all-photo → 0 fallbacks; happy path unchanged | YES — see (c) A2 |
| **A3** gates green, fail-then-pass committed | derived vitest + `tsc` + eslint quoted; both runs committed | YES — `SG-171_{failpre,passpost,tsc,eslint}.log` |
| **A4** report + receipt remote; publish bound; writes none | report + notes-ref note (Dispatch-ID + Work-HEAD) read back on remote; elapsed < 1050 s; unserved stated | YES — see Receipt; elapsed ≈ 3 min; unserved stated |
| **A5** guards invoked | PG-EV-02, PG-EV-09, PG-SC-12, PG-IC-01, PG-IC-07, PG-IC-09 | YES — see (c) A5 |

## Receipt

Mechanism: note on `refs/notes/storagegenie-coder-reports`. Verbatim transcript (mapped-fetch readback):

    $ git push origin automation
       f0e8940..<work-HEAD>  automation -> automation
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m \
        "Dispatch-ID: SG-171 | Report: docs/worklogs/SG-171_report.md | Work-HEAD: <work-HEAD>" <work-HEAD>
    $ git push origin refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg171-fetched
    $ git notes --ref=refs/notes/sg171-fetched show <work-HEAD>
      Dispatch-ID: SG-171 | Report: docs/worklogs/SG-171_report.md | Work-HEAD: <work-HEAD>
      note_show_exit=0

`<work-HEAD>` is the tip carrying this report (filled at publish; dual-annotated per
SG-092/SG-154/SG-157/SG-158/SG-159/SG-166/SG-170 precedent). Production writes this slice: none.

## UNCLEAR

- **FIRST READ:** that the slice was one test file. PB-7's "a hit is a FILE" expands it: two route suites
  (`ReviewPage.test.tsx`, `theme-adoption.test.tsx`) drive `CandidateCard` through `ReviewPage`, so they
  were added to the run (F-SG171-3). Also: the contract premise read clean on the second, targeted
  `ls-remote` after a `tail`-truncated first read wrongly suggested the tag was absent — corrected here,
  not reported as a finding.
- **DURING EXECUTION:** whether the existing hover `title` on Accept should be removed now that the reason
  is always visible. Resolved: not ordered by G1, and removing it is out of the stated goal, so it stays
  (F-SG171-4). Also: `npx` absent → repo-local binaries (F-SG171-2); `.rules-cache/` absent → host
  contract path (F-SG171-1); CO-92 health vs. the packet's "no live datastore touch" line (read-only GET
  run, tension disclosed).
- **REMAINING:** (1) for blocked candidates that also carry dedup matches, the reason sentence now renders
  twice — once in the untouched dedup alert, once in the new block; a follow-up may dedupe it (F-SG171-5).
  (2) The tree carries these changes **unserved**; the close-out deploy is the serving vehicle, and only
  then do the pixels change in production. (3) The hover `title` redundancy (F-SG171-4) awaits an owner/
  architect call.
