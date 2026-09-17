import { useEffect, useMemo, useState } from "react";
import {
  useAssets,
  useDeleteSavedSearch,
  useFacets,
  useHouseholds,
  useSaveSearch,
  useSavedSearches,
} from "../hooks/useAssets";
import { ProductGrid } from "../components/catalog/ProductGrid";
import { AppShell } from "../components/shell/AppShell";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import {
  CATEGORY_ALL,
  SORT_LABELS,
  sortCatalog,
  type Density,
  type SortOption,
} from "../components/shell/CatalogToolbar";
import { assetToProductItem } from "../types/product";
import type { Asset, SavedSearchQuery } from "../api/types";

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
  const [category, setCategory] = useState<string>(CATEGORY_ALL);
  const [sort, setSort] = useState<SortOption>("recent");
  const [density, setDensity] = useState<Density>("grid");
  const [cursor, setCursor] = useState<string | undefined>(undefined);
  const [allItems, setAllItems] = useState<Asset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [selectedSavedSearchId, setSelectedSavedSearchId] = useState("");

  const effectiveHousehold = useMemo(
    () => householdId || households?.[0]?.id || "",
    [householdId, households]
  );

  const { data: savedSearchesData } = useSavedSearches(effectiveHousehold);
  const savedSearches = useMemo(() => savedSearchesData?.items ?? [], [savedSearchesData]);
  const saveSearch = useSaveSearch(effectiveHousehold);
  const deleteSavedSearch = useDeleteSavedSearch(effectiveHousehold);

  // Saved searches are per-household: switching households drops the selection
  // so the dropdown shows THAT household's set (SG-068 G2).
  useEffect(() => {
    setSelectedSavedSearchId("");
  }, [effectiveHousehold]);

  useEffect(() => {
    if (households && households.length && !householdId) {
      const first = households[0].id;
      setHouseholdId(first);
      localStorage.setItem("household_id", first);
    }
  }, [households, householdId]);

  // Facet counts share the list base (household + debounced `q`). The active
  // category is deliberately NOT sent, so every pill keeps showing the count
  // reachable by selecting it (SG-064 G1: counts omit their own dimension).
  const { data: facets } = useFacets(effectiveHousehold, q);
  const categoryCounts = useMemo(() => facets?.asset_type ?? {}, [facets]);

  // Pills come from the real `asset_type` population, not the static DQ1 list;
  // each renders `Label (N)`. "All" shows the unfiltered-with-q total.
  const categoryLabels = useMemo(() => {
    const total = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
    const labels = new Map<string, string>();
    labels.set(CATEGORY_ALL, `${CATEGORY_ALL} (${total})`);
    for (const key of Object.keys(categoryCounts)) {
      labels.set(key, `${key} (${categoryCounts[key]})`);
    }
    return labels;
  }, [categoryCounts]);

  const categories = useMemo(() => Array.from(categoryLabels.values()), [categoryLabels]);
  const activeCategoryLabel = categoryLabels.get(category) ?? category;

  const handleCategoryChange = (label: string) => {
    for (const [key, value] of categoryLabels) {
      if (value === label) {
        setCategory(key);
        return;
      }
    }
    setCategory(label);
  };

  // reset accumulation when any server-side query dimension changes
  useEffect(() => {
    setAllItems([]);
    setCursor(undefined);
  }, [effectiveHousehold, q, category]);

  const { data, isLoading, isFetching } = useAssets(
    effectiveHousehold,
    q,
    cursor,
    category === CATEGORY_ALL ? undefined : category
  );

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

  // Server owns `q` (FTS MATCH on `display_name`) and the category filter
  // (`asset_type`); this only orders the loaded page. The evidence id the card
  // thumbnail reads comes from the list serializer's `evidence_ids` (SG-064 G3).
  const visibleItems = useMemo(() => {
    const items = displayed.map((asset) => {
      const item = assetToProductItem(asset);
      const firstEvidenceId = asset.evidence_ids?.[0];
      return firstEvidenceId ? { ...item, evidenceId: firstEvidenceId } : item;
    });
    return sortCatalog(items, sort);
  }, [displayed, sort]);

  const activeFilters = useMemo(() => {
    const filters: string[] = [];
    if (qRaw.trim()) filters.push(`Search: ${qRaw.trim()}`);
    if (category !== CATEGORY_ALL) filters.push(category);
    if (sort !== "recent") filters.push(SORT_LABELS[sort]);
    return filters;
  }, [qRaw, category, sort]);

  const clearAll = () => {
    setQRaw("");
    setCategory(CATEGORY_ALL);
    setSort("recent");
    setSelectedSavedSearchId("");
  };

  const handleSaveSearch = () => {
    const name = window.prompt("Name this saved search");
    if (!name || !name.trim()) return;
    const query: SavedSearchQuery = {};
    if (qRaw.trim()) query.q = qRaw.trim();
    if (category !== CATEGORY_ALL) query.asset_type = category;
    saveSearch.mutate({ name: name.trim(), query });
  };

  // Applying a saved search sets the SAME state the pills/search box use, so
  // the existing reset effect (and the single `GET /v1/assets` path) re-queries
  // -- no second query language.
  const handleSavedSearchSelect = (id: string) => {
    setSelectedSavedSearchId(id);
    const selected = savedSearches.find((saved) => saved.id === id);
    if (!selected) return;
    setQRaw(selected.query.q ?? "");
    setCategory(selected.query.asset_type ?? CATEGORY_ALL);
  };

  const handleSavedSearchDelete = (id: string) => {
    deleteSavedSearch.mutate(id);
    if (selectedSavedSearchId === id) setSelectedSavedSearchId("");
  };

  return (
    <AppShell
      loadedCount={displayed.length}
      searchValue={qRaw}
      onSearchChange={setQRaw}
      categories={categories}
      activeCategory={activeCategoryLabel}
      onCategoryChange={handleCategoryChange}
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
      savedSearches={savedSearches}
      selectedSavedSearchId={selectedSavedSearchId}
      onSavedSearchSelect={handleSavedSearchSelect}
      onSavedSearchDelete={handleSavedSearchDelete}
      onSaveSearch={handleSaveSearch}
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
