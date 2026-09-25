import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetDetailPage, EnrichButton, enrichCapRefusal, ENRICH_PER_PRESS_CAP_USD } from "./AssetDetailPage";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
  enterManualExpiry: vi.fn(),
  fetchLocations: vi.fn(),
  assignAssetLocation: vi.fn(),
  unassignAssetLocation: vi.fn(),
  fetchRelations: vi.fn(),
  createRelation: vi.fn(),
  deleteRelation: vi.fn(),
  fetchHouseholdAssets: vi.fn(),
}));
vi.mock("../api/client", () => api);

const evidence = [
  { id: "ev-1", sha256: "sha", storage_key: "key", original_filename: "photo.jpg" },
];

function assertion(id: string, field_path: string, value: unknown, review_state: string) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: null };
}

const before = {
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
  evidence,
  assertions: [assertion("a-name", "display_name", "Milk", "accepted"), assertion("a-qty-old", "quantity", 2, "accepted")],
  audit_events: [],
};

const after = {
  ...before,
  version: 2,
  quantity: 3,
  assertions: [
    assertion("a-name", "display_name", "Milk", "accepted"),
    assertion("a-qty-old", "quantity", 2, "superseded"),
    assertion("a-qty-new", "quantity", 3, "accepted"),
  ],
  audit_events: [{ id: "ae-1", action: "asset.update", actor: "api", timestamp: "2026-09-14T00:00:01+00:00", before: {}, after: { quantity: 3 } }],
};

const needsEvidence = {
  ...before,
  assertions: [
    assertion("a-name", "display_name", "Milk", "accepted"),
    assertion("a-exp", "plugin:expiry-tracker/expiry_date", { status: "unknown" }, "needs_evidence"),
  ],
};

function renderPage() {
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

afterEach(() => {
  vi.clearAllMocks();
});

beforeEach(() => {
  // Default: the location tree route is dormant (backend flag OFF -> 404), so
  // the section hides unless a test opts in with a resolved value.
  api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
  // Default: the relation surface is dormant too (flag OFF -> 404).
  api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
});

describe("AssetDetailPage", () => {
  test("editing quantity patches via PATCH and shows the superseded prior value in history", async () => {
    api.apiGet.mockResolvedValueOnce(before).mockResolvedValueOnce(after);
    api.apiPatch.mockResolvedValue(after);
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Edit" }));
    fireEvent.change(await screen.findByLabelText("Quantity"), { target: { value: "3" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() =>
      expect(api.apiPatch).toHaveBeenCalledWith(
        "/v1/assets/asset-1",
        expect.objectContaining({ display_name: "Milk", quantity: 3 }),
        { household_id: "hh" },
        { "If-Match": "1" }
      )
    );
    expect(await screen.findByText("superseded")).toBeInTheDocument();
    expect(await screen.findByText("asset.update")).toBeInTheDocument();
  });

  test("a needs_evidence asset offers hand entry beside its detail and refuses an empty date", async () => {
    api.apiGet.mockResolvedValue(needsEvidence);
    api.enterManualExpiry.mockResolvedValue({ assertion: null, resolved_review_task_ids: [] });
    renderPage();

    expect(await screen.findByText("Manual expiry entry")).toBeInTheDocument();
    const save = screen.getByRole("button", { name: "Save expiry" });
    expect(save).toBeDisabled();

    fireEvent.change(screen.getByLabelText("Date"), { target: { value: "2030-05-06" } });
    await waitFor(() => expect(save).not.toBeDisabled());
    fireEvent.click(save);

    await waitFor(() =>
      expect(api.enterManualExpiry).toHaveBeenCalledWith(
        "asset-1",
        "hh",
        expect.objectContaining({ expiry_date: "2030-05-06", source_evidence_ids: ["ev-1"] })
      )
    );
  });
});

describe("EnrichButton per-press cap (SG-082)", () => {
  test("the page renders the Enrich button with the last measured spend and cap", async () => {
    api.apiGet.mockResolvedValue(before);
    renderPage();

    expect(await screen.findByRole("button", { name: "Enrich" })).toBeInTheDocument();
    expect(screen.getByText(`Last measured spend: $0.00 · per-press cap $${ENRICH_PER_PRESS_CAP_USD.toFixed(2)}`)).toBeInTheDocument();
  });

  test("cap helper refuses above the cap with a named reason (seen-to-fail) and allows below", () => {
    expect(enrichCapRefusal(0.01)).toBeNull();
    expect(enrichCapRefusal(0.06)).toBe(
      "per_press_cap_exceeded: last press cost $0.060000 exceeds cap $0.05"
    );
  });

  test("a press above the cap is refused and never runs; below the cap it runs", () => {
    const run = vi.fn();
    const { rerender } = render(<EnrichButton lastSpendUsd={0.06} onRun={run} />);

    expect(screen.getByText("Last measured spend: $0.060000 · per-press cap $0.05")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Enrich" }));
    expect(run).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "per_press_cap_exceeded: last press cost $0.060000 exceeds cap $0.05"
    );

    rerender(<EnrichButton lastSpendUsd={0.01} onRun={run} />);
    fireEvent.click(screen.getByRole("button", { name: "Enrich" }));
    expect(run).toHaveBeenCalledTimes(1);
  });

  test("the page's wired Enrich handler POSTs the enrich endpoint under the cap (SG-098)", async () => {
    api.apiGet.mockResolvedValue(before);
    api.apiPost.mockResolvedValue({ candidate_id: "cand-1", state: "proposed" });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Enrich" }));

    await waitFor(() =>
      expect(api.apiPost).toHaveBeenCalledWith("/v1/enrich/asset-1", {}, { household_id: "hh" })
    );
  });

  test("an enrich press renders the returned brand alternate with its source (SG-119 G2)", async () => {
    api.apiGet.mockResolvedValue(before);
    api.apiPost.mockResolvedValue({
      candidate_id: "cand-1",
      state: "proposed",
      web_alternates: [
        {
          field: "brand",
          value: "Jacobs Cronat Gold",
          source_type: "web:OpenFoodFacts",
          source_url: "https://world.openfoodfacts.org/api/v2/search?search_terms=Jacobs",
          retrieved_at: "2026-09-25T00:00:00+00:00",
        },
      ],
    });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Enrich" }));

    const section = await screen.findByRole("region", { name: "Web alternates" });
    expect(within(section).getByText("brand")).toBeInTheDocument();
    expect(within(section).getByText("Jacobs Cronat Gold")).toBeInTheDocument();
    expect(within(section).getByText("web:OpenFoodFacts")).toBeInTheDocument();
  });
});

describe("LocationsSection (SG-113)", () => {
  const fridge = { id: "loc-1", household_id: "hh", name: "Fridge", parent_id: null, created_at: null, updated_at: null };
  const freezer = { id: "loc-2", household_id: "hh", name: "Freezer", parent_id: null, created_at: null, updated_at: null };

  test("hides the whole section when the backend reports the tree disabled", async () => {
    api.apiGet.mockResolvedValue(before);
    renderPage();

    await screen.findByRole("heading", { name: "Milk" });
    await waitFor(() => expect(screen.queryByText("Locations")).not.toBeInTheDocument());
  });

  test("shows the empty state for an asset with no assignments (never an error)", async () => {
    api.apiGet.mockResolvedValue(before);
    api.fetchLocations.mockResolvedValueOnce({ items: [fridge] });
    renderPage();

    expect(await screen.findByText("Locations")).toBeInTheDocument();
    expect(await screen.findByText("No locations assigned")).toBeInTheDocument();
  });

  test("lists assigned locations, assigns from the select and unassigns", async () => {
    api.apiGet.mockResolvedValue({ ...before, locations: [fridge] });
    api.fetchLocations.mockResolvedValueOnce({ items: [fridge, freezer] });
    api.assignAssetLocation.mockResolvedValue({ status: "assigned", asset_id: "asset-1", location_id: "loc-2" });
    api.unassignAssetLocation.mockResolvedValue({ status: "unassigned", asset_id: "asset-1", location_id: "loc-1" });
    renderPage();

    expect(await screen.findByText("Fridge")).toBeInTheDocument();
    // The already-assigned location is not offered again in the select.
    const select = screen.getByLabelText("Assign location");
    expect(screen.queryByRole("option", { name: "Fridge" })).not.toBeInTheDocument();

    fireEvent.change(select, { target: { value: "loc-2" } });
    await waitFor(() =>
      expect(api.assignAssetLocation).toHaveBeenCalledWith("asset-1", "loc-2", "hh")
    );

    fireEvent.click(screen.getByRole("button", { name: "Remove" }));
    await waitFor(() =>
      expect(api.unassignAssetLocation).toHaveBeenCalledWith("asset-1", "loc-1", "hh")
    );
  });
});

describe("RelationsSection (SG-114)", () => {
  const screwdriver = {
    id: "asset-2",
    household_id: "hh",
    display_name: "Screwdriver",
    asset_type: "product",
    status: "ACTIVE",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    updated_at: null,
  };
  const relation = {
    id: "rel-1",
    household_id: "hh",
    from_asset_id: "asset-1",
    to_asset_id: "asset-2",
    relation_type: "contains",
    direction: "outgoing" as const,
    created_at: null,
    updated_at: null,
  };

  test("hides the whole section when the backend reports relations disabled", async () => {
    api.apiGet.mockResolvedValue(before);
    renderPage();

    await screen.findByRole("heading", { name: "Milk" });
    await waitFor(() => expect(screen.queryByText("Related assets")).not.toBeInTheDocument());
  });

  test("shows the empty state for an unlinked asset (never an error)", async () => {
    api.apiGet.mockResolvedValue(before);
    api.fetchRelations.mockResolvedValueOnce({ items: [] });
    api.fetchHouseholdAssets.mockResolvedValueOnce({ items: [before, screwdriver], next_cursor: null });
    renderPage();

    expect(await screen.findByText("Related assets")).toBeInTheDocument();
    expect(await screen.findByText("No related assets")).toBeInTheDocument();
  });

  test("lists both directions, creates a link and deletes one", async () => {
    api.apiGet.mockResolvedValue({ ...before, relations: [relation] });
    api.fetchRelations.mockResolvedValue({ items: [relation] });
    api.fetchHouseholdAssets.mockResolvedValue({ items: [before, screwdriver], next_cursor: null });
    api.createRelation.mockResolvedValue(relation);
    api.deleteRelation.mockResolvedValue({ status: "deleted", id: "rel-1" });
    renderPage();

    // The linked asset is named and its direction is labelled from this asset.
    expect(await screen.findByText("(contains, outgoing)")).toBeInTheDocument();
    expect(await screen.findByRole("option", { name: "Screwdriver" })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Related asset"), { target: { value: "asset-2" } });
    fireEvent.change(screen.getByLabelText("Relation type"), { target: { value: "contains" } });
    fireEvent.click(screen.getByRole("button", { name: "Link" }));
    await waitFor(() =>
      expect(api.createRelation).toHaveBeenCalledWith("asset-1", "asset-2", "contains", "hh")
    );

    fireEvent.click(screen.getByRole("button", { name: "Remove" }));
    await waitFor(() =>
      expect(api.deleteRelation).toHaveBeenCalledWith("asset-1", "rel-1", "hh")
    );
  });
});
