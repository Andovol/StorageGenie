# SG-300 screenshots — scratch only, then removed

Captured on the scratch build (`VITE_API_BASE=http://127.0.0.1:14300`, Node proxy to the scratch backend `127.0.0.1:18300` on a fresh migrated SQLite file, providers off, `SG_PROVIDER_ID=fake`). Test data through the API only: 14 items (12 food, 1 gone, 1 unsorted), generated 96 px test images. Light unless marked dark. Empty state: a second scratch database with one household and no food. Capture: Chrome DevTools Protocol from `shoot.mjs` / `shoot2.mjs` (kept here as evidence; `seed.mjs` made the data).

sha256 is the first 12 characters; bytes is the file size (`stat -c %s`). The DOM text is read from the page through the same DevTools session (`proof.json`, `shoot2` output).

| file | state | width | sha256 (12) | bytes | DOM text that proves the state |
|---|---|---|---|---|---|
| pantry-full-light-1280.png | Pantry full page, light | 1280 | ea1e21f6e484 | 482491 | `12 ITEMS`; 6 tile columns (distinct offsetLeft); horizontal overflow -15 (none); bordered tile wrappers 0 |
| pantry-useseen-light-1280.png | Use soon in view (top of page), light | 1280 | e7bbfc2c44c8 | 195489 | `JuiceEXPIREDExpired 3 days ago500 ml leftEditUse it upCheeseEXPIREDExpired yesterday1 left−1Use it upMilkUse by tomorrow2 left−1Use it up…` |
| pantry-full-light-375.png | Pantry full page, light | 375 | 15372fe310f1 | 490356 | 2 tile columns; overflow 0; bordered wrappers 0 |
| pantry-useseen-light-375.png | Use soon in view, light | 375 | cf09bdac835f | 114111 | same Use soon text as 1280 (order Juice, Cheese, Milk, Yogurt, Apples, Eggs, Bread) |
| pantry-tileminus-375.png | Milk tile after −1 (made through the API, `quantity/decrement` status 200) | 375 | ad72fce20647 | 137648 | `MilkUse by tomorrow1 left−1Use it up` |
| pantry-notice-375.png | Notice after Use it up (Juice), bottom of the screen | 375 | 5035cb335b48 | 111193 | `Juice used up · Put back` (`data-testid=pantry-notice`, role=status) |
| item-panel-light-1280.png | Item panel for Milk after −1 | 1280 | 8ae2964aa465 | 159869 | `Amount left−11 left+1` |
| catalog-gone-light-1280.png | Catalog, Gone filter | 1280 | 64c05ac944cc | 40365 | DOM text line `Gone — used up` (one element), `Old Soup` link (1), `Put back` button (1) |
| pantry-full-dark-1280.png | Pantry full page, dark | 1280 | b953913cd22a | 481884 | body background `rgb(15, 14, 13)`; 6 columns; overflow -15 |
| pantry-full-dark-375.png | Pantry full page, dark | 375 | f731ce3baaf4 | 490485 | body background `rgb(15, 14, 13)`; 2 columns; overflow 0 |
| pantry-useseen-dark-375.png | Use soon in view, dark | 375 | add156b168e0 | 113172 | body background `rgb(15, 14, 13)` (same DOM as light) |
| pantry-empty-375.png | Pantry empty state (second scratch DB, one household, no food) | 375 | f46eb2e611eb | 25777 | `0 ITEMS`; `No food yet. Add an item from Capture and classify it as food to see it here.`; Use soon `Nothing needs using soon.`; overflow 0 |

Distinct-hash check: `sha256sum *.png | awk '{print substr($1,1,12)}' | sort -u | wc -l` → 12; 12 shots → every shot has its own hash. No two shots of different states share a hash.

Not captured separately: dark Use soon at 1280 (the dark full page at 1280 shows the same section), a dark notice, dark catalog Gone view.
