# SG-278 — Second opinion Phase B (critique): the live candidate state constraint

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

Phase A (`docs/worklogs/SG-277_report.md`) is done. This is **Phase B — the critique.** Attack the Architect's recommendation below, which goes to the owner next. It is a recommendation; the schema decision is the owner's.

## The Architect's recommendation, verbatim

> **R1 Fix:** one new migration widens `ck_candidate_state` to the five existing states plus `split` and `merged`, keeping the named constraint; the model declares the same constraint, so test schemas match. No other schema change.
>
> **R2 Tests:** two cases on a temporary database built by Alembic at head, a real split and a real merge through their routes, with read-back; plus one test that all seven states are accepted and an invalid one refused on that schema. FAIL on the old head must name `ck_candidate_state`. Other tests keep `create_all`.
>
> **R3 Build slice:** builds R1 and R2, and rehearses the upgrade on a temporary database populated at the old head: every candidate column, timestamps, indexes, foreign keys and row counts compared before and after. It also runs the downgrade, which refuses if `split` or `merged` rows exist.
>
> **R4 Deploy rider, in this order:** build the image first; stop the backend container so the reminder loop and all writers stop (a compose stop, so it does not restart itself); take a backup with SQLite's backup mechanism; restore that backup to a scratch path and prove `integrity_check`, `foreign_key_check`, the schema head and all table counts; only then run the one migration; compare the live schema text and every table count; start the new image; health and shell routes. Any failed step before the migration starts the old image with nothing changed. A failure after it restores the backup, since no writer has run; that is within the owner's approval. Once writers resume, a restore would lose work, so it needs a new owner decision.
>
> **R5 Not now:** a general proof of restore from export stays with stage D. This backup proof covers only this one migration.
>
> **R6 Order:** this runs before SG-271. The live split is not tried on the owner's data; the first real use is the owner's.

## G1 — Read

`AGENTS.md`'s top section, `docs/reviews/2026-11-02-candidate-state-constraint-context.md`, `docs/worklogs/SG-277_report.md`, and the code they name. **List every file read beyond those.**

## G2 — Per recommendation R1–R6

- the strongest case against it, with evidence (`file:line`, a quote, a measurement);
- a premise of it that is unverified;
- the observation that would settle any disagreement.

An objection without evidence is labelled `opinion`. Check especially: whether SQLite's table rebuild endangers the `asset_fts` tables, triggers or other foreign keys that point at `candidate`; whether the compose stop and a one-shot migration can really run with the backend stopped and on this lane's socket; whether the lane's rights permit it (`PB-2`); and whether R4's failure paths are complete.

## G3 — Report

Your final message **is** the report (read back with `SG-278 --status`; the Architect copies it unedited to `docs/worklogs/SG-278_report.md`). **Keep the whole report under 200 lines: the engine keeps only 200 lines of a read-only run's report.** The most serious objection first. Shape: `SG-278` as the first token; the contract-version line (`PB-4`); the extra-files list; R1–R6; a closing line of what you read.

## Constraints

Read-only; reads confined to the repository at BASE; no host changes, credentials, browser, network or database. Hang bound: file reads 120 s each. A denial is a STOP (`PB-2`).

## Acceptance criteria

Each of R1–R6 answered; each objection evidenced or labelled `opinion`; extra-files list complete; report under 200 lines. `PB-3` vacuity: "no objection" needs one sentence on what was checked.

## Report

Destination: final message (engine-published). Identity line and stop path are `PB-4`/`PB-6`. State that you wrote nothing.
