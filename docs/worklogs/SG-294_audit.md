# SG-294 audit — the recovery image exists and is proved

**Score 98/100; no flag.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh`, from the receipt's `Settings:` line. Diff `9ab143a..12e2087` is `docs/worklogs/SG-294_report.md` and `SG-294_inventory.py`; receipt on the notes ref, `published_head=yes`. Read: report, inventory script (no environment access, no printing beyond counts and per-entry metadata), receipt. Host-side claims are the report's.

## What holds

- **Recovery image:** `storagegenie-backend:recovery-sg270` = `sha256:2acd0c2438f34b5070b13bd04fa898b42cde126241dab43b0d124aa3a7a99ea2`, linux/amd64, created on the absent branch.
- **Same files as the live container:** its export and the live export have identical inventories (19,046 entries, sha256 `27c1376c…`, also equal to SG-293's two exports). The check was seen to fail on an altered copy first, on exactly one path.
- **Same launch configuration:** `Cmd`, `Entrypoint`, `WorkingDir`, `User`, `ExposedPorts` equal field by field; image environment 5/5 equal by hash; `GPG_KEY` fingerprint-shaped. No `.env` value in the image: the eleven compose and `.env` keys stay outside it, supplied at run time as today.
- **It starts:** on a scratch copy taken by SQLite's backup API, no network, no `env_file`: `GET /v1/health` 200 and `GET /v1/households` 200.
- **Live app untouched:** baseline equal to SG-290 at start and end; health ok.
- ~355 s against an expected ~600 s.

## Findings

I1. **`chmod 777` on its own scratch storage folder.** Allowed by the packet (a `chmod` on your own scratch folder); broader than needed, and removed with the scratch. No deduction beyond style.

I2. **Modification times are not compared,** by design: an import re-stamps nothing that runs, and the packet excluded them. Recorded so the rider does not assume them.

## Model note

Second Muse slice: **clean end-to-end execution of a long proof, every gate reported with counts, the negative control placed correctly, and a sensible route choice when two read routes needed parameters.**

## Rating

`slowest_waste`: none. Next: the rider, **SG-295 on Haiku 5.5 `high`** (rotation).
