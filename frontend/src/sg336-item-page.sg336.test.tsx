import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetDetailPage } from "./routes/AssetDetailPage";

// SG-336 G1: the item page as in the mockup — one row per live pack with the
// same name. Shapes below are copied from AssetDetailPage.sg272.test.tsx
// (the `shell()` body + taxonomy the API client really serves), never
// hand-made (SG-322).

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
vi.mock("./api/client", () => api);

function assertion(id: string, field_path: string, value: unknown, review_state: string) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: "2026-10-01T00:00:00+00:00" };
}

function classificationAssertion(id: string, category: string) {
  return assertion(id, "plugin:expiry-tracker/classification", { category, label: category }, "accepted");
}

function expiryAssertion(id: string, date: string) {
  return assertion(id, "plugin:expiry-tracker/expiry_date", { expiry_date: date, date_type: "expiry_date" }, "accepted");
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

function packBody(overrides: Record<string, unknown> = {}) {
  return {
    id: "pack-1",
    household_id: "hh",
    display_name: "Olive Oil",
    asset_type: "product",
    status: "ACTIVE",
    gone_reason: null,
    quantity: 500,
    unit: "ml",
    condition: null,
    version: 1,
    created_at: "2026-05-01T10:00:00+00:00",
    updated_at: null,
    evidence: [],
    audit_events: [],
    assertions: [],
    ...overrides,
  };
}

// The live store the mocked reads serve; writes mutate it so refetches move.
let store: Record<string, Record<string, unknown>>;

function resetStore() {
  store = {
    "pack-1": packBody({
      id: "pack-1",
      display_name: "Olive Oil",
      quantity: 500,
      unit: "ml",
      created_at: "2026-05-01T10:00:00+00:00",
      assertions: [classificationAssertion("a-class-1", "food_beverages"), expiryAssertion("a-exp-1", "2030-05-06")],
      audit_events: [{ id: "ae-1", action: "asset.update", actor: "api", timestamp: "2026-05-02T10:00:00+00:00", before: {}, after: { quantity: 500 } }],
    }),
    "pack-2": packBody({
      id: "pack-2",
      quantity: 250,
      unit: "ml",
      created_at: "2026-06-01T10:00:00+00:00",
      evidence: [{ id: "ev-2", sha256: "sha", storage_key: "key-2", original_filename: "olive2.jpg" }],
      assertions: [classificationAssertion("a-class-2", "food_beverages"), expiryAssertion("a-exp-2", "2031-02-03")],
    }),
    "pack-3": packBody({
      id: "pack-3",
      display_name: "olive oil",
      quantity: 1,
      unit: "bottle",
      created_at: "2026-07-01T10:00:00+00:00",
      assertions: [],
    }),
    "rice-1": packBody({
      id: "rice-1",
      display_name: "Rice",
      quantity: 1000,
      unit: "g",
      created_at: "2026-04-01T10:00:00+00:00",
      assertions: [classificationAssertion("a-class-r", "food_beverages"), expiryAssertion("a-exp-r", "2030-01-01")],
    }),
  };
}

function renderPack1() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/assets/pack-1?household_id=hh"]}>
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
  resetStore();
  api.apiGet.mockImplementation((path: string) => {
    if (path.includes("/v1/taxonomy")) return Promise.resolve(taxonomy);
    if (path === "/v1/assets") return Promise.resolve({ items: Object.values(store), next_cursor: null });
    const id = String(path).split("/").pop() ?? "";
    const body = store[id];
    if (!body) return Promise.reject(new Error(`no asset ${id}`));
    return Promise.resolve(body);
  });
  // The location tree and the relation surface stay dormant (flag OFF), as in
  // the older suites: both sections hide, never error.
  api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
  api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
  api.markGone.mockImplementation(async (assetId: string) => {
    store[assetId] = { ...store[assetId], status: "ARCHIVED", gone_reason: "used_up" };
    return store[assetId];
  });
  api.putBack.mockImplementation(async (assetId: string) => {
    store[assetId] = { ...store[assetId], status: "ACTIVE", gone_reason: null };
    return store[assetId];
  });
  api.apiPost.mockImplementation(async (path: string, body: unknown) => {
    if (path === "/v1/assets") {
      const payload = body as Record<string, unknown>;
      const created = packBody({
        id: "pack-4",
        display_name: payload.display_name,
        asset_type: payload.asset_type,
        quantity: null,
        unit: null,
        created_at: "2026-08-01T10:00:00+00:00",
      });
      store["pack-4"] = created;
      return { id: "pack-4" };
    }
    return {};
  });
});

describe("SG-336 item page, one row per pack", () => {
  test("T1 three live Olive Oil packs in date order, Rice nowhere, muted line ends 3 packs", async () => {
    renderPack1();
    const dates = await screen.findAllByTestId("pack-date");
    expect(dates.map((d) => d.textContent)).toEqual(["Use by 6 May 2030", "Use by 3 Feb 2031", "No date"]);
    const muted = await screen.findByTestId("packs-muted");
    expect(muted.textContent ?? "").toMatch(/3 packs$/);
    expect(screen.queryByText("Rice", { exact: true })).toBeNull();
  });

  test("T2 Used up on the second row marks that pack only; Undo restores it only", async () => {
    renderPack1();
    await screen.findAllByTestId("pack-date");
    const row2 = screen.getByTestId("pack-row-pack-2");
    fireEvent.click(within(row2).getByRole("button", { name: "Used up" }));
    await waitFor(() => expect(api.markGone).toHaveBeenCalledWith("pack-2", "hh", "used_up"));
    // The row leaves; the notice reads as the Pantry wording.
    await waitFor(() => expect(screen.queryByTestId("pack-row-pack-2")).toBeNull());
    const notice = await screen.findByTestId("pack-notice");
    expect(notice.textContent).toBe("Olive Oil used up · Undo");
    // No request touches the other two packs.
    expect(api.markGone.mock.calls.filter(([id]) => id !== "pack-2")).toEqual([]);
    fireEvent.click(within(notice).getByRole("button", { name: "Undo" }));
    await waitFor(() => expect(api.putBack).toHaveBeenCalledWith("pack-2", "hh"));
    expect(api.putBack.mock.calls.filter(([id]) => id !== "pack-2")).toEqual([]);
    expect(await screen.findByTestId("pack-row-pack-2")).toBeInTheDocument();
  });

  test("T3 Add another pack creates with name, kind and place, no date, no photo; its row opens editing", async () => {
    renderPack1();
    await screen.findAllByTestId("pack-date");
    fireEvent.click(screen.getByRole("button", { name: /Add another pack/ }));
    await waitFor(() => expect(api.apiPost).toHaveBeenCalledWith(
      "/v1/assets",
      expect.objectContaining({ display_name: "Olive Oil", asset_type: "product" }),
      { household_id: "hh" },
      expect.objectContaining({ "Idempotency-Key": expect.any(String) })
    ));
    const payload = api.apiPost.mock.calls.find(([p]) => p === "/v1/assets")?.[1] as Record<string, unknown>;
    expect(payload).not.toHaveProperty("evidence_ids");
    expect(payload).not.toHaveProperty("expiry_date");
    const row4 = await screen.findByTestId("pack-row-pack-4");
    expect(within(row4).getByLabelText("Date")).toBeInTheDocument();
  });

  test("T4 Edit on a row opens that pack's date editor; saving writes that pack only", async () => {
    api.enterManualExpiry.mockResolvedValue({ asset_id: "pack-1", assertion: null });
    renderPack1();
    await screen.findAllByTestId("pack-date");
    const row1 = screen.getByTestId("pack-row-pack-1");
    fireEvent.click(within(row1).getByRole("button", { name: "Edit" }));
    const dateInput = within(row1).getByLabelText("Date") as HTMLInputElement;
    expect(dateInput.value).toBe("2030-05-06");
    fireEvent.change(dateInput, { target: { value: "2030-06-01" } });
    fireEvent.click(within(row1).getByRole("button", { name: "Save date" }));
    await waitFor(() => expect(api.enterManualExpiry).toHaveBeenCalledWith(
      "pack-1", "hh", expect.objectContaining({ expiry_date: "2030-06-01" }), "a-exp-1"
    ));
    expect(api.enterManualExpiry.mock.calls.filter(([id]) => id !== "pack-1")).toEqual([]);
  });

  test("T5 History and More about this item stay folded until opened", async () => {
    renderPack1();
    await screen.findAllByTestId("pack-date");
    // The opened pack's audit entry stays out of the document while folded.
    expect(screen.queryByText("Updated", { exact: false })).toBeNull();
    expect(screen.queryByText("Shelf life")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /History \(/ }));
    expect(await screen.findByText("Updated", { exact: false })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "More about this item" }));
    expect(await screen.findByRole("heading", { name: "Shelf life" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Amount left" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Evidence" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Details" })).toBeInTheDocument();
  });

  test("T6 no ISO date, no raw status word, no object dump anywhere on the page", async () => {
    renderPack1();
    await screen.findAllByTestId("pack-date");
    const text = document.body.textContent ?? "";
    expect(text).not.toMatch(/\d{4}-\d{2}-\d{2}/);
    expect(text).not.toContain("ACTIVE");
    expect(text).not.toContain("ARCHIVED");
    expect(text).not.toContain("[object Object]");
  });

  test("T7 the tile shows the second pack's photo when the opened item has none", async () => {
    renderPack1();
    await screen.findAllByTestId("pack-date");
    const tile = await screen.findByTestId("item-photo");
    const img = within(tile).getByRole("img");
    expect((img as HTMLImageElement).src).toContain("ev-2");
  });

  test("T8 Add another pack copies the opened item's shelf-life category onto the new pack", async () => {
    renderPack1();
    await screen.findAllByTestId("pack-date");
    fireEvent.click(screen.getByRole("button", { name: /Add another pack/ }));
    await waitFor(() => expect(api.apiPost).toHaveBeenCalledWith(
      "/v1/assets",
      expect.objectContaining({ display_name: "Olive Oil", asset_type: "product" }),
      { household_id: "hh" },
      expect.objectContaining({ "Idempotency-Key": expect.any(String) })
    ));
    // The create is followed by one classification write for the new id only,
    // and none for any other id.
    await waitFor(() => expect(api.classifyAsset).toHaveBeenCalledWith("pack-4", "hh", "food_beverages"));
    expect(api.classifyAsset.mock.calls.filter(([id]) => id !== "pack-4")).toEqual([]);
  });

  test("T9 saving a new date re-reads the packs list and the row shows the new date", async () => {
    api.enterManualExpiry.mockImplementation(async (assetId: string, _householdId: string, payload: unknown) => {
      const body = store[assetId];
      const nextDate = (payload as Record<string, unknown>)["expiry_date"] as string;
      const nextType = (payload as Record<string, unknown>)["date_type"] ?? "expiry_date";
      const assertions = (body["assertions"] as unknown[]).map((entry) => {
        const rec = entry as Record<string, unknown>;
        if (
          typeof rec["field_path"] === "string" &&
          (rec["field_path"] as string).endsWith("expiry_date") &&
          rec["review_state"] === "accepted"
        ) {
          return { ...rec, value: { expiry_date: nextDate, date_type: nextType } };
        }
        return rec;
      });
      store[assetId] = { ...body, assertions };
      return { asset_id: assetId, assertion: null };
    });
    renderPack1();
    await screen.findAllByTestId("pack-date");
    const listReadsBefore = api.apiGet.mock.calls.filter(([path]) => path === "/v1/assets").length;
    const row1 = screen.getByTestId("pack-row-pack-1");
    fireEvent.click(within(row1).getByRole("button", { name: "Edit" }));
    const dateInput = within(row1).getByLabelText("Date") as HTMLInputElement;
    expect(dateInput.value).toBe("2030-05-06");
    fireEvent.change(dateInput, { target: { value: "2031-02-03" } });
    fireEvent.click(within(row1).getByRole("button", { name: "Save date" }));
    await waitFor(() => expect(api.enterManualExpiry).toHaveBeenCalledWith(
      "pack-1", "hh", expect.objectContaining({ expiry_date: "2031-02-03" }), "a-exp-1"
    ));
    await waitFor(() => {
      const after = api.apiGet.mock.calls.filter(([path]) => path === "/v1/assets").length;
      expect(after).toBeGreaterThan(listReadsBefore);
    });
    await waitFor(() =>
      expect(within(screen.getByTestId("pack-row-pack-1")).getByTestId("pack-date")).toHaveTextContent("Use by 3 Feb 2031")
    );
  });

  test("T10 clearing the date re-reads the packs list and the row reads No date", async () => {
    api.clearExpiryDate.mockImplementation(async (assetId: string) => {
      const body = store[assetId];
      const kept = (body["assertions"] as unknown[]).filter((entry) => {
        const rec = entry as Record<string, unknown>;
        return (rec["field_path"] as string) === "plugin:expiry-tracker/classification";
      });
      store[assetId] = {
        ...body,
        assertions: [...kept, assertion("a-exp-cleared", "plugin:expiry-tracker/expiry_date", null, "accepted")],
      };
      return { asset_id: assetId, assertion: null };
    });
    renderPack1();
    await screen.findAllByTestId("pack-date");
    const listReadsBefore = api.apiGet.mock.calls.filter(([path]) => path === "/v1/assets").length;
    const row1 = screen.getByTestId("pack-row-pack-1");
    fireEvent.click(within(row1).getByRole("button", { name: "Edit" }));
    fireEvent.click(within(row1).getByRole("button", { name: "Clear expiry date" }));
    await waitFor(() => expect(api.clearExpiryDate).toHaveBeenCalledWith("pack-1", "hh", "a-exp-1"));
    await waitFor(() => {
      const after = api.apiGet.mock.calls.filter(([path]) => path === "/v1/assets").length;
      expect(after).toBeGreaterThan(listReadsBefore);
    });
    await waitFor(() =>
      expect(within(screen.getByTestId("pack-row-pack-1")).getByTestId("pack-date")).toHaveTextContent("No date")
    );
  });
});
