import { useState } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, Package } from "lucide-react";
import type { ProductItem, ProductStatus } from "../../types/product";

/**
 * A catalog card item: the DQ1 `ProductItem` plus the media the grid renders.
 * `assetToProductItem` fills the ProductItem fields for live assets; the
 * cutout/scene URLs are mock-only until the S3-era image derivation lands.
 */
export type CatalogProduct = ProductItem & {
  cutoutUrl?: string;
  sceneUrl?: string;
  evidenceId?: string;
};

/**
 * DQ3 badge pairs, embedded verbatim. Tailwind is not installed (DQ2: the CSS
 * custom-property tokens are the requirement), so each pair is paired with the
 * SG-043 semantic token class below that carries the same light/dark swatches.
 * The raw DQ3 utility strings stay on the element so the palette is greppable.
 */
export const BADGE_CLASS: Record<ProductStatus, string> = {
  raw: "bg-stone-100 text-stone-700 border-stone-200 dark:bg-stone-800/50 dark:text-stone-400 dark:border-stone-700/50",
  processed:
    "bg-sky-50 text-sky-800 border-sky-200 dark:bg-sky-950/40 dark:text-sky-400 dark:border-sky-800/50",
  rendered:
    "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800/50",
  failed:
    "bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800/50",
};

const STATUS_TOKEN_CLASS: Record<ProductStatus, string> = {
  raw: "badge-raw",
  processed: "badge-processed",
  rendered: "badge-rendered",
  failed: "badge-failed",
};

export const STATUS_LABEL: Record<ProductStatus, string> = {
  raw: "Source Only",
  processed: "Cutout Extracted",
  rendered: "Scene Rendered",
  failed: "Failed",
};

export function statusBadgeClass(status: ProductStatus): string {
  return `${STATUS_TOKEN_CLASS[status]} ${BADGE_CLASS[status]}`;
}

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

export function ProductCard({
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
      className="product-card bg-card border-border focus-ring"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        borderStyle: "solid",
        borderWidth: 1,
        borderRadius: 12,
        padding: 10,
        textDecoration: "none",
        color: "inherit",
        aspectRatio: "3 / 4",
      }}
    >
      <div
        data-testid="product-card-well"
        className={`bg-card-muted${failed ? " border border-rose-500/30" : ""}`}
        style={{
          position: "relative",
          aspectRatio: "1 / 1",
          borderRadius: 8,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          ...(failed
            ? {
                borderStyle: "solid",
                borderWidth: 1,
                borderColor: "hsl(var(--badge-failed-fg) / 0.3)",
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
            style={{ color: "hsl(var(--badge-failed-fg))" }}
          />
        ) : null}
        <span
          data-testid="status-badge"
          className={statusBadgeClass(item.status)}
          style={{
            position: "absolute",
            top: 8,
            right: 8,
            borderStyle: "solid",
            borderWidth: 1,
            borderRadius: 999,
            padding: "2px 8px",
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          {STATUS_LABEL[item.status]}
        </span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, minWidth: 0 }}>
          <span
            title={item.name}
            style={{
              fontWeight: 600,
              fontSize: 14,
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
              style={{ flexShrink: 0, color: "hsl(var(--badge-failed-fg))" }}
            />
          ) : null}
        </div>
        <span
          className="bg-card-muted text-muted-foreground font-mono"
          style={{
            alignSelf: "flex-start",
            fontSize: 11,
            padding: "2px 6px",
            borderRadius: 4,
            whiteSpace: "nowrap",
          }}
        >
          {item.category}
        </span>
        {item.metadata.primaryColors?.length ? (
          <div data-testid="color-dots" style={{ display: "flex", gap: 4 }}>
            {item.metadata.primaryColors.map((color) => (
              <span
                key={color}
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 999,
                  backgroundColor: color,
                  borderWidth: 1,
                  borderStyle: "solid",
                  borderColor: "hsl(var(--border))",
                }}
              />
            ))}
          </div>
        ) : null}
      </div>
    </Link>
  );
}
