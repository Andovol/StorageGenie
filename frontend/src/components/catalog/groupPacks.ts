import { sameNameKey } from "../../lib/sameNamePacks";
import type { SortOption } from "../shell/CatalogToolbar";
import type { CatalogProduct } from "./ProductCard";

/**
 * SG-337: grid-only grouping of live same-name packs into one card per name.
 * The grouping key is the shared same-name rule (`sameNameKey`: trimmed,
 * lower-cased, exact) — never a second copy. The table view and the Gone
 * view keep one row/entry per pack; only the grid path calls this.
 *
 * Order inside a group is date order, soonest first, no-date last (ISO
 * date-only strings compare lexically; a missing date always sorts after a
 * dated one) — the same order the SG-336 item page lists its packs. The
 * representative the card renders is the soonest pack: its name as written,
 * its date/photo/id, plus `packCount` for the muted `<N> packs` line.
 */
export function groupCatalogPacks(
  items: CatalogProduct[],
  sort: SortOption
): CatalogProduct[] {
  const byKey = new Map<string, CatalogProduct[]>();
  for (const item of items) {
    const key = sameNameKey(item.name);
    const group = byKey.get(key);
    if (group) group.push(item);
    else byKey.set(key, [item]);
  }

  const byDate = (a: CatalogProduct, b: CatalogProduct): number => {
    const da = a.useBy || "";
    const db = b.useBy || "";
    if (!da && !db) return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
    if (!da) return 1;
    if (!db) return -1;
    if (da !== db) return da < db ? -1 : 1;
    return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
  };

  const groups = [...byKey.values()].map((packs) => {
    const ordered = [...packs].sort(byDate);
    const soonest = ordered[0];
    // The soonest pack's photo, else the first pack in date order that has
    // one (the soonest may be dateless-by-photo while a later pack has a
    // thumbnail).
    const withMedia =
      ordered.find((pack) => pack.cutoutUrl ?? pack.sceneUrl ?? pack.evidenceId) ?? soonest;
    return {
      ...soonest,
      name: soonest.name,
      useBy: soonest.useBy,
      daysRemaining: soonest.daysRemaining,
      cutoutUrl: withMedia.cutoutUrl,
      sceneUrl: withMedia.sceneUrl,
      evidenceId: withMedia.evidenceId,
      packCount: ordered.length,
    };
  });

  // The grid's sort places a group by its soonest date (Use by, soonest
  // first) or its name — the same comparators `sortCatalog` uses for packs.
  groups.sort((a, b) => {
    if (sort === "name") return a.name.localeCompare(b.name);
    if (sort === "useby") {
      const da = a.useBy || "";
      const db = b.useBy || "";
      if (!da && !db) return a.name.localeCompare(b.name);
      if (!da) return 1;
      if (!db) return -1;
      if (da !== db) return da < db ? -1 : 1;
      return a.name.localeCompare(b.name);
    }
    return b.dateAdded.localeCompare(a.dateAdded);
  });
  return groups;
}
