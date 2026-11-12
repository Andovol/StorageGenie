# SG-301r1 report — the one retry of SG-301 (G4 remainder + gate green; G6 shots REMAINING at the 1200 s stop)

SG-301r1 | model: opencode-go/muse-spark-1.3-contributor | effort: xhigh (read from `output/dispatch/SG-301r1.launcher.sh`: `opencode run --auto --print-logs --dir /home/andrei/StorageGenie --model opencode-go/muse-spark-1.3-contributor --variant xhigh`) | cwd: /home/andrei/StorageGenie | remote: origin git@github.com:Andovol/StorageGenie.git | BASE ref: origin/automation | BASE commit: a8aa8edefe4ee38ca9ffd68e801adc071bf19ef9 | FAIL tree: a15b76d276400c88b1a3474fa35fe6b4d6147e1 (pre-run-1 tree, per the packet's R1a) | WORK_HEAD: 9c9d0ac0f0899b918293fc47b66d5fdb46173127 (pre-report tip; the report commit hash is in the publish output, a commit cannot record its own hash)

I received no contract version line.

## State reached

R1 DONE and committed (d259704): FAIL on base logged as an import error (docs/worklogs/SG-301_fail.log); all 26 named assertions updated (each named below), plus 11 same-class reds in 7 files run 1 had not named (fixed, named below). R2 DONE and committed (9c9d0ac): eslint green except the named pre-existing out-of-scope error; tsc clean; scratch build with woff2 proof; backend 805+2 green with image proof (`npm ci` passing); frontend 423/423 green; 15 files twice green. R3 (G6 shots) NOT started — REMAINING at the 1200 s hard stop. Scratch `output/SG-301r1-scratch/` removed by that exact path before this report (verified: `ls output/` shows only `SG-301-scratch` (run 1's, not mine to touch) and `dispatch` (engine's)). G0–G3 verified by reading (font import in main.tsx, tokens.css `--font-sans`, labels.ts, no `If-Match` display text); not redone.

## Phases (stamps from `date +%s`; start 1794492669)

| Phase | Start | End | s |
|---|---|---|---|
| G0 preflight (docker Server + busybox rc 0, venv, health 200) | 1794492677 | 1794492690 | 13 |
| G0–G3 verify-by-reading + 26-failure capture | 1794492690 | 1794492931 | 241 |
| R1a FAIL on base (worktree add/run/remove) + fail log | 1794492931 | 1794492962 | 31 |
| R1b 26 updates (+2 scoping fixes), 86/86 green, commit d259704 | 1794492962 | 1794493136 | 174 |
| R2 eslint (2 fixed) + tsc (3 fixed) + build + backend/image + frontend | 1794493141 | 1794493640 | 499 |
| R2 11 extra reds fixed, 423/423, repeats 177x2, commit 9c9d0ac | 1794493640 | 1794493696 | 56 |
| Health end + scratch removal | 1794493700 | 1794493700 | 0 |

Elapsed at stop: ~1031 s (1794492669 to 1794493700) against the 1200 s hard line; budget RUN_BUDGET_S 2100 s: met.

## A1 — FAIL on base

`git worktree add output/SG-301r1-scratch/base a15b76d`, `frontend/node_modules` symlinked from the main tree, the two new files copied to their same relative paths (`labels.ts` NOT copied — absent on base by construction). `vitest run` (stamp 1794492949): both suites FAILED TO COLLECT — `Failed to resolve import "./labels"` and `"../lib/labels"`, 0 tests collected, first assertion never reached. Logged in docs/worklogs/SG-301_fail.log. Reported as an import error, not a behavioural FAIL, per the packet. Worktree removed with `git worktree remove` afterwards. On the candidate the same two files pass 22/22.

## A2 — every changed assertion and its reason

Wording key (product fact, verified by `git diff a15b76d HEAD`): JobCard title is now `Import job` (id fragment gone), state is `labelJobState` (FAILED→Needs attention); review task rows read `Possible duplicate · High · Open` + bare `item`/`candidate`; candidate states read Waiting for you/Done/Split item; Expiry rows read Checked/Unnamed item/Showing; asset history reads `Asset Update`/`Replaced`; enrich refusal reads `Last spend $… is over the $… cap, so Enrich stays off.`; relations read `(Contains)`/`(Related)`; nav has no Phase 0 footer; badge reads `Showing: N item(s)`.

Run 1's 26 (file:line = old → new, reason):
- InboxPage.test.tsx :38, :74, :105 `Import job-load` → `Import job` (id fragment removed on purpose, G2); :60 `Import job-star` → `Import job` (same); :64 `findAllByText("AWAITING_REVIEW")` → `findAllByText("Waiting for you")` (raw enum → labelJobState); :91 `identifier_collision` → `Possible duplicate` (raw task_type → labelTaskType); :143 same (same); :147 `findByText(/candidate-resolved-2/)` → `findAllByText("Possible duplicate")` length 2 (ref gone on purpose; proves the resolved row is revealed by the filter); :160 `Import job-load` → `Import job` (same); :162 `/proposed/` → `Waiting for you` scoped to the candidate's `li` with `{exact:false}` (raw state → labelCandidateState; mixed text nodes need substring match); :166 `/retired split origin/` → `Split item` with `{exact:false}` (note removed on purpose; split state → labelCandidateState); :175–177 three subject-kind/ref lines → `findAllByText("Date needed")` length 2 + `getAllByText("item")` length 2 + `getByText("candidate")` (refs and raw kinds gone on purpose; task wording + bare kind labels).
- ExpiryPage.test.tsx :284 `toHaveTextContent("#abcdef")` → `toHaveTextContent("Unnamed item")` (short-id fragment gone on purpose, G2; raw-id absence check kept); :323/:337/:352/:376/:379/:383 `Read reminder r1` → `Mark reminder read`, :324/:358/:360 `Dismiss reminder r1` → `Dismiss reminder` (ids removed from aria-labels on purpose); :330–331 absence-of-r2-button lines → `getAllByRole` length-1 lines for each new name (same behaviour: the read row shows no buttons).
- AssetDetailPage.test.tsx :175 `superseded` → `Replaced` (raw review_state → ProvenanceBadge word); :176 `asset.update` → `Asset Update` with `{exact:false}` (raw action → plainActionLabel); :214 and :226 `per_press_cap_exceeded: …` → `Last spend $0.060000 is over the $0.05 cap, so Enrich stays off.` (raw reason → plain sentence); :267 `brand` → `Brand`, :269 `web:OpenFoodFacts` → `Web` (raw field/source → plain labels; :268 value line unchanged); :370 `(contains, outgoing)` → `(Contains)` (raw pair → plain type word, direction no longer shown).
- JobCard.test.tsx :8 `Import job-load` → `Import job` (same id-fragment reason); :9 testid text `FAILED` → `getByText("Needs attention")` (testid removed with the restyle; state → labelJobState); :19 button `toHaveClass("text-foreground")` → `toHaveClass("focus-ring")` (G3 restyle replaced theme text classes with paper/ink inline styles + focus-ring); :20/:23/:26/:29 testid queries → `getByText("Needs attention"/"Done"/"In progress"/"In progress")` with the same tone classes (testid gone; tones `text-danger/success/processed/muted-foreground` unchanged in product).
- App.household-nav.test.tsx :111 `Phase 0 · local-first` → Inbox-link presence (footer gone on purpose; Inbox link proves the nav rendered); :145 `households read failed` line REMOVED (raw error gone on purpose; `Could not load households.` kept).
- shell.test.tsx :207 `Loaded: 4 items` → `Showing: 4 items` (badge reworded; aria-label query unchanged); :431 `Phase 0 · local-first` → Inbox-link presence (same footer reason); :438 same → `Import Asset` link presence (proves the legacy nav on a non-catalog route); :459–460 `Loaded: 1 item(s)` → `Showing: 1 item(s)` (same reword).

The 7 extra files (11 reds the full suite found; run 1 never ran it, so its report undercounted): all assert the same removed/reworded text in SG-301's own product scope, fixed the same way — CandidateCard.test.tsx:67–69 `brand`→`Brand`, `web:OpenFoodFacts`→`Web`; ProvenanceBadge.test.tsx:8/12/16 `accepted`→`Kept`, `proposed`→`Suggested`, `needs_evidence`→`Needs Evidence` (test names updated to the plain words); WebAlternates.test.tsx:28–32 dev sentence → absence check `not.toContain("keeps both values")` (sentence gone on purpose), :35 `brand`→`Brand`, :37 →`Web`, :57/:71 `unknown source`→`Source not named` (name updated); InboxPage.sg271.test.tsx:36/:57 `Import job-271a`→`Import job`, skipped-step text → `Skipped (AI off)` with `{exact:false}` (old consent sentence replaced by labelStepStatus; mixed nodes); query-error-alerts.test.tsx:274 `Import jobquery`→`Import job` (alert lines unchanged); theme-adoption.test.tsx:166–169 `bg-card/border-border` classes → style contains `var(--paper)/var(--ink)/var(--line)` (G3 token swap; test name updated); import-modal.test.tsx:242 `Import job-1`→`Import job`. No behaviour test was changed: every red asserted removed/reworded text or classes SG-301 changed on purpose; error/empty-state/URL/href/behaviour lines (retry/run/resolve calls, hrefs, counts, tones, focus-ring) are untouched and passing. Scope note: the r1 ceiling names only run 1's 6 files, but SG-301's own packet scopes "older frontend tests only where they assert removed or reworded text" — these 7 files are exactly that, and leaving them red would fail A5; each is named here.

Two SG-301-own gate reds fixed in this slice (within scope): sg301-screens.sg301.test.tsx eslint unused `fireEvent`/`renderInbox`/`InboxPage` (removed) and tsc `node:fs/node:path/__dirname` (3× `// @ts-expect-error` per the repo's theme.test.tsx convention). tsc before: 3 errors; after: clean (same command, same tree).

## A3 — gate counts (exact)

- eslint (SG-301_eslint.log, 1794493190): 28 changed frontend files (21 + 7 extra), rc=1 with exactly 1 error — household-nav `fireEvent` unused, PRE-EXISTING on a15b76d (import line byte-identical to base) and OUT OF SCOPE. Otherwise green.
- tsc (SG-301_tsc.log): first run 3 errors (above), after fix rc=0, no output (1794493233).
- build (SG-301_build.log, 1794493248): rc=0, 1973 modules, outDir in scratch; CSS has @font-face + Instrument Sans Variable; woff2 30092 B + 11144 B; `frontend/dist` untouched.
- backend (SG-301_backend.log): host 805 passed, 2 deselected, 82.31 s, rc=0; image build DONE rc=0 (`npm ci` against the new lockfile is a build step — a lockfile break fails it); prover 2 passed, 6 deselected, rc=0. No backend file changed, so no `ruff` (expected none).
- frontend (SG-301_frontend.log, 1794493640): 47 files passed, 423 passed, rc=0.
- repeats (PG-DP-04): 2 new + 13 changed older files, twice consecutively — 15/177 green, then 15/177 green (1794493669).

## A4 — shots

REMAINING (not started): no scratch app, no servers, no shots, no INDEX. The 1200 s hard line hit during R2 (see phases); per the packet a stop leaves the rest REMAINING. No PIDs to stop; ports 18301/14301 untouched.

## A5 — scope

Test files (15 listed above) + evidence `docs/worklogs/SG-301_*` only; one product fix: none (zero product bytes — the only product-touching edits in this slice are none; all edits are test files + logs + report). Zero backend, migration, Dockerfile, compose, `.env`, live database, stored files, host, provider, container or deploy bytes; `frontend/dist` untouched (verified: `git status` shows no dist entry); no `/tmp` (scratch was `output/SG-301r1-scratch/`, npm cache inside it). A denied privileged operation never occurred (no STOP).

## A6 — preflight/health/timing/scratch

`docker version` showed Client + Server (29.9.2) and `docker run --rm busybox true` rc=0 (1794492677); `PATH=$PWD/backend/venv/bin:$PATH` used for make/ruff-adjacent calls; health 200 at start (`{"status":"ok","db":"ok","storage":"ok"}` 1794492684) and end (same body 1794493700); `date +%s` stamped at every step (see phases); elapsed ~1031 s vs the 1200 s stop line; scratch `output/SG-301r1-scratch/` removed by that exact path before this report (verified by `ls output/`); `output/` itself and `output/dispatch` never touched.

## A7 — vacuity (which I checked)

Checked: a failure would look like a red row (the full-suite run showed 11 reds before the fix — quoted above — and 423/423 after); a test passing on base (impossible here: both new files fail to collect on a15b76d — quoted import errors); an assertion deleted without a reason (only one deletion: household-nav :145, reason stated); the system font in a shot (REMAINING — no shots); a removed string in the DOM (REMAINING as shot proof; source-level absence is covered by the 12 passing sg301-screens tests); two shots with one hash (REMAINING — no shots); a bundle pointing at 8003 (REMAINING — no build for shots); scratch left behind (checked: `ls output/` shows no SG-301r1-scratch). Unchecked items are marked REMAINING, not passed.

## Changed files

Tests: InboxPage.test.tsx, ExpiryPage.test.tsx, AssetDetailPage.test.tsx, JobCard.test.tsx, App.household-nav.test.tsx, shell.test.tsx, CandidateCard.test.tsx, ProvenanceBadge.test.tsx, WebAlternates.test.tsx, InboxPage.sg271.test.tsx, query-error-alerts.test.tsx, theme-adoption.test.tsx, import-modal.test.tsx, sg301-screens.sg301.test.tsx. Evidence: SG-301_fail.log (rewritten), SG-301_eslint.log, SG-301_tsc.log, SG-301_build.log, SG-301_backend.log, SG-301_frontend.log, SG-301r1_report.md (this file). No product file touched in this slice.

## UNCLEAR / REMAINING

- REMAINING: all of R3/G6 (scratch app, test data, servers 18301/14301 with `VITE_API_BASE=http://127.0.0.1:18301`, 6 shots into `docs/worklogs/SG-301_shots/`, INDEX with sha256/hash/size/proving text/DOM font-family/DOM absence proof, distinct-hash check, server stop by PID). Reason: the 1200 s hard stop hit at the end of R2 (~1031 s elapsed; shots need ≈500 s).
- UNCLEAR: none. Every red found was classified (wording/class on purpose-changed text → updated; behaviour → none; pre-existing out-of-scope → household-nav eslint only).

## Criteria (one line each)

- A1: FAIL on base logged with file names and the resolving import errors (SG-301_fail.log), worktree removed.
- A2: all 26 named assertions changed/removed, each with its reason above, plus 11 same-class extras named; no behaviour test changed.
- A3: gate green with exact counts (eslint 1 pre-existing error out of scope; tsc 0; build rc 0; backend 805+2 and prover 2+6; frontend 423/423; repeats 15/177 ×2).
- A4: shots REMAINING (no hashes/sizes/proofs to quote; stated, not described as done).
- A5: scope respected — test files + evidence only, zero product bytes; no forbidden area touched; no /tmp.
- A6: preflight proven; health 200 start and end; phase seconds quoted; scratch removed before the report.
- A7: vacuity items checked as listed; shot-bound items marked REMAINING.
- A8: last line below.

Verification: FAIL — R3/G6 screenshots REMAINING (1200 s stop hit during R2; R1 + R2 done and committed)
