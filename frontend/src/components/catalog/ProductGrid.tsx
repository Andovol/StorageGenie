import { useState, type CSSProperties } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Package } from "lucide-react";
import type { Density } from "../shell/CatalogToolbar";
import { ProductCard, cardMedia, type CatalogProduct } from "./ProductCard";
import { formatUseByDate, labelAssetType } from "../../lib/labels";
import { ProductCardSkeleton } from "./ProductCardSkeleton";
import { AssetImportModal } from "../shell/AssetImportModal";

/**
 * SG-330 R4 (D41 Midnight): items per row is a setting — wide 4 / 5 / 6
 * (default 5), narrow 3 / 4 (default 3). The column count and the gaps ride
 * inline on the region (wide 40 x 24 px row x column, narrow 16 x 8 px row x
 * column, SG-331 T7 — CSS `gap` is row column); the class only
 * carries `display: grid`. Injected as plain CSS because Tailwind is not
 * installed (DQ2).
 */
const GRID_CSS = `
.catalog-grid { display: grid; }
`;

const emptyStyle: CSSProperties = {
  borderStyle: "dashed",
  borderWidth: 1,
  borderColor: "hsl(var(--line))",
  borderRadius: 0,
  padding: "56px 24px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 12,
  textAlign: "center",
  backgroundColor: "hsl(var(--paper))",
  color: "hsl(var(--ink))",
};

const ctaStyle: CSSProperties = {
  padding: "8px 16px",
  borderRadius: 0,
  textDecoration: "none",
  fontWeight: 600,
  fontSize: 13,
};

const COLUMNS: { label: string; width: string; align?: "right" | "center" }[] = [
  { label: "Asset", width: "56px", align: "center" },
  { label: "Name", width: "200px" },
  { label: "Category", width: "140px" },
  { label: "Use by", width: "130px" },
  { label: "Added", width: "110px", align: "right" },
  { label: "Actions", width: "48px", align: "center" },
];

/**
 * Relative "Added" label. Production reads the live clock; tests inject `nowMs`
 * so no fixed calendar date is ever asserted (`PG-IC-07`).
 */
export function formatRelativeDate(iso: string, nowMs: number = Date.now()): string {
  const then = new Date(iso).getTime();
  if (!Number.isFinite(then)) return "—";
  const seconds = Math.round((nowMs - then) / 1000);
  if (seconds < 45) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return minutes === 1 ? "1 min ago" : `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return hours === 1 ? "1 hour ago" : `${hours} hours ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return days === 1 ? "1 day ago" : `${days} days ago`;
  const months = Math.round(days / 30);
  if (months < 12) return months === 1 ? "1 month ago" : `${months} months ago`;
  const years = Math.round(months / 12);
  return years === 1 ? "1 year ago" : `${years} years ago`;
}

function TableThumb({ item, householdId }: { item: CatalogProduct; householdId: string }) {
  const [broken, setBroken] = useState(false);
  const media = cardMedia(item, householdId);
  return (
    <span
      style={{
        display: "inline-flex",
        width: 40,
        height: 40,
        borderRadius: 0,
        overflow: "hidden",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "hsl(var(--paper))",
      }}
    >
      {media && !broken ? (
        <img
          src={media}
          alt={item.name}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
          onError={() => setBroken(true)}
        />
      ) : (
        <Package
          data-testid="product-fallback-icon"
          aria-hidden="true"
          size={20}
          className="text-muted-foreground"
        />
      )}
    </span>
  );
}

function TableView({
  items,
  householdId,
  onSelect,
}: {
  items: CatalogProduct[];
  householdId: string;
  onSelect?: (id: string) => void;
}) {
  const navigate = useNavigate();
  const openDetail = (item: CatalogProduct) =>
    onSelect ? onSelect(item.id) : navigate(`/assets/${item.id}?household_id=${householdId}`);

  return (
    <div
      data-testid="table-scroll"
      role="region"
      aria-label="Product results table"
      style={{ overflowX: "auto" }}
    >
      <table role="table" aria-label="Product results" style={{ width: "100%", borderCollapse: "collapse" }}>
        <colgroup>
          {COLUMNS.map((column) => (
            <col key={column.label} style={{ width: column.width, minWidth: column.width }} />
          ))}
        </colgroup>
        <thead>
          <tr className="border-border" style={{ borderBottomStyle: "solid", borderBottomWidth: 1, borderColor: "hsl(var(--line))" }}>
            {COLUMNS.map((column) => (
              <th
                key={column.label}
                scope="col"
                style={{
                  textAlign: column.align ?? "left",
                  fontSize: 13,
                  fontWeight: 600,
                  padding: "8px 10px",
                  whiteSpace: "nowrap",
                  color: "hsl(var(--ink-muted))",
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            return (
              <tr
                key={item.id}
                data-testid="product-row"
                role="link"
                tabIndex={0}
                aria-label={`Open ${item.name}`}
                onClick={() => openDetail(item)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") openDetail(item);
                }}
                className="border-border focus-ring"
                style={{ borderBottomStyle: "solid", borderBottomWidth: 1, cursor: "pointer" }}
              >
                <td style={{ padding: "8px 10px", textAlign: "center" }}>
                  <TableThumb item={item} householdId={householdId} />
                </td>
                <td style={{ padding: "8px 10px", maxWidth: 200 }}>
                  <span
                    style={{
                      display: "inline-block",
                      maxWidth: 200,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      verticalAlign: "middle",
                    }}
                  >
                    {item.name}
                  </span>
                </td>
                <td style={{ padding: "8px 10px" }}>
                  <span
                    style={{ fontSize: 13, padding: "2px 8px", borderRadius: 0, whiteSpace: "nowrap", borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink-muted))" }}
                  >
                    {labelAssetType(item.category)}
                  </span>
                </td>
                <td style={{ padding: "8px 10px" }}>
                  <span
                    data-testid="use-by-cell"
                    style={{ fontSize: 13, whiteSpace: "nowrap", color: "hsl(var(--ink))" }}
                  >
                    {formatUseByDate(item.useBy) || "No date"}
                  </span>
                </td>
                <td
                  style={{ padding: "8px 10px", textAlign: "right", whiteSpace: "nowrap", fontSize: 13, color: "hsl(var(--ink-muted))" }}
                >
                  {formatRelativeDate(item.dateAdded)}
                </td>
                <td style={{ padding: "8px 10px", textAlign: "center" }}>
                  <button
                    type="button"
                    aria-label={`More actions for ${item.name}`}
                    title={`More actions for ${item.name}`}
                    onClick={(event) => {
                      event.stopPropagation();
                      openDetail(item);
                    }}
                    className="focus-ring"
                    style={{
                      background: "hsl(var(--paper))",
                      borderStyle: "solid",
                      borderWidth: 1,
                      borderColor: "hsl(var(--line))",
                      color: "hsl(var(--ink))",
                      cursor: "pointer",
                      fontSize: 16,
                      lineHeight: 1,
                      padding: "4px 6px",
                      borderRadius: 0,
                    }}
                  >
                    ...
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

type ProductGridProps = {
  items: CatalogProduct[];
  density: Density;
  householdId: string;
  loading?: boolean;
  limit?: number;
  onSelect?: (id: string) => void;
  /** SG-330 R4: resolved items-per-row count (CatalogPage owns the setting). */
  perRow?: number;
  /** SG-330 R4: live narrow flag (< 640 px) for the narrow gaps. */
  narrow?: boolean;
};

export function ProductGrid({
  items,
  density,
  householdId,
  loading = false,
  limit = 20,
  onSelect,
  perRow = 5,
  narrow = false,
}: ProductGridProps) {
  const [importOpen, setImportOpen] = useState(false);
  // SG-331 T7: CSS `gap` is row column — wide 40 x 24 px, narrow 16 x 8 px.
  const gridStyle: CSSProperties = {
    gridTemplateColumns: `repeat(${perRow}, minmax(0, 1fr))`,
    gap: narrow ? "16px 8px" : "40px 24px",
  };

  if (loading) {
    return (
      <div
        role="region"
        aria-label="Product results"
        aria-busy="true"
        data-testid="catalog-grid"
        className="catalog-grid"
        style={gridStyle}
      >
        <style data-testid="catalog-grid-style">{GRID_CSS}</style>
        {Array.from({ length: limit }, (_, index) => (
          <ProductCardSkeleton key={index} />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div
        role="region"
        aria-label="Product results"
        aria-busy="false"
        data-testid="catalog-grid-empty"
        className="border-border text-foreground"
        style={emptyStyle}
      >
        <p style={{ margin: 0, fontSize: 13, color: "hsl(var(--ink-muted))" }}>
          No items match the current view.
        </p>
        <Link
          to="/capture"
          onClick={(event) => {
            event.preventDefault();
            setImportOpen(true);
          }}
          className="focus-ring"
          style={{ ...ctaStyle, backgroundColor: "hsl(var(--ink))", color: "hsl(var(--paper))" }}
        >
          Import New Item
        </Link>
        <p style={{ margin: 0, fontSize: 13, color: "hsl(var(--ink-muted))" }}>
          Opens the import dialog: drop, select or paste photos. The Capture route stays for direct
          navigation.
        </p>
        {importOpen ? (
          <AssetImportModal householdId={householdId} onClose={() => setImportOpen(false)} />
        ) : null}
      </div>
    );
  }

  if (density === "table") {
    return <TableView items={items} householdId={householdId} onSelect={onSelect} />;
  }

  return (
    <div
      role="region"
      aria-label="Product results"
      aria-busy="false"
      data-testid="catalog-grid"
      className="catalog-grid"
      style={gridStyle}
    >
      <style data-testid="catalog-grid-style">{GRID_CSS}</style>
      {items.map((item) => (
        <ProductCard key={item.id} item={item} householdId={householdId} onSelect={onSelect} />
      ))}
    </div>
  );
}
