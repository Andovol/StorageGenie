# SG-273 screenshots — scratch only (backend 127.0.0.1:18273, frontend 127.0.0.1:14273)

Test data via API only: 12 food items (generated PNGs, mixed pcs/g/ml, due soon/expired/safe/dateless), 1 unsorted, 1 gone. Providers off (fake, no key). Real photos: generated test images only; owner's first look is with real photos.

| file | shows |
|---|---|
| pantry-light-1280.png | Pantry full page, light, 1280x800 |
| pantry-dark-1280.png | Pantry full page, dark, 1280x800 |
| pantry-light-375.png | Pantry full page, light, 375x812 |
| pantry-dark-375.png | Pantry full page, dark, 375x812 |
| pantry-useseen-light-1280.png | Pantry Use soon section (same page, top), light 1280 (dark/375 same page as full; REMAINING as separate crops) |
| pantry-tileminus-light-1280.png | Pantry tile after -1 (Milk 2→1 via API), light 1280 |
| pantry-tileminus-dark-1280.png | Pantry tile after -1, dark 1280 |
| sg272-itempanel-light-1280.png | SG-272 item panel (live Milk): Amount left −1/+1, Use it up, light |
| sg272-itempanel-dark-1280.png | SG-272 item panel, dark |
| sg272-goneasset-light-1280.png | SG-272 gone asset page (Gone Soup, Used up, Put back), light |
| sg272-goneasset-dark-1280.png | SG-272 gone asset page, dark |
| sg272-catalog-light-1280.png | Catalog live (Gone view needs interaction; shows live list), light |
| sg272-catalog-dark-1280.png | Catalog live, dark |
| sg271-expiry-light-1280.png | SG-271 Expiry page with dateless note (Salt/Tea No date), light |
| sg271-expiry-dark-1280.png | SG-271 Expiry page, dark |
| sg271-inbox-light-1280.png | SG-271 Inbox step row (manual-entry tasks), light |
| sg271-inbox-dark-1280.png | SG-271 Inbox step row, dark |

REMAINING: pantry empty state (needs empty household; context auto-picks first — not captured); pantry Use soon dark/375 crops, tile 375, catalog Gone view filtered state, SG-271 Review committed candidate (In your catalog / Open item) and asset proposed date (Date proposed) — both need provider-made candidate state, skipped per packet (cannot be made without a provider).

Pixel shares (non-background vs corner sample, threshold 60): pantry-light-1280 14.7% 48892B; pantry-dark-1280 20.3% 50271B; pantry-light-375 32.1% 26955B; pantry-dark-375 39.3% 27259B; tileminus/useseen same as pantry (same viewport); itempanel 3.8%/3.3% 71241/71324B; goneasset 4.1%/3.7% 73749/73892B; catalog 6.5%/5.5% 90880/91082B; expiry 6.2%/4.7% 114366/114033B; inbox 3.3%/2.8% 62399/62199B. No blank (blank proof 2727B, 0% nonwhite).

Design note: tiles render; dark paper/ink read well. Nothing changed on screens because of screenshots.
