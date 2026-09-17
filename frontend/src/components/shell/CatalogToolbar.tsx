import type { ProductItem } from "../../types/product";
import type { Household } from "../../api/types";

export type SortOption = "recent" | "name" | "status";
export type Density = "grid" | "table";

export const SORT_LABELS: Record<SortOption, string> = {
  recent: "Recently Added",
  name: "Name (A-Z)",
  status: "Processing Status",
};

export const DENSITY_LABELS: Record<Density, string> = {
  grid: "Standard Grid",
  table: "Compact Table",
};

// The "All" pill's key; category pills are otherwise the raw `asset_type`
// facet keys (SG-064 G2: the UI follows the data, not the static DQ1 labels).
export const CATEGORY_ALL = "All";

/**
 * The loaded page is ordered client-side only. Filtering by `q` (server FTS
 * MATCH on `display_name`) and by category (server `asset_type`) is owned by
 * `GET /v1/assets`; the former client-side re-filters are gone so the server is
 * the single authority (SG-064 G2).
 */
export function sortCatalog(items: ProductItem[], sort: SortOption): ProductItem[] {
  const sorted = [...items];
  sorted.sort((a, b) => {
    if (sort === "name") return a.name.localeCompare(b.name);
    if (sort === "status") return a.status.localeCompare(b.status);
    return b.dateAdded.localeCompare(a.dateAdded);
  });
  return sorted;
}

type CatalogToolbarProps = {
  categories: readonly string[];
  activeCategory: string;
  onCategoryChange: (category: string) => void;
  sort: SortOption;
  onSortChange: (sort: SortOption) => void;
  density: Density;
  onDensityChange: (density: Density) => void;
  activeFilters: string[];
  onClearAll: () => void;
  householdId: string;
  households: Household[];
  onHouseholdChange: (householdId: string) => void;
};

const controlStyle: React.CSSProperties = {
  padding: "4px 10px",
  borderRadius: 6,
  borderStyle: "solid",
  borderWidth: 1,
  fontSize: 13,
  cursor: "pointer",
};

export function CatalogToolbar({
  categories,
  activeCategory,
  onCategoryChange,
  sort,
  onSortChange,
  density,
  onDensityChange,
  activeFilters,
  onClearAll,
  householdId,
  households,
  onHouseholdChange,
}: CatalogToolbarProps) {
  return (
    <div
      className="bg-card border-border"
      style={{
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: 8,
        padding: "8px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
      }}
    >
      <select
        aria-label="Household"
        value={householdId}
        onChange={(event) => onHouseholdChange(event.target.value)}
        className="bg-background text-foreground border-border focus-ring"
        style={controlStyle}
      >
        {households.map((household) => (
          <option key={household.id} value={household.id}>
            {household.name}
          </option>
        ))}
        {households.length === 0 && <option value="">No households</option>}
      </select>

      {categories.map((category) => {
        const active = category === activeCategory;
        return (
          <button
            key={category}
            type="button"
            aria-pressed={active}
            onClick={() => onCategoryChange(category)}
            className={`${active ? "bg-primary text-primary-foreground" : "bg-card-muted text-muted-foreground"} focus-ring`}
            style={{ ...controlStyle, fontWeight: active ? 600 : 400 }}
          >
            {category}
          </button>
        );
      })}

      <select
        aria-label="Sort catalog"
        value={sort}
        onChange={(event) => onSortChange(event.target.value as SortOption)}
        className="bg-background text-foreground border-border focus-ring"
        style={controlStyle}
      >
        {(Object.keys(SORT_LABELS) as SortOption[]).map((option) => (
          <option key={option} value={option}>
            {SORT_LABELS[option]}
          </option>
        ))}
      </select>

      <div role="group" aria-label="Density" style={{ display: "inline-flex", gap: 4 }}>
        {(Object.keys(DENSITY_LABELS) as Density[]).map((option) => {
          const active = option === density;
          return (
            <button
              key={option}
              type="button"
              aria-pressed={active}
              onClick={() => onDensityChange(option)}
              className={`${active ? "bg-primary text-primary-foreground" : "bg-card-muted text-muted-foreground"} focus-ring`}
              style={{ ...controlStyle, fontWeight: active ? 600 : 400 }}
            >
              {DENSITY_LABELS[option]}
            </button>
          );
        })}
      </div>

      <div style={{ flex: 1 }} />

      {activeFilters.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {activeFilters.map((filter) => (
            <span
              key={filter}
              className="bg-card-muted text-muted-foreground"
              style={{ fontSize: 11, padding: "2px 8px", borderRadius: 999 }}
            >
              {filter}
            </span>
          ))}
          <button
            type="button"
            onClick={onClearAll}
            className="text-primary focus-ring"
            style={{ background: "none", border: "none", fontSize: 12, cursor: "pointer", textDecoration: "underline" }}
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
