# SG-219 audit — D-27 pilot: render 3 FAILED on provider content policy (RECITATION 400, unbilled); render 4 unattempted, rated 98

Immutable audit: base `da63d45` → G1 `367baa8` (driver + plan, no send) → work `299f48c` (BLOCKED: render 3 failed) → report `0da65eb` → receipt `f1d04d4` (transcript + mapped read-back; Work-HEAD 0da65eb). Local `--ff-only` to the exact tip (`f1d04d4` == origin/automation at pull); tree clean. Trigger exit 0; status verb `result=done id=SG-219 exit=0`. Receipt note `Dispatch-ID: SG-219 | Report: docs/worklogs/SG-219_report.md` IS on the remote — own read-back finds `0da65eb` via `git log --notes`, and the transcript shows notes + branch pushes `rc=0` with mapped-fetch read-back. Per `DISPATCH.md` §2: receipt present → NOT failed. No runner misfire — fourth clean trigger in a row.

## Verified (parsed from the committed artifacts, not the report's §(c))

- **FAILED/STOPPED, correctly (independently read):** `SG-219_render3_result.json` = status `failed`, `status_code` 400, `evidence_id` null, ledger `01a15fe8-aa48-…`, `usage` null. The ledger row carries `cost` NULL, `error_state=http_status:400`; its `output_payload.response_body` is the 400 body — re-grepped by this audit: `RECITATION` (finish_reason + block_reason) and "flagged for copyrighted or trademarked material", zero `b64_json` occurrences (no image bytes anywhere). Unbilled on both accountings (no usage object).
- **STOP discipline:** one POST total (render 3, CEAFĂ); render 4 (Costiță-2) not attempted. The packet's stop language supported both readings; the Coder took the conservative one (stop the slice, ship the body) and flagged the fork explicitly instead of spending a second render past a content-policy signal — the safer behavior, and the re-dispatch call is the Architect's, not an in-slice interpretation. No deduction.
- **L2 retry (legitimate, spent):** the pre-send `KeyError: 'authority'` (F-SG219-1) crashed before any POST and wrote no DB row; root-cause fix (return the authority object, three call sites), attempt preserved verbatim. One retry, root-cause only, lane tooling — inside the L2 cap.
- **Money:** authority cap 1.36224 (pilot remainder tightest); projection 0.86383713 `proceed`; synthetic over-cap + no-authority refusals proven. Actual $0 both accountings. Pilot stays 2/10 billed (the 400 added only a null-cost row: unknown-cost calls 4→5, disclosed as tightening future guards). Caps held.
- **DB post-state:** evidence 20→20, provider_call 31→32 (the 400 row), audit_event 93→93, known sum unchanged. No UPDATE/DELETE.
- **Scope:** 25 files — driver `backend/scripts/sg219_render.py` + `docs/worklogs/SG-219_*`; zero product/test bytes, no migration, no restart. Contract 0.50.0 live proof. Elapsed 605 s vs ≈600 s (at the bound, not over in any binding sense; no command over 60 s).
- **Secrets:** literal gate final pass exit 1 EMPTY (first exit-2 self-read disclosed, corrected by temp-file rename); live-value key gate `matching_bytes=0` (1224 files).

## Rating

**Holistic: 98/100, no flag.** A provider content-policy wall is evidence, not failure, and the slice treated it exactly that way: stopped, preserved the body verbatim, counted the pilot honestly (2/10, not 4), spent the one L2 retry on the true root cause before any money moved, and handed the re-dispatch fork upward instead of interpreting it away. `deduction_attribution`: empty (nothing deducted). `slowest_waste`: `none` — every CO-79 phase output was used (enumeration, plan, guard, the failed attempt log, the 400 leg, post-state, gates). Guards: PG-EV-02/03/05/06/07/09/14; PG-SC-03/05/09; PG-IC-01/07/08/09; PG-PR-01/03/10.

## Dispositions

| Item | Destination |
|---|---|
| Render 3 FAILED (RECITATION on CEAFĂ's trademarked label) | Finding, not defect — CEAFĂ parked unless a content-policy decision re-opens it (prompt/asset handling is a future fork, not in-slice work) |
| Render 4 unattempted (Costiță-2, pilot-unused) | Re-dispatch SG-220 under D-27 this turn — the block was asset-specific, the path is proven |
| Null-cost row (unknown 4→5) | Automatic — tightens future guard projections by one worst case |
| Pre-send KeyError | Fixed in the driver, attempt preserved; SG-220's packet tells its driver to inherit the fixed handoff |
| Runner clean | Nothing filed — ISS-4 stays at 18 |

Harness context-size reading unavailable; no conclusion made.
