SG-004 — Receipt evidence-prefill verification report

BASE REF: automation
BASE resolved: 31e6b7d36c3ae5b06112a2b0ec48b18d0168acb2
WORK_HEAD: c0a14eed0045a01dd6e825f902766cf3acb28deb (the candidate work commit)
Work dir: /home/andrei/StorageGenie
Remote: git@github.com:Andovol/StorageGenie.git
Timeouts: 120s per ordinary command; 2100s overall. Observed commands completed in under 2s each; no command was killed or hung.

## G1 — wrapper repair

Checked `/opt/storagegenie-dispatch/finalize_dispatch_report.sh` read-only. The expected values are implemented across the first validation block, rather than as named header constants:

- ID prefix: `SG-`, line 6, match count 1 in the ID regex.
- Worklog directory: `docs/worklogs`, line 9 in `REPORT_PATH`, match count 1.
- Evidence ref: `storagegenie-evidence`, lines 12, 19, 33, and 42, match count 4.

The report/header argument for this run is exactly `contract_sync=refresh version=0.17.2`; that string is supplied to the publisher and is not embedded in the finalize script.

Foreign-project grep over `/opt/storagegenie-dispatch/*` for `HL-`, `healthylaws`, and `HealthyLaws` was non-empty: 1 hit, `/opt/storagegenie-dispatch/dispatch_coder.sh:72`, in negative-probe paths. The finalize script had 0 foreign hits. This is a reported pre-existing wrapper finding; it is outside this slice because the packet says that file was never patched.

Receipt command usage was checked unmodified; `--help` returned `DISPATCH_BLOCKED_REPORT: usage`, as expected for a four-argument-only interface. No wrapper repair was made.

## G2 — version chain

- Workstation checkout: `AGENTS.md` records rule-set version `0.17.2`.
- Host payload: `/home/andrei/launcher/VERSION` observed as bytes `0.17.2` followed by newline.
- Run header: `contract_sync=refresh version=0.17.2`.
- Evidence ref existence: `git ls-remote` observed `637302e74fac291a383525518dc4d263ce88267c refs/heads/storagegenie-evidence`.

All observed version links agree at `0.17.2`.

## G3 — contract, provenance, and health

The contract was read from `/home/andrei/launcher/CODER.md` for the shared contract path and `/home/andrei/launcher/CODER_PRODUCTION.md` for CO-42. The wrapper declares `CONTRACT_DIR=/home/andrei/launcher` at `/opt/storagegenie-dispatch/dispatch_coder.sh:11`; no `CODER.md` exists under `/opt/storagegenie-dispatch/`.

CO-42 exact quote from the host contract copy:

`CO-42` **Restoring production from backup is an incident, never silent cleanup.**

Model: `unknown`. Reasoning effort: `unknown`. Process arguments exposed only the shell command; no provider metadata was available. This is intentionally not inferred from an identity line.

Start health, exact outputs:

- `curl -s http://localhost:8000/v1/health` → `Not Found` (exit 0). This is the shared-host foreign 404 leg.
- `python3 -c "from fastapi.testclient import TestClient; from app.main import app; print(TestClient(app).get('/v1/health').json())"` → traceback ending `ModuleNotFoundError: No module named 'sqlalchemy'` (exit 1). The fallback is unanswered because this checkout's runtime dependencies are absent; no dependency installation was authorized.

End health, exact outputs:

- `curl -s http://localhost:8000/v1/health` → `Not Found` (exit 0).
- The same TestClient command → traceback ending `ModuleNotFoundError: No module named 'sqlalchemy'` (exit 1).

Delta: curl output unchanged (`Not Found` to `Not Found`); TestClient output unchanged (missing `sqlalchemy` to missing `sqlalchemy`). The app health criterion is unanswered, not green. The first orchestration attempt had malformed nested quoting and produced a `SyntaxError`; a corrected valid fallback attempt produced the dependency error above.

## G4 — worklog/report

Created only these repository outputs:

- `docs/worklogs/SG-004.log`
- `docs/worklogs/SG-004_report.md`

Both begin with token `SG-004`. No product files, database, `.env`, service, or migration were changed. No test suite was ordered. The required three UNCLEAR lines are at the end of this report.

## G5 — prefill and publisher

WORK_HEAD `c0a14eed0045a01dd6e825f902766cf3acb28deb` was pushed to `automation` (return code 0). The first mandated prefill from `90c4cabc98218ee9634a9829d20adb1451213f21` was rejected non-fast-forward because the existing evidence tip `637302e74fac291a383525518dc4d263ce88267c` was not its ancestor; no force push was used. The evidence tip was merged into the work history, producing `ec4254f45ffdfe0ee82b0bc214298209fea9f932`. The first publisher attempt then returned `unrelated_dirty: M docs/worklogs/SG-004_report.md`; this exposed that the unmodified publisher requires the report to be untracked. The report was therefore removed from the candidate index in `c0a14eed0045a01dd6e825f902766cf3acb28deb` while retained as the sole untracked output. The mandated prefill then succeeded (return code 0): `git push origin c0a14eed0045a01dd6e825f902766cf3acb28deb:refs/heads/storagegenie-evidence`. After fetch, `origin/storagegenie-evidence` was exactly `c0a14eed0045a01dd6e825f902766cf3acb28deb`; equality was verified before publisher invocation.

The unmodified publisher invocation is `/opt/storagegenie-dispatch/finalize_dispatch_report.sh SG-004 "contract_sync=refresh version=0.17.2" docs/worklogs/SG-004_report.md c0a14eed0045a01dd6e825f902766cf3acb28deb`. Its return code and receipt artifact hash are quoted in the final handoff. The evidence artifact must carry trailer `Dispatch-ID: SG-004`; absence is a failure, not a vacuous pass.

UNCLEAR — FIRST READ: The repository does not contain the referenced ARCHITECT.md, PACKET.md, DISPATCH.md, or PRODUCTION.md files; only the packet, AGENTS.md, and host contract files were available.
UNCLEAR — DURING EXECUTION: TestClient health remained unanswered because `sqlalchemy` is absent; no privilege or dependency-install route was attempted.
UNCLEAR — REMAINING: The final handoff supplies the publisher return code, receipt hash/trailer proof, and final clean-tree proof.
