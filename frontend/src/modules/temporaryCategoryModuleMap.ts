/**
 * Temporary category-to-module map (SG-273, roadmap stage C).
 *
 * This map is deliberately temporary: Wardrobe's slice registers the first real
 * second plugin and replaces this with the module framework. For now the Pantry
 * view reads it to know that accepted category `food_beverages` belongs to the
 * pantry module. Household pantry is shared (Q26).
 */
export const TEMPORARY_CATEGORY_MODULE_MAP: Record<string, string> = {
  food_beverages: "pantry",
};

/** The accepted classification slug the Pantry view lists. */
export const PANTRY_CATEGORY = "food_beverages";

/** The module name the Pantry view serves (read from the temporary map). */
export function pantryModuleForCategory(category: string): string | null {
  return TEMPORARY_CATEGORY_MODULE_MAP[category] ?? null;
}
