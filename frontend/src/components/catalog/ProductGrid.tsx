import { useState, type CSSProperties } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Package } from "lucide-react";
import type { Density } from "../shell/CatalogToolbar";
import { ProductCard, cardMedia, statusBadgeClass, STATUS_LABEL, type CatalogProduct } from "./ProductCard";
import { ProductCardSkeleton } from "./ProductCardSkeleton";
import { AssetImportModal } from "../shell/AssetImportModal";

/**
 * 2 cols mobile -> 3 tablet -> 4 desktop -> 5 ultrawide, gap-4 / md:gap-5.
 * Injected as plain classes because Tailwind is not installed (DQ2: the CSS
 * custom-property tokens are the requirement, utility classes are optional).
 */
const GRID_CSS = `
.catalog-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
@media (min-width: 768px) { .catalog-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; } }
@media (min-width: 1024px) { .catalog-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
@media (min-width: 1536px) { .catalog-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); } }
`;

const emptyStyle: CSSProperties = {
  borderStyle: "dashed",
  borderWidth: 1,
  borderColor: "hsl(var(--border))",
  borderRadius: 12,
  padding: "56px 24px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  gap: 12,
  textAlign: "center",
};

const ctaStyle: CSSProperties = {
  padding: "8px 16px",
  borderRadius: 6,
  textDecoration: "none",
  fontWeight: 600,
  fontSize: 13,
};

const COLUMNS: { label: string; width: string; align?: "right" | "center" }[] = [
  { label: "Asset", width: "56px", align: "center" },
  { label: "Name", width: "200px" },
  { label: "Category", width: "140px" },
  { label: "Status", width: "130px" },
  { label: "Dimensions/Specs", width: "120px" },
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
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.round(days / 30);
  if (months < 12) return `${months}mo ago`;
  return `${Math.round(months / 12)}y ago`;
}

function TableThumb({ item, householdId }: { item: CatalogProduct; householdId: string }) {
  const [broken, setBroken] = useState(false);
  const media = cardMedia(item, householdId);
  return (
    <span
      className="bg-card-muted"
      style={{
        display: "inline-flex",
        width: 40,
        height: 40,
        borderRadius: 6,
        overflow: "hidden",
        alignItems: "center",
        justifyContent: "center",
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
          <tr className="border-border" style={{ borderBottomStyle: "solid", borderBottomWidth: 1 }}>
            {COLUMNS.map((column) => (
              <th
                key={column.label}
                scope="col"
                className="text-muted-foreground"
                style={{
                  textAlign: column.align ?? "left",
                  fontSize: 11,
                  fontWeight: 600,
                  padding: "8px 10px",
                  whiteSpace: "nowrap",
                }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const specs = item.metadata.dimensions ?? item.metadata.material ?? "—";
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
                    className="bg-card-muted text-muted-foreground font-mono"
                    style={{ fontSize: 11, padding: "2px 6px", borderRadius: 4, whiteSpace: "nowrap" }}
                  >
                    {item.category}
                  </span>
                </td>
                <td style={{ padding: "8px 10px" }}>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                    <span
                      data-testid="status-dot"
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: 999,
                        backgroundColor: `hsl(var(--badge-${item.status}-fg))`,
                      }}
                    />
                    <span
                      className={statusBadgeClass(item.status)}
                      style={{
                        borderStyle: "solid",
                        borderWidth: 1,
                        borderRadius: 999,
                        padding: "2px 8px",
                        fontSize: 11,
                        fontWeight: 600,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {STATUS_LABEL[item.status]}
                    </span>
                  </span>
                </td>
                <td style={{ padding: "8px 10px", whiteSpace: "nowrap" }}>{specs}</td>
                <td
                  className="font-mono text-muted-foreground"
                  style={{ padding: "8px 10px", textAlign: "right", whiteSpace: "nowrap" }}
                >
                  {formatRelativeDate(item.dateAdded)}
                </td>
                <td style={{ padding: "8px 10px", textAlign: "center" }}>
                  <button
                    type="button"
                    aria-label={`Actions for ${item.name}`}
                    onClick={(event) => {
                      event.stopPropagation();
                      openDetail(item);
                    }}
                    className="text-muted-foreground focus-ring"
                    style={{
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      fontSize: 16,
                      lineHeight: 1,
                      padding: "4px 6px",
                      borderRadius: 4,
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
};

export function ProductGrid({
  items,
  density,
  householdId,
  loading = false,
  limit = 20,
  onSelect,
}: ProductGridProps) {
  const [importOpen, setImportOpen] = useState(false);

  if (loading) {
    return (
      <div
        role="region"
        aria-label="Product results"
        aria-busy="true"
        data-testid="catalog-grid"
        className="catalog-grid"
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
        style={emptyStyle}
      >
        <p className="text-muted-foreground" style={{ margin: 0 }}>
          No items match the current view.
        </p>
        <Link
          to="/capture"
          onClick={(event) => {
            event.preventDefault();
            setImportOpen(true);
          }}
          className="bg-primary text-primary-foreground focus-ring"
          style={ctaStyle}
        >
          Import New Item
        </Link>
        <p className="text-muted-foreground" style={{ margin: 0, fontSize: 12 }}>
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
    >
      <style data-testid="catalog-grid-style">{GRID_CSS}</style>
      {items.map((item) => (
        <ProductCard key={item.id} item={item} householdId={householdId} onSelect={onSelect} />
      ))}
    </div>
  );
}
