import type { Asset, Evidence, Job } from "../api/types";

/**
 * The canonical DQ1 taxonomy. Custom categories are user-extensible: any string
 * that is not one of these passes through `toProductCategory` unchanged.
 */
export const CANONICAL_CATEGORIES = [
  "Hardware & Tools",
  "Electronics & Gadgets",
  "Apparel & Textiles",
  "Home & Decor",
  "Packaging & Materials",
  "Uncategorized",
] as const;

export type CanonicalCategory = (typeof CANONICAL_CATEGORIES)[number];

export type ProductStatus = "raw" | "processed" | "rendered" | "failed";

/**
 * Display-only fallback for an asset captured without a name and without a
 * photo to derive one from. Never written to the database and never a promise
 * of AI naming.
 */
export const UNTITLED_ASSET_NAME = "Untitled asset";

export type ProductMetadata = {
  dimensions?: string;
  primaryColors?: string[];
  material?: string;
  notes?: string;
};

export type ProductItem = {
  id: string;
  name: string;
  category: string;
  description?: string;
  tags: string[];
  dateAdded: string;
  status: ProductStatus;
  metadata: ProductMetadata;
};

export type BoundingBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type AssetMedia = {
  originalUrl: string;
  isolatedCutoutUrl?: string;
  sceneRenderUrl?: string;
  boundingBox?: BoundingBox;
};

export type RenderJobStatus = "idle" | "processing" | "completed" | "failed";

export type RenderModelInfo = {
  provider: string;
  model: string;
  executedAt: string;
  latencyMs: number;
};

export type RenderJob = {
  jobId: string;
  status: RenderJobStatus;
  modelInfo?: RenderModelInfo;
};

// ⚡ Bolt Optimization: Map canonical categories to lower-case for O(1) hash map lookup
// replacing O(N) array scan (.find()) per asset during rendering/filtering.
const CANONICAL_CATEGORY_MAP = new Map<string, string>(
  CANONICAL_CATEGORIES.map((category) => [category.toLowerCase(), category])
);

export function toProductCategory(assetType: string): string {
  const trimmed = (assetType ?? "").trim();
  if (!trimmed) return "Uncategorized";
  const lower = trimmed.toLowerCase();
  if (lower === "unknown") return "Uncategorized";
  return CANONICAL_CATEGORY_MAP.get(lower) ?? trimmed;
}

export function assetToProductItem(asset: Asset): ProductItem {
  return {
    id: asset.id,
    name: asset.display_name || UNTITLED_ASSET_NAME,
    category: toProductCategory(asset.asset_type),
    // description: not carried by Asset; the SG-047 import modal supplies it.
    // tags: populated by the SG-045 grid mocks / SG-047 import modal.
    tags: [],
    dateAdded: asset.created_at,
    // DQ10 initial state; media-derived status arrives with the AI-derivation slices.
    status: "raw",
    // dimensions/primaryColors/material/notes: not carried by Asset yet; SG-046 fills them.
    metadata: {},
  };
}

export function evidenceToAssetMedia(
  evidence: Evidence,
  options: { householdId: string; baseUrl?: string }
): AssetMedia {
  const base =
    options.baseUrl ?? import.meta.env.VITE_API_BASE ?? "http://localhost:8003";
  return {
    // Route mirrors EvidenceGallery.tsx:11 — original file stream, not the thumb.
    originalUrl: `${base}/v1/evidence/${evidence.id}/file?household_id=${options.householdId}`,
    // isolatedCutoutUrl / sceneRenderUrl: absent until the S3-era image-derivation work.
    // boundingBox: absent until an isolation model emits normalized 0-1 fractions (DQ4).
  };
}

const JOB_STATE_MAP: Record<string, RenderJobStatus> = {
  idle: "idle",
  queued: "idle",
  pending: "idle",
  processing: "processing",
  running: "processing",
  in_progress: "processing",
  completed: "completed",
  succeeded: "completed",
  success: "completed",
  failed: "failed",
  error: "failed",
  errored: "failed",
};

export function jobToRenderJob(job: Job): RenderJob {
  const state = (job.state ?? "").toLowerCase();
  return {
    jobId: job.id,
    // Explicit DQ10 default: an unmapped state is treated as not-yet-started.
    status: JOB_STATE_MAP[state] ?? "idle",
    // modelInfo: filled once renders read the provider ledger (SG-046+, DQ4).
  };
}
