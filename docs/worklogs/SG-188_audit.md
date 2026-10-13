# SG-188 — R3 semantics implemented; one packet premise disproven by SG-181's own log

Immutable audit: base `d7f6ba9906809357659454e6ea594a7aa6dc3c92` → work `e911cdc` (2 product + 3 test files) → evidence `0f62d45` → report `2400f6f`. Forced-command status at end: `result=done id=SG-188 exit=0`; status verb after: `result=reject reason=replay` (correct: receipted). Mapped notes fetch read the receipt; settings envelope-sourced (command). Local pulled `--ff-only` to the exact report HEAD. Scope diff: product `review_tasks.py` (+46/−1: data-required guard + list cursor 422) + `assets.py` (+25/−7: cursor 422 + default ARCHIVED exclusion); tests: new `test_sg188_semantics.py` (303 lines, 5 tests) + coupled updates `test_assets_crud.py` (+29) + `test_search.py` (+13) with CO-38 SG-188/D8 attribution in-comment; 10 worklogs. No migration, no frontend, no config.

Holistic rating: **97/100**, no flag. Contract 0.47.0 echoed verbatim.

## Evidence accepted (re-read in the diff)

- Resolve guard is exactly the D7 boundary: bare (absent/`{}`) + `expiry.manual_entry` → 422 naming the field, task and assertion untouched; any payload still closes (keeps phase2/3 e2e green in the authoritative set). FAIL half shows base closing 200 with data unknown; real-entry path resolves with `resolved_review_task_ids`.
- Cursor 422 on both list surfaces (`is not None` + `decoded is None` → 422); 25-row tied-timestamp walk lossless. Third twin `jobs.py:116` reported, outside ceiling, untouched.
- Default ARCHIVED exclusion in `list_assets` only; facets keep the ARCHIVED bucket (stated boundary, packet-named surface). Coupled expectations narrowed to the decided semantic with explicit-inclusion controls — legitimate, not weakening.
- FAIL half 8F/12P on isolated base (bare-resolve 200, cursor page-1, archived-in-default, coupled D8 expectations); PASS focused 20/20; authoritative 172/172; ruff clean; mypy 41 == 41 (shifts only); health 200/200.
- The (a)1 correction is PROVEN, not asserted: engine already filters `lifecycle.active_clause()` (read in tree, SG-111 comment); 3913381 predates the SG-181 base (ancestor check exit 0); SG-181's own probe log shows the archived asset (`71fb`, the task's `subject_ref`) ABSENT from rows and unresolved_rows post-archive while a different id (`720d`) remains. F-SG181-7's engine half was a misattribution — independently re-derived by the Architect from the committed SG-181 evidence, all three links above. No engine diff manufactured; the vacuous leg declared with its proof. SG-181's frozen report is left untouched (history); this audit is where the correction lives with provenance.
- D8 stands unweakened: its list-surface half was genuinely broken and is genuinely fixed; only the engine half was already satisfied.

No deduction: packet premises verified-or-corrected without Coder fault; nothing breached, mismatched or looped. The already-resolved guard scope (a)2 and the boundary semantics are disclosed for the record: re-resolving an already-resolved data-required task bare now 422s (was idempotent success) — packet-faithful, no covered path broke (172 green).

## Dispositions

| Item | Destination |
|---|---|
| F-SG181-7 engine half | CORRECTED by measurement (this audit) — was misattribution, not a defect; D8 list half unaffected |
| jobs.py:116 cursor twin | Candidate home: SG-189 (guard family) to consider at re-review |
| Non-perishable `unresolved_rows` observation | SG-176/177/178 visibility scope — untouched, per packet |
| SG-176/177/178 grants | Untouched, not consumed (verified: no classification file in the diff) |
| Serve | Normal deploy course, not this slice |

Harness context-size reading unavailable; no conclusion made.
