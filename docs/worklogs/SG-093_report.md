# SG-093 report — Taxonomy T1: vendored Google data + pure resolver + bucket map

**Dispatch-ID:** SG-093 · **Coder:** opencode · **effort:** high · **model:** unknown (CLI default, no `--model` in argv)
**Work dir:** `/home/andrei/StorageGenie` · **origin remote:** `git@github.com:Andovol/StorageGenie.git`
**BASE** (`origin/automation` resolved at start): `dbe0c21624db56b83d8c5c545fc75d9d41278d14`
**WORK_HEAD:** `9a7a0d47a7777b57d849c0c1f8b907afd1905d24` (the pre-note work commit carrying this report;
the Receipt paste is this later docs-only commit).
**Spend:** REAL metered **$0.000000** (one free, unmetered taxonomy download GET; zero provider calls).

**Role guard:** Coder, never Architect. No dispatch verb was run for any ID; no unit was started or
polled by me. This slice is the slice that was dispatched TO me.

## Model and effort (from process arguments — not from an identity line)

- Own argv, read from the launching process (`/proc/1780906/cmdline`):
  `opencode run --auto --dir /home/andrei/StorageGenie --variant high <packet text on argv>`
  → **effort `high`** (the `--variant high` token).
- No `--model` token in argv. Per the packet the model is the omitted CLI default and is not determinable
  from process arguments here, so **model = `unknown` (CLI default)** — written as unknown, never guessed
  (`CO-78`). Source: own argv.

## Contract echo + source path (no drift)

- Packet-recorded, source `docs/packets/SG-093-taxonomy-data-resolver.md:7`:
  `Contract: recorded 0.30.0 == published (c9c9ba3; D125 adoption); echo verbatim + source path.`
- Live contract line verbatim, source `/home/andrei/storagegenie-contract/CODER.md:3`:
  `**Contract version: 0.30.0** — **echo this line verbatim in your receipt.** It is the only proof that you`
- Live `VERSION` = `0.30.0`; contract repo HEAD = `c9c9ba3ee3715d102b55c740f4f2107344e7de3a` "Contract
  payload 0.30.0"; `RULES.sha256` = `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46`
  (byte-equal to the AGENTS.md header payload hash). **Recorded == published == live; no drift.**

## (a) Issues / deviations / surprises

1. **Plan id/path typo (non-blocking, reported not bent).** Plan Task 1 test 4
   (`docs/superpowers/plans/2026-09-21-google-taxonomy.md:53`) calls
   `bucket_for("414", "Food, Beverages & Tobacco > Beverages")`, but in the vendored file id **414** is
   `Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer` and the `Beverages` node is id
   **413**. `bucket_for` is path-first, so the pin passes and is meaningful; the plan's literal call was
   kept. Reported as a finding, not silently corrected.
2. **Pharma exception enumeration.** Under `Health & Beauty` the only pharma row is the single leaf
   `518 - Health & Beauty > Health Care > Medicine & Drugs` (verified: no descendants in the vendored
   file). It is the one enumerated pharma prefix; the rest of `Health & Beauty` defaults to
   `cosmetics_personal_care`. Vendored rows quoted in the module comment and in this report.
3. **`.gitignore` path.** `.gitignore` ignores `backend/data/`, not `backend/app/data/`; the vendored
   target is trackable (`git check-ignore` exit 1 = not ignored). No scratch copy committed anywhere;
   `find` for `*2021-09-21*` returns exactly the one vendored file.
4. **Scoring formula was a design call.** The spec fixes exact-match-at-1.0 + gates but not the token-set
   formula. Chosen: exact normalized full-path short-circuit; otherwise Jaccard over the token sets
   (`[a-z0-9]+`), top-`TOP_K`, accept iff `score ≥ 0.6` and `margin ≥ 0.15`. Below gates → `unclear` with
   alternatives and **no** mapped id; `None`/blank → `uncategorized`.
5. **Non-vacuity proven, not asserted.** Two extra pins monkeypatch the mechanism off: removing the
   accept gates flips an `unclear` partial overlap to `resolved`, and dropping the pharma prefix flips
   `medicine_pharma` to the Health & Beauty default. No pin can pass with its mechanism disabled.

## (b) Actions

- Created `backend/app/data/google_taxonomy/2021-09-21.txt` (one download GET; byte-identical vendored
  data; sha256 `30039729880ec5ac4851de088ad228a6898aa253f0de5d5ebea5bb1437478fce`).
- Created `backend/app/services/google_taxonomy.py` (pure offline resolver + bucket map; no network, no
  clock, reads only the vendored file).
- Created `backend/tests/test_google_taxonomy.py` (17 pins; 5 plan cases + gates/map/non-vacuity/source).
- Created `docs/worklogs/SG-093.log`, `SG-093_report.md`, `SG-093_verify.log`.
- No schema change, no prompt change, no candidates wiring, no migration, no container action, no deploy.
- Highest-impact action: the resolver + its fail-then-pass evidence.

## (c) Verification

G1 — vendored file, three ways (raw in `SG-093_verify.log`):
```
$ head -n1 backend/app/data/google_taxonomy/2021-09-21.txt
# Google_Product_Taxonomy_Version: 2021-09-21
$ wc -c backend/app/data/google_taxonomy/2021-09-21.txt
482896 backend/app/data/google_taxonomy/2021-09-21.txt
$ wc -l backend/app/data/google_taxonomy/2021-09-21.txt
5596 backend/app/data/google_taxonomy/2021-09-21.txt
$ sha256sum backend/app/data/google_taxonomy/2021-09-21.txt
30039729880ec5ac4851de088ad228a6898aa253f0de5d5ebea5bb1437478fce  backend/app/data/google_taxonomy/2021-09-21.txt
```
All three match the packet's hypothesis (version line / 482896 B / 5596 lines). No hand-edit.

G2 — fail-then-pass (`PG-EV-09`), both raw in `SG-093_verify.log`:
```
PRE-RUN (module absent): python -m pytest tests/test_google_taxonomy.py -v
E   ImportError: cannot import name 'google_taxonomy' from 'app.services'
1 error in 0.07s            (0 collected)
POST-RUN (module present): 17 passed in 0.12s
```

Gates:
```
ruff check .            -> All checks passed!                      (rc 0)
mypy app                -> 41 errors with module, 41 baseline,     (delta 0; google_taxonomy.py has none)
                           error list diff empty
full suite (pytest -q)  -> 2 failed, 445 passed in 19.94s
    failed: test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier
            test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
    both are pre-existing ENV reds (pyzbar/libzbar and pytesseract not installed), STASH-PROVED: the pair
    fails identically on a clean origin/automation tree with this slice's files stashed (raw in verify log).
secret gate             -> rg 'api[_-]?key|OPENCODE_API_KEY|Bearer|private key|BEGIN .*PRIVATE' = 0 matches.
```

Non-vacuity: the accept-gate and pharma-prefix pins are load-bearing (above, finding 5); the source pin
greps the module source itself and asserts no `httpx`/`urllib`/`socket`/`requests`/`aiohttp` import.

## Acceptance criteria (`PG-SC-09`)

- Vendored file byte-verified all three ways, values quoted — **done** (line + 482896 B + 5596 lines).
- 5 plan cases fail-pre (module absent) and pass-post, both committed raw; module source has no network
  import — **done** (pre `ImportError`, post 17 passed; source pin green).
- Gates green as in G2; nothing outside the ceiling; no vacuous pass — **done** (ruff clean, mypy delta 0,
  suite green modulo 2 stash-proved env reds, secret gate 0; diff is exactly the 3 allowed paths +
  `docs/worklogs`).

## Receipt

Push work to `automation`; worktree clean. No push to `storagegenie-evidence`; no `{{RECEIPT_CMD}}`.
The note is added on the WORK_HEAD, pushed to `refs/notes/storagegenie-coder-reports`, then fetched into
a mapped local ref and shown verbatim. The raw commands and the pasted `show` output are appended by this
follow-up docs-only commit.

WORK_HEAD (pre-note work commit) = `9a7a0d47a7777b57d849c0c1f8b907afd1905d24`.

Commands executed (raw):

```
$ git notes --ref=refs/notes/storagegenie-coder-reports show 9a7a0d47a7777b57d849c0c1f8b907afd1905d24
error: no note found for object 9a7a0d47a7777b57d849c0c1f8b907afd1905d24.
existing_exit=1
$ git notes --ref=refs/notes/storagegenie-coder-reports add -m "Dispatch-ID: SG-093 | Report: docs/worklogs/SG-093_report.md | Work-HEAD: 9a7a0d47a7777b57d849c0c1f8b907afd1905d24" 9a7a0d47a7777b57d849c0c1f8b907afd1905d24
add_exit=0
$ git push origin refs/notes/storagegenie-coder-reports
To github.com:Andovol/StorageGenie.git
   18737bb..65c29c8  refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports
push_notes_exit=0
$ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/storagegenie-coder-reports-sg093-verify
From github.com:Andovol/StorageGenie
 * [new ref]         refs/notes/storagegenie-coder-reports -> refs/notes/storagegenie-coder-reports-sg093-verify
fetch_exit=0
$ git rev-parse refs/notes/storagegenie-coder-reports-sg093-verify
65c29c8e40f7db1397e1572f38107666fe0f3f5e
$ git notes --ref=refs/notes/storagegenie-coder-reports-sg093-verify show 9a7a0d47a7777b57d849c0c1f8b907afd1905d24
```

Pasted `show` output (verbatim, from the FETCHED mapped ref
`refs/notes/storagegenie-coder-reports-sg093-verify` = `65c29c8e40f7db1397e1572f38107666fe0f3f5e`):

```
Dispatch-ID: SG-093 | Report: docs/worklogs/SG-093_report.md | Work-HEAD: 9a7a0d47a7777b57d849c0c1f8b907afd1905d24
```

No existing note was found before adding (`existing_exit=1`), so this was not an existing-note refusal.
The final tip (this docs-only paste commit) is dual-annotated with the same note body so the engine's
`note_anchor=END_HEAD` readback resolves (SG-092 note-anchor inoculation precedent).

note=yes

## UNCLEAR (FIRST READ)

Whether the plan's Task 1 id/path typo (id 414 vs the `Beverages` node 413) is meant to be corrected by
the Coder or carried as written; I carried the file's real id and kept the plan's literal test call.

## UNCLEAR (DURING EXECUTION)

Whether scoring should be Jaccard (chosen) or a containment/coverage score; the spec fixes exact-match,
gates and top-k but not the exact token-set formula, so the formula was a design call.

## UNCLEAR (REMAINING)

Whether the vendored data file must later be added to the Docker build context / hatch package data so
T2/T3 see it at runtime; that is outside T1's ceiling and was not touched.
