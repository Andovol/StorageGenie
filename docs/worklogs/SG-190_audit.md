# SG-190 — R8 responsive shell: overflow zeroed on all viewports, contrast AA, no logic drift

Immutable audit: base `2112cd1c0759041ce497fa21f0a8ad6579a8a022` → work `dc36291` (13 frontend files, +213/−65) → evidence `87d74cb` (+ masker fixup `82788dd`) → report `82788dd`. Forced-command status at end: `result=done id=SG-190 exit=0`; status verb after: `result=reject reason=replay` (correct: receipted). Mapped notes fetch read the receipt; settings envelope-sourced (command). Local pulled `--ff-only` to the exact report HEAD. Scope: frontend shell/routes/components/CSS + driver/measure/logs/shots only. Backend diff EMPTY (verified: `git diff 2112cd1..dc36291 -- backend` no output; frontend-only stat 13 files). No package.json change, no new dependency, no production write, no restart.

Holistic rating: **97/100**, no flag. Contract 0.47.0 echoed verbatim.

## Evidence accepted

- A1 NUMERIC, like-for-like: base reproduces the SG-183 verdict exactly (390: 10/10 routes, 136 offenders; 834: 9/10, 9; 320: 10/10, 153; contrast min 4.3977 on the exact audited pair) → candidate all-zero overflow on all 4 viewports incl. 320 reflow, contrast 1046 samples 0 below AA, min 5.2606. Recompute RESULT ok:true, all 9 checks true. Improvement shown numerically; no shortfall.
- A2: 30-Tab probe obscured=0/invisible=0 (numeric in measure JSON); menu closed 0/8 visible on all 10 routes at 390, open 8/8 in viewport, toggle hidden ≥768 — VISUALLY CONFIRMED in shots; draft round-trip preserved=true.
- A3: no logic drift — drift scan over added lines shows zero data-path additions (the one `localStorage.setItem` hit is a pre-existing handler on a re-wrapped line, proven in the InboxPage hunk); Menu button + Import CTA are local-state composition of EXISTING links/modal (read in full in the App.tsx diff — no data path, no navigation, aria-expanded/controls present); "Loaded:" literal with unchanged aria-label; test updates literal-only and SG-190-labelled. No `preventScroll`/alpha revival (grep over added lines empty). Rejected SG-183 claims not re-argued.
- Gates: 266/266 tests, lint 0, build 0 (verified in gate log, rc lines read).
- D425 discharged: ALL 43 images opened and confirmed one by one — 10 routes × 4 viewports render the expected route with intact layout and no visible overflow; menu-open shows all 8 destinations; tab/draft probes match their checklist lines; draft shot shows the honest filtered empty state. Masking is layout-readable throughout.
- Limits honestly stated (desktop-rendering, no zoom/touch/dark/authenticated-live, loopback fulfillment, sandbox flag) — carried as future scope, not passes.

No deduction: disclosed judgement calls (menu element, whole-frontend-suite authoritative set) were inside the plan/packet letter with revert paths and justification; environment notes (stale coder-read router, missing .rules-cache) are host facts, not slice faults.

## Dispositions

| Item | Destination |
|---|---|
| SC-15 sampled verdict (overflow + muted contrast) | **RESOLVED** on the sampled denominators — 0 overflow all viewports, 0 below-AA |
| SG-190 REMAINING: route error branches, nav household context/count, zoom/touch/dark/auth-live, density system | Next-session slice candidates (recorded in STATE, not slices yet) |
| jobs.py:116 cursor twin | Still queued micro-slice (unchanged) |
| Close-out live deploy (standing directive) | D398: close requested — recorded for next session, not executed unasked (production write, G-K2) |
| Serve | Normal deploy course via the recorded deploy decision |

Harness context-size reading unavailable; no conclusion made.
