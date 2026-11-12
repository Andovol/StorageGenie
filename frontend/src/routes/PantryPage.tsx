import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Package } from "lucide-react";
import { apiGet, decrementQuantity, fetchAnalyticsSummary, fetchExpiryStatus, markGone, putBack } from "../api/client";
import type { Asset, AssetListResponse, ExpiryStatusResponse, ExpiryStatusRow } from "../api/types";
import { useHouseholdContext } from "../hooks/HouseholdContext";
import { PageContainer } from "../components/shell/PageContainer";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import { thumbUrl } from "../components/catalog/ProductCard";
import { isCountedUnit } from "./AssetDetailPage";
import { quantityLeftText } from "../lib/quantityText";
import { invalidateAssetViews } from "../lib/invalidateAssetViews";
import { PANTRY_CATEGORY, pantryModuleForCategory } from "../modules/temporaryCategoryModuleMap";

/**
 * SG-273 G1: the Pantry view — what you have and what to use soon.
 *
 * What enters: ACTIVE assets whose accepted classification is `food_beverages`
 * (read through the temporary `food_beverages → pantry` map). The list reads
 * `GET /v1/assets?category=food_beverages` for the food set and
 * `GET /v1/plugins/expiry-tracker/status?category=food_beverages` for the
 * engine's own dates. Household scoping matches the catalog (Q26).
 *
 * Use soon reuses the engine's own window: bucket in {expired, this-week}.
 *
 * SG-300 G1: the time left comes from the engine's `days_remaining` (never a
 * second date calculation); every list sorts by urgency (most overdue first,
 * then soonest, dateless last, then by name); the tiles carry no card box.
 */

// SG-300 G1 line 5: two columns at 375 px (each track >= 150 px, or half the
// width less the gap when that is narrower), as many as fit above that.
export const PANTRY_GRID_CSS = `
.pantry-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(150px, calc(50% - 8px)), 1fr)); gap: 16px; width: 100%; max-width: 100%; }
.pantry-label { text-transform: uppercase; letter-spacing: 0.12em; }
`;

const NOTICE_MS = 6000;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const ACTION_STYLE: CSSProperties = {
  flex: "1 1 0",
  minWidth: 0,
  minHeight: 40,
  padding: "0 6px",
  borderRadius: 0,
  borderStyle: "solid",
  borderWidth: 1,
  borderColor: "hsl(var(--line))",
  backgroundColor: "hsl(var(--card))",
  color: "hsl(var(--ink))",
  fontSize: 13,
  whiteSpace: "nowrap",
  cursor: "pointer",
};

export function pantryUseSoonBucket(bucket: string): boolean {
  return bucket === "expired" || bucket === "this-week";
}

/**
 * SG-300 G1 line 2: the time left, from the engine's days remaining.
 * 0 is "Use today"; past days read "Expired …"; a date more than 14 days out
 * reads "Use by 18 Nov" (with the year only when it is not `todayYear`).
 */
export function pantryTimeLeftText(
  days: number | null | undefined,
  expiryDate: string | null | undefined,
  todayYear: number
): string {
  if (days == null || !expiryDate) return "No date";
  if (days < 0) return days === -1 ? "Expired yesterday" : `Expired ${-days} days ago`;
  if (days === 0) return "Use today";
  if (days === 1) return "Use by tomorrow";
  if (days <= 14) return `Use in ${days} days`;
  const [year, month, day] = expiryDate.split("-").map(Number);
  const short = `${day} ${MONTHS[month - 1]}`;
  return `Use by ${year === todayYear ? short : `${short} ${year}`}`;
}

/**
 * SG-300 G1 line 1: one order for every list. Most overdue first (smallest
 * days remaining), then soonest; dateless items last; ties by name.
 */
export function sortPantryItems(items: Asset[], rows: Map<string, ExpiryStatusRow>): Asset[] {
  return [...items].sort((a, b) => {
    const da = rows.get(a.id)?.days_remaining ?? null;
    const db = rows.get(b.id)?.days_remaining ?? null;
    if (da == null && db != null) return 1;
    if (da != null && db == null) return -1;
    if (da != null && db != null && da !== db) return da - db;
    return (a.display_name ?? "").localeCompare(b.display_name ?? "");
  });
}

function PantryTile({
  asset,
  row,
  householdId,
  todayYear,
  onOpen,
  onUsedUp,
}: {
  asset: Asset;
  row: ExpiryStatusRow | undefined;
  householdId: string;
  todayYear: number;
  onOpen: (id: string) => void;
  onUsedUp: (asset: Asset) => void;
}) {
  const qc = useQueryClient();
  const [tileError, setTileError] = useState<string | null>(null);
  const [broken, setBroken] = useState(false);
  const counted = isCountedUnit(asset.unit);
  const qtyValue = asset.quantity ?? null;
  const evidenceId = asset.evidence_ids?.[0] ?? null;
  const media = evidenceId ? thumbUrl(evidenceId, householdId) : null;
  const days = row?.days_remaining ?? null;
  const expired = days != null && days < 0;
  const accent = days != null && days <= 2;
  const timeText = pantryTimeLeftText(days, row?.expiry_date ?? null, todayYear);

  const decMut = useMutation({
    mutationFn: () => decrementQuantity(asset.id, householdId),
    onSuccess: () => {
      invalidateAssetViews(qc, asset.id);
      setTileError(null);
    },
    onError: (e: unknown) => setTileError(e instanceof Error ? e.message : String(e)),
  });
  const goneMut = useMutation({
    mutationFn: () => markGone(asset.id, householdId, "used_up"),
    onSuccess: () => {
      invalidateAssetViews(qc, asset.id);
      setTileError(null);
      onUsedUp(asset);
    },
    onError: (e: unknown) => setTileError(e instanceof Error ? e.message : String(e)),
  });

  return (
    <article
      data-testid="pantry-tile"
      data-asset-id={asset.id}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 6,
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
      {expired ? (
        <span
          data-testid="pantry-expired"
          className="pantry-label"
          style={{ fontSize: 13, fontWeight: 700, color: "hsl(var(--link))" }}
        >
          EXPIRED
        </span>
      ) : null}
      <span
        data-testid="pantry-time-left"
        data-accent={accent ? "true" : "false"}
        style={{ fontSize: 13, color: accent ? "hsl(var(--link))" : "hsl(var(--ink-muted))" }}
      >
        {timeText}
      </span>
      <span data-testid="pantry-quantity" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>
        {quantityLeftText(qtyValue, asset.unit, counted)}
      </span>
      <span style={{ marginTop: "auto", paddingTop: 6, display: "flex", gap: 8 }}>
        {counted ? (
          <button
            type="button"
            aria-label="Take off 1"
            onClick={() => decMut.mutate()}
            disabled={decMut.isPending || (qtyValue ?? 0) <= 0}
            className="focus-ring"
            style={{ ...ACTION_STYLE, opacity: decMut.isPending || (qtyValue ?? 0) <= 0 ? 0.5 : 1 }}
          >
            {decMut.isPending ? "…" : "−1"}
          </button>
        ) : (
          <button type="button" onClick={() => onOpen(asset.id)} className="focus-ring" style={ACTION_STYLE}>
            Edit
          </button>
        )}
        <button
          type="button"
          onClick={() => goneMut.mutate()}
          disabled={goneMut.isPending}
          className="focus-ring"
          style={ACTION_STYLE}
        >
          {goneMut.isPending ? "…" : "Use it up"}
        </button>
      </span>
      {tileError ? (
        <span role="alert" style={{ fontSize: 13, color: "hsl(var(--badge-failed-fg))" }}>{tileError}</span>
      ) : null}
    </article>
  );
}

export function PantryPage() {
  const qc = useQueryClient();
  const { households, householdId } = useHouseholdContext();
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ assetId: string; name: string } | null>(null);
  const [noticeError, setNoticeError] = useState<string | null>(null);
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

  // SG-300 G1 line 8: one notice at a time, gone after about six seconds.
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => {
      setNotice(null);
      setNoticeError(null);
    }, NOTICE_MS);
    return () => clearTimeout(timer);
  }, [notice]);

  const putBackMut = useMutation({
    mutationFn: (assetId: string) => putBack(assetId, effectiveHousehold),
    onSuccess: (_data, assetId) => {
      invalidateAssetViews(qc, assetId);
      setNotice(null);
      setNoticeError(null);
    },
    onError: (e: unknown) => setNoticeError(e instanceof Error ? e.message : String(e)),
  });

  const allFood = useMemo(() => assetsQuery.data?.items ?? [], [assetsQuery.data]);
  const liveFood = useMemo(() => allFood.filter((a) => a.status === "ACTIVE"), [allFood]);
  const rowById = useMemo(() => {
    const map = new Map<string, ExpiryStatusRow>();
    for (const row of expiryQuery.data?.rows ?? []) map.set(row.asset_id, row);
    return map;
  }, [expiryQuery.data]);
  const todayYear = Number((expiryQuery.data?.as_of ?? "").slice(0, 4)) || new Date().getFullYear();
  const useSoonAssets = useMemo(
    () =>
      sortPantryItems(
        liveFood.filter((a) => {
          const row = rowById.get(a.id);
          return !!row && pantryUseSoonBucket(row.bucket);
        }),
        rowById
      ),
    [liveFood, rowById]
  );
  const everything = useMemo(() => sortPantryItems(liveFood, rowById), [liveFood, rowById]);
  const unsortedCount = summaryQuery.data?.categories?.uncategorized ?? 0;
  const selectedAsset = useMemo(
    () => liveFood.find((a) => a.id === selectedAssetId) ?? null,
    [liveFood, selectedAssetId]
  );

  const isEmpty = !!assetsQuery.data && liveFood.length === 0 && !assetsQuery.isLoading;

  return (
    <div style={{ color: "hsl(var(--ink))", minHeight: "100vh" }}>
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
          What you have, and what to use first.
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
                      row={rowById.get(asset.id)}
                      householdId={effectiveHousehold}
                      todayYear={todayYear}
                      onOpen={setSelectedAssetId}
                      onUsedUp={(a) => {
                        setNoticeError(null);
                        setNotice({ assetId: a.id, name: a.display_name || "Item" });
                      }}
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
                  No food yet. Add an item from{" "}
                  <Link
                    to="/capture"
                    className="focus-ring"
                    style={{ color: "hsl(var(--link))", textDecoration: "underline" }}
                  >
                    Capture
                  </Link>{" "}
                  and classify it as food to see it here.
                </div>
              ) : (
                <div className="pantry-grid" data-testid="pantry-grid">
                  {everything.map((asset) => (
                    <PantryTile
                      key={asset.id}
                      asset={asset}
                      row={rowById.get(asset.id)}
                      householdId={effectiveHousehold}
                      todayYear={todayYear}
                      onOpen={setSelectedAssetId}
                      onUsedUp={(a) => {
                        setNoticeError(null);
                        setNotice({ assetId: a.id, name: a.display_name || "Item" });
                      }}
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
      {notice ? (
        <div
          data-testid="pantry-notice"
          role="status"
          style={{
            position: "fixed",
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 50,
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "center",
            gap: 6,
            padding: "12px 16px",
            backgroundColor: "hsl(var(--card))",
            borderTop: "1px solid hsl(var(--line))",
            fontSize: 13,
            color: "hsl(var(--ink))",
          }}
        >
          <span>{notice.name} used up · </span>
          <button
            type="button"
            onClick={() => putBackMut.mutate(notice.assetId)}
            disabled={putBackMut.isPending}
            className="focus-ring"
            style={{ ...ACTION_STYLE, flex: "0 0 auto", padding: "0 12px" }}
          >
            {putBackMut.isPending ? "…" : "Put back"}
          </button>
          {noticeError ? <span role="alert">{noticeError}</span> : null}
        </div>
      ) : null}
    </div>
  );
}
