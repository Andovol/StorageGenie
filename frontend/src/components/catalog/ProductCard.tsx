import { memo, useState } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, Package } from "lucide-react";
import type { ProductItem } from "../../types/product";
import { formatUseByDate, labelAssetType } from "../../lib/labels";

/**
 * A catalog card item: the DQ1 `ProductItem` plus the media the grid renders.
 * `assetToProductItem` fills the ProductItem fields for live assets; the
 * cutout/scene URLs are mock-only until the S3-era image derivation lands.
 */
export type CatalogProduct = ProductItem & {
  cutoutUrl?: string;
  sceneUrl?: string;
  evidenceId?: string;
  /** SG-325 P8: the item's use-by date (ISO YYYY-MM-DD) joined from the
   * expiry status read; null when the item has no date. */
  useBy?: string | null;
};

/**
 * The live-asset thumbnail route, mirrors `AssetCard.tsx:9` and
 * `EvidenceGallery.tsx:17` (`/v1/evidence/{id}/thumb/{size}?household_id=`).
 */
export function thumbUrl(evidenceId: string, householdId: string, size = 256): string {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:8003";
  return `${base}/v1/evidence/${evidenceId}/thumb/${size}?household_id=${householdId}`;
}

export function cardMedia(item: CatalogProduct, householdId: string): string | null {
  if (item.cutoutUrl) return item.cutoutUrl;
  if (item.sceneUrl) return item.sceneUrl;
  if (item.evidenceId) return thumbUrl(item.evidenceId, householdId);
  return null;
}

/**
 * ⚡ Bolt Optimization: Memoize ProductCard to prevent re-rendering catalog grid items
 * when parent state changes (e.g. search input keystrokes before debounce, active filters,
 * or opening/closing the inspector drawer).
 * Expected Impact: Reduces catalog item re-renders by ~100% on search typing and drawer toggles.
 */
export const ProductCard = memo(function ProductCard({
  item,
  householdId,
  onSelect,
}: {
  item: CatalogProduct;
  householdId: string;
  onSelect?: (id: string) => void;
}) {
  const [broken, setBroken] = useState(false);
  const failed = item.status === "failed";
  const media = cardMedia(item, householdId);

  return (
    <Link
      to={`/assets/${item.id}?household_id=${householdId}`}
      data-testid="product-card"
      onClick={
        onSelect
          ? (event) => {
              event.preventDefault();
              onSelect(item.id);
            }
          : undefined
      }
      onKeyDown={
        onSelect
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelect(item.id);
              }
            }
          : undefined
      }
      className="product-card focus-ring"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        borderStyle: "solid",
        borderWidth: 1,
        borderColor: "hsl(var(--line))",
        borderRadius: 0,
        padding: 10,
        textDecoration: "none",
        color: "hsl(var(--ink))",
        backgroundColor: "hsl(var(--paper))",
      }}
    >
      <div
        data-testid="product-card-well"
        className={failed ? "border border-rose-500/30 border-danger" : ""}
        style={{
          position: "relative",
          aspectRatio: "1 / 1",
          borderRadius: 0,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "hsl(var(--paper))",
          ...(failed
            ? {
                borderStyle: "solid",
                borderWidth: 1,
              }
            : {}),
        }}
      >
        {media && !broken ? (
          <img
            src={media}
            alt={item.name}
            className="object-contain"
            style={{ width: "100%", height: "100%", objectFit: "contain" }}
            onError={() => setBroken(true)}
          />
        ) : null}
        {!failed && (!media || broken) ? (
          <Package
            data-testid="product-fallback-icon"
            aria-hidden="true"
            size={28}
            className="text-muted-foreground"
          />
        ) : null}
        {failed ? (
          <AlertTriangle
            data-testid="failed-warning"
            aria-hidden="true"
            size={28}
            className="text-danger"
          />
        ) : null}
        <span
          data-testid="use-by-date"
          style={{
            position: "absolute",
            top: 8,
            right: 8,
            borderStyle: "solid",
            borderWidth: 1,
            borderRadius: 0,
            padding: "2px 8px",
            fontSize: 13,
            fontWeight: 600,
            whiteSpace: "nowrap",
            borderColor: "hsl(var(--line))",
            backgroundColor: "hsl(var(--paper))",
            color: "hsl(var(--ink-muted))",
          }}
        >
          {formatUseByDate(item.useBy) || "No date"}
        </span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: 0 }}>
          <span
            title={item.name}
            style={{
              fontWeight: 600,
              fontSize: 14,
              color: "hsl(var(--ink))",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {item.name}
          </span>
          {failed ? (
            <AlertTriangle
              data-testid="title-error-icon"
              aria-hidden="true"
              size={14}
              className="text-danger"
              style={{ flexShrink: 0 }}
            />
          ) : null}
        </div>
        <span
          data-testid="product-category"
          style={{
            alignSelf: "flex-start",
            fontSize: 13,
            padding: "2px 8px",
            borderRadius: 0,
            borderStyle: "solid",
            borderWidth: 1,
            borderColor: "hsl(var(--line))",
            backgroundColor: "hsl(var(--paper))",
            color: "hsl(var(--ink-muted))",
            whiteSpace: "nowrap",
          }}
        >
          {labelAssetType(item.category)}
        </span>
        {item.metadata.primaryColors?.length ? (
          <div data-testid="color-dots" style={{ display: "flex", gap: 4 }}>
            {item.metadata.primaryColors.map((color) => (
            <span
              key={color}
              className="border-border"
              style={{
                width: 8,
                height: 8,
                borderRadius: 0,
                backgroundColor: color,
                borderWidth: 1,
                borderStyle: "solid",
              }}
            />
            ))}
          </div>
        ) : null}
      </div>
    </Link>
  );
});
