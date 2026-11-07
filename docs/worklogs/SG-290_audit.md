# SG-290 audit — the commit route is closed: the daemon cannot commit a container whose image is gone

**Score 96/100; no flag. The stop was correct.** Model `opencode-go/muse-spark-1.3-contributor`, effort `xhigh`, from the receipt's `Settings:` line (command source). Diff `a90102b..8728e34` is `docs/worklogs/SG-290_*` only; receipt on the notes ref, `published_head=yes`. Read: report, commit log, receipt. Host-side claims are the report's.

## What holds

- **Live app untouched:** same container and start time, restart count 0, health ok at start, during and end; the diff set unchanged at 208.
- **The diff rule now passes as intended:** 205 cache entries and their parents, plus exactly the three mount-point directories.
- **`docker commit` fails deterministically:** `NotFound: content digest sha256:93e35323…: not found`, twice, identical (`SG-290_commit.log`). Nothing was written; the tag is still absent; image count unchanged at 62.

## Findings

I1. **D23's commit route is closed on this daemon.** `UNVERIFIED — the Coder's inference and mine:` on the containerd image store, commit needs the parent image's content, which went with `96a66241`. Two identical failures make it deterministic, not transient. **This returns to the owner as D26**, since any other route was not approved.

I2. **My packet used a deprecated flag.** The daemon answered *"Flag --pause has been deprecated, and enabled by default. Use --no-pause to disable pausing during commit."* `UNVERIFIED:` whether `--pause=false` was honoured. If not, the live container was paused for at most the moments before each refusal; health stayed ok and the start time and restart count are unchanged. **Attribution: packet.** Any future commit uses `--no-pause`.

I3. **The lane denies `crontab -l` and the contract folder;** both disclosed, neither routed around. No deduction.

## Model note, for `docs/coder-profiles.md`

First rotated Muse slice. **Kept every stop rule, used exactly the one retry the contract allows, verified "nothing changed" when the packet's second diff no longer applied, and kept out-of-scope checks labelled as such.** ~100 s.

## Rating

`slowest_waste`: none. Deductions: packet (an untested route; a deprecated flag).
