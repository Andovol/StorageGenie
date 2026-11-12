# SG-302 shots — scratch only, then removed

Captured on the scratch build (`VITE_API_BASE=http://127.0.0.1:18302`, backend `127.0.0.1:18302`, frontend `127.0.0.1:14302`, fresh migrated SQLite files, providers off). Full DB: 14 items via API (12 food, 1 gone, 1 unsorted, generated 96 px images); after the notice click Juice is gone (11 ITEMS). Empty: second scratch DB with one household, no food. Capture: Chrome DevTools Protocol from `shoot_full.mjs` / `shoot_empty.mjs` (kept in scratch until removal; `seed.mjs` made the data). Backend scratch needed `CORS_ORIGINS=http://127.0.0.1:14302` for the direct `VITE_API_BASE` bundle; without it the browser fetches failed (`Failed to fetch`). The first three Use-soon shots were retaken once after the CORS fix (their first versions showed 0 ITEMS); the hashes below are the retaken (valid) versions.

sha256 is the first 12 characters; bytes is the file size (`stat -c %s`). DOM text read from the page through the same DevTools session (`proof_full.json`, `proof_empty.json`, plus a final dump for the retaken Use-soon state without Juice).

| file | state | width | sha256 (12) | bytes | DOM text that proves the state |
|---|---|---|---|---|---|
| pantry-use-soon-dark-1280.png | Pantry Use soon in view, dark (post-notice, Juice gone) | 1280 | 7beb2d8005da | 302754 | `11 ITEMS`; Use soon `CheeseEXPIREDExpired 3 days ago1 left−1Use it upMilkEXPIREDExpired yesterday…` (no Juice; Juice used up); EXPIRED label colour `rgb(213, 156, 154)` on `rgb(32, 27, 23)` |
| pantry-use-soon-dark-375.png | Pantry Use soon in view, dark | 375 | 03d2456b7a36 | 114654 | same Use soon text as 1280 (Cheese, Milk, Yogurt, Apples, Eggs, Bread); EXPIRED `rgb(213, 156, 154)` |
| pantry-use-soon-light-375.png | Pantry Use soon in view, light (proof light unchanged) | 375 | e0dd18e15335 | 114070 | same Use soon text (Cheese…Bread); EXPIRED `rgb(110, 48, 46)` on `rgb(244, 240, 232)` |
| pantry-notice-dark-375.png | Notice after Use it up (Juice), dark | 375 | 3e506593d834 | 111434 | `Juice used up · Put back` (`data-testid=pantry-notice`, role=status); EXPIRED at notice time `rgb(213, 156, 154)` |
| pantry-empty-dark-375.png | Pantry empty state, dark | 375 | ea0b32585cc4 | 26575 | `0 ITEMS`; `No food yet. Add an item from Capture and classify it as food to see it here.`; empty Capture link `href=/capture` `rgb(213, 156, 154)` underline on `rgb(32, 27, 23)` |
| pantry-empty-light-375.png | Pantry empty state, light | 375 | 718aecfea113 | 26288 | same empty text; empty Capture link `href=/capture` `rgb(110, 48, 46)` underline |
| catalog-gone-dark-1280.png | Catalog, Gone view, dark | 1280 | d9f337ee6b06 | 44278 | DOM `Gone — used up` (2); `Old Soup listed` (plus Juice gone after notice) |

Distinct-hash check: `sha256sum *.png | awk '{print substr($1,1,12)}' | sort -u | wc -l` → 7; 7 shots → every shot has its own hash. No two shots share a hash.
