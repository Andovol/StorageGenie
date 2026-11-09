import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetDetailPage } from "./AssetDetailPage";

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
vi.mock("../api/client", () => api);

function assertion(id: string, field_path: string, value: unknown, review_state: string) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: "2026-10-01T00:00:00+00:00" };
}

function classificationAssertion(id: string, category: string) {
  return assertion(id, "plugin:expiry-tracker/classification", {
    category,
    label: category,
    profile: { notification_tier: "upcoming", notification_days: 30, tier_defaults: { critical: 1, urgent: 7, upcoming: 30 }, opened_date_tracking: false, disposal_guidance: false },
  }, "accepted");
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

const shell = {
  id: "asset-271",
  household_id: "hh",
  display_name: "Milk",
  asset_type: "product",
  status: "ACTIVE",
  quantity: null,
  unit: null,
  condition: null,
  version: 1,
  created_at: "2026-09-14T00:00:00+00:00",
  updated_at: null,
  evidence: [],
  audit_events: [],
};

let assetBody: Record<string, unknown>;

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/assets/asset-271?household_id=hh"]}>
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

describe("AssetDetailPage SG-271", () => {
  test("a proposed date offers Accept date with the AI value prefilled", async () => {
    assetBody = {
      ...shell,
      assertions: [
        classificationAssertion("a-class", "food_beverages"),
        assertion("a-exp", "plugin:expiry-tracker/expiry_date", { expiry_date: "2030-01-15", date_type: "expiry_date" }, "proposed"),
      ],
    };
    api.enterManualExpiry.mockResolvedValue({ assertion: null, resolved_review_task_ids: [] });
    renderPage();
    const accept = await screen.findByRole("button", { name: "Accept date" });
    expect(accept).toBeInTheDocument();
    expect(screen.getByDisplayValue("2030-01-15")).toBeInTheDocument();
  });

  test("the AI shelf life preselects the control with a confirm note", async () => {
    assetBody = {
      ...shell,
      assertions: [assertion("a-cat", "category_proposed", "food_beverages", "proposed")],
    };
    renderPage();
    const select = (await screen.findByLabelText("Shelf life")) as HTMLSelectElement;
    expect(select.value).toBe("food_beverages");
    expect(await screen.findByText(/The AI suggests Food & beverages/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save shelf life" })).toBeInTheDocument();
  });

  test("an unmapped suggestion names itself instead of guessing", async () => {
    assetBody = {
      ...shell,
      assertions: [assertion("a-cat", "category_proposed", "dairy", "proposed")],
    };
    renderPage();
    expect(await screen.findByText(/matches no shelf life/)).toBeInTheDocument();
    const select = (await screen.findByLabelText("Shelf life")) as HTMLSelectElement;
    expect(select.value).toBe("");
  });
});
