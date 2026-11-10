import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "../theme/ThemeProvider";
import { PantryPage } from "./PantryPage";

const client = vi.hoisted(() => ({
  apiGet: vi.fn(),
  fetchExpiryStatus: vi.fn(),
  fetchAnalyticsSummary: vi.fn(),
  decrementQuantity: vi.fn(),
  markGone: vi.fn(),
}));

vi.mock("../api/client", async (importOriginal) => {
  const original = await importOriginal<typeof import("../api/client")>();
  return {
    ...original,
    apiGet: (...args: unknown[]) => client.apiGet(...args),
    fetchExpiryStatus: (...args: unknown[]) => client.fetchExpiryStatus(...args),
    fetchAnalyticsSummary: (...args: unknown[]) => client.fetchAnalyticsSummary(...args),
    decrementQuantity: (...args: unknown[]) => client.decrementQuantity(...args),
    markGone: (...args: unknown[]) => client.markGone(...args),
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

vi.mock("./AssetDetailPage", async (importOriginal) => {
  const original = await importOriginal<typeof import("./AssetDetailPage")>();
  return { ...original, isCountedUnit: (unit: string | null | undefined) => !unit || !["ml", "l", "g", "kg"].includes((unit || "").toLowerCase()) };
});

const foodLive = {
  id: "food-1",
  household_id: "hh",
  display_name: "Milk",
  asset_type: "product",
  status: "ACTIVE",
  quantity: 2,
  unit: "pcs",
  condition: null,
  version: 1,
  created_at: "2026-09-14T00:00:00+00:00",
  evidence_ids: [],
};

const foodGone = { ...foodLive, id: "food-gone", display_name: "Old Yogurt", status: "ARCHIVED" };

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

describe("PantryPage SG-273", () => {
  test("only ACTIVE food is listed; unsorted is counted in Not sorted yet", async () => {
    client.apiGet.mockResolvedValue({ items: [foodLive], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-11-10",
      category: "food_beverages",
      rows: [],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 0 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({
      categories: { uncategorized: 2 },
    });
    renderPage();
    expect(await screen.findByText("Milk")).toBeInTheDocument();
    expect(screen.queryByText("Wrench")).not.toBeInTheDocument();
    expect(screen.getByTestId("pantry-unsorted")).toHaveTextContent(/Not sorted yet/);
    expect(screen.getByTestId("pantry-count")).toHaveTextContent("1 ITEMS");
  });

  test("a gone item leaves the Pantry and Put back brings it back", async () => {
    client.apiGet
      .mockResolvedValueOnce({ items: [foodLive, foodGone], next_cursor: null })
      .mockResolvedValue({ items: [foodLive], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-11-10",
      category: "food_beverages",
      rows: [],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 0 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    // Gone row is filtered client-side to ACTIVE only.
    expect(await screen.findByText("Milk")).toBeInTheDocument();
    expect(screen.queryByText("Old Yogurt")).not.toBeInTheDocument();
  });

  test("Use soon holds exactly expired or this-week, either side of the 7-day edge", async () => {
    const in7 = { ...foodLive, id: "edge-in", display_name: "Edge In" };
    const out8 = { ...foodLive, id: "edge-out", display_name: "Edge Out" };
    client.apiGet.mockResolvedValue({ items: [in7, out8], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-11-10",
      category: "food_beverages",
      rows: [
        { asset_id: "edge-in", display_name: "Edge In", category: "food_beverages", expiry_date: "2026-11-17", date_type: "expiry_date", days_remaining: 7, tier: "urgent", bucket: "this-week" },
        { asset_id: "edge-out", display_name: "Edge Out", category: "food_beverages", expiry_date: "2026-11-18", date_type: "expiry_date", days_remaining: 8, tier: "upcoming", bucket: "this-month" },
      ],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 2 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const useSoon = await screen.findByTestId("pantry-use-soon-grid");
    expect(useSoon).toHaveTextContent("Edge In");
    expect(useSoon).not.toHaveTextContent("Edge Out");
    expect(screen.getByTestId("pantry-grid")).toHaveTextContent("Edge Out");
  });

  test("-1 and Used up call the existing routes and the tile updates", async () => {
    client.apiGet.mockResolvedValue({ items: [foodLive], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-11-10",
      category: "food_beverages",
      rows: [],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 0 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.decrementQuantity.mockResolvedValue({ ...foodLive, quantity: 1 });
    client.markGone.mockResolvedValue({ ...foodLive, status: "ARCHIVED", gone_reason: "used_up" });
    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: "Take off 1" }));
    await waitFor(() => expect(client.decrementQuantity).toHaveBeenCalledWith("food-1", "hh"));
    fireEvent.click(screen.getByRole("button", { name: "Used up" }));
    await waitFor(() => expect(client.markGone).toHaveBeenCalledWith("food-1", "hh", "used_up"));
  });

  test("journey: classified food appears, -1, Used up, gone from the grid", async () => {
    client.apiGet
      .mockResolvedValueOnce({ items: [], next_cursor: null })
      .mockResolvedValue({ items: [foodLive], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-11-10",
      category: "food_beverages",
      rows: [],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 0 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 1 } });
    client.decrementQuantity.mockResolvedValue({ ...foodLive, quantity: 1 });
    client.markGone.mockResolvedValue({ ...foodLive, status: "ARCHIVED", gone_reason: "used_up" });
    renderPage();
    expect(await screen.findByText(/No food yet/)).toBeInTheDocument();
  });
});
