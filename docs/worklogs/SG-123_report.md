BLOCKED: G1's move cannot be completed inside the ceiling — relocating the 5 loose
`backend/eval/corpus/sg026_*.json` under `corpus/sg026/` breaks
`tests/test_extraction_contract.py::test_corpus_integrity` (it globs the corpus ROOT for exactly 5 JSON
files), and that suite file is outside this slice's write ceiling ("suite files beyond the two lines is
a STOP"). A second, independent shape mismatch also blocks the packet's FROZEN definition: the fixtures
are pre-manifest v1 smoke shape (no `category`, no `image`), so the real
`run.py --corpus sg026 --check-only` prints `CORPUS INTEGRITY FAILURE` and exits 1 — it cannot report
"integrity OK" as G1 and the acceptance criteria require. All move/manifest/frozen-record/test edits
were reverted to a clean BASE; finding + raw evidence below.

---

# SG-123 — freeze sg026 via manifest: BLOCKED

Dispatch-ID: SG-123 · Coder: opencode · Effort: high (`--variant high`, from the trigger per
D302/D120) · Model: `deepseek-v4.1-flash` (provider metadata banner `> build · deepseek-v4.1-flash`
in `output/dispatch/SG-123.log`; no `--model` on argv = the contract-legal omitted-model subset. A
launcher env var `MODEL=opencode-go/muse-spark-1.3-contributor` was present in the dispatch
environment but is **not** what the provider reported ran; the provider banner is quoted as provider
metadata, never a system-prompt identity line) · Contract: 0.37.0

BASE REF: `origin/automation` — BASE COMMIT (resolved): `0b183d52c6cad353b608141f1c7a0912f71e3a93`
(start HEAD; worktree clean at start; `git status --porcelain` empty).

WORK_HEAD: the commit carrying this report + worklog + verify log (resolved hash published in the
receipt note below).

Work dir: `/home/andrei/StorageGenie` · Remote: `git@github.com:Andovol/StorageGenie.git` (as on host).

Spend: `$0.000000` real vs `$0` bound · Network: none · DB: none · Restart: none · Container: none ·
No live leg of any kind.

**Verdict: BLOCKED** (both the fixture-shape and the root-glob shape mismatch). Worktree clean.
Nothing shipped; no hunk outside the ceiling.

## Contract echo (verbatim, source path)

- `/home/andrei/storagegenie-contract/VERSION` reads `0.37.0`.
- Checkout HEAD `1acd7730e5fa6de5b7403aacce71207e9946461d` (== packet's `1acd773`, D15 adoption).
- `RULES.md` sha256 `18de7fd7b3546bd7624b3a7b59a78bd629752816cd7fa8f1af6113d1bafc8d46` == payload
  `RULES.sha256` (installed == payload; clean).
- Packet records contract `0.37.0` == published. `.rules-cache/` is absent on this host (standing,
  SG-121 F-SG121-1); the contract checkout above is the source path used.

## G0 — premises (verify each)

- Corpus root holds exactly `sg029/` + `sg049/` + `sg079/` + the 5 loose `sg026_*.json` — **MATCHES**
  the packet (no sixth entry). Confirmed by `ls -la backend/eval/corpus/`.
- Selector shape read, never inherited: `run.py:60-66` (`available_corpora` = parent names of
  `*/manifest.json`; `manifest_path` = `CORPUS_DIR / corpus / manifest.json`), `:82-84`
  (fixtures resolve under `manifest["base_dir"]`), `:119-139` (`check_manifest`). sg049 manifest key
  shape (`corpus`/`description`/`base_dir`/`count`/`fixtures`) confirmed — used as template.
- Test pins `:177` and `:236` confirmed present.
- **DIFFERENCE (finding F-SG123-1):** the 5 sg026 fixtures are the pre-manifest **v1 smoke shape** —
  keys `id`, `class`, `note`, `provider_output`, `ground_truth`; **no `category`, no `image`**.
  `run.py:89` requires both. Raw gate output quoted in `SG-123_verify.log`.

## G1 — move + manifest (mechanics worked, then reverted)

- `git mv` of all 5 files into `backend/eval/corpus/sg026/` preserved history as **5 renames**
  (`R` entries in `git status`); filenames byte-identical.
- Wrote `corpus/sg026/manifest.json` in the sg049 key shape (`corpus: sg026`, `base_dir: sg026`,
  `count: 5`, the 5 filenames, honest description). `check_manifest(sg026)` returned `[]` — count ==
  listed == disk, ids unique; `available_corpora()` then returned `['sg026', 'sg029', 'sg049', 'sg079']`;
  `DEFAULT_CORPUS` stayed `sg029` and `load_manifest()['corpus'] == 'sg029'`.
- Real `run.py --corpus sg026 --check-only` **FAILED** (finding F-SG123-1): `missing key 'category'`,
  `missing key 'image'` for all 5; exit 1. The packet's G1 premise "`--corpus sg026` integrity OK with
  count 5" is therefore **falsified by the real runner**.

## G2 — selector test flip (worked) + suite (finding F-SG123-2)

- Edited `:177` → `SELECTED_CORPORA = ("sg029", "sg049", "sg079", "sg026")` and `:236` →
  `assert "sg026" in known, "manifest -> selectable (SG-123 freeze)"`.
- **FAIL-pre** (updated test, BEFORE the move): `2 failed, 12 passed` — `sg026 must be selectable`
  and `FileNotFoundError: baseline_sg026_frozen.md` (quoted).
- **PASS-post** (AFTER the move + manifest + frozen record): `14 passed` (quoted). The flip genuinely
  rides the data change; not vacuous.
- **Full suite WITH the move:** `3 failed, 593 passed` (32.09s of a 600s bound). The **new** red is
  `test_extraction_contract.py::test_corpus_integrity` (`assert len(fixtures) == 5`; got `0` because
  the fixtures left the corpus root). **F-SG123-2.**
- **Full suite on clean BASE (no move):** `2 failed, 593 passed` — the 2 `test_signals.py` reds
  (`test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`,
  `test_ocr_has_text_boxes_and_mean_confidence`) are **base-proved** (OCR/barcode environment), and
  `test_corpus_integrity` is **green** on base. Therefore the move caused **exactly one new red**, and
  repairing it requires editing `tests/test_extraction_contract.py` — a suite file beyond the two
  allowed lines → **STOP**.

### Why this is a STOP, not a fix

The scope ceiling is explicit: "Any other hunk — scoring code, history baselines, **suite files beyond
the two lines**, product code — is a STOP." `test_corpus_integrity` lives in an off-ceiling suite
file, so it cannot be updated here; without updating it the move leaves `automation` red. Per the
packet's own BLOCKED clause ("a shape mismatch stopped the move"), the move was reverted.

## Revert + empty diffs

All move/manifest/frozen-record/test edits reverted; `git status --porcelain` empty before the
worklogs. `run.py`, the scorer `app/services/providers/schemas.py`, the 5 history baselines, and the
whole corpus dir all show empty diffs against BASE (quoted in `SG-123_verify.log`). Scoring code zero
hunks — confirmed.

## Findings (loud)

- **F-SG123-1 (BLOCKING)** — fixture shape: the 5 sg026 fixtures carry no `category` and no `image`,
  so the real `run.py` integrity gate cannot pass and FROZEN's "integrity OK" is unreachable in-ceiling.
  (Same image-less asymmetry already documented for sg049/sg079, one field worse — `category` also
  absent.)
- **F-SG123-2 (BLOCKING)** — `tests/test_extraction_contract.py:376-385` depends on the 5 loose
  fixtures sitting at the corpus ROOT (`CORPUS_DIR.glob("*.json") == 5`). The move breaks it, and the
  file is off-ceiling → the freeze cannot land without a ceiling that includes it.
- **F-SG123-3 (minor)** — the packet's BLOCKED clause says "a shape mismatch stopped the move", but
  F-SG123-2 is only visible after staging the move (the runner's gate and the fallback test do not
  reveal it by reading). I reverted to honor the clause.
- **F-SG123-4 (minor, outside scope)** — `STATE.md:2` still reads contract `0.36.0` while
  AGENTS/packet/checkout read `0.37.0` (carried from SG-121 F-SG121-3; Architect's file).

## Recommendation (not implemented)

A follow-up packet that adds `tests/test_extraction_contract.py` (specifically `test_corpus_integrity`)
to the ceiling — candidate fix: point its glob at `CORPUS_DIR / "sg026"` (or fold that check into the
`test_eval_corpus.py` selector test, which now owns the corpus manifest authority) — then SG-123's
move + manifest + frozen record can be applied in one shot. If the packet also wants `run.py`'s
`--corpus sg026` integrity to be OK, the fixtures additionally need a `category` (and either an
`image` asset or a scoring-only bypass in the gate), which is a separate authored-data decision.

## Vacuous-pass statement

Nothing is reported as a pass. The selector flip genuinely failed-then-passed (both raw runs quoted),
but the FROZEN verdict is **not** claimable: the suite is not green under the move, and the `run.py`
integrity proof is impossible for this fixture shape. No hunk was shipped.

## Receipt (note on `refs/notes/storagegenie-coder-reports`)

Work committed and pushed to `automation`, worktree clean (`CO-55`). No push to
`storagegenie-evidence`; no `{{RECEIPT_CMD}}` (per this packet's M20-corrected block). The note was
added on WORK_HEAD, the notes ref pushed, the refspec fetched into a MAPPED local name, and the
`git notes --ref=… show <WORK_HEAD>` output is pasted verbatim in the follow-up docs commit
(`SG-123 docs: paste receipt show from mapped ref`) and in the delivery message — a receipt subsection
with no pasted `show` output means the step was not executed. Existing-note refusal is a STOP. Final
line: `note=yes`.

## UNCLEAR

- **FIRST READ:** whether the sg026 fixtures carried the SG-029 image-corpus shape (they do not — no
  `category`, no `image`), and whether any test beyond `test_eval_corpus.py` depended on their root
  location (one does: `test_extraction_contract.py::test_corpus_integrity`). Both were read, not
  assumed.
- **DURING EXECUTION:** whether to ship the mechanically-working freeze and report the suite red, or to
  revert. Chose revert + STOP: the packet forbids suite hunks beyond the two lines, so shipping would
  leave `automation` red with no in-ceiling repair; "a shape mismatch stopped the move" is the packet's
  own BLOCKED clause.
- **REMAINING:** (1) sg026 is still unfrozen — needs a ceiling that includes
  `tests/test_extraction_contract.py` (and a decision on `category`/`image` if `run.py` integrity is to
  pass); (2) SG-085/SG-089's "sg026 needs a manifest" residual stays open; (3) `STATE.md:2` stale
  contract `0.36.0` (F-SG123-4).
