# SG-190 owner checklist — R8 responsive shell/design (presentation-only)

Every line names its evidence. Numeric proof: `SG-190_measure.json` (candidate, build dc36291) and `SG-190_summary_2026-10-13.log`; screenshots: `SG-190_shots/`.

- [ ] No sideways scrolling at 390px on any of the 10 routes (numeric: 0/10 overflow; shots `*_390x844.jpg`).
- [ ] No sideways scrolling at 834px (numeric: 0/10; shots `*_834x1112.jpg`).
- [ ] Desktop 1440px unchanged and clean (numeric: 0/10; shots `*_1440x900.jpg`).
- [ ] 320px reflow (non-excepted content): 0/10 overflow (numeric; shots `*_320x720.jpg`).
- [ ] Narrow left nav: tap "Menu" — all 8 destinations listed, active destination highlighted (`menu_open_390x844.jpg`); closed menu shows no focusable links (numeric: 0/8 visible, all 10 routes).
- [ ] Wide screens: menu never appears; destinations always inline; toggle hidden ≥768px (numeric 1440 check).
- [ ] Catalog header reads "Loaded: N items" with the loaded-not-total title (`catalog_390x844.jpg`, `catalog_1440x900.jpg`).
- [ ] Primary capture action ("Import Asset") reachable from every route (nav on non-catalog routes; header on catalog; same dialog).
- [ ] Capture page shows accepted formats and the 20 MiB per-file limit (`capture_390x844.jpg`, note under the dropzone).
- [ ] Keyboard: Tab through the catalog at 390px — focus stays visible, nothing hidden behind the sticky header (numeric: 30 Tabs, obscured=0, invisible=0; shot `tab_focus_catalog_390x844.jpg`).
- [ ] Drafts survive a viewport/rotation change: typed search text kept across 390→834→390 (numeric draft_probe preserved=true; shot `draft_probe_catalog_390x844.jpg`).
- [ ] Muted labels/chips meet contrast ≥4.5:1 on their surfaces (numeric: min 5.26:1, 0 samples below AA; was 4.3977 before).
- [ ] Asset detail narrow: title wraps, selects fit, assertions table fits the column (shots `asset_detail_390x844.jpg`, `asset_detail_320x720.jpg`).
- [ ] Asset detail: Evidence / Assertions / Audit history read as separate ruled sections (shots `asset_detail_*.jpg`).
- [ ] Review narrow: candidate fields stack above source evidence; completing actions visible (`review_390x844.jpg`).
- [ ] Inbox narrow: jobs list and detail stack in one column instead of a fixed two-column grid (`inbox_390x844.jpg`).
- [ ] Settings/Planning/Analytics/Chat/Expiry: controls themed, rows wrap, no page overflow at any sampled width (shots per route).
- [ ] No new behavior: no API/route change; backend diff empty; retry/run/complete actions unchanged (see report A3).

Notes for the owner: dark theme, touch emulation, page zoom, and the authenticated public URL were NOT measured in this slice (stated limits in the report). All screenshots use desktop rendering with names/photos masked.
