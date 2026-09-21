# SG-077 — inspector drawer panel width repair

**Branch:** `automation` · **Remote:** `git@github.com:Andovol/StorageGenie.git` · **Work dir:** `/home/andrei/StorageGenie`
**BASE (packet ref `origin/automation`):** `29134a66604b99d28f54eb199660d599fd2a70fb` (`D99: SG-077 drawer width repair packet`)
**WORK_HEAD:** `{{WORK_HEAD}}` (work commit; the post-note receipt commit is HEAD after it)
**Contract:** recorded `0.28.2` == published; source `/home/andrei/storagegenie-contract/VERSION`, contract repo HEAD `b495b59b3426af66772a87939473ac558f8f72d2`
**Model / effort (`CO-78`):** model `deepseek-v4.1-flash` (provider `opencode-go`, read from provider metadata `/home/andrei/.local/share/opencode/log/opencode.log` line `run=eae3fc6e … llm.provider=opencode-go llm.model=deepseek-v4.1-flash`, **not** a system-prompt identity line; argv carries no `--model`) · effort `medium` (process argv `/proc/80676/cmdline`: `opencode run --auto --dir /home/andrei/StorageGenie --variant medium`)
**Spend (real $):** `$0.000000` actual vs `$0` bound — zero metered provider calls.
**Autonomy:** `L2` slice (1 retry available; not used).

The D99-approved defect repair. The owner reported a giant photo and "no information" in the
inspector drawer. Root cause (verified below, not assumed): `EMPTY_PANEL` sized the fixed
`aside` with Tailwind utility names — `max-w-2xl w-full border-l border-border bg-card p-6
overflow-y-auto z-50` — in a project that has **no Tailwind**. The panel therefore had no
width and no padding, and the `aspect-ratio: 1/1` viewer well sized itself off the viewport,
pushing every field below the fold. This slice constrains the panel and the well with
project-native inline CSS only, then enumerates and disposes of every other dead framework
class in the file. No behavior, copy, tab, field, handler or PATCH shape changed.

## Premise verification (a difference would have been a finding)

| Packet premise | Measured on tree | Verdict |
|---|---|---|
| No Tailwind dependency | `frontend/package.json` deps = react, react-dom, react-router-dom, @tanstack/react-query, lucide-react; no `tailwind` string in any `src` source/config | **confirmed** |
| `tokens.css` defines no `max-w-2xl`/`w-full` | selector set of the only stylesheet (`frontend/src/theme/tokens.css`) has neither; also missing `z-50`, `p-6`, `border-l`, `overflow-y-auto` | **confirmed** |
| `ItemInspectorDrawer.tsx:17` carries the dead constant | line 17 verbatim before edit: `const EMPTY_PANEL = "max-w-2xl w-full border-l border-border bg-card p-6 overflow-y-auto z-50";` | **confirmed** |
| Fixed-position `aside` gets no width | `style={{ position: "fixed", top: 0, right: 0, height: "100vh" }}` — no width; the 6 width tokens were all dead | **confirmed** |
| Contract recorded `0.28.2` == published | `VERSION` → `0.28.2`; contract repo HEAD `b495b59…` | **confirmed** |

One environmental difference, reported not bent: `frontend/.rules-cache/` is absent on this
host; the contract was read from the canonical `/home/andrei/storagegenie-contract/` checkout
(HEAD `b495b59…`, VERSION `0.28.2`). No `.rules-cache` dependency exists for this frontend
slice.

## G1 — constrain the drawer panel (project-native CSS only)

### Repair (all in `frontend/src/components/shell/ItemInspectorDrawer.tsx`)

```diff
-const EMPTY_PANEL = "max-w-2xl w-full border-l border-border bg-card p-6 overflow-y-auto z-50";
+const EMPTY_PANEL = "border-border bg-card";
+const PANEL_MAX_WIDTH = 440;
+const VIEWER_MAX_SIZE = 260;
```

The `aside` style now carries the real constraint (width cap 440 px, padding 24, vertical
scroll, stacking 50, left border from the project's `--border` token):

```diff
         className={EMPTY_PANEL}
-        style={{ position: "fixed", top: 0, right: 0, height: "100vh" }}
+        style={{
+          position: "fixed",
+          top: 0,
+          right: 0,
+          height: "100vh",
+          width: "100%",
+          maxWidth: PANEL_MAX_WIDTH,
+          padding: 24,
+          overflowY: "auto",
+          zIndex: 50,
+          borderLeft: "1px solid hsl(var(--border))",
+        }}
```

The viewer well keeps `aspect-ratio: 1 / 1` but can no longer exceed the panel — it is
width-bounded and height-bounded at 260 px and centered:

```diff
           style={{
             position: "relative",
             aspectRatio: "1 / 1",
+            width: "100%",
+            maxWidth: VIEWER_MAX_SIZE,
+            maxHeight: VIEWER_MAX_SIZE,
+            marginLeft: "auto",
+            marginRight: "auto",
             borderRadius: 8,
             overflow: "hidden",
```

**`tokens.css` was NOT touched.** The additive-utility allowance was not needed: the cap is a
single numeric value and the file already styles through inline objects, so no new selector
was warranted. Diff is 2 files (component + test).

### Dead-class enumeration (criterion: class name no project stylesheet defines)

I extracted every `className` token in the file (including the `EMPTY_PANEL` constant),
resolved the selector set of every `src/**/*.css` file, and diffed the two sets. Result:

| Dead token (pre-fix) | Was | Working replacement |
|---|---|---|
| `max-w-2xl` | panel max width — dead, so `none` | inline `maxWidth: 440` (PANEL_MAX_WIDTH) |
| `w-full` | panel width — dead, so content-shrink | inline `width: "100%"` |
| `border-l` | left width — dead (only `border-border` *color* exists) | inline `borderLeft: "1px solid hsl(var(--border))"` |
| `p-6` | panel padding — dead, so `0` | inline `padding: 24` |
| `overflow-y-auto` | panel scroll — dead, so `visible` | inline `overflowY: "auto"` |
| `z-50` | panel stacking — dead, so `auto` (backdrop is inline `zIndex: 40`) | inline `zIndex: 50` |

**No token was left intentionally dead.** Post-fix scanner output: USED = `bg-background
bg-card bg-card-muted bg-primary border-border focus-ring font-mono font-sans text-danger
text-foreground text-muted-foreground text-primary-foreground` (+ the constant name), and
every one of those has a project selector (the only "dead" entry was the parser echoing the
identifier `EMPTY_PANEL`, not a class). Raw scanner output is in `SG-077_verify.log`.

### FAIL-then-PASS (raw both sides; `PG-SC-12` — run against the real component)

Two presentation-only tests were **appended** to `frontend/src/components/shell/drawer.test.tsx`
under `describe("SG-077 panel containment (presentation only)")`. No behavior assert was
edited (`PG-SC-09`); `git diff` on that file is pure insertion.

**Pre-change (run against the dead-class component), raw:**

```
 ❯ src/components/shell/drawer.test.tsx  (17 tests | 2 failed | 15 skipped) 90ms
   ❯ … > the drawer panel carries a bounded width and the viewer well is capped to it
     → expected false to be true // Object.is equality
   ❯ … > no dead framework class survives on the drawer panel
     → expected [ 'max-w-2xl', 'w-full', …(6) ] to not include 'max-w-2xl'

 FAIL  … > the drawer panel carries a bounded width and the viewer well is capped to it
AssertionError: expected false to be true // Object.is equality
 ❯ src/components/shell/drawer.test.tsx:315:39
    314|     const panelMax = Number.parseFloat(panel.style.maxWidth);
    315|     expect(Number.isFinite(panelMax)).toBe(true);
 Test Files  1 failed (1)
      Tests  2 failed | 15 skipped (17)
EXIT=1
```

**Post-change, raw:**

```
 ✓ src/components/shell/drawer.test.tsx  (17 tests | 15 skipped) 121ms
 Test Files  1 passed (1)
      Tests  2 passed | 15 skipped (17)
EXIT=0
```

The tests assert `parseFloat(panel.style.maxWidth)` is finite and in `(0, 640]`, and
`parseFloat(well.style.maxWidth || well.style.maxHeight)` is finite, positive and `<= panelMax`.
Pre-change `panel.style.maxWidth` is `""` → `NaN` → finite check fails; the class check finds
the six dead tokens. Neither assert can pass vacuously: both read the live rendered DOM.

## G2 — what did NOT change

- **Diff scope (raw `git diff --stat`):** `ItemInspectorDrawer.tsx` (+25 −2) and
  `drawer.test.tsx` (+31 −0). **No backend, no migration, no `App.tsx`, no other component,
  no dependency, no compose, no `.env`.** No new dependency; no network call; no CDN.
- **Existing suites unchanged and green (raw):**

```
 ✓ src/components/shell/drawer.test.tsx  (17 tests) 593ms
 ✓ src/components/shell/shell.test.tsx  (20 tests) 1337ms
 Test Files  2 passed (2)
      Tests  37 passed (37)
EXIT=0
```

  37 = the 35 pre-existing tests (15 drawer + 20 shell, byte-for-byte unchanged) plus the 2
  new presentation tests. The 15 original drawer tests pass untouched — behavior, tabs,
  fields, handlers, PATCH shape and copy are identical.
- **Build (raw, `npm run build` = `tsc && vite build`):**

```
✓ 1961 modules transformed.
dist/index.html                   0.94 kB │ gzip:  0.47 kB
dist/assets/index-CoNI-1Zn.css    3.84 kB │ gzip:  1.04 kB
dist/assets/index-pbMtNPuG.js   303.97 kB │ gzip: 89.12 kB
✓ built in 1.71s
EXIT=0
```

- **Lint (`eslint` on both changed files):** EXIT=0, no output.
- **Secret scan (diff):** 0 real hits. The only match was the identifier `tokens`
  (`className.split(/\s+/)` in the new test) against a naive "token" keyword — not a secret.
- **No migration; no deploy; no restart.** `PG-PR-04` stated: this ships in a later rider.
- **Worktree clean** after the receipt commit (`CO-55`); `frontend/package.json` unmodified.

## G3 — guards, spend, receipt

- **Guards invoked (rating row):** `PG-EV-01` · `PG-EV-02` · `PG-EV-05` · `PG-EV-06`
  (authority: NONE — no dispatch verb run, own unit never started/polled) · `PG-EV-09` ·
  `PG-SC-02` · `PG-SC-09` · `PG-SC-12` · `PG-IC-01` · `PG-IC-07` · `PG-IC-09` · `PG-PR-03` ·
  `PG-PR-04` (NO DEPLOY).
- **Vacuous-pass analysis (loud):** the two new tests read the rendered DOM's inline styles and
  class list, so neither can pass without the component actually changing; the fail-pre run is
  committed raw and shows `EXIT=1`. The enumeration scanner did not scope itself narrowly — it
  walked every `className` token and every `src/**/*.css` selector. The build/lint/suite
  commands all ran against the real tree. No criterion could have passed on an empty diff: the
  pre-change tree provably failed the new tests.
- **Spend:** `$0.000000` real metered vs `$0` bound (zero provider calls, zero network).
- **Receipt:** work pushed to `automation`; worktree clean; note added on `WORK_HEAD` and the
  notes ref pushed; then fetched into a mapped local ref and `git notes show` pasted verbatim
  in the receipt subsection below.

### Receipt note verification (pasted `show` output)

```
{{NOTE_SHOW}}
```

Final line: `note=yes`

## UNCLEAR

- **FIRST READ:** the packet's `frontend/src/theme/tokens.css` additive-utility allowance was
  granted "only if the width needs one"; I judged it did not, because inline objects already
  style this file and a single numeric cap needs no selector. If the Architect intended a token
  utility regardless, this is the call to correct.
- **DURING EXECUTION:** `frontend/.rules-cache/` (referenced by the project table for the host
  contract) is absent on this box, so the contract echo was read from
  `/home/andrei/storagegenie-contract/` instead. No in-scope work depended on it.
- **REMAINING:** visual confirmation that the drawer now reads well at real viewport sizes is
  the owner's eyeball; jsdom asserts that a bound exists and is sane, never how it looks
  (`PG-PR-04`, BEAUTY not claimed).
