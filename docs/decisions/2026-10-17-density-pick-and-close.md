# Density pick (D-8), session close (D-9), and the close record — 2026-10-17

**Owner message, byte-identical (2026-10-17, chat):**

> D1 and D2 as recommended

(In-session decision IDs D1 = the density pick, D2 = close-or-hold; recorded here as D-8 / D-9 to continue the project's decision sequence.)

## D-8 — APPROVED: density Option B (dark focus-ring token fix); C and D not approved

- Adopted: **Option B — dark focus-ring token fix** (`docs/proposals/2026-10-17-density-proposal.md`, option 2).
- What it authorises: the next slice corrects the dark-theme `.focus-ring` contrast (`frontend/src/theme/tokens.css:173`; measured 1.7559:1 dark vs 9.8813:1 light — below the 3:1 non-text contrast floor; simulated fix 7.4784 vs toolbar) and re-verifies every `.focus-ring` surface in both themes. Then **serve**: new product commits will land ⇒ the D-5 conditional close re-serve becomes due.
- NOT approved: **Option C** (native default-button faces off-token in dark, `SG-199_report.md:14`) — stays open, may be proposed again; **Option D** (width-adaptive default) — needs an owner requirement (threshold / persistence / scope) before any work.
- Option A (leave-it) is superseded by the B pick.
- Basis: SG-204 rated 98 (4 real-page renders, measured injections, no recommendation); the pick follows the recommendation presented with the question (Option B), accepted whole.

## D-9 — APPROVED: close the session

- The L4 window (2026-10-17 14:58→17:58, +03:00) ran to its end; both window goals discharged (serve D-5, density proposal D-6). Owner approved the close as recommended; no re-serve due (no new product commits since the SG-202 serve).

## Close record

- **State: `CLOSE_COMPLETE`** (on the close commit; repository StorageGenie only — the single repository touched). Tree committed/pushed; staged none; untracked none; no merge/rebase/bisect; no stash; no submodule; `sensitive_uncommitted_state_present` — no.
- **Three orthogonal facts:** work outcome = changed (17 commits); publication = pushed (origin/automation == tree); close = CLOSE_COMPLETE. No dispatch in flight; background jobs (reply-deadline, window-end wakes) all exited.
- **Work this session** (since the last close `c0d8f52`): SG-200/201 second-opinion review (ledger `docs/reviews/review-ledger.md`); D-5/D-6/D-7 answers + L4 window recorded (`docs/decisions/2026-10-17-d5-d6-d7-answers-l4-window.md`, owner directive byte-quoted); SG-202 serve rider 97 (SG-196+SG-198 SERVED live, container `d868f373`/image `15a1fe63`/bundle `dd4f1bd0`; supersedes SG-197); SG-203 density measurement 96 (dark focus-ring defect found); SG-204 density proposal 98 (4 renders; F-SG204-1 packet path premise, caught by PG-IC-09). All audited (docs/worklogs/SG-*_audit.md), rated (docs/ratings.md), pushed.
- **Live==tree verified:** `3857b6a..de0c285` contains no product change ⇒ no close re-serve due (D-5=A). Standing 2026-09-28 close-deploy directive discharged for this delta by SG-202.
- **Cold start:** `rules_check` 2026-10-17: G-L1 CLEAN ×3, VERSION CURRENT 0.50.0, watch-files hash match. **total[opencode] 34657 B vs last close 34467 B (+190 B — the AGENTS.md D-7 row edit)**; target `G-P1` ~20 KB (ARCHITECT.md:240) ⇒ 1.69×, under the 3× mandatory-move trigger. **STATE.md 12137 → 4593 B** (this close trimmed the accumulated slice narrative from RESUME; every live fact kept, history immutable in Git). File that grew most in the cold-start set: STATE.md (+3609 B during the session, then trimmed). **Repo-wide since last close: 74 files, +23689/−4 as of the audit commit `de0c285`** (largest single: SG-204 evidence logs/measure).
- **The state file's bytes at close: 4593 B.**
- **Issues raised, all dispositioned:** ISS-4 runner `report_unreadable` — 7 instances (SG-195/196/198/199/202/203/204), receipt present every time, no re-trigger, cost one audit cycle of diagnosis per instance with zero work lost — filed Launcher #84 + follow-up through instance 7. SG-203's report AA-total (490 stated / 245 artifact) — recorded in its audit, conclusion unaffected. F-SG204-1 packet path premise (`styles/tokens.css` vs actual `theme/tokens.css`) — recorded, PG-IC-09 caught it in-slice, zero rework.
- **Append-only owner-facing records:** no new superseded entry this session beyond the D-7 reviewer-value supersession, marked in place (`docs/decisions/2026-10-15-contract-050-adoption.md:35`, SUPERSEDED 2026-10-17 note).
- **Premises corrected in the record:** the packet's `frontend/src/styles/tokens.css:173` → actual `frontend/src/theme/tokens.css:173` (recorded in `SG-204_audit.md` and the proposal).
- **Files exist / references resolve:** all cited audits, ratings rows, packets, proposals, and decision records verified present in the tree.
- **Mojibake / control-character scan:** run over every file this session touched — clean (no U+FFFD, no control chars beyond CR/LF/TAB).
- **Context-size reading:** unavailable on this harness — stated, never invented.

## Self-review (5 slices crossed — SG-200/201/202/203/204)

- Five cycles in one session, ratings 97/96/98 (+2 reviews), no flags, zero unserved delta at close.
- Cost drivers: the ISS-4 misfires (5th–7th) each cost one diagnosis cycle (re-attach + fetch + receipt read-back); nothing else material. No work was lost to any misfire.
- The premise guards worked as designed: PG-IC-09 caught the packet's wrong path before any effect (F-SG204-1); PB-1's hypothesis frame ran in every slice.
- What would have made the session cheaper: only the runner classification fix (already filed at #84).
- **Lesson a global rule could act on:** none new — the strongest candidate (verify packet path premises at authoring) is already the designed mitigation, exercised and effective; adding a second guard would duplicate PG-IC-09 for a zero-cost failure (`G-A7`).
