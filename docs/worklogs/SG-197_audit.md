# SG-197 — Close-out deploy rider served live, rated 97

Immutable audit: base `e025fc3` (packet + D-3 record) -> work `94c8fc2` (10 evidence logs, +686, zero product) -> paste `2f840d5`. Trigger exit 0, `result=done id=SG-197 exit=0`. TWO receipts read back (WORK_HEAD note + paste dual-annotation note, identical trailer + Work-HEAD `94c8fc2`; paste note carries envelope-sourced settings, coder/model/effort all `*_source=command`, matching the trigger). Local `--ff-only` to the exact paste HEAD (`2f840d5` == origin/automation). Scope: work diff exactly 10 worklog files; zero product/config/schema/migration/test edits in the slice (the deployed product tree is the pre-existing merged SG-194+SG-195 tree). No restart beyond the one authorized recreate; production datastore never written (mode=ro reads; DB sha identical before/after deployment and tests). Contract 0.50.0 echoed == packet expectation, sha match; host rules_check exit-3 known shape.

Holistic rating: **97/100**, no flag. Deduction attribution: coder (I1 two self-caused aborted invocations, zero tests each, disclosed and corrected once — cheap but needless). `slowest_waste` = `none` (every committed leg's conclusion was used; attempt-1 zero-test outputs used for the CO-35 non-prove finding).

## Evidence accepted

- A1: build log read — one issuance through the lane socket, exit 0, 27 s, image manifest `e3b7c0aa`, dist asset `index-_9IDZb0V.js`. Recreate log read — one issuance through the lane socket, exit 0, 2 s, `Recreated/Started`. New running instance proven by container ID/Created (`e8a6ed6985ef`/2026-10-15T19:48:14Z -> `a77e3f2ff0dd`/2026-10-16T19:41:19Z), RestartCount=0 both, image `c3b85d5a` -> `e3b7c0aa`. Health green: prestate/end identical ok/ok/ok plus six post-recreate 200s read in their logs. Served bundle changed (`fd4a916e` 324210 B -> `8ba02c64` 325053 B; content-hash filename equals the build log name; bytes re-hashed from the live GET); index.html changed; CSS unchanged (expected — neither slice diff touches CSS). Schema delta none (alembic head unchanged); count delta none (28 tables, DB sha `e6bef157` pre == post == end).
- A2: base ref requested/resolved echoed separately; reachability `8a67ce3`/`f757ebd` ancestor-of-HEAD yes/yes read in the prestate log (PG-IC-07). Merged-vs-served product diff re-checked locally: `3c89c69..94c8fc2 -- backend frontend` = exactly 8 files +473/-18 (SG-194 hunk + test module; SG-195 5 routes + test module); models/alembic empty. PG-EV-08 before+after both captured: pre-serve bad/empty cursor 200 page-1-identical, post-serve both 422 `malformed cursor`, plain page-1 byte-identical across the recreate; SG-188 review-tasks control 422 unchanged. SPA routes /review /inbox /catalog 200 with new index sha; CORS preflight + actual GET headers read. Still-open items named as unchanged (SG-195 out-of-set -> SG-196 premises; SG-190 REMAINING stand; SG-176/178 untouched; known-host env rows unchanged).
- A3: 10 work logs + report; 514 s of 2100 (24.5%) with per-leg seconds and lane sources; constraints each answered; FIRST READ / DURING EXECUTION / REMAINING dispositioned; first token SG-197.
- A4: receipts verified (both notes present at ref tip, transcript in-report); pushes complete (branch `e025fc3..94c8fc2`, notes `19286a7..b193826`, both read back); bound lane receipt, retired finalizer untouched.
- Deduction (I1): backend pytest first ran under the root venv (pillow_heif collection errors, zero tests) and frontend vitest from backend cwd (binary absent, zero executed); corrected (backend-local venv, frontend cwd) with one rerun each; both attempts committed; no acceptance result consumed by attempt 1 (CO-35). Worklog deadline typo (I4) corrected by append (SG-195 precedent); prestate argv blemish (I2), host-reboot context (I3), vite display offset (I5) all disclosed and immaterial.
- `slowest_waste` (`D434`/`D436`): `none` — orientation (premise confirmation, load-bearing), prestate, build, recreate, post legs, focused tests, freeze/push/receipt all used; superseded attempt-1 outputs used for the CO-35 finding. Next packet removes nothing on this axis.

## Dispositions

| Item | Destination |
|---|---|
| SG-194 + SG-195 repairs | **SERVED** live (container `a77e3f2f`/image `e3b7c0aa`/bundle `8ba02c64`); unserved delta is now empty |
| Full-suite env rows (pyzbar/tesseract absent on host) | STATE known-host condition (host provisioning is Launcher's; no project action available) |
| SG-197 REMAINING (dual paste note post-report by construction; audit/rate done here) | Closed here |
| SG-195 out-of-set household queries; SG-190 REMAINING | SG-196 nav-context packet next in queue (STATE ordered work) |
| ISS-4 runner misfire class | Receipt-based condition held again here (done + receipt present, no re-trigger); desk matter, no new filing |

Harness context-size reading unavailable; no conclusion made.
