import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./theme/ThemeProvider";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CatalogPage } from "./routes/CatalogPage";
import type { Asset, AssetListResponse, ExpiryStatusResponse } from "./api/types";

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

// SG-330 R4/R5: the real AssetListResponse + ExpiryStatusResponse shapes — one
// item past its date, one within 7 days, one later, one with no date.
const listBody: AssetListResponse = {
  items: [
    asset("a-past", "Milk"),
    asset("a-soon", "Yogurt"),
    asset("a-later", "Olive Oil"),
    asset("a-none", "Black Beans"),
  ],
  next_cursor: null,
};

function row(asset_id: string, display_name: string, expiry_date: string, days_remaining: number) {
  return {
    asset_id,
    display_name,
    category: "food_beverages",
    expiry_date,
    date_type: "expiry_date",
    days_remaining,
    tier: null,
    bucket: "safe",
  } as const;
}

const statusBody: ExpiryStatusResponse = {
  household_id: "h1",
  as_of: "2026-11-16",
  category: null,
  rows: [
    row("a-past", "Milk", "2026-10-27", -20),
    row("a-soon", "Yogurt", "2026-11-21", 5),
    row("a-later", "Olive Oil", "2030-05-06", 100),
  ],
  summary: { by_tier: {}, by_bucket: {}, unresolved: 1, total: 4 },
  unresolved_rows: [{ asset_id: "a-none", reason: "dateless" }],
};

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

function setViewportWidth(width: number) {
  Object.defineProperty(window, "innerWidth", { writable: true, configurable: true, value: width });
  fireEvent(window, new Event("resize"));
}

describe("SG-330 R4 items per row", () => {
  beforeEach(() => {
    window.localStorage.clear();
    api.apiGet.mockReset();
    api.apiPatch.mockReset();
    api.fetchExpiryStatus.mockReset();
    mockApi();
    setViewportWidth(1280);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    setViewportWidth(1024);
  });

  test("wide screens offer 4/5/6 with 5 pressed and five columns", async () => {
    renderCatalog();
    await screen.findAllByTestId("product-card");
    const group = screen.getByRole("group", { name: "Per row" });
    expect(group).toBeInTheDocument();
    for (const n of ["4", "5", "6"]) {
      expect(group.querySelector(`button[name="${n}"]`) ?? screen.getByRole("button", { name: n })).toBeInTheDocument();
    }
    expect(screen.getByRole("button", { name: "5" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("catalog-grid").style.gridTemplateColumns).toContain("repeat(5,");
  });

  test("the choice persists per device and is read back after a remount", async () => {
    const first = renderCatalog();
    await screen.findAllByTestId("product-card");
    fireEvent.click(screen.getByRole("button", { name: "6" }));
    expect(screen.getByRole("button", { name: "6" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("catalog-grid").style.gridTemplateColumns).toContain("repeat(6,");
    expect(window.localStorage.getItem("sg-per-row-wide")).toBe("6");
    first.unmount();

    renderCatalog();
    await screen.findAllByTestId("product-card");
    expect(screen.getByRole("button", { name: "6" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("catalog-grid").style.gridTemplateColumns).toContain("repeat(6,");
  });

  test("a broken localStorage falls back to the default instead of breaking the page", async () => {
    const realGet = window.localStorage.getItem.bind(window.localStorage);
    vi.spyOn(window.localStorage.__proto__, "getItem").mockImplementation((...args: unknown[]) => {
      const key = args[0] as string;
      if (key === "sg-per-row-wide" || key === "sg-per-row-narrow") throw new Error("denied");
      return realGet(key);
    });
    renderCatalog();
    await screen.findAllByTestId("product-card");
    expect(screen.getByRole("button", { name: "5" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByTestId("catalog-grid").style.gridTemplateColumns).toContain("repeat(5,");
  });

  test("narrow screens offer 3/4 with 3 pressed and narrow gaps", async () => {
    setViewportWidth(500);
    renderCatalog();
    await screen.findAllByTestId("product-card");
    expect(screen.getByRole("button", { name: "3" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "4" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "6" })).not.toBeInTheDocument();
    expect(screen.getByTestId("catalog-grid").style.gridTemplateColumns).toContain("repeat(3,");
  });
});
