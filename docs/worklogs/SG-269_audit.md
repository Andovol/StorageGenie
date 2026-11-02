# SG-269 audit — read-only walk, capture to finding it again

**Score 97/100; no flag.** The diff `4d1114a..1b8c010` is `docs/worklogs/SG-269*` only. G0's proof holds: temporary database and storage under scratch, no provider key, live health 200 at both ends, scratch removed by exact path. The findings have evidence, and every packet hypothesis is dispositioned.

Cross-check of F1, the largest finding, by a separate search: the only frontend candidate calls are the review page's single read, decision and split (`frontend/src/api/client.ts:205,217`, `frontend/src/routes/ReviewPage.tsx`), so no screen lists a job's candidates. Confirmed.

## Findings on the walk itself

I1. **The report's claim that F1 is "the most likely explanation for a low live census" is an inference, not measured.** The live app has a provider and 10 candidates against 7 assets (`docs/worklogs/SG-263_g4_census.log`). F1 was driven only without a provider. `UNVERIFIED — my inference`: a dated food read by AI also opens no task (J3 was accepted by direct call), so it would be just as unreachable. The fix slice proves this.

I2. Chrome exists on the box, which the packet did not expect; without a driver or an authorised frontend server it stayed unused. So look and phone layout are still unobserved. Packet deduction. The next UI slice should say how screens get seen.

I3. J6's barcode path is not established, because the host's Python lacks `pyzbar` and `tesseract` (known: `docs/backlog.md` W1). **Destination:** the next slice touching duplicates, proved through the image route.

## Disposition of the findings

| Finding | Goes to |
|---|---|
| F1 no screen lists a job's candidates; F2 AI-no-date dead end; F6 asset date task links to a 404; Inbox Resolve always refused on date tasks | Next slice: flow fixes |
| F4 AI date overwritten on classify; F5, F12 accepted food unclassified, proposal unused; F7 two "category" controls; F8 dateless item nags | Second slice: carry the AI's work through |
| F3 no way to mark gone; F13 archived items unfindable | Third slice: gone, put back, quantities |
| F9, F10 same product twice | Pantry view slice, with C-4's separate tiles; F10's lost second date is the open part |
| F11 "completed" step that was skipped | Note; second slice if cheap |

All of it is in `STATE.md`'s ordered work.

Slowest waste: none; the 201 s of source reading and 391 s of writing are what the audit used.
