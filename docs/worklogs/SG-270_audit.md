# SG-270 audit — flow fixes

**Score 91/100; no flag. The deploy is held until SG-275 fixes I1.** Audited from the diff `efdedcf..24e9d38`. Gate counts read from the logs: host 777 passed, 2 deselected; frontend 336 passed per the report; FAIL run 11 failed, 2 passed, at assertion level; PASS run 13 passed; ruff clean; mypy 9 errors, the same 9 on base. Scope holds: no schema, migration, model or deploy byte. Elapsed 1608 s against ≈1500 s expected.

The fourth dead end was real and is fixed (report (a); `SG-274_report.md` first raised it). Test bodies read: the journey, split, failure and duplicate tests drive the real routes and read rows back. No placebo.

## Findings

I1. **Accepting a candidate committed before this slice creates a second item.** The repeat-accept guard is a `committed_assets` map, written only by new commits. `_prepare_commit_steps` (`backend/app/api/v1/candidates.py`) reopens the commit step for any accepted candidate, and Accept stays enabled on an accepted candidate. The new Inbox list makes those candidates reachable. **Reproduced by this audit** on a temporary database, same flow with and without the map, at `24e9d38`:

```
CONTROL (1, False)
OLD_ROW (2, True)
```

Asset count, then `created`. Before this slice the step stayed complete, so a repeat created nothing: this is a regression the deploy would have put on the owner's live rows. The test suite only tried a repeat on new rows. **Fix: SG-275, before the deploy.**

I2. The optional fallbacks `blocking_review_task_ids ?? review_task_ids` and `subject_kind ?? "candidate"` are for payloads that cannot occur, since the frontend and backend ship together and the types mark both required. Minor. **SG-275 removes them.**

## UNCLEAR and REMAINING

| Line | Goes to |
|---|---|
| Screens unseen, no browser (SG-269 I2) | SG-273, already says how screens get seen |
| `needs_evidence` can be true when the date is not the unknown; the cosmetics prompt ties it to the opened date | SG-271, `STATE.md` |
| Rejected candidates' tasks from before this slice | SG-276 rider counts them, read-only |
| Accepted candidate reloaded: no link to the item | SG-271, `STATE.md` |

## Below 95 (`RATING_ISSUE.md`)

1. **Failure class:** prompt gap and model execution, both.
2. **Root cause:** a new marker was trusted to describe rows written before it existed. The packet said "accepting the same candidate twice creates one asset" and spoke of live rows only for open candidates, so neither it nor the test named a candidate already committed.
3. **Exact correction:** SG-275 takes the committed asset from the commit step's existing output before reopening it.
4. **Recurrence guard:** a packet that adds any stored marker names the row written before the marker as a required test case. Applied from SG-275 on.
5. **Owner impact:** elapsed 1608 s plus one repair slice; the deploy waits. Cost `unavailable`. No live data touched.

Slowest waste: none.
