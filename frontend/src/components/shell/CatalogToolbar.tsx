import { LayoutGrid, List } from "lucide-react";
import type { ProductItem } from "../../types/product";
import type { SavedSearch } from "../../api/types";

export type SortOption = "useby" | "recent" | "name";
export type Density = "grid" | "table";

// SG-331 T2: the one sort that puts what needs you first — past dates oldest
// first, then soonest, then no-date, ties by name. It is the default sort.
export const SORT_LABELS: Record<SortOption, string> = {
  useby: "Use by, soonest first",
  recent: "Recently added",
  name: "Name, A to Z",
};

// SG-331 T4: the view switch is two icon buttons — Photo grid / List. The
// map stays the single source for the accessible names and titles.
export const DENSITY_LABELS: Record<Density, string> = {
  grid: "Photo grid",
  table: "List",
};

const DENSITY_ICONS = { grid: LayoutGrid, table: List } as const;

// The "All" pill's key; category pills are otherwise the raw `asset_type`
// facet keys (SG-064 G2: the UI follows the data, not the static DQ1 labels).
export const CATEGORY_ALL = "All";

/**
 * The loaded page is ordered client-side only. Filtering by `q` (server FTS
 * MATCH on `display_name`) and by category (server `asset_type`) is owned by
 * `GET /v1/assets`; the former client-side re-filters are gone so the server is
 * the single authority (SG-064 G2).
 */
export type SortableItem = ProductItem & { useBy?: string | null };

export function sortCatalog<T extends SortableItem>(items: T[], sort: SortOption): T[] {
  const sorted = [...items];
  sorted.sort((a, b) => {
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
  return sorted;
}

export type CatalogStatusFilter = "live" | "gone";

/**
 * SG-330 R4: items per row. Wide viewports offer 4 / 5 / 6 (default 5),
 * narrow viewports (< 640 px) offer 3 / 4 (default 3). The choice is kept per
 * device in localStorage; the toolbar only shows the set for the live width.
 */
export const PER_ROW_WIDE = [4, 5, 6] as const;
export const PER_ROW_NARROW = [3, 4] as const;

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
  perRowWide?: number;
  onPerRowWideChange?: (n: number) => void;
  perRowNarrow?: number;
  onPerRowNarrowChange?: (n: number) => void;
  isNarrow?: boolean;
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
  perRowWide = 5,
  onPerRowWideChange,
  perRowNarrow = 3,
  onPerRowNarrowChange,
  isNarrow = false,
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

      {/* SG-331 T1: text tabs — no border or fill; the active one is ink 600
          with a 2 px ink underline, the rest muted at 15 px. The row scrolls
          sideways instead of wrapping. Labels carry no counts. */}
      <div
        data-testid="catalog-kind-tabs"
        style={{ display: "flex", gap: 16, overflowX: "auto", flexWrap: "nowrap", alignItems: "center" }}
      >
        {categories.map((category) => {
          const active = category === activeCategory;
          return (
            <button
              key={category}
              type="button"
              aria-pressed={active}
              onClick={() => onCategoryChange(category)}
              className="focus-ring"
              style={{
                background: "transparent",
                border: "none",
                borderBottom: active
                  ? "2px solid hsl(var(--ink))"
                  : "2px solid transparent",
                borderRadius: 0,
                padding: "4px 2px",
                fontSize: 15,
                fontWeight: active ? 600 : 400,
                cursor: "pointer",
                whiteSpace: "nowrap",
                color: active ? "hsl(var(--ink))" : "hsl(var(--ink-muted))",
              }}
            >
              {category}
            </button>
          );
        })}
      </div>

      {/* SG-331 T2: a plain select, no box — ink text with the native chevron. */}
      <select
        aria-label="Sort"
        value={sort}
        onChange={(event) => onSortChange(event.target.value as SortOption)}
        className="focus-ring"
        style={{ background: "transparent", border: "none", fontSize: 13, color: "hsl(var(--ink))", cursor: "pointer" }}
      >
        {(Object.keys(SORT_LABELS) as SortOption[]).map((option) => (
          <option key={option} value={option}>
            {SORT_LABELS[option]}
          </option>
        ))}
      </select>

      {/* SG-331 T4: two icon buttons in one small bordered group. */}
      <div
        role="group"
        aria-label="Density"
        style={{ display: "inline-flex", gap: 0, alignItems: "center", borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", borderRadius: 0 }}
      >
        {(Object.keys(DENSITY_LABELS) as Density[]).map((option) => {
          const active = option === density;
          const Icon = DENSITY_ICONS[option];
          return (
            <button
              key={option}
              type="button"
              aria-pressed={active}
              aria-label={DENSITY_LABELS[option]}
              title={DENSITY_LABELS[option]}
              onClick={() => onDensityChange(option)}
              className="focus-ring"
              style={{
                padding: "4px 8px",
                background: "transparent",
                border: "none",
                borderRadius: 0,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                color: active ? "hsl(var(--ink))" : "hsl(var(--ink-muted))",
              }}
            >
              <Icon size={16} aria-hidden="true" />
            </button>
          );
        })}
      </div>

      <div role="group" aria-label="Per row" style={{ display: "inline-flex", gap: 0, alignItems: "center" }}>
        <span aria-hidden="true" style={{ fontSize: 13, color: "hsl(var(--ink-muted))", marginRight: 4 }}>
          Per row
        </span>
        {(isNarrow ? PER_ROW_NARROW : PER_ROW_WIDE).map((option) => {
          const active = option === (isNarrow ? perRowNarrow : perRowWide);
          return (
            <button
              key={option}
              type="button"
              name={String(option)}
              aria-pressed={active}
              onClick={() =>
                isNarrow ? onPerRowNarrowChange?.(option) : onPerRowWideChange?.(option)
              }
              className="sg-paper-control focus-ring sg-per-row-button"
              style={{
                padding: "4px 10px",
                borderRadius: 0,
                fontSize: 13,
                fontWeight: active ? 600 : 400,
                cursor: "pointer",
                minHeight: 44,
                backgroundColor: active ? "hsl(var(--ink))" : "hsl(var(--paper))",
                color: active ? "hsl(var(--paper))" : "hsl(var(--ink))",
              }}
            >
              {option}
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
