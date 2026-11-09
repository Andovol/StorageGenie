# SG-271 audit — the AI's work carries through; one Expiry-page rule hides too much

**Score 90/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh`, from the receipt's `Settings:` line. Retry run (the one allowed): run 1 was killed at the 2100 s budget past its publish point with nothing pushed (`SG-271.dbg`). Diff `29df408..9f9963c`, 39 files; receipt on the notes ref, `published_head=yes`, ~420 s. Read: report, the backend diff in full (`candidates.py`, `api/v1/candidates.py`, `api/v1/jobs.py`, `expiry_engine.py`, the eval baseline), the Review and Expiry page diffs, `clear_expiry_date` in `expiry_tracker.py`.

## What holds

- **G1** — `requires_date_task(unknowns)` gates both producers; a cosmetics opened-date unknown opens no task, a food null date still does. FAIL-then-PASS committed.
- **G2** — `committed_asset_id` is derived on read from the proposal, then the SG-270 map, then the commit step output, each hop household-checked; it reaches `GET /v1/candidates/{id}` and the job candidate list. Review page shows *In your catalog* + *Open item* and gates the buttons **and** the `a`/`r` keys. Closes SG-275 I1.
- **G3** — a proposed date survives classification with *Accept date*; the proposed shelf life preselects and only an explicit *Confirm shelf life* / *Save shelf life* classifies.
- **G4** — *Kind of item* / *Shelf life*, every occurrence listed, no field renamed.
- **G6** — skipped steps read *Skipped — the AI is turned off*.
- **Gate** — backend 793 passed, 2 deselected, image proof 2 passed; frontend 345 passed; affected files twice; ruff, eslint, tsc, build clean. Design section present per screen, tokens and themed classes only.
- **Retry discipline** — finished at ~420 s against a 1300 s stop rule; the stranded work was reused and every gate re-run from the base, as asked.

## Findings

I1. **A perishable item whose date the user cleared now disappears from Unresolved.** `compute_status` counts any accepted null expiry as deliberately dateless (`expiry_engine.py`, SG-271 G5 hunk). `clear_expiry_date` (`expiry_tracker.py:771`) writes that same accepted null for **perishable** items — it refuses Non-perishable ones (`:794`). So a cleared milk date now reads *"set to need no date — nothing to do here"* instead of SG-262's *No date*. The packet said an item with no date and no such decision still shows; clearing a date is not deciding the item needs none. **Attribution: mixed** — the packet asked the Coder to establish the distinguisher; the Coder named the clear path and chose it. **Destination: SG-272, fix first** — key the quiet count to the Non-perishable classification only; a cleared perishable stays on Unresolved as *No date*; a test that clears a food date. Not held: no owner use is live yet (`STATE.md`: first real use is the owner's, after SG-273).

I2. **New notes are 12 px.** The packet said no font sizes below the page's body size, and D18 asks to enlarge the small type; the Coder matched the page's existing 12 px notes. **Attribution: coder** (small). **Destination: SG-272** — new notes at body size.

I3. **`backend/eval/baseline_sg029_frozen.md` was changed** (6→4 correction tasks, with an amendment note) although the packet made a product file outside `backend/app|tests`, `frontend/src` a STOP. The change is correct and disclosed, and an eval record is arguably not a product file; the packet's word "product" left that open. **Attribution: packet.** No action; future packets name eval records explicitly.

I4. **A split child now opens a date task from its unknowns alone,** no longer also requiring its `needs_evidence` flag. Consistent with G1's purpose; noted, no action.

I5. **The frontend FAIL log is 5206 lines.** Evidence volume, not a defect.

## Below 95 (`RATING_ISSUE.md`)

- **Failure class:** prompt gap plus model execution (class 14: the clear path was found and the inference that it is not deliberate was not drawn).
- **Root cause:** the packet delegated "what distinguishes deliberate from missing" without stating that a clear writes the same null.
- **Correction:** SG-272 fix-first items I1, I2.
- **Recurrence guard:** a packet delegating a distinguisher names every writer of the value it keys on (here: Non-perishable classify and `clear_expiry_date`).
- **Owner impact:** run 1 2100 s lost; run 2 ~420 s; cost `unavailable`.

## Model note

Muse, two runs. **Run 1 broke a stop rule** (the 1500 s publish point) and lost the run; **run 2 kept a sharper stop rule easily** and did strong, well-tested work. Flagged to the owner and the desk (D25).

## Rating

`slowest_waste`: none in run 2 (run 1: 2100 s lost to the budget kill). Next: SG-296, the deploy rider, on Haiku.
