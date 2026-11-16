import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  useAssets,
  useDeleteSavedSearch,
  useFacets,
  useSaveSearch,
  useSavedSearches,
} from "../hooks/useAssets";
import { fetchExpiryStatus, putBack } from "../api/client";
import { useHouseholdContext } from "../hooks/HouseholdContext";
import { ProductGrid } from "../components/catalog/ProductGrid";
import { AppShell } from "../components/shell/AppShell";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import {
  CATEGORY_ALL,
  SORT_LABELS,
  sortCatalog,
  type CatalogStatusFilter,
  type Density,
  type SortOption,
} from "../components/shell/CatalogToolbar";
import { goneReasonLabel } from "../api/types";
import { assetToProductItem } from "../types/product";
import { labelAssetType } from "../lib/labels";
import type { Asset, ExpiryStatusResponse, SavedSearchQuery } from "../api/types";

function useDebounced<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}

// SG-328 (owner 2026-11-16): the catalog always opens in Standard Grid. The
// SG-212 / D-21 width rule is retired: no measure, no layout effect, no stored
// choice. The density toggle stays one click away.
//
// SG-330 R4: items per row is a setting, remembered per device. Wide screens
// offer 4 / 5 / 6 (default 5), narrow screens (< 640 px) offer 3 / 4
// (default 3). The choice is read and written inside try/catch so a denied
// store falls back to the default instead of breaking the page.
const PER_ROW_WIDE_KEY = "sg-per-row-wide";
const PER_ROW_NARROW_KEY = "sg-per-row-narrow";

function readPerRow(key: string, valid: readonly number[], fallback: number): number {
  try {
    const n = Number(window.localStorage.getItem(key));
    if (valid.includes(n)) return n;
  } catch {
    /* storage denied: fall through to the default */
  }
  return fallback;
}

function useIsNarrow(): boolean {
  const [narrow, setNarrow] = useState(
    () => typeof window !== "undefined" && window.innerWidth < 640
  );
  useEffect(() => {
    const onResize = () => setNarrow(window.innerWidth < 640);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return narrow;
}

export function CatalogPage() {
  // SG-196 G1: household selection now comes from the shared context; the
  // effective-household derivation shape is unchanged.
  const { households, householdId } = useHouseholdContext();
  const [qRaw, setQRaw] = useState("");
  const q = useDebounced(qRaw, 200);
  const [category, setCategory] = useState<string>(CATEGORY_ALL);
  // SG-272 G2 (F13): the Gone view asks the list for `status=ARCHIVED` and
  // shows each gone row's reason with its Put back. Live is the default.
  const [statusFilter, setStatusFilter] = useState<CatalogStatusFilter>("live");
  const [sort, setSort] = useState<SortOption>("recent");
  const [density, setDensity] = useState<Density>("grid");
  const [cursor, setCursor] = useState<string | undefined>(undefined);
  const isNarrow = useIsNarrow();
  const [perRowWide, setPerRowWide] = useState(() => readPerRow(PER_ROW_WIDE_KEY, [4, 5, 6], 5));
  const [perRowNarrow, setPerRowNarrow] = useState(() => readPerRow(PER_ROW_NARROW_KEY, [3, 4], 3));
  const changePerRowWide = (n: number) => {
    setPerRowWide(n);
    try {
      window.localStorage.setItem(PER_ROW_WIDE_KEY, String(n));
    } catch {
      /* storage denied: the page keeps the in-memory choice */
    }
  };
  const changePerRowNarrow = (n: number) => {
    setPerRowNarrow(n);
    try {
      window.localStorage.setItem(PER_ROW_NARROW_KEY, String(n));
    } catch {
      /* storage denied: the page keeps the in-memory choice */
    }
  };

  const [allItems, setAllItems] = useState<Asset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [selectedSavedSearchId, setSelectedSavedSearchId] = useState("");
  const qc = useQueryClient();
  const [goneNotice, setGoneNotice] = useState<string | null>(null);
  const [goneError, setGoneError] = useState<string | null>(null);

  const effectiveHousehold = useMemo(
    () => householdId || households?.[0]?.id || "",
    [householdId, households]
  );

  const putBackMut = useMutation({
    mutationFn: (assetId: string) => putBack(assetId, effectiveHousehold),
    onSuccess: (restored) => {
      setGoneNotice(`“${restored.display_name || "Item"}” is back in your catalog.`);
      setGoneError(null);
      qc.invalidateQueries({ queryKey: ["assets"] });
    },
    onError: (e: unknown) => {
      setGoneError(e instanceof Error ? e.message : String(e));
      setGoneNotice(null);
    },
  });

  const { data: savedSearchesData, isError: savedSearchesIsError, error: savedSearchesError } =
    useSavedSearches(effectiveHousehold);
  const savedSearches = useMemo(() => savedSearchesData?.items ?? [], [savedSearchesData]);
  const saveSearch = useSaveSearch(effectiveHousehold);
  const deleteSavedSearch = useDeleteSavedSearch(effectiveHousehold);

  // Saved searches are per-household: switching households drops the selection
  // so the dropdown shows THAT household's set (SG-068 G2).
  useEffect(() => {
    setSelectedSavedSearchId("");
  }, [effectiveHousehold]);

  // Facet counts share the list base (household + debounced `q`). The active
  // category is deliberately NOT sent, so every pill keeps showing the count
  // reachable by selecting it (SG-064 G1: counts omit their own dimension).
  const { data: facets, isError: facetsIsError, error: facetsError } = useFacets(
    effectiveHousehold,
    q
  );
  const categoryCounts = useMemo(() => facets?.asset_type ?? {}, [facets]);

  // Pills come from the real `asset_type` population and speak the same
  // vocabulary the cards show (`labelAssetType`, SG-307 plain words): the raw
  // `unknown` facet key renders as `Uncategorized`, while selecting that pill
  // still sends the REAL server filter `asset_type=unknown`.
  //
  // SG-118 G3: one pill per RAW facet key, never merged across keys. The server
  // filter is single-valued (`asset_type=<key>`), so a pill that merged two raw
  // keys would show a count it could not filter — a lie. Keys are sorted for a
  // deterministic pill order; if two raw keys render the same display label
  // (e.g. the `unknown` alias and a literal `Uncategorized`), the later one is
  // disambiguated with its raw key so every label maps to exactly one filter.
  const categoryOptions = useMemo(() => {
    const total = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
    const options: { display: string; key: string; label: string }[] = [
      { display: CATEGORY_ALL, key: CATEGORY_ALL, label: `${CATEGORY_ALL} (${total})` },
    ];
    const usedLabels = new Set<string>([options[0].label]);
    for (const key of Object.keys(categoryCounts).sort()) {
      const display = labelAssetType(key);
      let label = `${display} (${categoryCounts[key]})`;
      if (usedLabels.has(label)) label = `${display} · ${key} (${categoryCounts[key]})`;
      usedLabels.add(label);
      options.push({ display, key, label });
    }
    return options;
  }, [categoryCounts]);

  const categories = useMemo(() => categoryOptions.map((option) => option.label), [categoryOptions]);
  const activeCategoryLabel =
    categoryOptions.find((option) => option.key === category)?.label ?? category;

  const handleCategoryChange = (label: string) => {
    const option = categoryOptions.find((entry) => entry.label === label);
    setCategory(option ? option.key : label);
  };

  // reset accumulation when any server-side query dimension changes
  useEffect(() => {
    setAllItems([]);
    setCursor(undefined);
  }, [effectiveHousehold, q, category, statusFilter]);

  const { data, isLoading, isFetching, isError, error } = useAssets(
    effectiveHousehold,
    q,
    cursor,
    category === CATEGORY_ALL ? undefined : category,
    statusFilter === "gone" ? "ARCHIVED" : undefined
  );

  // SG-325 P8: the use-by date for every module's items. The status read with
  // no category carries the whole household (fetchExpiryStatus drops the empty
  // category param), joined here by asset id — the same join the Pantry uses.
  const expiryQuery = useQuery<ExpiryStatusResponse>({
    queryKey: ["expiry-status", effectiveHousehold],
    queryFn: () => fetchExpiryStatus(effectiveHousehold),
    enabled: !!effectiveHousehold,
  });
  // SG-330 R5: the join carries the countdown too, the same way as the date.
  const useByById = useMemo(() => {
    const map = new Map<string, { date: string; days: number }>();
    for (const row of expiryQuery.data?.rows ?? [])
      map.set(row.asset_id, { date: row.expiry_date, days: row.days_remaining });
    return map;
  }, [expiryQuery.data]);

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
      const withMedia = firstEvidenceId ? { ...item, evidenceId: firstEvidenceId } : item;
      const dated = useByById.get(asset.id);
      return { ...withMedia, useBy: dated?.date ?? null, daysRemaining: dated?.days ?? null };
    });
    return sortCatalog(items, sort);
  }, [displayed, sort, useByById]);

  const activeFilters = useMemo(() => {
    const filters: string[] = [];
    if (qRaw.trim()) filters.push(`Search: ${qRaw.trim()}`);
    if (category !== CATEGORY_ALL) filters.push(labelAssetType(category));
    if (statusFilter === "gone") filters.push("Gone");
    if (sort !== "recent") filters.push(SORT_LABELS[sort]);
    return filters;
  }, [qRaw, category, statusFilter, sort]);

  const clearAll = () => {
    setQRaw("");
    setCategory(CATEGORY_ALL);
    setStatusFilter("live");
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
      statusFilter={statusFilter}
      onStatusFilterChange={setStatusFilter}
      sort={sort}
      onSortChange={setSort}
      density={density}
      onDensityChange={setDensity}
      titleCount={displayed.length}
      perRowWide={perRowWide}
      onPerRowWideChange={changePerRowWide}
      perRowNarrow={perRowNarrow}
      onPerRowNarrowChange={changePerRowNarrow}
      isNarrow={isNarrow}
      activeFilters={activeFilters}
      onClearAll={clearAll}
      savedSearches={savedSearches}
      selectedSavedSearchId={selectedSavedSearchId}
      onSavedSearchSelect={handleSavedSearchSelect}
      onSavedSearchDelete={handleSavedSearchDelete}
      onSaveSearch={handleSaveSearch}
    >
      <div data-testid="catalog-content-column">
        {facetsIsError && (
          <div role="alert">Could not load catalog facets: {String(facetsError)}</div>
        )}
        {savedSearchesIsError && (
          <div role="alert">Could not load saved searches: {String(savedSearchesError)}</div>
        )}
        {isError && (
          <div role="alert">Could not load the asset list: {String(error)}</div>
        )}
        {isLoading && !data ? (
          <ProductGrid
            items={[]}
            density={density}
            householdId={effectiveHousehold}
            loading
            limit={20}
            perRow={isNarrow ? perRowNarrow : perRowWide}
            narrow={isNarrow}
          />
        ) : (
          <>
            {statusFilter === "gone" ? (
              <section aria-label="Gone items" style={{ display: "grid", gap: 8 }}>
                {goneNotice && (
                  <div role="status" className="text-success" style={{ fontSize: 13 }}>{goneNotice}</div>
                )}
                {goneError && (
                  <div role="alert" className="text-danger" style={{ fontSize: 13 }}>{goneError}</div>
                )}
                {displayed.length === 0 && !isError && (
                  <div role="status" className="text-muted-foreground" style={{ fontSize: 13 }}>
                    Nothing is gone. Mark an item gone from its page and it will wait for you here.
                  </div>
                )}
                {displayed.map((gone) => {
                  const label = goneReasonLabel(gone.gone_reason);
                  return (
                    <div
                      key={gone.id}
                      style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", padding: 12, borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", borderRadius: 0, backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink))" }}
                    >
                      <Link
                        className="text-link focus-ring"
                        style={{ fontWeight: 600 }}
                        to={`/assets/${gone.id}?household_id=${effectiveHousehold}`}
                      >
                        {gone.display_name || "Unnamed item"}
                      </Link>
                      <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                        Gone{label ? ` — ${label.toLowerCase()}` : ""}
                      </span>
                      <button
                        type="button"
                        onClick={() => putBackMut.mutate(gone.id)}
                        disabled={putBackMut.isPending}
                        className="sg-paper-control focus-ring"
                        style={{ padding: "6px 12px", borderRadius: 0, cursor: "pointer", fontSize: 13 }}
                      >
                        {putBackMut.isPending ? "Putting back…" : "Put back"}
                      </button>
                    </div>
                  );
                })}
              </section>
            ) : (
            !(isError && displayed.length === 0) && (
              <>
                <ProductGrid
                    items={visibleItems}
                    density={density}
                    householdId={effectiveHousehold}
                    onSelect={setSelectedAssetId}
                    perRow={isNarrow ? perRowNarrow : perRowWide}
                    narrow={isNarrow}
                  />
                </>
              )
            )}
            <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "center" }}>
              {nextCursor && (
                <button
                  onClick={() => setCursor(nextCursor)}
                  disabled={isFetching}
                  className="sg-paper-control focus-ring"
                  style={{ padding: "8px 16px", borderRadius: 0, cursor: "pointer", fontSize: 13 }}
                >
                  {isFetching ? "Loading..." : "Load more"}
                </button>
              )}
              {isFetching && <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>Fetching...</span>}
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
      </div>
    </AppShell>
  );
}
