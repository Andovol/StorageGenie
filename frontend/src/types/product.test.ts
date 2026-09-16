import { describe, expect, test } from "vitest";
import type { Asset, Evidence, Job } from "../api/types";
import type { AssetMedia } from "./product";
import {
  CANONICAL_CATEGORIES,
  assetToProductItem,
  evidenceToAssetMedia,
  jobToRenderJob,
  toProductCategory,
} from "./product";

const asset: Asset = {
  id: "a1",
  household_id: "h1",
  display_name: "Oxford Shirt",
  asset_type: "Apparel & Textiles",
  status: "ACTIVE",
  quantity: null,
  unit: null,
  condition: null,
  version: 1,
  created_at: "2026-09-16T10:00:00Z",
  updated_at: null,
};

const evidence: Evidence = {
  id: "e1",
  sha256: "abc123",
  storage_key: "households/h1/e1.jpg",
  media_type: "image/jpeg",
  original_filename: "shirt.jpg",
  size_bytes: 1234,
};

const job: Job = {
  id: "j1",
  job_type: "render",
  state: "processing",
  household_id: "h1",
  created_at: null,
  updated_at: null,
};

function hasRawResponseKey(value: unknown): boolean {
  if (value === null || typeof value !== "object") return false;
  if (Object.prototype.hasOwnProperty.call(value, "rawResponse")) return true;
  return Object.values(value as Record<string, unknown>).some(hasRawResponseKey);
}

describe("CANONICAL_CATEGORIES", () => {
  test("exports the DQ1 six canonical categories exactly", () => {
    expect(CANONICAL_CATEGORIES).toEqual([
      "Hardware & Tools",
      "Electronics & Gadgets",
      "Apparel & Textiles",
      "Home & Decor",
      "Packaging & Materials",
      "Uncategorized",
    ]);
  });

  test("custom categories pass through and canonical casing is normalised", () => {
    expect(toProductCategory("Vintage Denim")).toBe("Vintage Denim");
    expect(toProductCategory("hardware & tools")).toBe("Hardware & Tools");
    expect(toProductCategory("")).toBe("Uncategorized");
    expect(toProductCategory("unknown")).toBe("Uncategorized");
  });
});

describe("assetToProductItem", () => {
  test("maps display_name to name and created_at to dateAdded", () => {
    const item = assetToProductItem(asset);
    expect(item.id).toBe("a1");
    expect(item.name).toBe("Oxford Shirt");
    expect(item.category).toBe("Apparel & Textiles");
    expect(item.dateAdded).toBe("2026-09-16T10:00:00Z");
  });

  test("status defaults to raw and tags start empty", () => {
    const item = assetToProductItem(asset);
    expect(item.status).toBe("raw");
    expect(item.tags).toEqual([]);
  });

  test("carries no rawResponse key", () => {
    expect(hasRawResponseKey(assetToProductItem(asset))).toBe(false);
  });
});

describe("evidenceToAssetMedia", () => {
  test("builds originalUrl on the EvidenceGallery route", () => {
    const media = evidenceToAssetMedia(evidence, { householdId: "h1", baseUrl: "http://api.test" });
    expect(media.originalUrl).toBe("http://api.test/v1/evidence/e1/file?household_id=h1");
  });

  test("leaves cutout, scene and boundingBox absent until the S3 era", () => {
    const media = evidenceToAssetMedia(evidence, { householdId: "h1", baseUrl: "http://api.test" });
    expect(media.isolatedCutoutUrl).toBeUndefined();
    expect(media.sceneRenderUrl).toBeUndefined();
    expect(media.boundingBox).toBeUndefined();
    expect(hasRawResponseKey(media)).toBe(false);
  });

  test("boundingBox fractions stay within 0-1 when supplied", () => {
    const media = evidenceToAssetMedia(evidence, { householdId: "h1", baseUrl: "http://api.test" });
    const withBox: AssetMedia = { ...media, boundingBox: { x: 0.1, y: 0.2, width: 0.3, height: 0.4 } };
    for (const fraction of Object.values(withBox.boundingBox!)) {
      expect(fraction).toBeGreaterThanOrEqual(0);
      expect(fraction).toBeLessThanOrEqual(1);
    }
  });
});

describe("jobToRenderJob", () => {
  test("maps known states", () => {
    expect(jobToRenderJob(job).jobId).toBe("j1");
    expect(jobToRenderJob({ ...job, state: "queued" }).status).toBe("idle");
    expect(jobToRenderJob({ ...job, state: "processing" }).status).toBe("processing");
    expect(jobToRenderJob({ ...job, state: "succeeded" }).status).toBe("completed");
    expect(jobToRenderJob({ ...job, state: "failed" }).status).toBe("failed");
  });

  test("unmapped job states fall back to idle", () => {
    expect(jobToRenderJob({ ...job, state: "some-future-state" }).status).toBe("idle");
  });

  test("carries no rawResponse key", () => {
    expect(hasRawResponseKey(jobToRenderJob(job))).toBe(false);
  });
});
