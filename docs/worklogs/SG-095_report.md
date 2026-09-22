# SG-095 — Taxonomy T3: reader flip to v4 + triple wiring + gated candidates

**Dispatch-ID:** SG-095 · **Coder:** opencode · **Effort:** high (`--variant high`, from own argv) ·
**MODEL:** `unknown` (CLI default; no `--model` token on argv, per model policy) ·
**Spend:** **real $0.000000** (fully offline: no download, no provider call, no key read).

**BASE ref:** `origin/automation` → resolved commit `2700876ff69de33ded3ee87493d9e70863905220`.
**WORK_HEAD:** `7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe` (the pre-note work commit carrying this
report; the Receipt paste is this later docs-only commit).
**Work dir:** `/home/andrei/StorageGenie` · **Origin:** `git@github.com:Andovol/StorageGenie.git`.
**Authoring date (metadata, never a gate):** 2026-09-22; all time reads the live clock (`PG-IC-07`).

**Contract echo + source path.** Packet-recorded: "Contract: recorded `0.30.0` == published (`c9c9ba3`;
D125 adoption); echo verbatim + source path." Live line, source `/home/andrei/storagegenie-contract/CODER.md:3`:
"**Contract version: 0.30.0** — **echo this line verbatim in your receipt.** It is the only proof that you".
Live: VERSION `0.30.0`, contract HEAD `c9c9ba3ee3715d102b55c740f4f2107344e7de3a`, `RULES.sha256`
`18de7fd7…` == AGENTS.md header payload. Recorded == published == live; no drift.

**Role guard.** I am the Coder, never the Architect: I ran no dispatch verb for any ID and started or
polled no unit. No dispatch was needed.

---

## Summary

| Gate | Result |
|---|---|
| G1 reader flip | `PROMPT_FILES` v3→v4 for all three; live pins enumerated + flipped; injected pairs kept; v1/v2/v3 files + vendored data byte-untouched |
| G2 triple wiring | resolver runs per item; primary triple → gated `fields`; alternatives on `google_type_resolution`; split promotes each item's own triple |
| G3 runtime visibility | in-tree loader proof green; `.dockerignore` non-match established; hatch wheel carries data + prompts; in-image proof named as T4's |
| G4 tests | `test_google_taxonomy.py` +4 tests; FAILPRE `4 failed, 24 passed` → PASSPOST `28 passed` (both raw, committed) |
| Suite | `2 failed, 456 passed` (the 2 known decoder env reds, stash-proved on bare BASE) |
| ruff | `All checks passed!` (post and bare BASE) |
| mypy | `41 errors in 9 files` == bare-BASE baseline (delta 0) |
| Secret gate | 0 identifiers, 0 real-looking key values |
| PG-SC-11 | end-relative grep over touched test files: 0 hits |
| Migration | none — triple rides existing `proposed_fields_json`/`value_json` Text storage (proved) |
| Scope | within ceiling + the G1-mandated pin flips (see Finding 5) |

## G1 — reader flip v3→v4 + version pins

`backend/app/services/providers/reader.py:54` `PROMPT_FILES` flipped to `extract-{food,medicine,cosmetics}-v4.md`.
The two-line SG-080 comment became a two-line SG-095 comment (line count deliberately preserved — Finding 3).
`load_prompt` is unchanged; the version it returns is read from each file's front matter.

**Enumeration (paths + lines) — `SG-095_verify.log` § G1 ENUMERATION.** Every `extract-*-vN` /
`PROMPT_FILES` / `prompt_template_version` pin in `backend/` was listed. The flip invalidates the
**live-map** pins, which were flipped v3→v4:

- `test_sg079_v3_schema.py:11,196-203` (map + runtime version; test renamed `…_points_at_v4`)
- `test_sg080_ingest_pipeline.py:5,8,18,208-216,223-234,593-602` (map, ledger row, wire shape; tests renamed)
- `test_ai_pipeline.py:207,505,518`
- `test_extraction_contract.py:303`
- `test_phase2_e2e.py:254,279`
- `test_sg049_v2_extraction.py:135-137` (live-map leg; test renamed `…_are_v4_…`)
- `test_google_taxonomy.py` T2 prompt test now loads the v3 baseline explicitly (the live loader is v4)

**Injected-version self-consistency pair — EXISTS, kept with reason.** `test_sg049_v2_extraction.py:204,213`
(injected scripted `analyzing` dict `"extract-food-v2"` + its assertion) and `test_review_split.py:82,130,275`
(seeded proposal `"extract-food-v1"` + split round-trip). These are provenance-plumbing literals, not the
live `PROMPT_FILES` map, so the flip does not invalidate them. `test_sg080_ingest_pipeline.py:373,569` are
likewise hand-built/seeded literals (kept). Frozen-file pins (v1/v2/v3 on disk) are kept — those files remain
as the rollback reference; `git diff` over them and the vendored taxonomy is empty (verify log).

**No-migration proof.** No `google_type*`/`taxonomy_version` reference exists in `backend/alembic/` or
`backend/app/models/` (`rg` exit 1). The triple persists inside the existing
`candidate.proposed_fields_json` (Text, `candidates.py:465`) and, after commit, `assertion.value_json`
(Text, `assertion.py:16`). Existing storage; no new column, no alembic revision, no migration written.

## G2 — triple wiring + gated candidates

The proposal builder is `build_candidate_from_extraction` (`candidates.py`). It now:

- declares `GOOGLE_TYPE_FIELDS = ("google_type_id","google_type_path","taxonomy_version")` and adds all
  three to `GATED_FIELDS` and `ALLOWED_CANDIDATE_FIELDS`;
- calls `resolve_google_type` **per item** (`_google_type_resolution`) and `bucket_for` on the outcome
  (the suggested `bucket` is recorded on the resolution; the six expiry buckets stay behaviour authority, D111);
- promotes the **primary** item's resolved triple into `fields` beside `category_proposed` — all three, or
  none (nullable together), as extraction-sourced gated proposals;
- attaches each item's own resolution to its `ai_items[i]["google_type_resolution"]`, so a split child
  promotes **its own** triple (`_split_child_fields` adds the three to `item_derived` and re-derives).

**`UNCLEAR`** keeps the resolver's top-k `alternatives` on `google_type_resolution` and maps **none** of
them; no triple field is written for an unclear/uncategorized item.

**0.0-threshold proof with contrast (real commit path).** `test_resolved_item_carries_triple_gated_through_route_and_commit`
runs the real pipeline with a scripted provider at `sg_confidence_threshold=0.0`, reads the triple back
**through `GET /v1/candidates/{id}`** (not around it), accepts through the real decision route, and asserts
each of the three committed assertions has `review_state="proposed"`, while the non-gated deterministic
`status` assertion is `review_state="accepted"` (`source_type="deterministic"`). `test_unclear_item_surfaces_alternatives_and_maps_nothing`
commits an unclear item and asserts **zero** Google assertions exist. Nothing auto-accepts on the triple.

**Read-back (`PG-SC-02`).** The writer (this builder) and the reader (`GET /v1/candidates`) are both
exercised: the route test asserts the three gated field envelopes carry the resolved values. D111 layered
rule holds — the triple is stored alongside, both gated; the 6 expiry buckets remain behaviour authority.

## G3 — runtime-visibility verdict (per mechanism; image proof is T4's)

1. **`backend/Dockerfile:17` `COPY backend/ ./`** — copies the whole `backend/` tree into `/app`; line 19
   `pip install … -e .` points the package at that copied source, so `app/data/…` and `app/services/…/prompts/…`
   are present at runtime.
2. **`.dockerignore` `data` (line 19) + `backend/data` (line 20)** — per Docker docs, leading/trailing
   slashes are disregarded and matching uses Go `filepath.Match`; a no-slash pattern matches only at the
   **context root** (docs' `temp?` row: "in the root directory"). So `data` == root `/data`, `backend/data`
   == `/backend/data`; neither matches `/backend/app/data`. No `**/data`/`app/data` pattern exists →
   `backend/app/data/google_taxonomy/` and the v4 prompt files **survive**.
3. **`backend/pyproject.toml:48` hatch `packages = ["app"]`** — non-`.py` data files **do** ride the wheel:
   a locally built wheel (`hatchling build`) lists `app/data/google_taxonomy/2021-09-21.txt` (482896 B) and
   all `extract-*-v4.md` (verify log § G3 MECHANISM (3)).

**In-tree loader proof (green).** From the repo root, the REAL resolver loaded the vendored file
(`_load()` → 5595 rows, version `2021-09-21`) and the REAL `reader.load_prompt` returned v4 for all three
categories with the spec block present. **The IN-IMAGE proof (bytes in the built image) is explicitly T4's
(SG-083 precedent) — not built here.**

## G4 — tests + gates

`test_google_taxonomy.py` extended (+4 T3 tests, + a local `sg095_env` fixture modeled on SG-080):
live reader v4 runtime; resolved triple via route + gated commit with 0.0 contrast; unclear alternatives +
no mapping; multi-item split per-item triple. The existing T2 v4-prompt test was adjusted to load the v3
baseline explicitly (the live loader is now v4).

**FAIL-then-PASS (`PG-EV-09`), both raw in `SG-095_verify.log`:** PRE (source stashed) `4 failed, 24 passed`
— failure modes: map still v3, missing `GOOGLE_TYPE_FIELDS`, missing `google_type_resolution` (KeyError).
POST `28 passed`. A separate G1 pin pair (`test_live_prompt_map_points_at_v4`) also fails pre-flip / passes post.

**`PG-SC-12`:** assertions run the REAL resolver over the REAL vendored file, the REAL `reader.load_prompt`,
the REAL pipeline through the named injection seam, and the REAL `GET /v1/candidates` route + decision
commit path — no re-implemented boundary, no re-typed prompt copy (the expected v4 block is parsed out of
the spec file).

**Gates:** full suite `2 failed, 456 passed` (the same 2 decoder env reds as bare BASE, stash-proved);
ruff `All checks passed!`; mypy `41 errors in 9 files` == bare-BASE (delta 0); secret gate 0 identifiers /
0 key values; PG-SC-11 end-relative grep 0 hits.

## Acceptance criteria

- Reader serves v4 at runtime for all three categories (asserted through the real loader); v1/v2/v3 pins
  enumerated with the flip list quoted; injected pair kept-iff-exists with reason — **yes**.
- Resolved item shows the full triple + version through `GET /v1/candidates`; unclear item gates with
  alternatives; 0.0-threshold proof with contrast; no auto-accept anywhere on the triple — **yes**.
- Runtime-visibility verdict per mechanism quoted; in-tree loader proof green; image proof named as T4's — **yes**.
- Tests fail-pre/post-pass both committed raw; gates green; nothing outside the ceiling + the G1 pin flips;
  no vacuous pass; no-migration proof stated — **yes**.

**No vacuous pass.** The fail-pre is a real run against the un-wired tree (distinct failure modes per test,
quoted raw); the 0.0-threshold test commits through the real route; the contrast field is a real
deterministic assertion; the two suite reds are pre-existing environment reds, not masked.

## Cross-product (`PG-IC-01`)

No criterion demands a deploy, filter UI, analytics change, provider call, migration write, or container
act — each cell (reader · candidates · tests · docs) is independently satisfiable. The one collision found
was a suite-green collision (privacy-audit line-number pin) resolved by the minimal in-ceiling repair
(Finding 3). No cell collides by design; the check exists on paper and is empty.

## FINDINGS (premise corrections vs. the packet)

1. **`GET /v1/candidates` is `GET /v1/candidates/{candidate_id}`.** There is no collection route; the
   gated fields are read back through the per-candidate route (as SG-080 G3 already did). No impact.
2. **The packet's scope ceiling omits the pin flips G1 requires.** G1 explicitly orders the SG-080
   precedent (enumerate tree-wide and flip every invalidated pin); the suite can only stay green if the
   live-map pins in `test_sg079/test_sg080/test_ai_pipeline/test_phase2_e2e/test_extraction_contract/
   test_sg049` are flipped. I treated the G1 instruction as governing (as SG-080 did) and disclose the six
   files touched. No behavioral code outside `reader.py`/`candidates.py` changed.
3. **Brittle absolute-line-number pin (collision, repaired).** `test_privacy_audit.py` asserts the
   `redact_image(` call sites by absolute line (`reader.py:402`). Any added line shifts it. I kept the
   reader comment at its original two lines so the call stays at `:402`, avoiding an out-of-ceiling edit.
   This is a PG-SC-11-adjacent brittleness worth a later hardening slice.
4. **`UNCLEAR` alternatives surface on the proposal, not through the route.** The acceptance says the
   *resolved triple* is shown through `GET /v1/candidates`; alternatives are recorded on
   `proposal["google_type_resolution"]` (and per `ai_item`). The read route returns only `fields` and the
   API file is outside this slice's ceiling, so alternatives are not exposed through it. Disclosed design
   call; a route/UI change would be a later slice.
5. **v4 prompt H1 still reads "(prompt v3)"** (carried from SG-094 Finding 2) — unchanged here.
6. **`rtk` wrapper** can swallow piped stdout in some forms; raw git/`rg` used for evidence capture.

## Receipt note (notes ref, M20-corrected block)

Pushed the work to `automation`; worktree clean (`CO-55`). No push to `storagegenie-evidence`, no
`{{RECEIPT_CMD}}`. The note is added on the WORK_HEAD, pushed to
`refs/notes/storagegenie-coder-reports`, then fetched into a **mapped** local name and verified with
`git notes --ref=… show`; executed output pasted verbatim:

WORK_HEAD (pre-note work commit) = `7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe`.

Commands executed (raw):

```
$ git rev-parse HEAD
7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   2700876..7475c42  automation -> automation
push_exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports show 7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe
error: no note found for object 7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe.
existing_exit=1
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-095 | Report: docs/worklogs/SG-095_report.md | Work-HEAD: 7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe" 7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   3bbfe22..a48cc40  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg095-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg095-verify
fetch_exit=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg095-verify
a48cc4092a7b006c8c9de371065b9ab1c6285c06
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg095-verify show 7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe
```

Pasted `show` output (verbatim, from the FETCHED mapped ref
`refs/notes/storagegenie-coder-reports-sg095-verify` = `a48cc4092a7b006c8c9de371065b9ab1c6285c06`):

```
Dispatch-ID: SG-095 | Report: docs/worklogs/SG-095_report.md | Work-HEAD: 7475c42dfd539bfd9814bacf8e2efe5cfc5d66fe
```

No existing note was found before adding (`existing_exit=1`), so this was not an existing-note refusal.
The final tip (this docs-only paste commit) is dual-annotated with the same note body so the engine's
`note_anchor=END_HEAD` readback resolves (SG-092 note-anchor inoculation precedent).

note=yes

## UNCLEAR

- **FIRST READ:** whether "`UNCLEAR` surfaces top-k alternatives to the reviewer" wants them in the
  candidate `fields` (the only reviewer route surface) rather than on the proposal record. The plan's
  Produces names exactly the three triple fields, and the API route is out of ceiling, so I kept the triple
  as the three fields and alternatives on `google_type_resolution` (Finding 4).
- **DURING EXECUTION:** whether the packet wants a 4th gated field for alternatives; adding one would put a
  list value into the committed assertion stream, which the plan's Produces does not name. Not added.
- **REMAINING:** whether the reviewer UI/route must later expose `google_type_resolution` (alternatives +
  suggested bucket) — deferred with the catalog filter (spec non-goal) and T4.
