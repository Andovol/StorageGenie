# 2026-10-15 — Close-out deploy decision (D-1)

(Filename retains 2026-10-14 — it is cited by the SG-193 packet/report. ISS-2: drafted against a stale clock; all dates below corrected to the live clock in the audit commit.)

Owner decision, recorded the moment issued (`G-O4`). Session item **D-1** (hyphenated; distinct from project D1 rule-set adoption 0.47.0, already approved 2026-10-13 and carrying no pending action).

Question put: execute the owed close-out deploy now, defer it to session close, or waive it — standing 2026-09-28 live-deploy-before-close directive vs `G-K2` production-write escalation; parked here by SG-190_audit D398.

Owner reply, quoted byte-identical: "D1 - approved" (2026-10-15, this chat). Read as approval of session item D-1 as recommended: **deploy now**. It is the only live decision in the turn. (`PG-IC-02`: every premise the question rested on — six unserved G1 commits, jobs.py:116 twin live, D16 L3 flow — was verified against tree/records before asking.)

Effect: authorizes the SG-193 serving rider (one rebuild + one recreate + verify, SG-192 shape) serving `341bd69`/`0dd037d`/`07d4ea8`/`e911cdc`/`02f1214`/`dc36291` (SG-185 through SG-190). The standing close-deploy is still due at session close (covers post-SG-193 delta: micro-slice + candidates).

Expected duration: ~600 s (uncalibrated; SG-191 ran 540 s stopped before build, SG-192 full serve inside the 600 s bound — `D369` lane-actual derivation, recorded here not in the packet).

Trigger settings (envelope, never packet per `D302`): coder=opencode (`D29`) model=opencode-go/deepseek-v4.1-flash effort=max (`D-1012-15`).
