import { afterEach, describe, expect, test, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
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

describe("PantryPage SG-302 warning colour", () => {
  test("EXPIRED label renders with var(--link), not var(--primary)", async () => {
    client.apiGet.mockResolvedValue({ items: [food("ex", "Cheese")], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(
      expiryResponse([expiryRow("ex", "Cheese", -1, "2026-11-09")])
    );
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const labels = await screen.findAllByTestId("pantry-expired");
    const label = labels[0];
    const style = label.getAttribute("style") ?? "";
    expect(style).toContain("var(--link)");
    expect(style).not.toContain("var(--primary)");
  });

  test("accent time-left line renders with var(--link), not var(--primary)", async () => {
    client.apiGet.mockResolvedValue({ items: [food("two", "Yogurt")], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(
      expiryResponse([expiryRow("two", "Yogurt", 1, "2026-11-11")])
    );
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const tile = (await screen.findAllByTestId("pantry-tile"))[0];
    const line = within(tile).getByTestId("pantry-time-left");
    expect(line).toHaveAttribute("data-accent", "true");
    const style = line.getAttribute("style") ?? "";
    expect(style).toContain("var(--link)");
    expect(style).not.toContain("var(--primary)");
  });
});

describe("PantryPage SG-302 empty state", () => {
  test("empty state contains a Capture link to /capture", async () => {
    client.apiGet.mockResolvedValue({ items: [], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue(expiryResponse([]));
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    renderPage();
    const link = await screen.findByRole("link", { name: "Capture" });
    const href = link.getAttribute("href") ?? "";
    expect(href.endsWith("/capture")).toBe(true);
  });
});
