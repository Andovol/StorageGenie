import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "../theme/ThemeProvider";
import { PantryPage, pantryTimeLeftText, sortPantryItems } from "./PantryPage";

const client = vi.hoisted(() => ({
  apiGet: vi.fn(),
  fetchExpiryStatus: vi.fn(),
  fetchAnalyticsSummary: vi.fn(),
  decrementQuantity: vi.fn(),
  markGone: vi.fn(),
  putBack: vi.fn(),
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
    quantity: 2,
    unit: "pcs",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    evidence_ids: [],
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

describe("PantryPage SG-300 order", () => {
  test("expired first (most overdue first), then soonest, dateless last, then by name", async () => {
    const items = [
      food("a", "Alpha", { quantity: 1 }),
      food("b", "Bravo", { quantity: 1 }),
      food("c", "Charlie", { quantity: 1 }),
      food("d", "Delta", { quantity: 1 }),
      food("e", "Echo", { quantity: 1 }),
    ];
    client.apiGet.mockResolvedValue({ items, next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(
      expiryResponse([
        expiryRow("a", "Alpha", 3, "2026-11-13"),
        expiryRow("b", "Bravo", -4, "2026-11-06"),
        expiryRow("d", "Delta", -1, "2026-11-09"),
        expiryRow("e", "Echo", 0, "2026-11-10"),
      ])
    );
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const grid = await screen.findByTestId("pantry-grid");
    const ids = within(grid)
      .getAllByTestId("pantry-tile")
      .map((tile) => tile.getAttribute("data-asset-id"));
    expect(ids).toEqual(["b", "d", "e", "a", "c"]);
  });

  test("sortPantryItems: same order rule, and the Use soon grid uses it too", () => {
    const rows = new Map([
      ["x", expiryRow("x", "X", 5, "2026-11-15")],
      ["y", expiryRow("y", "Y", -2, "2026-11-08")],
    ]);
    const sorted = sortPantryItems(
      [food("z", "Zulu"), food("x", "X"), food("y", "Y")] as never,
      rows as never
    );
    expect(sorted.map((a) => a.id)).toEqual(["y", "x", "z"]);
  });
});

describe("PantryPage SG-300 time left", () => {
  test.each([
    [0, "2026-11-10", "Use today"],
    [1, "2026-11-11", "Use by tomorrow"],
    [2, "2026-11-12", "Use in 2 days"],
    [14, "2026-11-24", "Use in 14 days"],
    [15, "2026-11-25", "Use by 25 Nov"],
    [-1, "2026-11-09", "Expired yesterday"],
    [-3, "2026-11-07", "Expired 3 days ago"],
  ])("days_remaining %s reads %s", (days, date, expected) => {
    expect(pantryTimeLeftText(days, date, 2026)).toBe(expected);
  });

  test("no date reads No date; a date in a later year carries the year", () => {
    expect(pantryTimeLeftText(null, null, 2026)).toBe("No date");
    expect(pantryTimeLeftText(40, "2027-01-02", 2026)).toBe("Use by 2 Jan 2027");
  });

  test("the time-left line is rendered from the engine days", async () => {
    client.apiGet.mockResolvedValue({ items: [food("m", "Milk")], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([expiryRow("m", "Milk", 1, "2026-11-11")]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const tile = (await screen.findAllByTestId("pantry-tile"))[0];
    expect(within(tile).getByText("Use by tomorrow")).toBeInTheDocument();
  });
});

describe("PantryPage SG-300 accent and EXPIRED label", () => {
  test("accent at 2 days or less, EXPIRED label only when expired", async () => {
    client.apiGet.mockResolvedValue({
      items: [food("ex", "Cheese"), food("two", "Yogurt"), food("three", "Butter")],
      next_cursor: null,
    });
    client.fetchExpiryStatus.mockResolvedValue(
      expiryResponse([
        expiryRow("ex", "Cheese", -1, "2026-11-09"),
        expiryRow("two", "Yogurt", 2, "2026-11-12"),
        expiryRow("three", "Butter", 3, "2026-11-13"),
      ])
    );
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    await screen.findAllByTestId("pantry-tile");
    const cheese = screen.getAllByTestId("pantry-tile").find((t) => t.getAttribute("data-asset-id") === "ex")!;
    const yogurt = screen.getAllByTestId("pantry-tile").find((t) => t.getAttribute("data-asset-id") === "two")!;
    const butter = screen.getAllByTestId("pantry-tile").find((t) => t.getAttribute("data-asset-id") === "three")!;
    expect(within(cheese).getByTestId("pantry-time-left")).toHaveAttribute("data-accent", "true");
    expect(within(yogurt).getByTestId("pantry-time-left")).toHaveAttribute("data-accent", "true");
    expect(within(butter).getByTestId("pantry-time-left")).toHaveAttribute("data-accent", "false");
    expect(within(cheese).getByText("EXPIRED")).toBeInTheDocument();
    expect(within(yogurt).queryByText("EXPIRED")).toBeNull();
    expect(within(butter).queryByText("EXPIRED")).toBeNull();
  });
});

describe("PantryPage SG-300 quantity wording", () => {
  test("counted items read N left; amounts read N unit left", async () => {
    client.apiGet.mockResolvedValue({
      items: [
        food("one", "Eggs", { quantity: 1, unit: "pcs" }),
        food("four", "Apples", { quantity: 4, unit: "" }),
        food("oats", "Oats", { quantity: 340, unit: "g" }),
      ],
      next_cursor: null,
    });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const grid = await screen.findByTestId("pantry-grid");
    expect(within(grid).getByText("1 left")).toBeInTheDocument();
    expect(within(grid).getByText("4 left")).toBeInTheDocument();
    expect(within(grid).getByText("340 g left")).toBeInTheDocument();
    expect(grid).not.toHaveTextContent("pcs left");
  });
});

describe("PantryPage SG-300 design", () => {
  test("the tile wrapper has no border and no card background", async () => {
    client.apiGet.mockResolvedValue({ items: [food("m", "Milk")], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const tile = (await screen.findAllByTestId("pantry-tile"))[0] as HTMLElement;
    expect(tile.style.borderStyle).toBe("");
    expect(tile.style.borderWidth).toBe("");
    expect(tile.style.backgroundColor).toBe("");
  });

  test("the grid track is two columns at 375 px and five or more at 1280 px", async () => {
    client.apiGet.mockResolvedValue({ items: [], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    const { container } = renderPage();
    await waitFor(() => expect(container.querySelector("[data-testid='pantry-grid-style']")).not.toBeNull());
    const css = container.querySelector("[data-testid='pantry-grid-style']")!.textContent ?? "";
    expect(css).toContain("repeat(auto-fill, minmax(min(150px, calc(50% - 8px)), 1fr))");
  });

  test("the subtitle reads the owner's line", async () => {
    client.apiGet.mockResolvedValue({ items: [], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    expect(await screen.findByText("What you have, and what to use first.")).toBeInTheDocument();
    expect(screen.queryByText(/Each pack is its own tile/)).toBeNull();
  });

  test("the actions sit in one row: counted gets -1 and Use it up, amount gets Edit and Use it up", async () => {
    client.apiGet.mockResolvedValue({
      items: [food("c", "Eggs", { quantity: 3, unit: "pcs" }), food("a", "Oats", { quantity: 340, unit: "g" })],
      next_cursor: null,
    });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const grid = await screen.findByTestId("pantry-grid");
    const tiles = within(grid).getAllByTestId("pantry-tile");
    expect(within(tiles[0]).getByRole("button", { name: "Take off 1" })).toBeInTheDocument();
    expect(within(tiles[0]).getByRole("button", { name: "Use it up" })).toBeInTheDocument();
    expect(within(tiles[1]).getByRole("button", { name: "Edit" })).toBeInTheDocument();
    expect(within(tiles[1]).getByRole("button", { name: "Use it up" })).toBeInTheDocument();
    expect(within(tiles[1]).queryByRole("button", { name: "Take off 1" })).toBeNull();
  });
});

describe("PantryPage SG-300 notice", () => {
  test("Use it up shows the notice; Put back calls the route and the tile returns", async () => {
    const milk = food("food-1", "Milk");
    client.apiGet
      .mockResolvedValueOnce({ items: [milk], next_cursor: null })
      .mockResolvedValueOnce({ items: [], next_cursor: null })
      .mockResolvedValue({ items: [milk], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    client.markGone.mockResolvedValue({ ...milk, status: "ARCHIVED", gone_reason: "used_up" });
    client.putBack.mockResolvedValue({ ...milk, status: "ACTIVE", gone_reason: null });
    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: "Use it up" }));
    await waitFor(() => expect(client.markGone).toHaveBeenCalledWith("food-1", "hh", "used_up"));
    const notice = await screen.findByTestId("pantry-notice");
    expect(notice).toHaveTextContent("Milk used up · Put back");
    fireEvent.click(within(notice).getByRole("button", { name: "Put back" }));
    await waitFor(() => expect(client.putBack).toHaveBeenCalledWith("food-1", "hh"));
    expect((await screen.findAllByTestId("pantry-tile"))[0]).toBeInTheDocument();
  });

  test("the notice clears after about six seconds", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    try {
      const milk = food("food-1", "Milk");
      client.apiGet.mockResolvedValue({ items: [milk], next_cursor: null });
      client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
      client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
      client.markGone.mockResolvedValue({ ...milk, status: "ARCHIVED", gone_reason: "used_up" });
      renderPage();
      fireEvent.click(await screen.findByRole("button", { name: "Use it up" }));
      expect(await screen.findByTestId("pantry-notice")).toBeInTheDocument();
      await vi.advanceTimersByTimeAsync(6100);
      await waitFor(() => expect(screen.queryByTestId("pantry-notice")).toBeNull());
    } finally {
      vi.useRealTimers();
    }
  });
});
