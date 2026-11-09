import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetDetailPage, isCountedUnit } from "./AssetDetailPage";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
  enterManualExpiry: vi.fn(),
  clearExpiryDate: vi.fn(),
  classifyAsset: vi.fn(),
  markGone: vi.fn(),
  putBack: vi.fn(),
  decrementQuantity: vi.fn(),
  incrementQuantity: vi.fn(),
  fetchLocations: vi.fn(),
  assignAssetLocation: vi.fn(),
  unassignAssetLocation: vi.fn(),
  fetchRelations: vi.fn(),
  createRelation: vi.fn(),
  deleteRelation: vi.fn(),
  fetchHouseholdAssets: vi.fn(),
}));
vi.mock("../api/client", () => api);

function assertion(id: string, field_path: string, value: unknown, review_state: string) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: "2026-10-01T00:00:00+00:00" };
}

const taxonomy = {
  plugins: [
    {
      plugin_id: "expiry-tracker",
      version: "1.0.0",
      categories: [
        { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
        { id: "non_perishable", name: "Non-perishable", active: true, notification: "none", opened_date_tracking: false, chat: "none" },
      ],
      date_types: ["expiry_date", "valid_until"],
      units: ["piece"],
    },
  ],
};

function shell(overrides: Record<string, unknown> = {}) {
  return {
    id: "asset-272",
    household_id: "hh",
    display_name: "Milk",
    asset_type: "product",
    status: "ACTIVE",
    gone_reason: null,
    quantity: 3,
    unit: "pcs",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    updated_at: null,
    evidence: [],
    audit_events: [],
    assertions: [],
    ...overrides,
  };
}

let assetBody: Record<string, unknown>;

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/assets/asset-272?household_id=hh"]}>
        <Routes>
          <Route path="/assets/:id" element={<AssetDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

beforeEach(() => {
  api.apiGet.mockImplementation((path: string) => {
    if (path.includes("/v1/taxonomy")) return Promise.resolve(taxonomy);
    return Promise.resolve(assetBody);
  });
  api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
  api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
});

describe("AssetDetailPage SG-272 counted rule", () => {
  test("empty, pcs and bottles count; ml, g, kg and l are amounts", () => {
    expect(isCountedUnit(null)).toBe(true);
    expect(isCountedUnit("")).toBe(true);
    expect(isCountedUnit("pcs")).toBe(true);
    expect(isCountedUnit("bottles")).toBe(true);
    expect(isCountedUnit("piece")).toBe(true);
    expect(isCountedUnit("ml")).toBe(false);
    expect(isCountedUnit("g")).toBe(false);
    expect(isCountedUnit("kg")).toBe(false);
    expect(isCountedUnit("l")).toBe(false);
  });
});

describe("AssetDetailPage SG-272 quantities", () => {
  test("a counted item offers one-tap −1 and a way back up", async () => {
    assetBody = shell({ quantity: 3, unit: "pcs" });
    api.decrementQuantity.mockResolvedValue(shell({ quantity: 2, unit: "pcs" }));
    api.incrementQuantity.mockResolvedValue(shell({ quantity: 4, unit: "pcs" }));
    renderPage();
    const minus = await screen.findByRole("button", { name: "Take off 1" });
    expect(screen.getByRole("button", { name: "Put 1 back on the count" })).toBeInTheDocument();
    expect(screen.getByText("3 pcs left")).toBeInTheDocument();
    fireEvent.click(minus);
    await waitFor(() => expect(api.decrementQuantity).toHaveBeenCalledWith("asset-272", "hh"));
  });

  test("an amount item takes a quick edit instead of −1", async () => {
    assetBody = shell({ quantity: 500, unit: "ml" });
    renderPage();
    expect(await screen.findByText(/change the amount with Edit above/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Take off 1" })).toBeNull();
  });

  test("at 0 a counted item reads None left with −1 refused", async () => {
    assetBody = shell({ quantity: 0, unit: "" });
    renderPage();
    expect(await screen.findByText("None left — mark it gone below.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Take off 1" })).toBeDisabled();
  });
});

describe("AssetDetailPage SG-272 gone and put back", () => {
  test("a live item offers the three reasons; Used up marks it gone", async () => {
    assetBody = shell({});
    api.markGone.mockResolvedValue(shell({ status: "ARCHIVED", gone_reason: "used_up" }));
    renderPage();
    const usedUp = await screen.findByRole("button", { name: "Used up" });
    expect(screen.getByRole("button", { name: "Thrown away" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Given away" })).toBeInTheDocument();
    fireEvent.click(usedUp);
    await waitFor(() => expect(api.markGone).toHaveBeenCalledWith("asset-272", "hh", "used_up"));
  });

  test("a gone item reads Gone with Put back and never a raw state name", async () => {
    assetBody = shell({ status: "ARCHIVED", gone_reason: "used_up" });
    api.putBack.mockResolvedValue(shell({ status: "ACTIVE", gone_reason: null }));
    renderPage();
    expect(await screen.findByText("Gone — used up")).toBeInTheDocument();
    expect(screen.queryByText("ARCHIVED", { exact: true })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Put back" }));
    await waitFor(() => expect(api.putBack).toHaveBeenCalledWith("asset-272", "hh"));
  });
});

describe("AssetDetailPage SG-272 G0b I2", () => {
  test("the AI suggestion notes render at body size, not 12 px", async () => {
    assetBody = shell({
      assertions: [assertion("a-cat", "category_proposed", "food_beverages", "proposed")],
    });
    renderPage();
    const note = await screen.findByText(/The AI suggests Food & beverages/);
    expect(note).toHaveStyle({ fontSize: "13px" });
  });
});
