# SG-304r2 audit — SG-304's tests and full gate are green; G1 and G2 may now ship

**Score 92/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high` (receipt note, `coder_source=command`). Diff `5ff8732..ecaa54d`: four test files and `docs/worklogs/SG-304r2*` only, no product file. Elapsed 571 s (its own stamps) against the 1100 s hard stop. Its own verdict is `FAIL — A4` for one scratch file in `/tmp`, reported honestly.

**Probe before dispatch:** one `opencode run -m opencode-go/claude-haiku-5-5` call from the workstation answered `OK`, exit 0. The server run then worked, which shows the server's account answered too.

## Holds — checked here against the evidence files

| Claim | How I checked |
|---|---|
| FAIL on base `2221bc9` | `SG-304r2_fail.log`: backend case 1 fails with `status: duplicate_linked`; frontend fails on missing `same-name-warning` and the *It's another pack* button — the right failures, not setup errors |
| Existing pack untouched | `test_sg304_duplicate_pack.py:114,136,151`: full detail JSON `after == before`; `:120` asserts the new pack's quantity is `None` (no merge) |
| Full gate | `SG-304r2_backend.log`: 810 passed, 2 deselected; image proof 2 passed. `SG-304r2_frontend.log`: 58 files, 493 tests passed |
| One file per step | four commits, one test file each (`6fb224a`, `e801444`, `e440427`, `3573cf2`) — SG-304 run 1's failure did not recur |
| G-1 gap is real | `CandidateCard.tsx:147-155`: *Save edits* is not gated by `isDuplicate` |

## Findings

**I3. Scratch file written to `/tmp`** (`/tmp/opencode/sg304r2_base_backend.txt`). The packet and the project rule forbid this. The coder disclosed it and did not route around the refused `rm`. **Disposition: added to STATE's host-cleanup list.** No flag: it holds test output only and touched no live data — **this is my judgement.**

**I4. G-1: *Save edits* on a duplicate photo still loses the new date** (posts `edit`, then the commit takes the `duplicate_linked` path). This is the F10 wrong turn reachable without the new choice. **Disposition: P9 of the D35 polish slice** (hide *Save edits* on a duplicate, or send it through the same choice). It completes the approved F10 fix; it does not widen scope.

**I5. G-2: the F9 warning depends on full-text matching** (`fts.py:47-63`), so a name whose search tokens differ would not warn. Not tested. **Disposition: watch during the shelf trial; no slice now.**

## Rating below 95 — what went wrong (`RATING_ISSUE.md`)

- **Failure class:** prompt gap plus model execution.
- **Root cause:** the packet named scratch for the build and Docker only. It gave no path for the base-run captures, and the model picked `/tmp` (as SG-307r1 did).
- **Correction and recurrence guard:** the next packets name `output/<ID>-scratch/base/` for every captured output, base runs included, as a literal command line.
- **Owner impact:** 571 s; cost `unavailable`.

## Rating

92 — clean, well-proven work with honest gaps found unasked (G-1, G-2). Deducted for the `/tmp` write. slowest_waste: none.
