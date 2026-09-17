import type { ReactNode } from "react";
import type { Household, SavedSearch } from "../../api/types";
import { AppHeader } from "./AppHeader";
import { CatalogToolbar, type Density, type SortOption } from "./CatalogToolbar";

type AppShellProps = {
  loadedCount: number;
  searchValue: string;
  onSearchChange: (value: string) => void;
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
  sort,
  onSortChange,
  density,
  onDensityChange,
  activeFilters,
  onClearAll,
  householdId,
  households,
  onHouseholdChange,
  savedSearches,
  selectedSavedSearchId,
  onSavedSearchSelect,
  onSavedSearchDelete,
  onSaveSearch,
  children,
}: AppShellProps) {
  return (
    <div className="bg-background text-foreground" style={{ minHeight: "100vh" }}>
      <div className="bg-background" style={{ position: "sticky", top: 0, zIndex: 10 }}>
        <AppHeader loadedCount={loadedCount} searchValue={searchValue} onSearchChange={onSearchChange} />
        <CatalogToolbar
          categories={categories}
          activeCategory={activeCategory}
          onCategoryChange={onCategoryChange}
          sort={sort}
          onSortChange={onSortChange}
          density={density}
          onDensityChange={onDensityChange}
          activeFilters={activeFilters}
          onClearAll={onClearAll}
          householdId={householdId}
          households={households}
          onHouseholdChange={onHouseholdChange}
          savedSearches={savedSearches}
          selectedSavedSearchId={selectedSavedSearchId}
          onSavedSearchSelect={onSavedSearchSelect}
          onSavedSearchDelete={onSavedSearchDelete}
          onSaveSearch={onSaveSearch}
        />
      </div>
      <main style={{ padding: 24 }}>{children}</main>
    </div>
  );
}
