# Second-opinion context pack — W1: the two host test libraries

**Prepared by:** the Architect, 2026-10-24. **Committed before Phase A runs** (`SECOND_OPINION.md`, `D451`).
**Decision:** W1 — how (or whether) the host `87.106.66.242` gets the two system libraries `libzbar0` and `tesseract`, so that the two always-red tests in `backend/tests/test_signals.py` stop being red on the host.
**Why it matters now:** every slice's backend suite run on the host ends two red, and each slice must first re-prove that those two reds are environmental before its own result can be read at all. The project's own image already carries both libraries, so the reds are *proven* environmental; the open question is only what the host should do about them.

## The evidence, verbatim

**The owner's own framing (2026-10-24, this chat):**

> W1 — whether to authorise an install path that can sudo for the two host test libraries (libzbar0, tesseract; the lane's sudo is denied and nothing on the host was changed; the image route make backend-test-image already proves those two reds environmental)

**The ruling already taken (2026-10-24, D-1024-6):**

> **Cheapest mechanism first:** the project's own image already installs both libraries (`backend/Dockerfile`: `apt-get install tesseract-ocr libzbar0`), so the fix is to run those tests **inside the image** and record the result — **no host change needed**.
>
> The host package install the owner authorised is the **fallback**, used only if the image route fails.

**The sudo probe inside a slice unit (`docs/worklogs/SG-238_sudo_probe.log`, verbatim):**

```
sudo_probe_start_utc=2026-10-24T14:09:17Z epoch=1792850957
sudo: The "no new privileges" flag is set, which prevents sudo from running as root.
sudo: If sudo is running in a container, you may need to adjust the container configuration to disable the flag.
sudo_rc=1
sudo_probe_end_utc=2026-10-24T14:09:17Z elapsed_s=0
```

**The image's libraries and the byte-equal test file (`docs/worklogs/SG-238_g3_image_libs.log`, verbatim):**

```
image_lib_probe_start_utc=2026-10-24T14:13:49Z
host test_signals.py sha256=0582e355210b2ff961865716ba424875e08ea89e9ba504e605be16a09d516fb7
0582e355210b2ff961865716ba424875e08ea89e9ba504e605be16a09d516fb7  /app/tests/test_signals.py
tesseract 5.3.0
	libzbar.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libzbar.so.0
pyzbar+pytesseract import ok; tesseract 5.3.0
image_lib_probe_end_utc=2026-10-24T14:13:50Z elapsed_s=1
```

**The repeatable route (`docs/worklogs/SG-238_g3_make_target.log`, verbatim):**

```
make_target_start_utc=2026-10-24T14:10:35Z
docker run --rm --network none storagegenie-backend:latest python -m pytest -q tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
..                                                                       [100%]
2 passed in 1.92s
rc=0
make_target_end_utc=2026-10-24T14:10:38Z elapsed_s=3
```

**SG-238's rating row (`docs/ratings.md`, the part that bears):**

> the two always-red signal tests proved environmental inside the project's own image (2 passed; tesseract 5.3.0 + libzbar.so.0 present; image test bytes byte-equal to host) with `sudo -n` DENIED so no host change was attempted; host suite 4 failed / 737 passed -> 2 failed / 740 passed (only the two environmental reds remain); repeatable command recorded as `make backend-test-image`

**The project's own image already installs both packages (`backend/Dockerfile:14`):**

```
RUN apt-get update && apt-get install -y --no-install-recommends curl tesseract-ocr libzbar0 && rm -rf /var/lib/apt/lists/*
```

**The two red tests (`backend/tests/test_signals.py`):**

- `test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier`
- `test_ocr_has_text_boxes_and_mean_confidence`

**The repeatable route as it stands (`Makefile:11-12`):**

```
backend-test-image:
	docker run --rm --network none storagegenie-backend:latest python -m pytest -q tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence
```

**The lane's shape (from the previous slices' own logs, `docs/worklogs/SG-238_sudo_probe.log` — the lane's own unit properties — and `docs/worklogs/SG-239.log`):**

- The slice runs as the dispatch account `andrei` in a systemd unit (`dispatch-storagegenie@<ID>`), with `RUN_BUDGET_S=2100`.
- The unit sets the **no-new-privileges** flag — the verbatim sudo probe above is that flag, not a password prompt. Escalation inside a slice unit is therefore impossible today; it is a unit property, not an account policy alone.

## Where it lives (read these — all inside this repository)

| What | Where |
|---|---|
| the image route | `Makefile:11-12` |
| the image's package install | `backend/Dockerfile:12-14` |
| the two red tests | `backend/tests/test_signals.py` |
| the sudo measurement | `docs/worklogs/SG-238_sudo_probe.log` |
| the image measurement | `docs/worklogs/SG-238_g3_image_libs.log` |
| the repeatable command's run | `docs/worklogs/SG-238_g3_make_target.log` |
| the suite counts | `docs/worklogs/SG-238_suite_before.log`, `docs/worklogs/SG-238_suite_after.log` |
| the rating | `docs/ratings.md` — the SG-238 row |
| the ruling already taken | `docs/decisions/2026-10-24-session-approvals.md` — D-1024-6 |
| the project's sensitive areas | `AGENTS.md` — "Project rules" |

## What binds it

**Rule IDs (quoted where the rule's own text matters):**

- **G-K2** — "These reach the owner however trivial they look: production data destruction or any production write, secrets / infrastructure / database-role changes, anything touching a declared sensitive surface, anything irreversible or outward-facing. They hold at every autonomy level."
- **PG-PR-01** — "Establish the capability model BEFORE writing a slice that depends on privileges. Enumerate the full capability set in one pass — 'what can this identity do to these objects?', never 'why did this one statement fail?' … Enumerate only with forms that change nothing if they succeed."
- **PG-PR-03** — "A denied privileged operation is a STOP, not a signal to route around."
- **G-A7** — "Simplicity over machinery. Prefer the smaller mechanism."
- **G-A10** — "Ask what already exists before designing it … AND IT FIRES IN THE DELETE DIRECTION TOO: before closing a gap, ask what the gap is FOR."
- **G-A9** — "A derived number is a hypothesis until something measures it … declare it uncalibrated at the site."
- **The project's own rule (`AGENTS.md`, "Project rules"):** "Sensitive areas: the stored photos and files, the app database, and the dispatch key and host. Every plan touching one goes to the owner alone, at every autonomy level."

**Decisions already taken (not reopened):**

- **D-1024-6** — the image route is the cheapest mechanism and comes first; the host package install is the owner's-authorised **fallback**, used only if the image route fails. The image route has since succeeded (the measurement quoted above).
- **D-1024-10** — the second opinion runs before a 🟠 decision reaches the owner; the review's pick, strongest objection and the disposition go into the decision item.

## The options as the Architect sees them (no pick shown — that is what makes Phase A blind)

- **A — Keep the image route as the home of those tests.** Extend `make backend-test-image` from the two signal tests to the whole backend suite, so the suite runs where the libraries already are and the host's two reds stop mattering.
- **B — Authorise an install path that can sudo** for exactly `libzbar0` and `tesseract` on the host. This is more than an apt line: the lane's unit sets the no-new-privileges flag and the dispatch account has no sudo rights today, so it means a unit property change **and** a scoped sudoers rule, on the live host that serves the app.
- **C — Leave everything as it is.** The host suite keeps two reds; every slice re-proves them as environmental before its own numbers can be read.

**What the pick is NOT allowed to assume:** that the host install is cheap, that the two reds cost nothing, or that the image route can carry the whole suite — that last one is unmeasured, and measuring it is work in itself.
