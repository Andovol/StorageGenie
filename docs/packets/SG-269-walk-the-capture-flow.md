# SG-269 — Read-only walk: from capturing a grocery to finding it again, on a throwaway copy

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice changes no product byte.** It produces a findings list; fixes follow as separate slices scoped from it. Finding nothing broken on a step is a good result, and so is stopping early (`PG-SC-03`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: a temporary SQLite file under scratch only.** Never the live database. No read or write of `/data/db`, the live container or its storage.
**Restart: none.** The live app is not touched.
**Provider: none.** No key, no `.env`, no spend.

**Previous report's open items:** SG-262's leftovers (`docs/backlog.md` W8) are not this slice's work unless a step fails because of them.

## Why this exists

The owner approved stage C (D14, *"d14 ok"*). The live census holds 7 assets, and nobody knows why so few. Reading the code suggests the journey is fragmented. **All below are hypotheses from reading, never driven; confirm or refute each:**

- Two capture paths: by hand creates an asset and goes to its page (`frontend/src/components/AssetForm.tsx:103-122`, `frontend/src/routes/CapturePage.tsx:30`); import creates a job and goes to the inbox (`frontend/src/components/shell/AssetImportModal.tsx:136-157`).
- Inbox links every task to `/review/<subject_ref>` and labels it "candidate" (`frontend/src/routes/InboxPage.tsx:50`), but a classify date task's subject is an asset id (`backend/app/plugins/expiry_tracker.py:374-393`), and the review page fetches a candidate (`frontend/src/routes/ReviewPage.tsx:37`).
- A bare resolve on `expiry.manual_entry` may be refused (`backend/app/api/v1/review_tasks.py:20`), while the inbox's Resolve button may send one (`frontend/src/routes/InboxPage.tsx:50`).
- An open task on a candidate blocks its commit (`backend/app/services/candidates.py:966-979`); how a reviewer clears a candidate's date task from the screens is unknown.
- The review page has no link to the asset after accepting (SG-262 audit I1).
- Two "category" controls: the drawer's writes `asset_type` (`frontend/src/components/shell/ItemInspectorDrawer.tsx:90-107`), the asset page's writes the classification (`frontend/src/routes/AssetDetailPage.tsx:447-475`).
- Accepting does not classify (`backend/app/services/candidates.py:850-905`), so an accepted food may not reach the Expiry page (`backend/app/services/expiry_engine.py:263-268`).

## G0 — A throwaway app, and proof it is throwaway

Use `output/SG-269-scratch/` for everything temporary. **Remove exactly that path at the end, never `output/` itself; `output/dispatch` belongs to the engine, and damaging it is a STOP** (`AGENTS.md`, Coder scratch).

Run the backend from the worktree's code with `backend/venv`, on a port you confirm is free (not 8003), with `DATABASE_URL` and `STORAGE_ROOT` pointing under scratch, the schema made by Alembic on that temporary file.

**`backend/app/config.py` reads `.env` relative to the working directory** (`model_config`, `:63`), and a real `.env` may exist at the worktree or in `backend/`. **Run with the working directory inside scratch, and prove before any request that the settings in use name the temporary database and storage, and that no provider key is loaded, without printing any key value.** If you cannot prove it, STOP. Run the live probe `curl -s http://127.0.0.1:8003/v1/health` at start and end, read-only.

**How the screens are checked:** `frontend/package.json` has no browser driver (no Playwright or Puppeteer), and installing one is out of scope. Establish whether a browser exists on this box without installing anything; none is expected. Then drive the flow through the **real HTTP routes** of the throwaway app, and for each screen state **what the source shows the user at that moment**, by `file:line`, using React component rendering in a scratch test where a claim turns on behaviour. Name, for each step, which of these was used. State plainly what this cannot show: look, feel and layout on a phone.

**Import path:** run it with no provider first and report what happens. For the path where AI proposes fields, use the repo's scripted fake (`ScriptedPhase2Provider`, `backend/tests/test_phase2_e2e.py:187`) in-process in a scratch test, never a real call. Test images are generated, as those tests do.

## G1 — Walk the journeys

Follow one grocery at a time, end to end. For each step record: what the user sees, what they must do next, what got written, and **every wrong turn, repeated entry or dead end, not only impossible steps**.

- **J1, by hand:** create an item named like a real grocery, set quantity and unit, choose the category, enter a date, find it in the catalog and on the Expiry page.
- **J2, by import, no provider:** upload a photo, inbox, review, accept, then the same onward steps. Does it stop anywhere?
- **J3, by import, scripted AI proposing a dated food:** review, accept, then category and date. Is the proposed category or date carried over, or re-entered?
- **J4, by import, scripted AI that cannot read a date (`needs_evidence`):** the candidate's date task. Can a user get through using only what the screens offer?
- **J5, the classify date task on an asset:** open it from the inbox, using only what the screens offer.
- **J6, the same product bought twice:** same barcode or same name, different dates. What happens at capture and review?
- **J7, shelf-stable food with no date** (honey, rice): how does a user get it classified without a date prompt nagging them or a push toward Non-perishable?
- **J8, using it up:** change the quantity; mark it gone with what exists today. How many steps from the catalog? Can they find it afterwards?

## G2 — The findings list

In `docs/worklogs/SG-269_findings.md`, one row per finding: ID (`F1`, `F2`…) · journey and step · what happens · evidence (`file:line`, a request and response, or a test name) · severity (`blocks`: the user cannot continue using the screens; `wrong-turn`: they can, with effort or re-entry; `note`) · how many steps or fields it costs · the smallest fix you can see, as a suggestion only. Sort by severity. Also state each hypothesis above as confirmed, refuted or not established. **Do not fix anything.**

## Acceptance criteria

- **A1** — G0's proof is in the log: temporary database and storage in use, no provider key loaded, live health 200 at start and end, and the live database not opened.
- **A2** — J1–J8 each walked, or the reason it could not be, with how each step was checked named.
- **A3** — The findings file exists, each row with evidence, and every hypothesis dispositioned. A finding with no evidence is labelled `opinion`.
- **A4** — Zero product, test, schema, config, dependency or lockfile bytes in the commit; only `docs/worklogs/SG-269*`. `git status` clean at the end; scratch removed by exact path; `output/dispatch` untouched.
- **A5** — `PB-3` vacuity: an empty findings list needs what each journey would have looked like had it failed. A step reported "works" needs its request and response or test name.
- **A6** — The report's last line is `Verification: PASS` or the honest failure reason.

## Scope ceiling

- Commit `docs/worklogs/SG-269*` only. Scratch tests stay in scratch and are copied into the evidence as text if they matter.
- **Reads of any repository file are allowed.** Runtimes authorised: `backend/venv` Python, Alembic on the temporary file, the throwaway backend, the repo's existing frontend test runner on a scratch test, `curl`. Running the existing frontend test runner on scratch tests may need a test file inside `frontend/`: if so, it stays untracked, is removed by exact path, and is named in the report. No image pull, no container, no docker, no install, no network beyond localhost.
- No touching the live container, its image, the live database or storage. No migration on anything but the temporary file. No browser install. No deploy.
- **A denied privileged operation is a STOP** (`PB-2`, `PG-PR-03`).

## Hang bounds

Backend start **60 s**; one request **60 s**; one scratch test file **300 s**; ordinary commands **120 s**. Run the throwaway backend in the background and stop it by its own PID when done. Nothing may reach the lane's idle kill. No interactive command.

## Budget

The lane's `RUN_BUDGET_S` (2100 s) is the ceiling. **Publish before the bound at 1500 s:** stop starting journeys, commit the findings so far, write the report, publish the receipt, and name the journeys not walked. A partial walk with a receipt is a success. Expected ≈900 s; no comparable walk exists on this lane, so this is uncalibrated, bracketed from SG-262's 991 s.

## Report

Destination: `docs/worklogs/SG-269_report.md`, with `SG-269_findings.md` and logs beside it (`docs/worklogs/SG-269_*.log`). Commit the findings before polishing the report. The first line states the slice ID, model and effort read from the process arguments (never a system-prompt label), working directory, remote, BASE ref and resolved BASE commit, and WORK_HEAD. The report compares elapsed time against the ≈900 s expectation and names every phase over 60 s, and carries the contract echo from `/home/andrei/storagegenie-contract/CODER.md` line 3, every `UNCLEAR` / `REMAINING` line, and a line per constraint.

The receipt goes to the notes ref `refs/notes/storagegenie-coder-reports`, first line:

```
Dispatch-ID: SG-269 | Report: docs/worklogs/SG-269_report.md | Work-HEAD: <work commit>
```

Fetch the ref explicitly (`git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports`), add the note with `git notes --ref=refs/notes/storagegenie-coder-reports add -m "<that first line>" HEAD`, and push it (`git push origin refs/notes/storagegenie-coder-reports`). A receipt that moves the product branch is refused (`CO-86`).

The report's last line is `Verification: PASS`, or `Verification: FAIL — <check>`.
