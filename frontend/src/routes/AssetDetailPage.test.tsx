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

const evidence = [
  { id: "ev-1", sha256: "sha", storage_key: "key", original_filename: "photo.jpg" },
];

function assertion(
  id: string,
  field_path: string,
  value: unknown,
  review_state: string,
  created_at: string | null = null
) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at };
}

function classificationAssertion(
  id: string,
  category: string,
  tierDefaults: Record<string, number>,
  created_at = "2026-10-01T00:00:00+00:00"
) {
  return assertion(
    id,
    "plugin:expiry-tracker/classification",
    {
      category,
      label: category,
      profile: {
        notification_tier: Object.keys(tierDefaults)[0] ?? null,
        notification_days: Object.values(tierDefaults)[0] ?? null,
        tier_defaults: tierDefaults,
        opened_date_tracking: false,
        disposal_guidance: false,
      },
    },
    "accepted",
    created_at
  );
}

const taxonomy = {
  plugins: [
    {
      plugin_id: "expiry-tracker",
      version: "1.0.0",
      categories: [
        { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
        { id: "household_chemicals", name: "Household chemicals", active: true, notification: "basic-expiry", opened_date_tracking: false, chat: "fallback" },
        { id: "documents_other", name: "Documents/other", active: true, notification: "long-lead-60-30", opened_date_tracking: false, chat: "fallback" },
        { id: "non_perishable", name: "Non-perishable", active: true, notification: "none", opened_date_tracking: false, chat: "none" },
        { id: "retired_category", name: "Retired category", active: false, notification: "none", opened_date_tracking: false, chat: "none" },
      ],
      date_types: ["expiry_date", "valid_until"],
      units: ["piece"],
    },
  ],
};

let assetBody: Record<string, unknown>;
let taxonomyBody: typeof taxonomy;

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
    classificationAssertion("a-class", "food_beverages", { critical: 1, urgent: 7, upcoming: 30 }),
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
  assetBody = before;
  taxonomyBody = taxonomy;
  // The asset and taxonomy reads share one client; route them by path.
  api.apiGet.mockImplementation((path: string) => {
    if (path.includes("/v1/taxonomy")) return Promise.resolve(taxonomyBody);
    return Promise.resolve(assetBody);
  });
  // Default: the location tree route is dormant (backend flag OFF -> 404), so
  // the section hides unless a test opts in with a resolved value.
  api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
  // Default: the relation surface is dormant too (flag OFF -> 404).
  api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
});

describe("AssetDetailPage", () => {
  test("editing quantity patches via PATCH and shows the superseded prior value in history", async () => {
    assetBody = before;
    api.apiPatch.mockImplementation(() => {
      assetBody = after;
      return Promise.resolve(after);
    });
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
    assetBody = needsEvidence;
    api.enterManualExpiry.mockResolvedValue({ assertion: null, resolved_review_task_ids: [] });
    renderPage();

    expect(await screen.findByText("Manual expiry entry")).toBeInTheDocument();
    const save = screen.getByRole("button", { name: "Save date" });
    expect(save).toBeDisabled();

    fireEvent.change(screen.getByLabelText("Date"), { target: { value: "2030-05-06" } });
    await waitFor(() => expect(save).not.toBeDisabled());
    fireEvent.click(save);

    await waitFor(() =>
      expect(api.enterManualExpiry).toHaveBeenCalledWith(
        "asset-1",
        "hh",
        expect.objectContaining({ expiry_date: "2030-05-06", source_evidence_ids: ["ev-1"] }),
        "a-exp"
      )
    );
  });
});

describe("EnrichButton per-press cap (SG-082)", () => {
  test("the page renders the Enrich button with the last measured spend and cap", async () => {
    assetBody = before;
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
    assetBody = before;
    api.apiPost.mockResolvedValue({ candidate_id: "cand-1", state: "proposed" });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Enrich" }));

    await waitFor(() =>
      expect(api.apiPost).toHaveBeenCalledWith("/v1/enrich/asset-1", {}, { household_id: "hh" })
    );
  });

  test("an enrich press renders the returned brand alternate with its source (SG-119 G2)", async () => {
    assetBody = before;
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
    assetBody = before;
    renderPage();

    await screen.findByRole("heading", { name: "Milk" });
    await waitFor(() => expect(screen.queryByText("Locations")).not.toBeInTheDocument());
  });

  test("shows the empty state for an asset with no assignments (never an error)", async () => {
    assetBody = before;
    api.fetchLocations.mockResolvedValueOnce({ items: [fridge] });
    renderPage();

    expect(await screen.findByText("Locations")).toBeInTheDocument();
    expect(await screen.findByText("No locations assigned")).toBeInTheDocument();
  });

  test("lists assigned locations, assigns from the select and unassigns", async () => {
    assetBody = { ...before, locations: [fridge] };
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
    assetBody = before;
    renderPage();

    await screen.findByRole("heading", { name: "Milk" });
    await waitFor(() => expect(screen.queryByText("Related assets")).not.toBeInTheDocument());
  });

  test("shows the empty state for an unlinked asset (never an error)", async () => {
    assetBody = before;
    api.fetchRelations.mockResolvedValueOnce({ items: [] });
    api.fetchHouseholdAssets.mockResolvedValueOnce({ items: [before, screwdriver], next_cursor: null });
    renderPage();

    expect(await screen.findByText("Related assets")).toBeInTheDocument();
    expect(await screen.findByText("No related assets")).toBeInTheDocument();
  });

  test("lists both directions, creates a link and deletes one", async () => {
    assetBody = { ...before, relations: [relation] };
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

const classifiedFood = {
  ...before,
  assertions: [
    classificationAssertion("a-class", "food_beverages", { critical: 1, urgent: 7, upcoming: 30 }),
    assertion(
      "a-exp-old",
      "plugin:expiry-tracker/expiry_date",
      { expiry_date: "2020-01-01", date_type: "expiry_date" },
      "superseded",
      "2026-01-01T00:00:00+00:00"
    ),
    assertion(
      "a-exp",
      "plugin:expiry-tracker/expiry_date",
      { expiry_date: "2030-05-06", date_type: "best_before" },
      "accepted",
      "2026-01-02T00:00:00+00:00"
    ),
  ],
};

function assetReads(): number {
  return api.apiGet.mock.calls.filter(([path]) => String(path).includes("/v1/assets/asset-1")).length;
}

describe("classification control (SG-258)", () => {
  test("lists active categories, shows the current one, saves with the token and re-reads", async () => {
    assetBody = {
      ...before,
      assertions: [classificationAssertion("a-class", "food_beverages", { upcoming: 30 })],
    };
    api.classifyAsset.mockResolvedValue({});
    renderPage();

    const select = await screen.findByLabelText("Classification category");
    const options = within(select).getAllByRole("option").map((option) => option.textContent);
    expect(options).toEqual(
      expect.arrayContaining([
        "Food & beverages",
        "Household chemicals",
        "Documents/other",
        "Non-perishable",
      ])
    );
    expect(options).not.toContain("Retired category");
    expect(select).toHaveValue("food_beverages");

    const beforeReads = assetReads();
    fireEvent.change(select, { target: { value: "documents_other" } });
    assetBody = {
      ...before,
      assertions: [classificationAssertion("a-class-2", "documents_other", { upcoming: 30, long_lead: 60 })],
    };
    fireEvent.click(screen.getByRole("button", { name: "Save category" }));

    await waitFor(() =>
      expect(api.classifyAsset).toHaveBeenCalledWith("asset-1", "hh", "documents_other", "a-class")
    );
    await waitFor(() => expect(assetReads()).toBeGreaterThan(beforeReads));
    expect(await screen.findByText("Category saved.")).toBeInTheDocument();
  });

  test("a 409 shows the reload message and re-reads the asset", async () => {
    assetBody = {
      ...before,
      assertions: [classificationAssertion("a-class", "food_beverages", { upcoming: 30 })],
    };
    api.classifyAsset.mockRejectedValue(new Error("This item changed; reload the asset"));
    renderPage();

    const beforeReads = assetReads();
    fireEvent.change(await screen.findByLabelText("Classification category"), {
      target: { value: "household_chemicals" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save category" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "This item changed; reload the asset"
    );
    await waitFor(() => expect(assetReads()).toBeGreaterThan(beforeReads));
  });

  test("an empty taxonomy shows a message instead of an empty select", async () => {
    taxonomyBody = { plugins: [] };
    renderPage();

    expect(
      await screen.findByText("No categories are available from the taxonomy.")
    ).toBeInTheDocument();
    expect(screen.queryByLabelText("Classification category")).not.toBeInTheDocument();
  });

  test("a move to Non-perishable confirms before clearing the active date", async () => {
    assetBody = classifiedFood;
    api.classifyAsset.mockResolvedValue({});
    const confirm = vi.spyOn(window, "confirm").mockReturnValue(false);
    renderPage();

    const select = await screen.findByLabelText("Classification category");
    fireEvent.change(select, { target: { value: "non_perishable" } });
    fireEvent.click(screen.getByRole("button", { name: "Save category" }));

    expect(confirm).toHaveBeenCalledWith(
      "This will clear the active date; the old value stays in the audit."
    );
    expect(api.classifyAsset).not.toHaveBeenCalled();

    confirm.mockReturnValue(true);
    fireEvent.click(screen.getByRole("button", { name: "Save category" }));
    await waitFor(() =>
      expect(api.classifyAsset).toHaveBeenCalledWith("asset-1", "hh", "non_perishable", "a-class")
    );
    confirm.mockRestore();
  });
});

describe("ExpiryEntryForm integration (SG-258)", () => {
  test("pre-fills the active expiry row, never the superseded one", async () => {
    assetBody = classifiedFood;
    renderPage();

    expect(await screen.findByLabelText("Date")).toHaveValue("2030-05-06");
    expect(screen.getByLabelText("Date type")).toHaveValue("best_before");
    expect(screen.getByRole("button", { name: "Save date" })).toBeDisabled();
    expect(
      screen.getByText("The date is kept when the category changes; check it still applies.")
    ).toBeInTheDocument();
  });

  test("Clear writes the null active and empties the form", async () => {
    assetBody = classifiedFood;
    api.clearExpiryDate.mockImplementation(() => {
      assetBody = {
        ...before,
        assertions: [
          classificationAssertion("a-class", "food_beverages", { critical: 1, urgent: 7, upcoming: 30 }),
          assertion(
            "a-exp",
            "plugin:expiry-tracker/expiry_date",
            { expiry_date: "2030-05-06", date_type: "best_before" },
            "superseded",
            "2026-01-02T00:00:00+00:00"
          ),
          assertion(
            "a-exp-cleared",
            "plugin:expiry-tracker/expiry_date",
            null,
            "accepted",
            "2026-01-03T00:00:00+00:00"
          ),
        ],
      };
      return Promise.resolve({ asset_id: "asset-1", assertion: null });
    });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Clear expiry date" }));

    await waitFor(() =>
      expect(api.clearExpiryDate).toHaveBeenCalledWith("asset-1", "hh", "a-exp")
    );
    await waitFor(() => expect(screen.getByLabelText("Date")).toHaveValue(""));
    expect(screen.queryByRole("button", { name: "Clear expiry date" })).not.toBeInTheDocument();
  });

  test("a proposed row offers Accept date and sends the active token", async () => {
    api.enterManualExpiry.mockResolvedValue({});
    assetBody = {
      ...before,
      assertions: [
        classificationAssertion("a-class", "food_beverages", { critical: 1, urgent: 7, upcoming: 30 }),
        assertion(
          "a-proposed",
          "plugin:expiry-tracker/expiry_date",
          { expiry_date: "2030-05-06", date_type: "expiry_date" },
          "proposed",
          "2026-01-02T00:00:00+00:00"
        ),
      ],
    };
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Accept date" }));

    await waitFor(() =>
      expect(api.enterManualExpiry).toHaveBeenCalledWith(
        "asset-1",
        "hh",
        expect.objectContaining({ expiry_date: "2030-05-06" }),
        "a-proposed"
      )
    );
  });

  test("a documents row shows the form with Valid until", async () => {
    assetBody = {
      ...before,
      assertions: [
        classificationAssertion("a-doc", "documents_other", { upcoming: 30, long_lead: 60 }),
        assertion(
          "a-doc-exp",
          "plugin:expiry-tracker/expiry_date",
          null,
          "accepted",
          "2026-01-02T00:00:00+00:00"
        ),
      ],
    };
    renderPage();

    expect(await screen.findByRole("heading", { name: "Manual date entry" })).toBeInTheDocument();
    expect(screen.getByLabelText("Date type")).toHaveValue("valid_until");
  });

  test("a non-perishable row hides the form", async () => {
    assetBody = {
      ...before,
      assertions: [classificationAssertion("a-none", "non_perishable", {})],
    };
    renderPage();

    await screen.findByRole("heading", { name: "Milk" });
    expect(screen.queryByText("Manual expiry entry")).not.toBeInTheDocument();
    expect(screen.queryByText("Manual date entry")).not.toBeInTheDocument();
  });
});
