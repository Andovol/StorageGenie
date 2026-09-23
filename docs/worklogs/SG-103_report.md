# SG-103 — Reviewer alternatives: `web_alternates` as first-class proposal rows (report)

**Dispatch-ID:** SG-103
**Coder / effort:** `opencode` / `high` — effort read from the packet dispatch head (`effort: high`); **model: `unknown`** (no model id is sent per policy, and no process argument or provider metadata exposed one — reported `unknown` rather than guessed from the system-prompt identity line).
**Work dir:** `/home/andrei/StorageGenie` · **Remote:** `origin` = `git@github.com:Andovol/StorageGenie.git`
**BASE (requested ref `origin/automation` resolved):** `d77756d95946f64c2f6202698efde359bd0e6474`
**WORK_HEAD:** `bb438057cba939e93867bc31cbd72f4389fb0965` · **Report:** `docs/worklogs/SG-103_report.md`
**Contract echo (verbatim):** `0.33.0` — recorded in `STATE.md:4` and `AGENTS.md:4`; published side `/home/andrei/storagegenie-contract/VERSION` → `0.33.0`, HEAD `b232b845d74e89cb346c60fa4b9a40ec401c42dd` "Contract payload 0.33.0", **G-L1 payload hash executed**: `sha256sum RULES.md` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == `RULES.sha256`, `sha256sum -c` → `RULES.md: OK`. Recorded == published == `0.33.0`.
**DATABASE: none** (existing candidate table only; tests on temp DBs; no production writes). **Restart: none. Deploy: none. Container actions: none** (`PG-PR-04`). No model/migration: `app/models` + `alembic` diff **empty**.
**Spend (real $):** **$0.000000** — every HTTP leg is a scripted `httpx.MockTransport` seam; no socket opened, no key crosses a wire, no provider invoked. No metered call exists on any path.

---

## Result in one line

The Enrich endpoint now computes the asset's **label side from its assertions**, runs the **REAL `merge_web_fields`** against the web fields, stores the result in the proposal's `web_alternates`, and serves it in the response **and** through the REAL `GET /v1/candidates/{id}` route — so a label/web conflict keeps the **label** value in the proposal while the **web** value stays visible as one alternate row with its full source triple. Proven by a new offline file (fail-pre 3F/1P → pass-post 4P) with **zero live touch**.

## G1 — label-side existing + the REAL merge (the delegated design call): **MET**

`backend/app/api/v1/enrich.py` (+44/−2):

- **New `label_existing_fields(db, asset)`** reads the asset's `Assertion` rows, keeps only the `field_path`s in the frozen SG-082 `LABEL_VISIBLE_FIELDS`, skips blank/unparsable values, and returns provenance envelopes `{"value", "source_type"}` so the REAL merge reads them through `_field_parts`.
- `trigger_enrich` now runs `label_existing = label_existing_fields(db, asset)` then `fields, alternates = candidates.merge_web_fields(label_existing, web_fields)`. The rule is **not re-implemented**, and `apply_web_fields_to_proposal` is **not** called blindly (that is the trap: it merges against the proposal's own web fields, which is the same source on both sides — re-verified on target, `existing = _asset_fields(proposal)`).
- `"web_alternates": []` → `alternates` in the stored proposal **and** in the endpoint response body.
- `backend/app/api/v1/candidates.py` (+4/−0, **F-SG103-2**): `GET /v1/candidates/{id}` now returns `web_alternates` (validated as a list) so the rows round-trip through the REAL reader route, as the acceptance criterion requires.

**Design calls (named per PACKET.md autonomy):**

1. **The label side is the asset's label-visible ASSERTIONS, not the denormalised asset columns.** Both commit paths (`_create_asset_for_candidate`, `asset_service.create_asset`) write a `display_name` assertion beside the column, so every production asset that reaches enrich carries one; the column's `display_name` still feeds the query name via `read_asset_identifiers`. Reading the column would double-count and would invalidate the SG-098/102 fixtures (which seed assertions only). **F-SG103-3.**
2. **`brand` is not label-visible** (absent from `LABEL_VISIBLE_FIELDS`; no web path emits a brand), so the conflict is on `display_name` (label assertion) vs the web `display_name`, not on `brand`. **F-SG103-4.**
3. **Label values are provenance envelopes**, not bare scalars, so the merged field keeps a `value`/`source_type` shape; this also keeps the pre-existing SG-098 `.value` assertion valid with **zero existing-test churn**.

## G2 — tests + gates ($0, temp DBs only): **MET**

New `backend/tests/test_sg103_web_alternates.py` — 4 tests driving the REAL endpoint/router/clients and the REAL candidate reader (scripted `MockTransport` seams only):

1. **Conflict:** label `display_name` assertion + brand assertion + web OFF hit → proposal keeps the label value (`source_type: "user"`); the gap field `identifier` fills from web; **exactly one** alternate carries the full triple (`field`+`value`+`source_type: web:OpenFoodFacts`+`source_url` containing `openfoodfacts.org`+`retrieved_at`); the rows **round-trip through `GET /v1/candidates/{id}`**.
2. **No conflict:** a label `expiry_date` assertion (no web counterpart) is retained; web fills `display_name`+`identifier`; `web_alternates == []` on the endpoint **and** the route.
3. **Brand-absent:** no brand assertion → the Jina fallback fires (non-empty alternates) and **no** alternate field is `brand`; `brand` is absent from fields. (Structural — see the vacuity note.)
4. **Regression:** consent-false → 403, **0 sends, 0 candidate rows**.

- **Fail-then-pass, BOTH raw committed (`PG-EV-09`, `PG-EV-01`):** fail-pre = clean HEAD worktree + the final test file → **3 failed, 1 passed in 1.05s** (raw R-FAILPRE); pass-post = **4 passed in 0.95s** (raw R-PASSPOST). The 1 pass-pre test is the consent regression, which holds pre and post by design; the 3 behaviour tests genuinely fail pre (`assert 'Jacobs Cronat Gold instant coffee' == 'Jacobs Cronat Gold'`, `KeyError: 'expiry_date'`, `KeyError: 'web_alternates'`).
- **Targeted:** `sg103 + sg098 + sg102 + sg100 + candidate_read + candidates` → **34 passed in 3.06s** (raw R-TARGETED).
- **Full suite:** **2 failed, 512 passed in 23.37s** (raw R-SUITE); the 2 are the known decoder env reds, **stash-proved** at a clean HEAD worktree (`test_signals.py` 2F/5P, raw R-STASHPROOF). Baseline was 2F/508P; +4 new tests → 512.
- **Gates:** ruff **clean**; mypy **41 → 41** errors (delta **0**, 84 source files); secret-pattern grep over changed/new files **0 real**; key NAMES **0** in changed files.
- **Scope:** `git diff --stat HEAD -- app/models alembic` → **empty** (no model/migration; `PG-SC-02`).

## Findings (disclosed)

- **F-SG103-1 — packet line-ref drift (benign).** `"web_alternates": []` sits at `api/v1/enrich.py:185` pre-edit, not `:173` (SG-102 shifted the file). The premise (hardcoded empty + helper unused) held.
- **F-SG103-2 — ceiling vs acceptance (resolved for acceptance).** The packet's scope ceiling enumerated only `api/v1/enrich.py` + the new test + `docs/worklogs`, yet the acceptance criterion requires the alternates to round-trip through the REAL `GET /v1/candidates/{id}` route, which did **not** serve `web_alternates`. Resolved with a **4-line additive** hunk in `backend/app/api/v1/candidates.py` (validated list; no existing key changed; the frontend ignores unknown keys). A failing test proves the hunk (M45 terms). Precedented by SG-102's disclosed SG-098 test edit.
- **F-SG103-3 — label side is assertion-driven (deviation from "display_name off the asset").** The asset's denormalised `display_name` column is used only as the query name; the label value comes from the `display_name` assertion. In production both commit paths write that assertion, so real label names win; only a hand-seeded asset with a column and no assertion would not conflict. Reported, not hidden.
- **F-SG103-4 — the conflict is on `display_name`, not `brand`.** `brand` is absent from `LABEL_VISIBLE_FIELDS` and no web path emits a brand, so the packet's "asset WITH brand assertion + web brand" could not be built literally. The conflict test seeds a brand assertion (query) **and** a label `display_name` assertion (the value that wins) against the web `display_name`.
- **F-SG103-5 — "brand-absent yields no brand alternate" is structural.** No web path emits a brand and `brand` is not label-visible, so the criterion cannot be non-vacuously **failed** on this tree. The test asserts the structural property over a **non-empty** alternate list and is reported as such.

## Cross-product / privacy (`PG-IC-01`, `PG-SC-05`)

No criterion demanded fetchers/synthesis/writer changes, a migration, frontend, deploy, restart, container act, or any metered call — no cell collides; stated so the check exists on paper. Reads used TestClient + host commands only; no image pulled/run; `docker compose config` never run. Identifiers TEXT only (never photos/GPS); key never in any file, log or assertion. No fixed dates in code — fixture timestamps are sample data. `STATE.md` / `AGENTS.md` / `docs/packets` untouched.

## Acceptance criteria — status

| Criterion | Status | Evidence |
|---|---|---|
| Conflict yields label value kept + one alternate with the full source triple | **MET** | test 1: label `display_name` kept; exactly one alternate with field/value/source_type/source_url/retrieved_at |
| No-conflict yields web-filled fields + `[]` | **MET** | test 2: `display_name`+`identifier` from web; `web_alternates == []` |
| Alternates round-trip via the REAL candidates route | **MET** | test 1 GET equality; test 2 GET `[]` |
| Brand-absent yields no brand alternate | **MET (structural)** | test 3; F-SG103-5 |
| Tests fail-pre/pass-post both committed raw | **MET** | R-FAILPRE 3F/1P; R-PASSPOST 4P |
| Gates green; $0; production untouched; no vacuous pass | **MET** | suite 2F/512P; ruff clean; mypy Δ0; secret 0; models/alembic empty; scripted transports only |

**Question each criterion answers (`PG-SC-09`):** **G1** — do label/web conflicts stay BOTH visible with sources instead of collapsing? **Yes:** the merged field keeps the label value and the web value survives as a `web_alternates` row with its source triple. **G2** — is it proven through the real commit path with zero live touch? **Yes:** the endpoint's own `db.commit` writes the candidate and the REAL `GET /v1/candidates/{id}` reads it back, with every HTTP leg a scripted seam ($0).

**Vacuous-pass check (`PG-EV-01`, loudly):** the 3 behaviour tests **genuinely failed** pre-change with raw output committed, and the 1 pass-pre test is a gate test that legitimately holds pre and post. The conflict test asserts the **alternate value differs from the label value** (not merely that a list is non-empty) and asserts the **full source triple**, so it cannot pass on an empty or mis-keyed merge. The no-conflict test asserts an **empty** list plus a retained non-web label field, so it catches both a spurious alternate and a dropped label field. **Where this slice is weaker than it looks:** (a) F-SG103-5 — the brand-absent criterion is structurally guaranteed and cannot be failed on this tree; (b) the label side is assertion-driven, so a hand-seeded asset without a `display_name` assertion is treated as having no label name (not a production state); (c) the frontend still does not render `web_alternates` (named backlog), so the rows are served but not yet shown in the review UI.

## Interim honesty (`PG-PR-05`)

The production service is **old code**; the endpoint's new alternates behaviour is unreachable in production until a later owner-gated deploy rider. Proof in this slice is **tests on temp DBs**, never the deployed service. Production was not touched.

## Report note on the notes ref (receipt)

Work pushed to `automation`; worktree clean. Note added on `WORK_HEAD`, notes ref pushed, and verified against the **fetched, mapped** ref. Executed, verbatim:

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show bb438057cba939e93867bc31cbd72f4389fb0965   # pre-check
error: no note found for object bb438057cba939e93867bc31cbd72f4389fb0965.   (exit 1 -> no existing note, add proceeds)

$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-103 | Report: docs/worklogs/SG-103_report.md | Work-HEAD: bb438057cba939e93867bc31cbd72f4389fb0965" bb438057cba939e93867bc31cbd72f4389fb0965
note add exit=0

$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   c668336..0e7006c  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports

$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-fetched
From github.com:Andovol/StorageGenie
   c668336..0e7006c  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-fetched

$ git notes --ref=refs/notes/storagegenie-coder-reports-fetched show bb438057cba939e93867bc31cbd72f4389fb0965
Dispatch-ID: SG-103 | Report: docs/worklogs/SG-103_report.md | Work-HEAD: bb438057cba939e93867bc31cbd72f4389fb0965
show exit=0
```

No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`. The final tip is dual-annotated too (note-anchor inoculation, SG-092 precedent). `note=yes`.

---

## UNCLEAR

- **FIRST READ:** the packet's trap claim held exactly — `apply_web_fields_to_proposal` merges web against the proposal's own fields, which for enrich are the web fields. The two premises I had to decide against the packet's wording: (a) the label side is the asset's **assertions**, not its denormalised columns (F-SG103-3), because both commit paths write the assertion and the column would double-count; (b) `brand` cannot be a merge field or alternate (F-SG103-4), because it is not in `LABEL_VISIBLE_FIELDS` and no web path emits it. The packet's `:173` line-ref was pre-hunk; the flip sits at `:185` pre-edit.
- **DURING EXECUTION:** the acceptance criterion "round-trip through the REAL `GET /v1/candidates/{id}` route" was not satisfiable within the packet's enumerated ceiling — the route did not serve `web_alternates` — so a 4-line additive hunk in `api/v1/candidates.py` was required (F-SG103-2). Also discovered: `apply_web_fields_to_proposal` has **no test** on this tree, so its trap was proven by reading the code and by the pre-change failure of the conflict test, not by an existing regression.
- **REMAINING:** the frontend still does not render `web_alternates` (named backlog, per the Enrich standing rule); the new behaviour is undeployed (owner-gated rider); a committed brand-bearing web path does not exist, so a `brand` alternate is unrepresentable until a later slice adds one; `.rules-cache/` remains absent (published hash verified from the contract checkout).
