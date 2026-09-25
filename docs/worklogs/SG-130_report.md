# SG-130 — Legacy PNG thumb backfill: `.jpg` thumbs written through the writer, all served 200

**Dispatch-ID:** SG-130 · **Verdict:** BACKFILLED — G0 did not trip (`PG-IC-08`), writer entry importable in-image, 14 artifacts written by the production writer, all 7 PNG evidences served 200 `image/jpeg` with `ffd8ff` magic, originals 13/13 sha-identical, no 15th artifact.
**First token:** `SG-130`. **Work dir:** `/home/andrei/StorageGenie`. **Origin remote (as on host):** `git@github.com:Andovol/StorageGenie.git`.
**BASE** (`origin/automation` requested; resolved at start): `b70237847452d83175e0ccdfa12c2f9277f6d9d7` · **WORK_HEAD:** `33b89535db0ce7c2544c7170f088cfc2cbde7072` (the work commit holding the script, tests and `SG-130.log`/`SG-130_verify.log`).
**Settings (CO-78, from process arguments / provider metadata — never the identity line):** coder `opencode`; **effort `high`** from process argv pid=1633509 `/proc/1633509/cmdline` = `opencode run --auto --dir /home/andrei/StorageGenie --variant high`; **model `opencode-go/deepseek-v4.1-flash`** from provider metadata (`~/.local/share/opencode/log/opencode.log`: `providerID=opencode-go`, `modelID=deepseek-v4.1-flash`). My argv carries no `--model`, so the model resolves via the Coder default — which is exactly what the metadata records.
**Spend: real $0.000000** (zero metered calls; no path constructs one — a metered call would have been a STOP).
**Contract echo (verbatim):** `> Rule-set version this project records: **0.37.0** (D15 adoption 2026-09-25: checkout `1acd773` tag `contract-v0.37.0` published …)`. **Source path:** `AGENTS.md:4`. Recorded `0.37.0` == published (`1acd773`, D15). **Finding F-SG130-1:** `.rules-cache/` is **ABSENT** at `/home/andrei/StorageGenie/.rules-cache` (persists F-SG129-1) — the echo is grounded on `AGENTS.md`, not a live fetch. Not load-bearing.
**Grant invoked:** `PG-PR-10` — volume `storagegenie_storage_data` at in-container `/data/storage`, D20. Container actions: `exec` for the backfill run only; no restart, no pull, no recreate; the script was piped over stdin (no `docker cp`, no write outside the volume).

## The three criterion questions (PG-SC-09)

- **enumerate — which evidences lack thumbs, and is the set exactly SG-129's aftermath?** YES. Live read-only sqlite shows 13 evidence rows (7 image/png + 1 image/jpeg + 5 text/plain); the live `*_thumb*` set is exactly 2 `.jpg` files, both the JPEG evidence `6050ed6f`. The 7 PNG evidences have no thumb — identical to SG-129's AFTER set, zero delta either direction (`PG-IC-08` did not trip). Non-vacuous: 7 real targets.
- **script — does the backfill reuse the writer's path on fixtures?** YES. `backend/scripts/backfill_legacy_png_thumbs.py` is a thin driver: `_decode_image` (production decode) → `_thumbnail_bytes` (production flatten-to-JPEG, SG-127) → `thumbnail_path` (production resolver), with the writer's own `.tmp`-then-replace atomic discipline. No resizer is re-implemented (`PG-SC-12`). Fixture tests prove RGB and RGBA PNG → `.jpg` with `ffd8ff` magic at 256/512, bounded to the size, skip-existing idempotency, `--overwrite` replacement, and a real-route 200 `image/jpeg`.
- **live — are all 7 PNG evidences served 200 with JPEG magic?** YES. All 14 PNG-evidence×size legs GET 200 `image/jpeg` `ffd8ff`; the served byte lengths equal the on-disk artifact lengths (writer path == reader path). The 2 JPEG-evidence legs stayed 200. Magic quoted per leg (no status-only pass).

## G0 — enumerate + entry check (nothing written until quoted)

Container `storagegenie-backend-1` healthy; volume `storagegenie_storage_data` mounted **RW** at `/data/storage`. The writer entry is importable in the served image: `docker exec … python -c "from app.services.evidence_service import _decode_image, _thumbnail_bytes; from app.storage.local_store import thumbnail_path; from app.config import settings; …"` returned `IMPORT_OK /data/storage [256, 512]`. `settings.thumbnail_sizes == [256, 512]` (matches the packet), so the exact count is 7 × 2 = **14** — re-scoped before writing, never after. The script itself is **not** in the running image (built before this packet), so the live run pipes it over stdin; that is not a BLOCKED condition because the *writer path* is the entry the packet names, and it is present. The BEFORE 404 table (14 PNG legs 404, 2 JPEG legs 200) is quoted in `SG-130_verify.log`.

## G1 — script + fixture proof (fail-then-pass, both runs committed)

The three fixture tests plus the route test were written first and **FAIL** against the absent script (`FileNotFoundError` at collection, pytest exit 2) — the run is quoted in `SG-130_verify.log`. With the script added, the same node ids **PASS**: `5 passed in 0.81s`. Idempotency decision, stated and proved: the script is **skip-existing** by default (a re-run writes nothing and changes no artifact); `--overwrite` rewrites an existing artifact through the same atomic path. `ruff check` clean on both new files; `mypy app` baseline 41/9 unchanged; `git diff --stat -- backend/app/models backend/alembic` **empty**.

## G2 — the live run: exactly the enumerated artifacts, then 200s

One exec run, once: `docker exec -i storagegenie-backend-1 python - --storage-key <7 keys> < backend/scripts/backfill_legacy_png_thumbs.py` printed `BACKFILLED artifacts_written=14 evidences=7 sizes=[256, 512]`, `run_exit=0`, elapsed 1 s. After-listing: **16** `*_thumb*` files = the 2 pre-existing JPEG thumbs + exactly 14 new `.jpg` artifacts; no `.tmp`, no non-`.jpg` thumb, **no 15th artifact**. Volume 15 → 29 files, 5,131,614 → 5,296,705 bytes (+165,091 = the 14 written artifacts' byte sum). Originals **13/13** sha256 identical to the BEFORE capture (`PG-EV-06` spirit). The 200-after table carries status, content-type, byte length and magic per leg; the 14 PNG legs flipped 404 → 200 and the 2 JPEG legs held 200. Any non-200 would have been PARTIAL (STOP-and-report, no second attempt); none occurred.

## Findings / disagreements

- **F-SG130-1** — `.rules-cache/` absent (contract echo grounded on `AGENTS.md:4`). Persists F-SG129-1. Not load-bearing.
- **F-SG130-2 (premise correction, mine)** — the SG-129 report narrative says "13 originals (7 image originals + 6 .txt originals)". The live tree holds **8** image originals (7 PNG + 1 JPEG) and **5** `.txt` originals = 13 files. The arithmetic total (13) is right; the split wording in the standing record is off by one on each side. Not load-bearing for this slice (the 7 PNG targets are correct), reported so the record can be corrected.
- **F-SG130-3 (premise)** — the packet's `PG-PR-10` grant line names the volume and path; I verified the RW mount live rather than trusting it. Matches.
- No app/model/migration/endpoint/config change; no rebuild, recreate, key, DB write, or metered call. `git diff --stat -- backend/app/models backend/alembic` empty; product diff for this slice is the two new files plus the three worklogs.
- The full suite run (`2 failed, 617 passed`) is **not** evidence for this slice: the two reds are in `tests/test_signals.py` (decode/OCR environment class, the known suite reds in STATE.md) and this slice touches no signals code. Called out so a green-looking number is not mistaken for a pass, and so a red is not mistaken for harm.

## Cross-product check (PG-IC-01)

G0 needs listing + image reads + the in-image import; G1 needs the script + fixture tests; G2 needs one exec run + route GETs. Nothing else. No criterion demands a rebuild, a DB touch, a key, or any metered call; no cell collides — stated so the check exists on paper.

## Budget (actual vs bound; units)

| Leg | Actual (wall-clock approx.) | Bound | Note |
|---|---|---|---|
| G0 recon (container/mount/import/DB/listing/BEFORE table) | ~180 s | 120 s ordinary per command | each command returned well under 120 s; no command killed |
| G1 script + tests + FAIL/PASS runs + lint/type | ~180 s | 600 s overall | pytest 0.81 s; ruff/mypy seconds |
| G2 live run + after-listing + 200 table | ~30 s | 120 s ordinary | run elapsed_s=1; 16 GETs |
| G3 docs + commit + notes receipt | ~150 s | 600 s overall | — |

Per-command bounds held; no command was killed or hung. Overall 600 s budget not approached. **Real metered spend $0.000000.**

## Receipt (notes ref)

Executed, in order. The `show` output below is the **executed** output against the **fetched** notes ref (mapped local name, not a bare `FETCH_HEAD`):

```
$ git push origin automation
To github.com:Andovol/StorageGenie.git
   b702378..33b8953  automation -> automation
push-exit=0
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-130 | Report: docs/worklogs/SG-130_report.md | Work-HEAD: 33b89535db0ce7c2544c7170f088cfc2cbde7072" 33b89535db0ce7c2544c7170f088cfc2cbde7072
note-add-exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   2686592..2e45b05  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
note-push-exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg130-verify
ok fetched (1 new refs)
fetch-exit=0
$ git rev-parse refs/notes/sg130-verify
2e45b05c746e3577a51075b1eb9774494a87243b
$ git notes --ref=refs/notes/sg130-verify show 33b89535db0ce7c2544c7170f088cfc2cbde7072
Dispatch-ID: SG-130 | Report: docs/worklogs/SG-130_report.md | Work-HEAD: 33b89535db0ce7c2544c7170f088cfc2cbde7072
show-exit=0
```

The work was pushed to `automation`; no push to `storagegenie-evidence`, no `{{RECEIPT_CMD}}`. The final tip is dual-annotated with the same message (note-anchor inoculation, SG-092 precedent). Final line: `note=yes`.

## UNCLEAR

- **FIRST READ:** whether "the backfill entry IN the served image" meant the *script file* must exist in the image (it does not — the image predates the packet) or the *writer functions* the script drives (they do, import proven). Resolved as the latter: a missing script file is a normal cutover state, not a missing writer; piping it over stdin keeps the "no rebuild" constraint. Stated because a strict file-presence reading would have produced a false BLOCKED.
- **DURING EXECUTION:** whether the pre-existing 2 `.jpg` thumbs for the JPEG evidence should be left untouched (they were) or regenerated alongside; the packet's scope is the 7 PNG evidences, so they were left and only reported.
- **REMAINING:** none blocking. Residual: the script and tests are committed but only the *writer path* is packaged in the running image until the next rebuild — the tool ships in-tree for the next image, and the live artifacts are already served. No deletion/cleanup of the backfilled artifacts is needed or performed.
