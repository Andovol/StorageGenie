# SG-155 — Scene T0: OpenRouter client seam + catalogue/envelope proof, read-only $0

Autonomy: L3 (D-1009-7 Scene arc T0→T1b→D7). Plan Task 1: `docs/superpowers/plans/2026-10-09-context-scene.md`. Spec §§2–3: `docs/superpowers/specs/2026-10-09-context-scene-design.md`.

> My premises are hypotheses about the tree carrying this packet. **Verify each before building on it; a
> difference is a finding, not an obstacle.** Where your numbers, paths or quotes differ from mine,
> investigate and explain — **do not bend yours to match. Correcting me is worth more than agreeing.**

**BASE REF: automation.** Resolved commit goes in the report, never here.
**DATABASE: none.** No datastore is opened, temp or live.
**Restart: none.**

## Why this exists

Locked: scene renders route through OpenRouter (D-1009-5), one owner-placed key, T0 is read-only $0 (D6/D-1009-4). CONFIRMED (read 2026-10-09): `backend/app/services/enrich/jina.py:1-140` key seam (`resolve_api_key` explicit > `settings.jina_api_key` > env, `Authorization` added at send time, key never stored/logged); `backend/app/config.py` whole file (63 lines — `jina_api_key` field + `sg_*_cap`/`sg_consent` pattern to mirror); `.env.example` at repo root; OpenRouter docs fetched 2026-10-09 (`POST /api/v1/chat/completions`, `tools: [{type: openrouter:image_generation, parameters}]`, `tool_choice`, `max_tool_calls`/`stop_server_tools_when`, `GET /api/v1/models`, `usage` object, temporary `imageUrl`, beta status). INFERRED: exact stop-condition schema and reference-image support — T0 verifies both live, nothing downstream assumes them.

## G1 — client seam

Create `backend/app/services/scene/__init__.py` + `backend/app/services/scene/openrouter.py`: `OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"`, `resolve_openrouter_key(explicit=None)` (jina seam shape), `build_scene_request(photo_ref, brief, image_model, orchestrator)` returning the exact sendable dict (`tool_choice: "required"`, `max_tool_calls: 1`, spend-stop from the T0-verified schema), loud refusal constructors (`missing_key`, `refused_consent`, `over_cap`). No send in tests — tests assert the built dict offline.

## G2 — config + example env

`backend/app/config.py`: add `openrouter_api_key: str | None = None` + `sg_scene_cap: float | None = None` (both off-by-default, jina-field comment shape). `.env.example`: names-only `OPENROUTER_API_KEY=` line (SG-097 precedent — name only, never a value).

## G3 — live legs, $0, read-only

T0a: `GET /api/v1/models` on the lane, filter image-output models, record the two shortlist slugs + per-call prices + orchestrator candidates. T0b ($0, no render): confirm the exact `stop_server_tools_when` condition schema and whether the image tool takes a source/reference image or is orchestrator-vision-only — both answers verbatim; T1b is blocked without them. Absent key is NOT grounds to stop: ship G1+G2+offline tests, report both legs UNANSWERED (PG-SC-03).

## G4 — gates

Full backend suite + ruff + mypy; suite reds get the stash leg (decoder-reds class stash-proved if present). No served-code change → no refresh (D145).

## Constraints

Scope ceiling: the G1/G2 files + `backend/tests/test_sg155_scene_t0.py` + `docs/worklogs/SG-155_*` logs; everything else read-only; no migration, no restart, no served-code change. Secrets: key name-only everywhere (report, logs, snapshots); CO-100 — no secret file copied, tests use monkeypatch (PG-EV-13). Privileged denial: pasted §3 block governs. Stash: as G4. Test scope: FULL suite (derived-set block not pasted). Expected duration 600s (recent read-only slices ~300s + two HTTP legs + suite; lane enforces `RUN_BUDGET_S`). Hang bounds per class: ordinary commands 120s, suite 600s, HTTP legs 120s — none near the 900s idle kill. Simplicity: mirror jina.py, no new package. Cross-product (PG-IC-01): G1 writes in-ceiling files — allowed; G3 issues GET reads — allowed (read class, no container/runtime launch needed); no criterion requires a write, restart, migration, or secret — no collisions. Stop precedence (PG-IC-03): missing-key refusal wins over retry — a refused leg is reported unanswered, never retried into spend.

> A denied privileged operation is never a signal to route around it. **A step you cannot complete
> without privilege is reported as unanswered, and the rest of the slice still ships.**

> If any acceptance criterion could pass **vacuously** — an empty diff, an empty set, a skipped gate, a
> test that never invokes the function, a grep scoped so narrowly it could not have matched — say so
> loudly rather than reporting a pass.

> Report the model and reasoning effort by reading them from your process arguments or provider metadata,
> never from a system-prompt identity line. **Write `unknown` rather than a plausible guess.**

> **DO NOT HANG.** Every command runs under a stated timeout. **Name the bound in the packet** — 120s is
> a reasonable default for ordinary commands, and a build, a test suite or a migration gets the bound its
> own work needs. **A command producing no observable progress within its bound is killed and reported.**
> **No bound reaches the lane's idle kill (`IDLE_KILL_S`, default 900 s):** a run printing nothing for
> that long is killed whole. Run longer work in the background and check it with short calls.
> Never run an interactive command. A command you had to kill is a finding worth reporting, not a failure
> to hide. *(D17: a single global 120s kill was an uncalibrated hard cap that would terminate valid work.)*

> Design calls inside these constraints are yours: decide and report, do not ask. A constraint you find
> wrong or impossible is a STOP. **If you stop for any reason**, commit what you have with
> `BLOCKED: <reason>` as the first line, push, publish the receipt, and leave the worktree clean.
> Report every issue and disagreement, including ones outside this slice's scope. End with the three
> UNCLEAR lines — FIRST READ, DURING EXECUTION, REMAINING.

## Acceptance criteria

- A1: new tests FAIL-pre→PASS-post, BOTH runs committed (`docs/worklogs/SG-155_failpre.log`, `docs/worklogs/SG-155_passpost.log`) — prose quotes do not satisfy (PG-EV-09).
- A2: offline shape test (no network, no key — PG-EV-04): built dict asserts endpoint URL, `tool_choice == "required"`, exactly one `openrouter:image_generation` tool entry, `max_tool_calls == 1`, headers without `Authorization`, photo as message image content.
- A3: T0a rows quoted — two shortlist slugs + per-call prices + orchestrator candidates (or UNANSWERED with the refusal named).
- A4: T0b answers verbatim — reference-image support yes/no + stop-condition schema (or UNANSWERED). These exact values are T0-PINNED for T1b.
- A5: production writes == 0 AND production reads other than the two named GETs == 0 — either direction stops before writing (PG-IC-08).
- A6: suite + ruff + mypy green modulo stash-proved base reds; guards invoked: PG-EV-04, PG-EV-09, PG-SC-03, PG-IC-01, PG-IC-03, PG-IC-07, PG-IC-08, PG-IC-09.

## Report

Echo `SG-155` as the first token. Destinations: worklog `docs/worklogs/SG-155_report.md` + fail/pass logs above. Publish the receipt through the bound `{{RECEIPT_CMD}}` wrapper (CO-97 note). Carry a T0-PINNED section (slugs, prices, both T0b answers) verbatim for the T1b packet. Close with FIRST READ / DURING EXECUTION / REMAINING.
