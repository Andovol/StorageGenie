# Correction — SG-218 render is the wrong product (owner-found 2026-10-21, audit miss)

## What happened

The Scene tab for Costiță de porc shows a PIKOK tin can. That image is the SG-218 render
(`01a15fdc-f5b6-7f31-9008-2f8d89be8813`, 731,496 B, sha256 `ce4794a2…`), made from the
BARONI vacuum-packed ribs photo. The model rendered a different product altogether.

## The miss (mine)

SG-218 was rated 98 without the auditor opening the render. The audit verified bytes
(sha match), JSON fields and ledger rows, and trusted the report's "opened +
dispositioned" claim — the exact substitution AUDIT.md §4 forbids ("open every one
yourself"). SG-220 was audited correctly (image opened, concurring judgment); SG-217's
render is owner-confirmed ok in the live app.

## Standing correction

Every image artifact gets opened at audit by the auditor, no exceptions — SG-220 proved
the rule works; SG-218 proves what happens without it. Rating rows for SG-217 (owner
confirmation) and SG-218 (wrong product, faithfulness failure) are annotated by this
note, not rewritten: the 98s stand as scored-off-incomplete-evidence, which is what
this correction records.

## Request on record (verbatim, from `SG-218_request.json`)

- model: `google/gemini-3.1-flash-image`, n: 1
- prompt: "Restage this packaged product on a clean kitchen counter in warm natural daylight; keep the package, its label and its printed text exactly as photographed."
- input_references: [the Costiță-1 source photo as data URL]

The request was correct — source photo right, keep-the-package instruction explicit.
The model did not honor the reference on this asset. Faithfulness varies per asset;
it is not guaranteed by the prompt.
