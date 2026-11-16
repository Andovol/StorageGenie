import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./theme/ThemeProvider";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CatalogPage } from "./routes/CatalogPage";
import type { Asset } from "./api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn(), fetchExpiryStatus: vi.fn() }));
vi.mock("./api/client", () => api);

function asset(id: string, name: string): Asset {
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
    created_at: "2026-09-10T00:00:00Z",
    updated_at: null,
  };
}

const items = [asset("a-1", "Drill"), asset("a-2", "Zap"), asset("a-3", "Shirt"), asset("a-4", "Mystery")];

function mockApi() {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve({
        asset_type: { product: 4 },
        status: { ACTIVE: 4 },
        has_evidence: { with: 0, without: 4 },
      });
    }
    if (path === "/v1/saved-searches") {
      return Promise.resolve({ items: [] });
    }
    if (path === "/v1/assets") return Promise.resolve({ items, next_cursor: null });
    if (path === "/v1/plugins/expiry-tracker/status") {
      return Promise.resolve({
        household_id: "h1",
        as_of: "2026-11-16",
        category: null,
        rows: [],
        summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 4 },
        unresolved_rows: [],
      });
    }
    return Promise.resolve({ items: [], next_cursor: null, total: 0 });
  });
  api.fetchExpiryStatus.mockImplementation((householdId: string) =>
    api.apiGet("/v1/plugins/expiry-tracker/status", { household_id: householdId })
  );
}

describe("SG-330 R3 catalog heading", () => {
  beforeEach(() => {
    window.localStorage.clear();
    api.apiGet.mockReset();
    api.apiPatch.mockReset();
    api.fetchExpiryStatus.mockReset();
    mockApi();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("the catalog opens with Your things and the live count", async () => {
    render(
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
    const heading = await screen.findByRole("heading", { name: "Your things", level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveClass("sg-catalog-title");
    expect(await screen.findByText("4 things")).toBeInTheDocument();
    expect(screen.queryByText(/ITEMS/)).not.toBeInTheDocument();
  });
});
