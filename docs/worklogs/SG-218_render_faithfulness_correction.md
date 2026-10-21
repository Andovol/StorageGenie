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
The model reproduced its source closely on the re-render — which proved the source
itself is the wrong product for the asset (see Correction 2 below). Faithfulness
verdicts now run source-first, then asset-identity.

## Correction 2 — the render was faithful; the source photo is the defect (SG-223 F-SG223-1, 2026-10-21, live bytes)

SG-223 proved with the live bytes what Correction 1 got wrong: source photo
`01a0c4a1-ad90-…` (sha `f9d71a40…`, opened as `SG-223_source_costita.png`) IS the PIKOK
tin can — not the BARONI vacuum pack. SG-218's render reproduces its source closely
(mark, label text, pig illustration, ring pull all legible), and SG-223's re-render of
the same photo does the same. The "wrong product" is the asset-photo pairing: the
asset "Costiță de porc" carries a PIKOK-can photo alongside the BARONI photo. The
model did not ignore the reference on this asset; the reference itself is the wrong
product for the asset.

What stands corrected: (1) the SG-218 audit miss stands — the image was still never
opened at audit, which is how a faithful render shipped with an unfaithful judgment;
(2) Correction 1's input attribution ("made from the BARONI vacuum-packed ribs photo")
was wrong and is superseded by this section — the committed prompt and photo hash were
always correct; (3) faithfulness verdicts now run source-first, then asset-identity —
SG-223's link decision (`link_decision.json`) is the template; (4) the Costiță
canonical-photo question (BARONI already rendered and linked; PIKOK photo stays an
upload) belongs to a future decision, never an in-slice repair.
