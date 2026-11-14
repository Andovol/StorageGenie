import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ExpiryEntryForm } from "./components/ExpiryEntryForm";
import { AssetDetailPage } from "./routes/AssetDetailPage";
import { THEMED_CONTROL_CLASS } from "./components/shell/CatalogToolbar";

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
vi.mock("./api/client", () => api);

function themedToken(): string {
  return THEMED_CONTROL_CLASS.split(" ")[0];
}

describe("SG-324 P1 themed controls", () => {
  beforeEach(() => {
    api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
    api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  test("Clear expiry date uses the theme control class, not white card", () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <ExpiryEntryForm
          assetId="asset-p1"
          householdId="hh"
          evidenceIds={["ev-1"]}
          activeAssertion={{
            id: "a-exp",
            field_path: "plugin:expiry-tracker/expiry_date",
            value: { expiry_date: "2030-05-06", date_type: "expiry_date" },
            source_type: "user",
            review_state: "accepted",
            confidence: null,
            source_evidence_ids: [],
            created_at: "2026-10-01T00:00:00+00:00",
          }}
          categorySlug="food_beverages"
          hasWindows
        />
      </QueryClientProvider>
    );
    const btn = screen.getByRole("button", { name: "Clear expiry date" });
    expect(btn).toHaveClass(themedToken());
  });

  test("asset Edit uses the theme control class, not white card", async () => {
    const assetBody = {
      id: "asset-1",
      household_id: "hh",
      display_name: "Milk",
      asset_type: "product",
      status: "ACTIVE",
      quantity: 2,
      unit: "piece",
      condition: null,
      version: 1,
      created_at: "2026-09-14T00:00:00+00:00",
      updated_at: null,
      evidence: [],
      assertions: [
        { id: "a-name", field_path: "display_name", value: "Milk", source_type: "user", review_state: "accepted", confidence: null, source_evidence_ids: [], created_at: null },
      ],
      audit_events: [],
    };
    const taxonomyBody = {
      plugins: [
        {
          plugin_id: "expiry-tracker",
          version: "1.0.0",
          categories: [
            { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
          ],
          date_types: ["expiry_date"],
          units: ["piece"],
        },
      ],
    };
    api.apiGet.mockImplementation((path: string) => {
      if (String(path).includes("/v1/taxonomy")) return Promise.resolve(taxonomyBody);
      return Promise.resolve(assetBody);
    });
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter initialEntries={["/assets/asset-1?household_id=hh"]}>
          <Routes>
            <Route path="/assets/:id" element={<AssetDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
    const btn = await screen.findByRole("button", { name: "Edit" });
    expect(btn).toHaveClass(themedToken());
  });
});
