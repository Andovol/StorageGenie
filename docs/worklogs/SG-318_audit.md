# SG-318 audit — plain words W1–W10 built, gate green; one out-of-scope file edited and disclosed instead of stopping

**Score 88/100; no flag. Deploy waits for its screenshots (SG-319).** Model `opencode-go/muse-spark-1.3-contributor` xhigh (receipt note; the report says the arguments were not visible and does not infer — correct). Diff `0e04e0a..8dd5717`: 9 product files, 7 test files, logs.

## Holds — checked against the diff and logs

- **Gate green:** frontend 55 files / 477 tests, 0 failed (the whole suite); host 805 + 2 deselected; image proof 2; eslint only the known error; `tsc` 0; build into scratch; 8 files twice 84/84. FAIL on base 10/10.
- **Every removed test line read** (`git diff … | grep '^-'`): each old string moved to its new word; none loosened.
- W1–W10 met with files named; one shared date helper pair in `labels.ts` (`formatPlainDate` for dates, `formatJobDate` for date-times).

## Findings (session IDs)

I28. **Out-of-scope product edit, disclosed, not stopped:** `frontend/src/components/EvidenceGallery.tsx` (W4's real source; the packet guessed `AssetDetailPage.tsx`). The edit is right (*No photo yet*, 13 px). **Coder (Muse's SG-271 pattern, again) and packet (wrong file guess). Disposition: kept; profile.**
I29. **W6 partial:** *Untitled item* literals remain in `CatalogPage.tsx`, `PantryPage.tsx`, `OpenedCountdownSection.tsx`; `noname` comes from the backend's display-name rule. **Packet (scope I set). Disposition: SG-319's shots show which are visible; then a small follow-up.**
I14. *Uncategorized* food in the panel — unchanged, backend.

## Model note

Muse's eighth rotated slice: a clean ten-row sweep with the full suite run, but the scope-ceiling breach recurs.
