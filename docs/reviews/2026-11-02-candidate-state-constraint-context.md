# Second-opinion context pack — the live candidate state constraint

**Prepared by:** the Architect, 2026-11-02. **Committed before Phase A runs** (`SECOND_OPINION.md`, T3; `AGENTS.md`, a 🟡 item on the app database).
**Decision:** how to let a multi-item photo be split, and candidates merged, on the live database.
**Why it matters now:** stage C's first real Pantry starts with the owner photographing real items. A photo with two products would stick.

## The problem in plain words

The code moves a candidate to the states `split` and `merged`. The live table's constraint does not allow them. The tests never see the constraint, because they build their tables from the models.

## The evidence, verbatim

**The live schema, `docs/worklogs/SG-276_report.md`, I2:**

> The served database's own `sqlite_master` text for `candidate` is `CHECK (state IN ('proposed', 'accepted', 'edited', 'held', 'rejected'))`; `split` and `merged` are not in it. No split or merged row can exist on this database yet

**Live counts, same report:** `candidate=10`; `proposed=4`, `edited=6`, 0 for held, accepted, rejected, split and merged; all 9 `review_task` rows resolved. Schema head `20261023_sg233_reminder`. `{{PROD_DB}}` in `AGENTS.md`: `sqlite:////data/db/storagegenie.db`.

**Not driven:** no live split was attempted, since it would write the owner's data. That it fails at the database is inference from the constraint.

**Owner, 2026-11-02, on stage C (`docs/decisions/2026-10-30-session-approvals.md`, D14 as put to the owner):** a needed schema change stops and goes to the owner. Stage goal: *"One styled Pantry you can use end to end"*. Restore from backup is not proven yet (`docs/ROADMAP.md`, stage D: *"export exists but restore does not"*).

## Where it lives

| Thing | File |
|---|---|
| The constraint | `backend/alembic/versions/20260908_sg014_candidate.py:31`; any other file in `backend/alembic/versions/` touching `candidate` |
| The model, states and writers | `backend/app/services/candidates.py`: `:496-510`, `SPLIT_ORIGIN_STATE`, `MERGED_STATE`, `split_candidate`, the merge function |
| Readers of those states | `backend/app/api/v1/candidates.py`, `backend/app/api/v1/jobs.py`, `backend/app/plugins/expiry_tracker.py:660-702`, `frontend/src/routes/InboxPage.tsx` |
| Tests that bypass the migrated schema | `backend/tests/test_review_split.py:33`, `test_sg270_flow.py:35`, `test_sg112_merge.py:45` |
| How migrations are tested and deployed | `backend/alembic/`, any test running them (search for `alembic`), the `Makefile`, the three latest files in `docs/releases/` |

**Do not read `STATE.md`, `docs/decisions/` or `docs/worklogs/SG-276_audit.md`.** They are not needed here, and this keeps the pass blind.

## What binds it

- **Decided, not reopened:** one candidate may split into per-item candidates, and each commits its own item (SG-033, SG-270).
- **Sensitive surface:** the app database (`AGENTS.md`). The owner decides any schema change.
- `AGENTS.md`: both app services restart on their own unless stopped.

## The options as I see them, without a pick

**Q1 — the fix.**

| Option | What happens |
|---|---|
| **M1 Migration, widen the constraint** | A new migration allows `split` and `merged`. On SQLite this rebuilds the table. |
| **M2 Migration, remove the constraint** | The states stay defined in code only. |
| **M3 No schema change** | The retired origin uses a state the table allows, with a marker in its proposal saying why. Readers change to use the marker. |
| **M4 Leave it and hide it** | Until later, the app says a multi-item photo must be captured one item at a time. |

**Q2 — the gap that hid it.** Should tests run against the migrated schema, and how much of the suite? Pick the smallest measure that would have caught this, and name its cost.

**Q3 — safety of the change, per your Q1 pick.** What must exist before it runs on the live file: a backup, its proof, the deploy order, what the old code does meanwhile (`PG-PR-05`)?

## What would make the whole approach wrong

Name it if the constraint is not what stops a split; for instance if the app's own start-up, or the way this database file was made, changes the picture. Also name any other model state or column that differs between the models and the migrated schema, if a read-only look can show one.
