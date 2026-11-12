import type { QueryClient } from "@tanstack/react-query";

/**
 * SG-308: one shared invalidation for every view that renders an asset's
 * quantity, status, expiry date or gone state.
 *
 * Keys refreshed (prefix invalidations, household-agnostic so every household
 * scope refetches):
 * - `pantry-assets` (Pantry tiles, count, ACTIVE/gone membership)
 * - `pantry-expiry` (Pantry Use soon membership + time-left line)
 * - `assets` (catalog list: quantity, status, Gone view)
 * - `asset` + id (drawer/detail singleton: quantity, status, gone, assertions)
 * - `expiry-status` (Expiry page buckets: expiry date, days, tier)
 * - `analytics-summary` (Analytics totals, Expiry uncategorized, Pantry unsorted)
 * - `household-assets` (relation target picker: names from the same asset rows)
 * - `asset-facets` (catalog pills: status/category counts)
 *
 * Not refreshed: `opened-countdown` (opened window, untouched by these five
 * mutations), `reminders` (reminder read/dismiss state), `planning-suggestions`
 * (suggestion state) — none displays quantity/status/expiry/gone from these
 * writes, and no test shows them going stale.
 *
 * Used by the panel's five mutations and by the Pantry's own tile/notice
 * handlers, so one place owns the set instead of five copies.
 */
export function invalidateAssetViews(qc: QueryClient, assetId: string): void {
  void qc.invalidateQueries({ queryKey: ["pantry-assets"] });
  void qc.invalidateQueries({ queryKey: ["pantry-expiry"] });
  void qc.invalidateQueries({ queryKey: ["assets"] });
  void qc.invalidateQueries({ queryKey: ["asset", assetId] });
  void qc.invalidateQueries({ queryKey: ["expiry-status"] });
  void qc.invalidateQueries({ queryKey: ["analytics-summary"] });
  void qc.invalidateQueries({ queryKey: ["household-assets"] });
  void qc.invalidateQueries({ queryKey: ["asset-facets"] });
}
