import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronRight, ScanLine, Sparkles, X } from "lucide-react";
import { apiGet, apiPatch } from "../../api/client";
import type { Asset, Assertion, Evidence } from "../../api/types";
import { useTaxonomy } from "../../hooks/useAssets";
import { toProductCategory, UNTITLED_ASSET_NAME } from "../../types/product";

type ViewerTab = "cutout" | "scene" | "source";

const TABS: readonly { id: ViewerTab; label: string }[] = [
  { id: "cutout", label: "Isolated Cutout" },
  { id: "scene", label: "Scene / Context" },
  { id: "source", label: "Source Photo" },
];

const EMPTY_PANEL = "max-w-2xl w-full border-l border-border bg-card p-6 overflow-y-auto z-50";

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function assertionFor(assertions: Assertion[], suffix: string): Assertion | undefined {
  return assertions.find((item) => item.field_path === suffix || item.field_path.endsWith(`/${suffix}`));
}

function colorTags(assertions: Assertion[]): string[] {
  const matching = assertions.filter((item) =>
    /(^|\/)(primary_)?colou?rs?$/i.test(item.field_path)
  );
  const values = matching.flatMap((item) => (Array.isArray(item.value) ? item.value : [item.value]));
  return values.filter((value): value is string => typeof value === "string" && value.trim() !== "");
}

export type ItemInspectorDrawerProps = {
  asset: Asset;
  householdId: string;
  onClose: () => void;
};

/**
 * The wardrobe-flow inspector drawer (SG-046). It reads the full asset record
 * (evidence + assertions) through the same GET route the detail page uses and
 * writes ONLY through the existing PATCH endpoint, with the same `If-Match`
 * version the detail screen sends (`AssetDetailPage.tsx:24-32`).
 *
 * Nothing here implies a working AI backend: the cutout/scene tabs say a
 * pipeline does not exist yet, and the AI buttons send no request at all.
 */
export function ItemInspectorDrawer({ asset, householdId, onClose }: ItemInspectorDrawerProps) {
  const qc = useQueryClient();
  const closeRef = useRef<HTMLButtonElement>(null);
  const invokingRef = useRef<HTMLElement | null>(
    typeof document !== "undefined" ? (document.activeElement as HTMLElement | null) : null
  );

  const [tab, setTab] = useState<ViewerTab>("source");
  const [title, setTitle] = useState(asset.display_name ?? "");
  const [category, setCategory] = useState(toProductCategory(asset.asset_type));
  const [quantity, setQuantity] = useState(asset.quantity != null ? String(asset.quantity) : "");
  const [unit, setUnit] = useState(asset.unit ?? "");
  const [condition, setCondition] = useState(asset.condition ?? "");
  const [rawOpen, setRawOpen] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // The card/table rows carry the summary Asset; the detail route carries the
  // full one. Fetch by id so evidence + assertions are present, and so the
  // drawer updates after a PATCH without a parent refetch.
  const { data: full } = useQuery<Asset>({
    queryKey: ["asset", asset.id, householdId],
    queryFn: () => apiGet<Asset>(`/v1/assets/${asset.id}`, { household_id: householdId }),
    initialData: asset,
    enabled: !!asset.id && !!householdId,
  });

  const current = full ?? asset;
  const displayName = current.display_name || UNTITLED_ASSET_NAME;
  const assertions = useMemo(() => current.assertions ?? [], [current.assertions]);
  const evidence = useMemo(() => current.evidence ?? [], [current.evidence]);

  // SG-065: the category suggestions are served (GET /v1/taxonomy), not a
  // hardcoded DQ1 list. A missing/empty response degrades to no suggestions —
  // the input stays a free-text passthrough, never a crash.
  const { data: taxonomy } = useTaxonomy();
  const categoryOptions = useMemo(
    () => taxonomy?.plugins?.flatMap((plugin) => plugin.categories.map((c) => c.name)) ?? [],
    [taxonomy]
  );

  // Reset the editable fields when the record changes underneath us (e.g. after
  // a successful PATCH or when a different asset is selected without unmount).
  useEffect(() => {
    setTitle(current.display_name ?? "");
    setCategory(toProductCategory(current.asset_type));
    setQuantity(current.quantity != null ? String(current.quantity) : "");
    setUnit(current.unit ?? "");
    setCondition(current.condition ?? "");
  }, [current.id, current.version, current.display_name, current.asset_type, current.quantity, current.unit, current.condition]);

  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  const close = useCallback(() => {
    onClose();
  }, [onClose]);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        close();
      }
    };
    document.addEventListener("keydown", handler);
    return () => {
      // Focus returns to the invoking element on close.
      document.removeEventListener("keydown", handler);
      invokingRef.current?.focus?.();
    };
  }, [close]);

  const patchMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      apiPatch(`/v1/assets/${asset.id}`, payload, { household_id: householdId }, { "If-Match": String(current.version ?? 1) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assets"] });
      qc.invalidateQueries({ queryKey: ["asset", asset.id] });
      setError(null);
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  const firstEvidence: Evidence | undefined = evidence[0];
  const sourceUrl = firstEvidence
    ? `${import.meta.env.VITE_API_BASE || "http://localhost:8003"}/v1/evidence/${firstEvidence.id}/file?household_id=${householdId}`
    : null;

  const colors = colorTags(assertions);
  const description = assertionFor(assertions, "description");
  const descriptionValue = description ? formatValue(description.value) : null;

  const save = () => {
    const canonical = categoryOptions.find(
      (value) => value.toLowerCase() === category.trim().toLowerCase()
    );
    const payload: Record<string, unknown> = {
      display_name: title.trim(),
      asset_type: canonical ?? category.trim(),
    };
    if (quantity.trim() !== "") payload.quantity = Number(quantity);
    if (unit.trim() !== "") payload.unit = unit.trim();
    if (condition.trim() !== "") payload.condition = condition.trim();
    patchMut.mutate(payload);
  };

  const showAiNotice = () => {
    setNotice("scene rendering lands with the AI stages — nothing was sent anywhere");
  };

  const rawJson = useMemo(
    () => JSON.stringify({ asset: current, assertions }, null, 2),
    [current, assertions]
  );

  return (
    <div data-testid="inspector-drawer" className="font-sans">
      <div
        data-testid="inspector-backdrop"
        className="bg-background"
        aria-hidden="true"
        onClick={close}
        style={{ position: "fixed", inset: 0, opacity: 0.5, zIndex: 40 }}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={`Inspector: ${displayName}`}
        className={EMPTY_PANEL}
        style={{ position: "fixed", top: 0, right: 0, height: "100vh" }}
      >
        <header style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 16 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h2 data-testid="drawer-title" style={{ margin: 0, fontSize: 20 }}>{displayName}</h2>
            <span
              data-testid="drawer-category"
              className="bg-card-muted text-muted-foreground font-mono"
              style={{ display: "inline-block", marginTop: 6, fontSize: 11, padding: "2px 6px", borderRadius: 4 }}
            >
              {toProductCategory(current.asset_type)}
            </span>
          </div>
          <button
            ref={closeRef}
            type="button"
            aria-label="Close inspector"
            onClick={close}
            className="text-muted-foreground focus-ring"
            style={{ background: "none", border: "none", cursor: "pointer", padding: 4, borderRadius: 4 }}
          >
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <div role="tablist" aria-label="Viewer" style={{ display: "flex", gap: 4, marginBottom: 12 }}>
          {TABS.map((entry) => {
            const active = entry.id === tab;
            return (
              <button
                key={entry.id}
                role="tab"
                type="button"
                aria-selected={active}
                onClick={() => setTab(entry.id)}
                className={`${active ? "bg-primary text-primary-foreground" : "bg-card-muted text-muted-foreground"} focus-ring`}
                style={{
                  padding: "6px 10px",
                  borderRadius: 6,
                  borderStyle: "solid",
                  borderWidth: 1,
                  borderColor: "hsl(var(--border))",
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: active ? 600 : 400,
                }}
              >
                {entry.label}
              </button>
            );
          })}
        </div>

        <div
          data-testid="viewer-well"
          className="bg-card-muted"
          style={{
            position: "relative",
            aspectRatio: "1 / 1",
            borderRadius: 8,
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: 20,
          }}
        >
          {tab === "cutout" && (
            <p data-testid="cutout-honest-state" className="text-muted-foreground" style={{ margin: 0, padding: 24, textAlign: "center", fontSize: 13 }}>
              No isolated cutout exists yet. Cutouts arrive with the AI stages — nothing is being processed.
            </p>
          )}
          {tab === "scene" && (
            <p data-testid="scene-honest-state" className="text-muted-foreground" style={{ margin: 0, padding: 24, textAlign: "center", fontSize: 13 }}>
              No context scene exists yet. Scene rendering arrives with the AI stages — nothing is being rendered.
            </p>
          )}
          {tab === "source" &&
            (sourceUrl ? (
              <img
                data-testid="source-image"
                src={sourceUrl}
                alt={displayName}
                style={{ width: "100%", height: "100%", objectFit: "contain" }}
              />
            ) : (
              <p data-testid="source-empty" className="text-muted-foreground" style={{ margin: 0, padding: 24, textAlign: "center", fontSize: 13 }}>
                No source photo is attached to this asset.
              </p>
            ))}
        </div>
        <p className="text-muted-foreground" style={{ margin: "-14px 0 20px", fontSize: 11 }}>
          Bounding-box overlay omitted: no bounding-box data exists for this asset yet — a decorative box is never drawn.
        </p>

        <section aria-labelledby="drawer-metadata-heading" style={{ marginBottom: 20 }}>
          <h3 id="drawer-metadata-heading" style={{ fontSize: 14, marginBottom: 8 }}>Metadata</h3>
          <div style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: 8, alignItems: "center" }}>
            <label htmlFor="drawer-title-input" style={{ fontSize: 13 }}>Title</label>
            <input
              id="drawer-title-input"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="bg-background text-foreground border-border focus-ring"
              style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
            />
            <label htmlFor="drawer-category-input" style={{ fontSize: 13 }}>Category</label>
            <input
              id="drawer-category-input"
              list="drawer-category-options"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="bg-background text-foreground border-border focus-ring"
              style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
            />
            <datalist id="drawer-category-options">
              {categoryOptions.map((value) => (
                <option key={value} value={value} />
              ))}
            </datalist>
            <label htmlFor="drawer-quantity-input" style={{ fontSize: 13 }}>Quantity</label>
            <input
              id="drawer-quantity-input"
              type="number"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
              className="bg-background text-foreground border-border focus-ring"
              style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
            />
            <label htmlFor="drawer-unit-input" style={{ fontSize: 13 }}>Unit</label>
            <input
              id="drawer-unit-input"
              value={unit}
              onChange={(event) => setUnit(event.target.value)}
              className="bg-background text-foreground border-border focus-ring"
              style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
            />
            <label htmlFor="drawer-condition-input" style={{ fontSize: 13 }}>Condition</label>
            <input
              id="drawer-condition-input"
              value={condition}
              onChange={(event) => setCondition(event.target.value)}
              className="bg-background text-foreground border-border focus-ring"
              style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
            />
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10 }}>
            <button
              type="button"
              onClick={save}
              disabled={patchMut.isPending || !title.trim()}
              className="bg-primary text-primary-foreground focus-ring"
              style={{ padding: "6px 12px", borderRadius: 6, border: "none", cursor: "pointer" }}
            >
              {patchMut.isPending ? "Saving..." : "Save changes"}
            </button>
            <span className="text-muted-foreground" style={{ fontSize: 11 }}>
              Uses If-Match: {current.version} for optimistic concurrency
            </span>
          </div>
          {error && <div style={{ color: "hsl(var(--badge-failed-fg))", fontSize: 13, marginTop: 8 }}>{error}</div>}
        </section>

        <section aria-labelledby="drawer-observed-heading" style={{ marginBottom: 20 }}>
          <h3 id="drawer-observed-heading" style={{ fontSize: 14, marginBottom: 8 }}>Observed (read-only)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: 8, fontSize: 13 }}>
            <span className="text-muted-foreground">Colors</span>
            <span data-testid="drawer-colors">
              {colors.length ? colors.join(", ") : "No observed color data for this asset."}
            </span>
            <span className="text-muted-foreground">Description</span>
            <span data-testid="drawer-description">
              {descriptionValue ?? "No functional description assertion for this asset."}
            </span>
          </div>
          <p className="text-muted-foreground" style={{ margin: "6px 0 0", fontSize: 11 }}>
            Read-only rows: these fields have no schema home yet, so they are never editable here (D65).
          </p>
        </section>

        <section aria-labelledby="drawer-ai-heading" style={{ marginBottom: 20 }}>
          <h3 id="drawer-ai-heading" style={{ fontSize: 14, marginBottom: 8 }}>AI actions</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              type="button"
              onClick={showAiNotice}
              className="bg-card-muted text-muted-foreground border-border focus-ring"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 12px",
                borderRadius: 6,
                borderStyle: "solid",
                borderWidth: 1,
                cursor: "pointer",
              }}
            >
              <ScanLine size={16} aria-hidden="true" />
              Re-isolate Asset
            </button>
            <button
              type="button"
              onClick={showAiNotice}
              className="bg-primary text-primary-foreground focus-ring"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 12px",
                borderRadius: 6,
                border: "none",
                cursor: "pointer",
              }}
            >
              <Sparkles size={16} aria-hidden="true" />
              Generate Context Scene
            </button>
          </div>
          {notice && (
            <div
              data-testid="ai-notice"
              role="status"
              className="bg-card-muted text-muted-foreground"
              style={{ marginTop: 8, padding: "6px 10px", borderRadius: 6, fontSize: 12 }}
            >
              {notice}
            </div>
          )}
          <p className="text-muted-foreground" style={{ margin: "6px 0 0", fontSize: 11 }}>
            No model or cost text is shown: with no provider backend a model/cost string would be fabricated.
          </p>
        </section>

        <section>
          <button
            type="button"
            aria-expanded={rawOpen}
            onClick={() => setRawOpen((value) => !value)}
            className="text-foreground focus-ring"
            style={{ display: "inline-flex", alignItems: "center", gap: 4, background: "none", border: "none", cursor: "pointer", padding: 0, fontSize: 14, fontWeight: 600 }}
          >
            {rawOpen ? <ChevronDown size={16} aria-hidden="true" /> : <ChevronRight size={16} aria-hidden="true" />}
            Raw data
          </button>
          {rawOpen && (
            <pre
              data-testid="raw-json"
              className="bg-card-muted font-mono"
              style={{ marginTop: 8, padding: 10, borderRadius: 8, fontSize: 11, overflowX: "auto", maxHeight: 280 }}
            >
              {rawJson}
            </pre>
          )}
        </section>
      </aside>
    </div>
  );
}
