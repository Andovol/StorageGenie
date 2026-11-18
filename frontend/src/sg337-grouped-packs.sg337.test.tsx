import { beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./theme/ThemeProvider";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CatalogPage } from "./routes/CatalogPage";
import { ProductCard, type CatalogProduct } from "./components/catalog/ProductCard";
import type { Asset, AssetListResponse, ExpiryStatusResponse } from "./api/types";

// SG-337 G1: the grid groups live same-name packs into one card. Asset and
// expiry shapes are copied from the catalog suites that serve the real API
// reads (catalog.test.tsx `catalogAsset`, sg331-redesign-b `row`), never
// hand-made (SG-322).

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPost: vi.fn(),
  putBack: vi.fn(),
  fetchExpiryStatus: vi.fn(),
}));
vi.mock("./api/client", () => api);

function asset(
  id: string,
  name: string,
  created: string,
  evidenceIds?: string[]
): Asset {
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
    ...(evidenceIds ? { evidence_ids: evidenceIds } : {}),
  };
}

// Olive Oil 6 May 2030 (no photo), olive oil 3 Feb 2031 (photo), Olive Oil
// no date, Rice no date, one past item.
const BASE_ASSETS: Asset[] = [
  asset("pack-1", "Olive Oil", "2026-05-01T10:00:00Z"),
  asset("pack-2", "olive oil", "2026-06-01T10:00:00Z", ["ev-2"]),
  asset("pack-3", "Olive Oil", "2026-07-01T10:00:00Z"),
  asset("rice-1", "Rice", "2026-04-01T10:00:00Z"),
  asset("past-1", "Vinegar", "2026-03-01T10:00:00Z"),
];

function expiryRow(
  asset_id: string,
  display_name: string,
  expiry_date: string,
  days_remaining: number
) {
  return {
    asset_id,
    display_name,
    category: "food_beverages",
    expiry_date,
    date_type: "expiry_date",
    days_remaining,
    tier: null,
    bucket: (
      days_remaining < 0 ? "expired" : days_remaining <= 7 ? "this-week" : "safe"
    ) as "expired" | "this-week" | "safe",
  };
}

const BASE_ROWS = [
  expiryRow("pack-1", "Olive Oil", "2030-05-06", 1200),
  expiryRow("pack-2", "olive oil", "2031-02-03", 1400),
  expiryRow("past-1", "Vinegar", "2020-01-01", -100),
];

function statusBody(rows: ReturnType<typeof expiryRow>[]): ExpiryStatusResponse {
  return {
    household_id: "h1",
    as_of: "2026-11-16",
    category: null,
    rows: rows as ExpiryStatusResponse["rows"],
    summary: { by_tier: {}, by_bucket: {}, unresolved: 1, total: 5 },
    unresolved_rows: [],
  };
}

function mockCatalog(allAssets: Asset[], rows: ReturnType<typeof expiryRow>[]) {
  api.apiGet.mockImplementation((path: string, params?: Record<string, string>) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve({
        asset_type: { product: allAssets.length },
        status: { ACTIVE: allAssets.length },
        has_evidence: { with: 1, without: allAssets.length - 1 },
      });
    }
    if (path === "/v1/saved-searches") {
      return Promise.resolve({ items: [] });
    }
    if (path === "/v1/assets") {
      // The server owns `q` (FTS MATCH on display_name): narrow first.
      const q = (params?.q ?? "").trim().toLowerCase();
      const items = q
        ? allAssets.filter((item) =>
            (item.display_name ?? "").toLowerCase().includes(q)
          )
        : allAssets;
      const body: AssetListResponse = { items, next_cursor: null };
      return Promise.resolve(body);
    }
    if (path === "/v1/plugins/expiry-tracker/status") {
      return Promise.resolve(statusBody(rows));
    }
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

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter initialEntries={["/"]}>{ui}</MemoryRouter>);
}

beforeEach(() => {
  window.localStorage.clear();
  api.apiGet.mockReset();
  api.apiPatch.mockReset();
  api.apiPost.mockReset();
  api.fetchExpiryStatus.mockReset();
  mockCatalog(BASE_ASSETS, BASE_ROWS);
});

describe("SG-337 grouped same-name packs in the grid", () => {
  test("T1 grid: one Olive Oil card reading 3 packs with the 6 May 2030 date line; one Rice card with no packs line; 3 cards total", async () => {
    renderCatalog();
    const cards = await screen.findAllByTestId("product-card");
    expect(cards).toHaveLength(3);

    const olive = cards.find((card) => within(card).queryByText("3 packs"));
    expect(olive).toBeTruthy();
    expect(within(olive as HTMLElement).getByText("Olive Oil")).toBeInTheDocument();
    expect(
      within(olive as HTMLElement).getByTestId("product-date-wide")
    ).toHaveTextContent("Use by 6 May 2030");

    const rice = cards.find((card) => within(card).queryByText("Rice"));
    expect(rice).toBeTruthy();
    expect(within(rice as HTMLElement).queryByTestId("product-packs")).toBeNull();
  });

  test("T2 the Olive Oil card shows the 3 Feb 2031 pack photo (the soonest pack has none)", async () => {
    renderCatalog();
    await screen.findByText("3 packs");
    const olive = (await screen.findAllByTestId("product-card")).find((card) =>
      within(card).queryByText("3 packs")
    ) as HTMLElement;
    const img = within(olive).getByRole("img") as HTMLImageElement;
    expect(img.src).toContain("ev-2");
  });

  test("T3 clicking the card opens the 6 May 2030 pack (pack-1)", async () => {
    renderCatalog();
    await screen.findByText("3 packs");
    const olive = (await screen.findAllByTestId("product-card")).find((card) =>
      within(card).queryByText("3 packs")
    ) as HTMLElement;
    // The card link targets the soonest pack, so navigation (no drawer
    // interception) lands on pack-1.
    expect(olive.getAttribute("href")).toBe("/assets/pack-1?household_id=h1");
    fireEvent.click(olive);
    expect(await screen.findByTestId("inspector-drawer")).toBeInTheDocument();
  });

  test("T4 the attention line counts packs: two past packs of one name read 2 items are past their date", async () => {
    const twoPast: Asset[] = [
      ...BASE_ASSETS,
      asset("past-2", "vinegar", "2026-03-02T10:00:00Z"),
    ];
    const rows = [...BASE_ROWS, expiryRow("past-2", "vinegar", "2020-02-01", -90)];
    api.apiGet.mockReset();
    api.fetchExpiryStatus.mockReset();
    mockCatalog(twoPast, rows);
    renderCatalog();
    const line = await screen.findByTestId("catalog-attention");
    expect(line.textContent).toContain("2 items are past their date");
  });

  test("T5 table view keeps one row per pack: three Olive Oil rows", async () => {
    renderCatalog();
    await screen.findAllByTestId("product-card");
    fireEvent.click(screen.getByRole("button", { name: "List" }));
    const rows = await screen.findAllByTestId("product-row");
    expect(rows).toHaveLength(5);
    expect(rows.filter((row) => /olive/i.test(row.textContent ?? ""))).toHaveLength(3);
  });

  test("T6 search narrows first: olive shows one card, 3 packs", async () => {
    renderCatalog();
    await screen.findAllByTestId("product-card");
    fireEvent.change(screen.getByLabelText("Search your things"), {
      target: { value: "olive" },
    });
    await waitFor(() => expect(screen.getAllByTestId("product-card")).toHaveLength(1));
    expect(screen.getByText("3 packs")).toBeInTheDocument();
  });

  test("T7 G4: a card at 79.5 px width keeps its past chip inside the card", () => {
    const pastItem: CatalogProduct = {
      id: "past-1",
      name: "Vinegar",
      category: "product",
      tags: [],
      dateAdded: "2026-03-01T10:00:00Z",
      status: "raw",
      metadata: {},
      useBy: "2020-01-01",
      daysRemaining: -100,
    };
    renderWithRouter(
      <div style={{ width: 79.5 }}>
        <ProductCard item={pastItem} householdId="h1" />
      </div>
    );
    for (const testId of ["product-date-wide", "product-date-narrow"]) {
      const chip = screen.getByTestId(testId);
      // The style that guarantees the chip never extends past the card's
      // right edge: capped at the card width with wrapping allowed.
      expect(chip.style.maxWidth).toBe("100%");
      expect(chip.style.whiteSpace).not.toBe("nowrap");
    }
  });

  test("T8 G5: the grid and attention line carry no inset the title does not", async () => {
    renderCatalog();
    await screen.findAllByTestId("product-card");
    const main = screen.getByTestId("page-container");
    expect(main.tagName).toBe("MAIN");
    // No 1100 px cap and no auto centering: the content shares the title's
    // full-bleed 24 px left edge instead of the old 114 px inset.
    expect(main.style.maxWidth).toBe("");
    expect(main.style.marginLeft).not.toBe("auto");
    expect(main.style.paddingLeft).toBe("24px");
  });
});
