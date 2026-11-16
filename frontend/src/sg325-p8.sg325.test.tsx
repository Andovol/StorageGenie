import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./theme/ThemeProvider";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CatalogPage } from "./routes/CatalogPage";
import type { Asset, AssetListResponse, ExpiryStatusResponse } from "./api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn(), fetchExpiryStatus: vi.fn() }));
vi.mock("./api/client", () => api);

// SG-325 P8+P13: two packs with one name and different dates, plus one item
// with no date. Shapes copy api/types.ts AssetListResponse /
// ExpiryStatusResponse and the catalog.test.tsx drawer-wiring asset.
function asset(id: string, name: string, created: string): Asset {
  return {
    id,
    household_id: "h1",
    display_name: name,
    asset_type: "product",
    status: "ACTIVE",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: created,
    updated_at: null,
  };
}

const listBody: AssetListResponse = {
  items: [
    asset("a-oil-1", "Olive Oil", "2026-09-10T00:00:00Z"),
    asset("a-oil-2", "Olive Oil", "2026-09-11T00:00:00Z"),
    asset("a-beans", "Black Beans", "2026-09-12T00:00:00Z"),
  ],
  next_cursor: null,
};

function row(asset_id: string, display_name: string, expiry_date: string) {
  return {
    asset_id,
    display_name,
    category: "food_beverages",
    expiry_date,
    date_type: "expiry_date",
    days_remaining: 100,
    tier: null,
    bucket: "safe",
  } as const;
}

const statusBody: ExpiryStatusResponse = {
  household_id: "h1",
  as_of: "2026-09-16",
  category: null,
  rows: [row("a-oil-1", "Olive Oil", "2030-05-06"), row("a-oil-2", "Olive Oil", "2031-02-03")],
  summary: { by_tier: {}, by_bucket: {}, unresolved: 1, total: 3 },
  unresolved_rows: [{ asset_id: "a-beans", reason: "dateless" }],
};

function mockApi() {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve({
        asset_type: { product: 3 },
        status: { ACTIVE: 3 },
        has_evidence: { with: 0, without: 3 },
      });
    }
    if (path === "/v1/assets") return Promise.resolve(listBody);
    if (path === "/v1/plugins/expiry-tracker/status") return Promise.resolve(statusBody);
    return Promise.resolve({ items: [], next_cursor: null, total: 0 });
  });
  api.fetchExpiryStatus.mockImplementation((householdId: string) =>
    api.apiGet("/v1/plugins/expiry-tracker/status", { household_id: householdId })
  );
}

function renderCatalog() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={["/"]}>
          <HouseholdProvider>
            <CatalogPage />
          </HouseholdProvider>
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

describe("SG-325 P8+P13 catalog Use by column", () => {
  beforeEach(() => {
    window.localStorage.clear();
    api.apiGet.mockReset();
    api.apiPatch.mockReset();
    mockApi();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("the table replaces Status with Use by: same-name rows show their own dates, dateless shows No date", async () => {
    // SG-328: the catalog opens in Photo grid, so reach the table through
    // the List toggle (was: wide column 900 px opened the table).
    renderCatalog();
    await screen.findAllByTestId("product-card");
    expect(screen.getByRole("button", { name: "Photo grid" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );

    fireEvent.click(screen.getByRole("button", { name: "List" }));
    await screen.findAllByTestId("product-row");

    const headers = screen.getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(headers).toContain("Use by");
    expect(headers).not.toContain("Status");

    expect(await screen.findByText("6 May 2030")).toBeInTheDocument();
    expect(screen.getByText("3 Feb 2031")).toBeInTheDocument();
    expect(screen.getByText("No date")).toBeInTheDocument();
    expect(screen.getAllByText("Olive Oil")).toHaveLength(2);
    expect(screen.queryByText("Photo only")).not.toBeInTheDocument();

    const rows = screen.getAllByTestId("product-row");
    expect(rows).toHaveLength(3);
    const dated = rows.filter((r) => within(r as HTMLElement).queryByText("6 May 2030") || within(r as HTMLElement).queryByText("3 Feb 2031"));
    expect(dated).toHaveLength(2);
  });

  test("the card view shows the same dates in place of the status badge", async () => {
    // SG-328: Photo grid is the default (was: 900 px column then click
    // Photo grid); the grid already shows the cards on first render.
    renderCatalog();
    const cards = await screen.findAllByTestId("product-card");
    expect(cards).toHaveLength(3);
    expect(screen.getByText("6 May 2030")).toBeInTheDocument();
    expect(screen.getByText("3 Feb 2031")).toBeInTheDocument();
    expect(screen.getByText("No date")).toBeInTheDocument();
    expect(screen.queryByText("Photo only")).not.toBeInTheDocument();
  });
});
