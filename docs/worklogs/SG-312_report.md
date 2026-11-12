SG-312 | model opencode-go/claude-haiku-5-5 | effort high (both read from the process arguments: `opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/claude-haiku-5-5 --variant high`) | cwd /home/andrei/StorageGenie | remote origin git@github.com:Andovol/StorageGenie.git | BASE ref origin/automation -> resolved 80011d0d8503e17daf9781d3add4106059469d57 | WORK_HEAD 80dce07ca9583dd54354d47ef462669c65ec1887 (this report's commit follows it)

# SG-312 report: paper ground, the font in controls, Inbox and asset page in plain words

**Result: G0, G1, G2, G3 done and green. G4 (screenshots) NOT done: the run went past the 1100 s stop line (see Elapsed). Verification: FAIL.**

## Elapsed and phase seconds (stamps from `date +%s`)

- Start 1794495499.
- G0 preflight 1794495499 to 1794495506 (7 s): `docker version` shows a Server section, rc 0; `docker run --rm busybox true` rc 0; health 200 at start.
- G2 tests written and FAIL-on-base run 1794495506 to 1794495769 (about 260 s, including two harness fixes and the FAIL log).
- G1 fixes, named test updates, PASS run and tsc 1794495769 to 1794495910 (about 140 s).
- G3 gate 1794495936 to 1794496083 (about 147 s).
- G4 1794496110 to 1794496722: the scratch-server launch command did not return and hit the 600 s tool timeout. This overran the 1100 s stop line by about 120 s. The servers were stopped by PID and the scratch folder removed at 1794496722.
- Health on 8003 is 200 at start and at end (1794496722 and 1794496755).

## Premises, confirmed or falsified (file:line as read before the edits)

- **I1 confirmed.** `frontend/src/theme/tokens.css:88-89` painted `hsl(var(--background))` on `body`. `frontend/src/App.tsx:186` wrapped every route in `bg-background`. `frontend/src/routes/PantryPage.tsx:322` alone set `--paper`. The asset page's Manual expiry card was `bg-card` (white): `frontend/src/components/ExpiryEntryForm.tsx:108`.
- **I2 confirmed by reading, not re-measured.** tokens.css had no control font rule. The Arial reading is SG-311's (`docs/worklogs/SG-311_report.md`); I did not re-read it in a browser (no shot was taken).
- **I3 partly falsified.** `labelStepName` is not in `frontend/src/lib/labels.ts`. It was a local function at `frontend/src/routes/InboxPage.tsx:32-35`. It returned "Review" for AWAITING_REVIEW and title-cased everything else; it did not produce uppercase words. The raw timestamp at `frontend/src/components/JobCard.tsx:53` is confirmed. Item names: `ReviewTask` (`frontend/src/api/types.ts:149-162`) carries only `subject_ref` and `subject_kind`, so the task data does not carry a name. Asset names come from the existing read `GET /v1/assets/{id}` (`useAsset`). Candidate names come from the existing read `GET /v1/candidates/{id}` (the same route and query key as `frontend/src/routes/ReviewPage.tsx:50`). No backend byte changed.
- **I4 confirmed.** The Menu button had no `nav-menu-toggle` class (`frontend/src/App.tsx:89-108`). The rule already existed at `tokens.css:276-288` and was never applied.
- **I5 confirmed, location corrected.** "Expiry evidence state" is in `frontend/src/components/ExpiryEntryForm.tsx:110`, not in AssetDetailPage. "per-press cap" is `frontend/src/routes/AssetDetailPage.tsx:116` (EnrichButton). "qty" is `AssetDetailPage.tsx:588`.
- **I6 confirmed.** `frontend/src/routes/ExpiryPage.tsx:33-34` labelled critical "Critical" and urgent "Urgent". The pill was pinned by `marginLeft: "auto"` at `ExpiryPage.tsx:85`.
- **Step names.** The backend steps are in `backend/app/services/job_service.py:19-25`: NORMALIZING, EXTRACTING_DETERMINISTIC_SIGNALS, DEDUPLICATING, COMMITTING, AWAITING_REVIEW.
- **Contract.** `CODER.md` section 14 (PB-1 to PB-6) was not read: the contract folder is denied on this lane.

## How each G1 line was met

- **G1.1 paper.** `tokens.css` body `background-color` is now `hsl(var(--paper))` (the one ground). The App shell wrapper (`App.tsx`) uses inline paper in place of `bg-background`. The Pantry's redundant wrapper background is removed (`PantryPage.tsx:322`). Panels on the Expiry and asset pages moved to paper with a `--line` border: the Manual expiry card (`ExpiryEntryForm.tsx`), the asset page's Edit panel (`AssetDetailPage.tsx`), and the opened-window pill (`OpenedCountdownSection.tsx`).
- **G1.2 font.** `tokens.css`, after the body rule: `button, input, select, textarea { font: inherit; }`. Side effect not measured: a control with no explicit font-size now takes the body size, not the browser's 13.33 px default.
- **G1.3 Inbox.** Step names are in `labels.ts` as `labelStepName`: EXTRACTING_DETERMINISTIC_SIGNALS "Checking the file", NORMALIZING "Tidying the details", DEDUPLICATING "Looking for duplicates", COMMITTING "Saving", AWAITING_REVIEW "Your review". Unmapped names become sentence case. The job date is `formatJobDate`: "5 Mar, 14:42", or "Today, 14:42" on the same local day, or "" if unreadable. Review rows show the subject's name from the existing reads above, or "Unnamed item" (`TaskSubjectName` in `InboxPage.tsx`). Candidates with no `display_name` also show "Unnamed item".
- **G1.4 Menu.** The Menu button has `nav-menu-toggle`. The existing rule in `tokens.css` shows it below 768 px and hides it at and above. Proven by test (class plus CSS rule), not by a 1280 or 375 render. The one-row header at 375 px is UNVERIFIED: there was no screenshot.
- **G1.5 asset page.** "Expiry evidence state: accepted" is now "Date confirmed" (`labelExpiryState`; other states: "Date to confirm", "Needs a date", "Replaced", "Not kept"). The Enrich line is "Enrich costs up to $0.05 a press". The refusal sentence is unchanged. "Live · qty 500 ml" is now "Live · 500 ml left" via `quantityLeftText`.
- **G1.6 Expiry tiers.** critical is "Use first", urgent is "Use soon", and no tier shows no pill. The pill is a plain label beside the date with `marginLeft: auto` removed. Upcoming, Long lead and Safe are unchanged (not named in G1.6). Owner decision still open.
- **Not changed (as the packet requires):** behaviour, routes, API calls, data, CatalogPage, the item panel, the Pantry beyond its background.

## Test changes (all named)

- New, FAIL on base and PASS on candidate: `frontend/src/theme/sg312-design.sg312.test.tsx` (7 tests), `frontend/src/lib/labels.sg312.test.ts` (10), `frontend/src/routes/sg312-screens.sg312.test.tsx` (10). Total 27.
- Older, updated because they asserted replaced wording:
  - `frontend/src/components/ExpiryEntryForm.test.tsx`: `toHaveTextContent("accepted")` to "Date confirmed"; "needs_evidence" to "Needs a date"; "proposed" to "Date to confirm". Reason: state labels.
  - `frontend/src/routes/AssetDetailPage.test.tsx`: the Enrich test title "with the last measured spend and cap" renamed to "with the plain cost line"; the two `Last measured spend: ... per-press cap ...` assertions now expect "Enrich costs up to $0.05 a press". The refusal assertions are unchanged. Reason: G1.5.
  - `frontend/src/routes/ExpiryPage.test.tsx`: the tier-pill test renamed; the expected pill list now has "Use first", "Use soon" (not "Critical", "Urgent") and asserts no "No tier" pill. Reason: G1.6.
  - `frontend/src/routes/InboxPage.test.tsx`: the review-row assertions for "item" x2 and "candidate" x1 now expect "Unnamed item" x3 and no bare "item" or "candidate". Reason: G1.3 (the mock has no names).
- No behaviour test was changed.

## FAIL-on-base (G2) and PASS

- FAIL on the tree before G1 (`origin/automation` 80011d0): 26 of 27 failed; 1 passed. The passing one is the existing `.nav-menu-toggle { display:none }` rule, kept as a guard. Names and first assertions: `docs/worklogs/SG-312_fail.log`.
- The FAIL-on-base run exposed two harness bugs (`?raw` imports returned an empty string; the Expiry stub lacked the analytics summary). Both were fixed before the logged run. The FAIL log is from the fixed run.
- PASS: the twice-run logs (`SG-312_twice_run1.log`, `SG-312_twice_run2.log`) show the three new files passing, 7 files and 86 tests in each run, which includes the new files. The separate `SG-312_pass.log` file was not written to docs: that run's verbose output was in scratch and was removed. The 27/27 count comes from the tool output of that run, not from a docs log.

## Gate counts (G3), logs in docs/worklogs/SG-312_<step>.log

- eslint on the 17 changed frontend files: 0 errors. One warning, because `tokens.css` was passed to eslint and eslint ignores CSS (`SG-312_eslint.log`).
- `tsc --noEmit`: rc 0 (`SG-312_tsc.log`, empty).
- Frontend build into scratch (`vite build --outDir ...`): rc 0 (`SG-312_build.log`).
- Backend `pytest -m "not requires_native_libs"`: 805 passed, 2 deselected, rc 0 (`SG-312_backend.log`).
- Image proof (`make backend-test-image`, which runs `docker build` on the Dockerfile): rc 0; `pytest -m requires_native_libs tests/test_signals.py` 2 passed, 6 deselected (`SG-312_image.log`).
- Frontend suite `npm test -- --run`: 50 files, 450 tests passed, rc 0 (`SG-312_frontend.log`).
- SG-312 files and every changed older test file, run twice in a row: 7 files, 86 tests in each run, rc 0 both (`SG-312_twice_run1.log`, `SG-312_twice_run2.log`).

## Shot table (G4): NOT TAKEN

- The scratch build with `VITE_API_BASE=http://127.0.0.1:18312` was made. The bundle had 7 hits for `127.0.0.1:18312` and 0 for `8003`. The migrations ran on a scratch database and the backend and frontend started and answered 200. The run then stopped at the budget line before seeding or any shot. No shot, no `INDEX.md`, no DOM proof, no design notes.

## Changed files

26 files, 987 insertions and 45 deletions (`git diff --stat 80011d0..HEAD`). Product: `frontend/src/{App.tsx, lib/labels.ts, components/{JobCard,ExpiryEntryForm,OpenedCountdownSection}.tsx, routes/{InboxPage,ExpiryPage,AssetDetailPage,PantryPage}.tsx, theme/tokens.css}`. Tests: the three new `*.sg312*` files and the four older files named above. Evidence: `docs/worklogs/SG-312_*.log` and this report. No backend, migration, Dockerfile, compose, lockfile, dependency, `.env`, `frontend/dist` or deploy bytes changed (checked with `git diff --name-only`).

## Contract line

No contract line received in this packet's context. The packet states `0.59.0` (`AGENTS.md`, D30) but gives no line of my own to echo, and this lane denies the contract folder, so I did not read it.

## UNCLEAR / REMAINING

- **REMAINING: G4 screenshots (four shots, INDEX.md, DOM proofs, design notes).** Cause: the scratch-server launch held the tool call until its 600 s timeout, which overran the 1100 s stop line.
- **UNCLEAR: the one-row header at 375 px** (G1.4). No render.
- **UNCLEAR: the Arial reading (I2)** is SG-311's; not re-measured.
- **REMAINING: buttons still on the white `--card` token.** AssetDetailPage Edit, Remove (locations and relations), the ExpiryEntryForm Clear button, Pantry tile cards (PantryPage:51, :442, out of scope). Not changed.
- **REMAINING (owner decision): tier names "Upcoming", "Long lead", "Safe"** are unchanged.
- **UNCLEAR: candidate names.** A candidate with no `display_name` shows "Unnamed item".
- **UNCLEAR: `font: inherit` size change** on unsized controls, not measured.
- **Not done: `docs/worklogs/SG-312_pass.log`** (see PASS section above).
- **Not verified: PB-1 to PB-6 text** (contract denied).
- **Vacuity (A7), what I checked:** the FAIL-on-base run showed a non-paper body (the `--paper` assertion fails and `--background` is present), no control font rule, Menu without its class, ISO date instead of "5 Mar, 14:42", raw "COMMITTING"-era label instead of "Saving", and "qty" instead of "500 ml left". Not checked separately: "evidence state" and "per-press" absence (the assertions sit inside tests that failed earlier), and two-shot hash distinctness (no shots). Bundle pointing at 8003: checked on the scratch build (0 hits).

## One line per criterion

- **A1** (G1.1 to G1.6 met, named file, item-name finding stated): partially met. G1.4 has no render; the item names come from existing reads, no backend byte.
- **A2** (FAIL on base, PASS on candidate, older tests named): met, with the `SG-312_pass.log` gap noted above.
- **A3** (gate green with counts, files twice green): met (counts above).
- **A4** (four shots with DOM proofs, distinct hashes, design notes): NOT MET. No shots.
- **A5** (zero backend, migration, Dockerfile, compose, lockfile, dependency, env, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched; no `/tmp`; tree clean, scratch removed): met for the bytes listed (diff check). Scratch removed; `git status --short` is empty before this report. No `/tmp` was used. `output/SG-301-scratch` is another slice's folder and was left alone.
- **A6** (preflight; health 200 start and end; phase seconds): met (above).
- **A7** (vacuity named): partially checked (above).
- **A8** (last line): FAIL, because A4 is not met.

Verification: FAIL — A4 (four screenshots with DOM proofs) not taken; G4 stopped at the budget line after a 600 s hung launch.
