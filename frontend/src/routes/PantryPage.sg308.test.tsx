import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "../theme/ThemeProvider";
import { PantryPage } from "./PantryPage";

const client = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  fetchExpiryStatus: vi.fn(),
  fetchAnalyticsSummary: vi.fn(),
  decrementQuantity: vi.fn(),
  incrementQuantity: vi.fn(),
  markGone: vi.fn(),
  putBack: vi.fn(),
}));

vi.mock("../api/client", async (importOriginal) => {
  const original = await importOriginal<typeof import("../api/client")>();
  return {
    ...original,
    apiGet: (...args: unknown[]) => client.apiGet(...args),
    apiPatch: (...args: unknown[]) => client.apiPatch(...args),
    fetchExpiryStatus: (...args: unknown[]) => client.fetchExpiryStatus(...args),
    fetchAnalyticsSummary: (...args: unknown[]) => client.fetchAnalyticsSummary(...args),
    decrementQuantity: (...args: unknown[]) => client.decrementQuantity(...args),
    incrementQuantity: (...args: unknown[]) => client.incrementQuantity(...args),
    markGone: (...args: unknown[]) => client.markGone(...args),
    putBack: (...args: unknown[]) => client.putBack(...args),
  };
});

vi.mock("../hooks/HouseholdContext", () => ({
  useHouseholdContext: () => ({
    households: [{ id: "hh", name: "Home", created_at: "2026-01-01" }],
    isError: false,
    error: null,
    householdId: "hh",
  }),
}));

function food(id: string, name: string, overrides: Record<string, unknown> = {}) {
  return {
    id,
    household_id: "hh",
    display_name: name,
    asset_type: "product",
    status: "ACTIVE",
    quantity: 4,
    unit: "pcs",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    evidence_ids: [],
    assertions: [],
    ...overrides,
  };
}

function expiryRow(assetId: string, name: string, days: number, expiryDate: string) {
  return {
    asset_id: assetId,
    display_name: name,
    category: "food_beverages",
    expiry_date: expiryDate,
    date_type: "expiry_date",
    days_remaining: days,
    tier: null,
    bucket: days < 0 ? "expired" : days <= 7 ? "this-week" : "this-month",
  };
}

function expiryResponse(rows: ReturnType<typeof expiryRow>[]) {
  return {
    household_id: "hh",
    as_of: "2026-11-10",
    category: "food_beverages",
    rows,
    summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: rows.length },
    unresolved_rows: [],
  };
}

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter>
          <PantryPage />
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("PantryPage SG-308 panel refresh", () => {
  test("panel -1 updates the rendered tile", async () => {
    let listItems: ReturnType<typeof food>[] = [food("m1", "Milk", { quantity: 4 })];
    let single: ReturnType<typeof food> = food("m1", "Milk", { quantity: 4 });
    client.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/taxonomy") return Promise.resolve({ plugins: [] });
      if (path === "/v1/assets") return Promise.resolve({ items: listItems, next_cursor: null });
      if (path.startsWith("/v1/assets/")) return Promise.resolve(single);
      return Promise.reject(new Error(`unexpected GET ${path}`));
    });
    client.fetchExpiryStatus.mockImplementation(() => Promise.resolve(expiryResponse([])));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.decrementQuantity.mockImplementation(async () => {
      const updated = { ...single, quantity: 3, version: 2 };
      single = updated;
      listItems = [{ ...listItems[0], quantity: 3, version: 2 }];
      return updated;
    });
    renderPage();
    const grid = await screen.findByTestId("pantry-grid");
    expect(within(grid).getByText("4 left")).toBeInTheDocument();
    const openers = await screen.findAllByRole("button", { name: "Open Milk" });
    fireEvent.click(openers[0]);
    const drawer = await screen.findByTestId("inspector-drawer");
    fireEvent.click(within(drawer).getByRole("button", { name: "Take off 1" }));
    await waitFor(() => expect(client.decrementQuantity).toHaveBeenCalledWith("m1", "hh"));
    await waitFor(() => expect(within(screen.getByTestId("pantry-grid")).getByText("3 left")).toBeInTheDocument(), { timeout: 3000 });
  });

  test("panel +1 updates the rendered tile", async () => {
    let listItems: ReturnType<typeof food>[] = [food("m2", "Milk", { quantity: 4 })];
    let single: ReturnType<typeof food> = food("m2", "Milk", { quantity: 4 });
    client.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/taxonomy") return Promise.resolve({ plugins: [] });
      if (path === "/v1/assets") return Promise.resolve({ items: listItems, next_cursor: null });
      if (path.startsWith("/v1/assets/")) return Promise.resolve(single);
      return Promise.reject(new Error(`unexpected GET ${path}`));
    });
    client.fetchExpiryStatus.mockImplementation(() => Promise.resolve(expiryResponse([])));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.incrementQuantity.mockImplementation(async () => {
      const updated = { ...single, quantity: 5, version: 2 };
      single = updated;
      listItems = [{ ...listItems[0], quantity: 5, version: 2 }];
      return updated;
    });
    renderPage();
    const grid = await screen.findByTestId("pantry-grid");
    expect(within(grid).getByText("4 left")).toBeInTheDocument();
    const openers = await screen.findAllByRole("button", { name: "Open Milk" });
    fireEvent.click(openers[0]);
    const drawer = await screen.findByTestId("inspector-drawer");
    fireEvent.click(within(drawer).getByRole("button", { name: "Put 1 back on the count" }));
    await waitFor(() => expect(client.incrementQuantity).toHaveBeenCalledWith("m2", "hh"));
    await waitFor(() => expect(within(screen.getByTestId("pantry-grid")).getByText("5 left")).toBeInTheDocument(), { timeout: 3000 });
  });

  test("panel save updates the rendered tile", async () => {
    let listItems: ReturnType<typeof food>[] = [food("m3", "Milk", { quantity: 4 })];
    let single: ReturnType<typeof food> = food("m3", "Milk", { quantity: 4 });
    client.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/taxonomy") return Promise.resolve({ plugins: [] });
      if (path === "/v1/assets") return Promise.resolve({ items: listItems, next_cursor: null });
      if (path.startsWith("/v1/assets/")) return Promise.resolve(single);
      return Promise.reject(new Error(`unexpected GET ${path}`));
    });
    client.fetchExpiryStatus.mockImplementation(() => Promise.resolve(expiryResponse([])));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.apiPatch.mockImplementation(async () => {
      const updated = { ...single, display_name: "Milk Fresh", quantity: 7, version: 2 };
      single = updated;
      listItems = [{ ...listItems[0], display_name: "Milk Fresh", quantity: 7, version: 2 }];
      return updated;
    });
    renderPage();
    const grid = await screen.findByTestId("pantry-grid");
    expect(within(grid).getByText("Milk")).toBeInTheDocument();
    const openers = await screen.findAllByRole("button", { name: "Open Milk" });
    fireEvent.click(openers[0]);
    const drawer = await screen.findByTestId("inspector-drawer");
    fireEvent.change(within(drawer).getByLabelText("Title"), { target: { value: "Milk Fresh" } });
    fireEvent.change(within(drawer).getByLabelText("Quantity"), { target: { value: "7" } });
    fireEvent.click(within(drawer).getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(client.apiPatch).toHaveBeenCalled());
    await waitFor(() => expect(within(screen.getByTestId("pantry-grid")).getByText("Milk Fresh")).toBeInTheDocument(), { timeout: 3000 });
    await waitFor(() => expect(within(screen.getByTestId("pantry-grid")).getByText("7 left")).toBeInTheDocument(), { timeout: 3000 });
  });

  test("panel gone removes the tile from Use soon", async () => {
    let listItems: ReturnType<typeof food>[] = [food("m4", "Milk", { quantity: 4 })];
    let single: ReturnType<typeof food> = food("m4", "Milk", { quantity: 4 });
    let rows: ReturnType<typeof expiryRow>[] = [expiryRow("m4", "Milk", 2, "2026-11-12")];
    client.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/taxonomy") return Promise.resolve({ plugins: [] });
      if (path === "/v1/assets") return Promise.resolve({ items: listItems, next_cursor: null });
      if (path.startsWith("/v1/assets/")) return Promise.resolve(single);
      return Promise.reject(new Error(`unexpected GET ${path}`));
    });
    client.fetchExpiryStatus.mockImplementation(() => Promise.resolve(expiryResponse(rows)));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.markGone.mockImplementation(async () => {
      const updated = { ...single, status: "ARCHIVED", gone_reason: "used_up", version: 2 };
      single = updated;
      listItems = [];
      rows = [];
      return updated;
    });
    renderPage();
    const useSoon = await screen.findByTestId("pantry-use-soon-grid");
    expect(within(useSoon).getByText("Milk")).toBeInTheDocument();
    const openers = await screen.findAllByRole("button", { name: "Open Milk" });
    fireEvent.click(openers[0]);
    const drawer = await screen.findByTestId("inspector-drawer");
    fireEvent.click(within(drawer).getByRole("button", { name: "Used up" }));
    await waitFor(() => expect(client.markGone).toHaveBeenCalledWith("m4", "hh", "used_up"));
    await waitFor(() => expect(screen.queryByTestId("pantry-use-soon-grid")).toBeNull(), { timeout: 3000 });
  });

  test("panel put back returns the tile to Use soon", async () => {
    let listItems: ReturnType<typeof food>[] = [food("m5", "Milk", { quantity: 4 })];
    let single: ReturnType<typeof food> = food("m5", "Milk", {
      quantity: 4,
      status: "ARCHIVED",
      gone_reason: "used_up",
    });
    let rows: ReturnType<typeof expiryRow>[] = [];
    client.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/taxonomy") return Promise.resolve({ plugins: [] });
      if (path === "/v1/assets") return Promise.resolve({ items: listItems, next_cursor: null });
      if (path.startsWith("/v1/assets/")) return Promise.resolve(single);
      return Promise.reject(new Error(`unexpected GET ${path}`));
    });
    client.fetchExpiryStatus.mockImplementation(() => Promise.resolve(expiryResponse(rows)));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.putBack.mockImplementation(async () => {
      const updated = { ...single, status: "ACTIVE", gone_reason: null, version: 2 };
      single = updated;
      listItems = [food("m5", "Milk", { quantity: 4 })];
      rows = [expiryRow("m5", "Milk", 2, "2026-11-12")];
      return updated;
    });
    renderPage();
    expect(await screen.findByTestId("pantry-grid")).toBeInTheDocument();
    expect(screen.queryByTestId("pantry-use-soon-grid")).toBeNull();
    const openers = await screen.findAllByRole("button", { name: "Open Milk" });
    fireEvent.click(openers[0]);
    const drawer = await screen.findByTestId("inspector-drawer");
    const putBackBtn = await within(drawer).findByRole("button", { name: "Put back" });
    fireEvent.click(putBackBtn);
    await waitFor(() => expect(client.putBack).toHaveBeenCalledWith("m5", "hh"));
    await waitFor(() => expect(screen.getByTestId("pantry-use-soon-grid")).toBeInTheDocument(), {
      timeout: 3000,
    });
    expect(within(screen.getByTestId("pantry-use-soon-grid")).getByText("Milk")).toBeInTheDocument();
  });
});
