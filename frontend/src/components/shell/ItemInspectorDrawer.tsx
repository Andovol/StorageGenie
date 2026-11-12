import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ScanLine, Sparkles, X } from "lucide-react";
import { apiGet, apiPatch, decrementQuantity, incrementQuantity, markGone, putBack } from "../../api/client";
import type { Asset, Assertion, Evidence, GoneReason } from "../../api/types";
import { goneReasonLabel } from "../../api/types";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "./CatalogToolbar";
import { useTaxonomy } from "../../hooks/useAssets";
import { UNTITLED_ASSET_NAME } from "../../types/product";
import { labelAssetType } from "../../lib/labels";
import { quantityLeftText } from "../../lib/quantityText";
import { invalidateAssetViews } from "../../lib/invalidateAssetViews";

type ViewerTab = "cutout" | "scene" | "source";

const TABS: readonly { id: ViewerTab; label: string }[] = [
  { id: "source", label: "Photo" },
  { id: "cutout", label: "Cut-out" },
  { id: "scene", label: "In a scene" },
];

// SG-077: the panel's width/padding/scroll/stacking used to come from Tailwind
// utility names this project never defines (no Tailwind anywhere), so the
// fixed-position aside had no width and the 1/1 viewer well blew up to viewport
// scale, pushing every field below the fold. Width is now an explicit pixel
// cap the project's own CSS honors; the well is capped to stay inside it.
// SG-307 G2: paper ground, --line rules, square corners — the Pantry parity.
const EMPTY_PANEL = "";
const PANEL_MAX_WIDTH = 440;
const VIEWER_MAX_SIZE = 260;

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
  const [category, setCategory] = useState(labelAssetType(asset.asset_type));
  const [quantity, setQuantity] = useState(asset.quantity != null ? String(asset.quantity) : "");
  const [unit, setUnit] = useState(asset.unit ?? "");
  const [condition, setCondition] = useState(asset.condition ?? "");
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [goneMessage, setGoneMessage] = useState<string | null>(null);
  const [goneError, setGoneError] = useState<string | null>(null);
  const [qtyMessage, setQtyMessage] = useState<string | null>(null);
  const [qtyError, setQtyError] = useState<string | null>(null);

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
  // SG-307 G2: the field reads `asset.asset_type` (see :390 label); a food
  // item whose food kind lives only in the expiry classification assertion
  // still reads Uncategorized here — that sync needs a backend change, so the
  // field is left reading asset_type, in plain words via labelAssetType.
  useEffect(() => {
    setTitle(current.display_name ?? "");
    setCategory(labelAssetType(current.asset_type));
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
      invalidateAssetViews(qc, asset.id);
      setError(null);
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  // SG-272 G2/G3: the panel mirrors the item page's Gone and −1 controls.
  // The counted rule lives in `routes/AssetDetailPage.tsx` (`isCountedUnit`);
  // this local copy keeps the drawer free of a route import.
  const goneEntry = assertions.find(
    (item) => item.field_path === "gone.reason" || item.field_path.endsWith("/gone.reason")
  );
  const goneRaw =
    goneEntry && goneEntry.value && typeof goneEntry.value === "object" && !Array.isArray(goneEntry.value)
      ? (goneEntry.value as Record<string, unknown>)["reason"]
      : null;
  const goneLabel = goneReasonLabel(current.gone_reason) ?? goneReasonLabel(typeof goneRaw === "string" ? goneRaw : null);
  const isGone = current.status === "ARCHIVED" || goneLabel !== null;
  const amountUnits = new Set(["ml", "milliliter", "millilitre", "l", "liter", "litre", "g", "gram", "grams", "kg", "kilogram", "kilograms"]);
  const counted = !current.unit || current.unit.trim() === "" || !amountUnits.has(current.unit.trim().toLowerCase());
  const qtyValue = current.quantity ?? null;

  const goneMut = useMutation({
    mutationFn: (reason: GoneReason) => markGone(asset.id, householdId, reason),
    onSuccess: (updated) => {
      invalidateAssetViews(qc, asset.id);
      const label = goneReasonLabel(updated.gone_reason) ?? "gone";
      setGoneMessage(`Marked as ${label.toLowerCase()}. Undo with Put back.`);
      setGoneError(null);
    },
    onError: (e: unknown) => {
      setGoneError(e instanceof Error ? e.message : String(e));
      setGoneMessage(null);
    },
  });
  const putBackMut = useMutation({
    mutationFn: () => putBack(asset.id, householdId),
    onSuccess: (updated) => {
      invalidateAssetViews(qc, asset.id);
      setGoneMessage(`“${updated.display_name || "Item"}” is back in your catalog.`);
      setGoneError(null);
    },
    onError: (e: unknown) => {
      setGoneError(e instanceof Error ? e.message : String(e));
      setGoneMessage(null);
    },
  });
  const decMut = useMutation({
    mutationFn: () => decrementQuantity(asset.id, householdId),
    onSuccess: (updated) => {
      invalidateAssetViews(qc, asset.id);
      setQtyError(null);
      setQtyMessage(updated.quantity != null ? `Now ${updated.quantity} left.` : "Quantity changed.");
    },
    onError: (e: unknown) => {
      setQtyError(e instanceof Error ? e.message : String(e));
      setQtyMessage(null);
    },
  });
  const incMut = useMutation({
    mutationFn: () => incrementQuantity(asset.id, householdId),
    onSuccess: (updated) => {
      invalidateAssetViews(qc, asset.id);
      setQtyError(null);
      setQtyMessage(updated.quantity != null ? `Now ${updated.quantity} left.` : "Quantity changed.");
    },
    onError: (e: unknown) => {
      setQtyError(e instanceof Error ? e.message : String(e));
      setQtyMessage(null);
    },
  });

  const firstEvidence: Evidence | undefined = evidence[0];
  const sourceUrl = firstEvidence
    ? `${import.meta.env.VITE_API_BASE || "http://localhost:8003"}/v1/evidence/${firstEvidence.id}/file?household_id=${householdId}`
    : null;
  const sceneEvidence = evidence.find((entry) => entry.source_kind === "scene_render");
  const sceneUrl = sceneEvidence
    ? `${import.meta.env.VITE_API_BASE || "http://localhost:8003"}/v1/evidence/${sceneEvidence.id}/file?household_id=${householdId}`
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
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          height: "100vh",
          width: "100%",
          maxWidth: PANEL_MAX_WIDTH,
          padding: 24,
          overflowY: "auto",
          zIndex: 50,
          borderLeft: "1px solid hsl(var(--line))",
          backgroundColor: "hsl(var(--paper))",
          color: "hsl(var(--ink))",
        }}
      >
        <header style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 16, borderBottom: "1px solid hsl(var(--line))", paddingBottom: 12 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h2 data-testid="drawer-title" style={{ margin: 0, fontSize: 20, color: "hsl(var(--ink))" }}>{displayName}</h2>
            <span
              data-testid="drawer-category"
              style={{ display: "inline-block", marginTop: 6, fontSize: 13, padding: "2px 8px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink-muted))" }}
            >
              {labelAssetType(current.asset_type)}
            </span>
          </div>
          <button
            ref={closeRef}
            type="button"
            aria-label="Close inspector"
            onClick={close}
            className="sg-paper-control focus-ring"
            style={{ cursor: "pointer", padding: 4, borderRadius: 0, fontSize: 13 }}
          >
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <div role="tablist" aria-label="Viewer" style={{ display: "flex", gap: 0, marginBottom: 12 }}>
          {TABS.map((entry) => {
            const active = entry.id === tab;
            return (
              <button
                key={entry.id}
                role="tab"
                type="button"
                aria-selected={active}
                onClick={() => setTab(entry.id)}
                className="sg-paper-control focus-ring"
                style={{
                  padding: "6px 10px",
                  borderRadius: 0,
                  cursor: "pointer",
                  fontSize: 13,
                  fontWeight: active ? 600 : 400,
                  backgroundColor: active ? "hsl(var(--ink))" : "hsl(var(--paper))",
                  color: active ? "hsl(var(--paper))" : "hsl(var(--ink))",
                  marginLeft: entry.id === "source" ? 0 : -1,
                }}
              >
                {entry.label}
              </button>
            );
          })}
        </div>

        <div
          data-testid="viewer-well"
          data-bbox-omitted="true"
          style={{
            position: "relative",
            aspectRatio: "1 / 1",
            width: "100%",
            maxWidth: VIEWER_MAX_SIZE,
            maxHeight: VIEWER_MAX_SIZE,
            marginLeft: "auto",
            marginRight: "auto",
            borderRadius: 0,
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: 20,
            backgroundColor: "hsl(var(--paper))",
            border: "1px solid hsl(var(--line))",
          }}
        >
          {tab === "cutout" && (
            <p data-testid="cutout-honest-state" style={{ margin: 0, padding: 24, textAlign: "center", fontSize: 13, color: "hsl(var(--ink-muted))" }}>
              No cut-out yet.
            </p>
          )}
          {tab === "scene" &&
            (sceneUrl ? (
              <img
                data-testid="scene-image"
                src={sceneUrl}
                alt={`${displayName} context scene`}
                style={{ width: "100%", height: "100%", objectFit: "contain" }}
              />
            ) : (
              <p data-testid="scene-honest-state" style={{ margin: 0, padding: 24, textAlign: "center", fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                No scene yet.
              </p>
            ))}
          {tab === "source" &&
            (sourceUrl ? (
              <img
                data-testid="source-image"
                src={sourceUrl}
                alt={displayName}
                style={{ width: "100%", height: "100%", objectFit: "contain" }}
              />
            ) : (
              <p data-testid="source-empty" style={{ margin: 0, padding: 24, textAlign: "center", fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                No photo yet.
              </p>
            ))}
        </div>

        <section aria-labelledby="drawer-metadata-heading" style={{ marginBottom: 20, borderTop: "1px solid hsl(var(--line))", paddingTop: 12 }}>
          <h3 id="drawer-metadata-heading" style={{ fontSize: 14, marginBottom: 8, color: "hsl(var(--ink))" }}>Metadata</h3>
          <div style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: 8, alignItems: "center" }}>
            <label htmlFor="drawer-title-input" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>Title</label>
            <input
              id="drawer-title-input"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="sg-paper-control focus-ring"
              style={{ padding: 8, borderRadius: 0, fontSize: 13 }}
            />
            <label htmlFor="drawer-category-input" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>Kind of item</label>
            <input
              id="drawer-category-input"
              list="drawer-category-options"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="sg-paper-control focus-ring"
              style={{ padding: 8, borderRadius: 0, fontSize: 13 }}
            />
            <datalist id="drawer-category-options">
              {categoryOptions.map((value) => (
                <option key={value} value={value} />
              ))}
            </datalist>
            <label htmlFor="drawer-quantity-input" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>Quantity</label>
            <input
              id="drawer-quantity-input"
              type="number"
              value={quantity}
              onChange={(event) => setQuantity(event.target.value)}
              className="sg-paper-control focus-ring"
              style={{ padding: 8, borderRadius: 0, fontSize: 13 }}
            />
            <label htmlFor="drawer-unit-input" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>Unit</label>
            <input
              id="drawer-unit-input"
              value={unit}
              onChange={(event) => setUnit(event.target.value)}
              className="sg-paper-control focus-ring"
              style={{ padding: 8, borderRadius: 0, fontSize: 13 }}
            />
            <label htmlFor="drawer-condition-input" style={{ fontSize: 13, color: "hsl(var(--ink))" }}>Condition</label>
            <input
              id="drawer-condition-input"
              value={condition}
              onChange={(event) => setCondition(event.target.value)}
              className="sg-paper-control focus-ring"
              style={{ padding: 8, borderRadius: 0, fontSize: 13 }}
            />
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10 }}>
            <button
              type="button"
              onClick={save}
              disabled={patchMut.isPending || !title.trim()}
              className="focus-ring"
              style={{ padding: "6px 12px", borderRadius: 0, cursor: "pointer", fontSize: 13, backgroundColor: "hsl(var(--ink))", color: "hsl(var(--paper))", border: "none" }}
            >
              {patchMut.isPending ? "Saving..." : "Save changes"}
            </button>
            {/* SG-307r1 fix 3: the system version detail is off the screen; the
                value stays in the DOM as data-version. The Save PATCH still
                sends it as the If-Match header above. */}
            <span data-version={current.version} style={{ display: "none" }} />
          </div>
          {error && <div className="text-danger" style={{ fontSize: 13, marginTop: 8 }}>{error}</div>}
        </section>

        <section aria-label="Amount left" style={{ marginBottom: 20, borderTop: "1px solid hsl(var(--line))", paddingTop: 12 }}>
          <h3 style={{ fontSize: 14, marginBottom: 8, color: "hsl(var(--ink))" }}>Amount left</h3>
          {counted ? (
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <button
                type="button"
                aria-label="Take off 1"
                onClick={() => decMut.mutate()}
                disabled={decMut.isPending || isGone || (qtyValue ?? 0) <= 0}
                className={THEMED_CONTROL_CLASS}
                style={{ ...CONTROL_STYLE, opacity: decMut.isPending || isGone || (qtyValue ?? 0) <= 0 ? 0.5 : 1 }}
              >
                {decMut.isPending ? "…" : "−1"}
              </button>
              <span style={{ fontSize: 13 }}>
                {quantityLeftText(qtyValue, current.unit, counted)}
              </span>
              <button
                type="button"
                aria-label="Put 1 back on the count"
                onClick={() => incMut.mutate()}
                disabled={incMut.isPending || isGone}
                className={THEMED_CONTROL_CLASS}
                style={{ ...CONTROL_STYLE, opacity: incMut.isPending || isGone ? 0.5 : 1 }}
              >
                {incMut.isPending ? "…" : "+1"}
              </button>
            </div>
          ) : (
            <div className="text-muted-foreground" style={{ fontSize: 13 }}>
              {quantityLeftText(qtyValue, current.unit, counted)} — change the amount with Save changes above.
            </div>
          )}
          {!isGone && counted && (qtyValue ?? 0) <= 0 && (
            <div role="status" className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
              None left — mark it gone below.
            </div>
          )}
          {qtyMessage && <div role="status" className="text-success" style={{ fontSize: 13, marginTop: 6 }}>{qtyMessage}</div>}
          {qtyError && <div role="alert" className="text-danger" style={{ fontSize: 13, marginTop: 6 }}>{qtyError}</div>}
        </section>

        <section aria-label="Use it up" style={{ marginBottom: 20, borderTop: "1px solid hsl(var(--line))", paddingTop: 12 }}>
          <h3 style={{ fontSize: 14, marginBottom: 8, color: "hsl(var(--ink))" }}>Use it up</h3>
          {isGone ? (
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <span role="status" style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                Gone{goneLabel ? ` — ${goneLabel.toLowerCase()}` : ""}
              </span>
              <button
                type="button"
                onClick={() => putBackMut.mutate()}
                disabled={putBackMut.isPending}
                className="focus-ring"
                style={{ padding: "6px 12px", borderRadius: 0, cursor: "pointer", fontSize: 13, backgroundColor: "hsl(var(--ink))", color: "hsl(var(--paper))", border: "none" }}
              >
                {putBackMut.isPending ? "Putting back…" : "Put back"}
              </button>
            </div>
          ) : (
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              {(["used_up", "thrown_away", "given_away"] as GoneReason[]).map((reason) => (
                <button
                  key={reason}
                  type="button"
                  onClick={() => goneMut.mutate(reason)}
                  disabled={goneMut.isPending}
                  className={THEMED_CONTROL_CLASS}
                  style={{ ...CONTROL_STYLE, borderRadius: 0, fontSize: 13 }}
                >
                  {goneReasonLabel(reason)}
                </button>
              ))}
            </div>
          )}
          {goneMessage && <div role="status" className="text-success" style={{ fontSize: 13, marginTop: 6 }}>{goneMessage}</div>}
          {goneError && <div role="alert" className="text-danger" style={{ fontSize: 13, marginTop: 6 }}>{goneError}</div>}
        </section>

        <section aria-labelledby="drawer-observed-heading" style={{ marginBottom: 20, borderTop: "1px solid hsl(var(--line))", paddingTop: 12 }}>
          <h3 id="drawer-observed-heading" style={{ fontSize: 14, marginBottom: 8, color: "hsl(var(--ink))" }}>Observed (read-only)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: 8, fontSize: 13, color: "hsl(var(--ink))" }}>
            <span style={{ color: "hsl(var(--ink-muted))" }}>Colors</span>
            <span data-testid="drawer-colors">
              {colors.length ? colors.join(", ") : "No colours yet."}
            </span>
            <span style={{ color: "hsl(var(--ink-muted))" }}>Description</span>
            <span data-testid="drawer-description">
              {descriptionValue ?? "No description yet."}
            </span>
          </div>
          <p style={{ margin: "6px 0 0", fontSize: 13, color: "hsl(var(--ink-muted))" }}>
            These stay read-only here.
          </p>
        </section>

        <section aria-labelledby="drawer-ai-heading" style={{ marginBottom: 20, borderTop: "1px solid hsl(var(--line))", paddingTop: 12 }}>
          <h3 id="drawer-ai-heading" style={{ fontSize: 14, marginBottom: 8, color: "hsl(var(--ink))" }}>AI actions</h3>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              type="button"
              onClick={showAiNotice}
              className="sg-paper-control focus-ring"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 12px",
                borderRadius: 0,
                cursor: "pointer",
                fontSize: 13,
              }}
            >
              <ScanLine size={16} aria-hidden="true" />
              Re-isolate Asset
            </button>
            <button
              type="button"
              onClick={showAiNotice}
              className="focus-ring"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 12px",
                borderRadius: 0,
                cursor: "pointer",
                fontSize: 13,
                backgroundColor: "hsl(var(--ink))",
                color: "hsl(var(--paper))",
                border: "none",
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
              style={{ marginTop: 8, padding: "6px 10px", borderRadius: 0, fontSize: 13, backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink-muted))", border: "1px solid hsl(var(--line))" }}
            >
              {notice}
            </div>
          )}
          <p style={{ margin: "6px 0 0", fontSize: 13, color: "hsl(var(--ink-muted))" }}>
            No model or cost shown.
          </p>
        </section>
      </aside>
    </div>
  );
}
