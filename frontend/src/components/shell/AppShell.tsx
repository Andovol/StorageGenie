import type { ReactNode } from "react";
import type { Household } from "../../api/types";
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
        />
      </div>
      <main style={{ padding: 24 }}>{children}</main>
    </div>
  );
}
