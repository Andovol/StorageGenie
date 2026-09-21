# SG-087 — privacy-controls audit: redaction + identifiers-only on every provider path, retention stated

**Dispatch-ID:** SG-087
**Coder / effort:** `opencode` (coder from packet); effort **medium** (process argv: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**MODEL:** **unknown** — argv carries no `--model` and no provider metadata was surfaced to the Coder in-process; reported per `CO-78`/packet rather than guessed from a system-prompt identity line
**Host / workdir:** `/home/andrei/StorageGenie` · branch `automation` · remote `git@github.com:Andovol/StorageGenie.git`
**BASE (start HEAD):** `1dceafbb613b6f80d4a5e9082ac4998b7975ca05` (packet requested `origin/automation`; this is the commit it resolved to — two fields, never one)
**WORK_HEAD:** recorded in the notes-ref receipt below (slice tip before the docs-only paste commit)
**Spend:** **$0.000000 actual** — zero provider calls; no metered call exists on any path in this slice (`PG-IC-04` not firing)
**Contract:** recorded `0.28.2` == published `0.28.2`; source path `/home/andrei/storagegenie-contract/VERSION`; checkout `b495b59b3426af66772a87939473ac558f8f72d2`
**Authoring date metadata:** 2026-09-21 (not a gate)
**Live clock:** recon 2026-09-21T17:2xZ; final capture 2026-09-21T17:35Z

## Verdict

**No hole found.** The audit's full sender enumeration is the witness: exactly one HTTP sender exists in `app/` (`opencode_go.py:252`), every image-bearing path redacts through the ONE shared `redact_image`, provider payloads and the ledger carry hashes/ids only, and no retention mechanism exists to mis-state. Everything is committed (new test + these logs); nothing in the slice is a report-only claim.

## G0 — what CAN leave the machine

Criterion: every call site that hands bytes to a provider seam or an HTTP sender.

- **HTTP senders (full static scan over `backend/app`, criterion-driven):** exactly one — `services/providers/opencode_go.py:252 client.post(self._base_url + CHAT_PATH, ...)`. All other `.post(` hits are FastAPI `@router.post` decorators. `_http_client_files()` (scan for `import httpx|requests|urllib|aiohttp|http.client|socket.socket|urlopen(`) == `{"services/providers/opencode_go.py": ["import httpx"]}`. **Cleared.**
- **`redact_image` call sites:** exactly two — `reader.py:402` (pipeline) and `opencode_go.py:299` (direct adapter). The packet's expectation matches exactly.
- **Image-bearing prompt services:** `analytics/service.py:536` and `planning/service.py:423` each build a generated **1x1 blank** PNG carrier (`_carrier_png()`) and send it through the vision op `extract_items`; their prompt content is text only. **`chat/service.py:344`** is the only truly image-free path (`extract_text`). *(Finding F-SG087-1: "text-only" is true of the prompt content, not of the wire — a blank carrier is still sent. Not a hole.)*
- **EXIF hotspot:** `signals.py:251` (`image.getexif()`) and `signals.py:278` (observation write) read only the DateTime tags `0x9003/0x9004/0x0132`, gated by `settings.exif_timestamps_enabled` (default `False`); GPS tag `0x8825` is never read. Observations are consumed only by `expiry_tracker` (ocr/barcode), `dedup` (phash/barcode) and `candidates` (barcode) — never by a provider payload. Traced end to end in G1.

## G1 — is every outbound byte clean

- **Real redactor, parsed proof:** the test imports the REAL `app.services.providers.redaction.redact_image` (no re-implementation, `PG-SC-12`). An EXIF+GPS-laden JPEG built in-test (`dict(exif) == {34853: 48, 271: 'TestMake'}`, GPS IFD `{1:'N',2:(51.0,30.0,0.0),3:'E',4:(0.0,7.0,0.0)}`) becomes PNG (`\x89PNG\r\n\x1a\n`) with `dict(exif) == {}`, `get_ifd(0x8825) == {}`, and **pixels preserved**: `(size, mode)` `(32, 32, 'RGB')` identical before/after. No binary fixture committed.
- **Seam proofs (`PG-SC-12`):** the reader pipeline (`job_service.run_job` → real reader) hands the provider a PNG with empty parsed EXIF, and each ledger row's `image_sha256` equals `sha256()` of the very bytes the provider received. The direct adapter proof overrides only `_post` (transport), decodes the real outgoing `data:image/png;base64,` image part, and asserts tag-free + size-preserving + no `OPENCODE_API_KEY`/`Bearer`/`sk-`/`TestMake`.
- **Ledger:** exercised rows carry `output_payload` with no `exif`/`gps`/`TestMake`; `input_hashes` are sha256 only.
- **Signals trace:** with `exif_timestamps_enabled=True`, an image carrying `DateTimeOriginal` produces an `exif` observation `{"tag": "DateTimeOriginal", "timestamp": "2021:07:04 10:20:30"}` with no GPS — and that exact timestamp/`TestMake` appears in **no** provider prompt and **no** ledger payload on the exercised path.
- **Seen-to-fail (`PG-EV-01`):** the committed negative control asserts the raw input carries EXIF+GPS and that the same tag-free assertion raises; the literal FAIL-PRE run (throwaway probe reusing the committed builder/assertion) fails with `AssertionError: EXIF survives redaction: {34853: 48, 271: 'TestMake'}` — quoted in `SG-087_verify.log`.

## G2 — do keys/PII stay home

- **Key custody:** `.env` probed presence/count only — `grep -c '^OPENCODE_API_KEY=' .env` → `1`, mode `600`; the value is never printed, logged, or committed. The only in-app reads are `opencode_go.py:242` (`os.environ`) and `config.py:29`; the key enters only the `Authorization: Bearer` header at `:249`. The wire builders accept no key parameter and render no `OPENCODE_API_KEY`/`Bearer`/`sk-`/`Authorization`; payloads carry `input_hashes` (sha256) and ids.
- **Enrich-absence:** no `jina`/`websearch`/`web_search` code exists; the G0 sender enumeration proves no web sender exists to receive photo/GPS bytes.
- **Consent:** `consent=false` binds zero provider calls on all four service entry points (reader `run_job`, analytics `run_insights`, planning `run_planning`, chat `respond`), proved with an exploding provider whose any-invocation raises — each returns `skipped/consent_disabled`, `probe.calls == []`, and `ProviderCall.count() == 0`.

## G3 — is the proof committed and the retention record unambiguous

- **New test:** `backend/tests/test_privacy_audit.py` (11 tests, temp fixtures only). **FAIL-then-PASS raw, both committed** (`PG-EV-09`): the pre-run is the unredacted input against the committed assertion (G1 seen-to-fail doubles as the pre-change run because this slice changes no code — composition stated explicitly).
- **Retention (measured + ADR-007, no policy invented):** kept — evidence originals (immutable, `settings.storage_root`), `provider_call` ledger rows (full `output_payload`, `input_hashes` = sha256 of the redacted bytes, cost/usage/latency/error_state), observations/assertions/guardrail events; where — local filesystem + local SQLite (`data/db/storagegenie.db`); redacted transients — memory only, never persisted; **how long — no TTL: no expiry/cleanup/purge/prune/scheduler exists in code → retained indefinitely; deletion is manual.** ADR-007:14 quotes the ledger payload retention, ADR-007:33 defers ledger-row retention to the production-datastore slice. **Home decided: worklog-only** (ADR-007 is already the policy home; `{{PROD_DB}}` is "not applicable", Phase 0 local SQLite). Stated, not silent.
- **Gates:** suite `2 failed, 376 passed` (the 2 reds are the base-proved decoder env reds, re-verified on bare BASE — `2 failed, 365 passed` — not inherited); `ruff check .` → `All checks passed!`; `mypy app` → `Found 41 errors in 9 files` (delta **0**: mypy checks `app/` only and this slice changes no `app/` file; note the pre-existing drift from SG-028's 40-in-9); secret grep (`api_key|OPENCODE_API_KEY|Bearer|[Tt]oken`) → only identifier/param-name/assertion hits, **0 real secret shapes**; `PG-SC-11` grep → **none** over any privacy/redaction path (raw hits listed with verdicts).

## Acceptance criteria — the question each answers (`PG-SC-09`)

| Criterion | Question it answers | Verdict |
|---|---|---|
| G0 enumeration complete, senders cleared/flagged, hotspot traced | What CAN leave the machine? | green: 1 sender, 2 redact sites, EXIF hotspot traced end to end |
| Redacted output tag-free + pixels preserved + seam + ledger + seen-to-fail | Is every outbound byte clean? | green: parsed EXIF empty, `(32,32,RGB)` preserved, both seams + ledger hash, failure quoted |
| Keys presence/count only; identifiers-only; Enrich absence; consent per path | Do keys/PII stay home? | green: count=1, 0 literals, no web sender, 4 paths refuse pre-call |
| Retention stated + home decided; FAIL-then-PASS committed; suite/ruff/mypy/secrets | Is the proof committed and the retention record unambiguous? | green: worklog-only home, both runs raw, gates quoted |
| G4 logs + receipt | Is the evidence committed, not merely reported? | green: see Receipt |

No criterion passed vacuously: the tag gate was fed EXIF and failed; the seam assertions read the real captured payload bytes (not a re-implementation); the sender scan is exhaustive over `backend/app`; the consent probe raises on any call; the suite is non-empty and the grep lists its hits rather than assuming none.

## Findings / disagreements

- **F-SG087-1 — "text-only" is about prompt content, not the wire.** Analytics and planning still send a generated 1x1 **blank PNG carrier** through the vision op `extract_items` (the adapter surface requires image bytes); only chat is image-free. The carrier is blank and is redacted by the adapter like any upload. Not a hole; reported as a premise nuance.
- **F-SG087-2 — `.rules-cache/` absent** in this worktree; the contract source is `/home/andrei/storagegenie-contract/` (same as SG-086 F-SG086-2). Contract echo still verified recorded==published.
- **F-SG087-3 — mypy is 41-in-9, not SG-028's 40-in-9.** Pre-existing drift (this slice changes no `app/` file; delta 0).
- No disagreement with the packet's authority or scope; the audit-only ceiling was honoured on every path.

## Guards invoked (for the rating row)

`PG-EV-01` (unredacted-input gate seen-to-fail, quoted) · `PG-EV-02` (each artifact verified at its path) · `PG-EV-05` (properties stated) · `PG-EV-09` (FAIL-PRE + PASS-POST both committed) · `PG-SC-03` (G0 enumeration complete; a HOLE stops — none found; negative case stated) · `PG-SC-05` · `PG-SC-09` (questions above) · `PG-SC-11` (grep + verdicts; empty over privacy paths) · `PG-SC-12` (real `redact_image` imported; assertions on the real seam/ledger bytes, no stand-in) · `PG-IC-01` (reads/suite/static enumeration only; no container image pull/run; network only for pushes) · `PG-IC-03` (hole-STOP precedence stated; none fired) · `PG-IC-07` (live clock) · `PG-IC-09` · `PG-PR-03` (no denied operation encountered) · `PG-PR-04` (NOTHING live: audit only; no deploy/restart; proof scoped to offline tests + static enumeration) · `PG-IC-04` stated not firing ($0, no bound to multiply).

## Receipt

Work pushed to `automation`, worktree clean (`CO-55`). No push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. Note added on the work HEAD and the notes ref pushed, then verified against the **fetched** ref mapped to a local name:

```
git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-087 | Report: docs/worklogs/SG-087_report.md | Work-HEAD: <hash>" <WORK_HEAD>
git push origin refs/notes/storagegenie-coder-reports
git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-remote
git notes --ref=refs/notes/storagegenie-coder-reports-remote show <WORK_HEAD>
```

The verbatim executed `show` output is pasted in the follow-up docs-only commit (M20-corrected block pattern, as SG-085/SG-086 did); the final committed report carries the paste.

## UNCLEAR

- **FIRST READ:** whether the analytics/planning "text-only" premise meant no image part at all — measured, they still send a generated 1x1 blank carrier through `extract_items`; only chat is image-free.
- **DURING EXECUTION:** whether "FAIL-then-PASS" required a committed failing state — since this slice changes no code, the FAIL-PRE is the unredacted input against the committed assertion, and the committed negative-control test captures that failure permanently.
- **REMAINING:** ledger-row retention for the eventual production datastore (ADR-007 defers it there); no TTL exists today, so the statement here is measured, not invented.
