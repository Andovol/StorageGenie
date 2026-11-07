# SG-286 audit — stopped correctly in G2 on my own rule: empty mount-point directories

**Score 96/100; no flag. The stop was correct.** Model `opencode-go/claude-haiku-5-5`, effort `high`, both from the receipt's `Settings:` line (command source). Diff `4b480d6..e8e45bf` is `docs/worklogs/SG-286_diff.log` and `SG-286_report.md` only; the receipt is on the notes ref and `published_head=yes`. Read: the report, the diff log (non-cache entries extracted), the receipt. Host-side claims are the report's; this audit cannot read the host.

## What holds

- **The live app was not touched:** same container, same start time `2026-11-02T15:52:53Z`, restart count 0, health ok at start and end, and the diff list unchanged at 208 lines.
- **The original image is not findable:** the containerd store is in use; the container's `.Image` and `96a66241` both answer `No such image`; no image was created in the 15:40–15:56Z window. So SG-284's "maybe it is still there" is now measured: it is not, by any listed reference.
- **No scheduled cleanup** in crontab, systemd units or the `Makefile`.
- **Secrets rule kept:** no environment printed, no `.env` opened, no `cut`-free dump of inspect output.

## Findings

I1. **My packet's `/data` rule cannot pass on any container with mounts.** The three entries are `A /data`, `A /data/db`, `A /data/storage`, the mount destinations Docker creates in the container's own layer. Every other entry is `__pycache__`, `*.pyc` or a `C` parent of one (`SG-286_diff.log`). `UNVERIFIED — my knowledge of Docker, to be measured by the rerun's G3:` commit excludes mounted content, so these are empty directories in the image. **Attribution: packet.**

I2. **Reading D23 as approved, the rerun stays in scope.** D23 allows a commit when the changed files are transient and none looks like a database. Empty mount-point directories are neither, provided the rerun proves them empty in the committed image. So the rerun allows exactly those three directory entries and adds that proof; anything inside them stays a STOP. **Not returned to the owner,** and said so in this session's report.

I3. **Contract checker denied, disclosed and not routed around.** A permission rule denies reading `/home/andrei/storagegenie-contract/rules_check.sh`; the packet did not need it. The echo line is the host-version evidence. No deduction.

I4. **Small report gaps:** the end mount list was cut by the Coder's own `cut` and not re-quoted; the identity line says the effort was not in its trigger, which is correct (`PB-4`). Report-quality deduction only.

## Model note, for `docs/coder-profiles.md`

First Haiku slice on this lane. **It kept a hard stop rule at the first sign, reported the evidence, offered options without acting on them, and respected a permission denial.** It did not check emptiness, correctly, because the packet did not allow it at that step. ~70 s.

## Rating

`slowest_waste`: none. Next: rerun as **SG-290 on Muse 1.3 Contributor `xhigh`** (rotation: a rerun takes a new ID and the next slot), allowing exactly the three mount-point directories and proving them empty.
