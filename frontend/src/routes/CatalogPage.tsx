import { useEffect, useMemo, useState } from "react";
import { useAssets, useHouseholds } from "../hooks/useAssets";
import { AssetCard } from "../components/AssetCard";
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
  const [assetType, setAssetType] = useState("");
  const [status, setStatus] = useState("");
  const [cursor, setCursor] = useState<string | undefined>(undefined);
  const [allItems, setAllItems] = useState<Asset[]>([]);

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

  // reset accumulation when filters change
  useEffect(() => {
    setAllItems([]);
    setCursor(undefined);
  }, [effectiveHousehold, q, assetType, status]);

  const { data, isLoading, isFetching } = useAssets(effectiveHousehold, q, cursor, assetType || undefined, status || undefined);

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

  return (
    <div style={{ padding: 24 }}>
      <h1>Catalog</h1>
      <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
        <select
          value={effectiveHousehold}
          onChange={(e) => {
            setHouseholdId(e.target.value);
            localStorage.setItem("household_id", e.target.value);
          }}
          style={{ padding: 8, borderRadius: 6, border: "1px solid #d1d5db" }}
        >
          {(households || []).map((h) => (
            <option key={h.id} value={h.id}>
              {h.name}
            </option>
          ))}
          {(!households || households.length === 0) && <option value="">No households</option>}
        </select>
        <input
          placeholder="Search..."
          value={qRaw}
          onChange={(e) => setQRaw(e.target.value)}
          style={{ padding: 8, border: "1px solid #d1d5db", borderRadius: 6, flex: 1, minWidth: 160 }}
        />
        <select value={assetType} onChange={(e) => setAssetType(e.target.value)} style={{ padding: 8, borderRadius: 6 }}>
          <option value="">All types</option>
          <option value="equipment">equipment</option>
          <option value="product">product</option>
          <option value="component">component</option>
          <option value="consumable">consumable</option>
          <option value="container">container</option>
          <option value="document">document</option>
          <option value="collection">collection</option>
          <option value="unknown">unknown</option>
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)} style={{ padding: 8, borderRadius: 6 }}>
          <option value="">All status</option>
          <option value="ACTIVE">ACTIVE</option>
          <option value="DRAFT">DRAFT</option>
          <option value="ARCHIVED">ARCHIVED</option>
          <option value="PENDING_REVIEW">PENDING_REVIEW</option>
        </select>
      </div>

      {isLoading && !data ? (
        <div>Loading...</div>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
            {displayed.map((a) => (
              <AssetCard key={a.id} asset={a} householdId={effectiveHousehold} />
            ))}
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "center" }}>
            {nextCursor && (
              <button
                onClick={() => setCursor(nextCursor)}
                disabled={isFetching}
                style={{ padding: "8px 16px", borderRadius: 6, border: "1px solid #d1d5db", background: "white", cursor: "pointer" }}
              >
                {isFetching ? "Loading..." : "Load more"}
              </button>
            )}
            {isFetching && <span style={{ fontSize: 12, color: "#6b7280" }}>Fetching...</span>}
          </div>
          {displayed.length === 0 && <div style={{ color: "#6b7280", marginTop: 16 }}>No assets yet — create one via Capture.</div>}
        </>
      )}
    </div>
  );
}
