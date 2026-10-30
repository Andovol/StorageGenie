# SG-261 — Second opinion Phase B (critique): the household-and-document picks

`PB-1`–`PB-6` bind (`CODER.md` §14).

**This slice is READ-ONLY by construction** (the dispatch command carries `agent=plan`): it cannot write, commit or push. If any step seems to require a write, that is a STOP (`PB-2`).

**BASE REF: `origin/automation`.** The ref is what the packet requests; the commit it resolved to is what the report states back — two fields, never one.
**DATABASE: none.**
**Restart: none.**

## Why this exists

`SECOND_OPINION.md` (contract 0.56.0; `T3`, `D555`) requires Phase B — the critique — after the blind pass and before the Architect commits the work packet. Phase A (`SG-260`) picked independently; its report is `docs/worklogs/SG-260_report.md`. The Architect adopts those picks, with the refinements below, and this phase attacks them.

**The picks, verbatim:**

- **D-A — A1.** Flip Documents/other to `has_expiry=True`, so its shipped 60/30-day windows can fire. **Refinement:** suppress the `_observed_date` proposal for documents — no OCR date is proposed as an expiry; the user enters the date manually. Reuse the existing `expiry_date` field and date-type list; do not add a new `DateType` this slice.
- **D-B — B1.** A classification control on the asset detail page, using the served taxonomy's active categories and the existing `POST /v1/plugins/expiry-tracker/assets/{asset_id}/classification` route. No `If-Match`: last-writer-wins is visible and re-doable through the same control.
- **D-C — C1.** In `classify_asset`, skip **both** the `needs_evidence` placeholder and the observed-date proposal when an active expiry assertion exists, so a category change keeps the date. The reverse move — a dated item classified into `non_perishable` — keeps the date active (today's behaviour); the packet tests and reports it.
- **D-D — D1.** Show the date form whenever the asset's classification profile has `tier_defaults`, read the active plugin `EXPIRY_FIELD` assertion (not a bare or superseded one), pre-fill an accepted or proposed date, and Save writes an accepted date. No clear action this slice; the D4 clear parity is noted as a follow-up.

## G1 — Read

Read, in this order:

1. the repository root file `AGENTS.md` — its top section;
2. the context pack `docs/reviews/2026-10-30-household-documents-context.md`;
3. the Phase A report `docs/worklogs/SG-260_report.md`;
4. every file the context pack names in its "Where it lives" table.

**LIST every file you read beyond those.**

## G2 — Per decision, the strongest case against

For **D-A**, **D-B**, **D-C** and **D-D**, as picked above, produce:

- (a) the **strongest case against the pick**, with evidence — a quote or a `file:line` from what you read; an objection without evidence is labelled `opinion`;
- (b) **one premise of the pick that is unverified**, and how it could be checked;
- (c) the **observation that would settle any disagreement** — what to read or measure, and what result would change the pick.

Do not restate the pick at length; attack it.

## G3 — Report

Your final message **is** the report (the engine publishes it; it is read back with `SG-261 --status`; the Architect copies it unedited to `docs/worklogs/SG-261_report.md`). Required shape:

- `SG-261` as the first token;
- the contract-version line (`PB-4`);
- the extra-files list (G1);
- one section for each of **D-A**, **D-B**, **D-C**, **D-D** with (a)–(c);
- a short closing statement of what you read and deliberately did not use.

## Constraints

- Read-only: no write of any kind, no commit, no push; the `agent=plan` launch enforces this; a denial anywhere is a STOP (`PB-2`).
- Reads confined to the repository at BASE; no host changes; no credentials; no browser; no external network.
- Hang bound: ordinary file reads 120 s each; no interactive prompt; the run should finish well inside the lane's `RUN_BUDGET_S`.
- No fixed dates except this header's authoring-date metadata; every time-dependent statement reads the live clock at execution (`PG-IC-07`).

## Acceptance criteria

- One strongest case per decision, each with evidence or self-labelled `opinion`.
- One unverified premise per decision, with a check.
- One settling observation per decision, naming the result that would change the pick.
- The extra-files list present and complete for your run.
- `PB-3` vacuity: a restatement of the pick, or an objection with no evidence and no `opinion` label, does not satisfy G2.

## Report

Destination: final message (engine-published; the Architect copies it unedited to `docs/worklogs/SG-261_report.md`). Identity line and stop path are `PB-4`/`PB-6` — cited, not pasted. You publish nothing else: this run produces no commit and no receipt note from your side; state that you wrote nothing.
