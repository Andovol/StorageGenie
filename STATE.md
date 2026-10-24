# StorageGenie — State
## RESUME — 2026-10-24, SG-235 landed and rated 97 (daily caller + Expiry Read/Dismiss buttons) but NOT live; next: SG-236 close-deploy rider, then the release record; Launcher #84 and #89 are closed

**Live:** the running app still serves the SG-233 delta (reminder store, daily compute, in-app sender), deployed as container `e1142971` from image `6bdaa3b0`, rated 98 via SG-234. SG-235 is in the code only — the served image has no daily pass and no Read/Dismiss buttons yet. Nothing is in flight.

**Startup record (2026-10-24):** Launcher **#84** (run-coder `report_unreadable`, SG-195) — **closed**: SG-235 finished `result=done exit=0` with a valid notes receipt, so no false `report_unreadable`. Launcher **#89** (verify-after-edit, D477) — **closed**: D477 verified live in contract 0.52.0 (`.rules-cache/RECIPES.md:100-103`). Also this session: contract 0.52.0 adopted (D-1024-1), `release-2026-10-23` tag + record, PRs #43–#49 closed as already applied (D-1024-3).

**Next:** **SG-236** close-deploy rider — build the new image and recreate the container so the daily caller and the buttons go live (`PG-PR-04`), then the release record for the shipped bytes. Then **SG-237**: relax the two stale scope gates (SG-233's and SG-235's) and the repo-wide ruff/mypy/eslint reds — the two missing host test libraries (`libzbar0`, `tesseract`) need the owner's word first. Then roadmap row 11 (opened-date countdown for cosmetics). Everything else parked. Email stays out until the owner binds SMTP creds (D1, D-1024-2). Rule set current at `0.52.0` (adoption D-1024-1, 2026-10-24).

**Rules for reports:** every report ends with next steps and starts step 1; the parked list is never shown. This keeps the owner's wish for no irrelevant detail while always saying what comes next.

**Standing:** before every close, deploy the live app and record a release when product code changed. Unrated or blocked work stops the deploy instead of shipping silently.

**Where things live:** product needs are in `docs/ROADMAP.md`; waiting items with their triggers are in `docs/backlog.md`; past work is in git history and `docs/ratings.md`; past decisions are in `docs/decisions/`; packets, audits, and worklogs are under `docs/`. The session-report thread is Launcher issue 62. Context-size readings are unavailable on this setup, so none are stated here.
