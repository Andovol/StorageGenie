import { apiGet } from "../api/client";
import type { Asset, AssetListResponse } from "../api/types";
import { expiryDateFrom } from "./labels";

/** SG-304 G1: a live item the typed name matches, with its date when it has one. */
export type SamePack = { id: string; name: string; expiry: string | null };

// Items in these states are not live; the list read already hides ARCHIVED.
export const NOT_LIVE_STATUSES = new Set(["ARCHIVED", "DISPOSED", "MERGED"]);

/**
 * SG-304 G1: live items whose name equals the typed name (trimmed,
 * case-insensitive). Uses the existing list read (`q` = FTS on display_name)
 * and the existing detail read for each match's date. Same name is NOT
 * identity: this only offers the existing item; the caller decides.
 *
 * SG-336: moved here from `components/AssetForm.tsx` so the capture form and
 * the item page share the one rule — no copy. Both callers import it.
 */
export async function findSameNamePacks(householdId: string, name: string): Promise<SamePack[]> {
  const wanted = name.trim().toLowerCase();
  const list = await apiGet<AssetListResponse>("/v1/assets", {
    household_id: householdId,
    q: name.trim(),
    limit: "100",
  });
  const matches = list.items.filter(
    (item) =>
      (item.display_name ?? "").trim().toLowerCase() === wanted && !NOT_LIVE_STATUSES.has(item.status)
  );
  return Promise.all(
    matches.map(async (item) => {
      let expiry: string | null = null;
      try {
        const detail = await apiGet<Asset>(`/v1/assets/${item.id}`, { household_id: householdId });
        expiry = expiryDateFrom(detail.assertions);
      } catch {
        expiry = null;
      }
      return { id: item.id, name: item.display_name ?? name.trim(), expiry };
    })
  );
}
