import type { ReactNode } from "react";
import type { SavedSearch } from "../../api/types";
import { AppHeader } from "./AppHeader";
import { CatalogToolbar, type CatalogStatusFilter, type Density, type SortOption } from "./CatalogToolbar";
import { PageContainer } from "./PageContainer";

type AppShellProps = {
  loadedCount: number;
  searchValue: string;
  onSearchChange: (value: string) => void;
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
  /** SG-330 R3: live items loaded; the Your-things heading sits above the toolbar. */
  titleCount?: number;
  /** SG-331 T3: gone items already counted by the loaded facets read (no new
      request); the title-row link shows it as Gone (n). */
  goneCount?: number;
  activeFilters: string[];
  onClearAll: () => void;
  savedSearches: SavedSearch[];
  selectedSavedSearchId: string;
  onSavedSearchSelect: (id: string) => void;
  onSavedSearchDelete: (id: string) => void;
  onSaveSearch: () => void;
  children: ReactNode;
};

export function AppShell({
  loadedCount,
  searchValue,
  onSearchChange,
  categories,
  activeCategory,
  onCategoryChange,
  statusFilter,
  onStatusFilterChange,
  sort,
  onSortChange,
  density,
  onDensityChange,
  perRowWide,
  onPerRowWideChange,
  perRowNarrow,
  onPerRowNarrowChange,
  isNarrow,
  titleCount,
  goneCount,
  activeFilters,
  onClearAll,
  savedSearches,
  selectedSavedSearchId,
  onSavedSearchSelect,
  onSavedSearchDelete,
  onSaveSearch,
  children,
}: AppShellProps) {
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink))" }}>
      <div style={{ position: "sticky", top: 0, zIndex: 10, backgroundColor: "hsl(var(--paper))" }}>
        <AppHeader loadedCount={loadedCount} searchValue={searchValue} onSearchChange={onSearchChange} />
        {typeof titleCount === "number" ? (
          <div style={{ padding: "16px 24px 4px", display: "flex", alignItems: "baseline", gap: 12 }}>
            <div style={{ flex: 1 }}>
              {/* SG-331 T3: the gone view retitles to Gone; the live view keeps Your things. */}
              <h1 className="sg-catalog-title">{statusFilter === "gone" ? "Gone" : "Your things"}</h1>
              <p style={{ margin: "4px 0 0", fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                {titleCount} {titleCount === 1 ? "thing" : "things"}
              </p>
            </div>
            {statusFilter === "gone" ? (
              <button
                type="button"
                onClick={() => onStatusFilterChange("live")}
                className="focus-ring"
                style={{ background: "none", border: "none", fontSize: 13, cursor: "pointer", textDecoration: "underline", color: "hsl(var(--ink))", whiteSpace: "nowrap" }}
              >
                Back to your things
              </button>
            ) : (
              <button
                type="button"
                onClick={() => onStatusFilterChange("gone")}
                className="focus-ring"
                style={{ background: "none", border: "none", fontSize: 13, cursor: "pointer", textDecoration: "underline", color: "hsl(var(--ink))", whiteSpace: "nowrap" }}
              >
                {goneCount != null ? `Gone (${goneCount})` : "Gone"}
              </button>
            )}
          </div>
        ) : null}
        <CatalogToolbar
          categories={categories}
          activeCategory={activeCategory}
          onCategoryChange={onCategoryChange}
          sort={sort}
          onSortChange={onSortChange}
          density={density}
          onDensityChange={onDensityChange}
          perRowWide={perRowWide}
          onPerRowWideChange={onPerRowWideChange}
          perRowNarrow={perRowNarrow}
          onPerRowNarrowChange={onPerRowNarrowChange}
          isNarrow={isNarrow}
          activeFilters={activeFilters}
          onClearAll={onClearAll}
          savedSearches={savedSearches}
          selectedSavedSearchId={selectedSavedSearchId}
          onSavedSearchSelect={onSavedSearchSelect}
          onSavedSearchDelete={onSavedSearchDelete}
          onSaveSearch={onSaveSearch}
        />
      </div>
      <PageContainer as="main">{children}</PageContainer>
    </div>
  );
}
