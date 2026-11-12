import type { ProductItem } from "../../types/product";
import type { SavedSearch } from "../../api/types";

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

export type CatalogStatusFilter = "live" | "gone";

type CatalogToolbarProps = {
  categories: readonly string[];
  activeCategory: string;
  onCategoryChange: (category: string) => void;
  statusFilter: CatalogStatusFilter;
  onStatusFilterChange: (status: CatalogStatusFilter) => void;
  sort: SortOption;
  onSortChange: (sort: SortOption) => void;
  density: Density;
  onDensityChange: (density: Density) => void;
  activeFilters: string[];
  onClearAll: () => void;
  savedSearches: SavedSearch[];
  selectedSavedSearchId: string;
  onSavedSearchSelect: (id: string) => void;
  onSavedSearchDelete: (id: string) => void;
  onSaveSearch: () => void;
};

/**
 * SG-105 G2 + SG-307 G3: one shared paper control treatment. The single
 * `.sg-paper-control` rule lives in `frontend/src/theme/tokens.css` (paper
 * ground, `--line` border, square, `--ink` text); every select/button on a
 * paper page reuses it so no white `--card`/`--background` control leaks
 * through light or dark. Inbox's Review status select inherits it via this
 * constant without touching `InboxPage.tsx`.
 */
export const THEMED_CONTROL_CLASS = "sg-paper-control focus-ring";

export const CONTROL_STYLE: React.CSSProperties = {
  padding: "4px 10px",
  borderRadius: 0,
  borderStyle: "solid",
  borderWidth: 1,
  fontSize: 13,
  cursor: "pointer",
};

export function CatalogToolbar({
  categories,
  activeCategory,
  onCategoryChange,
  statusFilter,
  onStatusFilterChange,
  sort,
  onSortChange,
  density,
  onDensityChange,
  activeFilters,
  onClearAll,
  savedSearches,
  selectedSavedSearchId,
  onSavedSearchSelect,
  onSavedSearchDelete,
  onSaveSearch,
}: CatalogToolbarProps) {
  const selectedSavedSearch = savedSearches.find((s) => s.id === selectedSavedSearchId);
  const savedSearchLabels: string[] = [];
  if (selectedSavedSearch) {
    if (selectedSavedSearch.query.q) {
      savedSearchLabels.push(`q: ${selectedSavedSearch.query.q}`);
    }
    if (selectedSavedSearch.query.asset_type) {
      savedSearchLabels.push(`type: ${selectedSavedSearch.query.asset_type}`);
    }
    if (selectedSavedSearch.query.status) {
      savedSearchLabels.push(`status: ${selectedSavedSearch.query.status}`);
    }
    if (selectedSavedSearch.query.has_evidence !== undefined) {
      savedSearchLabels.push(selectedSavedSearch.query.has_evidence ? "evidence: yes" : "evidence: no");
    }
  }

  return (
    <div
      data-testid="catalog-toolbar"
      style={{
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: 8,
        padding: "8px 24px",
        borderBottomStyle: "solid",
        borderBottomWidth: 1,
        borderColor: "hsl(var(--line))",
        backgroundColor: "hsl(var(--paper))",
        color: "hsl(var(--ink))",
      }}
    >
      <div role="group" aria-label="Live or gone" style={{ display: "inline-flex", gap: 0 }}>
        {(["live", "gone"] as CatalogStatusFilter[]).map((option) => {
          const active = option === statusFilter;
          return (
            <button
              key={option}
              type="button"
              aria-pressed={active}
              onClick={() => onStatusFilterChange(option)}
              className="sg-paper-control focus-ring"
              style={{
                padding: "4px 10px",
                borderRadius: 0,
                fontSize: 13,
                fontWeight: active ? 600 : 400,
                cursor: "pointer",
                backgroundColor: active ? "hsl(var(--ink))" : "hsl(var(--paper))",
                color: active ? "hsl(var(--paper))" : "hsl(var(--ink))",
              }}
            >
              {option === "live" ? "Live" : "Gone"}
            </button>
          );
        })}
      </div>

      {categories.map((category) => {
        const active = category === activeCategory;
        return (
          <button
            key={category}
            type="button"
            aria-pressed={active}
            onClick={() => onCategoryChange(category)}
            className="sg-paper-control focus-ring"
            style={{
              padding: "4px 10px",
              borderRadius: 0,
              fontSize: 13,
              fontWeight: active ? 600 : 400,
              cursor: "pointer",
              backgroundColor: active ? "hsl(var(--ink))" : "hsl(var(--paper))",
              color: active ? "hsl(var(--paper))" : "hsl(var(--ink))",
            }}
          >
            {category}
          </button>
        );
      })}

      <select
        aria-label="Sort catalog"
        value={sort}
        onChange={(event) => onSortChange(event.target.value as SortOption)}
        className={THEMED_CONTROL_CLASS}
        style={CONTROL_STYLE}
      >
        {(Object.keys(SORT_LABELS) as SortOption[]).map((option) => (
          <option key={option} value={option}>
            {SORT_LABELS[option]}
          </option>
        ))}
      </select>

      <div role="group" aria-label="Density" style={{ display: "inline-flex", gap: 0 }}>
        {(Object.keys(DENSITY_LABELS) as Density[]).map((option) => {
          const active = option === density;
          return (
            <button
              key={option}
              type="button"
              aria-pressed={active}
              onClick={() => onDensityChange(option)}
              className="sg-paper-control focus-ring"
              style={{
                padding: "4px 10px",
                borderRadius: 0,
                fontSize: 13,
                fontWeight: active ? 600 : 400,
                cursor: "pointer",
                backgroundColor: active ? "hsl(var(--ink))" : "hsl(var(--paper))",
                color: active ? "hsl(var(--paper))" : "hsl(var(--ink))",
              }}
            >
              {DENSITY_LABELS[option]}
            </button>
          );
        })}
      </div>

      <div style={{ flex: 1 }} />

      <button
        type="button"
        onClick={onSaveSearch}
        disabled={activeFilters.length === 0}
        className="sg-paper-control focus-ring"
        style={{ padding: "4px 10px", borderRadius: 0, fontSize: 13, cursor: "pointer", opacity: activeFilters.length === 0 ? 0.5 : 1 }}
      >
        Save search
      </button>

      {savedSearches.length > 0 ? (
        <select
          aria-label="Saved searches"
          value={selectedSavedSearchId}
          onChange={(event) => onSavedSearchSelect(event.target.value)}
          className={THEMED_CONTROL_CLASS}
          style={CONTROL_STYLE}
        >
          <option value="">Saved searches</option>
          {savedSearches.map((saved) => (
            <option key={saved.id} value={saved.id}>
              {saved.name}
            </option>
          ))}
        </select>
      ) : (
        <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>
          None yet
        </span>
      )}

      {selectedSavedSearch && (
        <button
          type="button"
          aria-label="Delete saved search"
          onClick={() => onSavedSearchDelete(selectedSavedSearch.id)}
          className="sg-paper-control focus-ring"
          style={{ padding: "4px 10px", borderRadius: 0, fontSize: 13, cursor: "pointer" }}
        >
          Delete
        </button>
      )}

      {savedSearchLabels.map((label) => (
        <span
          key={label}
          style={{ fontSize: 13, padding: "2px 8px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink-muted))" }}
        >
          {label}
        </span>
      ))}

      {activeFilters.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {activeFilters.map((filter) => (
            <span
              key={filter}
              style={{ fontSize: 13, padding: "2px 8px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink-muted))" }}
            >
              {filter}
            </span>
          ))}
          <button
            type="button"
            onClick={onClearAll}
            className="focus-ring"
            style={{ background: "none", border: "none", fontSize: 13, cursor: "pointer", textDecoration: "underline", color: "hsl(var(--link))" }}
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
