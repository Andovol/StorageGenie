import { describe, expect, test, vi, afterEach, beforeEach } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { HouseholdProvider } from "../hooks/HouseholdContext";
import { ProductCard } from "../components/catalog/ProductCard";
import { EvidenceGallery } from "../components/EvidenceGallery";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import { AssetDetailPage } from "./AssetDetailPage";
import { ExpiryPage } from "./ExpiryPage";
import {
  UNNAMED_ITEM,
  formatPlainDate,
  formatJobDate,
  labelAssetType,
  labelStepName,
  labelStepState,
} from "../lib/labels";
import { UNTITLED_ASSET_NAME, assetToProductItem } from "../types/product";
import type { ReactNode } from "react";

// Shared mocks
const household = { id: "hh-sg318", name: "SG-318 home", created_at: "2026-01-01" };

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
  enterManualExpiry: vi.fn(),
  clearExpiryDate: vi.fn(),
  classifyAsset: vi.fn(),
  fetchLocations: vi.fn(),
  assignAssetLocation: vi.fn(),
  unassignAssetLocation: vi.fn(),
  fetchRelations: vi.fn(),
  createRelation: vi.fn(),
  deleteRelation: vi.fn(),
  fetchHouseholdAssets: vi.fn(),
}));
vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  ...api,
}));
vi.mock("../hooks/useAssets", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../hooks/useAssets")>()),
  useHouseholds: () => ({ data: [household] }),
}));

const taxonomy = {
  plugins: [
    {
      plugin_id: "expiry-tracker",
      version: "1.0.0",
      categories: [
        { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
        { id: "non_perishable", name: "Non-perishable", active: true, notification: "none", opened_date_tracking: false, chat: "none" },
      ],
      date_types: ["expiry_date"],
      units: ["ml"],
    },
  ],
};

function withClient(node: ReactNode, entry = "/") {
  return (
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <HouseholdProvider>
        <MemoryRouter initialEntries={[entry]}>
          <Routes>
            <Route path="/assets/:id" element={node} />
            <Route path="*" element={node} />
          </Routes>
        </MemoryRouter>
      </HouseholdProvider>
    </QueryClientProvider>
  );
}

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

beforeEach(() => {
  api.apiGet.mockReset();
  api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
  api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
  api.fetchHouseholdAssets.mockResolvedValue({ items: [] });
});

afterEach(() => {
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});

describe("SG-318 W1 catalog chips in plain words", () => {
  test("a food_beverages card reads Food & beverages, never the raw key", () => {
    const item = {
      id: "a1",
      name: "Milk",
      category: "food_beverages",
      tags: [],
      dateAdded: new Date().toISOString(),
      status: "raw" as const,
      metadata: {},
    };
    render(
      <MemoryRouter>
        <ProductCard item={item} householdId="hh-sg318" />
      </MemoryRouter>
    );
    expect(screen.getByTestId("product-category")).toHaveTextContent("Food & beverages");
    expect(screen.queryByText("food_beverages")).toBeNull();
  });
});

describe("SG-318 W2 asset Details in plain words", () => {
  test("objects never read [object Object]; dates, categories and statuses are plain", async () => {
    const assertion = (id: string, field_path: string, value: unknown, review_state = "accepted") => ({
      id,
      field_path,
      value,
      source_type: "user",
      review_state,
      confidence: null,
      source_evidence_ids: [],
      created_at: "2026-10-01T00:00:00+00:00",
    });
    const asset = {
      id: "asset-318-w2",
      household_id: household.id,
      display_name: "Oat milk",
      asset_type: "product",
      status: "ACTIVE",
      quantity: 500,
      unit: "ml",
      condition: null,
      version: 1,
      created_at: "2026-09-14T00:00:00+00:00",
      updated_at: null,
      evidence: [],
      audit_events: [],
      assertions: [
        assertion("a-type", "asset_type", "food_beverages"),
        assertion("a-status", "status", "ACTIVE"),
        assertion("a-unit", "unit", "ml"),
        assertion("a-class", "plugin:expiry-tracker/classification", {
          category: "food_beverages",
          label: "food_beverages",
          profile: { tier_defaults: { critical: 1 } },
        }),
        assertion("a-exp", "plugin:expiry-tracker/expiry_date", { expiry_date: "2026-11-07" }),
      ],
    };
    api.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/taxonomy") ? Promise.resolve(taxonomy) : Promise.resolve(asset)
    );
    render(withClient(<AssetDetailPage />, `/assets/asset-318-w2?household_id=${household.id}`));
    // Category through the label map (select option plus Details rows)
    const foodLabels = await screen.findAllByText("Food & beverages");
    expect(foodLabels.length).toBeGreaterThanOrEqual(1);
    expect(screen.queryByText("food_beverages")).toBeNull();
    // Date as the owner reads it
    expect(screen.getByText("7 Nov 2026")).toBeInTheDocument();
    // Status through the label map
    expect(screen.getByText("Live")).toBeInTheDocument();
    expect(screen.queryByText("ACTIVE")).toBeNull();
    // Rows named for what they are
    expect(screen.getByText("Kind of item")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Unit")).toBeInTheDocument();
    // No object dump anywhere
    expect(screen.queryByText("[object Object]")).toBeNull();
    expect(document.body.textContent ?? "").not.toContain("[object Object]");
  });
});

describe("SG-318 W3 asset History in plain words", () => {
  test("ISO stamps read Today/time; actions read Added and Accepted", async () => {
    const now = new Date();
    const isoToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 19, 6, 54).toISOString();
    const asset = {
      id: "asset-318-w3",
      household_id: household.id,
      display_name: "Milk",
      asset_type: "product",
      status: "ACTIVE",
      quantity: 1,
      unit: "pcs",
      condition: null,
      version: 1,
      created_at: "2026-09-14T00:00:00+00:00",
      updated_at: null,
      evidence: [],
      audit_events: [
        { id: "h1", action: "asset.create", actor: "api", timestamp: isoToday, before: {}, after: {} },
        { id: "h2", action: "asset.accepted", actor: "api", timestamp: isoToday, before: {}, after: {} },
      ],
      assertions: [],
    };
    api.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/taxonomy") ? Promise.resolve(taxonomy) : Promise.resolve(asset)
    );
    render(withClient(<AssetDetailPage />, `/assets/asset-318-w3?household_id=${household.id}`));
    const history = await screen.findByText("Added", { exact: false });
    expect(history).toBeInTheDocument();
    expect(screen.getByText("Accepted", { exact: false })).toBeInTheDocument();
    expect(screen.queryByText("Asset Create")).toBeNull();
    expect(screen.queryByText("Asset Accepted")).toBeNull();
    expect(screen.queryByText(isoToday)).toBeNull();
    // The Inbox date shape (Today, 19:06) is shared via formatJobDate
    expect(document.body.textContent ?? "").toMatch(/Today, 19:06/);
  });
});

describe("SG-318 W4 asset photo fallback in plain words", () => {
  test("a failed thumb reads No photo yet at 13px, never Thumbnail unavailable", () => {
    render(<EvidenceGallery evidence={[{ id: "ev-bad", storage_key: "k", original_filename: "b.png" }]} householdId="h" />);
    const img = screen.getByAltText("Evidence thumbnail for b.png");
    fireEvent.error(img);
    const fallback = screen.getByText("No photo yet");
    expect(fallback).toBeInTheDocument();
    expect(fallback.style.fontSize).toBe("13px");
    expect(screen.queryByText("Thumbnail unavailable")).toBeNull();
  });
});

describe("SG-318 W5 item panel photo fallback", () => {
  test("a broken source photo falls back to No photo yet, no broken img left", async () => {
    const asset = {
      id: "asset-318-w5",
      household_id: "h1",
      display_name: "Milk",
      asset_type: "product",
      status: "ACTIVE",
      quantity: 1,
      unit: "pcs",
      condition: null,
      version: 1,
      created_at: "2026-09-10T00:00:00Z",
      updated_at: null,
      evidence: [{ id: "ev-1", sha256: "abc", storage_key: "key", media_type: "image/jpeg", original_filename: "milk.jpg", size_bytes: 10 }],
      assertions: [],
    } as never;
    api.apiGet.mockResolvedValue(asset);
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <ItemInspectorDrawer asset={asset} householdId="h1" onClose={vi.fn()} />
      </QueryClientProvider>
    );
    const img = await screen.findByTestId("source-image");
    fireEvent.error(img);
    expect(await screen.findByText("No photo yet.")).toBeInTheDocument();
    expect(screen.queryByTestId("source-image")).toBeNull();
  });
});

describe("SG-318 W6 one nameless word everywhere", () => {
  test("null, noname and Untitled asset all read Unnamed item", () => {
    expect(UNTITLED_ASSET_NAME).toBe("Unnamed item");
    expect(UNNAMED_ITEM).toBe("Unnamed item");
    const nullName = assetToProductItem({
      id: "a",
      display_name: null,
      asset_type: "product",
    } as never);
    expect(nullName.name).toBe("Unnamed item");
    const stemName = assetToProductItem({
      id: "b",
      display_name: "noname",
      asset_type: "product",
    } as never);
    expect(stemName.name).toBe("Unnamed item");
    expect(stemName.name).not.toBe("noname");
    expect(labelAssetType("food_beverages")).toBe("Food & beverages");
  });
});

describe("SG-318 W7 expiry dates in plain words", () => {
  test("7 Nov 2026 reads, never the ISO stamp", () => {
    expect(formatPlainDate("2026-11-07")).toBe("7 Nov 2026");
    expect(formatPlainDate("2026-11-07T00:00:00+00:00")).toBe("7 Nov 2026");
    expect(formatJobDate).toBeDefined();
  });
});

describe("SG-318 W8 tier pills only for the two action tiers", () => {
  test("Safe rows and Long lead rows show no pill; Use first and Use soon do", async () => {
    const status = {
      household_id: household.id,
      as_of: "2026-11-12",
      category: null,
      rows: [
        { asset_id: "a1", display_name: "Milk", category: "food_beverages", expiry_date: "2026-11-07", date_type: "expiry_date", days_remaining: -5, tier: "critical", bucket: "expired" },
        { asset_id: "a2", display_name: "Yogurt", category: "food_beverages", expiry_date: "2026-11-15", date_type: "expiry_date", days_remaining: 3, tier: "urgent", bucket: "this-week" },
        { asset_id: "a3", display_name: "Passport", category: "documents_other", expiry_date: "2026-12-27", date_type: "valid_until", days_remaining: 45, tier: "long_lead", bucket: "safe" },
        { asset_id: "a4", display_name: "Warranty", category: "documents_other", expiry_date: "2027-06-01", date_type: "expiry_date", days_remaining: 250, tier: "safe", bucket: "safe" },
      ],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 4 },
      unresolved_rows: [],
    };
    const summary = {
      household_id: household.id,
      as_of_date: "2026-11-12",
      generated_at: "2026-11-12T00:00:00+00:00",
      assets: { total: 4, active: 4, by_status: {} },
      categories: { taxonomy: [], counts: {}, uncategorized: 0 },
      expiry: {},
      waste: { expired_untouched: 0 },
      adherence: { suggestions: {}, review_tasks: {} },
      stats: [],
    };
    api.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/taxonomy") ? Promise.resolve(taxonomy) : Promise.resolve({ items: [], next_cursor: null, total: 0 })
    );
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/v1/reminders")) return Promise.resolve(jsonResponse({ household_id: household.id, unread_count: 0, items: [] }));
        if (url.includes("/v1/plugins/expiry-tracker/opened")) return Promise.resolve(jsonResponse({ household_id: household.id, as_of: "2026-11-12", rows: [] }));
        if (url.includes("/v1/plugins/expiry-tracker/status")) return Promise.resolve(jsonResponse(status));
        if (url.includes("/v1/analytics/summary")) return Promise.resolve(jsonResponse(summary));
        return Promise.resolve(jsonResponse({}));
      })
    );
    render(withClient(<ExpiryPage />));
    expect(await screen.findByText("Use first")).toBeInTheDocument();
    expect(screen.getByText("Use soon")).toBeInTheDocument();
    expect(screen.queryByText("Long lead")).toBeNull();
    expect(screen.queryByText("Safe", { selector: '[data-testid="tier-pill"]' })).toBeNull();
    expect(screen.getAllByTestId("tier-pill")).toHaveLength(2);
  });
});

describe("SG-318 W9 PENDING waits in plain words", () => {
  test("PENDING reads Not started, never In progress", () => {
    expect(labelStepState("PENDING")).toBe("Not started");
    expect(labelStepState("PENDING")).not.toBe("In progress");
    expect(labelStepState("RUNNING")).toBe("In progress");
  });
});

describe("SG-318 W10 step names in plain words", () => {
  test("the three missing steps never leak underscores or ai", () => {
    expect(labelStepName("VALIDATING_INPUT")).toBe("Checking your upload");
    expect(labelStepName("ANALYZING_WITH_AI")).toBe("Reading the photo");
    expect(labelStepName("BUILDING_CANDIDATES")).toBe("Making items");
    for (const raw of ["VALIDATING_INPUT", "ANALYZING_WITH_AI", "BUILDING_CANDIDATES"]) {
      expect(labelStepName(raw)).not.toMatch(/_/);
      expect(labelStepName(raw)).not.toMatch(/Analyzing with ai/);
    }
  });
});
