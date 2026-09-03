# Launcher relay — publisher must restore the worktree branch after publishing

**Date:** 2026-09-03 · **Status:** drafted, UNSENT (send after SG-005 lands — nothing pushes to `automation` mid-flight) · **Joins the queued relay** (`STATE.md` Findings: `receipt_valid` literal, finalize re-parameterization, `max`/`xhigh` vocabulary)

## Defect class

Template-drift / missing-cleanup in the host dispatch payload (`/opt/storagegenie-dispatch/`). Same family as the two repaired drifts: code that works once, then poisons the next run.

## Incident (provenance)

- SG-004's publisher (`finalize_dispatch_report.sh`) created receipt `3294091` on `storagegenie-evidence` and left the host worktree's `automation` branch pointing at it (verified on host: `git log origin/automation..HEAD` → `3294091 receipt(SG-004)`; local `automation` == `origin/storagegenie-evidence`).
- SG-005's dispatch was then refused at the pre-work gate: `DISPATCH_REJECTED g2b_divergence_refused` (wrapper stdout, exit 2). The gate worked as designed — it stopped a slice that would otherwise have built on a receipt commit on the wrong line.
- Recovery was an owner-run `git reset --hard origin/automation` (lossless: `3294091` stays reachable from the evidence ref). Cost: one full diagnose-and-recover round trip plus owner hands on the box.

## Proposed fix (Launcher owns the template; permissive-only)

In `finalize_dispatch_report.sh`, after a successful publish: record the pre-publish branch/HEAD at script start, restore it at script end (`checkout` back, no history rewritten, no `--force` anywhere). If restore fails, the receipt is still valid — report the unrestored branch loudly in the publisher output so the next `g2b` refusal arrives pre-diagnosed.

`g2b()` itself stays exactly as is: it converted silent corruption into a 15-second loud stop, which is its job.

## Why not fixed from the project side

No shell path by design (`CODERS.md:278`); host payload is `root:root` outside the project tree; `--force` on the verb would route around the guard protecting the receipt commit. The only project-side levers — re-trigger discipline (done) and this relay — are both used.
