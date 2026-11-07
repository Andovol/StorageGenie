# SG-293 audit — export proof passes; stopped on my over-broad key-name rule (`GPG_KEY`)

**Score 96/100; no flag. The stop was correct.** Model `opencode-go/claude-haiku-5-5`, effort `high`, from the receipt's `Settings:` line. Diff `ddc7643..6300f5f` is `docs/worklogs/SG-293_report.md` and `SG-293_inventory.py`; receipt on the notes ref, `published_head=yes`. Read: report, inventory script, receipt. Host-side claims are the report's.

## What holds

- **Baseline unchanged** from SG-290: same container, start time, restart count 0, mounts, and the sorted diff set (208).
- **Export is safe and stable:** two exports of 642,994,176 bytes and 19,046 entries each; exactly three empty `data/` directories, no `.env`; inventories identical (sha256 `27c1376c…`). No extended attributes or capabilities in the tar; 3 long-name PAX records.
- **Launch fields:** `Cmd` equals `backend/Dockerfile:22`; no `Entrypoint`; `WorkingDir` `/app`; empty `User`; port 8000. Healthcheck lives in compose and equals it.
- **Image environment:** the donor (`sha256:e3e74a61…`, linux/amd64) has five keys, `GPG_KEY`, `LANG`, `PATH`, `PYTHON_SHA256`, `PYTHON_VERSION`; **all five hash equal in the live container.** The live container's other eleven keys are the compose and `.env` settings, by name only.
- **No value printed;** the inventory script reads only the tar it is given.

## Findings

I1. **My key-name rule caught a public value.** `GPG_KEY` is set by the official Python base image to the release signing key's fingerprint, a public value used to verify the Python download. `UNVERIFIED — my knowledge of the base image;` the rerun checks its shape without printing it. The rule did its job literally. **Attribution: packet.**

I2. **The rerun stays inside D26:** D26 takes the image environment from `:latest`'s image configuration, and `GPG_KEY` is part of it. Not returned to the owner.

I3. **Phase timings not captured** (162 s total, so no phase can have breached its bound). Report-quality deduction only.

## Model note

Second Haiku slice: **applied a hard rule literally even when the value was obviously harmless to a human, and reported options without choosing.** Good on safety; one small report gap.

## Rating

`slowest_waste`: none. Rerun as **SG-294 on Muse 1.3 `xhigh`** (rotation), with `GPG_KEY` allowed only if its value is a 40-character hexadecimal fingerprint.
