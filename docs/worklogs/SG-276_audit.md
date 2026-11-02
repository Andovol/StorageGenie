# SG-276 audit — deploy rider for SG-270 and SG-275

**Score 97/100; no flag.** The diff `aad92fa..d7bd7c1` is `docs/worklogs/SG-276*` only. Runtime diff is exactly the four expected files, the served tree equals the worktree, the JS moved, no migration, all 29 table counts identical, and the database file's hash and mtime match the SG-262 release. The rider proved a cache-satisfied build rather than trusting it. Elapsed 362 s before report writing, against ≈450 s expected.

## Findings

I1. **Splitting and merging cannot work on the live database, and the rider is what caught it.** Its I2 quotes the live `candidate` table: `CHECK (state IN ('proposed', 'accepted', 'edited', 'held', 'rejected'))`. The code writes `split` and `merged`. The constraint comes from `backend/alembic/versions/20260908_sg014_candidate.py:31`; a search of `backend/alembic/versions` found no later migration changing it, and the model declares none (`backend/app/services/candidates.py:496-505`).

`UNVERIFIED — my inference from the live schema; not driven live, since it would write the owner's data`: a split on the live app fails at the database, so a multi-item photo stays stuck, because its `candidate.multi_item` task still blocks Accept.

**This corrects the SG-270 audit:** the fourth dead end is fixed in the code and on the test schema, not live.

**Root cause, and why 781 tests missed it:** `test_review_split.py:33`, `test_sg270_flow.py:35` and `test_sg112_merge.py:45` build their tables from the models with `Base.metadata.create_all`, which has no such constraint, so these tests never meet the migrated schema. Not caused by this rider or by SG-270: splitting dates from SG-033 and merging from SG-112.

**Live exposure today:** no open tasks at all (`SG-276_counts.log`), so nothing is stuck yet. The next multi-item photo would be.

**Destination:** a schema change on the app database stops and goes to the owner (D14), after a two-phase second opinion (`AGENTS.md`): SG-277, SG-278, then a decision item.

I2. **The answer to the rider's question:** no date task or other task is waiting on rejected candidates, so no cleanup decision is needed. Closes SG-270's line on them.

## UNCLEAR and REMAINING

None new. SG-270's other lines keep their destinations.

Slowest waste: none.
