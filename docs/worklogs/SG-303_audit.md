# SG-303 audit — the Pantry is live (`release-sg303`); one product finding: the access log records household ids

**Score 95/100; no flag.** Model `opencode-go/claude-haiku-5-5`, effort `high` from the trigger (the run could not read it). Report `7fc8882`; receipt `result=done exit=0 published_head=yes`. **Elapsed 128 s** against ≈300 s. Read: the whole report, the runtime diff, both census files.

## Checked independently

- **Census:** `diff SG-303_census_before.txt SG-303_census_after.txt` → no difference (every table, `reminder` 4 both).
- **Runtime diff:** exactly `app/api/v1/assets.py`, `tests/test_sg273_pantry.py` (added) and the three `static/` files — the derived backend set plus the expected frontend build.
- **Served strings** and the dark `--link: 2 41% 72%` quoted from the served artifact; `/pantry` 200.

## What holds

S1 reached with no rollback; container `0b4742d3…`, image `1e139734…` tagged `release-sg303`; schema head unchanged, no migration; health six times 200; routes `/`, `/pantry`, `/expiry`, `/inbox`, `/planning` 200; startup log clean; served `backend/` equals the worktree, 287 of 287 files. Every deviation disclosed unasked.

## Findings

I1. **The uvicorn access log writes query strings, including `household_id`, into `docker logs`.** Found by the Coder; the id reached its tool output (and so the model provider of this run) through a too-broad log filter, though not any file. It is an internal identifier, not a name. **Destination: backlog item for the owner** — move `household_id` out of query strings or drop query strings from the access log; riders filter logs to named lines only from now on.

I2. **An unlisted probe container** (`docker run --rm --network none --entrypoint sh` on the new image, no mounts, no env file) to hash the tree before the recreate. Harmless and disclosed; **attribution: packet** — G1 asked for a pre-recreate comparison without naming the command. Future riders name it.

I3. **Two `/tmp` attempts**, both refused by the gate, not retried. Coder; second `/tmp` slip this session (SG-302 on Muse too). Riders now say *"no `/tmp`"* explicitly, as build packets do.

I4. **The packet's `total` premise was false:** `/v1/assets` returns `{items, next_cursor}`. Packet defect; the Coder reported the count instead.

## Below 95

Not below 95.

## Model note

Haiku's eighth rotated slice: fastest rider yet, every state proven, every slip disclosed, and a real privacy finding raised unasked. Weakness: two `/tmp` attempts and an over-broad log grep.

`slowest_waste`: none notable (19 s of post-checks).
