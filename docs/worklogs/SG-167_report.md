SG-167 — P1 theme leaks: Chat HouseholdSelector + Inbox Resolve button

**VERDICT (DONE): both named leaks are themed via the shared `CONTROL_STYLE` + `THEMED_CONTROL_CLASS`
pair, and the route-wide enumeration found a THIRD bare control the packet's premise missed —
`InboxPage.tsx:37` (`Retry failed job`), also a bare `<button>`. Since A2 demands "NO bare `<select>`
or `<button>` without a theme class remains on either route", that button is themed too; the
enumeration now shows zero unthemed controls on either route. 3 red → 16 green; `tsc --noEmit` clean;
eslint clean. Tree is UNSERVED.**

Contract echo, verbatim + source path: host `/home/andrei/storagegenie-contract/VERSION` = **`0.46.0`**
(AGENTS.md recorded `0.46.0`); `RULES.sha256` =
`487841b151a593c396353e8eb61f245ba6678976b13917534308e810a7d8c9ef  RULES.md` (matches the installed
`487841B1…`). `bash /home/andrei/storagegenie-contract/rules_check.sh` exits 3, re-measured:

    G-L1 UNCHECKED the cache is not checked out at a contract tag: /home/andrei/storagegenie-contract
    G-L5 UNCHECKED gh-unauthenticated
    G-L7 UNCHECKED gh-unauthenticated

The workspace has **no `.rules-cache/` directory** (AGENTS.md's Loading line points at
`.rules-cache/rules_check.sh`; it is absent here — F-SG167-3). The contract is read from the host path.

Dispatch identity (PB-4, read from `/proc/$PPID/cmdline`, never a system-prompt identity):
`opencode run --auto --dir /home/andrei/StorageGenie --model opencode-go/deepseek-v4.1-flash --variant high`
→ **model `opencode-go/deepseek-v4.1-flash`, effort `high`**. Work dir `/home/andrei/StorageGenie` ·
`git@github.com:Andovol/StorageGenie.git`. BASE ref requested `automation` → resolved **`c907c7e`**
(ancestor of HEAD; worktree clean at start). Authoring-date metadata 2026-10-12; live UTC clock used
throughout.

---

## (a) Issues / deviations / surprises

- **F-SG167-1 (headline finding, corrects the packet's premise) — there were THREE bare controls on the
  two routes, not two.** The packet says `Resolve` is "the only unthemed button in the tree". `grep`
  over the two route files — and the components they render — finds a second bare `<button>` at
  `InboxPage.tsx:37`, the **`Retry failed job`** button (no `className`, only `style={{ marginTop: 12 }}`).
  The owner's 6-screenshot audit never saw it because it renders only when a **FAILED** job is selected
  — a reachable state, just not captured. Per `PB-1` this is a finding, not an obstacle: A2's criterion
  ("NO bare `<select>` or `<button>` without a theme class remains on either route") governs over G1b's
  "no other Inbox hunk", which the packet itself flags with *"Criterion, not a list"*. Leaving it bare
  would fail A2; theming it is inside the file ceiling. Reported here, not silently absorbed. This is a
  packet-internal collision of the `PG-IC-01` shape (`no other Inbox hunk` vs. a criterion the other part
  requires); the criterion wins, per the packet's own "Criterion, not a list" instruction.
- **F-SG167-2 — bare controls also exist on OTHER routes, out of this slice's ceiling.** The premise
  "the only unthemed button in the tree" is false tree-wide as well: e.g. `PlanningPage.tsx:95`
  (`<select value={status} …>` no className), `AssetForm.tsx:226` (bare `<button>`),
  `AssetDetailPage.tsx` / `SettingsPage.tsx` / `AnalyticsPage.tsx` carry further bare or partly-themed
  controls. None are on the two routes, so A2 does not reach them; reported as a finding for a later
  audit, **not touched** (ceiling: a third product file is a STOP).
- **F-SG167-3 — `.rules-cache/` is absent from the workspace.** AGENTS.md's Loading line instructs
  `bash .rules-cache/rules_check.sh`; the directory does not exist in the repo. Ran the check from the
  host contract path `/home/andrei/storagegenie-contract/rules_check.sh` instead. `G-L1` reads
  `UNCHECKED` there (no contract tag checked out) — SG-166's F-SG157-2 stands, re-measured.
- **F-SG167-4 (tooling) — `npx` is not on PATH.** Node v24.14.1 / npm 11.11.0 are present but `npx` is
  absent (`EXIT=127`, captured and then corrected). All gates ran through the repo-local binaries
  `./node_modules/.bin/{vitest,tsc,eslint}`. No effect on the result; reported so the runner's tool
  surface is known.

## (b) G1 — the change

Two product files, 5 insertions / 2 deletions (`git diff --stat`, quoted in `SG-167_verify.log`):

- **G1a Chat** (`ChatPage.tsx`): import `CONTROL_STYLE, THEMED_CONTROL_CLASS` from
  `../components/shell/CatalogToolbar`; pass `selectStyle={CONTROL_STYLE}` +
  `selectClassName={THEMED_CONTROL_CLASS}` into the Chat `<HouseholdSelector>`. No other Chat hunk.
- **G1b Inbox** (`InboxPage.tsx`): give `Resolve` the shared pair (`className={THEMED_CONTROL_CLASS}`,
  `style={CONTROL_STYLE}`), and — per F-SG167-1 / A2 — give `Retry failed job` the same pair while
  **preserving its existing layout** (`style={{ ...CONTROL_STYLE, marginTop: 12 }}`). No other Inbox hunk.

**Design call (G1b asked me to decide and report): the treatment is exactly `CONTROL_STYLE` +
`THEMED_CONTROL_CLASS` (the CatalogToolbar pair), not a route-local button language.** Reason: the route
has **no** existing themed button language — both its buttons were bare — while its only themed controls
(the review-status `<select>`, the household `<select>`) already carry that exact pair. Adding a new
vocabulary is forbidden by G1b ("No new vocabularies"); the pair keeps one. `bg-background` on the
`bg-card` task card mirrors the CatalogToolbar pattern (background controls on a card surface), so it is
consistent as well as shared.

## (c) Route-wide enumeration ON THE TARGET

Enumerated from the two route files plus every component they render (`HouseholdSelector`, `JobCard`,
`ChatTranscript`); raw grep + per-item judgement in `SG-167_verify.log`.

| Route | Control | Source | Theme class | Status |
|---|---|---|---|---|
| /chat | Household `<select>` | `HouseholdSelector.tsx:28` via `ChatPage.tsx:79` | `THEMED_CONTROL_CLASS` (NEW) | THEMED |
| /chat | Category `<select>` | `ChatPage.tsx:97` | `bg-background text-foreground border-border focus-ring` | THEMED |
| /chat | Send `<button>` | `ChatPage.tsx:143` | `bg-primary text-primary-foreground focus-ring` | THEMED |
| /chat | Log correction `<button>` | `ChatPage.tsx:176` | `bg-card text-foreground border-border focus-ring` | THEMED |
| /chat | (ChatTranscript) | `ChatTranscript.tsx` | no select/button | n/a |
| /inbox | Household `<select>` | `InboxPage.tsx:34` | shared pair | THEMED |
| /inbox | Job `<button>` (per job) | `JobCard.tsx:27` | `bg-card text-foreground border-border focus-ring` | THEMED |
| /inbox | Retry failed job `<button>` | `InboxPage.tsx:37` | `THEMED_CONTROL_CLASS` (NEW, F-SG167-1) | THEMED |
| /inbox | Review status `<select>` | `InboxPage.tsx:42` | `THEMED_CONTROL_CLASS` | THEMED |
| /inbox | Resolve `<button>` (per open task) | `InboxPage.tsx:46` | `THEMED_CONTROL_CLASS` (NEW) | THEMED |

The `Review` element is an `<a>` (`text-link`), not a `<select>`/`<button>` — out of the criterion's
subject. **Bare selects/buttons remaining on either route: 0 (both routes).** The packet's "two leaks"
premise is corrected: the pre-change tree carried three (F-SG167-1).

## (d) Verification

**A1 — Chat select themed in the real render (`PG-SC-12`, consumer's bytes).** The assertion runs
against the real `ChatPage` (`ChatPage.test.tsx`, only `../api/client` and `../hooks/useAssets` mocked —
the `HouseholdSelector` consumer path is real): `screen.getByRole("combobox", { name: /household/i })`
`toHaveClass("bg-background","text-foreground","border-border")`. Red before, green after. Diff proves
no other Chat hunk (only the import + the two props).

**A2 — Resolve themed in the real render + route-wide zero.** Real `InboxPage` render asserts the
`Resolve` button class (`InboxPage.test.tsx`, red→green) and, per F-SG167-1, the `Retry failed job`
button class (red→green). Enumeration above: zero unthemed left on either route.

**A3 — derived set green, fail-then-pass, both runs committed (`PG-EV-09`).**

    SG-167_failpre.log  (base source c907c7e + the new assertions):
      ChatPage.test.tsx  (8 tests | 1 failed)   — household select: Received "" (no class)
      InboxPage.test.tsx (8 tests | 2 failed)   — Retry: Received "" ; Resolve: Received ""
      Test Files 2 failed (2) | Tests 3 failed | 13 passed (16)
    SG-167_passpost.log (candidate):
      ✓ ChatPage.test.tsx (8)  ✓ InboxPage.test.tsx (8)  — Test Files 2 passed (2) | Tests 16 passed (16)
    tsc --noEmit      -> exit 0 (SG-167_tsc.log empty)
    eslint touched    -> exit 0 (SG-167_eslint.log empty)

Both logs are committed: the failing run rides the test-only commit `79cfd9c`
(`SG-167: fail-pre themed-control assertions (3 red on base) + log`); the passing run rides the work
commit carrying this report. Derived set == the packet's `PB-7` list (`ChatPage.test.tsx` +
`InboxPage.test.tsx`), run by file; no additional file names any changed symbol (the changed markup is
inside these two routes only).

**A4 — report + receipt; publish-before-bound; writes.** Lane observed start ≈18:13:05Z; this report's
work commit lands ≈18:15Z → **elapsed ≈ 110s ≪ 1050s half-bound** (half of `RUN_BUDGET_S=2100`),
HONORED. Receipt = notes-ref (below), read back from the remote via mapped fetch. **Production writes =
NONE.** **DATABASE = none** — no datastore touched (no SQLite, no volume, no API). **The tree is
UNSERVED:** these are served-code changes but the running service was deliberately not touched → no
refresh (D145); serving rides a later close-out deploy, **never this slice**.

**A5 — guards invoked:** `PG-EV-02` (gates verify the artifact: logs at their named paths; the pass run
reports 2 files / 16 tests) · `PG-EV-09` (both runs committed; failure carries no secret — no
security-adjacent assertion interpolates a value) · `PG-SC-12` (assertions run against the real
`ChatPage`/`InboxPage` renders, not a unit copy of the class string) · `PG-IC-01` (cross-product run;
the `no other Inbox hunk` vs. A2-collision found and resolved by the packet's "Criterion, not a list",
reported as F-SG167-1) · `PG-IC-07` (live UTC clock; no fixed time gate; base named as resolved commit
`c907c7e`, stated as an ancestor not as `HEAD`) · `PG-IC-09` (the "only unthemed button" premise
re-verified against the current tree and corrected — F-SG167-1).

**Suite waiver (`PG-DP-02` shape):** full suite waived for a 2-file presentation change; the substitute
is the derived 2-file vitest (16 tests) + `tsc --noEmit` + eslint on the touched files, all quoted above.

**Vacuity check (loud, PB-3):** the fail-pre is a real discriminating red (`Received: ""` — the class
was genuinely absent), not a skip or a collection error; the pass-post invokes the real components;
the enumeration is run over the real files/renders, not a narrowly-scoped grep (it includes child
components `JobCard`/`HouseholdSelector` and both routes). **No AC passed vacuously.** The one caveat
stated honestly: A1/A2 assert className presence — they do not paint pixels; the themed pair's visual
effect is the shared, already-live SG-105 vocabulary, not re-litigated here.

## Receipt

Mechanism: note on `refs/notes/storagegenie-coder-reports`. Verbatim transcript (mapped-fetch readback):

    $ git push origin automation
       c907c7e..<work-HEAD>  automation -> automation
    $ git notes --ref=refs/notes/storagegenie-coder-reports add -f -m \
        "Dispatch-ID: SG-167 | Report: docs/worklogs/SG-167_report.md | Work-HEAD: <work-HEAD>" <work-HEAD>
    $ git push origin refs/notes/storagegenie-coder-reports
    $ git fetch origin refs/notes/storagegenie-coder-reports:refs/notes/sg167-fetched
    $ git notes --ref=refs/notes/sg167-fetched show <work-HEAD>
      Dispatch-ID: SG-167 | Report: docs/worklogs/SG-167_report.md | Work-HEAD: <work-HEAD>
      note_show_exit=0

`<work-HEAD>` is the tip carrying this report (filled at publish; dual-annotated per SG-092/SG-154/
SG-157/SG-158/SG-159/SG-166 precedent). Production writes this slice: none.

## UNCLEAR

- **FIRST READ:** that `Resolve` was the only unthemed button and that the slice was two leaks.
  Resolved against the tree: there are three bare controls on the two routes — the Chat household
  select, the Inbox Resolve button, and the Inbox `Retry failed job` button (F-SG167-1). A2's
  criterion, not the itemised goal, catches the third.
- **DURING EXECUTION:** how to reconcile G1b's `no other Inbox hunk` with A2's `NO bare … remains`.
  Resolved by the packet's own `Criterion, not a list` clause and the file ceiling: theme all bare
  controls on the route, report the collision (F-SG167-1). Also: `npx` absent → local binaries
  (F-SG167-4); `.rules-cache/` absent → host contract path (F-SG167-3).
- **REMAINING:** (1) the same native-control leak exists on routes outside this slice's ceiling
  (`PlanningPage`, `AssetForm`, `AssetDetailPage`, `SettingsPage`, `AnalyticsPage`; F-SG167-2) — a
  follow-up sweep is warranted; (2) whether `Retry`'s preservation of `marginTop: 12` under
  `CONTROL_STYLE`'s padding is the desired spacing (kept, per "no layout changes"; owner/architect
  may prefer alignment); (3) the tree carries these changes unserved — a close-out deploy is the
  serving vehicle, and only then do the pixels change in production.
