import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AssetDetailPage } from "./routes/AssetDetailPage";

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

function assertion(id: string, field_path: string, value: unknown, review_state: string) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: "2026-10-01T00:00:00+00:00" };
}

function classificationAssertion(id: string, category: string) {
  return assertion(id, "plugin:expiry-tracker/classification", { category, label: category, profile: { tier_defaults: { upcoming: 30 } } }, "accepted");
}

const taxonomy = {
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

function renderWithAsset(assetBody: Record<string, unknown>) {
  api.apiGet.mockImplementation((path: string) => {
    if (String(path).includes("/v1/taxonomy")) return Promise.resolve(taxonomy);
    if (path === "/v1/assets")
      return Promise.resolve({
        items: [{ id: "asset-1", display_name: "Juice", status: "ACTIVE" }],
        next_cursor: null,
      });
    return Promise.resolve(assetBody);
  });
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/assets/asset-1?household_id=hh"]}>
        <Routes>
          <Route path="/assets/:id" element={<AssetDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function openMore() {
  fireEvent.click(screen.getByRole("button", { name: "More about this item" }));
}

function baseAsset(assertions: unknown[]) {
  return {
    id: "asset-1",
    household_id: "hh",
    display_name: "Juice",
    asset_type: "product",
    status: "ACTIVE",
    quantity: 300,
    unit: "ml",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    updated_at: null,
    evidence: [],
    assertions,
    audit_events: [],
  };
}

describe("SG-324 P3 details rows", () => {
  beforeEach(() => {
    api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
    api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  test("Shelf life hides when it repeats Kind of item", async () => {
    const assetBody = baseAsset([
      assertion("a-kind", "asset_type", "food_beverages", "accepted"),
      classificationAssertion("a-shelf", "food_beverages"),
    ]);
    renderWithAsset(assetBody);
    await screen.findByRole("heading", { name: "Juice" });
    // SG-338: Details now lives behind More about this item — same table.
    openMore();
    const table = await screen.findByRole("table");
    expect(within(table).queryByText("Shelf life")).toBeNull();
    expect(within(table).getByText("Kind of item")).toBeInTheDocument();
  });

  test("a superseded Replaced row is hidden from Details", async () => {
    const assetBody = baseAsset([
      assertion("a-name", "display_name", "Juice", "accepted"),
      assertion("a-old", "quantity", 2, "superseded"),
      assertion("a-new", "quantity", 3, "accepted"),
    ]);
    renderWithAsset(assetBody);
    await screen.findByRole("heading", { name: "Juice" });
    // SG-338: Details now lives behind More about this item — same rows.
    openMore();
    await screen.findAllByText("Amount");
    expect(screen.queryByText("Replaced")).toBeNull();
  });

  test("Amount and Unit read as one 300 ml row", async () => {
    const assetBody = baseAsset([
      assertion("a-qty", "quantity", 300, "accepted"),
      assertion("a-unit", "unit", "ml", "accepted"),
    ]);
    renderWithAsset(assetBody);
    await screen.findByRole("heading", { name: "Juice" });
    // SG-338: Details now lives behind More about this item — same combined row.
    openMore();
    expect(await screen.findByText("300 ml")).toBeInTheDocument();
    const table = screen.getByText("300 ml").closest("table") as HTMLElement;
    expect(within(table).queryByText("Unit")).toBeNull();
  });
});
