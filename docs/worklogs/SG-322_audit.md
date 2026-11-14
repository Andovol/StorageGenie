# SG-322 audit — the duplicate card is reachable: an open or held duplicate now reads with no `asset_id`

**Score 93/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high` (receipt note, `coder_source=command`). Diff `31eeac4..4111f3a`: `backend/app/services/candidates.py` (+12 −4), two new test files, SG-322 evidence, and SG-321's rescued report and shots (`83a5eb5`). Own verdict `FAIL — A3, A5`; **both failures trace to my packet** (below).

## Holds — checked here

| Claim | How I checked |
|---|---|
| The fix | `git diff`: `committed_asset_id` takes the duplicate proposal's own asset only when `candidate.state in {"accepted", "edited"}`; the later hops (SG-270, SG-275) are unchanged |
| FAIL then PASS (backend) | `SG-322_fail.log`: open, held and the Inbox open read return the existing item's id on the old code; 7/7 pass on the new code |
| *Another pack* already worked | case 4 passed on the old code — my packet's premise there was wrong, and it said so |
| Full gate | backend host 817 passed, image 2; frontend 59 files / 495 tests; the sg322, sg304 and sg271 files 19 + 27 green twice |
| SG-321 rescue | the shots and report are on `automation`, only `docs/worklogs` paths |

## Findings

**I13. Frontend FAIL-on-base was impossible** — the packet forbade any frontend product change, yet asked the frontend test to fail on the old code. **Packet error (mine).** The test is a guard fed the real API shapes, which is what was needed.

**I14. `/tmp` written by pytest's default temp folder** (`/tmp/pytest-of-andrei`) during `make backend-test`. **Packet error (mine):** the mandated gate writes there by default. Every earlier backend gate did the same. **Correction:** packets set `PYTEST_ADDOPTS="--basetemp=$PWD/output/<ID>-scratch/pytest"` in the preflight block.

**I15. A first report said `PASS`, then corrected itself to `FAIL`** within the run (`340d634` → `4111f3a`), before the receipt note. The correction is honest; the first verdict was not checked against its own criteria.

**I16. With `edited` counted as "decided", *Save edits* on a duplicate (gap G-1) still ends in *In your catalog* with the new date lost** — unchanged behaviour, still polish P9.

## Rating below 95

- **Failure class:** prompt gap (I13, I14) and model execution (I15).
- **Recurrence guard:** set `PYTEST_ADDOPTS` with `--basetemp` under scratch in every packet's preflight; never ask for FAIL-on-base from a file the scope forbids changing.
- **Owner impact:** elapsed per its stamps ≈ 330 s plus gate; cost `unavailable`.

## Rating

93 — a small correct fix, proven through the real read path, with honest self-correction. slowest_waste: none.
