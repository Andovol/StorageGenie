/**
 * SG-300 G1 line 3: the one shared quantity wording, used by the Pantry tile,
 * the item panel (ItemInspectorDrawer) and the item page (AssetDetailPage).
 *
 * `counted` is SG-272's rule (`isCountedUnit` in routes/AssetDetailPage.tsx):
 * an empty unit, pcs, bottles and other count units are counted and read
 * "4 left"; amount units (ml, l, g, kg and their names) read "340 g left".
 * An empty quantity reads SG-272's "No count yet" / "No amount yet".
 */
export function quantityLeftText(
  quantity: number | null | undefined,
  unit: string | null | undefined,
  counted: boolean
): string {
  if (quantity == null) return counted ? "No count yet" : "No amount yet";
  if (counted) return `${quantity} left`;
  const label = unit?.trim() ?? "";
  return label ? `${quantity} ${label} left` : `${quantity} left`;
}
