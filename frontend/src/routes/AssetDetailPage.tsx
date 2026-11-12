import { useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAsset, useTaxonomy } from "../hooks/useAssets";
import { quantityLeftText } from "../lib/quantityText";
import { EvidenceGallery } from "../components/EvidenceGallery";
import { ProvenanceBadge } from "../components/ProvenanceBadge";
import { ExpiryEntryForm } from "../components/ExpiryEntryForm";
import { PageContainer } from "../components/shell/PageContainer";
import {
  apiPatch,
  apiPost,
  assignAssetLocation,
  classifyAsset,
  createRelation,
  decrementQuantity,
  deleteRelation,
  fetchHouseholdAssets,
  fetchLocations,
  fetchRelations,
  incrementQuantity,
  markGone,
  putBack,
  unassignAssetLocation,
  uploadEvidence,
} from "../api/client";
import type {
  Asset,
  AssetListResponse,
  AssetRelation,
  Assertion,
  EnrichResponse,
  GoneReason,
  LocationListResponse,
  RelationListResponse,
} from "../api/types";
import { goneReasonLabel } from "../api/types";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { WebAlternates } from "../components/WebAlternates";
import { UNTITLED_ASSET_NAME } from "../types/product";
import { formatJobDate, formatPlainDate, labelAssetType, labelExpiryState } from "../lib/labels";

// SG-082: per-press Enrich cap. UNCALIBRATED on purpose (`G-A9`): the value is
// a stated ceiling, not a measured cost. The button shows the last measured
// spend and refuses a press above the cap with a named reason.
export const ENRICH_PER_PRESS_CAP_USD = 0.05;

// SG-272 G3 (Q22): the counted rule. A unit of ml, l, g or kg (and their
// written-out names) is an amount — taking off "1" means nothing there, so it
// gets a quick edit instead of −1. Everything else (empty, pcs, bottles, cups,
// piece, dose, tablet, …) is counted and gets the one-tap −1 with a way back
// up. The rule is the design call, written down here and shared by the tests.
const AMOUNT_UNITS = new Set([
  "ml",
  "milliliter",
  "millilitre",
  "l",
  "liter",
  "litre",
  "g",
  "gram",
  "grams",
  "kg",
  "kilogram",
  "kilograms",
]);

export function isCountedUnit(unit: string | null | undefined): boolean {
  if (!unit || unit.trim() === "") return true;
  return !AMOUNT_UNITS.has(unit.trim().toLowerCase());
}

export function enrichCapRefusal(
  projectedSpendUsd: number,
  capUsd: number = ENRICH_PER_PRESS_CAP_USD
): string | null {
  if (!Number.isFinite(projectedSpendUsd)) {
    return "Cannot check the last spend, so Enrich stays off.";
  }
  if (projectedSpendUsd > capUsd) {
    return `Last spend $${projectedSpendUsd.toFixed(6)} is over the $${capUsd.toFixed(2)} cap, so Enrich stays off.`;
  }
  return null;
}

export function EnrichButton({
  lastSpendUsd,
  onRun,
  capUsd = ENRICH_PER_PRESS_CAP_USD,
}: {
  lastSpendUsd: number | null;
  onRun?: () => void;
  capUsd?: number;
}) {
  const [refusal, setRefusal] = useState<string | null>(null);
  function handleClick() {
    const reason = enrichCapRefusal(lastSpendUsd ?? 0, capUsd);
    if (reason) {
      setRefusal(reason);
      return;
    }
    setRefusal(null);
    onRun?.();
  }
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
      <button
        type="button"
        onClick={handleClick}
        className="bg-primary text-primary-foreground focus-ring"
        style={{ padding: "6px 12px", borderRadius: 0, border: "none", cursor: "pointer" }}
      >
        Enrich
      </button>
      <span className="text-muted-foreground" style={{ fontSize: 13 }}>
        Enrich costs up to ${capUsd.toFixed(2)} a press
      </span>
      {refusal && (
        <span role="alert" className="text-danger" style={{ fontSize: 13 }}>
          {refusal}
        </span>
      )}
    </div>
  );
}

// SG-113: the asset-detail location section. It reads the tree from the
// flag-gated list route: when the backend is dormant the route answers 404,
// the query errors, and the WHOLE section is hidden (no error, no fallback
// list). When enabled it shows the assigned locations and an assign select.
export function LocationsSection({
  asset,
  householdId,
}: {
  asset: Asset;
  householdId: string;
}) {
  const qc = useQueryClient();
  const { data: all, isError } = useQuery<LocationListResponse>({
    queryKey: ["locations", householdId],
    queryFn: () => fetchLocations(householdId),
    retry: false,
  });
  const assignMut = useMutation({
    mutationFn: (locationId: string) => assignAssetLocation(asset.id, locationId, householdId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["asset", asset.id] }),
  });
  const unassignMut = useMutation({
    mutationFn: (locationId: string) => unassignAssetLocation(asset.id, locationId, householdId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["asset", asset.id] }),
  });
  if (isError || !all) return null;
  const assigned = asset.locations || [];
  const assignedIds = new Set(assigned.map((l) => l.id));
  const available = all.items.filter((l) => !assignedIds.has(l.id));
  return (
    <section style={{ marginBottom: 16 }}>
      <h3>Locations</h3>
      {assigned.length === 0 ? (
        <div className="text-muted-foreground" style={{ fontSize: 13 }}>No locations assigned</div>
      ) : (
        <ul style={{ fontSize: 13, paddingLeft: 18 }}>
          {assigned.map((l) => (
            <li key={l.id} style={{ marginBottom: 4 }}>
              {l.name}{" "}
              <button
                type="button"
                onClick={() => unassignMut.mutate(l.id)}
                className="bg-card text-foreground border-border focus-ring"
                style={{ padding: "2px 8px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, cursor: "pointer", fontSize: 13 }}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      <select
        aria-label="Assign location"
        value=""
        onChange={(e) => {
          if (e.target.value) assignMut.mutate(e.target.value);
        }}
        className="bg-background text-foreground border-border focus-ring"
        style={{ padding: 6, borderRadius: 0, borderStyle: "solid", borderWidth: 1, fontSize: 13, maxWidth: "100%" }}
      >
        <option value="">Assign to location…</option>
        {available.map((l) => (
          <option key={l.id} value={l.id}>{l.name}</option>
        ))}
      </select>
    </section>
  );
}

// SG-114: the asset-detail relation section. It reads the flag-gated list
// route: when the backend is dormant the route answers 404, the query errors,
// and the WHOLE section is hidden (no error, no fallback list). When enabled it
// lists BOTH directions (each row labelled from this asset), creates a typed
// link, and deletes one. The target picker reads the always-on catalog list.
export function RelationsSection({
  asset,
  householdId,
}: {
  asset: Asset;
  householdId: string;
}) {
  const qc = useQueryClient();
  const { data: rels, isError } = useQuery<RelationListResponse>({
    queryKey: ["relations", asset.id, householdId],
    queryFn: () => fetchRelations(asset.id, householdId),
    retry: false,
  });
  const { data: assets } = useQuery<AssetListResponse>({
    queryKey: ["household-assets", householdId],
    queryFn: () => fetchHouseholdAssets(householdId),
    retry: false,
    enabled: !!rels,
  });
  const createMut = useMutation({
    mutationFn: (vars: { toAssetId: string; relationType: string }) =>
      createRelation(asset.id, vars.toAssetId, vars.relationType, householdId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["relations", asset.id, householdId] }),
  });
  const deleteMut = useMutation({
    mutationFn: (relationId: string) => deleteRelation(asset.id, relationId, householdId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["relations", asset.id, householdId] }),
  });
  const [toAssetId, setToAssetId] = useState("");
  const [relationType, setRelationType] = useState("related_to");
  if (isError || !rels) return null;
  const items = rels.items;
  const nameById = new Map((assets?.items ?? []).map((a) => [a.id, a.display_name || "Unnamed item"]));
  const otherId = (rel: AssetRelation) =>
    rel.direction === "outgoing" ? rel.to_asset_id : rel.from_asset_id;
  const options = (assets?.items ?? []).filter((a) => a.id !== asset.id);
  const selectStyle = {
    padding: 6,
    borderRadius: 0,
    borderStyle: "solid" as const,
    borderWidth: 1,
    fontSize: 13,
    maxWidth: "100%",
  };
  return (
    <section style={{ marginBottom: 16 }}>
      <h3>Related assets</h3>
      {items.length === 0 ? (
        <div className="text-muted-foreground" style={{ fontSize: 13 }}>No related assets</div>
      ) : (
        <ul style={{ fontSize: 13, paddingLeft: 18 }}>
          {items.map((rel) => (
            <li key={rel.id} style={{ marginBottom: 4 }}>
              {nameById.get(otherId(rel)) ?? "Unnamed item"}{" "}
              <span style={{ color: "hsl(var(--ink-muted))" }}>
                ({rel.relation_type === "contains" ? "Contains" : "Related"})
              </span>{" "}
              <button
                type="button"
                onClick={() => deleteMut.mutate(rel.id)}
                className="bg-card text-foreground border-border focus-ring"
                style={{ padding: "2px 8px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, cursor: "pointer", fontSize: 13 }}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <select
          aria-label="Related asset"
          value={toAssetId}
          onChange={(e) => setToAssetId(e.target.value)}
          className="bg-background text-foreground border-border focus-ring"
          style={selectStyle}
        >
          <option value="">Select asset…</option>
          {options.map((a) => (
            <option key={a.id} value={a.id}>{a.display_name || "Unnamed item"}</option>
          ))}
        </select>
        <select
          aria-label="Relation type"
          value={relationType}
          onChange={(e) => setRelationType(e.target.value)}
          className="bg-background text-foreground border-border focus-ring"
          style={selectStyle}
        >
          <option value="related_to">Related</option>
          <option value="contains">Contains</option>
        </select>
        <button
          type="button"
          disabled={!toAssetId || createMut.isPending}
          onClick={() => createMut.mutate({ toAssetId, relationType })}
          className={`${toAssetId ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"} border-border focus-ring`}
          style={{ padding: "6px 12px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
        >
          {createMut.isPending ? "Linking..." : "Link"}
        </button>
      </div>
    </section>
  );
}

function valueRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

function plainFieldLabel(fieldPath: string): string {
  const lower = fieldPath.toLowerCase();
  if (lower.includes("classification") || lower.includes("category_proposed")) return "Shelf life";
  if (lower.includes("expiry_date") || lower.includes("expiry")) return "Expiry date";
  if (lower.includes("gone")) return "Gone reason";
  if (lower.includes("display_name")) return "Name";
  if (lower.includes("quantity")) return "Amount";
  if (lower.includes("condition")) return "Condition";
  if (lower.includes("location")) return "Location";
  if (lower.includes("asset_type") || lower === "category" || lower.endsWith("/category")) return "Kind of item";
  if (lower.includes("status")) return "Status";
  if (lower.includes("unit")) return "Unit";
  // SG-318 W2: never the bare "Detail" — humanize the last segment instead.
  const last = fieldPath.split("/").pop()?.split(":").pop() ?? fieldPath;
  const words = last.replace(/[_.]+/g, " ").trim();
  if (!words) return "Detail";
  return words.replace(/\b\w/g, (c) => c.toUpperCase());
}

function plainSourceLabel(sourceType: string): string {
  if (sourceType === "user") return "You";
  if (sourceType === "deterministic") return "Rule";
  if (sourceType === "extraction") return "Photo read";
  if (sourceType.startsWith("web:")) return "Web";
  return sourceType.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function plainStatusLabel(status: string): string {
  const key = (status ?? "").toUpperCase();
  if (key === "ACTIVE") return "Live";
  if (key === "ARCHIVED") return "Gone";
  return (status ?? "").replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) || "—";
}

/**
 * SG-318 W2: every Details value in owner words — never "[object Object]".
 * Objects unpack to their meaningful field (a category through
 * labelAssetType, a date through the shared formatPlainDate, a status
 * through the label map); anything else reads "—", never raw JSON.
 */
function plainDetailValue(fieldPath: string, value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string") {
    const lower = fieldPath.toLowerCase();
    if (lower.includes("classification") || lower.includes("category_proposed") || lower.includes("asset_type") || lower === "category" || lower.endsWith("/category"))
      return labelAssetType(value);
    if (lower.includes("expiry_date") || lower.includes("expiry")) {
      const dated = formatPlainDate(value);
      return dated || value;
    }
    if (lower.includes("status")) return plainStatusLabel(value);
    return value === "" ? "—" : value;
  }
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) {
    if (value.length === 0) return "—";
    return value.map((entry) => plainDetailValue(fieldPath, entry)).join(", ");
  }
  if (typeof value === "object") {
    const rec = value as Record<string, unknown>;
    if (typeof rec.category === "string") return labelAssetType(rec.category);
    if (typeof rec.expiry_date === "string") return formatPlainDate(rec.expiry_date) || "—";
    if (typeof rec.value === "string" || typeof rec.value === "number") return plainDetailValue(fieldPath, rec.value);
    if (typeof rec.label === "string") {
      const lower = fieldPath.toLowerCase();
      if (lower.includes("classification") || lower.includes("category") || lower.includes("asset_type")) return labelAssetType(rec.label);
      return rec.label || "—";
    }
    if (typeof rec.status === "string") {
      const lower = fieldPath.toLowerCase();
      if (lower.includes("expiry")) return labelExpiryState(rec.status);
      return plainStatusLabel(rec.status);
    }
    if (typeof rec.reason === "string") return plainStatusLabel(rec.reason);
    return "—";
  }
  return String(value);
}

function plainActionLabel(action: string): string {
  const key = (action ?? "").toLowerCase();
  // SG-318 W3: audit actions in plain words.
  if (key === "asset.create" || key === "asset.lifecycle.created" || key === "asset_create") return "Added";
  if (key === "asset.accepted" || key === "asset_accepted") return "Accepted";
  if (key === "asset.update" || key === "asset.lifecycle.updated") return "Updated";
  if (key === "asset.attach_evidence") return "Photo added";
  if (key === "asset.gone" || key === "asset.archive") return "Marked gone";
  if (key === "asset.put_back") return "Put back";
  if (key === "asset.quantity_adjust") return "Amount changed";
  if (key === "asset.merge") return "Combined";
  if (key.includes("expiry") && (key.includes("manual") || key.includes("enter"))) return "Date entered by you";
  if (key.includes("expiry_date") || key.includes("expiry date")) return "Date entered by you";
  return action.replace(/[_.:]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function latestActiveAssertion(assertions: Assertion[], fieldPath: string): Assertion | null {
  return (
    assertions
      .filter(
        (item) =>
          item.field_path === fieldPath &&
          item.review_state !== "superseded" &&
          item.review_state !== "rejected"
      )
      .sort((a, b) => (b.created_at ?? "").localeCompare(a.created_at ?? ""))[0] ?? null
  );
}

export function AssetDetailPage() {
  const { id } = useParams();
  const [search] = useSearchParams();
  const householdId = search.get("household_id") || localStorage.getItem("household_id") || "";
  const { data: asset, isLoading } = useAsset(householdId, id || "");
  const { data: taxonomy } = useTaxonomy();
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editQuantity, setEditQuantity] = useState("");
  const [editUnit, setEditUnit] = useState("");
  const [editCondition, setEditCondition] = useState("");
  const [attachFiles, setAttachFiles] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [classificationChoice, setClassificationChoice] = useState<string | null>(null);
  const [classificationMessage, setClassificationMessage] = useState<string | null>(null);
  const [classificationError, setClassificationError] = useState<string | null>(null);
  const [goneMessage, setGoneMessage] = useState<string | null>(null);
  const [goneError, setGoneError] = useState<string | null>(null);
  const [qtyMessage, setQtyMessage] = useState<string | null>(null);
  const [qtyError, setQtyError] = useState<string | null>(null);

  const assertions = asset?.assertions || [];
  const classificationAssertion = latestActiveAssertion(
    assertions,
    "plugin:expiry-tracker/classification"
  );
  const classificationValue = valueRecord(classificationAssertion?.value);
  const currentCategory =
    typeof classificationValue?.category === "string" ? classificationValue.category : "";
  const profile = valueRecord(classificationValue?.profile);
  const hasProfileTierDefaults =
    profile !== null && Object.prototype.hasOwnProperty.call(profile, "tier_defaults");
  const profileTierDefaults = valueRecord(profile?.tier_defaults);
  const taxonomyCategories =
    taxonomy?.plugins.find((plugin) => plugin.plugin_id === "expiry-tracker")?.categories ?? [];
  const activeCategories = taxonomyCategories.filter((category) => category.active);
  const taxonomyCategory = activeCategories.find((category) => category.id === currentCategory);
  const hasWindows =
    classificationAssertion !== null &&
    (hasProfileTierDefaults
      ? Object.keys(profileTierDefaults ?? {}).length > 0
      : (taxonomyCategory?.notification ?? "none") !== "none");
  const selectedCategory = classificationChoice ?? currentCategory;
  // SG-271 G3 (F5/F12): the AI's shelf-life suggestion preselects the control
  // until the user confirms. It never classifies by itself — saving is the
  // user's explicit Confirm.
  const proposedAssertion =
    assertions.find(
      (entry) => entry.field_path === "category_proposed" || entry.field_path.endsWith("/category_proposed")
    ) ?? null;
  const proposedRaw =
    valueRecord(proposedAssertion?.value)?.value ?? proposedAssertion?.value;
  const proposedText = typeof proposedRaw === "string" ? proposedRaw : null;
  const normalizeShelfLife = (text: string) => text.trim().toLowerCase().replace(/[_\-\s]+/g, "");
  const suggestedCategory =
    proposedText !== null
      ? activeCategories.find((entry) => normalizeShelfLife(entry.id) === normalizeShelfLife(proposedText))?.id ?? null
      : null;
  const suggestedName =
    suggestedCategory !== null
      ? activeCategories.find((entry) => entry.id === suggestedCategory)?.name ?? suggestedCategory
      : null;
  const effectiveCategory = selectedCategory || suggestedCategory || "";
  const expiryAssertion = latestActiveAssertion(
    assertions,
    "plugin:expiry-tracker/expiry_date"
  );
  const expiryValue = valueRecord(expiryAssertion?.value);
  const hasActiveDate = typeof expiryValue?.expiry_date === "string";

  const classifyMut = useMutation({
    mutationFn: (category: string) =>
      classifyAsset(asset?.id ?? "", householdId, category, classificationAssertion?.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      setClassificationChoice(null);
      setClassificationMessage("Shelf life saved.");
      setClassificationError(null);
    },
    onError: (caught: unknown) => {
      const text = caught instanceof Error ? caught.message : String(caught);
      setClassificationError(text);
      setClassificationMessage(null);
      if (/changed|409/i.test(text)) {
        qc.invalidateQueries({ queryKey: ["asset", id] });
        setClassificationChoice(null);
      }
    },
  });

  const patchMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      apiPatch(`/v1/assets/${id}`, payload, { household_id: householdId }, { "If-Match": String(asset?.version ?? 1) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      setEditing(false);
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  const goneMut = useMutation({
    mutationFn: (reason: GoneReason) => markGone(asset?.id ?? "", householdId, reason),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      qc.invalidateQueries({ queryKey: ["assets"] });
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
    mutationFn: () => putBack(asset?.id ?? "", householdId),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      setGoneMessage(`“${updated.display_name || "Item"}” is back in your catalog.`);
      setGoneError(null);
    },
    onError: (e: unknown) => {
      setGoneError(e instanceof Error ? e.message : String(e));
      setGoneMessage(null);
    },
  });

  const decMut = useMutation({
    mutationFn: () => decrementQuantity(asset?.id ?? "", householdId),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      setQtyError(null);
      setQtyMessage(updated.quantity != null ? `Now ${updated.quantity} left.` : "Quantity changed.");
    },
    onError: (e: unknown) => {
      setQtyError(e instanceof Error ? e.message : String(e));
      setQtyMessage(null);
    },
  });

  const incMut = useMutation({
    mutationFn: () => incrementQuantity(asset?.id ?? "", householdId),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      setQtyError(null);
      setQtyMessage(updated.quantity != null ? `Now ${updated.quantity} left.` : "Quantity changed.");
    },
    onError: (e: unknown) => {
      setQtyError(e instanceof Error ? e.message : String(e));
      setQtyMessage(null);
    },
  });

  const attachMut = useMutation({
    mutationFn: async () => {
      if (!attachFiles?.length || !id) throw new Error("No files selected");
      const ids: string[] = [];
      for (const f of Array.from(attachFiles)) {
        const ev = await uploadEvidence(householdId, f);
        ids.push(ev.id);
      }
      return apiPost(`/v1/assets/${id}/evidence`, { evidence_ids: ids }, { household_id: householdId });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      setAttachFiles(null);
      (document.getElementById("attach-input") as HTMLInputElement | null)?.value &&
        ((document.getElementById("attach-input") as HTMLInputElement).value = "");
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  // SG-098: the manual Enrich trigger. The button itself already gates the
  // press through `enrichCapRefusal`; this handler only runs under the cap.
  // SG-119: the press response carries the web alternates. They are rendered
  // beside the button (the asset-detail brand surface); a press is still the
  // only way this page can see them until a GET job->candidate path exists.
  const enrichMut = useMutation({
    mutationFn: () => apiPost<EnrichResponse>(`/v1/enrich/${id}`, {}, { household_id: householdId }),
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  if (isLoading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (!asset) return <div style={{ padding: 24 }}>Asset not found — <Link to="/">back to catalog</Link></div>;

  const evidence = (asset as unknown as { evidence: { id: string; storage_key: string; sha256: string; original_filename: string }[] }).evidence || [];
  const audits = (asset as unknown as { audit_events: { id: string; action: string; actor: string; timestamp: string; before: unknown; after: unknown }[] }).audit_events || [];
  const displayName = asset.display_name || UNTITLED_ASSET_NAME;
  const goneFromPayload = goneReasonLabel(asset.gone_reason);
  const goneFromAssertion = (() => {
    const entry = latestActiveAssertion(assertions, "gone.reason");
    if (!entry) return null;
    const value = valueRecord(entry.value);
    const raw = value ? value["reason"] : entry.value;
    return goneReasonLabel(typeof raw === "string" ? raw : null);
  })();
  const goneLabel = goneFromPayload ?? goneFromAssertion;
  const isGone = asset.status === "ARCHIVED" || goneLabel !== null;
  const counted = isCountedUnit(asset.unit);
  const qtyValue = asset.quantity ?? null;
  const noneLeft = !isGone && counted && (qtyValue ?? 0) <= 0;
  const saveClassification = () => {
    if (!effectiveCategory || classifyMut.isPending) return;
    if (
      effectiveCategory === "non_perishable" &&
      hasActiveDate &&
      !window.confirm("This will clear the active date; the old value stays in the audit.")
    ) {
      return;
    }
    classifyMut.mutate(effectiveCategory);
  };

  return (
    <PageContainer className="text-foreground">
      <Link to={`/?household_id=${householdId}`} className="text-link focus-ring" style={{ fontSize: 13 }}>← Back to catalog</Link>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 12, marginTop: 8 }}>
        <h1 className="page-header text-foreground" style={{ margin: 0, minWidth: 0, overflowWrap: "anywhere" }}>{displayName}</h1>
        <button
          onClick={() => {
            setEditName(asset.display_name ?? "");
            setEditQuantity(asset.quantity != null ? String(asset.quantity) : "");
            setEditUnit(asset.unit ?? "");
            setEditCondition(asset.condition ?? "");
            setEditing((v) => !v);
          }}
          className="bg-card text-foreground border-border focus-ring"
          style={{ padding: "6px 12px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
        >
          {editing ? "Cancel" : "Edit"}
        </button>
      </div>
      <div style={{ marginBottom: 13, fontSize: 13, color: "hsl(var(--ink-muted))" }}>
        {isGone ? `Gone${goneLabel ? ` — ${goneLabel}` : ""}` : "Live"}
        {asset.quantity != null && <> · {quantityLeftText(asset.quantity, asset.unit, counted)}</>}
        {asset.condition && <> · {asset.condition}</>}
      </div>

      <div style={{ marginBottom: 16 }}>
        <EnrichButton lastSpendUsd={null} onRun={() => enrichMut.mutate()} />
      </div>

      <WebAlternates alternates={enrichMut.data?.web_alternates ?? []} />

      <section style={{ marginBottom: 16 }}>
        <h3>Shelf life</h3>
        {activeCategories.length === 0 ? (
          <div className="text-muted-foreground" style={{ fontSize: 13 }}>
            No shelf life options are available.
          </div>
        ) : (
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <select
              aria-label="Shelf life"
              value={effectiveCategory}
              onChange={(event) => setClassificationChoice(event.target.value)}
              className="bg-background text-foreground border-border focus-ring"
              style={{ padding: 6, borderRadius: 0, borderStyle: "solid", borderWidth: 1, fontSize: 13, maxWidth: "100%" }}
            >
              {effectiveCategory === "" && <option value="">Select a shelf life…</option>}
              {activeCategories.map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>
            <button
              type="button"
              onClick={saveClassification}
              disabled={!effectiveCategory || classifyMut.isPending}
              className="bg-primary text-primary-foreground focus-ring"
              style={{ padding: "6px 12px", borderRadius: 0, border: "none", cursor: "pointer" }}
            >
              {classifyMut.isPending ? "Saving…" : "Save shelf life"}
            </button>
          </div>
        )}
        {!classificationAssertion && suggestedName && (
          <div role="status" className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
            The AI suggests {suggestedName}. Confirm below, or pick another shelf life.
          </div>
        )}
        {!classificationAssertion && !suggestedName && proposedText && (
          <div role="status" className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
            The AI suggested “{proposedText}”, which matches no shelf life — pick the closest one below.
          </div>
        )}
        {!classificationAssertion && (
          <div role="status" className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
            Choose a shelf life, then add a date if it has one.
          </div>
        )}
        {effectiveCategory === "documents_other" && (
          <div className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
            Documents/other: renewal or validity dates. Keepsakes, letters and photos belong under Non-perishable.
          </div>
        )}
        {effectiveCategory === "non_perishable" && (
          <div className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
            No date; no expiry reminder.
          </div>
        )}
        {classificationMessage && (
          <div role="status" className="text-success" style={{ fontSize: 13, marginTop: 6 }}>{classificationMessage}</div>
        )}
        {classificationError && (
          <div role="alert" className="text-danger" style={{ fontSize: 13, marginTop: 6 }}>{classificationError}</div>
        )}
      </section>

      <section aria-label="Amount left" style={{ marginBottom: 16 }}>
        <h3>Amount left</h3>
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
            <span className="text-foreground" style={{ fontSize: 13 }}>
              {quantityLeftText(qtyValue, asset.unit, counted)}
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
            {quantityLeftText(qtyValue, asset.unit, counted)} — change the amount with Edit above.
          </div>
        )}
        {noneLeft && (
          <div role="status" className="text-muted-foreground" style={{ fontSize: 13, marginTop: 6 }}>
            None left — mark it gone below.
          </div>
        )}
        {qtyMessage && (
          <div role="status" className="text-success" style={{ fontSize: 13, marginTop: 6 }}>{qtyMessage}</div>
        )}
        {qtyError && (
          <div role="alert" className="text-danger" style={{ fontSize: 13, marginTop: 6 }}>{qtyError}</div>
        )}
      </section>

      <section aria-label="Use it up" style={{ marginBottom: 16 }}>
        <h3>Use it up</h3>
        {isGone ? (
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <span role="status" className="text-muted-foreground" style={{ fontSize: 13 }}>
              Gone{goneLabel ? ` — ${goneLabel.toLowerCase()}` : ""}
            </span>
            <button
              type="button"
              onClick={() => putBackMut.mutate()}
              disabled={putBackMut.isPending}
              className="bg-primary text-primary-foreground focus-ring"
              style={{ padding: "6px 12px", borderRadius: 0, border: "none", cursor: "pointer" }}
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
                style={CONTROL_STYLE}
              >
                {goneReasonLabel(reason)}
              </button>
            ))}
          </div>
        )}
        {goneMessage && (
          <div role="status" className="text-success" style={{ fontSize: 13, marginTop: 6 }}>{goneMessage}</div>
        )}
        {goneError && (
          <div role="alert" className="text-danger" style={{ fontSize: 13, marginTop: 6 }}>{goneError}</div>
        )}
      </section>

      <LocationsSection asset={asset} householdId={householdId} />

      <RelationsSection asset={asset} householdId={householdId} />

      {editing && (
        <div style={{ borderRadius: 0, padding: 12, marginBottom: 16, borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", backgroundColor: "hsl(var(--paper))" }}>
          <div style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: 8, alignItems: "center" }}>
            <label htmlFor="edit-display-name" style={{ fontSize: 13 }}>Display name</label>
            <input id="edit-display-name" value={editName} onChange={(e) => setEditName(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 0, borderStyle: "solid", borderWidth: 1 }} />
            <label htmlFor="edit-quantity" style={{ fontSize: 13 }}>Quantity</label>
            <input id="edit-quantity" type="number" value={editQuantity} onChange={(e) => setEditQuantity(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 0, borderStyle: "solid", borderWidth: 1 }} />
            <label htmlFor="edit-unit" style={{ fontSize: 13 }}>Unit</label>
            <input id="edit-unit" value={editUnit} onChange={(e) => setEditUnit(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 0, borderStyle: "solid", borderWidth: 1 }} />
            <label htmlFor="edit-condition" style={{ fontSize: 13 }}>Condition</label>
            <input id="edit-condition" value={editCondition} onChange={(e) => setEditCondition(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 0, borderStyle: "solid", borderWidth: 1 }} />
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10 }}>
            <button
              onClick={() => {
                const payload: Record<string, unknown> = { display_name: editName.trim() };
                if (editQuantity.trim() !== "") payload.quantity = Number(editQuantity);
                if (editUnit.trim() !== "") payload.unit = editUnit.trim();
                if (editCondition.trim() !== "") payload.condition = editCondition.trim();
                patchMut.mutate(payload);
              }}
              disabled={patchMut.isPending || !editName.trim()}
              className="bg-primary text-primary-foreground focus-ring"
              style={{ padding: "6px 12px", borderRadius: 0, border: "none", cursor: "pointer" }}
            >
              {patchMut.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </div>
      )}

      {error && <div className="text-danger" style={{ fontSize: 13, marginBottom: 12 }}>{error}</div>}

      {hasWindows && hasActiveDate && expiryAssertion?.review_state === "accepted" && (
        <div className="text-muted-foreground" style={{ fontSize: 13, marginTop: 8 }}>
          The date is kept when the category changes; check it still applies.
        </div>
      )}

      {classificationAssertion && hasWindows && (
        <ExpiryEntryForm
          key={expiryAssertion?.id ?? "no-expiry"}
          assetId={asset.id}
          householdId={householdId}
          evidenceIds={evidence.map((item) => item.id)}
          activeAssertion={expiryAssertion}
          categorySlug={currentCategory}
          hasWindows={hasWindows}
        />
      )}

      <h3 className="detail-heading">Evidence</h3>
      <EvidenceGallery evidence={evidence} householdId={householdId} />
      <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
        <input id="attach-input" type="file" multiple accept="image/*,.pdf" onChange={(e) => setAttachFiles(e.target.files)} />
        <button
          onClick={() => attachMut.mutate()}
          disabled={attachMut.isPending || !attachFiles?.length}
          className={`${attachFiles?.length ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"} border-border focus-ring`}
          style={{ padding: "6px 12px", borderRadius: 0, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
        >
          {attachMut.isPending ? "Attaching..." : "Attach evidence"}
        </button>
      </div>

      <h3 className="detail-heading">Details</h3>
      {assertions.length === 0 ? (
        <div style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>No details</div>
      ) : (
        <table className="detail-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Detail</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Value</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Source</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>State</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Confidence</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {assertions.map((a) => (
              <tr key={a.id}>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1, fontSize: 13 }}>{plainFieldLabel(a.field_path)}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>{plainDetailValue(a.field_path, a.value)}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>{plainSourceLabel(a.source_type)}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>
                  <ProvenanceBadge state={a.review_state} />
                </td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>{a.confidence != null ? String(a.confidence) : "—"}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1, fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                  {a.source_evidence_ids?.length ? `${a.source_evidence_ids.length} attached` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h3 className="detail-heading">History</h3>
      {audits.length === 0 ? (
        <div style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>No history</div>
      ) : (
        <ul style={{ fontSize: 13, paddingLeft: 18 }}>
          {audits.map((e) => (
            <li key={e.id} style={{ marginBottom: 4 }}>
              {plainActionLabel(e.action)} — {formatJobDate(e.timestamp) || "—"}
            </li>
          ))}
        </ul>
      )}
    </PageContainer>
  );
}
