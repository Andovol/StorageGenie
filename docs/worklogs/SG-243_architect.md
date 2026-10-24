# SG-243 — Architect record (Phase B of the W1 second opinion, run on 2026-10-24)

**Trigger:** `SG-243 coder=opencode model=opencode-go/muse-spark-1.3-contributor effort=xhigh agent=plan` (read-only lane, the same reviewer as Phase A). The lane returned `exit 0`.
**Status verb read-back:** `result=done id=SG-243 inactive`; the published report was fetched with `SG-243 --status` and copied **unedited** to `docs/worklogs/SG-243_report.md` (9586 bytes, the report body between the `debug-report-begin` / `debug-report-end` markers).
**Receipt:** the reviewer published no receipt note of its own (as Phase A did not) — the record of this phase is this file and the committed report.

## What Phase B found, and the Architect's disposition of every finding

| # | Finding (Phase B) | Disposition | Why |
|---|---|---|---|
| **a1** | **Phase A's refused-D objection HOLDS**: D keeps the image run mandatory, so the host suite going from `2 failed, 740 passed` to `740 passed, 2 skipped` proves nothing by itself — D relabels the confusion and does not remove the proof tax | **ACCEPTED** (with a precision) | True: the image run stays mandatory under D. The precision: the tax D removes is the **explanation** tax — today every slice must re-prove that two reds are environmental; the run itself was already required by D-1024-6. D does not make the run optional, and the slice design must not pretend it does |
| **a2** | **D as written trades a loud failure for a quiet one**: (i) under `-q` the suite reads as healthy counts and a slice can report PASS without ever running the image; (ii) the mandatory-run trigger is **procedural**, enforced by nothing in the repo, and a regression arriving via a non-signals path (Pillow/heif upgrade, `settings`, observation schema, storage path) triggers no image run; (iii) **three lists** must agree forever — the product's import branches (`signals.py:102-109`, `:207-214`), the new test guards, and the prover's hardcoded node IDs (`Makefile:11-12`); the gated tests also exercise **pure-Python validation** (`bad_value not in json.dumps(bad_values)`, `validated is False`, `test_signals.py:136-140`) that would then never run on the host | **ACCEPTED — it changes the design** | The mechanism is evidenced (unenforced trigger, `-q` invisibility, list drift), the severity ranking is labelled opinion. The fixes are small and go into the slice: **(i)** the skip reason is printed by the host run's own summary, and the **enforcement moves from the report to the target** — `make backend-test` runs the host suite **and** the image proof of the gated set, and fails if the proof fails, so a slice cannot report green without it; **(ii)** the gate is triggered by the **target**, not by "a slice that touches the signals code", so a non-signals regression path is covered by construction; **(iii)** the **single source of truth is a pytest marker** on the gated tests — the Makefile refers to the marker, not to hardcoded node IDs — and the **pure-Python validation is split out** of the gated test so the host keeps that coverage |
| **a3** | **Guard/product drift**: the product's pure-Python `_fallback_ean13` (`signals.py:153-192`) can recover an EAN **without zbar**, so a guard that skips on "pyzbar missing" would skip a test that could have run — green in both places, coverage lost | **ACCEPTED as a design requirement** | Verified: `signals.py:153` `def _fallback_ean13` and `:195` `_ean_check_digit` exist and are pure Python. So the guard must probe **the exact capability the test needs** — `from pyzbar.pyzbar import decode` loadability and `shutil.which("tesseract")` — and the skip must name the missing capability, not the package |
| **b** | The strongest case **for** D: B is out on measured grounds (no-new-privileges is a unit property — a unit change plus a scoped sudoers rule on the live serving host — and D-1024-6 priced B as a fallback used only if the image route fails, which has since succeeded); A moves 740 tests that need no native library for 2 that do, at an unmeasured cost; D is test-side only; the guard's specificity matches measured host behaviour (the **modules are present** — `requirements.lock:78` `pytesseract==0.3.13`, `:94` `pyzbar==0.1.9` — while the **binary and shared library are absent**: `SG-238_suite_after.log:43-44` "Barcode extraction unavailable: pyzbar/libzbar is not installed" / "OCR extraction unavailable: tesseract is not installed or it's not in your PATH") | **ACCEPTED** — no objection to raise | Every citation was re-checked against the committed logs and the lockfile this turn |
| **c** | **Unverified premise of D**: "the procedural prover rule is obeyed and sufficient — every future signals regression comes via a slice that touches the signals code, and that slice runs the image prover and reports it" | **ACCEPTED** — and it is *why* the design changes | The premise is unverified because nothing enforces it and sufficiency was never measured. An enforced target-level gate makes obedience **structural**; the marker set makes the gated set **single-sourced**; the trial below covers the sufficiency question at the level that can be measured |
| **d** | **The settling observation**: one whole-suite image trial, named not performed — build the image from the **current worktree** (not the stale `:latest` serve tag), run the FULL backend suite inside it as `docker run --rm --network none <fresh-image> python -m pytest -q`, record rc, duration and failures. Decision rule: green and comparable to the host's measured `61.96s` → A's premise holds and **A wins**; red, or far slower, or demanding a loop change → A's premise is false and **D wins** | **ACCEPTED — with one addition** | The reviewer's rule is adopted as written. The addition: the trial must also record **(i) the build time for a changed tree** (a rebuild is what a per-slice "one home" would cost — the cached build was 2 s of 600 s, a changed tree is not cached) and **(ii) whether a read-only worktree mount works under `--network none`** — the app's Dockerfile copies the code in, so "one home in the image" needs either a rebuild per slice or a mount; the review named only the rebuild. A's promise of a comparable loop is not established by the suite duration alone |
| — | **Judgement on A**: A as gated is coherent but does not survive as the immediate pick; A survives **only as the conditional fallback the trial would establish** | **ACCEPTED** | This moves the Architect's own position: A becomes **the consolidation to measure**, not the immediate pick. The immediate posture is D **with the fixes above** |

## The Architect's position after Phase B (what goes to the owner)

**The image route stays the home for the two library-dependent tests, with no change to the live host.** Three
parts:

1. **Gate only the two lib-dependent tests**, as loud presence-gated skips in the host suite; the skip names
   the missing capability and the command that proves the test in the image. The pure-Python EAN/validation
   coverage is split out so the host keeps it.
2. **Enforce the proof in the target, not in the report**: `make backend-test` runs the host suite **and** the
   image proof of the marked set and fails if the proof fails; the marked set is the single source of truth
   (one pytest marker, referenced by the Makefile, no hardcoded node IDs).
3. **Build the prover image from the current worktree**, never the stale `storagegenie-backend:latest` serve
   tag — the content staleness SG-240's audit caught.

**And measure the one consolidation the review named:** one whole-suite image trial from a fresh worktree
image, recording rc, suite duration, build time and whether a worktree mount works. Its result decides
whether the whole suite later moves into the image (A) or the host keeps the 740 (D). It changes nothing on
the host: no privilege, no service, no production write, no money.

**B (the host sudo install) stays out**, on measured grounds — not on taste: the fallback condition D-1024-6
attached to it ("used only if the image route fails") has not fired, and the price would be a unit-property
change plus a scoped sudoers rule on the live serving host.

## What is now the Architect's own residual uncertainty

The remaining unknown is **not** the pick; it is the **sufficiency of the gated set**. The marker names the
tests that need the native libraries today; a third lib-dependent test, or a new one added later, must join
the marker or it runs on the host and fails there. That is a **process** risk, and the slice's answer is the
narrowest thing that removes it: the marker set is the single source of truth, and the Makefile's gate proves
the marked set in the image **every time** — so a new unmarked lib-dependent test fails loudly on the host,
which is the signal to mark it. That is the honest cost of D, and it is smaller than it looks.
