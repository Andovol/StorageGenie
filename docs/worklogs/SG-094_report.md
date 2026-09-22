# SG-094 — Taxonomy T2: schema field + v4 prompts, transcribe-only

**Dispatch-ID:** SG-094 · **Coder:** opencode · **Effort:** high (`--variant high`, from own argv) ·
**MODEL:** `unknown` (CLI default; no `--model` token on argv, per model policy) ·
**Spend:** **real $0.000000** (fully offline: no download, no provider call, no key read).

**BASE ref:** `origin/automation` → resolved commit `d6e968b3ef7c707ce67f2444eb08068a41d7f100`.
**WORK_HEAD:** `<WORK_HEAD>` (work commit; docs-only receipt commit is the tip, below).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**Authoring date (metadata, never a gate):** 2026-09-22; all time reads the live clock (`PG-IC-07`).

**Contract echo + source path.** Packet-recorded (`docs/packets/SG-094-taxonomy-schema-prompts.md:7`):
"Contract: recorded `0.30.0` == published (`c9c9ba3`; D125 adoption); echo verbatim + source path."
Live line, source `/home/andrei/storagegenie-contract/CODER.md:3`:
"**Contract version: 0.30.0** — **echo this line verbatim in your receipt.** It is the only proof that you".
Live: VERSION `0.30.0`, contract HEAD `c9c9ba3ee3715d102b55c740f4f2107344e7de3a` ("Contract payload
0.30.0"), `RULES.sha256` `18de7fd7…` == AGENTS.md header payload. Recorded == published == live; no drift.

**Role guard.** I am the Coder, never the Architect: I ran no dispatch verb for any ID and started or
polled no unit. No dispatch was needed.

---

## Summary

| Gate | Result |
|---|---|
| G1 schema field | `google_type_proposed: str \\| None = None` added; joins `_non_blank_when_present`; nullable, blank-rejected, unknowns-paired |
| G2 v4 prompts | 3 new `extract-*-v4.md` = v3 bytes + spec block + front-matter bump; v3 tracked diff empty; reader still v3 |
| G3 tests | T1 file extended +7 tests; pre-run 7 failed / 17 passed → post-run 24 passed (both raw, committed) |
| G4 docs | `SG-094.log`, `SG-094_report.md`, `SG-094_verify.log` |
| Suite | 2 failed, 452 passed (the 2 known decoder env reds, stash-reproved on bare BASE) |
| ruff | `All checks passed!` |
| mypy | 41 errors in 9 files == bare-BASE baseline (delta 0) |
| Secret gate | 0 matches |
| Migration | none — nullable pydantic field, no DB column, no writer/reader this slice |
| Scope | within ceiling; nothing else touched |

## G1 — schema field (nullable, transcribed-only, validated)

`backend/app/services/providers/schemas.py`:
- `google_type_proposed: str | None = None` declared beside the SG-079 v3 fields (after
  `category_proposed`).
- `"google_type_proposed"` added to the `_non_blank_when_present` decorator argument list (one entry;
  nothing else in that list changed). Blank (`"  "`) is rejected with the message
  `google_type_proposed must be non-blank when present`; null is legal.

Unknowns mechanism, verified on target (not inherited): `ExtractionOutput._unknowns_are_absent_fields`
(`schemas.py:136-153`) requires the named field to exist in `ExtractionItem.model_fields` and its value
to be `None`/`[]`; a fabricated value beside an unknowns entry raises. Because the field is now in
`model_fields`, `items.0.google_type_proposed` validates with a null value — pinned by test.

**`PG-SC-02` (in as many words):** this field is UNRECORDED this slice — no writer fills it, no reader
shows it; T3 owns both the writer and the reader wiring. The resolved `id+path+version` triple is not
produced here.

**No migration (stated):** `ExtractionItem` is a pydantic validation model, not a SQLAlchemy table; no
`app/models` or `app/alembic` reference to `category_proposed`/`google_type_proposed` exists (grep in
`SG-094_verify.log`). Nothing persists the field, so a nullable model field needs no DB migration.

## G2 — three frozen v4 prompts (v3 byte-identical)

Created `extract-food-v4.md`, `extract-medicine-v4.md`, `extract-cosmetics-v4.md`, each derived
deterministically from its v3 file: front-matter `template_version` v3→v4 and the spec §S2 block
inserted before `## Repair`. The full v3→v4 diffs are quoted raw in `SG-094_verify.log`; each shows only
the version line and the 4-line block.

The block is taken **verbatim from the spec file** (`docs/superpowers/specs/2026-09-21-google-taxonomy-design.md`,
§S2) — the packets-quote-the-spec rule:
```
## Product type (Google taxonomy)
Propose `google_type_proposed` as the verbatim full category path from the Google
Product Taxonomy, a top-level-only path when unsure, or null when illegible/absent
(plus the matching `unknowns` entry). Never invent numeric IDs or paths.
```

**v3 untouched:** `git diff` over the three v3 files is empty (quoted in the verify log) — the tracked
tree shows only the three new untracked v4 files. **Reader still on v3:** `reader.PROMPT_FILES` was not
touched; the live-prompt-map pins are green:
`tests/test_sg079_v3_schema.py::test_live_prompt_map_points_at_v3` and
`tests/test_sg080_ingest_pipeline.py::test_reader_loads_v3_for_all_categories_at_runtime` (both ran
green; see verify log).

## G3 — tests + gates

`backend/tests/test_google_taxonomy.py` extended (+7 tests, T1 file verified present):
- `test_google_type_proposed_declared_nullable_beside_v3_fields` — field exists, default `None`, parses null.
- `test_google_type_proposed_parses_verbatim_when_present`.
- `test_blank_google_type_proposed_is_rejected` — asserts the **specific** validator message (a bare
  `pytest.raises` would pass vacuously via `extra="forbid"`).
- `test_unknowns_entry_for_google_type_proposed_validates_with_null` — honest null + unknowns passes;
  fabricated value beside the entry fails.
- `test_v4_prompt_loads_through_real_loader_as_v3_plus_block[food|medicine|cosmetics]` — `PG-SC-12`:
  v3 base is read through the **real** `reader.load_prompt`; the expected block is parsed out of the
  **spec file**; v4 is loaded through the real loader (map monkeypatched in-test) and asserted equal to
  `v3 + version bump + block`. No re-typed prompt copy.

**FAIL-then-PASS (`PG-EV-09`), both raw in `SG-094_verify.log`:**
- PRE (tests added; field + v4 absent): `7 failed, 17 passed` — fails on the unknown keyword
  (`KeyError` on `model_fields["google_type_proposed"]`), `extra="forbid"` on the new field, and
  `FileNotFoundError` on the v4 files.
- POST (field + v4 present): `24 passed`.

**Gates:** full suite `2 failed, 452 passed` — the same 2 decoder env reds as bare BASE
(`tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
`…::test_ocr_has_text_boxes_and_mean_confidence`), stash-reproved (raw in verify log). ruff
`All checks passed!`. mypy `41 errors in 9 files` with change == bare-BASE baseline (delta 0).
Secret gate 0 matches over the tracked diff + new v4 files.

## Acceptance criteria

- Field present, nullable, blank-rejected, unknowns-paired — yes; the validator list otherwise behaves
  identically (full suite green modulo the known env reds).
- v4 = v3 bytes + verbatim block + version bump (diff quoted); v3 files byte-identical (empty diff
  quoted); reader still on v3 (both pins named green).
- Tests fail-pre/post-pass both committed raw; gates green; nothing outside the ceiling.
- **No vacuous pass:** the blank pin fails pre-impl for the right reason; the prompt pins derive expected
  content from the spec + real loader; the v3-untouched proof is the empty tracked diff. The 2 suite reds
  are pre-existing environment reds, not masked passes.

## Cross-product (`PG-IC-01`)

No acceptance criterion demands a reader flip, candidates wiring, a resolver call in the pipeline, a
migration, or a container act; each cell (schema · prompts · tests · docs) is independently satisfiable
here. No cell collides — the check exists on paper and is empty by construction.

## FINDINGS (premise corrections vs. the packet)

1. **`.rules-cache/` absent on this worktree.** AGENTS.md and the packet name the contract `.rules-cache/`;
   it does not exist here. The adopted contract lives at `/home/andrei/storagegenie-contract/` (git repo,
   HEAD `c9c9ba3`, VERSION `0.30.0`). Echo sourced from the real path; no impact.
2. **v4 H1 title.** SG-079's v2→v3 precedent also bumped the `# … (prompt vN)` title. SG-094's explicit
   formula ("v3 file's exact content + the spec's verbatim block + front-matter `template_version`
   bumped") does not include a title change, so I followed it literally: the v4 H1 still reads
   "(prompt v3)". Disclosed design call; one-line change if the Architect prefers a title bump.
3. **`rtk` wrapper swallowed `git diff` stdout** (exit 1, no output). Used `/usr/bin/git` directly.
   Environment finding, no impact.
4. No migration needed (per G1) — stated explicitly as required.

## Receipt note (notes ref, M20-corrected block)

Pushed the work to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. Note added on the work HEAD, the notes ref pushed, then fetched into a **mapped**
local name and verified with `git notes --ref=… show`; executed output pasted verbatim:

```
<RECEIPT_SHOW>
```

Dual-annotation of the final tip (note-anchor inoculation, SG-092 precedent):

```
<TIP_SHOW>
```

Final line: `note=yes`.

## UNCLEAR

- **FIRST READ:** whether the v4 H1 title should bump v3→v4. The v2→v3 precedent did; SG-094's explicit
  content formula did not. I followed the packet formula and left it — a disclosed design call.
- **DURING EXECUTION:** whether "v3 byte-identical" wants more than the empty tracked `git diff` (e.g. a
  committed content hash); a suite test cannot compare against a git base, so the empty diff is the proof.
- **REMAINING:** whether T3 must add the v4 files to the Docker build context / package data so the
  running service can load them at flip time. Out of this slice's ceiling; not touched.
