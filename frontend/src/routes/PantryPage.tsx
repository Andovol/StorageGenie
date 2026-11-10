import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Package } from "lucide-react";
import { apiGet, decrementQuantity, fetchAnalyticsSummary, fetchExpiryStatus, markGone } from "../api/client";
import type { Asset, AssetListResponse, ExpiryStatusResponse } from "../api/types";
import { goneReasonLabel } from "../api/types";
import { useHouseholdContext } from "../hooks/HouseholdContext";
import { PageContainer } from "../components/shell/PageContainer";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import { thumbUrl } from "../components/catalog/ProductCard";
import { isCountedUnit } from "./AssetDetailPage";
import { PANTRY_CATEGORY, pantryModuleForCategory } from "../modules/temporaryCategoryModuleMap";

/**
 * SG-273 G1: the Pantry view — what you have and what to use soon.
 *
 * What enters: ACTIVE assets whose accepted classification is `food_beverages`
 * (read through the temporary `food_beverages → pantry` map). The list reads
 * `GET /v1/assets?category=food_beverages` (SG-273 read-only param) for the
 * food set and `GET /v1/plugins/expiry-tracker/status?category=food_beverages`
 * for the engine's own dates. Household scoping matches the catalog (Q26:
 * shared household pantry).
 *
 * Use soon reuses the engine's own window, never a new number: bucket in
 * {expired, this-week} i.e. days_remaining <= 7, which for food_beverages is
 * the URGENT tier window (FOOD_TIERS urgent 7; `bucket_for` this-week <= 7).
 * Each pack is its own tile (names are not product identity). Tiles reuse
 * SG-272's actions and wording (`-1`, `Used up`, `No count yet` /
 * `No amount yet`, `No date`).
 */

export const PANTRY_GRID_CSS = `
.pantry-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)); gap: 16px; width: 100%; max-width: 100%; }
.pantry-tile { border-radius: 0; }
.pantry-label { text-transform: uppercase; letter-spacing: 0.12em; }
`;

export function pantryUseSoonBucket(bucket: string): boolean {
  return bucket === "expired" || bucket === "this-week";
}

export function pantryQuantityText(asset: Asset): string {
  const counted = isCountedUnit(asset.unit);
  if (asset.quantity == null) return counted ? "No count yet" : "No amount yet";
  const unit = asset.unit ? ` ${asset.unit}` : "";
  return `${asset.quantity}${unit} left`;
}

export function pantryDateText(expiryDate: string | null): string {
  return expiryDate ?? "No date";
}

function PantryTile({
  asset,
  expiryDate,
  householdId,
  onOpen,
}: {
  asset: Asset;
  expiryDate: string | null;
  householdId: string;
  onOpen: (id: string) => void;
}) {
  const qc = useQueryClient();
  const [tileMessage, setTileMessage] = useState<string | null>(null);
  const [tileError, setTileError] = useState<string | null>(null);
  const counted = isCountedUnit(asset.unit);
  const qtyValue = asset.quantity ?? null;
  const evidenceId = asset.evidence_ids?.[0] ?? null;
  const media = evidenceId ? thumbUrl(evidenceId, householdId) : null;
  const [broken, setBroken] = useState(false);

  const decMut = useMutation({
    mutationFn: () => decrementQuantity(asset.id, householdId),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["pantry-assets"] });
      qc.invalidateQueries({ queryKey: ["pantry-expiry"] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      setTileError(null);
      setTileMessage(updated.quantity != null ? `Now ${updated.quantity} left.` : "Quantity changed.");
    },
    onError: (e: unknown) => {
      setTileError(e instanceof Error ? e.message : String(e));
      setTileMessage(null);
    },
  });
  const goneMut = useMutation({
    mutationFn: () => markGone(asset.id, householdId, "used_up"),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["pantry-assets"] });
      qc.invalidateQueries({ queryKey: ["pantry-expiry"] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      const label = goneReasonLabel(updated.gone_reason) ?? "gone";
      setTileMessage(`Marked as ${label.toLowerCase()}. Undo with Put back.`);
      setTileError(null);
    },
    onError: (e: unknown) => {
      setTileError(e instanceof Error ? e.message : String(e));
      setTileMessage(null);
    },
  });

  return (
    <article
      data-testid="pantry-tile"
      data-asset-id={asset.id}
      style={{
        backgroundColor: "hsl(var(--card))",
        borderColor: "hsl(var(--line))",
        borderStyle: "solid",
        borderWidth: 1,
        borderRadius: 0,
        padding: 12,
        display: "flex",
        flexDirection: "column",
        gap: 8,
        minWidth: 0,
        maxWidth: "100%",
      }}
    >
      <button
        type="button"
        onClick={() => onOpen(asset.id)}
        aria-label={`Open ${asset.display_name || "item"}`}
        style={{ background: "none", border: "none", padding: 0, cursor: "pointer", textAlign: "left" }}
      >
        <span
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            aspectRatio: "1 / 1",
            width: "100%",
            backgroundColor: "hsl(var(--paper))",
            overflow: "hidden",
          }}
        >
          {media && !broken ? (
            <img
              src={media}
              alt={asset.display_name || "Pantry item"}
              style={{ width: "100%", height: "100%", objectFit: "contain" }}
              onError={() => setBroken(true)}
            />
          ) : (
            <span style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              <Package aria-hidden="true" size={28} color="hsl(var(--ink-muted))" />
              <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>No photo yet</span>
            </span>
          )}
        </span>
        <span style={{ display: "block", fontWeight: 600, fontSize: 14, color: "hsl(var(--ink))", marginTop: 8, overflowWrap: "anywhere" }}>
          {asset.display_name || "Untitled item"}
        </span>
      </button>
      <span style={{ fontSize: 13, color: "hsl(var(--ink))" }}>{pantryQuantityText(asset)}</span>
      <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>{pantryDateText(expiryDate)}</span>
      <span style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        {counted ? (
          <button
            type="button"
            aria-label="Take off 1"
            onClick={() => decMut.mutate()}
            disabled={decMut.isPending || (qtyValue ?? 0) <= 0}
            className="focus-ring"
            style={{
              padding: "6px 12px",
              borderRadius: 0,
              borderStyle: "solid",
              borderWidth: 1,
              borderColor: "hsl(var(--line))",
              backgroundColor: "hsl(var(--card))",
              color: "hsl(var(--ink))",
              fontSize: 13,
              cursor: "pointer",
              opacity: decMut.isPending || (qtyValue ?? 0) <= 0 ? 0.5 : 1,
            }}
          >
            {decMut.isPending ? "…" : "−1"}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => onOpen(asset.id)}
            className="focus-ring"
            style={{
              padding: "6px 12px",
              borderRadius: 0,
              borderStyle: "solid",
              borderWidth: 1,
              borderColor: "hsl(var(--line))",
              backgroundColor: "hsl(var(--card))",
              color: "hsl(var(--ink))",
              fontSize: 13,
              cursor: "pointer",
            }}
          >
            Edit amount
          </button>
        )}
        <button
          type="button"
          onClick={() => goneMut.mutate()}
          disabled={goneMut.isPending}
          className="focus-ring"
          style={{
            padding: "6px 12px",
            borderRadius: 0,
            borderStyle: "solid",
            borderWidth: 1,
            borderColor: "hsl(var(--line))",
            backgroundColor: "hsl(var(--card))",
            color: "hsl(var(--ink))",
            fontSize: 13,
            cursor: "pointer",
          }}
        >
          {goneMut.isPending ? "…" : "Used up"}
        </button>
      </span>
      {tileMessage ? (
        <span role="status" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>{tileMessage}</span>
      ) : null}
      {tileError ? (
        <span role="alert" style={{ fontSize: 13, color: "hsl(var(--badge-failed-fg))" }}>{tileError}</span>
      ) : null}
    </article>
  );
}

export function PantryPage() {
  const { households, householdId } = useHouseholdContext();
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const effectiveHousehold = householdId || households?.[0]?.id || "";
  // The temporary map names the module; the view lists its category.
  const pantryCategory = pantryModuleForCategory(PANTRY_CATEGORY) ? PANTRY_CATEGORY : PANTRY_CATEGORY;

  const assetsQuery = useQuery<AssetListResponse>({
    queryKey: ["pantry-assets", effectiveHousehold],
    queryFn: () =>
      apiGet<AssetListResponse>("/v1/assets", {
        household_id: effectiveHousehold,
        category: pantryCategory,
        limit: "100",
      }),
    enabled: !!effectiveHousehold,
  });
  const expiryQuery = useQuery<ExpiryStatusResponse>({
    queryKey: ["pantry-expiry", effectiveHousehold],
    queryFn: () => fetchExpiryStatus(effectiveHousehold, pantryCategory),
    enabled: !!effectiveHousehold,
  });
  const summaryQuery = useQuery({
    queryKey: ["analytics-summary", effectiveHousehold],
    queryFn: () => fetchAnalyticsSummary(effectiveHousehold),
    enabled: !!effectiveHousehold,
  });

  const allFood = useMemo(() => assetsQuery.data?.items ?? [], [assetsQuery.data]);
  const liveFood = useMemo(() => allFood.filter((a) => a.status === "ACTIVE"), [allFood]);
  const expiryById = useMemo(() => {
    const map = new Map<string, string>();
    for (const row of expiryQuery.data?.rows ?? []) map.set(row.asset_id, row.expiry_date);
    return map;
  }, [expiryQuery.data]);
  const useSoonIds = useMemo(() => {
    const ids = new Set<string>();
    for (const row of expiryQuery.data?.rows ?? []) {
      if (pantryUseSoonBucket(row.bucket)) ids.add(row.asset_id);
    }
    return ids;
  }, [expiryQuery.data]);
  const useSoonAssets = useMemo(
    () => liveFood.filter((a) => useSoonIds.has(a.id)),
    [liveFood, useSoonIds]
  );
  const unsortedCount = summaryQuery.data?.categories?.uncategorized ?? 0;
  const selectedAsset = useMemo(
    () => liveFood.find((a) => a.id === selectedAssetId) ?? null,
    [liveFood, selectedAssetId]
  );

  const isEmpty = !!assetsQuery.data && liveFood.length === 0 && !assetsQuery.isLoading;

  return (
    <div style={{ backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink))", minHeight: "100vh" }}>
      <PageContainer className="text-foreground">
        <style data-testid="pantry-grid-style">{PANTRY_GRID_CSS}</style>
        <h1 className="page-header text-foreground">Pantry</h1>
        <div
          data-testid="pantry-count"
          className="pantry-label"
          style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", color: "hsl(var(--ink))" }}
        >
          {liveFood.length} ITEMS
        </div>
        <p style={{ fontSize: 13, color: "hsl(var(--ink-muted))", margin: "8px 0 0" }}>
          What you have and what to use soon. Each pack is its own tile.
        </p>
        {unsortedCount > 0 ? (
          <div data-testid="pantry-unsorted" style={{ marginTop: 12, fontSize: 13, color: "hsl(var(--ink))" }}>
            <span>Not sorted yet: {unsortedCount}. </span>
            <Link
              to={`/?household_id=${effectiveHousehold}`}
              className="focus-ring"
              style={{ color: "hsl(var(--ink))", fontSize: 13 }}
            >
              Sort them in the catalog
            </Link>
          </div>
        ) : null}
        {assetsQuery.isLoading ? <div style={{ fontSize: 13 }}>Loading pantry…</div> : null}
        {assetsQuery.isError ? (
          <div role="alert" style={{ fontSize: 13 }}>Could not load the pantry: {String(assetsQuery.error)}</div>
        ) : null}

        {!assetsQuery.isLoading && !assetsQuery.isError ? (
          <>
            <section aria-label="Use soon" style={{ marginTop: 20 }}>
              <h2 className="pantry-label" style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase" }}>
                USE SOON
              </h2>
              {useSoonAssets.length === 0 ? (
                <div style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>Nothing needs using soon.</div>
              ) : (
                <div className="pantry-grid" data-testid="pantry-use-soon-grid">
                  {useSoonAssets.map((asset) => (
                    <PantryTile
                      key={asset.id}
                      asset={asset}
                      expiryDate={expiryById.get(asset.id) ?? null}
                      householdId={effectiveHousehold}
                      onOpen={setSelectedAssetId}
                    />
                  ))}
                </div>
              )}
            </section>

            <section aria-label="Everything" style={{ marginTop: 20 }}>
              <h2 className="pantry-label" style={{ fontSize: 13, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase" }}>
                EVERYTHING
              </h2>
              {isEmpty ? (
                <div role="status" style={{ fontSize: 13 }}>
                  No food yet. Add an item from Capture and classify it as food to see it here.
                </div>
              ) : (
                <div className="pantry-grid" data-testid="pantry-grid">
                  {liveFood.map((asset) => (
                    <PantryTile
                      key={asset.id}
                      asset={asset}
                      expiryDate={expiryById.get(asset.id) ?? null}
                      householdId={effectiveHousehold}
                      onOpen={setSelectedAssetId}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        ) : null}
        {selectedAsset ? (
          <ItemInspectorDrawer
            asset={selectedAsset}
            householdId={effectiveHousehold}
            onClose={() => setSelectedAssetId(null)}
          />
        ) : null}
      </PageContainer>
    </div>
  );
}
