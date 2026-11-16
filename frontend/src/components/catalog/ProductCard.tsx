import { memo, useState } from "react";
import { Link } from "react-router-dom";
import { Package } from "lucide-react";
import type { ProductItem } from "../../types/product";
import { formatUseByDate, formatUseByDayMonth, labelAssetType } from "../../lib/labels";

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
  /** SG-330 R5: days until the use-by date from the same join (negative when
   * past its date); null when the item has no date. Carried the same way as
   * `useBy` so the card can mark past and this-week dates. */
  daysRemaining?: number | null;
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

export type CardDateTone = "past" | "soon" | "later" | "none";

/**
 * SG-330 R5: the date line in owner words. `narrow` selects the short phone
 * wording; the wide wording is the default.
 */
export function cardDateLine(
  useBy: string | null | undefined,
  daysRemaining: number | null | undefined,
  narrow: boolean
): { text: string; tone: CardDateTone } {
  if (!useBy) {
    return narrow ? { text: "No date", tone: "none" } : { text: "No date yet", tone: "none" };
  }
  if (typeof daysRemaining === "number" && Number.isFinite(daysRemaining)) {
    if (daysRemaining < 0) {
      const dayMonth = formatUseByDayMonth(useBy) || formatUseByDate(useBy);
      return narrow
        ? { text: `Past · ${dayMonth}`, tone: "past" }
        : { text: `Past its date · ${dayMonth}`, tone: "past" };
    }
    if (daysRemaining <= 7) {
      const dayMonth = formatUseByDayMonth(useBy) || formatUseByDate(useBy);
      if (narrow) return { text: dayMonth, tone: "soon" };
      const count = daysRemaining === 1 ? "1 day" : `${daysRemaining} days`;
      return { text: `Use by ${dayMonth} · ${count}`, tone: "soon" };
    }
  }
  const full = formatUseByDate(useBy);
  if (!full) {
    return narrow ? { text: "No date", tone: "none" } : { text: "No date yet", tone: "none" };
  }
  // The later line keeps the full date with its year in both widths.
  return { text: narrow ? full : `Use by ${full}`, tone: "later" };
}

const DATE_TONE_STYLE: Record<CardDateTone, { backgroundColor: string; color: string }> = {
  past: { backgroundColor: "hsl(var(--past-bg))", color: "hsl(var(--past-fg))" },
  soon: { backgroundColor: "hsl(var(--soon-bg))", color: "hsl(var(--soon-fg))" },
  later: { backgroundColor: "transparent", color: "hsl(var(--ink))" },
  none: { backgroundColor: "transparent", color: "hsl(var(--ink-muted))" },
};

/**
 * ⚡ Bolt Optimization: Memoize ProductCard to prevent re-rendering catalog grid items
 * when parent state changes (e.g. search input keystrokes before debounce, active filters,
 * or opening/closing the inspector drawer).
 * Expected Impact: Reduces catalog item re-renders by ~100% on search typing and drawer toggles.
 *
 * SG-330 R5 (D41 Midnight): photo first — a square tile filling the column
 * (photo `object-fit: contain` on `--tile`), no border, no status dot or
 * badge. The failed pipeline icons, the status dots and the category pill are
 * gone on purpose; the date line below the name carries past/this-week in
 * their washes. Same-name packs stay separate cards.
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
  const media = cardMedia(item, householdId);
  const wide = cardDateLine(item.useBy, item.daysRemaining, false);
  const narrow = cardDateLine(item.useBy, item.daysRemaining, true);
  const wideStyle = DATE_TONE_STYLE[wide.tone];

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
        gap: 8,
        borderStyle: "none",
        borderRadius: 0,
        padding: 0,
        textDecoration: "none",
        color: "hsl(var(--ink))",
        backgroundColor: "hsl(var(--paper))",
      }}
    >
      <div
        data-testid="product-card-well"
        style={{
          position: "relative",
          aspectRatio: "1 / 1",
          borderStyle: "none",
          borderRadius: 0,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "hsl(var(--tile))",
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
        ) : (
          <Package
            data-testid="product-fallback-icon"
            aria-hidden="true"
            size={28}
            className="text-muted-foreground"
          />
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4, minWidth: 0 }}>
        <span title={item.name} className="sg-card-name">
          {item.name}
        </span>
        <span
          data-testid="product-date-wide"
          className="sg-wide-only"
          style={{
            alignSelf: "flex-start",
            fontSize: 13,
            fontWeight: wide.tone === "later" || wide.tone === "none" ? 400 : 600,
            padding: wide.tone === "past" || wide.tone === "soon" ? "2px 8px" : 0,
            borderRadius: 0,
            whiteSpace: "nowrap",
            ...wideStyle,
          }}
        >
          {wide.text}
        </span>
        <span
          data-testid="product-date-narrow"
          className="sg-narrow-only"
          style={{
            alignSelf: "flex-start",
            fontSize: 13,
            fontWeight: narrow.tone === "later" || narrow.tone === "none" ? 400 : 600,
            padding: narrow.tone === "past" || narrow.tone === "soon" ? "2px 8px" : 0,
            borderRadius: 0,
            whiteSpace: "nowrap",
            ...DATE_TONE_STYLE[narrow.tone],
          }}
        >
          {narrow.text}
        </span>
        <span data-testid="product-kind" className="sg-card-kind">
          {labelAssetType(item.category)}
        </span>
      </div>
    </Link>
  );
});
