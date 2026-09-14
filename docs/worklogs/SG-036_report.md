# SG-036 report — Cosmetics category + opened-date tracking

**Dispatch-ID:** SG-036 · **Coder:** opencode · **Effort:** medium
**BASE REF:** `automation` → resolved commit `bc9d69f267f619a1dfe70e6a14b9ed620f59b615` (two fields, as required).
**WORK_HEAD:** the commit carrying this file; its hash is recorded by the G5 receipt note on
`refs/notes/storagegenie-coder-reports` (a committed file cannot contain its own commit hash).
**Work dir** `/home/andrei/StorageGenie` · **origin** `git@github.com:Andovol/StorageGenie.git`.
**DATABASE:** none — temp SQLite only; zero live rows, `/data/db` never opened. **Restart:** none — no
service touched, nothing deployed. **NETWORK:** none; **spend $0** (zero live provider calls).

**Model/effort per `CO-78`** — read from process arguments, never an identity line. Parent argv
(`/proc/$PPID/cmdline`), quoted verbatim:

```
opencode run --auto --dir /home/andrei/StorageGenie --variant medium # SG-036 — Cosmetics category + opened-date tracking (opencode, medium)
```

Coder `opencode`, effort `medium` (`--variant medium`), **model `unknown`** — the CLI default IS the
model and is omitted per policy; no model id appears in argv or the packet, so I write `unknown`
rather than a guess. Grandparent: `bash /usr/local/lib/dispatch/run-coder SG-036`.

## Verdict

GREEN. The third category is live end-to-end on the proven rails: `ExtractionItem.opened_date` shares
`expiry_date`'s `YYYY-MM-DD` validator (one validator, both fields); `extract-cosmetics-v1.md` follows
the food prompt shape exactly; `reader.load_prompt("cosmetics")` returns versioned text;
`cosmetics_personal_care` is active with declared tiers and per-category `opened_date_tracking=True`;
the corpus now covers cosmetics clean/no-date/partial with recipe-authored ground truth and
manifest count 10. FAIL-then-PASS raw: pre-change the targeted set is `7 failed, 20 passed` (pydantic
`extra_forbidden` on `opened_date`; `load_prompt("cosmetics")` raises), post-change `27 passed`. Full
suite green modulo the 2 base-proved decoder env reds; `ruff` clean; mypy delta 0; no alembic diff;
frozen prompts byte-identical; secret-value scan 0; no frontend change.

One judgment call outside the literal ceiling is disclosed below: **`eval/run.py` was touched** — the
packet's conditional allows it only if cosmetics scoring needs it, and it does.

## Premises verified; differences stated, not bent

- **G1 schema premise verified.** `ExtractionItem` (`schemas.py:30-54`) carried
  name/expiry_date/date_type/lot/confidence/uncertainty_reasons with an ISO validator on
  `expiry_date` only; no `opened_date`. The new field extends that exact validator.
- **G1 registry premise verified.** `reader.py:51-54` `PROMPT_FILES` mapped food/medicine only; no
  cosmetics file existed. `sg_prompt_category` remains an unvalidated `str` (`config.py:38`) — no
  config change, as the packet states.
- **G1 taxonomy premise verified.** `cosmetics_personal_care` was `active=False, tiers={}, "Phase 3"`
  (`expiry_tracker.py:112-114`) and `profile()` hardcoded `opened_date_tracking: False` in BOTH
  branches (`:79`, `:89`). `has_expiry` was already True. Activating and making the flag per-category
  required no new machinery.
- **Corpus path nuance (finding, not obstacle).** The packet says "`manifest.json` count 7". The
  7-fixture manifest is `backend/eval/corpus/sg029/manifest.json`; the top-level
  `backend/eval/corpus/` holds 5 legacy SG-026 JSONs without images. The SG-029 corpus is the right
  extension point (it owns the recipe + images + manifest); its `count <= 10` ceiling is satisfied
  exactly by 7 + 3. No correction to the tree beyond the intended extension.
- **`test_plugin_expiry.py` was asserted-inactive.** That test listed `"Cosmetics/personal care"` in
  its inactive-422 set. The packet ceiling explicitly includes this file, so updating it (cosmetics
  now 200 + profile assertions; inactive set reduced to household/documents) is expected, not a
  deviation.
- **No tables touched.** The SG-035 CHECK-constraint question does not bind here; per the packet it
  is deferred to SG-037. `test_postgres_dialect.py` needs NO registry change — stated and proven
  (`1 passed`, no tables added).

## G1 — schema + prompt + activation

- `backend/app/services/providers/schemas.py` — `opened_date: str | None = None` on `ExtractionItem`;
  `_date_is_iso` now validates `("expiry_date", "opened_date")` and names the offending field via
  `ValidationInfo.field_name`. Old payloads keep parsing (`opened_date` defaults to None).
- `backend/app/services/providers/prompts/extract-cosmetics-v1.md` (new) — front matter
  `template_version: extract-cosmetics-v1` / `category: cosmetics_personal_care` /
  `output_schema: ExtractionOutput` / `repair_policy: single-retry-then-fail`; no-inference system
  line; 9 rules; unknowns discipline; single-repair section. Printed opened/open-jar dates →
  `opened_date` only when fully legible; partial/illegible → null + unknowns + `needs_evidence`.
- `backend/app/services/providers/reader.py` — `PROMPT_FILES["cosmetics"]` line only.
- `backend/app/plugins/expiry_tracker.py` — `Category.opened_date_tracking` (per-category, after
  `phase` to preserve positional construction); `profile()` returns the category's flag in both
  branches; `COSMETICS_TIERS = {critical: 7, urgent: 30, upcoming: 90}`; `cosmetics_personal_care`
  active with that tier map, default `upcoming`, and `opened_date_tracking=True`.
  **Tier values are DECLARED UNCALIBRATED (`G-A9`)** — implemented as the packet's premise, not
  tuned, no data behind them.
- Classify proof: `test_cosmetics_classifies_without_a_new_task_type` shows the classify path returns
  `review_state="needs_evidence"` and opens exactly one existing `expiry.manual_entry` task — no new
  task type was invented.

## G2 — eval corpus + contract (offline only)

- `generate.py` — 3 cosmetics recipes (`clean_cosmetics`, `no_date_cosmetics`,
  `partial_label_cosmetics`) + `RECIPES` entries 08/09/10. Re-running the recipe reproduced the 7
  committed PNGs **byte-for-byte**; only the 3 new PNGs are new.
- Ground truth is **authored from the recipe** (clean: `opened_date="2031-04-10"`; no-date and
  partial: `opened_date=null` + unknowns + `needs_evidence`), never from a model.
- `manifest.json` count 7 → 10 (within the committed `<=10` ceiling).
- `eval/run.py` (CONDITIONAL, disclosed) — `CATEGORIES += "cosmetics"`; `score_fixture` now compares
  every date field the ground-truth item declares, so `opened_date` is scored and food/medicine
  scoring is byte-identical (baseline per-fixture scores unchanged). Touching this file is required:
  the corpus allowlist and the date comparison would otherwise drop cosmetics or miss `opened_date`.
- Contract tests added: `opened_date` ISO accept/reject; unknowns may name `opened_date` (and a value
  beside it fails); `load_prompt("cosmetics")` versioned; unknown category still raises; frozen prompt
  names still versioned.
- **`PG-SC-02` trace:** recipe (`generate.py`) → fixtures (ground truth + image) → `run.py`
  (`--check-only` integrity, then offline scoring). `corpus integrity OK: 10 fixtures`; scoring green.

## G3 — proof

- FAIL-then-PASS raw in the verify log §2–§3 (`7 failed, 20 passed` → `27 passed`), with the exact
  pre-change pydantic error quoted.
- Full backend suite from `backend/` (600s bound): `2 failed, 137 passed in 9.71s`; the 2 reds are
  **re-proved at base** (detached worktree @ `bc9d69f`: same 2, `132 passed`) — not inherited.
- `ruff check app tests`: clean. `mypy app`: `40 errors in 9 files (checked 63)` = base (delta 0); the
  touched files contribute zero (the 3 errors mypy reports for them are in `base.py`/`audit_service.py`).
- Negatives proven: `git diff --name-only -- backend/alembic` empty; frozen-prompt diff empty;
  frontend diff empty (so no `npm run build` is needed — zero frontend files touched); secret-value
  scan 0; `git diff --check` clean; `test_postgres_dialect.py` 1 passed (no registry change).
- Health: **unanswered** — `docker compose ps` shows 0 services, `curl :8000/v1/health` → `Not Found`,
  and `:8000` is held by a foreign process. No service was started (deploying is out of scope).

## Vacuous-pass disclosure (loud)

The 3 cosmetics `provider_output` caches are **authored offline references**, not model reads — no
`--live` leg runs in this slice. Their `1.000` scores are therefore corpus-integrity evidence
(fixture ↔ scorer wiring), **not a measurement of model extraction quality**. This is stated so the
"offline scoring runs" criterion is not read as a model-accuracy pass. A metered cosmetics leg is
owed before any accuracy claim (see REMAINING). The corpus-integrity gates are non-vacuous: 10
fixtures are really parsed by the strict schema, 3 categories and 5 case shapes are asserted, and the
scorer still discriminates (`sg029-03` scores 0.000 on a recorded reason).

## Acceptance criteria

- Starting tree clean, quoted; every premise verified with quoted reads. **Met.**
- `load_prompt("cosmetics")` versioned; `opened_date` honored-or-unknown (never guessed); unknown
  category raises; frozen prompts byte-identical. **Met.**
- Cosmetics classifies with `opened_date_tracking=True` and uncalibrated tiers; no new task type.
  **Met.**
- Cosmetics corpus clean/no-date/partial with recipe-authored truth; integrity green; offline scoring
  from committed fixtures. **Met** (scoring caveat above).
- Suite green modulo the 2 base-proved decoder reds; `ruff` clean; touched files add zero mypy errors;
  no alembic diff; secret scan 0; MODEL+effort provenance quoted; no vacuous pass (disclosed). **Met.**

## Budget (actual vs. bound; per leg)

| Leg | Bound | Actual |
|---|---|---|
| Probes (status/reads/health) | 120s each | sub-second–1.3s |
| Base suite (worktree) | 600s | 9.83s (ELAPSED 11.26s wall) |
| Targeted FAIL-then-PASS (pre / post) | 300s each | 1.51s / 1.40s |
| Full backend suite (post) | 600s | 9.71s (ELAPSED 11.15s wall) |
| `ruff` / `mypy app` / `mypy touched` / eval | 120/180/180/120s | 0.02s / 0.15s / ~2s / 0.36s + 0.50s |
| Early-close / overall ceiling | 1800s / 2400s | well under; no command killed |

## Live-state ledger

spend `$0` · live provider calls `0` · network attempts `0` (no network symbols in changed code; the
one `$schema` URL is a pre-existing JSON-Schema identifier) · key reads `0` (`.env`
`OPENCODE_API_KEY` line count `1`, value never read/printed) · live DB rows `0` · services
deployed/restarted `0` · frozen-prompt byte changes `0`.

## UNCLEAR — FIRST READ

- The packet says "printed PAO/open-jar dates" become `opened_date`. A real PAO is usually a period
  (`12M`), not a calendar date. I implemented the field as an ISO date and made the prompt rule
  explicit that `12M`-style periods are NOT open dates (null + unknown), while a printed open-jar
  **date** is transcribed when fully legible. If the Architect intends `opened_date` to also encode a
  PAO period, that is a schema-type change (not this packet) and I should be corrected.

## UNCLEAR — DURING EXECUTION

- `eval/run.py` was touched under the conditional. Required, not silent: cosmetics needed category
  registration and `opened_date` scoring. The edit preserves food/medicine scoring exactly.
- Cosmetics needed a `provider_output` cache to score offline, but `--live` is forbidden this slice.
  I authored offline references and labelled them as such; the alternative (leave caches absent) makes
  `run.py` fail offline scoring, and the alternative (a `--live` leg) violates the money posture.

## UNCLEAR — REMAINING

- Cosmetics model accuracy is unmeasured; a future metered cosmetics leg (or dropping the authored
  references from the accuracy claim) is owed.
- Cosmetics tier values (7/30/90) are declared-uncalibrated and await data.
- `ISS-7` entry-point run-2 for this Coder lane remains owed.
