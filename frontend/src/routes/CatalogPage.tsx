import { useEffect, useMemo, useState } from "react";
import { useAssets, useHouseholds } from "../hooks/useAssets";
import { ProductGrid } from "../components/catalog/ProductGrid";
import { AppShell } from "../components/shell/AppShell";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import {
  CATEGORY_PILLS,
  SORT_LABELS,
  filterAndSortCatalog,
  type Density,
  type SortOption,
} from "../components/shell/CatalogToolbar";
import { assetToProductItem } from "../types/product";
import type { Asset } from "../api/types";

function useDebounced<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}

export function CatalogPage() {
  const { data: households } = useHouseholds();
  const [householdId, setHouseholdId] = useState(() => localStorage.getItem("household_id") || "");
  const [qRaw, setQRaw] = useState("");
  const q = useDebounced(qRaw, 200);
  const [category, setCategory] = useState("All");
  const [sort, setSort] = useState<SortOption>("recent");
  const [density, setDensity] = useState<Density>("grid");
  const [cursor, setCursor] = useState<string | undefined>(undefined);
  const [allItems, setAllItems] = useState<Asset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);

  const effectiveHousehold = useMemo(
    () => householdId || households?.[0]?.id || "",
    [householdId, households]
  );

  useEffect(() => {
    if (households && households.length && !householdId) {
      const first = households[0].id;
      setHouseholdId(first);
      localStorage.setItem("household_id", first);
    }
  }, [households, householdId]);

  // reset accumulation when the server-side query changes
  useEffect(() => {
    setAllItems([]);
    setCursor(undefined);
  }, [effectiveHousehold, q]);

  const { data, isLoading, isFetching } = useAssets(effectiveHousehold, q, cursor);

  useEffect(() => {
    if (data?.items) {
      if (!cursor) {
        setAllItems(data.items);
      } else {
        setAllItems((prev) => [...prev, ...data.items]);
      }
    }
  }, [data, cursor]);

  const displayed = allItems.length ? allItems : (data?.items || []);
  const nextCursor = data?.next_cursor;

  // The card/table rows hand back an id; the summary Asset for it is already in
  // the loaded page, which is all the drawer needs (it fetches the full record).
  const selectedAsset = useMemo(
    () => (selectedAssetId ? displayed.find((asset) => asset.id === selectedAssetId) ?? null : null),
    [displayed, selectedAssetId]
  );

  // Category/sort are client-side over the loaded page: the list API returns no
  // per-category counts and there is no aggregation endpoint yet. See the report.
  const visibleItems = useMemo(() => {
    const items = displayed.map((asset) => {
      const item = assetToProductItem(asset);
      const firstEvidence = asset.evidence?.[0];
      return firstEvidence ? { ...item, evidenceId: firstEvidence.id } : item;
    });
    return filterAndSortCatalog(items, { q: qRaw, category, sort });
  }, [displayed, qRaw, category, sort]);

  const activeFilters = useMemo(() => {
    const filters: string[] = [];
    if (qRaw.trim()) filters.push(`Search: ${qRaw.trim()}`);
    if (category !== "All") filters.push(category);
    if (sort !== "recent") filters.push(SORT_LABELS[sort]);
    return filters;
  }, [qRaw, category, sort]);

  const clearAll = () => {
    setQRaw("");
    setCategory("All");
    setSort("recent");
  };

  return (
    <AppShell
      loadedCount={displayed.length}
      searchValue={qRaw}
      onSearchChange={setQRaw}
      categories={CATEGORY_PILLS}
      activeCategory={category}
      onCategoryChange={setCategory}
      sort={sort}
      onSortChange={setSort}
      density={density}
      onDensityChange={setDensity}
      activeFilters={activeFilters}
      onClearAll={clearAll}
      householdId={effectiveHousehold}
      households={households || []}
      onHouseholdChange={(id) => {
        setHouseholdId(id);
        localStorage.setItem("household_id", id);
      }}
    >
      {isLoading && !data ? (
        <ProductGrid
          items={[]}
          density={density}
          householdId={effectiveHousehold}
          loading
          limit={20}
        />
      ) : (
        <>
          <ProductGrid
            items={visibleItems}
            density={density}
            householdId={effectiveHousehold}
            onSelect={setSelectedAssetId}
          />
          <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "center" }}>
            {nextCursor && (
              <button
                onClick={() => setCursor(nextCursor)}
                disabled={isFetching}
                className="bg-card text-foreground border-border focus-ring"
                style={{ padding: "8px 16px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
              >
                {isFetching ? "Loading..." : "Load more"}
              </button>
            )}
            {isFetching && <span className="text-muted-foreground" style={{ fontSize: 12 }}>Fetching...</span>}
          </div>
          {selectedAsset ? (
            <ItemInspectorDrawer
              asset={selectedAsset}
              householdId={effectiveHousehold}
              onClose={() => setSelectedAssetId(null)}
            />
          ) : null}
        </>
      )}
    </AppShell>
  );
}
