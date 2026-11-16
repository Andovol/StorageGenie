import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./theme/ThemeProvider";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CatalogPage } from "./routes/CatalogPage";
import { ProductGrid } from "./components/catalog/ProductGrid";
import { sortCatalog } from "./components/shell/CatalogToolbar";
import type { Asset, AssetListResponse, ExpiryStatusResponse } from "./api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn(), fetchExpiryStatus: vi.fn() }));
vi.mock("./api/client", () => api);

// SG-331 T7: CSS `gap` is row column — wide 40px 24px, narrow 16px 8px.
function item(id: string, name: string) {
  return {
    id,
    name,
    category: "product",
    tags: [],
    dateAdded: "2026-09-10T00:00:00Z",
    status: "raw" as const,
    metadata: {},
  };
}

describe("SG-331 T7 grid gaps are row column", () => {
  test("wide grid uses 40px 24px and narrow uses 16px 8px", () => {
    const { unmount } = render(
      <MemoryRouter>
        <ProductGrid items={[item("a", "Milk")]} density="grid" householdId="h1" perRow={5} narrow={false} />
      </MemoryRouter>
    );
    expect(screen.getByTestId("catalog-grid").style.gap).toBe("40px 24px");
    unmount();
    render(
      <MemoryRouter>
        <ProductGrid items={[item("a", "Milk")]} density="grid" householdId="h1" perRow={3} narrow />
      </MemoryRouter>
    );
    expect(screen.getByTestId("catalog-grid").style.gap).toBe("16px 8px");
  });
});

// SG-331 T2: Use by, soonest first — past oldest first, then soonest, then
// no-date, ties by name. Real AssetListResponse + ExpiryStatusResponse shapes:
// two past, one within 7 days, one later, one with no date.
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

// created_at runs opposite to the use-by order so "recent" and "useby" disagree.
const listBody: AssetListResponse = {
  items: [
    asset("a-none", "Black Beans", "2026-09-14T00:00:00Z"),
    asset("a-later", "Olive Oil", "2026-09-13T00:00:00Z"),
    asset("a-soon", "Yogurt", "2026-09-12T00:00:00Z"),
    asset("a-past-new", "Eggs", "2026-09-11T00:00:00Z"),
    asset("a-past-old", "Milk", "2026-09-10T00:00:00Z"),
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
    row("a-past-old", "Milk", "2026-10-27", -20),
    row("a-past-new", "Eggs", "2026-11-11", -5),
    row("a-soon", "Yogurt", "2026-11-21", 5),
    row("a-later", "Olive Oil", "2030-05-06", 100),
  ],
  summary: { by_tier: {}, by_bucket: {}, unresolved: 1, total: 5 },
  unresolved_rows: [{ asset_id: "a-none", reason: "dateless" }],
};

function mockApi() {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve({
        asset_type: { product: 5 },
        status: { ACTIVE: 5 },
        has_evidence: { with: 0, without: 5 },
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

describe("SG-331 T1 kind-of-item text tabs", () => {
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

  test("pills become borderless text tabs with no counts, active underlined", async () => {
    renderCatalog();
    await screen.findAllByTestId("product-card");
    const tabs = screen.getByTestId("catalog-kind-tabs");
    expect(tabs.style.overflowX).toBe("auto");
    // No counts anywhere in the tab labels.
    for (const button of screen.getAllByRole("button")) {
      expect(button.textContent ?? "").not.toMatch(/\(\d+\)/);
    }
    const all = screen.getByRole("button", { name: "All" });
    expect(all).toHaveAttribute("aria-pressed", "true");
    expect(all.style.fontSize).toBe("15px");
    expect(all.style.fontWeight).toBe("600");
    expect(all.style.borderBottom).toContain("2px solid");
    expect(all.style.color).toBe("hsl(var(--ink))");
    const product = screen.getByRole("button", { name: "Product" });
    expect(product).toHaveAttribute("aria-pressed", "false");
    expect(product.style.fontSize).toBe("15px");
    expect(product.style.color).toBe("hsl(var(--ink-muted))");
  });
});

describe("SG-331 T2 use-by sort first", () => {
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

  test("sortCatalog orders past oldest first, then soonest, then no-date, ties by name", () => {
    const dated = [
      { ...item("a-soon", "Yogurt"), useBy: "2026-11-21" },
      { ...item("a-none", "Black Beans"), useBy: null },
      { ...item("a-later", "Olive Oil"), useBy: "2030-05-06" },
      { ...item("a-past-new", "Eggs"), useBy: "2026-11-11" },
      { ...item("a-past-old", "Milk"), useBy: "2026-10-27" },
    ];
    expect(sortCatalog(dated, "useby").map((i) => i.name)).toEqual([
      "Milk",
      "Eggs",
      "Yogurt",
      "Olive Oil",
      "Black Beans",
    ]);
    const tied = [
      { ...item("b", "Zed"), useBy: "2026-10-27" },
      { ...item("a", "Amy"), useBy: "2026-10-27" },
    ];
    expect(sortCatalog(tied, "useby").map((i) => i.name)).toEqual(["Amy", "Zed"]);
  });

  test("the catalog defaults to Use by, soonest first and lists past oldest first", async () => {
    renderCatalog();
    const cards = await screen.findAllByTestId("product-card");
    expect(cards).toHaveLength(5);
    const select = screen.getByLabelText("Sort");
    expect(select).toHaveValue("useby");
    expect(select.textContent).toContain("Use by, soonest first");
    expect(select.textContent).toContain("Recently added");
    expect(select.textContent).toContain("Name, A to Z");
    expect(select.textContent).not.toContain("Processing Status");
    const names = cards.map((card) => card.textContent ?? "");
    const order = ["Milk", "Eggs", "Yogurt", "Olive Oil", "Black Beans"].map((name) =>
      names.findIndex((text) => text.includes(name))
    );
    expect(order).toEqual([...order].sort((a, b) => a - b));
    expect(order[0]).toBeGreaterThanOrEqual(0);
    void fireEvent;
  });
});
