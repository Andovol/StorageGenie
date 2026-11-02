# SG-275 audit — no second item on older rows

**Score 97/100; no flag.** Audited from the diff `19be9e3..edeb28e`. The commit step's output is read before the reset, only a `created: true` output for this candidate seeds the map, and the existing branch returns the item after checking its household. Gate counts read from the report and logs: FAIL 2 failed, 2 passed at assertion level; PASS 17 passed; host 781 passed, 2 deselected; frontend 336 passed. Elapsed 465 s against ≈500 s expected. Scope holds. **This clears the hold on SG-270's deploy.**

Test bodies read: the older-row cases run a real commit, remove only the map and repeat through the real route. No placebo. They use the same row shape as the audit's own probe, whose result this fix reverses.

## Findings

I1. **A repeat edit on an older row returns the item and changes nothing on it, with no word to the user.** `test_pre_sg270_repeat_edit_returns_the_existing_item` passes "Renamed older row" and asserts only the id and count. The packet asked only for one item. No data is harmed, but the page offers an edit that has no effect. **Destination: SG-271**, with the reload link: a candidate already committed links to its item and stops offering decisions (`STATE.md` step 2).

## UNCLEAR and REMAINING

The four SG-270 lines keep their destinations (`SG-270_audit.md`). No new line from this slice.

Slowest waste: none.
